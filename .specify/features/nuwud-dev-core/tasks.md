# Tasks: nuwud-dev Core Operations Platform

**Input**: `.specify/features/nuwud-dev-core/plan.md`, `.specify/features/nuwud-dev-core/spec.md`
**Prerequisites**: plan.md ✅ spec.md ✅ (research, data-model, quickstart, contracts embedded in plan.md)
**Generated**: 2026-05-01

## Format: `[ID] [P?] [Story] Description — file path (FR refs)`

- **[P]**: Parallelizable with other [P] tasks in same phase (different files, no shared dependencies)
- **[Story]**: User story tag maps to spec.md priorities ([US1]=P1 … [US6]=P6)
- No test tasks — not requested in spec

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repo skeleton and credential model. Must be complete before any script or workflow work.

- [x] T001 Create `.env.example` with all required keys (no values): `PRINTIFY_API_TOKEN`, `PRINTIFY_SHOP_ID`, `PRINTFUL_API_TOKEN`, `SHOPIFY_STORE_DOMAIN`, `LOGO_DIR`, `NOTION_TOKEN` in `.env.example` — (FR-005, FR-006, FR-023)
- [x] T002 [P] Create `.gitignore` covering `.env`, `__pycache__/`, `*.pyc`, `*.egg-info/`, `.pytest_cache/` in `.gitignore` — (FR-006, SC-006)
- [x] T003 [P] Create `requirements.txt` with `requests>=2.31.0` and `python-dotenv>=1.0.0` in `requirements.txt` — (FR-022)
- [x] T004 [P] Create `scripts/` package structure: empty `scripts/__init__.py` and `scripts/lib/__init__.py` in `scripts/lib/__init__.py` — (FR-021)
- [x] T005 [P] Create `assets/README.md` documenting the four canonical logo assets (filenames, use cases, canonical path at `LOGO_DIR`) in `assets/README.md` — (Decision 8, FR-023)

**Checkpoint**: Repo structure and credential scaffolding in place — library implementation can begin

---

## Phase 2: Foundational (Shared Library Helpers — blocks all script phases)

**Purpose**: Core `lib/` helpers shared by every script. Must be fully implemented before any CLI script work starts.

⚠️ **CRITICAL**: No user-story script work can begin until T006 and T007 are complete.

- [x] T006 Implement `scripts/lib/env.py` — `require_env(keys: list[str]) -> dict` that collects all missing keys, prints them as a list, and calls `sys.exit(1)` before any API call is made in `scripts/lib/env.py` — (FR-005, FR-022, Decision 7)
- [x] T007 Implement `scripts/lib/printify.py` — four functions: `upload_image(token, file_path) -> image_id` (base64 encode + POST `/v1/uploads/images.json`), `get_variants(token, blueprint_id, provider_id) -> list` (GET catalog API, no caching), `create_product(token, shop_id, config, image_id, variant_ids) -> product_id` (POST `/v1/shops/{id}/products.json`), `publish(token, shop_id, product_id)` (POST `/v1/shops/{id}/products/{id}/publish.json`); also define `PRODUCT_CONFIGS` dict keyed by slug (`sticker-3in`, `sticker-sheet`, `tote`) with `blueprint_id`, `provider_id`, `placeholders`, `logo_asset`, `title`, `description` in `scripts/lib/printify.py` — (FR-001, FR-002, FR-003, FR-004, Decision 1, Decision 2, Decision 3)

**Checkpoint**: Shared helpers complete — US1 script implementation can begin

---

## Phase 3: User Story 1 — Printify Product Creation (Priority: P1) 🎯 MVP

**Goal**: Single command creates and publishes any supported Printify POD product to Shopify without browser work.

**Independent Test**: `python scripts/create_printify_product.py --product sticker-3in` from repo root — verify product appears published in Shopify admin with correct title, variants, and logo.

**FR Coverage**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-021, FR-022

### Implementation

