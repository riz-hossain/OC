# Performance Automation

Use this folder for load, latency, throughput, memory, startup, and resource-budget checks.

Local runner integration is configured in `qa/automation/config/zkme-adapters.json` under `adapters.performance`.

Preferred command contract:

```json
{
  "schemaVersion": "zkme.adapter-step-request.v1",
  "adapter": "performance",
  "testcase": {"id": "TC-...", "title": "..."},
  "step": {"id": "step-001", "action": "run benchmark"},
  "config": {"budgets": {"p95LatencyMs": 1000}}
}
```

The adapter command must print JSON with `status`, `message`, and optional `artifacts`.
