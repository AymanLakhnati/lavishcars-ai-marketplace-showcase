"""Materialize the public review presentation from the sanitized tracked sources."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
destination = ROOT / "review-site/dist"
(destination / "assets").mkdir(parents=True, exist_ok=True)
for name in ("index.html", "style.css", "script.js"):
    shutil.copyfile(ROOT / "showcase/site" / name, destination / name)
for source, target in [
    ("apps/web/public/images/hero-concept.webp", "hero.webp"),
    ("showcase/poster.jpg", "poster.jpg"),
    ("showcase/LavishCars-Demo.mp4", "LavishCars-Demo.mp4"),
    ("showcase/captions.vtt", "captions.vtt"),
    ("showcase/TRANSCRIPT.md", "transcript.txt"),
    ("showcase/SHOWCASE_ROADMAP.md", "showcase-roadmap.txt"),
    ("output/showcase/LavishCars-Ayman-Lakhnati-Source.zip", "LavishCars-Source.zip"),
    ("docs/screenshots/home-desktop.png", "marketplace.png"),
    ("docs/screenshots/supplier-desktop.png", "supplier.png"),
    ("docs/screenshots/admin-desktop.png", "admin.png"),
    ("docs/screenshots/concierge-desktop.png", "concierge.png"),
]:
    shutil.copyfile(ROOT / source, destination / "assets" / target)
print("Prepared static review presentation in review-site/dist")
