# UI/UX Standards

No UI surface was detected; UI/UX standards are kept for future UI-impacting changes.

## UI Artifact Load Order

Before changing UI, read the smallest relevant source files plus these ZKME artifacts when present:

- `static/ui_surface_index.json`: legacy UI pages, selectors, actions, and assertions
- `static/locator_policy.v1.json`: selector priority and locator stability policy
- `static/layout_tokens.json`: layout, sizing, overflow, grid, flex, and table signals
- `static/ui_event_bindings.v1.json`: interactive UI bindings and network coverage
- `static/frontend_calls.json`: frontend-to-backend calls
- `static/flow_graph.v1.json`: end-to-end user flow graph
- `static/assertion_anchors.v1.json`: existing UI and test assertion anchors

## Detected UI Profile

- Platforms/frameworks: UNKNOWN

## Existing UI Surfaces

- No UI surfaces were enumerated in `static/ui/ui_model.v1.json`.

## Existing Components

- No reusable UI components were detected. Search source before creating a new component.

## Design System First Rule

Agents must preserve the project's existing design system before inventing UI.

1. Reuse existing project components and variants first.
2. Reuse existing layout, spacing, typography, color, icon, form, table, modal, drawer, tab, badge, empty-state, and error-state patterns.
3. If a design token, theme variable, CSS utility, component prop, or shared component exists, use it instead of hardcoding a new visual value.
4. Add a new component only when it captures a repeated workflow or removes meaningful duplication.
5. Do not create a parallel button, input, modal, table, card, badge, toast, navigation, search, or filter system.
6. If no design system is detected, use the most common local pattern and document the evidence used.

## Component Reuse Gate

Before adding or changing UI, answer these checks in the plan or final report:

- Which existing component, pattern, or file was inspected?
- Why can the existing component be reused or extended?
- If a new component is needed, what existing naming, props, state, styling, and test-selector conventions does it follow?
- What empty, loading, error, denied, partial, and success states are affected?
- What keyboard, focus, accessibility-name, responsive, and i18n text-fit checks are required?

## Workflow Rules

- Build the actual operator workflow, not a placeholder or marketing page.
- Define empty, loading, error, denied, partial, and success states for user-facing changes.
- Keep layouts stable while loading or updating.
- Avoid clipped, overlapping, or layout-shifting text.
- Support keyboard operation, visible focus, semantic labels, and accessible names.
- Allow longer translated strings and avoid assumptions based on English text length.
- Preserve the current route/screen model unless the user approved navigation changes.
- Do not hide policy-denied, permission-denied, partial-data, or failed-target states.
- Make destructive, billing, admin, or irreversible actions visibly distinct and confirmation-backed.

## Component Rules

- Search for existing buttons, filters, tables, tabs, modals, drawers, status badges, empty states, and progress patterns before adding new UI patterns.
- Keep destructive actions visually distinct and confirmation-backed.
- Match existing component naming, prop names, data loading patterns, state stores, form libraries, and validation surfaces.
- Prefer composition over forked copies of an existing component.
- Keep page-level layout separate from reusable control components when the project already follows that boundary.
- Do not introduce a new CSS framework, UI library, icon library, animation library, or design token scheme without explicit user approval.
- Keep text inside controls short and stable. Move longer detail to helper text, body copy, table cells, tooltips, or details panels.

## Layout Rules

- Total layout-sensitive tokens: 0

- Use the existing spacing, sizing, grid, flex, table, and overflow patterns surfaced above.
- Keep fixed-format UI stable with explicit dimensions, min/max constraints, aspect ratios, or container-relative sizing.
- Avoid hover, loading, counter, badge, or validation states that resize controls.
- Do not nest cards inside cards.
- Use cards for repeated items, modals, and framed tools; page sections should be unframed or full-width bands unless the existing design system differs.
- Do not use decorative gradients, blobs, or ornamental backgrounds for serious operational workflows.
- Match density to the product domain. SaaS, CRM, admin, QA, analytics, and security tools should prioritize scanability, comparison, and repeated action.

## Controls And Interaction Rules

- Use icons for familiar tool actions when the project already uses an icon library.
- Provide accessible labels or tooltips for icon-only buttons.
- Use segmented controls, tabs, toggles, checkboxes, sliders, steppers, or menus according to the data type and the existing local pattern.
- Search must show the active query, support keyboard focus, and expose empty results with a next action.
- Filters must show applied state and allow clearing one filter or all filters.
- Tables and dense lists must handle empty, loading, error, partial, overflow, sorting/filtering, pagination/virtualization, and narrow viewport states.
- Avoid relying on color alone for status or validation.

## Test Selector And Locator Rules

- Locator priority: `data-automation` > `data-testid` > `data-test` > `aria-label` > `role` > `id` > `name` > `class` > `css` > `xpath`
- Primary platform: `web_generic`
- Generic web locator priorities.

- New interactive elements must expose selectors following the detected locator policy.
- Prefer user-facing role/label/test-id contracts over CSS classes or XPath.
- Locator names should describe stable product intent, not visual implementation.
- Do not rename existing test selectors unless test updates are part of the change.

## Interaction Binding Evidence

- Event bindings: 0
- Bindings with network calls: 0
- Interactive elements covered: 0/1 (0.0%)

- When a UI action calls an API, preserve request shape, auth behavior, error categories, retry behavior, and loading state.
- For new UI-to-API behavior, update or add tests that cover success, validation failure, unauthorized/forbidden, and dependency failure where applicable.

## Agent Anti-Drift Rules

- Do not restyle unrelated screens while implementing a feature.
- Do not create one-off visual language because another AI agent did so elsewhere.
- Do not mix component libraries in one surface unless that is already the project pattern.
- Do not replace semantic HTML or accessibility attributes with div-only UI.
- Do not use screenshots or visual guesses as the only source of truth; cite source files and ZKME artifacts.
- If existing UI is inconsistent, preserve behavior and propose a separate cleanup instead of broad visual churn.

## Required UI Report Fields

For UI work, final reports must include:

- Existing components or patterns reused
- New components added and why they were necessary
- UI states covered: empty/loading/error/denied/partial/success
- Accessibility checks performed
- Responsive/text-fit checks performed
- Test selectors or locator policy followed
- ZKME UI artifacts consulted

## ZKME UI Evidence

- architectureStandards: `SYSTEM_OVERVIEW.md`, `L2_CONTEXT.md`, `ZKME_REPO_PROFILE.json`, `static/files.json`
- developmentStandards: `ZKME_CHANGE_IMPACT.json`, `ZKME_CONTRACTS_INVARIANTS.json`, `static/hot_files.json`
- uiUxStandards: `static/locator_policy.v1.json`, `static/layout_tokens.json`, `static/ui_event_bindings.v1.json`, `static/frontend_calls.json`
- qaStandards: `static/negative_test_matrix.v1.json`, `static/assertion_anchors.v1.json`, `static/data_matrix.v1.json`
- securityStandards: `static/auth_contract.v1.json`, `KNOWN_HAZARDS.md`, `static/hazards.json`
- performanceStandards: `static/runtime_constraints.v1.json`, `static/hot_files.json`, `ZKME_CHANGE_IMPACT.json`
- databaseStandards: `static/db_migrations_intelligence.v1.json`, `DATA_TOUCH_MAP.json`
- i18nStandards: `static/files.json`
- reportingStandard: `00_START_HERE.md`
