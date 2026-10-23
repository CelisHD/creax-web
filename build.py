#!/usr/bin/env python3
"""Genera el sitio estático de Creax.

Lee el contenido de content/*.json, las plantillas de templates/ y los
archivos de assets/, y escribe el sitio listo para subir en dist/.

Uso:
    python3 build.py            # genera dist/
    python3 build.py --preview  # genera preview/ (versión para vista previa en Claude)
    python3 build.py --staging  # genera dist/ para revisión del cliente (noindex, sin sitemap)

Requisitos: Python 3.9+, Jinja2 y Pillow  (pip install jinja2 pillow)
"""
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
TEMPLATES = ROOT / "templates"
WIDTHS = (640, 1200, 1800)  # anchos generados para cada foto


def load_content():
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in CONTENT.glob("*.json")}


def build_images(out: Path):
    """Crea versiones WebP en varios anchos para que cada pantalla baje solo lo que necesita."""
    out_dir = out / "img"
    out_dir.mkdir(parents=True, exist_ok=True)
    info = {}
    for src in sorted((ASSETS / "images").iterdir()):
        if src.suffix.lower() not in {".webp", ".jpg", ".jpeg", ".png"}:
            continue
        im = ImageOps.exif_transpose(Image.open(src))
        keep_alpha = im.mode in ("RGBA", "LA")
        if not keep_alpha:
            im = im.convert("RGB")
        w, h = im.size
        variants = []
        for target in WIDTHS:
            tw = min(target, w)
            if variants and tw == variants[-1][0]:
                continue
            th = round(h * tw / w)
            name = f"{src.stem}-{tw}.webp"
            im.resize((tw, th), Image.LANCZOS).save(out_dir / name, "WEBP", quality=80, method=6)
            variants.append((tw, name))
        best = variants[-1]
        info[src.name] = {
            "src": f"img/{variants[min(1, len(variants) - 1)][1]}",
            "srcset": ", ".join(f"img/{n} {vw}w" for vw, n in variants),
            "w": best[0],
            "h": round(h * best[0] / w),
        }
    return info


def build_icons(out: Path, logo_name: str, share_name: str):
    logo = Image.open(ASSETS / "images" / logo_name).convert("RGBA")
    logo.resize((32, 32), Image.LANCZOS).save(out / "favicon-32.png")
    bg = Image.new("RGBA", (180, 180), (247, 247, 245, 255))
    bg.alpha_composite(logo.resize((150, 150), Image.LANCZOS), (15, 15))
    bg.convert("RGB").save(out / "apple-touch-icon.png")
    # Imagen para compartir en redes (1200x630)
    share = ImageOps.fit(Image.open(ASSETS / "images" / share_name).convert("RGB"), (1200, 630), Image.LANCZOS)
    share.save(out / "og.jpg", "JPEG", quality=85, optimize=True)


def jsonld(sitio):
    c = sitio["contacto"]
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "CREAX",
        "description": sitio["seo"]["descripcion"],
        "url": sitio["seo"]["url"],
        "image": sitio["seo"]["url"] + "/og.jpg",
        "logo": sitio["seo"]["url"] + "/apple-touch-icon.png",
        "email": c["email"],
        "telephone": c["telefono"].replace(" ", ""),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": c["direccion"].split(",")[0].strip(),
            "addressLocality": c["direccion"].split(",")[-1].strip(),
            "addressRegion": c["region"],
            "addressCountry": c["pais"],
        },
        "areaServed": "CL",
        "sameAs": [c["instagram"], c["linkedin"]],
    }, ensure_ascii=False)


def main():
    preview = "--preview" in sys.argv
    staging = "--staging" in sys.argv
    out = ROOT / ("preview" if preview else "dist")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()

    content = load_content()
    sitio, inicio = content["sitio"], content["inicio"]

    images = build_images(out)
    shutil.copytree(ASSETS / "css", out / "css")
    shutil.copytree(ASSETS / "js", out / "js")
    shutil.copytree(ASSETS / "fonts", out / "fonts")

    # Versión para evitar caché antigua al cambiar estilos o scripts
    h = hashlib.sha1()
    for f in sorted((ASSETS / "css").glob("*")) + sorted((ASSETS / "js").glob("*")):
        h.update(f.read_bytes())
    version = h.hexdigest()[:8]

    env = Environment(loader=FileSystemLoader(TEMPLATES), undefined=StrictUndefined, autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)
    html = env.get_template("index.html").render(
        sitio=sitio, inicio=inicio, images=images, preview=preview, staging=staging,
        jsonld=jsonld(sitio), version=version,
    )
    (out / "index.html").write_text(html, encoding="utf-8")

    if not preview:
        build_icons(out, sitio["marca"]["logo"], sitio["seo"]["imagen_compartir"])
        url = sitio["seo"]["url"]
        if staging:
            # Versión de revisión: que los buscadores no la indexen como duplicado del sitio real.
            (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
            (out / ".nojekyll").touch()
        else:
            (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {url}/sitemap.xml\n", encoding="utf-8")
            (out / "sitemap.xml").write_text(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                f"  <url><loc>{url}/</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n"
                "</urlset>\n", encoding="utf-8")

    total = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"Sitio generado en {out.name}/ ({total / 1024:.0f} KB en total)")


if __name__ == "__main__":
    main()
