# TypeScript Portable Runner

This folder contains a native TypeScript wrapper for `zkme.portable-testcase.v1` files.

It is intended for JavaScript/TypeScript projects that want to load ZKME generated testcases without translating them by hand.

Run after installing a TypeScript runtime such as `tsx` or `ts-node`:

```bash
npx tsx qa/automation/local-runner/adapters/typescript/run-zkme-tests.ts
```

The wrapper discovers JSON files under `qa/automation/local-runner/test-cases/`, executes API steps through `fetch`, records unsupported platform steps as candidates, and writes a ZeuZ-compatible local report under `qa/automation/reports/zeuz-compatible/`.