- [x] T008 [US1] Implement `scripts/list_blueprints.py` — argparse CLI with optional `--provider` flag (default 73), calls `require_env(["PRINTIFY_API_TOKEN"])`, fetches blueprints via Printify catalog API, prints as formatted table; exit codes 0 (success), 1 (missing env), 3 (API error) in `scripts/list_blueprints.py` — (FR-001, FR-005, FR-021, FR-022)
- [x] T009 [US1] Implement `scripts/create_printify_product.py` — argparse CLI with `--product` (sticker-3in | sticker-sheet | tote), optional `--logo-path` override, optional `--dry-run` flag; calls `require_env`, resolves logo path from `LOGO_DIR` or `--logo-path`, uploads image via `lib/printify.upload_image`, fetches variants via `lib/printify.get_variants`, creates product via `lib/printify.create_product` using `PRODUCT_CONFIGS[slug]`, publishes via `lib/printify.publish`; implements all exit codes 0–4 as specified in CLI contract in `scripts/create_printify_product.py` — (FR-001 through FR-006, FR-021, FR-022, SC-001)
- [x] T010 [US1] Validate sticker-3in end-to-end: run `python scripts/create_printify_product.py --product sticker-3in --dry-run` and confirm dry-run exits 0; run live and verify product published to Shopify within 90s in `scripts/create_printify_product.py` — (SC-001, acceptance scenario 1)
- [x] T011 [US1] Validate sticker-sheet: run `python scripts/create_printify_product.py --product sticker-sheet` and confirm all four placeholders `front_1`, `front_2`, `front_3`, `front_4` are populated (not `front`) — (FR-001, Decision 3, acceptance scenario 2)
- [x] T012 [US1] Validate tote: run `python scripts/create_printify_product.py --product tote` and confirm `front` placeholder is populated with light-background logo — (FR-001, acceptance scenario 3)
- [x] T013 [US1] Add **Printify** section to `TOOLS.md` covering: prerequisites, `.env` setup, `list_blueprints.py` usage, all three `create_printify_product.py` invocations, `--dry-run` mode, and expected exit codes in `TOOLS.md` — (FR-012, SC-007)

**Checkpoint**: US1 complete — Printify automation fully functional and documented

---

## Phase 4: User Story 2 — Printful Embroidery Product Creation (Priority: P2)

**Goal**: Single command creates an embroidered hat (3D Puff) in Printful and syncs to Shopify, for both snapback and dad-hat styles.

**Independent Test**: `python scripts/create_printful_product.py --style snapback` — verify a Printful sync item appears in Shopify admin with correct hat variant and embroidery design.

**FR Coverage**: FR-007, FR-008, FR-009, FR-021, FR-022

### Implementation

- [ ] T014 [US2] Implement `scripts/lib/printful.py` — `create_sync_product(token, style, logo_svg_path) -> sync_product_id` that POSTs to `POST /store/products` with `sync_product` + `sync_variants` payload; define hat style configs mapping `snapback` → Yupoong 6089M variant IDs and `dad-hat` → Yupoong 6245CM variant IDs with 3D Puff embroidery technique in `scripts/lib/printful.py` — (FR-007, FR-008, Decision 4)
- [ ] T015 [US2] Implement `scripts/create_printful_product.py` — argparse CLI with `--style` (snapback | dad-hat), optional `--logo-path` override, optional `--dry-run` flag; calls `require_env(["PRINTFUL_API_TOKEN", "SHOPIFY_STORE_DOMAIN", "LOGO_DIR"])`, validates SVG logo path exists before any API call, calls `lib/printful.create_sync_product`; implements exit codes 0–3 as specified in CLI contract in `scripts/create_printful_product.py` — (FR-007, FR-008, FR-009, FR-022, SC-002)
- [ ] T016 [US2] Validate snapback flow: run `python scripts/create_printful_product.py --style snapback --dry-run`; run live and verify Yupoong 6089M sync item appears in Shopify admin — (SC-002, acceptance scenario 1)
- [ ] T017 [US2] Validate dad-hat flow: run `python scripts/create_printful_product.py --style dad-hat` and verify Yupoong 6245CM sync item appears in Shopify admin — (acceptance scenario 2)
- [ ] T018 [US2] Add **Printful** section to `TOOLS.md` covering: snapback and dad-hat commands, SVG logo requirement, Shopify sync verification steps in `TOOLS.md` — (FR-012, SC-007)

