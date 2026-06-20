import { create } from 'zustand';
import { NativeService, OfflineSyncService } from '../services/nativeService';

export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export interface Task {
  id: number;
  title: string;
  description?: string;
  priority: string;
  status: string;
  due_date?: string;
  due_time?: string;
  estimated_time?: number;
  repeat_rule?: string;
  reminder_rule?: string;
  notes?: string;
  labels: { id: number; label: string }[];
}

export interface HabitLog {
  id: number;
  date: string;
  status: string;
}

export interface Habit {
  id: number;
  name: string;
  category?: string;
  frequency: string;
  goal?: string;
  logs: HabitLog[];
}

export interface GoalMilestone {
  id: number;
  title: string;
  progress: number;
  is_completed: boolean;
}

export interface Goal {
  id: number;
  title: string;
  category?: string;
  target_value?: number;
  current_value: number;
  deadline?: string;
  status: string;
  milestones: GoalMilestone[];
}

export interface Note {
  id: number;
  title: string;
  content?: string;
  tags?: string;
  parent_note_id?: number;
  created_at: string;
}

export interface Trade {
  id: number;
  entry_time: string;
  exit_time?: string;
  ticker: string;
  type: string;
  quantity: number;
  entry_price: number;
  exit_price?: number;
  strategy?: string;
  psychology_notes?: string;
  pnl: number;
}

export interface Panchang {
  date: string;
  tithi: string;
  nakshatra: string;
  yoga: string;
  karana: string;
  sunrise: string;
  sunset: string;
  festivals: string[];
  muhurats: string[];
}

interface LifeOSState {
  // Auth
  token: string | null;
  user: { email: string; full_name?: string } | null;
  isOffline: boolean;
  
  // App states
  activeTab: string;
  tasks: Task[];
  habits: Habit[];
  goals: Goal[];
  notes: Note[];
  trades: Trade[];
  panchang: Panchang | null;
  
  // AI states
  aiSchedule: any;
  aiBreakdown: any;
  loadingAI: boolean;

  // Actions
  getHeaders: () => Record<string, string>;
  apiCall: (path: string, options?: RequestInit) => Promise<any>;
  setToken: (token: string | null) => void;
  setUser: (user: any) => void;
  setActiveTab: (tab: string) => void;
  setOfflineMode: (offline: boolean) => void;
  
  // Data actions
  fetchTasks: () => Promise<void>;
  createTask: (task: any) => Promise<void>;
  updateTask: (id: number, task: any) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
  
  fetchHabits: () => Promise<void>;
  createHabit: (habit: any) => Promise<void>;
  logHabit: (id: number, dateStr: string, status: string) => Promise<void>;
  
  fetchGoals: () => Promise<void>;
  createGoal: (goal: any) => Promise<void>;
  updateGoal: (id: number, goalUpdate: any) => Promise<void>;
  deleteGoal: (id: number) => Promise<void>;
  addMilestone: (goalId: number, milestone: any) => Promise<void>;
  
  fetchNotes: () => Promise<void>;
  createNote: (note: any) => Promise<void>;
  deleteNote: (id: number) => Promise<void>;
  
  fetchTrades: () => Promise<void>;
  logTrade: (trade: any) => Promise<void>;
  exitTrade: (id: number, tradeUpdate: any) => Promise<void>;
  
  fetchPanchang: (dateStr?: string) => Promise<void>;
  optimizeSchedule: () => Promise<void>;
  breakdownTaskAI: (title: string, description?: string) => Promise<void>;
}

// Initial Mock Data for Local Fallback
const getLocalTasks = () => JSON.parse(localStorage.getItem("lifeos_tasks") || "[]");
const getLocalHabits = () => JSON.parse(localStorage.getItem("lifeos_habits") || "[]");
const getLocalGoals = () => JSON.parse(localStorage.getItem("lifeos_goals") || "[]");
const getLocalNotes = () => JSON.parse(localStorage.getItem("lifeos_notes") || "[]");
const getLocalTrades = () => JSON.parse(localStorage.getItem("lifeos_trades") || "[]");

