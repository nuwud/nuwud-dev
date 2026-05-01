# Implementation Plan: nuwud-dev Core Operations Platform

**Branch**: `main` (core infrastructure) | **Date**: 2026-05-01 | **Spec**: [spec.md](./spec.md)  
**Input**: `.specify/features/nuwud-dev-core/spec.md`  
**Constitution**: `.specify/memory/constitution.md`

---

## Summary

Build the three-pillar internal automation platform for Nuwud Multimedia LLC:

1. **POD Automation** — Python CLI scripts to create and publish Printify (stickers, tote) and Printful (embroidered hats) products to Shopify without manual browser work.
2. **Shopify Hydrogen Tooling** — Documented commands and scripts that target the MyStore Hydrogen project at `C:\Users\Nuwud\Projects\MyStore\` via API/CLI; no storefront source lives here.
3. **Internal Agent Automation** — n8n workflow JSON files (Revenue Scout, Offer Framing, Client Reactivation) using local Ollama inference, with Notion/Slack output and mandatory human-approval gates on all client-facing actions.

All three pillars share a single credential model (`.env`), a single scripts directory (`scripts/`), and the dual-memory principle (`.specify/` + Notion).

---

## Technical Context

**Language/Version**: Python 3.11+ (scripts), JSON (n8n workflow definitions)  
**Primary Dependencies**: `requests`, `python-dotenv` (Python); n8n (workflow engine, external)  
**Storage**: No persistent local storage — Notion (agent outputs), Qdrant `http://localhost:6333` (vector memory for agents)  
**Testing**: Manual CLI execution for scripts; n8n test execution for workflows; `pytest` optional for lib/ unit tests  
**Target Platform**: Windows (PowerShell-compatible); Python scripts invoked from project root  
**Project Type**: Tooling/automation scripts + importable workflow JSON files  
**Performance Goals**: SC-001 (Printify product created + published < 90s); SC-002 (Printful hat synced < 120s); SC-004 (offer doc < 5 min)  
**Constraints**: All secrets from `.env` only; no cloud LLM for inference; Windows PowerShell compatibility required  
**Scale/Scope**: Single-operator (Patrick); 3 POD product types; 3 agent workflows; ~10 Python scripts total

### Resolved Architecture Decisions

