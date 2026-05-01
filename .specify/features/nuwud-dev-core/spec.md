# Feature Specification: nuwud-dev Core Operations Platform

**Feature Branch**: `main` (core infrastructure — not a feature branch)
**Created**: 2026-05-01
**Status**: Draft
**Owner**: Patrick Wood, Nuwud Multimedia LLC

---

## Overview

nuwud-dev is the internal automation and tooling codebase for Nuwud Multimedia LLC. It is **not** a client project — it is the internal operating infrastructure. The platform delivers three capability pillars:

1. **POD Automation** — End-to-end product creation and publishing to Shopify via Printify and Printful
2. **Shopify Hydrogen Storefront Tooling** — Developer scripts and tooling supporting the Nuwud Hydrogen storefront
3. **Internal Agent Automation** — A compact AI agent crew (n8n + Ollama) for revenue scouting, offer framing, and client reactivation

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Printify Product Creation (Priority: P1)

Patrick runs a single command that uploads the correct logo asset, fetches all available variants, creates a fully configured product, and publishes it to the Shopify store — without visiting any browser or admin panel.

**Why this priority**: Printify is the primary POD revenue channel (stickers, sheets, totes). Automation eliminates hours of manual product setup per SKU and enables bulk launches.

**Independent Test**: Can be fully tested by running `python scripts/create_printify_product.py --product sticker-3in` and verifying the product appears published in the Shopify admin with correct title, variants, and logo image.

**Acceptance Scenarios**:

