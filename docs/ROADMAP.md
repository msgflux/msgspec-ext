# msgspec_ext SDK Roadmap

Planned features for future releases.

## v1.1.0 - Sampling and Performance

### Trace Sampling
Add support for trace sampling to reduce overhead in high-volume production environments.

**Feature**: `MSGTRACE_TRACE_SAMPLE_RATE`

**Implementation**:
```python
# Environment variable
MSGTRACE_TRACE_SAMPLE_RATE=0.1  # Sample 10% of traces

# In tracer.py, add to _initialize_tracer():
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

sample_rate = float(os.getenv("MSGTRACE_TRACE_SAMPLE_RATE", "1.0"))
sampler = TraceIdRatioBased(sample_rate)
provider = TracerProvider(resource=resource, sampler=sampler)
```

**Use cases**:
- Production environments with high traffic (sample 1-10%)
- Development/staging with full sampling (100%)
- Cost optimization by reducing trace volume
- Performance optimization by reducing overhead

**Configuration options**:
- `1.0` (default) - Capture 100% of traces
- `0.5` - Capture 50% of traces
- `0.1` - Capture 10% of traces
- `0.0` - Disable tracing (alternative to MSGTRACE_TELEMETRY_ENABLED)

**Technical details**:
- Uses OpenTelemetry's `TraceIdRatioBased` sampler
- Deterministic sampling based on trace ID
- Sampling decision propagated to child spans
- No performance impact on non-sampled traces

---

## Future Considerations

### Batch Export Configuration
Fine-tune batch processor settings:
- `MSGTRACE_BATCH_MAX_QUEUE_SIZE`
- `MSGTRACE_BATCH_SCHEDULE_DELAY`
- `MSGTRACE_BATCH_MAX_EXPORT_BATCH_SIZE`

### Custom Samplers
Support for custom sampling strategies:
- Parent-based sampling
- Rate limiting sampler
- Attribute-based sampling

### Metrics Support
Add OpenTelemetry metrics alongside traces:
- Token usage metrics
- Cost metrics
- Latency histograms
- Error rates

### Log Correlation
Automatic correlation between logs and traces:
- Inject trace context into logs
- Link log records to spans
