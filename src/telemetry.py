"""
OpenTelemetry setup for observability (Phase 4).
Metrics, tracing, and distributed request tracking.
"""
from opentelemetry import metrics, trace
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_metrics():
    """Initialize Prometheus metrics exporter."""
    reader = PrometheusMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)

    meter = metrics.get_meter(__name__)

    # Request metrics
    request_counter = meter.create_counter(
        "http_requests_total",
        description="Total HTTP requests",
        unit="1",
    )

    request_latency = meter.create_histogram(
        "http_request_duration_seconds",
        description="HTTP request latency",
        unit="s",
    )

    # HITL metrics
    hitl_decisions = meter.create_counter(
        "hitl_decisions_total",
        description="Total HITL decisions",
        unit="1",
    )

    # Audit metrics
    audit_writes = meter.create_counter(
        "audit_log_writes_total",
        description="Total audit log writes",
        unit="1",
    )

    return {
        "request_counter": request_counter,
        "request_latency": request_latency,
        "hitl_decisions": hitl_decisions,
        "audit_writes": audit_writes,
    }


def setup_tracing():
    """Initialize Jaeger distributed tracing exporter."""
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    trace_provider = TracerProvider()
    trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace.set_tracer_provider(trace_provider)

    return trace.get_tracer(__name__)


def get_tracer():
    """Get global tracer instance."""
    return trace.get_tracer(__name__)


def get_meter():
    """Get global meter instance."""
    return metrics.get_meter(__name__)


# Initialize on module load
try:
    _metrics = setup_metrics()
    _tracer = setup_tracing()
except Exception:
    # Graceful degradation if telemetry not available
    _metrics = {}
    _tracer = None
