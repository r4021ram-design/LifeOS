# Python 3.14 Compatibility & Standard Compliance Report

This report documents the standard compliance updates implemented across the codebase to ensure compatibility with Python 3.14.0 and Pydantic v2.

## 1. Timezone-Aware DateTime Migration

### The Issue
`datetime.datetime.utcnow()` has been deprecated in Python for several versions and is scheduled for complete removal in a future release. It returns naive datetimes which are prone to comparison and timezone-interpretation bugs.

### Implemented Fixes
All occurrences of `datetime.datetime.utcnow()` have been replaced:
1. **Database Models Defaults (`app/models/models.py`):**
   Converted class-level defaults and update hook callbacks to use timezone-aware lambdas:
   ```python
   created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
   updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), onupdate=lambda: datetime.datetime.now(datetime.UTC))
   ```
2. **Notification Scheduler (`app/services/notifications/scheduler.py`):**
   ```python
   now = datetime.datetime.now(datetime.UTC)
   ```
3. **Trading Journal (`app/api/v1/trading.py`):**
   ```python
   db_trade.exit_time = trade_in.exit_time or datetime.datetime.now(datetime.UTC)
   ```
4. **Test Suites (`tests/reminders/test_reminders.py`):**
   ```python
   now = datetime.datetime.now(datetime.UTC)
   ```

---

## 2. Pydantic v2 Configuration Migration

### The Issue
Pydantic v1 utilized nested `class Config:` declarations. In Pydantic v2, this has been deprecated in favor of a modern, flat class attribute named `model_config` using `ConfigDict`.

### Implemented Fixes
1. **Application Schemas (`app/schemas/schemas.py`):**
   All 10+ response/request schemas have been converted:
   ```python
   # MODERN IMPLEMENTATION
   from pydantic import BaseModel, ConfigDict

   class UserResponse(BaseModel):
       id: int
       email: str
       full_name: Optional[str]
       role: str
       is_active: bool
       created_at: datetime.datetime

       model_config = ConfigDict(from_attributes=True)
   ```
2. **BaseSettings Settings Configuration (`app/core/config.py`):**
   Updated to use `SettingsConfigDict`:
   ```python
   class Settings(BaseSettings):
       ...
       model_config = SettingsConfigDict(env_file=".env", extra="ignore")
   ```

---

## 3. Test Warning Resolution (AsyncMock Coroutines)

### The Issue
In Python 3.14, returning a coroutine object from a patched mock and discarding it without awaiting generates a `RuntimeWarning: coroutine was never awaited`. This was occurring during health and search tests due to unawaited coroutines in `asyncio.run_coroutine_threadsafe` mock calls.

### Implemented Fixes
In [test_reminders.py](file:///c:/Users/admin/Desktop/todo/backend/tests/reminders/test_reminders.py), we updated the mock of `asyncio.run_coroutine_threadsafe` to explicitly close the coroutine:
```python
def dummy_run_coroutine_threadsafe(coro, loop):
    coro.close()  # Clean up coroutine object to prevent warning
    return mock_future

with patch("asyncio.run_coroutine_threadsafe", side_effect=dummy_run_coroutine_threadsafe):
    ...
```
This eliminated the unawaited coroutine warnings during test execution.