| Decision | Resolution |
|---|---|
| POD script structure | Single-file per product type + shared `scripts/lib/` helpers |
| Printify API base | `https://api.printify.com/v1` — Bearer token auth |
| Printful API base | `https://api.printful.com` — Bearer token auth |
| Printify blueprints | 358 (die-cut sticker 3"), 661 (sticker sheet), 51 (tote bag); provider 73 (Printed Simply) |
| Sticker sheet placeholders | `front_1`, `front_2`, `front_3`, `front_4` — NOT `front` |
| Shopify handle | `31zh0s-4t` / `31zh0s-4t.myshopify.com` |
| Agent inference | Ollama `http://localhost:11434`, model `qwen3:30b-a3b` |
| Agent orchestration | n8n cloud (`nuwud.app.n8n.cloud`) + local Docker port 5678 |
| Notification | Slack via n8n Slack node |
| Notion integration | Notion API via `NOTION_TOKEN` env var |
| Vector memory | Qdrant `http://localhost:6333` |
| Human approval gate | n8n Human Approval node before ALL client-facing action nodes |
| OpenClaw gateway | `ws://127.0.0.1:3100` |
| Tapstitch | Explicitly out of scope — no API; manual wizard only |
| Hydrogen storefront boundary | No storefront source in nuwud-dev; TOOLS.md documents commands only |

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-evaluated after Phase 1 design.*

| Principle | Gate | Status | Notes |
|---|---|---|---|
| I. Automation-First | All repeatable tasks scriptable; >3-step workflows get a script | ✅ PASS | All three pillars are pure automation. Tapstitch (no API) is the documented exception. |
| II. Secrets Stay Local | No credentials in VCS; `.env.example` kept in sync | ✅ PASS | FR-005/006/023 enforce this. Pre-commit check planned (SC-006). |
| III. Local AI by Default | Ollama is primary inference; cloud APIs for integration actions only | ✅ PASS | FR-013 mandates Ollama for reasoning/scoring. Cloud only for Slack/Notion writes. |
| IV. Script Portability (Windows-First) | All scripts run in PowerShell on Windows | ✅ PASS | Python scripts invoked as `python scripts/...`; no Linux-only tooling. |
| V. Shopify Hydrogen Standards | TypeScript for Hydrogen; codegen after GraphQL changes; no storefront source in nuwud-dev | ✅ PASS | FR-010/011/012 enforced. Storefront at `MyStore/` stays separate. |
| VI. Dual Memory | `.specify/` (git) + Notion sync for all plans/specs/outputs | ✅ PASS | Post-plan action: sync to Notion page 3501ef62-3177-81a0-a126-c2afdd5889ee. |
| VII. Simplicity (YAGNI) | No abstraction without 3 use cases | ✅ PASS | `lib/` helpers justified by ≥3 scripts each. No over-engineering of shared infra. |

**Gate Result**: ✅ ALL PASS — proceed to Phase 0.

---

## Phase 0: Research

> **Status**: Complete — all decisions resolved by explicit architecture input. No NEEDS CLARIFICATION items remain.

### research.md

#### Decision 1: Printify Image Upload Strategy

- **Decision**: Base64 encode image file at upload time; use `POST /v1/uploads/images.json` with `{"file_name": "...", "contents": "<base64>"}`.
- **Rationale**: Printify API requires base64 encoding for uploads. No pre-signed URLs.
- **Alternatives considered**: URL-based upload (requires public hosting of logo — rejected; keeps assets local).

#### Decision 2: Variant Fetching Strategy

- **Decision**: Always `GET /v1/catalog/blueprints/{bp}/print_providers/{p}/variants.json` on each script run; never cache variant IDs.
- **Rationale**: FR-003 and edge case — blueprint variants can change between runs. Stale hardcoded IDs would silently publish wrongly-configured products.
- **Alternatives considered**: Local JSON cache with TTL — rejected; adds complexity and failure mode without significant speed benefit.

#### Decision 3: Placeholder Configuration

- **Decision**: Encode placeholder names per blueprint in `scripts/lib/printify.py` as a configuration dict keyed by blueprint ID.
- **Rationale**: Sticker sheet (661) uses `front_1`..`front_4` while all other blueprints use `front`. Centralizing this prevents per-script divergence.
- **Alternatives considered**: Runtime discovery from API — catalog API does not reliably expose placeholder names; hardcoded map is safer.

#### Decision 4: Printful Hat Product Creation

- **Decision**: Use Printful API `POST /store/products` with `sync_product` + `sync_variants` payload. Hat styles (6089M snapback, 6245CM dad hat) selected via `--style` CLI argument.
- **Rationale**: Printful does not have a "blueprint" model; products are created via sync with variant catalog IDs.
- **Alternatives considered**: Printful mockup generator endpoint — not required for product creation.

#### Decision 5: n8n Workflow Storage

- **Decision**: Export each workflow as JSON from n8n UI (`Settings → Export`) and commit to `n8n-workflows/` directory.
- **Rationale**: FR-020/SC-010 require version-controlled workflow definitions. JSON export is the standard n8n portability format.
- **Alternatives considered**: n8n API backup — requires running n8n instance; manual export is reliable and simpler.

#### Decision 6: Human Approval Gate Implementation

- **Decision**: Every n8n workflow that can trigger a client-facing action (email, DM, Slack message, Notion write with `approval_status = "pending"`) MUST include an n8n Human Approval (Wait) node. The workflow pauses until Patrick clicks Approve/Reject in the n8n UI or a Slack approval button.
- **Rationale**: FR-015/SC-005 are hard constraints. No bypass path.
- **Alternatives considered**: Webhook-based approval — acceptable alternative but adds external dependency; n8n native approval is self-contained.

#### Decision 7: `.env` Validation Pattern

- **Decision**: `scripts/lib/env.py` provides a `require_env(keys: list[str]) -> dict` function. All scripts call this before any API call. Missing keys → print full list of missing vars → `sys.exit(1)`.
- **Rationale**: FR-005/edge case: fail-fast with full missing-key list prevents confusing mid-execution API errors.
- **Alternatives considered**: Pydantic BaseSettings — adds a dependency not otherwise needed (YAGNI).

#### Decision 8: Logo Asset References

- **Decision**: Logo files are NOT copied into nuwud-dev. `assets/README.md` documents the canonical path on disk (`C:\Users\Nuwud\Projects\Nuwud Multimedia LLC\Nuwud Logos\`). Scripts accept `--logo-path` override or default to the path in `.env` as `LOGO_DIR`.
- **Rationale**: Constitution §II — no large binary assets in VCS. The actual files live in the Nuwud Multimedia project directory.
- **Alternatives considered**: Git LFS — adds infrastructure complexity; path reference + env var is simpler.

---

## Phase 1: Design

### data-model.md

#### Entity: Product Configuration

Represents a POD product type as configured for a specific provider. Stateless — derived fresh each run.

```python
@dataclass
class ProductConfig:
    blueprint_id: int          # Printify blueprint (e.g., 358, 661, 51)
    provider_id: int           # Print provider (e.g., 73 = Printed Simply)
    placeholders: list[str]    # e.g., ["front"] or ["front_1","front_2","front_3","front_4"]
    logo_asset: str            # Absolute path to logo file (PNG or SVG)
    title: str                 # Product title for Shopify
    description: str           # Product description
```

Supported product types:

| Slug | Blueprint | Provider | Placeholders | Logo Asset |
|---|---|---|---|---|
| `sticker-3in` | 358 | 73 | `["front"]` | `Nuwud-Gorilla-Logo-Fixed.png` |
| `sticker-sheet` | 661 | 73 | `["front_1","front_2","front_3","front_4"]` | `Nuwud-Gorilla-Logo-Fixed.png` |
| `tote` | 51 | 73 | `["front"]` | `Nuwud-Gorilla-Logo-Fixed.png` |

#### Entity: Lead

A business opportunity record output by the Revenue Scout Agent. Written to Notion and announced in Slack.

```
Lead {
  business_name: str          # Company or individual name
  opportunity_type: str       # e.g., "weak Shopify store", "abandoned cart flow"
  revenue_leak_diagnosis: str # Specific problem identified
  score: int                  # 0–100 priority score
  proposed_outreach: str      # Draft first message (awaiting approval)
  approval_status: str        # "pending" | "approved" | "rejected"
  created_at: datetime
}
```

State transitions: `pending → approved` (Patrick approves) | `pending → rejected` (Patrick rejects). No outreach sent until `approved`.

#### Entity: Offer

Structured proposal document output by the Offer Framing Agent.

```
Offer {
  client_name: str
  problem_summary: str
  revenue_leak_diagnosis: str
  offer_tier: str             # e.g., "Core Infrastructure", "Premium Retainer"
  pricing_floor: decimal      # Minimum engagement price; must exceed any client budget hint
  scope_boundaries: str       # What is and is not included
  upsell_paths: list[str]     # Potential future expansions
  risk_warnings: list[str]    # Risks if client does not proceed
  approval_status: str        # "for_review" | "approved" | "sent"
  created_at: datetime
}
```

**Invariant**: `pricing_floor` MUST be calculated to exceed any client budget signal present in input. The agent prompt must explicitly enforce this.

#### Entity: Client Record

Historical relationship entry categorized by Client Reactivation Agent.

```
ClientRecord {
  contact_name: str
  history_summary: str
  category: str               # See allowed values below
  last_interaction_date: date
  suggested_next_action: str  # Optional; null for "do not chase"
  pricing_guard: bool         # True → no legacy pricing in any output
  reasoning_note: str         # Why agent assigned this category
}
```

**Allowed categories** (exactly six, no others):
1. `good_client_lost_touch`
2. `needs_boundaries`
3. `potential_upsell`
4. `legacy_underpriced`
5. `do_not_chase`
6. `strategic`

**Invariants**:
- Every record MUST be assigned exactly one category (FR-018/SC-009).
- If `category == "do_not_chase"` → `suggested_next_action` MUST be null.
- If `category == "legacy_underpriced"` → generated outreach MUST NOT reference any previous rate (FR-019).

#### Entity: Logo Asset (reference)

Not stored in nuwud-dev. Referenced by path.

```
LogoAsset {
  name: str          # e.g., "gorilla-light", "gorilla-dark", "gorilla-svg", "hologram"
  filename: str      # Actual filename under LOGO_DIR
  use_case: str      # "light_background" | "dark_apparel" | "embroidery" | "hologram"
  format: str        # "png" | "svg"
}
```

Canonical mapping:

| Name | Filename | Use Case |
|---|---|---|
| `gorilla-light` | `Nuwud-Gorilla-Logo-Fixed.png` | `light_background` (stickers, tote) |
| `gorilla-dark` | `Nuwud-Gorilla-Logo-Fixed-white.png` | `dark_apparel` |
| `gorilla-svg` | `Nuwud-Gorilla-Logo-Fixed.svg` | `embroidery` (Printful) |
| `hologram` | `Nuwud_Gorilla_3Inch_Hologram_Sticker.png` | `hologram` |

#### Entity: Agent Workflow

n8n workflow definition (stored as JSON).

```
AgentWorkflow {
  name: str                   # e.g., "revenue-scout"
  filename: str               # e.g., "n8n-workflows/revenue-scout.json"
  trigger: str                # "cron:2h" | "webhook" | "manual"
  inference_model: str        # "qwen3:30b-a3b"
  outputs: list[str]          # e.g., ["notion", "slack"]
  approval_gates: list[str]   # Nodes that require human approval before execution
}
```

---

### contracts/

This repo has no public external API surface (it is internal tooling). The contracts are **CLI invocation contracts** for all runnable scripts.

#### CLI Contract: `create_printify_product.py`

```
Usage:
  python scripts/create_printify_product.py --product <slug> [--logo-path <path>] [--dry-run]

Arguments:
  --product   Required. One of: sticker-3in | sticker-sheet | tote
  --logo-path Optional. Override default logo path from LOGO_DIR env var.
  --dry-run   Optional. Fetch variants and validate config but do not create product.

Exit codes:
  0  Product created and published successfully.
  1  Missing .env keys (lists all missing keys).
  2  Logo file not found at resolved path.
  3  Printify API error (prints HTTP status + response body).
  4  Publish-to-Shopify error.

Environment variables required:
  PRINTIFY_API_TOKEN, PRINTIFY_SHOP_ID, LOGO_DIR (or --logo-path)
```

#### CLI Contract: `create_printful_product.py`

```
Usage:
  python scripts/create_printful_product.py --style <style> [--logo-path <path>] [--dry-run]

Arguments:
  --style     Required. One of: snapback | dad-hat
  --logo-path Optional. Override SVG logo path from LOGO_DIR env var.
  --dry-run   Optional. Validate config but do not create product.

Exit codes:
  0  Product created and synced to Shopify successfully.
  1  Missing .env keys.
  2  SVG logo file not found.
  3  Printful API error.

Environment variables required:
  PRINTFUL_API_TOKEN, SHOPIFY_STORE_DOMAIN, LOGO_DIR (or --logo-path)
```

#### CLI Contract: `list_blueprints.py`

```
Usage:
  python scripts/list_blueprints.py [--provider <id>]

Arguments:
  --provider  Optional. Filter by print provider ID (default: 73).

Exit codes:
  0  Success (prints blueprint list as formatted table).
  1  Missing .env keys.
  3  Printify API error.

Environment variables required:
  PRINTIFY_API_TOKEN
```

---

### quickstart.md

#### Prerequisites

1. Python 3.11+ installed. Verify: `python --version`
2. Clone repo: `git clone https://github.com/nuwud/nuwud-dev.git && cd nuwud-dev`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in all values:

```powershell
Copy-Item .env.example .env
notepad .env
```

Required `.env` keys:
```
PRINTIFY_API_TOKEN=
PRINTIFY_SHOP_ID=26662299
PRINTFUL_API_TOKEN=
SHOPIFY_STORE_DOMAIN=31zh0s-4t.myshopify.com
LOGO_DIR=C:\Users\Nuwud\Projects\Nuwud Multimedia LLC\Nuwud Logos
NOTION_TOKEN=
```

#### Run a Printify Product

```powershell
# Die-cut sticker 3"
python scripts/create_printify_product.py --product sticker-3in

# Sticker sheet (4-up)
python scripts/create_printify_product.py --product sticker-sheet

# Tote bag
python scripts/create_printify_product.py --product tote

# Dry run (validates without creating)
python scripts/create_printify_product.py --product sticker-3in --dry-run
```

#### Run a Printful Product

```powershell
# Snapback hat (Yupoong 6089M)
python scripts/create_printful_product.py --style snapback

# Dad hat (Yupoong 6245CM)
python scripts/create_printful_product.py --style dad-hat
```

#### Import n8n Workflows

1. Open n8n at `https://nuwud.app.n8n.cloud` (or `http://localhost:5678` for local Docker).
2. Go to **Workflows → Import from file**.
3. Import each JSON from `n8n-workflows/`:
   - `revenue-scout.json` — lead scoring, runs every 2 hours
   - `offer-framing.json` — webhook-triggered offer document generator
   - `client-reactivation.json` — manual trigger, categorizes client records
4. Set workflow credentials (Notion, Slack, Ollama HTTP node) in n8n Credentials panel.
5. Activate each workflow.

---

## Project Structure

### Documentation (this feature)

```
.specify/features/nuwud-dev-core/
├── spec.md              # Source specification
├── plan.md              # This file
├── research.md          # (embedded in plan — Phase 0 above)
├── data-model.md        # (embedded in plan — Phase 1 above)
├── quickstart.md        # (embedded in plan — Phase 1 above)
├── contracts/           # (embedded in plan — Phase 1 above)
├── checklists/
│   └── requirements.md
└── tasks.md             # Generated by /speckit.tasks (NOT by /speckit.plan)
```

### Source Code (repository root)

```
nuwud-dev/
├── scripts/
│   ├── lib/
│   │   ├── printify.py            # Printify API helpers: upload_image, get_variants, create_product, publish
│   │   ├── printful.py            # Printful API helpers: create_sync_product
│   │   └── env.py                 # require_env(keys) — fail-fast .env validation
│   ├── create_printify_product.py # Pillar 1: CLI for Printify products
│   ├── create_printful_product.py # Pillar 1: CLI for Printful products
│   └── list_blueprints.py         # Utility: list available Printify blueprints
├── n8n-workflows/
│   ├── revenue-scout.json         # Pillar 3: 2-hour cron lead scoring
│   ├── offer-framing.json         # Pillar 3: webhook offer doc generator
│   └── client-reactivation.json   # Pillar 3: client categorization
├── assets/
│   └── README.md                  # Points to logo files at LOGO_DIR; no binaries in repo
├── .env.example                   # All required keys, no values
├── .gitignore                     # Must include .env, __pycache__, *.pyc
├── TOOLS.md                       # All documented commands (Pillar 2 lives here)
├── requirements.txt               # requests, python-dotenv
└── .specify/                      # SpecKit artifacts (this directory)
```

**Structure Decision**: Flat `scripts/` with shared `lib/` subpackage. Three n8n workflow JSON files at `n8n-workflows/`. No backend/frontend split — pure tooling repo.

---

## Implementation Sequence

Tasks are dependency-ordered. Full task list generated by `/speckit.tasks`.

### Milestone 1 — Foundation (blocking all else)

1. Create `.env.example` with all required keys
2. Create `.gitignore` (covers `.env`, `__pycache__`, `*.pyc`, `*.egg-info`)
3. Create `requirements.txt` (`requests>=2.31.0`, `python-dotenv>=1.0.0`)
4. Implement `scripts/lib/env.py` — `require_env()` helper
5. Implement `scripts/lib/printify.py` — upload, variants, create, publish
6. Update `TOOLS.md` with setup instructions

### Milestone 2 — Printify Automation (P1)

7. Implement `scripts/list_blueprints.py`
8. Implement `scripts/create_printify_product.py` — supports all three slugs
9. Validate: sticker-3in, sticker-sheet (4 placeholders), tote — all produce published Shopify products
10. Document in `TOOLS.md`

### Milestone 3 — Printful Automation (P2)

11. Implement `scripts/lib/printful.py`
12. Implement `scripts/create_printful_product.py` — snapback + dad-hat
13. Validate: hat products appear synced in Shopify admin
14. Document in `TOOLS.md`

### Milestone 4 — Agent Workflows (P3–P5)

15. Design Revenue Scout workflow in n8n (cron, Ollama HTTP, Notion write, Slack announce, Approval gate)
16. Export `n8n-workflows/revenue-scout.json`
17. Design Offer Framing workflow (webhook trigger, Ollama prompt, Notion write, Approval gate)
18. Export `n8n-workflows/offer-framing.json`
19. Design Client Reactivation workflow (manual trigger, Ollama categorization, Notion write)
20. Export `n8n-workflows/client-reactivation.json`

### Milestone 5 — Hydrogen Tooling (P6)

21. Document all Hydrogen commands in `TOOLS.md` (codegen, typecheck, build, dev)
22. Create `assets/README.md` documenting logo asset canonical paths

---

## Complexity Tracking

No constitution violations. No complexity justification required.

---

## Post-Plan Action

> **Dual Memory Sync Required (Constitution §VI)**  
> Summarize this plan to Notion page **"🛍️ Shopify + POD AI Workflow — Nuwud Training Guide"**  
> Page ID: `3501ef62-3177-81a0-a126-c2afdd5889ee`  
> 
> The plan agent does not write to Notion. This is a manual or next-step action:  
> Run the Notion sync workflow or use `openclaw agent --agent nuwud-dev --message "Sync nuwud-dev-core plan to Notion training guide page"` after this plan is committed.

---

## Acceptance Gate Summary

| Success Criterion | Verification Method |
|---|---|
| SC-001: Printify product < 90s | `time python scripts/create_printify_product.py --product sticker-3in` |
| SC-002: Printful hat synced < 120s | `time python scripts/create_printful_product.py --style snapback` |
| SC-003: Revenue Scout weekly Notion output | Trigger workflow manually; verify Notion entry |
| SC-004: Offer doc < 5 min | Submit test transcript; verify all 7 fields in output |
| SC-005: Zero unapproved client messages | Audit n8n execution log — every client-facing node preceded by Approval node |
| SC-006: Zero secrets in git | `git log --all -p | Select-String "TOKEN"` returns no matches |
| SC-007: All TOOLS.md scripts run cleanly | Follow TOOLS.md from fresh clone; all commands succeed |
| SC-008: Hydrogen typecheck + build pass | `npm run typecheck && npm run build` in MyStore — zero errors |
| SC-009: 100% client records categorized | Provide test records; every record has a valid category |
| SC-010: Workflows re-importable | Fresh n8n instance; import all 3 JSON files; all activate without error |
