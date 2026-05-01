# TOOLS.md — nuwud-dev Agent Navigation Reference

> This file is the authoritative self-navigation guide for AI coding agents
> working in this repository. Keep it up to date whenever tooling, credentials
> paths, or blueprints change.

**Purpose:** POD (Print-on-Demand) automation + Shopify Hydrogen store tooling for Nuwud Multimedia LLC.

---

## 1. Repository Layout

```
nuwud-dev/
├── .env.example          ← credential template (safe to commit)
├── .env                  ← real secrets (gitignored — NEVER commit)
├── .gitignore
├── .github/
│   ├── copilot-instructions.md   ← Copilot system instructions
│   ├── agents/                   ← spec-kit agent mode files
│   └── prompts/                  ← spec-kit slash-command prompts
├── .specify/
│   ├── memory/constitution.md    ← project governing principles
│   ├── templates/                ← spec / plan / task templates
│   ├── extensions/               ← installed specify extensions
│   └── workflows/                ← specify workflow definitions
├── .vscode/settings.json         ← workspace editor settings
├── nuwud-dev.code-workspace      ← VS Code multi-root workspace file
├── scripts/                      ← automation scripts (Printify, Printful, Shopify)
└── TOOLS.md                      ← this file
```

---

## 2. Credentials

All secrets live in `.env` (gitignored). Load with `python-dotenv` or `dotenv` in Node.

| Key | Service | Notes |
|---|---|---|
| `PRINTIFY_API_TOKEN` | Printify REST API | JWT, stored in nuwud-dev workspace |
| `PRINTIFY_SHOP_ID` | Printify | `26662299` |
| `PRINTFUL_API_TOKEN` | Printful REST API | 51-char token |
| `SHOPIFY_STORE_DOMAIN` | Shopify prod | `31zh0s-4t.myshopify.com` |
| `SHOPIFY_DEV_DOMAIN` | Shopify dev | `nuwud-shop-0532438991d762b1a700.o2.myshopify.dev` |

OpenClaw copies: `C:\Users\Nuwud\.openclaw\workspaces\nuwud-dev\printify-credentials.json` and `printful-credentials.json`

---

## 3. Logo Assets

All source files at: `C:\Users\Nuwud\Projects\Nuwud Multimedia LLC\Nuwud Logos\`

| File | Use |
|---|---|
| `Nuwud-Gorilla-Logo-Fixed-white.png` | Dark apparel (DTG/embroidery) |
| `Nuwud-Gorilla-Logo-Fixed.png` (958KB) | Light products, stickers, tote |
| `Nuwud-Gorilla-Logo-Fixed.svg` | Embroidery conversion |
| `Nuwud_Gorilla_3Inch_Hologram_Sticker.png` | Hologram sticker product |

---

## 4. Printify API Quick Reference

Base URL: `https://api.printify.com/v1` — Bearer token auth.

```
POST /v1/uploads/images.json          ← upload image (base64)
GET  /v1/catalog/blueprints/{bp}/print_providers/{p}/variants.json
POST /v1/shops/{shop_id}/products.json ← create product
POST /v1/shops/{shop_id}/products/{id}/publish.json ← push to Shopify
```

**Blueprint IDs (provider 73 = Printed Simply):**

| Product | Blueprint | Placeholder(s) |
|---|---|---|
| Die-Cut Sticker 3" | `358` | `front` |
| Sticker Sheet | `661` | `front_1, front_2, front_3, front_4` ⚠️ NOT `front` |
| Tote Bag | `51` | `front` |
| AOP Hoodie | confirm via catalog | `front`, `back` |

---

## 5. Printful API Quick Reference

Base URL: `https://api.printful.com` — Bearer token auth.
Embroidered hats (Yupoong 6089M snapback, 6245CM dad hat) are supported via API.

---

## 6. Tapstitch

**No API.** Manual wizard only via Shopify Apps → Tapstitch.
Target: Yupoong 6089M Snapback | $38 retail | SVG | 3D Puff (when available).

---

## 7. Shopify Hydrogen Store

Project: `C:\Users\Nuwud\Projects\MyStore`
Dev server: `npm run dev` (port 3000/4000)
Codegen: `npm run codegen`

---

## 8. Local AI Stack

Ollama at `http://localhost:11434`

| Model | Best for |
|---|---|
| `qwen3:30b-a3b` | Code, API tasks (nuwud-dev default) |
| `qwen3:8b` | Fast fallback |
| `gemma4:26b` | Creative/writing |
| `deepseek-r1:14b` | Reasoning/planning |
| `patrick:latest` | Custom 19GB model |

---

## 2. Spec-Kit (Specify CLI) — Slash Commands

Spec-Driven Development workflow. Run these inside GitHub Copilot Chat or
any supported agent:

| Command | Purpose |
|---|---|
| `/speckit.constitution` | Create / update project governing principles |
| `/speckit.specify` | Define what to build (requirements + user stories) |
| `/speckit.clarify` | Clarify ambiguous areas before planning |
| `/speckit.plan` | Create technical implementation plan |
| `/speckit.analyze` | Cross-artifact consistency report |
| `/speckit.checklist` | Generate quality checklists |
| `/speckit.tasks` | Generate actionable task list |
| `/speckit.implement` | Execute tasks and build the feature |
| `/speckit.taskstoissues` | Push tasks to GitHub Issues |

