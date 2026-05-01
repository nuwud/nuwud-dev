# nuwud-dev Constitution

## Core Principles

### I. Automation-First
Every repeatable POD or Shopify task must be scriptable. If a workflow requires more than 3 manual steps, write a script for it. Scripts live in `scripts/` and are documented in `TOOLS.md`. Tapstitch (no API) is the only sanctioned exception.

### II. Secrets Stay Local
No API tokens, JWTs, or credentials ever enter version control. All secrets load from `.env` (gitignored) using `python-dotenv` (Python) or `dotenv` (Node). `.env.example` is always kept in sync with required keys. OpenClaw workspace copies at `C:\Users\Nuwud\.openclaw\workspaces\nuwud-dev\` are the source of truth for credentials.

### III. Local AI by Default
Ollama (`qwen3:30b-a3b`) is the primary inference engine. Cloud LLM APIs (Anthropic, OpenAI) are fallbacks only — never the first call. All agent tasks route through OpenClaw (`openclaw agent --agent nuwud-dev`). Remote APIs cost money; local models do not.

### IV. Script Portability (Windows-First)
All shell commands must work in PowerShell on Windows. Avoid Linux-only tools (`fuser`, `lsof`, etc.) in scripts or documentation. Use `taskkill /PID <pid> /F` for port management. Use `python` (not `python3`) unless the environment requires it.

### V. Shopify Hydrogen Standards
TypeScript only for Hydrogen/Storefront work. Use React Router v7 patterns. Regenerate types with `npm run codegen` after any GraphQL change. Never deploy to Oxygen without a clean `npm run typecheck` and `npm run build`.

**Boundary:** The Hydrogen storefront lives at `C:\Users\Nuwud\Projects\MyStore\` in its own VS Code window. nuwud-dev does NOT contain storefront source — it contains scripts and tooling that *target* that store via API or CLI. Never copy storefront files into nuwud-dev.

### VI. Dual Memory — Local + Notion
All significant decisions, specs, plans, tasks, and agent outputs are written to both:
1. The local `.specify/` directory (git-tracked source of truth)
2. The Nuwud Notion workspace (human-readable command layer for Patrick)

Notion is updated whenever a spec, plan, or task list is created or amended. The Notion page "🛍️ Shopify + POD AI Workflow — Nuwud Training Guide" is the canonical agent training reference.

### VII. Simplicity (YAGNI)
Don't build what isn't needed yet. Scripts solve one product type at a time. No shared infrastructure for one-time operations. Abstractions require at least 3 use cases before being extracted.

## Technology Stack

| Layer | Technology |
|---|---|
| Storefront | Shopify Hydrogen, React Router v7, TypeScript, Tailwind CSS v4 |
| POD APIs | Printify REST, Printful REST |
| AI / Inference | Ollama (local), OpenClaw gateway (port 3100) |
| Primary model | `qwen3:30b-a3b` via Ollama |
| Automation scripts | Python (with `python-dotenv`, `requests`) |
| Package manager | npm (Hydrogen), pip (Python scripts) |
| Hosting | Shopify Oxygen (edge) |

## Development Workflow

1. **Spec** — run `/speckit.specify` to define what to build
2. **Plan** — run `/speckit.plan` to generate design artifacts
3. **Tasks** — run `/speckit.tasks` to create dependency-ordered task list
4. **Implement** — run `/speckit.implement` or delegate to nuwud-dev agent
5. **Verify** — `npm run typecheck` + `npm run build` for Hydrogen; test scripts against Printify/Printful sandbox where available
6. **Commit** — conventional commits (`feat:`, `fix:`, `chore:`); no force-push to `main`

### POD Product Creation Checklist
- [ ] Image uploaded via Printify `/uploads/images.json` (base64)
- [ ] Correct blueprint + provider + placeholder IDs confirmed
- [ ] Variants fetched and at least one variant selected
- [ ] Product created via `POST /shops/{id}/products.json`
- [ ] Product published to Shopify via `publish.json`
- [ ] Verify product appears in Shopify Admin

## Governance

This constitution supersedes all other project practices. Amendments require updating this file and syncing `TOOLS.md` and `.github/copilot-instructions.md`. No production Shopify deployment without owner (Nuwud) approval. All agent tool calls that delete or publish are gated — confirm before irreversible actions.

Runtime development guidance lives in `TOOLS.md`.

**Version**: 1.0.0 | **Ratified**: 2026-05-01 | **Last Amended**: 2026-05-01
