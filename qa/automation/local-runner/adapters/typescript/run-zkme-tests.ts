#!/usr/bin/env node
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { basename, dirname, isAbsolute, join, resolve } from "node:path";
import { performance } from "node:perf_hooks";

type JsonObject = Record<string, unknown>;
type StepStatus = "passed" | "failed" | "skipped" | "blocked";

interface PortableStep {
  id?: string;
  stepKey?: string;
  stepName?: string;
  intent?: string;
  adapter?: string;
  action?: string;
  input?: JsonObject;
  expected?: string;
  zeuzMapping?: { stepName?: string; stepId?: number; stepSequence?: number };
}

interface PortableTestcase {
  schemaVersion?: string;
  id?: string;
  title?: string;
  targets?: string[];
  baseURL?: string;
  api?: { baseURL?: string };
  steps?: PortableStep[];
}

interface StepResult {
  id: string;
  stepKey: string;
  name: string;
  zeuzStepName: string;
  status: StepStatus;
  message: string;
  durationMs: number;
  startedAt: string;
  endedAt: string;
}

interface TestcaseResult {
  id: string;
  title: string;
  status: StepStatus;
  durationMs: number;
  startedAt: string;
  endedAt: string;
  steps: StepResult[];
}

const runnerDir = dirname(resolve(process.argv[1] || "."));
const testcaseDir = resolve(runnerDir, "..", "..", "test-cases");
const reportDir = resolve(runnerDir, "..", "..", "..", "reports", "zeuz-compatible");

function utcNow(): string {
  return new Date().toISOString();
}

function discoverJsonFiles(paths: string[]): string[] {
  const requested = paths.length ? paths : [testcaseDir];
  const files: string[] = [];
  const visit = (rawPath: string): void => {
    const path = isAbsolute(rawPath) ? rawPath : resolve(process.cwd(), rawPath);
    if (!existsSync(path)) {
      throw new Error(`Path does not exist: ${path}`);
    }
    const stat = statSync(path);
    if (stat.isDirectory()) {
      for (const item of readdirSync(path)) {
        visit(join(path, item));
      }
      return;
    }
    if (path.endsWith(".json")) {
      files.push(path);
    }
  };
  for (const requestedPath of requested) {
    visit(requestedPath);
  }
  return files.sort();
}

function loadTestcase(path: string): PortableTestcase {
  const testcase = JSON.parse(readFileSync(path, "utf-8")) as PortableTestcase;
  if (testcase.schemaVersion !== "zkme.portable-testcase.v1") {
    throw new Error(`${path}: expected schemaVersion zkme.portable-testcase.v1`);
  }
  if (!testcase.id || !testcase.title || !Array.isArray(testcase.steps)) {
    throw new Error(`${path}: missing id, title, or steps`);
  }
  return testcase;
}

function joinUrl(baseURL: string, url: string): string {
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  if (!baseURL) {
    throw new Error(`Relative URL requires testcase.baseURL or api.baseURL: ${url}`);
  }
  return `${baseURL.replace(/\/+$/, "")}/${url.replace(/^\/+/, "")}`;
}

async function executeApiStep(step: PortableStep, testcase: PortableTestcase): Promise<{ message: string }> {
  const input = (step.input || {}) as JsonObject;
  const method = String(input.method || step.action || "GET").toUpperCase();
  const baseURL = testcase.baseURL || testcase.api?.baseURL || "";
  const url = joinUrl(baseURL, String(input.url || "/"));
  const expectedStatus = Number(input.expectedStatus || input.status || 200);
  const headers = { ...((input.headers as JsonObject | undefined) || {}) } as Record<string, string>;
  let body: string | undefined;
  if (Object.prototype.hasOwnProperty.call(input, "json")) {
    body = JSON.stringify(input.json);
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  } else if (typeof input.body === "string") {
    body = input.body;
  }
  const response = await fetch(url, { method, headers, body });
  const text = await response.text();
  if (response.status !== expectedStatus) {
    throw new Error(`Expected HTTP ${expectedStatus}, got ${response.status}: ${text.slice(0, 500)}`);
  }
  const expectedContains = input.expectedContains;
  if (typeof expectedContains === "string" && !text.includes(expectedContains)) {
    throw new Error(`Response did not contain expected text: ${expectedContains}`);
  }
  return { message: `${method} ${url} -> ${response.status}` };
}

