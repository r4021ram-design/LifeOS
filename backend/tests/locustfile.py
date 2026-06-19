import uuid
from locust import HttpUser, task, between

class LifeOSUser(HttpUser):
    # Simulated think time between user actions (1 to 3 seconds)
    wait_time = between(1, 3)

    def on_start(self):
        """Executed when a simulated user starts: registers and logs in."""
        self.username = f"user_{uuid.uuid4().hex[:8]}@lifeos-test.com"
        self.password = "secure_password_123"
        self.token = ""
        self.register_and_login()

    def register_and_login(self):
        # 1. Register User
        signup_payload = {
            "email": self.username,
            "password": self.password,
            "full_name": "Simulated Load User"
        }
        response = self.client.post("/api/v1/auth/signup", json=signup_payload)
        
        # 2. Login User to acquire JWT Token
        login_payload = {
            "email": self.username,
            "password": self.password
        }
        response = self.client.post("/api/v1/auth/login", json=login_payload)
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(3)
    def load_dashboard(self):
        """Simulates loading the dashboard by fetching tasks, habits, and goals."""
        if not self.token:
            return
        self.client.get("/api/v1/tasks/", headers=self.headers)
        self.client.get("/api/v1/habits/", headers=self.headers)
        self.client.get("/api/v1/goals/", headers=self.headers)

    @task(2)
    def create_and_update_task(self):
        """Simulates creating a task with a reminder rule, then updating and completing it."""
        if not self.token:
            return
        # Create Task (This acts as Create Task and Create Reminder due to reminder_rule)
        task_payload = {
            "title": f"Load test task {uuid.uuid4().hex[:6]}",
            "description": "Simulated task description for performance testing.",
            "priority": "High",
            "status": "Pending",
            "due_date": "2026-06-20",
            "reminder_rule": "15m_before",
            "labels": ["load-test", "automated"]
        }
        response = self.client.post("/api/v1/tasks/", json=task_payload, headers=self.headers)
        if response.status_code in (200, 201):
            task_data = response.json()
            task_id = task_data.get("id")
            if task_id:
                # Update Task
                update_payload = {"status": "In Progress"}
                self.client.put(f"/api/v1/tasks/{task_id}", json=update_payload, headers=self.headers)
                
                # Complete Task
                complete_payload = {"status": "Completed"}
                self.client.put(f"/api/v1/tasks/{task_id}", json=complete_payload, headers=self.headers)

    @task(2)
    def search_query(self):
        """Simulates utilizing the Raycast-like command palette global search."""
        if not self.token:
            return
        self.client.get("/api/v1/search/?q=test", headers=self.headers)

    @task(1)
    def ai_planner_requests(self):
        """Simulates calling AI planner assistant (schedule optimization and task breakdown)."""
        if not self.token:
            return
        # 1. Schedule Optimization
        schedule_payload = {
            "tasks": [{"title": "Hardening tests", "priority": "High"}]
        }
        self.client.post("/api/v1/ai/schedule", json=schedule_payload, headers=self.headers)
        
        # 2. Task Breakdown
        breakdown_payload = {
            "title": "Complete production audits",
            "description": "Review and harden all components before launch"
        }
        self.client.post("/api/v1/ai/breakdown", json=breakdown_payload, headers=self.headers)

    @task(1)
    def logout_sim(self):
        """Simulates logging out and logging back in to verify session auth flow."""
        self.token = ""
        self.headers = {}
        self.register_and_login()