**Checkpoint**: US2 complete — embroidered hat products sync to Shopify, Printful pillar documented

---

## Phase 5: User Story 3 — Revenue Scout Agent (Priority: P3)

**Goal**: n8n workflow auto-scores leads every 2 hours, delivers ranked Revenue Leak Lead List to Notion + Slack, with no client-facing messages sent without Patrick's approval.

**Independent Test**: Import `n8n-workflows/revenue-scout.json`, trigger manually, verify a scored Lead record with all required fields appears in Notion and a Slack announcement fires.

**FR Coverage**: FR-013, FR-014, FR-015, FR-016, FR-020

### Implementation

- [ ] T019 [US3] Build and export `n8n-workflows/revenue-scout.json` — workflow structure: Cron trigger (every 2h) → HTTP Request node (GET lead source data) → Ollama HTTP node (`qwen3:30b-a3b`, lead scoring + diagnosis prompt) → Code node (parse scores, build Lead entity with fields: `business_name`, `opportunity_type`, `revenue_leak_diagnosis`, `score`, `proposed_outreach`, `approval_status="pending"`) → Notion node (write Lead record) → Slack node (announce ranked list) → Human Approval (Wait) node (gates any outreach write) in `n8n-workflows/revenue-scout.json` — (FR-013, FR-014, FR-015, FR-016, FR-020, Decision 5, Decision 6)
- [ ] T020 [US3] Validate Revenue Scout offline: import JSON to n8n, trigger manually, verify Lead record appears in Notion with all five required fields populated — (SC-003, acceptance scenario 1)
- [ ] T021 [US3] Validate approval gate: confirm Slack outreach message is NOT sent until Patrick approves in n8n UI; confirm graceful Slack error notification fires when Ollama is offline — (FR-015, SC-005, acceptance scenario 4)
- [ ] T022 [US3] Add **Revenue Scout Agent** section to `TOOLS.md` covering: n8n import steps, manual trigger, expected Notion Lead fields, Slack output format, approval workflow in `TOOLS.md` — (FR-012, SC-007, SC-010)

**Checkpoint**: US3 complete — lead scoring runs on cron, all outputs version-controlled

---

## Phase 6: User Story 4 — Offer Framing Agent (Priority: P4)

**Goal**: Webhook-triggered agent converts raw client notes into a structured 7-field offer document in Notion, gated by human approval before any client-facing use.

**Independent Test**: POST sample client transcript to n8n webhook; verify Notion Offer record has all 7 required fields and `approval_status = "for_review"`.

**FR Coverage**: FR-013, FR-015, FR-017, FR-020

### Implementation

- [ ] T023 [US4] Build and export `n8n-workflows/offer-framing.json` — workflow structure: Webhook trigger (POST, raw client notes body) → Ollama HTTP node (`qwen3:30b-a3b`, offer framing prompt that explicitly enforces `pricing_floor > any client budget hint present in input`) → Code node (parse output into Offer entity: `client_name`, `problem_summary`, `revenue_leak_diagnosis`, `offer_tier`, `pricing_floor`, `scope_boundaries`, `upsell_paths`, `risk_warnings`, `approval_status="for_review"`) → Notion node (write Offer record) → Human Approval (Wait) node (gates all client-facing output) in `n8n-workflows/offer-framing.json` — (FR-013, FR-015, FR-017, FR-020, Decision 6)
- [ ] T024 [US4] Validate Offer Framing: POST sample transcript to webhook URL; verify Notion record contains all 7 required fields; verify `pricing_floor` exceeds any budget hint in the sample input — (SC-004, acceptance scenarios 1–3)
- [ ] T025 [US4] Add **Offer Framing Agent** section to `TOOLS.md` covering: webhook URL, POST body format, expected 7-field output, approval workflow, "for_review" status meaning in `TOOLS.md` — (FR-012, SC-007, SC-010)