export const useLifeOSStore = create<LifeOSState>((set, get) => ({
  token: localStorage.getItem("lifeos_token"),
  user: JSON.parse(localStorage.getItem("lifeos_user") || "null"),
  isOffline: false,
  activeTab: "dashboard",
  
  tasks: getLocalTasks(),
  habits: getLocalHabits(),
  goals: getLocalGoals(),
  notes: getLocalNotes(),
  trades: getLocalTrades(),
  panchang: null,
  
  aiSchedule: null,
  aiBreakdown: null,
  loadingAI: false,

  setToken: (token) => {
    if (token) {
      localStorage.setItem("lifeos_token", token);
      NativeService.setSecureItem("lifeos_token", token);
    } else {
      localStorage.removeItem("lifeos_token");
      NativeService.removeSecureItem("lifeos_token");
    }
    set({ token });
  },
  
  setUser: (user) => {
    if (user) {
      localStorage.setItem("lifeos_user", JSON.stringify(user));
      NativeService.setSecureItem("lifeos_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("lifeos_user");
      NativeService.removeSecureItem("lifeos_user");
    }
    set({ user });
  },

  setActiveTab: (activeTab) => set({ activeTab }),
  setOfflineMode: (isOffline) => set({ isOffline }),

  // Headers helper
  getHeaders: () => {
    const token = get().token;
    return {
      "Content-Type": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {})
    };
  },

  // API Call Wrapper with local fallback
  apiCall: async (path: string, options: RequestInit = {}) => {
    const headers = get().getHeaders();
    const url = `${API_BASE}${path}`;
    try {
      const res = await fetch(url, {
        ...options,
        headers: { ...headers, ...options.headers }
      });
      if (res.status === 401) {
        // Clear auth on unauthorized
        get().setToken(null);
        get().setUser(null);
      }
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      set({ isOffline: true });
      throw err;
    }
  },

  fetchTasks: async () => {
    try {
      const data = await get().apiCall("/tasks/");
      set({ tasks: data, isOffline: false });
      localStorage.setItem("lifeos_tasks", JSON.stringify(data));
    } catch (err) {
      set({ tasks: getLocalTasks() });
    }
  },

  createTask: async (task) => {
    try {
      const data = await get().apiCall("/tasks/", {
        method: "POST",
        body: JSON.stringify(task)
      });
      set((state) => {
        const updated = [...state.tasks, data];
        localStorage.setItem("lifeos_tasks", JSON.stringify(updated));
        return { tasks: updated, isOffline: false };
      });
    } catch (err) {
      // Offline fallback creation
      const newTask = {
        id: Date.now(),
        ...task,
        status: task.status || "Pending",
        priority: task.priority || "Medium",
        labels: (task.labels || []).map((l: string, i: number) => ({ id: i, label: l })),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      OfflineSyncService.enqueueAction('CREATE', 'task', newTask.id, newTask);
      set((state) => {
        const updated = [...state.tasks, newTask];
        localStorage.setItem("lifeos_tasks", JSON.stringify(updated));
        return { tasks: updated };
      });
    }
  },

  updateTask: async (id, taskUpdate) => {
    try {
      const data = await get().apiCall(`/tasks/${id}`, {
        method: "PUT",
        body: JSON.stringify(taskUpdate)
      });
      set((state) => {
        const updated = state.tasks.map((t) => (t.id === id ? data : t));
        localStorage.setItem("lifeos_tasks", JSON.stringify(updated));
        return { tasks: updated, isOffline: false };
      });
    } catch (err) {
      OfflineSyncService.enqueueAction('UPDATE', 'task', id, taskUpdate);
      set((state) => {
        const updated = state.tasks.map((t) => {
          if (t.id === id) {
            return {
              ...t,
              ...taskUpdate,
              labels: taskUpdate.labels 
                ? taskUpdate.labels.map((l: string, i: number) => ({ id: i, label: l })) 
                : t.labels
            };
          }
          return t;
        });
        localStorage.setItem("lifeos_tasks", JSON.stringify(updated));
        return { tasks: updated };
      });
    }
  },

  deleteTask: async (id) => {
    try {
      await get().apiCall(`/tasks/${id}`, { method: "DELETE" });
      set((state) => {
        const updated = state.tasks.filter((t) => t.id !== id);
        localStorage.setItem("lifeos_tasks", JSON.stringify(updated));
        return { tasks: updated, isOffline: false };
      });
    } catch (err) {
      OfflineSyncService.enqueueAction('DELETE', 'task', id, null);
      set((state) => {
        const updated = state.tasks.filter((t) => t.id !== id);
        localStorage.setItem("lifeos_tasks", JSON.stringify(updated));
        return { tasks: updated };
      });
    }
  },

  fetchHabits: async () => {
    try {
      const data = await get().apiCall("/habits/");
      set({ habits: data, isOffline: false });
      localStorage.setItem("lifeos_habits", JSON.stringify(data));
    } catch (err) {
      set({ habits: getLocalHabits() });
    }
  },

  createHabit: async (habit) => {
    try {
      const data = await get().apiCall("/habits/", {
        method: "POST",
        body: JSON.stringify(habit)
      });
      set((state) => {
        const updated = [...state.habits, data];
        localStorage.setItem("lifeos_habits", JSON.stringify(updated));
        return { habits: updated, isOffline: false };
      });
    } catch (err) {
      const newHabit = {
        id: Date.now(),
        ...habit,
        created_at: new Date().toISOString(),
        logs: []
      };
      OfflineSyncService.enqueueAction('CREATE', 'habit', newHabit.id, newHabit);
      set((state) => {
        const updated = [...state.habits, newHabit];
        localStorage.setItem("lifeos_habits", JSON.stringify(updated));
        return { habits: updated };
      });
    }
  },

  logHabit: async (id, dateStr, status) => {
    try {
      const logData = await get().apiCall(`/habits/${id}/logs`, {
        method: "POST",
        body: JSON.stringify({ date: dateStr, status })
      });
      set((state) => {
        const updated = state.habits.map((h) => {
          if (h.id === id) {
            const index = h.logs.findIndex((l) => l.date === dateStr);
            const logsCopy = [...h.logs];
            if (index > -1) logsCopy[index] = logData;
            else logsCopy.push(logData);
            return { ...h, logs: logsCopy };
          }
          return h;
        });
        localStorage.setItem("lifeos_habits", JSON.stringify(updated));
        return { habits: updated, isOffline: false };
      });
    } catch (err) {
      OfflineSyncService.enqueueAction('UPDATE', 'habit', id, { date: dateStr, status });
      set((state) => {
        const updated = state.habits.map((h) => {
          if (h.id === id) {
            const index = h.logs.findIndex((l) => l.date === dateStr);
            const logsCopy = [...h.logs];
            if (index > -1) {
              logsCopy[index] = { ...logsCopy[index], status };
            } else {
              logsCopy.push({ id: Date.now(), date: dateStr, status });
            }
            return { ...h, logs: logsCopy };
          }
          return h;
        });
        localStorage.setItem("lifeos_habits", JSON.stringify(updated));
        return { habits: updated };
      });
    }
  },

  fetchGoals: async () => {
    try {
      const data = await get().apiCall("/goals/");
      set({ goals: data, isOffline: false });
      localStorage.setItem("lifeos_goals", JSON.stringify(data));
    } catch (err) {
      set({ goals: getLocalGoals() });
    }
  },

  createGoal: async (goal) => {
    try {
      const data = await get().apiCall("/goals/", {
        method: "POST",
        body: JSON.stringify(goal)
      });
      set((state) => {
        const updated = [...state.goals, data];
        localStorage.setItem("lifeos_goals", JSON.stringify(updated));
        return { goals: updated, isOffline: false };
      });
    } catch (err) {
      const newGoal = {
        id: Date.now(),
        ...goal,
        current_value: 0.0,
        status: "Pending",
        milestones: []
      };
      set((state) => {
        const updated = [...state.goals, newGoal];
        localStorage.setItem("lifeos_goals", JSON.stringify(updated));
        return { goals: updated };
      });
    }
  },

  updateGoal: async (id, goalUpdate) => {
    try {
      const data = await get().apiCall(`/goals/${id}`, {
        method: "PUT",
        body: JSON.stringify(goalUpdate)
      });
      set((state) => {
        const updated = state.goals.map((g) => (g.id === id ? data : g));
        localStorage.setItem("lifeos_goals", JSON.stringify(updated));
        return { goals: updated, isOffline: false };
      });
    } catch (err) {
      set((state) => {
        const updated = state.goals.map((g) => {
          if (g.id === id) return { ...g, ...goalUpdate };
          return g;
        });
        localStorage.setItem("lifeos_goals", JSON.stringify(updated));
        return { goals: updated };
      });
    }
  },

  deleteGoal: async (id) => {
    try {
      await get().apiCall(`/goals/${id}`, { method: "DELETE" });
      set((state) => {
        const updated = state.goals.filter((g) => g.id !== id);
        localStorage.setItem("lifeos_goals", JSON.stringify(updated));
        return { goals: updated, isOffline: false };
      });
    } catch (err) {
      set((state) => {
        const updated = state.goals.filter((g) => g.id !== id);
        localStorage.setItem("lifeos_goals", JSON.stringify(updated));
        return { goals: updated };
      });
    }
  },

  addMilestone: async (goalId, milestone) => {
    try {
      await get().apiCall(`/goals/${goalId}/milestones`, {
        method: "POST",
        body: JSON.stringify(milestone)
      });
      // Fetch updated goal values
      get().fetchGoals();
    } catch (err) {
      set((state) => {
        const updated = state.goals.map((g) => {
          if (g.id === goalId) {
            const milestones = [...g.milestones, { id: Date.now(), ...milestone }];
            const completed = milestones.filter((m) => m.is_completed);
            const current_value = (completed.length / milestones.length) * 100;
            return {
              ...g,
              milestones,
              current_value,
              status: current_value >= 100 ? "Completed" : "In Progress"
            };
          }
          return g;
        });
        localStorage.setItem("lifeos_goals", JSON.stringify(updated));
        return { goals: updated };
      });
    }
  },

  fetchNotes: async () => {
    try {
      const data = await get().apiCall("/notes/");
      set({ notes: data, isOffline: false });
      localStorage.setItem("lifeos_notes", JSON.stringify(data));
    } catch (err) {
      set({ notes: getLocalNotes() });
    }
  },

  createNote: async (note) => {
    try {
      const data = await get().apiCall("/notes/", {
        method: "POST",
        body: JSON.stringify(note)
      });
      set((state) => {
        const updated = [...state.notes, data];
        localStorage.setItem("lifeos_notes", JSON.stringify(updated));
        return { notes: updated, isOffline: false };
      });
    } catch (err) {
      const newNote = {
        id: Date.now(),
        ...note,
        created_at: new Date().toISOString()
      };
      OfflineSyncService.enqueueAction('CREATE', 'note', newNote.id, newNote);
      set((state) => {
        const updated = [...state.notes, newNote];
        localStorage.setItem("lifeos_notes", JSON.stringify(updated));
        return { notes: updated };
      });
    }
  },

  deleteNote: async (id) => {
    try {
      await get().apiCall(`/notes/${id}`, { method: "DELETE" });
      set((state) => {
        const updated = state.notes.filter((n) => n.id !== id);
        localStorage.setItem("lifeos_notes", JSON.stringify(updated));
        return { notes: updated, isOffline: false };
      });
    } catch (err) {
      OfflineSyncService.enqueueAction('DELETE', 'note', id, null);
      set((state) => {
        const updated = state.notes.filter((n) => n.id !== id);
        localStorage.setItem("lifeos_notes", JSON.stringify(updated));
        return { notes: updated };
      });
    }
  },

  fetchTrades: async () => {
    try {
      const data = await get().apiCall("/trading/journal");
      set({ trades: data, isOffline: false });
      localStorage.setItem("lifeos_trades", JSON.stringify(data));
    } catch (err) {
      set({ trades: getLocalTrades() });
    }
  },

  logTrade: async (trade) => {
    try {
      const data = await get().apiCall("/trading/journal", {
        method: "POST",
        body: JSON.stringify(trade)
      });
      set((state) => {
        const updated = [...state.trades, data];
        localStorage.setItem("lifeos_trades", JSON.stringify(updated));
        return { trades: updated, isOffline: false };
      });
    } catch (err) {
      const newTrade = {
        id: Date.now(),
        ...trade,
        entry_time: new Date().toISOString(),
        pnl: 0.0
      };
      set((state) => {
        const updated = [...state.trades, newTrade];
        localStorage.setItem("lifeos_trades", JSON.stringify(updated));
        return { trades: updated };
      });
    }
  },

  exitTrade: async (id, tradeUpdate) => {
    try {
      const data = await get().apiCall(`/trading/journal/${id}`, {
        method: "PUT",
        body: JSON.stringify(tradeUpdate)
      });
      set((state) => {
        const updated = state.trades.map((t) => (t.id === id ? data : t));
        localStorage.setItem("lifeos_trades", JSON.stringify(updated));
        return { trades: updated, isOffline: false };
      });
    } catch (err) {
      set((state) => {
        const updated = state.trades.map((t) => {
          if (t.id === id) {
            const exit_price = tradeUpdate.exit_price || t.entry_price;
            const multiplier = t.type.toLowerCase() === "long" ? 1 : -1;
            return {
              ...t,
              exit_price,
              exit_time: new Date().toISOString(),
              psychology_notes: tradeUpdate.psychology_notes || t.psychology_notes,
              pnl: (exit_price - t.entry_price) * t.quantity * multiplier
            };
          }
          return t;
        });
        localStorage.setItem("lifeos_trades", JSON.stringify(updated));
        return { trades: updated };
      });
    }
  },

  fetchPanchang: async (dateStr) => {
    const path = dateStr ? `/panchang/?date_str=${dateStr}` : "/panchang/";
    try {
      const data = await get().apiCall(path);
      set({ panchang: data, isOffline: false });
    } catch (err) {
      // Mock local panchang fallback
      const today = dateStr ? new Date(dateStr) : new Date();
      set({
        panchang: {
          date: today.toISOString().split("T")[0],
          tithi: "Ekadashi (Auspicious)",
          nakshatra: "Rohini",
          yoga: "Siddhi",
          karana: "Bava",
          sunrise: "05:45 AM",
          sunset: "06:42 PM",
          festivals: ["Ekadashi Vrat", "Yoga Sadhana Day"],
          muhurats: [
            "Abhijit Muhurat: 11:45 AM - 12:35 PM",
            "Amrit Kaal: 02:15 PM - 03:50 PM",
            "Rahu Kaal (Avoid): 01:30 PM - 03:00 PM"
          ]
        }
      });
    }
  },

  optimizeSchedule: async () => {
    set({ loadingAI: true });
    try {
      const taskSummaries = get().tasks.map(t => ({
        title: t.title,
        priority: t.priority,
        due_date: t.due_date,
        estimated_time: t.estimated_time
      }));
      const data = await get().apiCall("/ai/schedule", {
        method: "POST",
        body: JSON.stringify({ tasks: taskSummaries })
      });
      set({ aiSchedule: data, loadingAI: false });
    } catch (err) {
      // Local schedule mock calculation
      const tasks = get().tasks;
      set({
        loadingAI: false,
        aiSchedule: {
          schedule: [
            { time: "09:00 AM", activity: "High Priority Focus Blocks", duration_minutes: 90 },
            { time: "10:30 AM", activity: "Email and Administrative Work", duration_minutes: 30 },
            { time: "11:00 AM", activity: "Routine Operations & Habits", duration_minutes: 120 }
          ],
          priority_order: tasks.map(t => t.title),
          focus_blocks: ["Morning Deep Work: 9:00 AM - 10:30 AM", "Afternoon Strategy: 3:00 PM - 4:00 PM"]
        }
      });
    }
  },

  breakdownTaskAI: async (title, description) => {
    set({ loadingAI: true });
    try {
      const data = await get().apiCall("/ai/breakdown", {
        method: "POST",
        body: JSON.stringify({ title, description })
      });
      set({ aiBreakdown: data, loadingAI: false });
    } catch (err) {
      set({
        loadingAI: false,
        aiBreakdown: {
          subtasks: [
            `Scoping & initial outline for "${title}"`,
            "Development of basic framework architecture",
            "Testing implementation against requirements",
            "Styling elements & refining user paths",
            "Completion and manual QA check"
          ],
          checklist: ["Requirements ready", "Design aligned", "Logic tested", "Approved"],
          execution_plan: `Perform sequential sprints to implement ${title}. Start with core structures, then build widgets and UI details.`
        }
      });
    }
  }
}));
