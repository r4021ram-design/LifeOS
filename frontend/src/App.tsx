import React, { useState, useEffect, useRef } from 'react';
import { 
  CheckSquare, Calendar, RefreshCw, Zap, TrendingUp, BookOpen, 
  Clock, Activity, Check, Plus, Trash, Lock, LogOut, Loader, Sparkles, AlertCircle, Search,
  ChevronDown, ChevronUp, Mic, Send, User, Sliders, X
} from 'lucide-react';
import { useLifeOSStore, API_BASE } from './store/useLifeOSStore';
import type { Note } from './store/useLifeOSStore';
import { NativeService, BiometricService, OfflineSyncService } from './services/nativeService';
import './App.css';

export default function App() {
  const store = useLifeOSStore();
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authName, setAuthName] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // Form states
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState('Medium');
  const [newTaskDueDate, setNewTaskDueDate] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');

  const [newHabitName, setNewHabitName] = useState('');
  const [newHabitGoal, setNewHabitGoal] = useState('');

  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [newGoalCategory, setNewGoalCategory] = useState('Personal');

  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [newNoteContent, setNewNoteContent] = useState('');
  const [_selectedNote, setSelectedNote] = useState<Note | null>(null);

  const [newTradeTicker, setNewTradeTicker] = useState('');
  const [newTradeType, setNewTradeType] = useState('Long');
  const [newTradeQty, setNewTradeQty] = useState('');
  const [newTradeEntry, setNewTradeEntry] = useState('');
  const [newTradeStrategy, setNewTradeStrategy] = useState('');
  const [closingTradeId, setClosingTradeId] = useState<number | null>(null);
  const [tradeExitPrice, setTradeExitPrice] = useState('');

  const [aiBreakdownInput, setAiBreakdownInput] = useState('');

  // Command Palette & Quick Capture Modal
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [commandSearch, setCommandSearch] = useState('');
  const [quickCaptureText, setQuickCaptureText] = useState('');
  const [isQuickCaptureOpen, setIsQuickCaptureOpen] = useState(false);
  const [quickCaptureType, setQuickCaptureType] = useState('Task'); // Task, Reminder, Habit, Note
  const commandPaletteInputRef = useRef<HTMLInputElement>(null);

  // Mobile navigation & Drawer
  const [isMoreDrawerOpen, setIsMoreDrawerOpen] = useState(false);
  
  // Collapsible home sections states
  const [collapseTodayFocus, setCollapseTodayFocus] = useState(false);
  const [collapseHabits, setCollapseHabits] = useState(false);
  const [collapseGoals, setCollapseGoals] = useState(false);
  const [collapsePanchang, setCollapsePanchang] = useState(false);

  // AI Chat Messages History
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{sender: 'user' | 'ai'; text: string; details?: any}>>([
    { 
      sender: 'ai', 
      text: "Hello! I am your LifeOS AI Assistant. I can help optimize your schedule, breakdown tasks, or coach you on goals. What would you like to plan today?" 
    }
  ]);

  // Voice input states
  const [isListening, setIsListening] = useState(false);
  const [speechLanguage, setSpeechLanguage] = useState<'hi-IN' | 'gu-IN' | 'en-US'>('hi-IN');
  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      
      rec.onstart = () => {
        setIsListening(true);
      };
      
      rec.onend = () => {
        setIsListening(false);
      };
      
      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setChatInput(prev => prev + (prev ? ' ' : '') + transcript);
      };
      
      rec.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };
      
      recognitionRef.current = rec;
    }
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.lang = speechLanguage;
      recognitionRef.current.start();
    }
  };

  const [touchStart, setTouchStart] = useState<number | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (window.scrollY === 0) {
      setTouchStart(e.targetTouches[0].clientY);
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStart === null) return;
    const touchEnd = e.changedTouches[0].clientY;
    const diff = touchEnd - touchStart;
    
    if (diff > 140) { // Pull down threshold
      store.fetchTasks();
      store.fetchHabits();
      store.fetchGoals();
      store.fetchNotes();
      store.fetchTrades();
      store.fetchPanchang();
      console.log("Pull-to-refresh: Syncing all data...");
    }
    setTouchStart(null);
  };

  const [isPushAvailable, setIsPushAvailable] = useState(false);
  const [syncStatus, setSyncStatus] = useState<'Connected' | 'Offline' | 'Syncing...' | 'Synced'>('Connected');

  // Native initializations (FCM, SQLite, Keyboard)
  useEffect(() => {
    const initNative = async () => {
      const res = await NativeService.initialize(store.token);
      setIsPushAvailable(res.pushAvailable);
    };
    initNative();
  }, [store.token]);

  // Restore JWT session on startup
  useEffect(() => {
    const restoreSession = async () => {
      const savedToken = await NativeService.getSecureItem("lifeos_token");
      const savedUserStr = await NativeService.getSecureItem("lifeos_user");
      if (savedToken) {
        store.setToken(savedToken);
        if (savedUserStr) {
          store.setUser(JSON.parse(savedUserStr));
        }
      }
    };
    restoreSession();
  }, []);

  // Biometric auto-login on startup
  useEffect(() => {
    const checkBiometricLogin = async () => {
      const isBiometricsEnabled = localStorage.getItem('biometrics_enabled') === 'true';
      const storedEmail = localStorage.getItem('auth_email');
      
      if (isBiometricsEnabled && storedEmail) {
        const token = await BiometricService.getStoredToken(storedEmail);
        if (token) {
          store.setToken(token);
          store.setUser({ email: storedEmail });
          store.setOfflineMode(false);
        }
      }
    };
    checkBiometricLogin();
  }, []);

  // Network status listeners
  useEffect(() => {
    const handleOnline = async () => {
      store.setOfflineMode(false);
      setSyncStatus('Syncing...');
      if (store.token) {
        await OfflineSyncService.syncWithBackend(store.token);
      }
      setSyncStatus('Synced');
      setTimeout(() => setSyncStatus('Connected'), 3000);
    };

    const handleOffline = () => {
      store.setOfflineMode(true);
      setSyncStatus('Offline');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    if (!navigator.onLine) {
      handleOffline();
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [store.token]);

  // Hardware back button registration
  useEffect(() => {
    NativeService.registerBackButtonHandler(() => {
      let closedAny = false;
      if (isMoreDrawerOpen) {
        setIsMoreDrawerOpen(false);
        closedAny = true;
      }
      if (isQuickCaptureOpen) {
        setIsQuickCaptureOpen(false);
        closedAny = true;
      }
      if (isCommandPaletteOpen) {
        setIsCommandPaletteOpen(false);
        closedAny = true;
      }
      return closedAny;
    });
  }, [isMoreDrawerOpen, isQuickCaptureOpen, isCommandPaletteOpen]);

  // Deep link listener registration
  useEffect(() => {
    NativeService.registerDeepLinkHandler();
  }, []);

  // Share intent custom event listener
  useEffect(() => {
    const handleShareEvent = (event: any) => {
      console.log('Received share event:', event);
      const data = event.detail || event || {};
      const text = data.text;
      const image = data.image;
      if (text) {
        store.createNote({
          title: 'Quick Share Note',
          content: text
        });
        store.setActiveTab('notes');
      } else if (image) {
        store.createNote({
          title: 'Quick Share Image',
          content: `Shared image location: ${image}`
        });
        store.setActiveTab('notes');
      }
    };
    window.addEventListener('shareIntoApp', handleShareEvent as any);
    return () => window.removeEventListener('shareIntoApp', handleShareEvent as any);
  }, []);

  // Initial data loading
  useEffect(() => {
    if (store.token) {
      store.fetchTasks();
      store.fetchHabits();
      store.fetchGoals();
      store.fetchNotes();
      store.fetchTrades();
      store.fetchPanchang();
      // Auto-trigger sync queue on startup if online
      OfflineSyncService.syncWithBackend(store.token);
    } else {
      store.fetchPanchang();
    }
  }, [store.token]);

  // Command Palette Keyboard shortcut listener (Ctrl+K / Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setIsCommandPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Auto focus input when palette opens
  useEffect(() => {
    if (isCommandPaletteOpen && commandPaletteInputRef.current) {
      commandPaletteInputRef.current.focus();
    }
  }, [isCommandPaletteOpen]);

  // Auth Handlers
  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    const url = isRegistering ? '/auth/signup' : '/auth/login';
    const body = isRegistering 
      ? { email: authEmail, password: authPassword, full_name: authName }
      : { email: authEmail, password: authPassword };

    try {
      const res = await fetch(`${API_BASE}${url}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      if (isRegistering) {
        setIsRegistering(false);
        setAuthError('Registration successful. Please login.');
      } else {
        store.setToken(data.access_token);
        store.setUser({ email: authEmail });
        store.setOfflineMode(false);
      }
    } catch (err: any) {
      setAuthError(err.message || 'Connection error. Running locally.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSkipAuth = () => {
    store.setToken("local-demo-token");
    store.setUser({ email: "local.user@lifeos.local", full_name: "Local Specialist" });
    store.setOfflineMode(true);
  };

  const handleLogout = () => {
    store.setToken(null);
    store.setUser(null);
    setIsMoreDrawerOpen(false);
  };

  // Quick Capture task creation
  const handleQuickCapture = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickCaptureText.trim()) return;
    store.createTask({
      title: quickCaptureText.trim(),
      priority: 'Medium',
      due_date: new Date().toISOString().split('T')[0]
    });
    setQuickCaptureText('');
  };

  // FAB Dialog Quick Capture submission
  const handleFABQuickCaptureSubmit = () => {
    if (!quickCaptureText.trim()) return;
    
    if (quickCaptureType === 'Task') {
      store.createTask({
        title: quickCaptureText.trim(),
        priority: 'Medium',
        due_date: new Date().toISOString().split('T')[0]
      });
    } else if (quickCaptureType === 'Reminder') {
      store.createTask({
        title: `[Reminder] ${quickCaptureText.trim()}`,
        priority: 'High',
        due_date: new Date().toISOString().split('T')[0],
        reminder_rule: "5 minutes before"
      });
    } else if (quickCaptureType === 'Habit') {
      store.createHabit({
        name: quickCaptureText.trim(),
        goal: 'Daily routine'
      });
    } else if (quickCaptureType === 'Note') {
      store.createNote({
        title: quickCaptureText.trim(),
        content: 'Quick captured note content...'
      });
    }
    
    setQuickCaptureText('');
    setIsQuickCaptureOpen(false);
  };

  // Send AI Chat message
  const handleSendChatMessage = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { sender: 'user', text: userMsg }]);

    // Add thinking response
    setChatMessages(prev => [...prev, { sender: 'ai', text: "Processing your request with LifeOS AI..." }]);

    try {
      if (userMsg.toLowerCase().includes('optimize') || userMsg.toLowerCase().includes('schedule')) {
        await store.optimizeSchedule();
        setChatMessages(prev => {
          const filtered = prev.slice(0, -1);
          return [...filtered, { 
            sender: 'ai', 
            text: "Here is your optimized daily focus schedule aligned with solar Muhurats:",
            details: store.aiSchedule 
          }];
        });
      } else {
        await store.breakdownTaskAI(userMsg);
        setChatMessages(prev => {
          const filtered = prev.slice(0, -1);
          return [...filtered, { 
            sender: 'ai', 
            text: `Here is the structured breakdown for: "${userMsg}"`,
            details: store.aiBreakdown 
          }];
        });
      }
    } catch (e) {
      setChatMessages(prev => {
        const filtered = prev.slice(0, -1);
        return [...filtered, { sender: 'ai', text: "Sorry, I couldn't reach the AI planner backend. Here is a local rule-based focus block schedule optimized for today." }];
      });
    }
  };

  // Filter items for command palette search
  const getFilteredCommands = () => {
    if (!commandSearch.trim()) return [];
    const searchLower = commandSearch.toLowerCase();
    
    const results: { type: string; title: string; subtitle?: string; action: () => void }[] = [];

    // Filter Tasks
    store.tasks
      .filter((t) => t.title.toLowerCase().includes(searchLower))
      .forEach((t) => {
        results.push({
          type: 'Task',
          title: t.title,
          subtitle: `Priority: ${t.priority} | Status: ${t.status}`,
          action: () => {
            store.setActiveTab('tasks');
            setIsCommandPaletteOpen(false);
          }
        });
      });

    // Filter Notes
    store.notes
      .filter((n) => n.title.toLowerCase().includes(searchLower))
      .forEach((n) => {
        results.push({
          type: 'Note',
          title: n.title,
          subtitle: `Tags: ${n.tags || 'none'}`,
          action: () => {
            setSelectedNote(n);
            store.setActiveTab('notes');
            setIsCommandPaletteOpen(false);
          }
        });
      });

    // Filter Habits
    store.habits
      .filter((h) => h.name.toLowerCase().includes(searchLower))
      .forEach((h) => {
        results.push({
          type: 'Habit',
          title: h.name,
          subtitle: `Goal: ${h.goal || 'none'}`,
          action: () => {
            store.setActiveTab('habits');
            setIsCommandPaletteOpen(false);
          }
        });
      });

    // Filter Goals
    store.goals
      .filter((g) => g.title.toLowerCase().includes(searchLower))
      .forEach((g) => {
        results.push({
          type: 'Goal',
          title: g.title,
          subtitle: `Progress: ${g.current_value.toFixed(0)}%`,
          action: () => {
            store.setActiveTab('goals');
            setIsCommandPaletteOpen(false);
          }
        });
      });

    return results.slice(0, 8); // Cap results at 8
  };

  const filteredCommands = getFilteredCommands();

  // Authentication View
  if (!store.token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#050508] p-4 relative overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-900/20 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-900/20 rounded-full blur-3xl pointer-events-none"></div>

        <div className="glass-panel w-full max-w-md p-6 md:p-8 relative z-10">
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 bg-purple-600/20 border border-purple-500/30 rounded-2xl flex items-center justify-center mb-4">
              <Zap className="w-8 h-8 text-purple-400" />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">LifeOS AI</h1>
            <p className="text-sm text-gray-400 text-center">Institutional Grade Productivity & Planner Engine</p>
          </div>

          <form onSubmit={handleAuth} className="space-y-4">
            {isRegistering && (
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Full Name</label>
                <input 
                  type="text" 
                  className="w-full glass-input"
                  placeholder="John Doe" 
                  value={authName}
                  onChange={(e) => setAuthName(e.target.value)}
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Email Address</label>
              <input 
                type="email" 
                className="w-full glass-input text-base md:text-sm"
                placeholder="name@company.com" 
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Password</label>
              <input 
                type="password" 
                className="w-full glass-input text-base md:text-sm"
                placeholder="••••••••" 
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                required
              />
            </div>

            {authError && (
              <div className="flex items-center gap-2 text-sm text-amber-400 bg-amber-500/10 border border-amber-500/20 p-3 rounded-lg">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{authError}</span>
              </div>
            )}

            <button 
              type="submit" 
              className="w-full py-3 px-4 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg shadow-lg shadow-purple-600/20 transition-all flex items-center justify-center gap-2 touch-target"
              disabled={authLoading}
            >
              {authLoading ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>{isRegistering ? 'Register Account' : 'Authenticate Credentials'}</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 flex flex-col gap-3 text-center">
            <button 
              onClick={() => setIsRegistering(!isRegistering)} 
              className="text-xs text-purple-400 hover:text-purple-300 font-medium py-2"
            >
              {isRegistering ? 'Already have an account? Sign In' : 'Create new institutional profile'}
            </button>

            <div className="border-t border-white/5 my-2"></div>

            <button 
              onClick={handleSkipAuth} 
              className="text-xs text-gray-400 hover:text-gray-300 flex items-center justify-center gap-1.5 py-2 touch-target"
            >
              <Sparkles className="w-3.5 h-3.5 text-yellow-500 animate-pulse" />
              <span>Explore in Local Offline Mode</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Sidebar navigation options (Desktop)
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare },
    { id: 'habits', label: 'Habits', icon: Clock },
    { id: 'goals', label: 'Goals', icon: Zap },
    { id: 'notes', label: 'Notes', icon: BookOpen },
    { id: 'trading', label: 'Trading Journal', icon: TrendingUp },
    { id: 'ai', label: 'AI Planner', icon: Sparkles },
  ];

  // Mobile Bottom Navigation tabs
  const mobileNavItems = [
    { id: 'dashboard', label: 'Home', icon: Activity },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare },
    { id: 'calendar_agenda', label: 'Calendar', icon: Calendar },
    { id: 'ai_assistant', label: 'AI', icon: Sparkles },
    { id: 'more', label: 'More', icon: Sliders },
  ];

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[#030303] text-gray-200" onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
      
      {/* Raycast-style Command Palette Dialog Modal */}
      {isCommandPaletteOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-2xl glass-panel shadow-2xl overflow-hidden border border-white/10 flex flex-col animate-fade-in">
            <div className="flex items-center px-4 py-3.5 border-b border-white/5 gap-3">
              <Search className="w-5 h-5 text-gray-400" />
              <input 
                ref={commandPaletteInputRef}
                type="text" 
                className="flex-1 bg-transparent border-none outline-none text-white text-base placeholder-gray-500"
                placeholder="Search tasks, notes, habits, goals... (Esc to close)"
                value={commandSearch}
                onChange={(e) => setCommandSearch(e.target.value)}
              />
              <span className="text-[10px] uppercase font-bold text-gray-500 px-2 py-0.5 rounded border border-white/5 bg-white/2">Raycast</span>
            </div>

            {/* Results body */}
            <div className="max-h-[350px] overflow-y-auto p-2 space-y-1">
              {filteredCommands.map((cmd, idx) => (
                <button
                  key={idx}
                  onClick={cmd.action}
                  className="w-full text-left px-4 py-3 rounded-lg flex items-center justify-between hover:bg-purple-600/10 hover:text-purple-400 group transition-all touch-target"
                >
                  <div>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-gray-400 group-hover:text-purple-300 mr-3">
                      {cmd.type}
                    </span>
                    <span className="text-sm font-semibold text-white group-hover:text-purple-300">{cmd.title}</span>
                  </div>
                  <span className="text-xs text-gray-500 group-hover:text-purple-400 font-medium">{cmd.subtitle}</span>
                </button>
              ))}
              {commandSearch.trim() && filteredCommands.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-6">No matching records found.</p>
              )}
              {!commandSearch.trim() && (
                <div className="p-4 space-y-3">
                  <p className="text-xs font-bold uppercase tracking-wider text-gray-500">Quick Commands & Navigation</p>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                    <button onClick={() => { store.setActiveTab('tasks'); setIsCommandPaletteOpen(false); }} className="px-3 py-2 text-left rounded bg-white/2 border border-white/5 hover:bg-white/5 hover:text-white touch-target">Go to Tasks Panel</button>
                    <button onClick={() => { store.setActiveTab('habits'); setIsCommandPaletteOpen(false); }} className="px-3 py-2 text-left rounded bg-white/2 border border-white/5 hover:bg-white/5 hover:text-white touch-target">Go to Habits Tracking</button>
                    <button onClick={() => { store.setActiveTab('trading'); setIsCommandPaletteOpen(false); }} className="px-3 py-2 text-left rounded bg-white/2 border border-white/5 hover:bg-white/5 hover:text-white touch-target">Go to Trading Journal</button>
                    <button onClick={() => { store.setActiveTab('ai'); setIsCommandPaletteOpen(false); }} className="px-3 py-2 text-left rounded bg-white/2 border border-white/5 hover:bg-white/5 hover:text-white touch-target">Go to AI Scheduler</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Floating Action Button (FAB) for Mobile Quick Capture */}
      <button 
        onClick={() => setIsQuickCaptureOpen(true)}
        className="fixed md:hidden bottom-20 right-4 w-14 h-14 bg-purple-600 hover:bg-purple-700 text-white rounded-full flex items-center justify-center shadow-lg shadow-purple-600/35 z-40 border border-purple-500/30 transition-transform active:scale-95"
        aria-label="Quick Capture Item"
      >
        <Plus className="w-6 h-6" />
      </button>

      {/* Quick Capture Overlay Modal */}
      {isQuickCaptureOpen && (
        <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
          <div className="w-full max-w-md glass-panel p-6 space-y-4 rounded-t-2xl md:rounded-2xl border border-white/10 animate-slide-up">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <h3 className="font-bold text-white text-lg">⚡ Quick Capture</h3>
              <button onClick={() => setIsQuickCaptureOpen(false)} className="p-1.5 hover:bg-white/5 rounded-full text-gray-400 touch-target">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Type selector */}
            <div className="grid grid-cols-4 gap-2">
              {['Task', 'Reminder', 'Habit', 'Note'].map((type) => (
                <button
                  key={type}
                  onClick={() => setQuickCaptureType(type)}
                  className={`py-2 text-xs font-bold rounded-lg border transition-all touch-target ${
                    quickCaptureType === type 
                      ? 'bg-purple-600/20 border-purple-500 text-purple-300' 
                      : 'bg-white/2 border-white/5 text-gray-400 hover:bg-white/5'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            <div className="space-y-3">
              <label className="text-xs text-gray-400 block font-semibold uppercase tracking-wider">Title / Content</label>
              <input 
                type="text" 
                className="w-full glass-input text-base"
                placeholder={`Type your new ${quickCaptureType.toLowerCase()}...`}
                value={quickCaptureText}
                onChange={(e) => setQuickCaptureText(e.target.value)}
                autoFocus
              />
            </div>

            <button
              onClick={handleFABQuickCaptureSubmit}
              className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-1 touch-target shadow-lg shadow-purple-600/15"
            >
              <Check className="w-4 h-4" />
              Add {quickCaptureType}
            </button>
          </div>
        </div>
      )}

      {/* Mobile Header */}
      <header className="flex md:hidden min-h-[3.5rem] pt-[env(safe-area-inset-top)] items-center justify-between px-4 border-b border-white/5 bg-[#09090d]/65 backdrop-blur-md sticky top-0 z-30 shrink-0">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-purple-500 fill-purple-500/20" />
          <span className="font-bold text-white tracking-wide text-base">LifeOS AI</span>
        </div>
        <div className="flex items-center gap-3">
          {store.panchang && (
            <span className="text-[10px] bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2.5 py-1 rounded font-medium font-mono">
              {store.panchang.tithi}
            </span>
          )}
          <button 
            onClick={() => setIsCommandPaletteOpen(true)}
            className="p-2 hover:bg-white/5 rounded-md text-gray-400 touch-target"
            title="Global Search"
          >
            <Search className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 border-r border-white/5 bg-[#09090d]/65 backdrop-blur-md flex-col justify-between shrink-0">
        <div>
          <div className="h-16 border-b border-white/5 flex items-center px-6 gap-3">
            <Zap className="w-6 h-6 text-purple-500 fill-purple-500/20" />
            <span className="font-bold text-white tracking-wide text-lg">LifeOS AI</span>
          </div>

          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => store.setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all touch-target ${
                    store.activeTab === item.id
                      ? 'bg-purple-600/10 text-purple-400 border-l-2 border-purple-500'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* User Footer Profile */}
        <div className="p-4 border-t border-white/5 bg-black/25 flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div className="truncate">
              <p className="text-xs text-gray-400">Authenticated user</p>
              <p className="text-sm font-bold text-white truncate">{store.user?.email}</p>
            </div>
            <button 
              onClick={handleLogout}
              className="p-2 hover:bg-white/5 rounded-md text-gray-400 hover:text-white touch-target"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
          
          <div className="flex items-center gap-2 mt-2">
            <div className={`w-2.5 h-2.5 rounded-full ${
              syncStatus === 'Offline' ? 'bg-amber-500 animate-pulse' :
              syncStatus === 'Syncing...' ? 'bg-blue-400 animate-spin' :
              syncStatus === 'Synced' ? 'bg-purple-400' : 'bg-emerald-500'
            }`}></div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-gray-400">
              {syncStatus === 'Offline' ? 'Offline Mode' :
               syncStatus === 'Syncing...' ? 'Syncing...' :
               syncStatus === 'Synced' ? 'Synced' : 'Cloud Connected'}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Workspace */}
      <main className="flex-1 flex flex-col overflow-y-auto max-h-screen">
        
        {/* Top Navbar (Desktop) */}
        <header className="hidden md:flex h-16 border-b border-white/5 items-center justify-between px-8 bg-[#09090d]/30 backdrop-blur-sm sticky top-0 z-20 shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-bold text-white uppercase tracking-wider">
              {navItems.find(n => n.id === store.activeTab)?.label || store.activeTab}
            </h2>
            <button 
              onClick={() => setIsCommandPaletteOpen(true)}
              className="px-2.5 py-1 bg-white/5 border border-white/10 hover:bg-white/10 text-[10px] text-gray-400 hover:text-white rounded font-mono transition-all"
            >
              Press Ctrl + K to search
            </button>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => {
                store.fetchTasks();
                store.fetchHabits();
                store.fetchGoals();
                store.fetchNotes();
                store.fetchTrades();
                store.fetchPanchang();
              }}
              className="p-2 hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-all flex items-center gap-1.5 text-xs font-semibold"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Sync Data
            </button>
            <span className="text-xs text-gray-500 font-mono">
              {new Date().toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}
            </span>
          </div>
        </header>

        {/* Quick Capture Inline Task Bar (Desktop) */}
        <div className="hidden md:block px-8 pt-6">
          <form onSubmit={handleQuickCapture} className="glass-panel p-2 flex items-center gap-3">
            <div className="w-5 h-5 rounded-md border border-purple-500/30 flex items-center justify-center bg-purple-600/10">
              <Zap className="w-3 h-3 text-purple-400" />
            </div>
            <input 
              type="text" 
              className="flex-1 bg-transparent border-none outline-none text-sm text-white placeholder-gray-500" 
              placeholder="⚡ Quick capture: Type task description and press Enter..."
              value={quickCaptureText}
              onChange={(e) => setQuickCaptureText(e.target.value)}
            />
            <button 
              type="submit" 
              className="px-3 py-1 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded text-xs font-bold transition-all border border-purple-500/20"
            >
              Add Task
            </button>
          </form>
        </div>

        {/* Dynamic Content Panel */}
        <div className="p-4 md:p-8 pb-24 md:pb-8 flex-1">
          
          {/* TAB 1: Dashboard (Home Dashboard Redesign) */}
          {(store.activeTab === 'dashboard' || store.activeTab === 'dashboard_home') && (
            <div className="space-y-6">
              
              {/* Today's Focus Widget */}
              <div className="glass-panel p-5">
                <div 
                  className="flex items-center justify-between mb-4 border-b border-white/5 pb-2 cursor-pointer"
                  onClick={() => setCollapseTodayFocus(!collapseTodayFocus)}
                >
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-purple-400" />
                    <h3 className="font-semibold text-white">Today's Focus & Plannings</h3>
                  </div>
                  {collapseTodayFocus ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronUp className="w-4 h-4 text-gray-500" />}
                </div>

                {!collapseTodayFocus && (
                  <div className="space-y-3">
                    {store.tasks.filter(t => t.priority === "Critical" || t.priority === "High").slice(0, 3).map((task) => (
                      <div key={task.id} className="glass-card p-3.5 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <button 
                            onClick={() => store.updateTask(task.id, { status: task.status === "Completed" ? "Pending" : "Completed" })}
                            className={`w-6 h-6 border rounded-md flex items-center justify-center transition-all ${
                              task.status === "Completed" ? 'bg-purple-600 border-purple-500 text-white' : 'border-white/20 hover:border-purple-500'
                            }`}
                          >
                            {task.status === "Completed" && <Check className="w-3.5 h-3.5 text-white" />}
                          </button>
                          <div>
                            <p className={`text-sm font-semibold text-white ${task.status === "Completed" ? "line-through text-gray-500" : ""}`}>{task.title}</p>
                            <p className="text-xs text-gray-400">{task.due_date || 'No due date'}</p>
                          </div>
                        </div>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-semibold uppercase ${
                          task.priority === "Critical" ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-orange-500/20 text-orange-400 border border-orange-500/30"
                        }`}>
                          {task.priority}
                        </span>
                      </div>
                    ))}
                    {store.tasks.filter(t => t.priority === "Critical" || t.priority === "High").length === 0 && (
                      <p className="text-sm text-gray-500 py-4 text-center">No critical focus tasks remaining today.</p>
                    )}
                  </div>
                )}
              </div>

              {/* Grid: Panchang sacred widget & AI suggestions */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Panchang Widget */}
                <div className="glass-panel p-5 col-span-2">
                  <div 
                    className="flex items-center justify-between mb-4 border-b border-white/5 pb-2 cursor-pointer"
                    onClick={() => setCollapsePanchang(!collapsePanchang)}
                  >
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-purple-400" />
                      <h3 className="font-semibold text-white">Hindu Panchang Widget</h3>
                    </div>
                    {collapsePanchang ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronUp className="w-4 h-4 text-gray-500" />}
                  </div>

                  {!collapsePanchang && (
                    store.panchang ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-3">
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <span className="text-gray-400">Tithi:</span>
                            <span className="font-semibold text-white">{store.panchang.tithi}</span>
                            <span className="text-gray-400">Nakshatra:</span>
                            <span className="font-semibold text-white">{store.panchang.nakshatra}</span>
                            <span className="text-gray-400">Yoga:</span>
                            <span className="font-semibold text-white">{store.panchang.yoga}</span>
                            <span className="text-gray-400">Karana:</span>
                            <span className="font-semibold text-white">{store.panchang.karana}</span>
                          </div>
                          <div className="border-t border-white/5 pt-3 flex items-center justify-between text-xs text-gray-400">
                            <span>Sunrise: <strong className="text-white">{store.panchang.sunrise}</strong></span>
                            <span>Sunset: <strong className="text-white">{store.panchang.sunset}</strong></span>
                          </div>
                        </div>

                        <div className="space-y-3 border-t md:border-t-0 md:border-l border-white/5 pt-3 md:pt-0 md:pl-6">
                          <p className="text-xs font-bold uppercase tracking-wider text-purple-400">Todays Festivals</p>
                          {store.panchang.festivals?.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {store.panchang.festivals.map((fest, idx) => (
                                <span key={idx} className="text-xs bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-2 py-0.5 rounded font-medium">
                                  {fest}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs text-gray-500">No major festivals observed today.</p>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-center p-6"><Loader className="w-6 h-6 animate-spin text-purple-500" /></div>
                    )
                  )}
                </div>

                {/* AI Suggestions Box */}
                <div className="glass-panel p-5 flex flex-col justify-between">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-5 h-5 text-yellow-500 animate-pulse" />
                    <h3 className="font-semibold text-white">AI Assistant Suggestions</h3>
                  </div>
                  <p className="text-sm text-gray-400 mb-4 leading-relaxed">
                    You have {store.tasks.filter(t => t.status === "Pending").length} pending tasks. High focus block suggested in accordance with daily Panchang cosmic Muhurats.
                  </p>
                  <button 
                    onClick={() => store.setActiveTab('ai')}
                    className="w-full py-3 bg-white/5 hover:bg-white/10 text-white rounded-lg text-xs font-bold border border-white/10 transition-all touch-target"
                  >
                    Open AI Planning
                  </button>
                </div>
              </div>

              {/* Habits Progress & Goals Collapsibles */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Habit Progress Widget */}
                <div className="glass-panel p-5">
                  <div 
                    className="flex items-center justify-between mb-4 cursor-pointer"
                    onClick={() => setCollapseHabits(!collapseHabits)}
                  >
                    <h3 className="font-semibold text-white">Habit Progress</h3>
                    {collapseHabits ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronUp className="w-4 h-4 text-gray-500" />}
                  </div>

                  {!collapseHabits && (
                    <div className="space-y-4">
                      {store.habits.slice(0, 3).map((habit) => {
                        const completions = habit.logs?.filter(l => l.status === "Completed").length || 0;
                        return (
                          <div key={habit.id} className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-white font-medium">{habit.name}</span>
                              <span className="text-xs text-purple-400 font-bold">{completions} completions</span>
                            </div>
                            <div className="flex gap-2">
                              {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, idx) => (
                                <div key={idx} className="flex-1">
                                  <div className={`h-8 rounded flex items-center justify-center text-xs font-bold border ${
                                    habit.logs?.some(l => l.status === "Completed") 
                                      ? 'bg-purple-600/30 text-purple-300 border-purple-500/30' 
                                      : 'bg-white/5 text-gray-500 border-transparent'
                                  }`}>
                                    {day}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                      {store.habits.length === 0 && (
                        <p className="text-sm text-gray-500 py-4 text-center">No habits added yet.</p>
                      )}
                    </div>
                  )}
                </div>

                {/* Goal Progress Widget */}
                <div className="glass-panel p-5">
                  <div 
                    className="flex items-center justify-between mb-4 cursor-pointer"
                    onClick={() => setCollapseGoals(!collapseGoals)}
                  >
                    <h3 className="font-semibold text-white">SMART Goal Metrics</h3>
                    {collapseGoals ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronUp className="w-4 h-4 text-gray-500" />}
                  </div>

                  {!collapseGoals && (
                    <div className="space-y-4">
                      {store.goals.slice(0, 3).map((goal) => (
                        <div key={goal.id} className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-white font-medium">{goal.title}</span>
                            <span className="text-xs text-purple-400 font-bold">{goal.current_value.toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-white/5 rounded-full h-2">
                            <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${goal.current_value}%` }}></div>
                          </div>
                        </div>
                      ))}
                      {store.goals.length === 0 && (
                        <p className="text-sm text-gray-500 py-4 text-center">No goals registered yet.</p>
                      )}
                    </div>
                  )}
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: Tasks Management */}
          {store.activeTab === 'tasks' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Form Input Card (Collapsible on mobile) */}
              <div className="glass-panel p-5 h-fit space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Add New Task</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Task Title*</label>
                    <input 
                      type="text" 
                      className="w-full glass-input text-base md:text-sm"
                      placeholder="Scaffold postgres database" 
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Description</label>
                    <textarea 
                      className="w-full glass-input h-16 resize-none text-base md:text-sm"
                      placeholder="Add brief details..."
                      value={newTaskDesc}
                      onChange={(e) => setNewTaskDesc(e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Priority</label>
                      <select 
                        className="w-full glass-input text-base md:text-sm"
                        value={newTaskPriority}
                        onChange={(e) => setNewTaskPriority(e.target.value)}
                      >
                        <option value="Critical">Critical</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Due Date</label>
                      <input 
                        type="date" 
                        className="w-full glass-input text-base md:text-sm"
                        value={newTaskDueDate}
                        onChange={(e) => setNewTaskDueDate(e.target.value)}
                      />
                    </div>
                  </div>
                  <button 
                    onClick={() => {
                      if (!newTaskTitle) return;
                      store.createTask({
                        title: newTaskTitle,
                        description: newTaskDesc,
                        priority: newTaskPriority,
                        due_date: newTaskDueDate
                      });
                      setNewTaskTitle('');
                      setNewTaskDesc('');
                      setNewTaskDueDate('');
                    }}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg shadow-lg shadow-purple-600/15 transition-all flex items-center justify-center gap-1 touch-target"
                  >
                    <Plus className="w-4 h-4" />
                    Create Task
                  </button>
                </div>
              </div>

              {/* Task Registry list */}
              <div className="glass-panel p-5 col-span-2 space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Active Task Registry</h3>
                
                {/* Swipe guides for mobile */}
                <div className="block md:hidden text-[10px] text-gray-500 font-medium text-center">
                  💡 Tip: Click checkbox to complete, trash icon to delete.
                </div>

                <div className="space-y-3">
                  {store.tasks.map((task) => (
                    <div key={task.id} className="glass-card p-4 flex items-center justify-between border-l-4 border-l-purple-500 animate-fade-in">
                      <div className="flex items-center gap-4 flex-1 mr-2">
                        <button 
                          onClick={() => store.updateTask(task.id, { status: task.status === "Completed" ? "Pending" : "Completed" })}
                          className={`w-6 h-6 border rounded-md flex items-center justify-center transition-all touch-target shrink-0 ${
                            task.status === "Completed" ? 'bg-purple-600 border-purple-500 text-white' : 'border-white/20 hover:border-purple-500'
                          }`}
                        >
                          {task.status === "Completed" && <Check className="w-4 h-4" />}
                        </button>
                        <div className="min-w-0">
                          <p className={`text-sm font-semibold text-white truncate ${task.status === "Completed" ? "line-through text-gray-500" : ""}`}>
                            {task.title}
                          </p>
                          <p className="text-xs text-gray-400 mt-1 truncate">{task.description}</p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {task.due_date && (
                              <span className="text-[10px] bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded text-purple-300 font-mono">
                                Due: {task.due_date}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        <span className={`text-[10px] px-2 py-0.5 rounded font-semibold uppercase ${
                          task.priority === "Critical" ? "bg-red-500/20 text-red-400 border border-red-500/30" :
                          task.priority === "High" ? "bg-orange-500/20 text-orange-400 border border-orange-500/30" :
                          task.priority === "Medium" ? "bg-blue-500/20 text-blue-400 border border-blue-500/30" :
                          "bg-gray-500/20 text-gray-400 border border-gray-500/30"
                        }`}>
                          {task.priority}
                        </span>
                        <button 
                          onClick={() => store.deleteTask(task.id)}
                          className="text-gray-500 hover:text-red-400 p-2 rounded-md transition-all touch-target"
                          title="Delete Task"
                        >
                          <Trash className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                  {store.tasks.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-8">No tasks recorded. Add one above.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Habits Tracker */}
          {store.activeTab === 'habits' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="glass-panel p-5 h-fit space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Track New Habit</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Habit Name*</label>
                    <input 
                      type="text" 
                      className="w-full glass-input text-base md:text-sm"
                      placeholder="Meditation / Gym / Read" 
                      value={newHabitName}
                      onChange={(e) => setNewHabitName(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Daily Target / Description</label>
                    <input 
                      type="text" 
                      className="w-full glass-input text-base md:text-sm"
                      placeholder="20 mins / day" 
                      value={newHabitGoal}
                      onChange={(e) => setNewHabitGoal(e.target.value)}
                    />
                  </div>
                  <button 
                    onClick={() => {
                      if (!newHabitName) return;
                      store.createHabit({
                        name: newHabitName,
                        goal: newHabitGoal
                      });
                      setNewHabitName('');
                      setNewHabitGoal('');
                    }}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg shadow-lg shadow-purple-600/15 transition-all flex items-center justify-center gap-1 touch-target"
                  >
                    <Plus className="w-4 h-4" />
                    Register Habit
                  </button>
                </div>
              </div>

              <div className="glass-panel p-5 col-span-2 space-y-6">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Habit Log Matrix</h3>
                <div className="space-y-4">
                  {store.habits.map((habit) => {
                    const todayStr = new Date().toISOString().split("T")[0];
                    const isCompletedToday = habit.logs?.some(l => l.date === todayStr && l.status === "Completed");
                    return (
                      <div key={habit.id} className="glass-card p-4 flex flex-col md:flex-row gap-3 md:items-center justify-between">
                        <div>
                          <p className="text-sm font-semibold text-white">{habit.name}</p>
                          <p className="text-xs text-gray-400 mt-1">{habit.goal}</p>
                        </div>

                        <div className="flex items-center justify-between md:justify-end gap-4">
                          <span className="text-xs text-purple-400 font-bold">
                            Streak: {habit.logs?.filter(l => l.status === "Completed").length} days
                          </span>
                          <button
                            onClick={() => store.logHabit(habit.id, todayStr, isCompletedToday ? "Pending" : "Completed")}
                            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all border touch-target ${
                              isCompletedToday 
                                ? 'bg-purple-600/20 border-purple-500/40 text-purple-400' 
                                : 'bg-white/5 border-white/10 text-white hover:bg-white/10'
                            }`}
                          >
                            {isCompletedToday ? 'Completed' : 'Log Daily Completion'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                  {store.habits.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-8">No habits configured. Create one above.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: Goal Management */}
          {store.activeTab === 'goals' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="glass-panel p-5 h-fit space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Add New Goal</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">SMART Goal Description*</label>
                    <input 
                      type="text" 
                      className="w-full glass-input text-base md:text-sm"
                      placeholder="Achieve 85% Trading accuracy" 
                      value={newGoalTitle}
                      onChange={(e) => setNewGoalTitle(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Category</label>
                    <select 
                      className="w-full glass-input text-base md:text-sm"
                      value={newGoalCategory}
                      onChange={(e) => setNewGoalCategory(e.target.value)}
                    >
                      <option value="Personal">Personal</option>
                      <option value="Business">Business</option>
                      <option value="Trading">Trading</option>
                      <option value="Fitness">Fitness</option>
                      <option value="Learning">Learning</option>
                    </select>
                  </div>
                  <button 
                    onClick={() => {
                      if (!newGoalTitle) return;
                      store.createGoal({
                        title: newGoalTitle,
                        category: newGoalCategory
                      });
                      setNewGoalTitle('');
                    }}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg shadow-lg shadow-purple-600/15 transition-all flex items-center justify-center gap-1 touch-target"
                  >
                    <Plus className="w-4 h-4" />
                    Register Goal
                  </button>
                </div>
              </div>

              <div className="glass-panel p-5 col-span-2 space-y-6">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">SMART Objectives</h3>
                <div className="space-y-4">
                  {store.goals.map((goal) => (
                    <div key={goal.id} className="glass-card p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded font-bold uppercase">
                            {goal.category}
                          </span>
                          <h4 className="text-sm font-semibold text-white inline-block ml-2">{goal.title}</h4>
                        </div>
                        <div className="flex items-center gap-3">
                          <button 
                            onClick={() => store.updateGoal(goal.id, { current_value: Math.min(100, goal.current_value + 10) })}
                            className="text-xs px-2.5 py-1.5 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/20 text-purple-400 rounded-lg touch-target"
                          >
                            +10%
                          </button>
                          <button 
                            onClick={() => store.deleteGoal(goal.id)}
                            className="text-gray-500 hover:text-red-400 p-2 rounded-md touch-target"
                          >
                            <Trash className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs text-gray-400">
                          <span>Progress</span>
                          <span>{goal.current_value.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-white/5 rounded-full h-2.5">
                          <div className="bg-purple-600 h-2.5 rounded-full transition-all" style={{ width: `${goal.current_value}%` }}></div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {store.goals.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-8">No goals added. Define one above.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: Notes Drawer / List */}
          {store.activeTab === 'notes' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="glass-panel p-5 h-fit space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Add New Note</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Note Title*</label>
                    <input 
                      type="text" 
                      className="w-full glass-input text-base md:text-sm"
                      placeholder="Meeting notes or scratchpad" 
                      value={newNoteTitle}
                      onChange={(e) => setNewNoteTitle(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Content</label>
                    <textarea 
                      className="w-full glass-input h-32 resize-none text-base md:text-sm"
                      placeholder="Type note content..."
                      value={newNoteContent}
                      onChange={(e) => setNewNoteContent(e.target.value)}
                    />
                  </div>
                  <button 
                    onClick={() => {
                      if (!newNoteTitle) return;
                      store.createNote({
                        title: newNoteTitle,
                        content: newNoteContent
                      });
                      setNewNoteTitle('');
                      setNewNoteContent('');
                    }}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-1 touch-target"
                  >
                    <Plus className="w-4 h-4" />
                    Save Note
                  </button>
                </div>
              </div>

              <div className="glass-panel p-5 col-span-2 space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Saved Notes</h3>
                <div className="space-y-3">
                  {store.notes.map((note) => (
                    <div key={note.id} className="glass-card p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-semibold text-white">{note.title}</h4>
                        <button 
                          onClick={() => store.deleteNote(note.id)}
                          className="text-gray-500 hover:text-red-400 p-2 rounded-md touch-target"
                        >
                          <Trash className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-xs text-gray-300 leading-relaxed whitespace-pre-line">{note.content}</p>
                    </div>
                  ))}
                  {store.notes.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-8">No notes saved. Add one above.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: Trading Journal Dashboard */}
          {store.activeTab === 'trading' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Log Entry Card */}
              <div className="glass-panel p-5 h-fit space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Log Trade Entry</h3>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Ticker*</label>
                      <input 
                        type="text" 
                        className="w-full glass-input text-base md:text-sm"
                        placeholder="NIFTY / AAPL" 
                        value={newTradeTicker}
                        onChange={(e) => setNewTradeTicker(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Direction</label>
                      <select 
                        className="w-full glass-input text-base md:text-sm"
                        value={newTradeType}
                        onChange={(e) => setNewTradeType(e.target.value)}
                      >
                        <option value="Long">Long / Buy</option>
                        <option value="Short">Short / Sell</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Qty*</label>
                      <input 
                        type="number" 
                        className="w-full glass-input text-base md:text-sm"
                        placeholder="10" 
                        value={newTradeQty}
                        onChange={(e) => setNewTradeQty(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-400 block mb-1">Entry Price*</label>
                      <input 
                        type="number" 
                        step="0.01" 
                        className="w-full glass-input text-base md:text-sm"
                        placeholder="182.50" 
                        value={newTradeEntry}
                        onChange={(e) => setNewTradeEntry(e.target.value)}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Strategy Name</label>
                    <input 
                      type="text" 
                      className="w-full glass-input text-base md:text-sm"
                      placeholder="Breakout / Support" 
                      value={newTradeStrategy}
                      onChange={(e) => setNewTradeStrategy(e.target.value)}
                    />
                  </div>

                  <button 
                    onClick={() => {
                      if (!newTradeTicker || !newTradeQty || !newTradeEntry) return;
                      store.logTrade({
                        ticker: newTradeTicker,
                        type: newTradeType,
                        quantity: parseInt(newTradeQty),
                        entry_price: parseFloat(newTradeEntry),
                        strategy: newTradeStrategy
                      });
                      setNewTradeTicker('');
                      setNewTradeQty('');
                      setNewTradeEntry('');
                      setNewTradeStrategy('');
                    }}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-1 touch-target"
                  >
                    <Plus className="w-4 h-4" />
                    Log Trade Entry
                  </button>
                </div>
              </div>

              {/* Execution History */}
              <div className="glass-panel p-5 col-span-2 space-y-4">
                <h3 className="font-semibold text-white border-b border-white/5 pb-2">Execution History & Journal</h3>
                <div className="space-y-3">
                  {store.trades.map((trade) => (
                    <div key={trade.id} className="glass-card p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                            trade.type === "Long" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                          }`}>
                            {trade.type}
                          </span>
                          <h4 className="text-sm font-semibold text-white inline-block ml-2">{trade.ticker}</h4>
                        </div>
                        
                        <div className="text-right">
                          <p className="text-xs text-gray-400">PNL</p>
                          <p className={`text-sm font-bold ${trade.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-400 border-t border-white/5 pt-2">
                        <div>Qty: <strong className="text-white">{trade.quantity}</strong></div>
                        <div>Entry: <strong className="text-white">${trade.entry_price}</strong></div>
                        <div>Exit: <strong className="text-white">{trade.exit_price ? `$${trade.exit_price}` : 'Open'}</strong></div>
                        <div>Strategy: <strong className="text-white">{trade.strategy || 'None'}</strong></div>
                      </div>

                      {!trade.exit_price && (
                        <div className="pt-2 border-t border-white/5 flex gap-2 justify-end">
                          {closingTradeId === trade.id ? (
                            <div className="flex gap-2 w-full">
                              <input 
                                type="number" 
                                step="0.01" 
                                className="flex-1 glass-input py-1 text-xs" 
                                placeholder="Exit Price"
                                value={tradeExitPrice}
                                onChange={(e) => setTradeExitPrice(e.target.value)}
                              />
                              <button 
                                onClick={() => {
                                  if (!tradeExitPrice) return;
                                  store.exitTrade(trade.id, { exit_price: parseFloat(tradeExitPrice) });
                                  setClosingTradeId(null);
                                  setTradeExitPrice('');
                                }}
                                className="px-3 py-1 bg-emerald-600 text-white rounded text-xs touch-target"
                              >
                                Save
                              </button>
                              <button 
                                onClick={() => setClosingTradeId(null)}
                                className="px-3 py-1 bg-white/5 text-white rounded text-xs touch-target"
                              >
                                Cancel
                              </button>
                            </div>
                          ) : (
                            <button 
                              onClick={() => setClosingTradeId(trade.id)}
                              className="px-3 py-1.5 bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 rounded-lg text-xs font-semibold touch-target"
                            >
                              Exit / Close Trade
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                  {store.trades.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-8">No trading activity recorded.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: Mobile Calendar Agenda View */}
          {store.activeTab === 'calendar_agenda' && (
            <div className="glass-panel p-5 space-y-6 animate-fade-in">
              <div className="flex items-center justify-between border-b border-white/5 pb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-purple-400" />
                  <h3 className="font-semibold text-white">Daily Agenda Planner</h3>
                </div>
                <span className="text-xs text-gray-400 font-mono">
                  {new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
                </span>
              </div>

              <div className="space-y-4">
                {/* Agenda sections */}
                {['Today', 'Tomorrow', 'This Week', 'Upcoming'].map((period) => {
                  const todayStr = new Date().toISOString().split('T')[0];
                  let periodTasks = [];

                  if (period === 'Today') {
                    periodTasks = store.tasks.filter(t => t.due_date === todayStr);
                  } else if (period === 'Tomorrow') {
                    const tomorrow = new Date();
                    tomorrow.setDate(tomorrow.getDate() + 1);
                    const tomorrowStr = tomorrow.toISOString().split('T')[0];
                    periodTasks = store.tasks.filter(t => t.due_date === tomorrowStr);
                  } else {
                    periodTasks = store.tasks.filter(t => t.due_date && t.due_date > todayStr);
                  }

                  return (
                    <div key={period} className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-purple-400 border-l-2 border-purple-500 pl-2">
                        {period} ({periodTasks.length})
                      </h4>
                      <div className="space-y-2">
                        {periodTasks.map((task) => (
                          <div key={task.id} className="glass-card p-3 flex items-center justify-between">
                            <span className="text-sm text-white font-medium">{task.title}</span>
                            <span className="text-xs text-gray-500 font-mono">{task.due_date}</span>
                          </div>
                        ))}
                        {periodTasks.length === 0 && (
                          <p className="text-xs text-gray-600 pl-3">No tasks or events scheduled.</p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 8: Mobile AI Planner Chat Assistant View */}
          {store.activeTab === 'ai_assistant' && (
            <div className="glass-panel p-4 h-[75vh] flex flex-col justify-between animate-fade-in">
              <div className="flex items-center justify-between border-b border-white/5 pb-2 shrink-0">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-yellow-400" />
                  <h3 className="font-semibold text-white">AI Planner Chat</h3>
                </div>
                <button 
                  onClick={() => {
                    store.optimizeSchedule();
                    setChatMessages(prev => [...prev, { sender: 'ai', text: "Calculated optimal focus schedule today." }]);
                  }}
                  className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-bold transition-all touch-target"
                >
                  Optimize
                </button>
              </div>

              {/* Chat bubble body */}
              <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      msg.sender === 'user' 
                        ? 'bg-purple-600 text-white rounded-tr-none' 
                        : 'bg-white/5 border border-white/5 text-gray-200 rounded-tl-none'
                    }`}>
                      <p>{msg.text}</p>
                      
                      {msg.details?.schedule && (
                        <div className="mt-3 space-y-2 border-t border-white/10 pt-2 text-xs">
                          {msg.details.schedule.map((item: any, id: number) => (
                            <div key={id} className="flex justify-between">
                              <span className="font-semibold text-purple-300">{item.time}</span>
                              <span className="text-gray-400">{item.activity}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {msg.details?.subtasks && (
                        <div className="mt-3 space-y-2 border-t border-white/10 pt-2 text-xs">
                          {msg.details.subtasks.map((st: string, id: number) => (
                            <div key={id} className="flex items-center gap-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-purple-400"></div>
                              <span>{st}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Chat suggestions */}
              <div className="py-2 flex gap-1.5 overflow-x-auto shrink-0 scrollbar-none">
                <button 
                  onClick={() => setChatInput("Optimize my schedule")}
                  className="px-3 py-1.5 bg-white/2 hover:bg-white/5 border border-white/5 text-gray-400 hover:text-white rounded-full text-xs shrink-0 touch-target"
                >
                  ⚡ Optimize Schedule
                </button>
                <button 
                  onClick={() => setChatInput("Breakdown task: Build auth middleware")}
                  className="px-3 py-1.5 bg-white/2 hover:bg-white/5 border border-white/5 text-gray-400 hover:text-white rounded-full text-xs shrink-0 touch-target"
                >
                  🛠️ Breakdown Task
                </button>
              </div>

              {/* Input field */}
              <div className="flex gap-2 items-center border-t border-white/5 pt-3 shrink-0">
                <div className="flex items-center gap-1.5 shrink-0">
                  <button 
                    onClick={toggleListening}
                    className={`p-2.5 border rounded-full touch-target transition-all ${
                      isListening 
                        ? 'bg-red-500/20 border-red-500 text-red-500 animate-pulse' 
                        : 'bg-white/2 hover:bg-white/5 border-white/10 text-gray-400 hover:text-white'
                    }`}
                    title={isListening ? "Stop listening" : "Start voice input"}
                  >
                    <Mic className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => {
                      setSpeechLanguage(prev => {
                        if (prev === 'hi-IN') return 'gu-IN';
                        if (prev === 'gu-IN') return 'en-US';
                        return 'hi-IN';
                      });
                    }}
                    className="px-2 py-1 bg-white/5 hover:bg-white/10 border border-white/10 text-[10px] font-bold rounded text-purple-400 hover:text-purple-300 transition-all font-mono touch-target"
                    title="Change voice input language"
                  >
                    {speechLanguage === 'hi-IN' ? 'HI' : speechLanguage === 'gu-IN' ? 'GU' : 'EN'}
                  </button>
                </div>
                <input
                  type="text"
                  className="flex-1 glass-input py-2 text-base md:text-sm"
                  placeholder="Ask AI assistant..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendChatMessage()}
                />
                <button 
                  onClick={handleSendChatMessage}
                  className="p-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-full touch-target"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}

          {/* Desktop Fallback views */}
          {store.activeTab === 'ai' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* AI Daily Planner */}
                <div className="glass-panel p-6 space-y-4">
                  <div className="flex items-center justify-between border-b border-white/5 pb-2">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-yellow-500" />
                      <h3 className="font-semibold text-white">AI Schedule Optimization</h3>
                    </div>
                    <button 
                      onClick={() => store.optimizeSchedule()}
                      className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
                      disabled={store.loadingAI}
                    >
                      {store.loadingAI ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
                      Optimize Schedule
                    </button>
                  </div>

                  {store.aiSchedule ? (
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-purple-400 mb-2">Recommended Focus Blocks</p>
                        <ul className="space-y-1.5">
                          {store.aiSchedule.focus_blocks?.map((fb: string, idx: number) => (
                            <li key={idx} className="text-sm text-gray-300 flex items-center gap-2">
                              <CheckSquare className="w-4 h-4 text-purple-500 shrink-0" />
                              <span>{fb}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-purple-400 mb-2">Optimized Sequence</p>
                        <div className="space-y-2">
                          {store.aiSchedule.schedule?.map((item: any, idx: number) => (
                            <div key={idx} className="glass-card p-3 flex items-center justify-between">
                              <div>
                                <p className="text-xs font-semibold text-white">{item.time}</p>
                                <p className="text-sm text-gray-300">{item.activity}</p>
                              </div>
                              <span className="text-xs text-gray-500">{item.duration_minutes} mins</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500 py-8 text-center">No calculated schedule yet. Click 'Optimize Schedule' to generate.</p>
                  )}
                </div>

                {/* AI Task Breakdown */}
                <div className="glass-panel p-6 space-y-4">
                  <div className="flex items-center gap-2 border-b border-white/5 pb-2">
                    <Sparkles className="w-5 h-5 text-yellow-500" />
                    <h3 className="font-semibold text-white">AI Task Breakdown Advisor</h3>
                  </div>

                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      className="flex-1 glass-input"
                      placeholder="Enter large task (e.g. Build auth middleware)" 
                      value={aiBreakdownInput}
                      onChange={(e) => setAiBreakdownInput(e.target.value)}
                    />
                    <button 
                      onClick={() => {
                        if (!aiBreakdownInput) return;
                        store.breakdownTaskAI(aiBreakdownInput);
                      }}
                      className="px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1"
                      disabled={store.loadingAI}
                    >
                      {store.loadingAI && <Loader className="w-3.5 h-3.5 animate-spin" />}
                      Breakdown
                    </button>
                  </div>

                  {store.aiBreakdown ? (
                    <div className="space-y-4 pt-2">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-purple-400 mb-2">Action Plan</p>
                        <p className="text-xs text-gray-400 leading-relaxed bg-white/2 p-3 rounded border border-white/5">
                          {store.aiBreakdown.execution_plan}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-purple-400 mb-2">Suggested Subtasks</p>
                        <div className="space-y-1.5">
                          {store.aiBreakdown.subtasks?.map((st: string, idx: number) => (
                            <div key={idx} className="flex items-center gap-2 text-sm text-gray-300">
                              <button 
                                onClick={() => {
                                  store.createTask({
                                    title: st,
                                    priority: "Medium",
                                    due_date: new Date().toISOString().split("T")[0]
                                  });
                                }}
                                className="p-1 bg-white/5 hover:bg-purple-600/20 text-purple-400 hover:text-purple-300 rounded border border-white/10"
                                title="Import as Task"
                              >
                                <Plus className="w-3.5 h-3.5" />
                              </button>
                              <span>{st}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500 py-8 text-center">Type in a complex objective and click 'Breakdown' to generate subtasks.</p>
                  )}
                </div>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Mobile Drawer (More Tab) slide-up modal overlay */}
      {isMoreDrawerOpen && (
        <div className="fixed inset-0 z-50 flex items-end bg-black/60 backdrop-blur-sm md:hidden animate-fade-in">
          <div className="w-full bg-[#09090d] border-t border-white/10 rounded-t-3xl p-6 space-y-6 animate-slide-up safe-bottom">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-purple-400" />
                <span className="font-bold text-white text-base truncate">{store.user?.email}</span>
              </div>
              <button 
                onClick={() => setIsMoreDrawerOpen(false)}
                className="p-1.5 hover:bg-white/5 rounded-full text-gray-400 touch-target"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Menu options */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => { store.setActiveTab('habits'); setIsMoreDrawerOpen(false); }}
                className="py-3 px-4 bg-white/2 border border-white/5 rounded-xl text-sm font-semibold text-white flex items-center gap-2 hover:bg-white/5 touch-target"
              >
                <Clock className="w-4 h-4 text-purple-400" />
                <span>Habits</span>
              </button>
              <button
                onClick={() => { store.setActiveTab('goals'); setIsMoreDrawerOpen(false); }}
                className="py-3 px-4 bg-white/2 border border-white/5 rounded-xl text-sm font-semibold text-white flex items-center gap-2 hover:bg-white/5 touch-target"
              >
                <Zap className="w-4 h-4 text-yellow-400" />
                <span>Goals</span>
              </button>
              <button
                onClick={() => { store.setActiveTab('notes'); setIsMoreDrawerOpen(false); }}
                className="py-3 px-4 bg-white/2 border border-white/5 rounded-xl text-sm font-semibold text-white flex items-center gap-2 hover:bg-white/5 touch-target"
              >
                <BookOpen className="w-4 h-4 text-blue-400" />
                <span>Notes</span>
              </button>
              <button
                onClick={() => { store.setActiveTab('trading'); setIsMoreDrawerOpen(false); }}
                className="py-3 px-4 bg-white/2 border border-white/5 rounded-xl text-sm font-semibold text-white flex items-center gap-2 hover:bg-white/5 touch-target"
              >
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <span>Trading Journal</span>
              </button>
            </div>

            {/* Biometric Enable toggle option */}
            <div className="flex items-center justify-between text-sm border-t border-white/5 pt-4">
              <span className="text-gray-400">Enable Biometric Login</span>
              <button
                onClick={async () => {
                  const isAvail = await BiometricService.isAvailable();
                  if (!isAvail) {
                    alert("Biometric hardware (Fingerprint/FaceID) is not available or enrolled on this device.");
                    return;
                  }
                  const enabled = localStorage.getItem('biometrics_enabled') === 'true';
                  if (enabled) {
                    localStorage.removeItem('biometrics_enabled');
                    await BiometricService.clearCredentials();
                    alert("Biometric authentication disabled.");
                  } else {
                    const secureToken = store.token;
                    const userEmail = store.user?.email;
                    if (secureToken && userEmail) {
                      const saved = await BiometricService.saveCredentials(userEmail, secureToken);
                      if (saved) {
                        localStorage.setItem('biometrics_enabled', 'true');
                        localStorage.setItem('auth_email', userEmail);
                        alert("Biometric authentication enabled successfully!");
                      } else {
                        alert("Failed to securely store biometric login credentials.");
                      }
                    } else {
                      alert("Please log in to enable biometric authentication.");
                    }
                  }
                  // Close drawer to refresh view
                  setIsMoreDrawerOpen(false);
                }}
                className={`py-1.5 px-3 border rounded-lg text-xs font-bold transition-all touch-target ${
                  localStorage.getItem('biometrics_enabled') === 'true'
                    ? 'bg-purple-600 border-purple-500 text-white'
                    : 'bg-white/2 border-white/5 text-gray-400 hover:text-white'
                }`}
              >
                {localStorage.getItem('biometrics_enabled') === 'true' ? 'Enabled' : 'Disabled'}
              </button>
            </div>
            {/* Push Notifications Configuration Status */}
            <div className="flex items-center justify-between text-sm border-t border-white/5 pt-4">
              <span className="text-gray-400">Push Notifications</span>
              <span className={`text-xs font-bold ${isPushAvailable ? 'text-emerald-400' : 'text-amber-500'}`}>
                {isPushAvailable ? 'Enabled' : 'Firebase Not Configured'}
              </span>
            </div>

            <div className="flex items-center justify-between border-t border-white/5 pt-4">
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${
                  syncStatus === 'Offline' ? 'bg-amber-500 animate-pulse' :
                  syncStatus === 'Syncing...' ? 'bg-blue-400 animate-spin' :
                  syncStatus === 'Synced' ? 'bg-purple-400' : 'bg-emerald-500'
                }`}></div>
                <span className="text-xs uppercase font-bold tracking-wider text-gray-400">
                  {syncStatus === 'Offline' ? 'Offline Local Mode' :
                   syncStatus === 'Syncing...' ? 'Syncing...' :
                   syncStatus === 'Synced' ? 'Synced' : 'Cloud Sync Connected'}
                </span>
              </div>

              <button 
                onClick={handleLogout}
                className="py-2.5 px-4 bg-red-600/10 border border-red-500/20 text-red-400 hover:bg-red-600 hover:text-white rounded-lg text-xs font-bold transition-all touch-target"
              >
                Sign Out / Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Mobile Bottom Tab Navigation */}
      <nav className="flex md:hidden fixed bottom-0 left-0 right-0 min-h-[4rem] pb-[env(safe-area-inset-bottom)] bg-[#09090d]/95 backdrop-blur-md border-t border-white/10 z-40 justify-around items-center px-2">
        {mobileNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = store.activeTab === item.id || 
            (item.id === 'more' && ['habits', 'goals', 'notes', 'trading'].includes(store.activeTab) && !isMoreDrawerOpen);
          return (
            <button
              key={item.id}
              onClick={() => {
                if (item.id === 'more') {
                  setIsMoreDrawerOpen(true);
                } else {
                  store.setActiveTab(item.id);
                  setIsMoreDrawerOpen(false);
                }
              }}
              className={`flex flex-col items-center justify-center flex-1 h-full py-1.5 touch-target ${
                isActive ? 'text-purple-400' : 'text-gray-500 hover:text-gray-300'
              }`}
              aria-label={item.label}
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span className="text-[10px] font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

    </div>
  );
}
