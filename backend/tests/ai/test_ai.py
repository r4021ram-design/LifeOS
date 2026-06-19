import pytest
import httpx
from unittest.mock import patch, MagicMock
from app.services.ai_assistant import generate_daily_schedule, breakdown_large_task, call_openai, call_gemini, log_ai_usage

@pytest.fixture
def dummy_tasks():
    return [
        {"title": "Task A", "priority": "High", "due_date": "2026-06-20", "estimated_time": 30},
        {"title": "Task B", "priority": "Medium", "due_date": "2026-06-20", "estimated_time": 45}
    ]

@pytest.mark.anyio
@patch("app.services.ai_assistant.httpx.AsyncClient.post")
async def test_call_openai_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "{\"schedule\": []}"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20}
    }
    mock_post.return_value = mock_resp

    with patch("app.services.ai_assistant.settings.OPENAI_API_KEY", "dummy_key"):
        res_data = await call_openai("test prompt", "system prompt")
        assert res_data is not None
        assert res_data["provider"] == "OpenAI"
        assert res_data["model"] == "gpt-4o-mini"
        assert res_data["cost"] > 0.0

@pytest.mark.anyio
async def test_call_openai_missing_key():
    with patch("app.services.ai_assistant.settings.OPENAI_API_KEY", ""):
        res = await call_openai("test prompt", "system prompt")
        assert res is None

@pytest.mark.anyio
@patch("app.services.ai_assistant.httpx.AsyncClient.post")
async def test_call_openai_timeout(mock_post):
    mock_post.side_effect = httpx.TimeoutException("OpenAI Timeout")
    with patch("app.services.ai_assistant.settings.OPENAI_API_KEY", "dummy_key"):
        res = await call_openai("test prompt", "system")
        assert res is None

@pytest.mark.anyio
@patch("app.services.ai_assistant.httpx.AsyncClient.post")
async def test_call_openai_non_200(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_post.return_value = mock_resp
    with patch("app.services.ai_assistant.settings.OPENAI_API_KEY", "dummy_key"):
        res = await call_openai("test prompt", "system")
        assert res is None

@pytest.mark.anyio
@patch("app.services.ai_assistant.httpx.AsyncClient.post")
async def test_call_gemini_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "{\"schedule\": []}"}]}}]
    }
    mock_post.return_value = mock_resp

    with patch("app.services.ai_assistant.settings.GEMINI_API_KEY", "dummy_key"):
        res_data = await call_gemini("test prompt", "system prompt")
        assert res_data is not None
        assert res_data["provider"] == "Gemini"
        assert res_data["model"] == "gemini-1.5-flash"

@pytest.mark.anyio
async def test_call_gemini_missing_key():
    with patch("app.services.ai_assistant.settings.GEMINI_API_KEY", ""):
        res = await call_gemini("test prompt", "system prompt")
        assert res is None

@pytest.mark.anyio
@patch("app.services.ai_assistant.httpx.AsyncClient.post")
async def test_call_gemini_timeout(mock_post):
    mock_post.side_effect = httpx.TimeoutException("Gemini Timeout")
    with patch("app.services.ai_assistant.settings.GEMINI_API_KEY", "dummy_key"):
        res = await call_gemini("test prompt", "system")
        assert res is None

@pytest.mark.anyio
@patch("app.services.ai_assistant.httpx.AsyncClient.post")
async def test_call_gemini_non_200(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_post.return_value = mock_resp
    with patch("app.services.ai_assistant.settings.GEMINI_API_KEY", "dummy_key"):
        res = await call_gemini("test prompt", "system")
        assert res is None

@pytest.mark.anyio
@patch("app.services.ai_assistant.call_openai")
@patch("app.services.ai_assistant.call_gemini")
async def test_ai_router_failover_openai_to_gemini(mock_call_gemini, mock_call_openai, dummy_tasks, db):
    mock_call_openai.return_value = None
    mock_call_gemini.return_value = {
        "text": "{\"schedule\": [], \"priority_order\": [], \"focus_blocks\": []}",
        "provider": "Gemini",
        "model": "gemini-1.5-flash",
        "in_tokens": 10,
        "out_tokens": 15,
        "cost": 0.0001
    }

    res = await generate_daily_schedule(dummy_tasks, db=db, user_id=1)
    
    mock_call_openai.assert_called_once()
    mock_call_gemini.assert_called_once()
    assert res == {"schedule": [], "priority_order": [], "focus_blocks": []}

@pytest.mark.anyio
@patch("app.services.ai_assistant.call_openai")
@patch("app.services.ai_assistant.call_gemini")
async def test_ai_router_local_fallback(mock_call_gemini, mock_call_openai, dummy_tasks, db):
    mock_call_openai.return_value = None
    mock_call_gemini.return_value = None

    res = await generate_daily_schedule(dummy_tasks, db=db, user_id=1)
    
    assert "schedule" in res
    assert "priority_order" in res
    assert "focus_blocks" in res
    assert len(res["focus_blocks"]) > 0

@pytest.mark.anyio
@patch("app.services.ai_assistant.call_openai")
@patch("app.services.ai_assistant.call_gemini")
async def test_breakdown_large_task_success(mock_call_gemini, mock_call_openai, db):
    mock_call_openai.return_value = None
    mock_call_gemini.return_value = {
        "text": "{\"subtasks\": [\"a\"], \"checklist\": [\"b\"], \"execution_plan\": \"plan\"}",
        "provider": "Gemini",
        "model": "gemini-1.5-flash",
        "in_tokens": 5,
        "out_tokens": 10,
        "cost": 0.00005
    }
    
    res = await breakdown_large_task("task", "desc", db=db, user_id=1)
    assert res == {"subtasks": ["a"], "checklist": ["b"], "execution_plan": "plan"}

@pytest.mark.anyio
@patch("app.services.ai_assistant.call_openai")
@patch("app.services.ai_assistant.call_gemini")
async def test_breakdown_large_task_fallback(mock_call_gemini, mock_call_openai, db):
    mock_call_openai.return_value = None
    mock_call_gemini.return_value = None
    
    res = await breakdown_large_task("task", "desc", db=db, user_id=1)
    assert "subtasks" in res
    assert "checklist" in res
    assert "execution_plan" in res

@pytest.mark.anyio
async def test_log_ai_usage_db_exception():
    mock_db = MagicMock()
    mock_db.commit.side_effect = Exception("DB commit crash")
    
    with patch("builtins.print") as mock_print:
        await log_ai_usage(mock_db, 1, "OpenAI", "gpt-4", 10, 10, 0.05)
        mock_print.assert_any_call("[AI Cost Logging Error] Failed to commit usage logs: DB commit crash")
        mock_db.rollback.assert_called_once()

def test_api_schedule_endpoint(client, auth_headers):
    with patch("app.api.v1.ai.generate_daily_schedule") as mock_schedule:
        mock_schedule.return_value = {"schedule": [], "priority_order": [], "focus_blocks": []}
        
        payload = {
            "tasks": [{"title": "Hardening tests", "priority": "High"}]
        }
        response = client.post("/api/v1/ai/schedule", json=payload, headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == {"schedule": [], "priority_order": [], "focus_blocks": []}

def test_api_breakdown_endpoint(client, auth_headers):
    with patch("app.api.v1.ai.breakdown_large_task") as mock_breakdown:
        mock_breakdown.return_value = {"subtasks": [], "checklist": [], "execution_plan": ""}
        
        payload = {
            "title": "Hardening tests",
            "description": "Increase test coverage"
        }
        response = client.post("/api/v1/ai/breakdown", json=payload, headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == {"subtasks": [], "checklist": [], "execution_plan": ""}
