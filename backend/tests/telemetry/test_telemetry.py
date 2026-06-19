import pytest
from unittest.mock import patch, MagicMock
from app.core.telemetry import initialize_telemetry

def test_initialize_telemetry_success():
    mock_app = MagicMock()
    mock_engine = MagicMock()
    
    with patch("app.core.telemetry.FastAPIInstrumentor") as mock_fastapi:
        with patch("app.core.telemetry.SQLAlchemyInstrumentor") as mock_sqlalchemy:
            with patch("app.core.telemetry.RedisInstrumentor") as mock_redis:
                with patch("app.core.telemetry.CeleryInstrumentor") as mock_celery:
                    
                    initialize_telemetry(mock_app, mock_engine)
                    
                    mock_fastapi.instrument_app.assert_called_once_with(mock_app)
                    mock_sqlalchemy.return_value.instrument.assert_called_once_with(engine=mock_engine)
                    mock_redis.return_value.instrument.assert_called_once()
                    mock_celery.return_value.instrument.assert_called_once()

def test_initialize_telemetry_exception():
    mock_app = MagicMock()
    # Force an exception during telemetry setup
    with patch("app.core.telemetry.TracerProvider", side_effect=RuntimeError("OTel failure")):
        with patch("builtins.print") as mock_print:
            initialize_telemetry(mock_app)
            mock_print.assert_any_call("[Telemetry Warning] Telemetry initialization skipped or failed: OTel failure")
