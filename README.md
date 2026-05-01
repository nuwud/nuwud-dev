# nuwud-dev

**POD Automation & Shopify Hydrogen Tooling** for [Nuwud Multimedia LLC](https://31zh0s-4t.myshopify.com)

This is the working repository for the `nuwud-dev` OpenClaw agent — automating Print-on-Demand product creation (Printify, Printful) and Shopify Hydrogen storefront tooling using a local AI stack.

---

## What This Does

- Creates and publishes Printify products (stickers, tote bags, apparel) via REST API
- Manages Printful embroidered hat products via REST API
- Supports Shopify Hydrogen storefront development at `C:\Users\Nuwud\Projects\MyStore`
- Runs autonomously via [OpenClaw](https://openclaw.dev) using local Ollama models (no cloud API required)

---

## Store

| | |
|---|---|
| Production | `31zh0s-4t.myshopify.com` |
| Dev | `nuwud-shop-0532438991d762b1a700.o2.myshopify.dev` |
| Hydrogen project | `C:\Users\Nuwud\Projects\MyStore` |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/nuwud/nuwud-dev.git
cd nuwud-dev
```

No npm dependencies yet — scripts are Python-based.

### 2. Configure credentials

```bash
cp .env.example .env
# Fill in your Printify, Printful, and Shopify tokens
```

Required keys (see `.env.example` for full list):

| Key | Source |
|---|---|
| `PRINTIFY_API_TOKEN` | Printify → My Account → Connections |
| `PRINTIFY_SHOP_ID` | `26662299` |
| `PRINTFUL_API_TOKEN` | Printful → Dashboard → API |
| `SHOPIFY_STORE_DOMAIN` | `31zh0s-4t.myshopify.com` |

### 3. Run the nuwud-dev agent

```powershell
openclaw agent --agent nuwud-dev --message "Create a die-cut sticker product on Printify"
```

---

## POD Blueprints (Printify, provider 73 — Printed Simply)

| Product | Blueprint ID | Placeholder(s) |
|---|---|---|
| Die-Cut Sticker 3" | `358` | `front` |
| Sticker Sheet | `661` | `front_1`, `front_2`, `front_3`, `front_4` |
| Tote Bag | `51` | `front` |

> ⚠️ Sticker Sheet uses `front_1`–`front_4`, **not** `front`.

---

## Scripts

Automation scripts live in `scripts/`. Each script loads credentials from `.env` via `python-dotenv`.

| Script | Purpose |
|---|---|
| *(coming soon)* | Printify product creation |
| *(coming soon)* | Printful hat product creation |

---

## Logo Assets

Source files at `C:\Users\Nuwud\Projects\Nuwud Multimedia LLC\Nuwud Logos\`

| File | Use |
|---|---|
| `Nuwud-Gorilla-Logo-Fixed.png` | Light backgrounds, stickers, tote |
| `Nuwud-Gorilla-Logo-Fixed-white.png` | Dark apparel, embroidery |
| `Nuwud-Gorilla-Logo-Fixed.svg` | Embroidery / vector |
| `Nuwud_Gorilla_3Inch_Hologram_Sticker.png` | Hologram sticker product |

---

## Local AI Stack

Ollama at `http://localhost:11434`

| Model | Role |
|---|---|
| `qwen3:30b-a3b` | nuwud-dev default (code + API tasks) |
| `qwen3:8b` | Fast fallback |
| `gemma4:26b` | Creative / writing |
| `deepseek-r1:14b` | Reasoning / planning |

---

## Gateway (Windows)

```powershell
# If port 3100 is stuck:
netstat -ano | findstr :3100   # note the PID
taskkill /PID <pid> /F
openclaw gateway
```

---

## Development Workflow (SpecKit)

```
/speckit.specify   → define what to build
/speckit.plan      → generate design artifacts
/speckit.tasks     → create task list
/speckit.implement → execute tasks
```

See `.specify/memory/constitution.md` for governing principles.