**Checkpoint**: US4 complete — offer documents generated from raw notes, pricing floor enforced

---

## Phase 7: User Story 5 — Client Reactivation Agent (Priority: P5)

**Goal**: Manual-trigger agent reads historical client records from Notion, assigns each to exactly one of six categories, writes category + reasoning back to Notion, never includes legacy pricing in outreach suggestions.

**Independent Test**: Provide sample client records; run workflow; verify all records assigned to one of six allowed categories and no "do_not_chase" record has a suggested next action.

**FR Coverage**: FR-013, FR-015, FR-018, FR-019, FR-020

### Implementation

- [ ] T026 [US5] Build and export `n8n-workflows/client-reactivation.json` — workflow structure: Manual trigger → Notion node (read ClientRecord pages) → Ollama HTTP node (`qwen3:30b-a3b`, categorization prompt listing exactly the six allowed categories, explicit rule: "if category is do_not_chase set suggested_next_action to null", explicit rule: "never reference legacy pricing rates") → Code node (validate category is one of the six, enforce pricing guard) → Notion node (write `category` + `reasoning_note` back to record) → Human Approval (Wait) node (gates any outreach suggestion write) in `n8n-workflows/client-reactivation.json` — (FR-013, FR-015, FR-018, FR-019, FR-020, Decision 6)
- [ ] T027 [US5] Validate categorization: run with sample records, verify all six categories can be assigned, verify "do_not_chase" records have `suggested_next_action = null` — (SC-009, acceptance scenarios 1, 3)
- [ ] T028 [US5] Validate pricing guard: confirm no "legacy_underpriced" outreach suggestion contains any previous rate reference — (FR-019, acceptance scenario 2)
- [ ] T029 [US5] Add **Client Reactivation Agent** section to `TOOLS.md` covering: manual trigger steps, Notion input format, six category definitions, pricing guard explanation in `TOOLS.md` — (FR-012, SC-007, SC-010)

**Checkpoint**: US5 complete — all client records categorized, pricing guard enforced, workflows version-controlled

---

## Phase 8: User Story 6 — Shopify Hydrogen Storefront Tooling (Priority: P6)

**Goal**: `TOOLS.md` is the single source of truth for all Hydrogen commands; contributors can follow it without external guidance.

