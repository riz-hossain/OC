# ZeuZ-Compatible Local Reports

This folder stores local execution reports in a shape that can later be sent to ZeuZ Server.

Phase 1 goal:

- run generated tests locally without ZeuZ Server
- preserve enough result metadata to display in ZeuZ later
- keep screenshots, traces, logs, and step statuses linked

## Report Flow

```text
local portable testcase
  -> local execution
  -> local report JSON/HTML
  -> ZeuZ-compatible report JSON with zeuzExecutionLog
  -> future ZeuZ Server import/sync
```

## Files

- `zeuz-report.schema.json`: target shape for ZeuZ-compatible local report envelopes
- generated report files should use `RUN-<timestamp>-<test-id>.zeuz-report.json`

## ZeuZ Server Mapping

The report envelope should preserve both developer-friendly local evidence and a ZeuZ-native projection:

- ZKME local fields: summary, testCases, steps, artifacts, environment, Playwright trace paths
- ZeuZ projection: `zeuzExecutionLog`, shaped like ZeuZ Node `CommonUtil.all_logs_json`
- Result update path: `zeuzExecutionLog[].test_cases[].execution_detail`
- Step update path: `zeuzExecutionLog[].test_cases[].steps[].execution_detail`

Future import/sync can map this file to ZeuZ Server's result update flow and report-file processing without requiring the original local run to happen through ZeuZ Server.

## Rule For AI Agents

When adding local runnable tests, include enough metadata to produce a ZeuZ-compatible report:

- test case id and title
- stable `stepKey`, unique ZeuZ `stepName`, statuses, timings, logs
- artifacts: screenshots, Playwright traces, videos, logs
- environment and browser/device details
- source evidence and ZKME artifacts used
- `zeuzExecutionLog` projection when the run has ZeuZ-compatible steps
