<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`.specify/features/nuwud-dev-core/plan.md`
<!-- SPECKIT END -->

## Project: nuwud-dev — POD Automation & Shopify Hydrogen Tooling

**Owner:** Nuwud Multimedia LLC  
**GitHub:** https://github.com/nuwud/nuwud-dev  
**Purpose:** Automate Print-on-Demand product creation (Printify, Printful) and Shopify Hydrogen storefront tooling using a local AI stack (Ollama + OpenClaw).

---

### Store Info
- **Shopify store handle:** `31zh0s-4t`
- **Storefront URL (prod):** `31zh0s-4t.myshopify.com`
- **Dev storefront URL:** `nuwud-shop-0532438991d762b1a700.o2.myshopify.dev`
- **Shopify Hydrogen project:** `C:\Users\Nuwud\Projects\MyStore`
- **POD integrations:** Printify, Printful, Tapstitch

### Credentials
All secrets live in `.env` (gitignored). See `.env.example` for required keys.
- `PRINTIFY_API_TOKEN` + `PRINTIFY_SHOP_ID=26662299`
- `PRINTFUL_API_TOKEN`
- `SHOPIFY_STORE_DOMAIN`, `SHOPIFY_DEV_DOMAIN`

OpenClaw credential copies: `C:\Users\Nuwud\.openclaw\workspaces\nuwud-dev\`

### Logo Assets
Source at `C:\Users\Nuwud\Projects\Nuwud Multimedia LLC\Nuwud Logos\`
- `Nuwud-Gorilla-Logo-Fixed.png` — primary (light backgrounds, stickers, tote)
- `Nuwud-Gorilla-Logo-Fixed-white.png` — dark apparel / embroidery
- `Nuwud-Gorilla-Logo-Fixed.svg` — embroidery/vector
- `Nuwud_Gorilla_3Inch_Hologram_Sticker.png` — hologram sticker

### Printify API Quick Reference
Base URL: `https://api.printify.com/v1` — Bearer token auth.

| Endpoint | Use |
|---|---|
| `POST /v1/uploads/images.json` | Upload image (base64) |
| `GET /v1/catalog/blueprints/{bp}/print_providers/{p}/variants.json` | Get variants |
| `POST /v1/shops/{shop_id}/products.json` | Create product |
| `POST /v1/shops/{shop_id}/products/{id}/publish.json` | Push to Shopify |

**Blueprint IDs (provider 73 = Printed Simply):**

| Product | Blueprint | Placeholder(s) |
|---|---|---|
| Die-Cut Sticker 3" | `358` | `front` |
| Sticker Sheet | `661` | `front_1, front_2, front_3, front_4` ⚠️ NOT `front` |
| Tote Bag | `51` | `front` |

### Printful API Quick Reference
Base URL: `https://api.printful.com` — Bearer token auth.
Supports embroidered hats (Yupoong 6089M snapback, 6245CM dad hat) via API.

### Tapstitch
**No public API.** Manual wizard only via Shopify Apps → Tapstitch.
Target: Yupoong 6089M Snapback | $38 retail | SVG logo | 3D Puff embroidery.

### Local AI Stack
Ollama at `http://localhost:11434`

| Model | Best for |
|---|---|
| `qwen3:30b-a3b` | Code, API scripting (nuwud-dev default) |
| `qwen3:8b` | Fast fallback |
| `gemma4:26b` | Creative / writing |
| `deepseek-r1:14b` | Reasoning / planning |
| `patrick:latest` | Custom 19GB model |

OpenClaw agent invocation: `openclaw agent --agent nuwud-dev --message "..."`

### Dev Commands
- `npm run dev` — start Shopify Hydrogen dev server (MyStore project)
- `npm run build` — production build with codegen
- `npm run codegen` — regenerate Storefront API types
- `openclaw gateway stop` — stop gateway (Windows; it runs as a scheduled task)
- `openclaw gateway` — start gateway after stopping

### SpecKit Workflow
Use `/speckit.constitution` → `/speckit.specify` → `/speckit.plan` →
`/speckit.tasks` → `/speckit.implement` for all new features.

### Coding Standards
- TypeScript for all Hydrogen/Shopify work; Python for automation scripts
- Load `.env` via `python-dotenv` (Python) or `dotenv` (Node)
- Never hardcode secrets; never commit `.env`
- API calls: always use Bearer token from env, never inline credentials
- Scripts go in `scripts/` directory