**Agent files**: `.github/agents/speckit.*.agent.md`  
**Prompt files**: `.github/prompts/speckit.*.prompt.md`  
**Constitution**: `.specify/memory/constitution.md`  
**CLI docs**: https://github.github.io/spec-kit/reference/overview.html

### Upgrade Specify CLI
```powershell
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

---

## 3. Credential Paths

### 3.1 Active secrets file
```
c:\Users\Nuwud\Projects\nuwud-dev\.env
```
- Copy `.env.example` → `.env` and fill in values.  
- `.env` is **gitignored** — never committed.

### 3.2 Template (safe reference)
```
c:\Users\Nuwud\Projects\nuwud-dev\.env.example
```

### 3.3 Key categories in `.env`

| Variable prefix | Service |
|---|---|
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic / Claude |
| `GITHUB_COPILOT_TOKEN` | GitHub Copilot |
| `GITHUB_TOKEN` | GitHub REST/GraphQL API |
| `AZURE_*` | Azure cloud services |
| `DATABASE_URL` | Primary database |
| `STRIPE_*` | Payments |
| `SENDGRID_API_KEY` | Email |
| `NOTION_TOKEN` | Notion API |

> Agents: load credentials from process environment — never hardcode keys
> or print them to stdout/logs.

---

## 4. Blueprint Reference

### 4.1 Spec-Kit workflow blueprint

```
1. /speckit.constitution   → .specify/memory/constitution.md
2. /speckit.specify        → .specify/features/<name>/spec.md
3. /speckit.clarify        → (clarification notes, optional)
4. /speckit.plan           → .specify/features/<name>/plan.md
5. /speckit.analyze        → (consistency report, optional)
6. /speckit.tasks          → .specify/features/<name>/tasks.md
7. /speckit.implement      → implementation code
8. /speckit.taskstoissues  → GitHub Issues (optional)
```

### 4.2 Git extension commands

| Command | Purpose |
|---|---|
| `/speckit.git.initialize` | Initialize repo + remote |
| `/speckit.git.feature` | Create feature branch |
| `/speckit.git.commit` | Smart commit from spec artifacts |
| `/speckit.git.validate` | Validate repo state |
| `/speckit.git.remote` | Configure / push remote |

**Git scripts**: `.specify/extensions/git/scripts/powershell/`

---

## 5. Development Prerequisites

| Tool | Required version | Install |
|---|---|---|
| Python | 3.11+ | https://python.org |
| uv | latest | `pip install uv` |
| Git | 2.x | https://git-scm.com |
| GitHub CLI (`gh`) | 2.x | https://cli.github.com |
| Specify CLI | 0.8.x | see §2 above |
| Node.js | 20+ LTS | https://nodejs.org (if JS work needed) |

---

## 6. GitHub Repository

- **Repo**: https://github.com/Nuwud/nuwud-dev  
- **Default branch**: `main`  
- **Remote alias**: `origin`

---

## 8. POD Automation — Printify

Scripts live in `scripts/`. Run all commands from the **project root** (`C:\Users\Nuwud\Projects\nuwud-dev`).

### Prerequisites

1. Python 3.11+ installed and on PATH.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Copy `.env.example` → `.env` and fill in:
   - `PRINTIFY_API_TOKEN` — your Printify Bearer token
   - `PRINTIFY_SHOP_ID` — `26662299` (your Printify shop)
   - `LOGO_DIR` — path to your logo directory, e.g. `C:\Users\Nuwud\Projects\Nuwud Multimedia LLC\Nuwud Logos\`

### List Available Blueprints

```powershell
python scripts/list_blueprints.py
python scripts/list_blueprints.py --provider 73
```

- Requires: `PRINTIFY_API_TOKEN`
- Exit codes: `0` (success), `1` (missing env), `3` (API error)

### Create and Publish Printify Products

**Die-Cut Sticker 3"** (blueprint 358, placeholder `front`):
```powershell
python scripts/create_printify_product.py --product sticker-3in
```

**Sticker Sheet** (blueprint 661, placeholders `front_1`…`front_4`):
```powershell
python scripts/create_printify_product.py --product sticker-sheet
```

**Tote Bag** (blueprint 51, placeholder `front`):
```powershell
python scripts/create_printify_product.py --product tote
```

### --dry-run Mode

Validates env vars, confirms logo file exists, prints resolved config. **No API calls made.** Exits `0` if everything is valid.

```powershell
python scripts/create_printify_product.py --product sticker-3in --dry-run
python scripts/create_printify_product.py --product sticker-sheet --dry-run
python scripts/create_printify_product.py --product tote --dry-run
```

### Override Logo Path

```powershell
python scripts/create_printify_product.py --product sticker-3in --logo-path "C:\path\to\my-logo.png"
```

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success — product published to Shopify (or `--dry-run` validated OK) |
| `1` | Missing required environment variables (full list printed) |
| `2` | Logo file not found at resolved path |
| `3` | Printify API error (status + response body printed) |

---

## 7. Agent Self-Navigation Checklist

When starting work in this repo, an agent should:

1. Read `.github/copilot-instructions.md` for project-level instructions.
2. Read `.specify/memory/constitution.md` for governing principles.
3. Check `.env.example` to know which environment variables are expected.
4. Identify the active feature under `.specify/features/` (if any).
5. Follow the spec-kit workflow blueprint in §4.1 above.
6. Never read, log, or expose values from `.env`.
