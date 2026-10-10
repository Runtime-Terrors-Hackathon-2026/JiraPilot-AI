#!/usr/bin/env python3
"""
JiraPilot AI — Closing Title Card Generator
============================================
Produces a standalone closing_title_card.png (1920×1080) for use as
the final frame / chapter card / LinkedIn thumbnail.

Usage:
    pip install pillow
    python generate_title_card.py

Output: output/closing_title_card.png
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080

BG      = (11, 18, 32)
SURFACE = (18, 26, 43)
LINE    = (36, 48, 68)
INK     = (232, 238, 248)
MUTED   = (139, 155, 179)
ACCENT  = (107, 139, 255)
TEAL    = (45, 212, 191)
COPPER  = (210, 120, 40)
COPPER_S= (255, 160, 60)

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)

def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf"  if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def draw_glow(img, cx, cy, radius, color, alpha=0.35):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r, g, b = color
    a = int(255 * alpha)
    for dr in range(radius, 0, -max(1, radius // 10)):
        ratio = dr / radius
        cur_a = int(a * (1 - ratio))
        d.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill=(r, g, b, cur_a))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius // 3))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

img = Image.new("RGB", (W, H), BG)

# Central copper glow
img = draw_glow(img, W // 2, H // 2, 460, COPPER, 0.30)

# Light sweep streak
sweep_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
ds = ImageDraw.Draw(sweep_img)
for dx in range(-30, 31):
    fade = 1 - abs(dx) / 30
    a_s = int(100 * fade)
    ds.line([(W // 2 - 600 + dx, H // 2 - 200),
              (W // 2 + 600 + dx, H // 2 + 80)],
             fill=(*COPPER_S, a_s), width=1)
sweep_img = sweep_img.filter(ImageFilter.GaussianBlur(6))
img = Image.alpha_composite(img.convert("RGBA"), sweep_img).convert("RGB")

draw = ImageDraw.Draw(img)

# --- Copper accent bar above logo ---
bar_w = 240
bx = (W - bar_w) // 2
draw.rectangle([(bx, H // 2 - 148), (bx + bar_w, H // 2 - 140)], fill=COPPER)

# --- Logo: "JiraPilot" (white) + "AI" (copper) ---
font_logo = load_font(100, bold=True)
prefix = "JiraPilot "
suffix = "AI"
bbox_p = draw.textbbox((0, 0), prefix, font=font_logo)
bbox_s = draw.textbbox((0, 0), suffix, font=font_logo)
pw = bbox_p[2] - bbox_p[0]
sw = bbox_s[2] - bbox_s[0]
total_w = pw + sw
lx = (W - total_w) // 2
logo_y = H // 2 - 130
draw.text((lx, logo_y), prefix, font=font_logo, fill=INK)
draw.text((lx + pw, logo_y), suffix, font=font_logo, fill=COPPER_S)

# --- Thin copper underline ---
ul_w = 320
ul_x = (W - ul_w) // 2
draw.rectangle([(ul_x, H // 2 - 8), (ul_x + ul_w, H // 2 - 2)], fill=COPPER)

# --- Main headline ---
font_hl = load_font(54, bold=True)
headline = "Less repetitive triage. More time to solve."
bbox_hl = draw.textbbox((0, 0), headline, font=font_hl)
hlw = bbox_hl[2] - bbox_hl[0]
draw.text(((W - hlw) // 2, H // 2 + 18), headline, font=font_hl, fill=INK)

# --- Supporting tagline ---
font_tl = load_font(32)
tagline = "JiraPilot AI  —  Your investigation copilot."
bbox_tl = draw.textbbox((0, 0), tagline, font=font_tl)
tlw = bbox_tl[2] - bbox_tl[0]
draw.text(((W - tlw) // 2, H // 2 + 94), tagline, font=font_tl, fill=MUTED)

# --- Subtle corner accent dots ---
for cx_dot, cy_dot in [(80, 80), (W - 80, 80), (80, H - 80), (W - 80, H - 80)]:
    for r_d in [12, 8, 4]:
        alpha_d = int(80 * (1 - r_d / 12))
        ov_d = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dd = ImageDraw.Draw(ov_d)
        dd.ellipse([cx_dot - r_d, cy_dot - r_d, cx_dot + r_d, cy_dot + r_d],
                   fill=(*COPPER, alpha_d))
        img = Image.alpha_composite(img.convert("RGBA"), ov_d).convert("RGB")

# --- Watermark / version ---
font_wm = load_font(16)
wm = "© 2026 RUNTIME_Terrors  |  Synthetic demo content — not real customer data"
draw2 = ImageDraw.Draw(img)
draw2.text((40, H - 40), wm, font=font_wm, fill=(*MUTED, 120))

out_path = os.path.join(OUT_DIR, "closing_title_card.png")
img.save(out_path, format="PNG", optimize=True)
print(f"Title card saved: {out_path}")