1. **Given** valid Printify API credentials and a local logo asset, **When** the script is run for blueprint 358 (Die-Cut Sticker 3"), **Then** the product is created with all available variants from provider 73 and published to Shopify within 60 seconds.
2. **Given** the Sticker Sheet blueprint (661), **When** the script is run, **Then** all four placeholders (`front_1`, `front_2`, `front_3`, `front_4`) are populated and the product is published.
3. **Given** the Tote Bag blueprint (51), **When** the script is run, **Then** the front placeholder uses the light-background logo and the product is published.
4. **Given** an invalid API token, **When** the script is run, **Then** it exits with a descriptive error message and no partial product is left in Printify.

---

### User Story 2 — Printful Embroidery Product Creation (Priority: P2)

Patrick runs a script that creates an embroidered hat product (3D Puff) in Printful using the SVG logo, targeting both the Yupoong 6089M snapback and the Yupoong 6245CM dad hat, and syncs the result to Shopify.

**Why this priority**: Embroidered apparel is a premium-margin product category. Scripting this removes manual Printful dashboard work for each hat style.

**Independent Test**: Run `python scripts/create_printful_product.py --style snapback` and verify a Printful sync item appears in the Shopify admin with the correct hat variant and embroidery design.

**Acceptance Scenarios**:

1. **Given** a valid Printful API token and the SVG logo file, **When** the snapback script runs, **Then** a Yupoong 6089M product with 3D Puff embroidery is created and synced to Shopify.
2. **Given** a valid Printful API token, **When** the dad hat script runs, **Then** a Yupoong 6245CM product with 3D Puff embroidery is created and synced to Shopify.
3. **Given** the SVG logo is missing from the expected path, **When** the script runs, **Then** it exits with a clear error identifying the missing asset.

---

### User Story 3 — Revenue Scout Agent (Priority: P3)

Every two hours (and on demand), an n8n workflow powered by a local Ollama model scans lead sources, scores each opportunity, and produces a weekly ranked Revenue Leak Lead List delivered to Patrick via Slack — requiring zero manual input from Patrick.

**Why this priority**: This directly drives new business acquisition. A weekly prioritized list means Patrick only engages where there is the highest probability of return.

**Independent Test**: Trigger the n8n workflow manually and verify a ranked lead list appears in the Slack notification channel within 10 minutes, containing at least one scored and categorized lead.

**Acceptance Scenarios**:

1. **Given** lead source data (imported lists or scraped records), **When** the workflow runs on its 2-hour cron, **Then** each lead is scored and a ranked list is stored in Notion and announced in Slack.
2. **Given** a new lead is identified as a weak Shopify store, **When** the local AI scores it, **Then** the output includes: business name, opportunity type, revenue leak diagnosis, and a proposed outreach angle awaiting Patrick's approval.
3. **Given** Patrick has not approved any outreach messages, **When** the workflow runs, **Then** no emails, DMs, or messages are sent — only internal records are written.
4. **Given** the Ollama model is offline, **When** the workflow runs, **Then** it fails gracefully with a Slack error notification and retries on the next cron cycle.

---

### User Story 4 — Offer Framing Agent (Priority: P4)

Patrick pastes raw client notes, call transcript snippets, or website findings into an n8n form or Slack command, and the agent returns a structured premium offer document: problem summary, revenue leak diagnosis, offer tier, pricing floor, scope boundaries, upsell paths, and risk warnings.

**Why this priority**: Prevents underpricing by reframing client work as infrastructure investment. This protects revenue on every engagement before a proposal is written.

**Independent Test**: Submit a sample client transcript via the n8n webhook endpoint and verify a structured offer document is returned to Slack/Notion with all required fields populated.

**Acceptance Scenarios**:

1. **Given** raw client notes submitted via the agent input channel, **When** the Offer Framing Agent processes them, **Then** the output includes problem summary, pricing floor, offer tier, scope boundaries, upsell paths, and risk warnings.
2. **Given** a client budget hint is present in the notes, **When** the agent processes the input, **Then** the pricing floor is calculated above that budget rather than anchored to it.
3. **Given** any client communication is included in the output, **When** the document is produced, **Then** it is marked "For Review" and requires Patrick's explicit approval before being sent to the client.

---

### User Story 5 — Client Reactivation Agent (Priority: P5)

The agent mines Patrick's historical client records and categorizes each relationship (good client lost touch / needs boundaries / potential upsell / legacy underpriced / do not chase / strategic), enabling targeted re-engagement without resurrecting legacy pricing.

**Why this priority**: Dormant relationships are a low-cost revenue opportunity. Proper categorization prevents underpriced re-engagement.

**Independent Test**: Provide the agent with a sample set of historical client records and verify each is categorized into one of the six defined categories and stored in Notion.

**Acceptance Scenarios**:

1. **Given** a set of historical client records in Notion, **When** the agent runs, **Then** each record is assigned one of the six categories with a reasoning note.
2. **Given** a record categorized as "legacy underpriced," **When** outreach is suggested, **Then** the suggested messaging does not reference any previous rate and frames the engagement at current pricing.
3. **Given** a record categorized as "do not chase," **When** the agent runs, **Then** no outreach is suggested or queued for that contact.

---

### User Story 6 — Shopify Hydrogen Storefront Tooling (Priority: P6)

Patrick and future contributors use documented scripts to develop, typecheck, build, and codegen the Hydrogen storefront without needing to memorize commands or look up documentation.

**Why this priority**: Storefront stability is required for all POD products to be purchasable. Developer tooling reduces friction and prevents deploy regressions.

**Independent Test**: A contributor with a fresh clone follows TOOLS.md to run `npm run typecheck` and `npm run build` successfully without external guidance.

**Acceptance Scenarios**:

1. **Given** any GraphQL schema change, **When** `npm run codegen` is run, **Then** updated TypeScript types are generated without errors.
2. **Given** a code change, **When** `npm run typecheck` is run, **Then** TypeScript errors are surfaced before any deploy attempt.
3. **Given** a production deploy, **When** `npm run build` succeeds, **Then** the build artifact is deployable to Shopify Oxygen without additional manual steps.

---

### Edge Cases

- What happens when a Printify blueprint's variants list changes between runs? The script must fetch fresh variants each time rather than caching stale data.
- How does the system handle Printify image upload failures (network timeout, oversized file)? The script must retry once and exit with a clear error, not silently proceed with a missing image.
- What if the Ollama model returns a malformed or empty scoring response? The agent must flag the lead as "unscored" and continue processing remaining leads rather than failing the whole batch.
- What if an n8n workflow attempts to send a client-facing message without approval? The action must be blocked at the workflow level — no bypass path should exist.
- What happens when `.env` is missing a required key at script startup? Scripts must fail fast with a list of all missing keys before making any API calls.
- Tapstitch has no API and is explicitly out of scope for automation. Any future attempt to automate Tapstitch must be treated as a new feature, not a bug fix.

---

## Requirements *(mandatory)*

### Functional Requirements

**POD Automation — Printify**

- **FR-001**: Scripts MUST accept a product type argument and automatically select the correct blueprint ID, print provider, placeholder names, and logo asset.
- **FR-002**: Scripts MUST upload the logo image via base64 encoding before creating any product.
- **FR-003**: Scripts MUST fetch current variant lists from the Printify catalog API on each run; no hardcoded variant IDs.
- **FR-004**: Scripts MUST create the product and immediately publish it to Shopify in a single invocation.
- **FR-005**: Scripts MUST load all credentials from `.env` and fail fast if any required key is absent.
- **FR-006**: Scripts MUST NOT commit any credentials, tokens, or secret values to the repository.

**POD Automation — Printful**

- **FR-007**: Scripts MUST create embroidery products for both the Yupoong 6089M snapback and Yupoong 6245CM dad hat styles.
- **FR-008**: Scripts MUST use the SVG logo asset for all Printful embroidery submissions.
- **FR-009**: Scripts MUST sync the created Printful product to the Shopify store.

**Shopify Hydrogen Storefront**

- **FR-010**: All TypeScript changes MUST pass `npm run typecheck` before a deploy is attempted.
- **FR-011**: Any GraphQL schema change MUST be followed by `npm run codegen` to regenerate types.
- **FR-012**: All scripts and commands MUST be documented in `TOOLS.md` with usage examples.

**Internal Agent Automation**

- **FR-013**: All agents MUST use local Ollama inference (qwen3:30b-a3b default) for reasoning and scoring; cloud APIs are permitted only for action/integration tasks (sending, syncing, storing).
- **FR-014**: Agents MUST fire on a 2-hour cron schedule and announce actionable results to Slack.
- **FR-015**: Any action that sends a message, creates a commitment, modifies pricing, or touches a client relationship MUST require explicit human approval before execution.
- **FR-016**: Revenue Scout Agent MUST output a ranked lead list to Notion weekly, each lead containing: business name, opportunity type, revenue leak diagnosis, and a proposed outreach angle.
- **FR-017**: Offer Framing Agent MUST produce documents containing: problem summary, revenue leak diagnosis, offer tier, pricing floor, scope boundaries, upsell paths, and risk warnings.
- **FR-018**: Client Reactivation Agent MUST categorize each historical client record into exactly one of these six categories: good client lost touch / needs boundaries / potential upsell / legacy underpriced / do not chase / strategic.
- **FR-019**: Client Reactivation Agent MUST NOT include legacy pricing in any generated outreach suggestion.
- **FR-020**: All agent workflows MUST be version-controlled (n8n export JSON stored in repository).

**General**

- **FR-021**: All Python scripts MUST reside in the `scripts/` directory and be runnable from the project root.
- **FR-022**: All Python scripts MUST use `python-dotenv` to load environment variables.
- **FR-023**: The `.env` file MUST never be committed; `.env.example` MUST be maintained with all required keys listed (no values).

### Key Entities

- **Product**: A POD item (sticker, tote, hat) defined by blueprint ID, print provider, placeholders, logo asset, and Shopify publish target.
- **Lead**: A business opportunity record with fields: business name, opportunity type, revenue leak diagnosis, score, proposed outreach, approval status.
- **Offer**: A structured proposal document with fields: problem summary, revenue leak diagnosis, offer tier, pricing floor, scope boundaries, upsell paths, risk warnings, approval status.
- **Client Record**: A historical relationship entry with fields: contact name, history summary, category, last interaction date, suggested next action, pricing guard flag.
- **Logo Asset**: A versioned image file (PNG/SVG) used as the print design, with a designated use case (light background, dark apparel, embroidery, hologram).
- **Agent Workflow**: An n8n workflow JSON defining trigger (cron or webhook), processing steps, Ollama inference calls, Notion/Slack integration, and approval gates.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single command creates and publishes a fully configured Printify product (any supported type) to Shopify in under 90 seconds.
- **SC-002**: A single command creates and syncs a Printful embroidered hat product to Shopify in under 120 seconds.
- **SC-003**: The Revenue Scout Agent produces a ranked lead list in Notion every week without any manual input from Patrick.
- **SC-004**: The Offer Framing Agent converts raw client notes into a structured offer document with all seven required fields populated within 5 minutes of submission.
- **SC-005**: Zero client-facing messages, sales outreach, or commitments are sent without Patrick's explicit approval — verified by workflow audit log.
- **SC-006**: Zero secrets or credential values appear in any git commit, verified by `.gitignore` coverage and a pre-commit check.
- **SC-007**: Every script listed in `TOOLS.md` runs successfully from the `scripts/` directory with only the setup steps described in that file.
- **SC-008**: All Hydrogen TypeScript changes pass `npm run typecheck` and `npm run build` with zero errors before any Oxygen deploy.
- **SC-009**: The Client Reactivation Agent categorizes 100% of provided historical client records into one of the six defined categories.
- **SC-010**: All agent workflow definitions are stored as versioned JSON files in the repository and can be re-imported to a fresh n8n instance.

---

## Assumptions

- All Printify products use print provider 73 (Printed Simply) unless a specific product type requires otherwise.
- Tapstitch is explicitly out of scope for automation due to the absence of a public API; Tapstitch products will continue to be created manually via the Shopify Apps wizard.
- The Ollama instance runs locally at `http://localhost:11434` and is expected to be running before any agent workflow or AI-dependent script executes.
- n8n runs locally via Docker on port 5678 for development; the cloud instance at `nuwud.app.n8n.cloud` is the production agent host.
- Human approval gates for agents are implemented at the n8n workflow level (e.g., a wait-for-webhook node); there is no separate approval application to build.
- The Hydrogen storefront at `C:\Users\Nuwud\Projects\MyStore` is managed as a separate repository; this repo only contains tooling scripts and documentation that support it.
- All scripts are written in Python with `python-dotenv` and `requests`; no new language runtimes are introduced for scripting.
- Logo assets are treated as static source files at their documented local paths; asset management and versioning is out of scope.
- The `.env.example` file is the single source of truth for required environment variable names.
- Agent cron schedules fire every 2 hours; schedule adjustments are configuration changes, not feature changes.
- Qdrant (port 6333) and PostgreSQL (port 5432) are available as infrastructure but their schema design is deferred to the planning phase for each agent that requires them.
