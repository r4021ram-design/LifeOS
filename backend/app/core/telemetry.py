from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from app.core.config import settings

# Global tracer instance
tracer = trace.get_tracer("lifeos-ai")

def initialize_telemetry(app, engine=None):
    """
    Initializes OpenTelemetry auto-instrumentation for FastAPI, SQLAlchemy, Redis, and Celery.
    Gracefully handles errors in local development profiles.
    """
    try:
        # Set tracer provider
        provider = TracerProvider()
        processor = SimpleSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)

        # Instrument Database queries
        if engine:
            SQLAlchemyInstrumentor().instrument(engine=engine)

        # Instrument Cache and Queues
        RedisInstrumentor().instrument()
        CeleryInstrumentor().instrument()
        print("[Telemetry Service] OpenTelemetry instrumentation successfully loaded.")
    except Exception as e:
        print(f"[Telemetry Warning] Telemetry initialization skipped or failed: {e}")
