#!/usr/bin/env python3
"""
Generate OGP images for log.fieldnotes.jp

- Slide pages: PDF first page resized to 1200x630 + site name badge
- Other pages: base photo + dark overlay + site name + title
"""

import os
import re
import sys
from io import BytesIO
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_IMAGE = Path("/workspace/.tmp/2021-03-06.jpg")
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
DOCS_DIR = Path("/workspace/docs")
SLIDES_MD_DIR = DOCS_DIR / "slides"
SLIDES_PDF_DIR = DOCS_DIR / "public/slides"
OUTPUT_DIR = DOCS_DIR / "public/ogp"
SITE_NAME = "log.fieldnotes.jp"

OGP_W, OGP_H = 1200, 630


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def crop_center(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_px: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Wrap text by character for CJK-safe line breaking."""
    lines, current = [], ""
    for ch in text:
        test = current + ch
        w = draw.textlength(test, font=font)
        if w <= max_px:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines or [text]


def draw_text_block(
    img: Image.Image,
    title: str,
    site_name: str = SITE_NAME,
) -> Image.Image:
    # Dark overlay
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle([(0, 0), img.size], fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    margin = 60
    max_w = OGP_W - margin * 2

    # Site name (bottom-left)
    site_font = ImageFont.truetype(FONT_REGULAR, 34)
    draw.text(
        (margin, OGP_H - margin - 34),
        site_name,
        font=site_font,
        fill=(200, 200, 200),
    )

    # Title (vertically centred, slightly above middle)
    if not title:
        return img
    title_font = ImageFont.truetype(FONT_BOLD, 62)
    lines = wrap_text(title, title_font, max_w, draw)
    line_h = 78
    block_h = len(lines) * line_h
    y = (OGP_H - block_h) // 2 - 20

    for line in lines:
        lw = draw.textlength(line, font=title_font)
        x = (OGP_W - lw) // 2
        # Drop shadow
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0))
        draw.text((x, y), line, font=title_font, fill=(255, 255, 255))
        y += line_h

    return img


def add_site_badge(img: Image.Image) -> Image.Image:
    """Small semi-transparent badge in the bottom-right corner."""
    font = ImageFont.truetype(FONT_REGULAR, 28)
    margin, pad = 16, 8

    tmp_draw = ImageDraw.Draw(img)
    tw = tmp_draw.textlength(SITE_NAME, font=font)
    th = 28

    bx0 = OGP_W - int(tw) - margin - pad * 2
    by0 = OGP_H - th - margin - pad * 2
    bx1, by1 = OGP_W - margin, OGP_H - margin

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle([(bx0, by0), (bx1, by1)], fill=(0, 0, 0, 160))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    ImageDraw.Draw(img).text(
        (bx0 + pad, by0 + pad),
        SITE_NAME,
        font=font,
        fill=(255, 255, 255),
    )
    return img


def get_frontmatter(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = line.split(":", 1)
        if len(kv) == 2:
            fm[kv[0].strip()] = kv[1].strip().strip('"').strip("'")
    return fm


def save(img: Image.Image, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def gen_default() -> None:
    img = crop_center(Image.open(BASE_IMAGE).convert("RGB"), OGP_W, OGP_H)
    img = draw_text_block(img, "")
    save(img, OUTPUT_DIR / "default.png")
    print("  default.png")


def gen_page(rel_path: str, title: str) -> None:
    slug = rel_path.replace(".md", "").replace("/", "__")
    img = crop_center(Image.open(BASE_IMAGE).convert("RGB"), OGP_W, OGP_H)
    img = draw_text_block(img, title)
    save(img, OUTPUT_DIR / f"{slug}.png")
    print(f"  {slug}.png")


def gen_slide(md_path: Path) -> None:
    fm = get_frontmatter(md_path)
    title = fm.get("title", md_path.stem)
    pdf_name = md_path.stem + ".pdf"
    pdf_path = SLIDES_PDF_DIR / pdf_name

    if not pdf_path.exists():
        print(f"  [SKIP] no PDF: {pdf_name}")
        return

    doc = fitz.open(str(pdf_path))
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
    doc.close()

    img = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
    img = crop_center(img, OGP_W, OGP_H)
    img = add_site_badge(img)

    save(img, OUTPUT_DIR / "slides" / f"{md_path.stem}.png")
    print(f"  slides/{md_path.stem}.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=== Generating OGP images ===")

    # Default
    print("\n[Default]")
    gen_default()

    # Slides (PDF first page)
    print("\n[Slides]")
    for md in sorted(SLIDES_MD_DIR.glob("*.md")):
        gen_slide(md)

    # Blog and other pages (base image + title)
    print("\n[Blog / other pages]")
    for md in sorted(DOCS_DIR.rglob("*.md")):
        rel = md.relative_to(DOCS_DIR)
        rel_str = str(rel)
        # Skip slides (already handled), index, slides index
        if rel_str.startswith("slides/"):
            continue
        fm = get_frontmatter(md)
        title = fm.get("title", "")
        if not title:
            continue
        gen_page(rel_str, title)

    print("\nDone.")


if __name__ == "__main__":
    main()
