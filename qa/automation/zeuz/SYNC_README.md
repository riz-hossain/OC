# ZeuZ Sync Client

`sync_zeuz.py` turns ZKME testcase package implementations, generated testcase drafts, and local run reports into ZeuZ-compatible payloads.

It is generated into every repo by ZKME so local execution does not require ZeuZ Server, but import is ready when credentials are supplied.

## Commands

- Validate generated draft test cases or package ZeuZ action implementations:

  ```bash
  python qa/automation/zeuz/sync_zeuz.py validate-drafts
  ```

- Build a dry-run draft import bundle:

  ```bash
  python qa/automation/zeuz/sync_zeuz.py push-drafts --project-id PROJ-1 --team-id 1 --user-id 1 --user-name qa
  ```

- Build a dry-run result/artifact import bundle:

  ```bash
  python qa/automation/zeuz/sync_zeuz.py push-results --project-id PROJ-1 --team-id 1 --user-id 1
  ```

- Export everything into one offline bundle:

  ```bash
  python qa/automation/zeuz/sync_zeuz.py export-bundle
  ```

Add `--execute --server-url https://zeuz.example.com --api-token ...` only when a human has reviewed the generated drafts and wants to submit to ZeuZ Server.

## ZeuZ Server Targets

- `POST /api/v1/tasks/import-testcases` imports draft test cases.
- `POST /api/v1/tasks/update-test-results` imports `zeuzExecutionLog` result data.
- `POST /api/v1/tasks/process-report-files` imports preserved local artifacts when files exist.

The preferred source is `qa/automation/testcases/<id>/manifest.json` with `implementations/zeuz-actions/actions.json`. Legacy `.zeuz-draft.json` files are still supported as compatibility exports.

Sync validation rejects duplicate ZeuZ step names inside a testcase. Keep `stepKey` as the stable package identity and use `zeuz-bindings.json` for server-assigned numeric ZeuZ step IDs after import.

Generated bundles are written under `qa/automation/zeuz/local-run/`.
