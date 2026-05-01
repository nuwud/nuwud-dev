# TOOLS.md — nuwud-dev Agent Navigation Reference

> This file is the authoritative self-navigation guide for AI coding agents
> working in this repository. Keep it up to date whenever tooling, credentials
> paths, or blueprints change.

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
└── TOOLS.md                      ← this file
```

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

## 7. Agent Self-Navigation Checklist

When starting work in this repo, an agent should:

1. Read `.github/copilot-instructions.md` for project-level instructions.
2. Read `.specify/memory/constitution.md` for governing principles.
3. Check `.env.example` to know which environment variables are expected.
4. Identify the active feature under `.specify/features/` (if any).
5. Follow the spec-kit workflow blueprint in §4.1 above.
6. Never read, log, or expose values from `.env`.
