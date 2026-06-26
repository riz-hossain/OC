# Playwright Test Template

Use this as the shape for generated web E2E tests. Do not commit this template as a runnable `.spec.ts` file.

```ts
import { test, expect } from "@playwright/test";

test.describe("<feature or workflow>", () => {
  test("<user-visible behavior>", async ({ page }) => {
    // Arrange with deterministic data and existing helpers.
    await page.goto("<route-from-zkme-evidence>");

    // Act with stable locators.
    await page.getByRole("button", { name: "<accessible-name>" }).click();

    // Assert user-visible outcome.
    await expect(page.getByText("<expected-result>")).toBeVisible();
  });
});
```

## Required Before Creating A Real Spec

- Replace route, locators, data, and assertions with evidence-backed values.
- Prefer repo-local helpers if they exist.
- Add a matching manual case under `qa/manual/test-cases/`.
- Add a ZeuZ-compatible candidate when this is a cross-surface workflow.
