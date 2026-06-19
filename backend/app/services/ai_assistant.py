import json
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import AIUsageLog

async def log_ai_usage(db: Optional[Session], user_id: int, provider: str, model: str, prompt_tokens: int, completion_tokens: int, cost: float):
    """Logs AI token usage and costs to database for plan limits validation."""
    if db is None:
        return
    try:
        log = AIUsageLog(
            user_id=user_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[AI Cost Logging Error] Failed to commit usage logs: {e}")
        db.rollback()

async def call_openai(prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
    """Tries calling OpenAI endpoint."""
    if not settings.OPENAI_API_KEY:
        return None
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=8.0
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                in_tokens = data["usage"]["prompt_tokens"]
                out_tokens = data["usage"]["completion_tokens"]
                # gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output
                cost = (in_tokens * 0.15 / 1000000) + (out_tokens * 0.60 / 1000000)
                return {
                    "text": content,
                    "provider": "OpenAI",
                    "model": "gpt-4o-mini",
                    "in_tokens": in_tokens,
                    "out_tokens": out_tokens,
                    "cost": cost
                }
    except Exception as e:
        print(f"[AI Router Warning] OpenAI primary provider failed: {e}")
    return None

async def call_gemini(prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
    """Tries calling Gemini API endpoint as secondary failover."""
    if not settings.GEMINI_API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{system_prompt}\n\nUser Request: {prompt}"
            }]
        }]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=8.0
            )
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                # Approximate token counts for Gemini response
                in_tokens = len(prompt) // 4
                out_tokens = len(content) // 4
                # gemini-1.5-flash pricing: $0.075/1M input, $0.30/1M output
                cost = (in_tokens * 0.075 / 1000000) + (out_tokens * 0.30 / 1000000)
                return {
                    "text": content,
                    "provider": "Gemini",
                    "model": "gemini-1.5-flash",
                    "in_tokens": in_tokens,
                    "out_tokens": out_tokens,
                    "cost": cost
                }
    except Exception as e:
        print(f"[AI Router Warning] Gemini secondary provider failed: {e}")
    return None

async def generate_daily_schedule(tasks: List[Dict[str, Any]], db: Optional[Session] = None, user_id: int = 1) -> Dict[str, Any]:
    tasks_summary = "\n".join([
        f"- {t['title']} (Priority: {t['priority']}, Due: {t.get('due_date')}, Est: {t.get('estimated_time')}m)"
        for t in tasks
    ])
    
    prompt = f"Optimize this list of tasks into a daily schedule with Focus Blocks:\n{tasks_summary}"
    system_prompt = (
        "You are the LifeOS AI planner. Format your response strictly as JSON with three keys: "
        "'schedule' (list of objects with 'time', 'activity', 'duration_minutes'), "
        "'priority_order' (ordered list of task names), and "
        "'focus_blocks' (list of strings describing high-focus deep work intervals)."
    )

    # 1. Try OpenAI
    response = await call_openai(prompt, system_prompt)
    
    # 2. Try Gemini Fallover
    if not response:
        response = await call_gemini(prompt, system_prompt)
        
    # 3. Log and return
    if response:
        await log_ai_usage(
            db, user_id, response["provider"], response["model"], 
            response["in_tokens"], response["out_tokens"], response["cost"]
        )
        try:
            return json.loads(response["text"])
        except Exception:
            pass

    # 4. Local rule-based/mock fallback if both fail
    return {
        "schedule": [
            {"time": "09:00 AM", "activity": "Deep Work Block (Critical Tasks)", "duration_minutes": 90},
            {"time": "10:30 AM", "activity": "Admin, Email, and Quick Updates", "duration_minutes": 30},
            {"time": "11:00 AM", "activity": "Secondary Focus Session", "duration_minutes": 120},
            {"time": "02:00 PM", "activity": "Collaborative Alignment and Meetings", "duration_minutes": 60},
            {"time": "03:00 PM", "activity": "Routine Tasks and Review", "duration_minutes": 60}
        ],
        "priority_order": [t["title"] for t in sorted(tasks, key=lambda x: x.get("priority", "Medium"), reverse=True)][:5],
        "focus_blocks": [
            "Morning Focus: 9:00 AM - 10:30 AM (90 mins) - Ideal for Critical priorities",
            "Midday Focus: 11:00 AM - 1:00 PM (120 mins) - Ideal for medium-intensity tasks"
        ]
    }

async def breakdown_large_task(task_title: str, task_desc: str, db: Optional[Session] = None, user_id: int = 1) -> Dict[str, Any]:
    prompt = f"Break down this task:\nTitle: {task_title}\nDescription: {task_desc or 'None'}"
    system_prompt = (
        "You are the LifeOS AI task breakdown engine. Format your response strictly as JSON with three keys: "
        "'subtasks' (list of strings representing actionable micro-steps), "
        "'checklist' (list of strings representing quality checks), and "
        "'execution_plan' (a brief paragraph explaining the recommended roadmap)."
    )

    # 1. Try OpenAI
    response = await call_openai(prompt, system_prompt)
    
    # 2. Try Gemini Fallover
    if not response:
        response = await call_gemini(prompt, system_prompt)
        
    # 3. Log and return
    if response:
        await log_ai_usage(
            db, user_id, response["provider"], response["model"], 
            response["in_tokens"], response["out_tokens"], response["cost"]
        )
        try:
            return json.loads(response["text"])
        except Exception:
            pass

    # 4. Local mock fallback
    return {
        "subtasks": [
            f"Define requirements and scope for {task_title}",
            "Draft initial implementation outline",
            "Code primary features and test core paths",
            "Refactor, style UI, and add validation",
            "Final integration test and verification"
        ],
        "checklist": [
            "Prerequisites verified",
            "Core functionality matches design",
            "Edge cases covered",
            "UI responsive and accessible"
        ],
        "execution_plan": f"Execute {task_title} in 3 distinct sprints. Start with scoping, build a skeleton mockup, and then layer on details."
    }