**Independent Test**: A contributor with a fresh clone follows TOOLS.md to run `npm run typecheck` and `npm run build` at `C:\Users\Nuwud\Projects\MyStore\` successfully.

**FR Coverage**: FR-010, FR-011, FR-012

### Implementation

- [ ] T030 [P] [US6] Add **Shopify Hydrogen Storefront** section to `TOOLS.md` covering: storefront path (`C:\Users\Nuwud\Projects\MyStore\`), `npm run dev`, `npm run codegen` (when to run: after any GraphQL schema change), `npm run typecheck` (must pass before deploy), `npm run build` (must succeed before Oxygen deploy); include expected output for each command in `TOOLS.md` — (FR-010, FR-011, FR-012, SC-007, SC-008)
- [ ] T031 [P] [US6] Add storefront boundary callout to `TOOLS.md` clarifying that nuwud-dev contains only tooling commands targeting MyStore via API/CLI — no storefront source files live here (Constitution §V) in `TOOLS.md` — (FR-012, Constitution §V)

**Checkpoint**: US6 complete — Hydrogen tooling fully documented for contributors

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, documentation audit, final repo hygiene.

- [ ] T032 [P] Audit `.gitignore` completeness — verify `.env`, `__pycache__/`, `*.pyc`, `*.egg-info/`, `.pytest_cache/` are all present; add any missing entries in `.gitignore` — (FR-006, SC-006)
- [ ] T033 [P] Review `TOOLS.md` end-to-end — verify every documented script runs from `scripts/` with only the described setup; fix any stale command or path reference in `TOOLS.md` — (SC-007)
- [ ] T034 [P] Verify `assets/README.md` documents all four logo assets with exact filenames and use cases matching the plan.md canonical mapping table in `assets/README.md` — (Decision 8)
- [ ] T035 Final smoke test from clean shell: run `python scripts/create_printify_product.py --product sticker-3in --dry-run` from repo root with only `requirements.txt` deps installed; confirm exit 0 — (SC-001, FR-021, SC-007)

---

## Dependencies

User story completion order (each phase unlocks the next column):

```
Phase 1 (Setup)
    └── Phase 2 (Foundational lib)
            ├── Phase 3 (US1 — Printify) ──────── T013 (TOOLS.md Printify)
            │       └── Phase 4 (US2 — Printful) ─ T018 (TOOLS.md Printful)
            │
            ├── Phase 5 (US3 — Revenue Scout) ──── T022 (TOOLS.md Revenue Scout)
            │       └── Phase 6 (US4 — Offer Framing) ── T025 (TOOLS.md Offer Framing)
            │               └── Phase 7 (US5 — Client Reactivation) ── T029 (TOOLS.md Client Reactivation)
            │
            └── Phase 8 (US6 — Hydrogen Tooling) ── T030-T031 (TOOLS.md Hydrogen)
                        └── Phase 9 (Polish)
```

**Key constraints**:
- T006 (`env.py`) must be complete before T008, T009, T014, T015 (all CLI scripts)
- T007 (`printify.py`) must be complete before T008, T009 (Printify scripts)
- T014 (`printful.py`) must be complete before T015 (Printful CLI)
- Phases 5–7 (n8n agents) are independent of Phases 3–4 (Python scripts) — can run in parallel after Phase 2
- Phase 6 must follow Phase 5 (Offer Framing builds on Revenue Scout patterns)
- Phase 9 must be last

---

## Parallel Execution Examples

### After Phase 2 completes, these can run simultaneously:

**Track A — Printify (US1)**: T008 → T009 → T010 → T011 → T012 → T013  
**Track B — Agent Workflows (US3+)**: T019 → T020 → T021 → T022  
**Track C — Hydrogen (US6)**: T030, T031 (both [P])

### Within Phase 4 (US2):

T014 (printful.py) and Phase 1 cleanup tasks [P] can run alongside each other.

---

## Implementation Strategy

**MVP Scope (Phase 1 + 2 + 3 only)**:
- 13 tasks: T001–T013
- Delivers: complete Printify automation for all three product types, fully documented
- Satisfies: FR-001 through FR-006, FR-021 through FR-023, SC-001, SC-006, SC-007 (partial)

**Full delivery order**: Phases 1 → 2 → 3 → 4 → 5–7 (agents) || 6 → 8 → 9

---

## Summary

| Phase | Stories | Tasks | Parallel | TOOLS.md Task |
|---|---|---|---|---|
| 1 — Setup | — | T001–T005 | T002, T003, T004, T005 | — |
| 2 — Foundation | — | T006–T007 | — | — |
| 3 — Printify | US1 (P1) | T008–T013 | — | T013 |
| 4 — Printful | US2 (P2) | T014–T018 | T015 | T018 |
| 5 — Revenue Scout | US3 (P3) | T019–T022 | — | T022 |
| 6 — Offer Framing | US4 (P4) | T023–T025 | — | T025 |
| 7 — Client Reactivation | US5 (P5) | T026–T029 | — | T029 |
| 8 — Hydrogen Tooling | US6 (P6) | T030–T031 | T030, T031 | T030–T031 |
| 9 — Polish | — | T032–T035 | T032, T033, T034 | — |
| **Total** | **6 stories** | **35 tasks** | **12 parallelizable** | **7 pillar docs** |