async function executeStep(step: PortableStep, testcase: PortableTestcase): Promise<{ status: StepStatus; message: string }> {
  const adapter = String(step.adapter || "manual").toLowerCase();
  if (adapter === "api") {
    const result = await executeApiStep(step, testcase);
    return { status: "passed", message: result.message };
  }
  if (["manual", "playwright", "db", "mobile", "desktop", "performance", "security"].includes(adapter)) {
    return { status: "skipped", message: `${adapter} step recorded as a portable candidate for the project adapter.` };
  }
  throw new Error(`Unsupported adapter: ${adapter}`);
}

function aggregateStatus(statuses: StepStatus[]): StepStatus {
  if (statuses.includes("failed")) return "failed";
  if (statuses.includes("blocked")) return "blocked";
  if (statuses.length > 0 && statuses.every((status) => status === "skipped")) return "skipped";
  return "passed";
}

async function runTestcase(path: string): Promise<TestcaseResult> {
  const testcase = loadTestcase(path);
  const startedAt = utcNow();
  const start = performance.now();
  const steps: StepResult[] = [];
  for (const [index, step] of (testcase.steps || []).entries()) {
    const stepStartedAt = utcNow();
    const stepStart = performance.now();
    let status: StepStatus = "passed";
    let message = "";
    try {
      const result = await executeStep(step, testcase);
      status = result.status;
      message = result.message;
    } catch (error) {
      status = "failed";
      message = error instanceof Error ? error.message : String(error);
    }
    steps.push({
      id: step.stepKey || step.id || `step-${index + 1}`,
      stepKey: step.stepKey || step.id || `step-${index + 1}`,
      name: step.zeuzMapping?.stepName || step.stepName || step.intent || step.action || `Step ${index + 1}`,
      zeuzStepName: step.zeuzMapping?.stepName || step.stepName || step.intent || step.action || `Step ${index + 1}`,
      status,
      message,
      durationMs: Math.round(performance.now() - stepStart),
      startedAt: stepStartedAt,
      endedAt: utcNow(),
    });
    if (status === "failed") {
      break;
    }
  }
  return {
    id: testcase.id || basename(path, ".json"),
    title: testcase.title || testcase.id || basename(path),
    status: aggregateStatus(steps.map((step) => step.status)),
    durationMs: Math.round(performance.now() - start),
    startedAt,
    endedAt: utcNow(),
    steps,
  };
}

function zeuzStatus(status: StepStatus): string {
  return { passed: "Passed", failed: "Failed", skipped: "Skipped", blocked: "Blocked" }[status];
}

function buildReport(results: TestcaseResult[]): JsonObject {
  const runId = `RUN-ZKME-TS-${Date.now()}`;
  const status = aggregateStatus(results.map((result) => result.status));
  return {
    schemaVersion: "zkme.zeuz-compatible-report.v1",
    run: { id: runId, source: "typescript-portable-runner", startedAt: utcNow(), endedAt: utcNow(), environment: "local" },
    summary: {
      status,
      passed: results.filter((result) => result.status === "passed").length,
      failed: results.filter((result) => result.status === "failed").length,
      skipped: results.filter((result) => result.status === "skipped").length,
      durationMs: results.reduce((total, result) => total + result.durationMs, 0),
    },
    testCases: results,
    zeuzExecutionLog: [
      {
        run_id: runId,
        test_cases: results.map((result) => ({
          testcase_no: result.id,
          title: result.title,
          execution_detail: { status: zeuzStatus(result.status), teststarttime: result.startedAt, testendtime: result.endedAt },
          steps: result.steps.map((step, index) => ({
            step_id: index + 1,
            step_key: step.stepKey,
            step_sequence: index + 1,
            name: step.zeuzStepName || step.name,
            execution_detail: { status: zeuzStatus(step.status), stepstarttime: step.startedAt, stependtime: step.endedAt },
          })),
        })),
      },
    ],
  };
}

async function main(): Promise<number> {
  const paths = discoverJsonFiles(process.argv.slice(2));
  const results: TestcaseResult[] = [];
  for (const path of paths) {
    results.push(await runTestcase(path));
  }
  mkdirSync(reportDir, { recursive: true });
  const report = buildReport(results);
  const reportPath = join(reportDir, `${String((report.run as JsonObject).id)}.zeuz-report.json`);
  writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n", "utf-8");
  console.log(JSON.stringify({ status: aggregateStatus(results.map((result) => result.status)), testcases: results.length, reportPath }, null, 2));
  return results.some((result) => result.status === "failed") ? 1 : 0;
}

main().then((code) => process.exit(code)).catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
