# Logo Assets — Nuwud Multimedia LLC

This directory is intentionally empty. Logo assets are **not** committed to version control
(Constitution §II — no binary assets in VCS).

## Canonical Asset Location

All Nuwud Multimedia logo files live at the path stored in the `LOGO_DIR` environment variable.

**Default path:** `C:\Users\Nuwud\Projects\Nuwud Multimedia LLC\Nuwud Logos\`

Set `LOGO_DIR` in your `.env` file (see `.env.example`).

---

## Canonical Logo Files

| Filename | Use Case |
|---|---|
| `Nuwud-Gorilla-Logo-Fixed.png` | Light backgrounds, stickers, tote bag |
| `Nuwud-Gorilla-Logo-Fixed-white.png` | Dark apparel (DTG/embroidery) |
| `Nuwud-Gorilla-Logo-Fixed.svg` | Embroidery / vector conversion |
| `Nuwud_Gorilla_3Inch_Hologram_Sticker.png` | Hologram sticker product |

---

## Usage in Scripts

Scripts resolve the logo path using the `LOGO_DIR` env var plus the product-specific filename:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logo_dir = Path(os.environ["LOGO_DIR"])
logo_path = logo_dir / "Nuwud-Gorilla-Logo-Fixed.png"
```

Override the logo path at runtime with `--logo-path`:

```
python scripts/create_printify_product.py --product sticker-3in --logo-path "C:\path\to\logo.png"
```
