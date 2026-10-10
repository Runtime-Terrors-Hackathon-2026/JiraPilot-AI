"""
Generate JiraPilot AI Brand Assets:
- Original geometric emblem (Faceted delta / pilot wings + orbital ring)
- Horizontal brand mark
- Deep purple / black presentation backgrounds with concentric rings
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
os.makedirs(IMG_DIR, exist_ok=True)

# Color tokens
C_NEAR_BLACK = (8, 7, 13)       # #08070D
C_DEEP_PURPLE = (23, 11, 43)    # #170B2B
C_VIOLET = (139, 92, 246)       # #8B5CF6
C_LAVENDER = (196, 181, 253)    # #C4B5FD
C_WHITE = (255, 255, 255)
C_MUTED = (184, 179, 199)       # #B8B3C7
C_TEAL = (45, 212, 191)

def get_font(size, bold=False):
    path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def generate_logo_icon():
    """Renders 512x512 original geometric JiraPilot AI emblem."""
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Concentric orbital rings (glowing lavender & violet)
    for r in [210, 170, 130]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=(*C_VIOLET, 50 if r > 150 else 90), width=2)

    # Glowing radial backing
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for dr in range(160, 0, -8):
        alpha = int(90 * (1 - dr / 160))
        gd.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill=(*C_VIOLET, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Faceted Geometric Delta Wings (Upward arrow / origami flight emblem)
    # Left wing
    p_left = [(cx, cy - 110), (cx - 95, cy + 55), (cx - 35, cy + 30), (cx, cy + 75)]
    draw.polygon(p_left, fill=(110, 65, 215, 240), outline=(*C_LAVENDER, 255))

    # Right wing
    p_right = [(cx, cy - 110), (cx + 95, cy + 55), (cx + 35, cy + 30), (cx, cy + 75)]
    draw.polygon(p_right, fill=(155, 110, 250, 240), outline=(*C_LAVENDER, 255))

    # Central aerodynamic cockpit / diamond core
    p_core = [(cx, cy - 130), (cx + 32, cy - 20), (cx, cy + 50), (cx - 32, cy - 20)]
    draw.polygon(p_core, fill=(240, 235, 255, 255), outline=(*C_WHITE, 255))

    # Outer chevron accents
    draw.line([(cx - 75, cy - 15), (cx, cy - 85), (cx + 75, cy - 15)],
              fill=(*C_LAVENDER, 220), width=4)

    out_path = os.path.join(IMG_DIR, "logo-icon.png")
    img.save(out_path, "PNG")
    print(f"[OK] Saved logo icon: {out_path}")
    return img

def generate_logo_full(icon_img):
    """Renders 1200x320 horizontal brand mark (Emblem + JiraPilot AI text)."""
    w, h = 1200, 320
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    # Resize icon
    icon_resized = icon_img.resize((240, 240), Image.Resampling.LANCZOS)
    img.paste(icon_resized, (40, 40), icon_resized)

    draw = ImageDraw.Draw(img)
    font_brand = get_font(92, bold=True)
    font_tag = get_font(32, bold=False)

    # "JiraPilot" (White) + " AI" (Electric Violet)
    draw.text((310, 75), "JiraPilot", font=font_brand, fill=C_WHITE)
    bbox_jp = draw.textbbox((0, 0), "JiraPilot", font=font_brand)
    jp_w = bbox_jp[2] - bbox_jp[0]

    draw.text((310 + jp_w + 15, 75), "AI", font=font_brand, fill=C_VIOLET)
    
    # Tagline
    draw.text((315, 195), "Your investigation copilot.", font=font_tag, fill=C_MUTED)

    out_path = os.path.join(IMG_DIR, "logo-full.png")
    img.save(out_path, "PNG")
    print(f"[OK] Saved full logo: {out_path}")
    return img

def generate_background_canvas():
    """Generates 1920x1080 master dark purple background with concentric rings and ambient glow."""
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    # Gradient from near-black (#08070D) to deep purple (#170B2B) in center
    cx, cy = w // 2, h // 2
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    
    # Large soft radial glow
    max_r = 750
    for r in range(max_r, 0, -25):
        ratio = r / max_r
        alpha = int(140 * (1 - ratio) ** 1.6)
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*C_DEEP_PURPLE, alpha))
        if r < 400:
            v_alpha = int(55 * (1 - r / 400))
            gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*C_VIOLET, v_alpha))

    glow = glow.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Concentric purple light rings (from reference video)
    ring_radii = [280, 440, 620, 820]
    for r in ring_radii:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=(*C_VIOLET, 28), width=1)
        # Subtle accent dots on rings
        for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(ang)
            px = int(cx + r * math.cos(rad))
            py = int(cy + r * math.sin(rad))
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(*C_LAVENDER, 70))

    # Subtle vignette
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(120):
        alpha = int(180 * (i / 120))
        # Top, bottom, left, right borders
        vd.rectangle([0, i, w, i + 1], fill=(0, 0, 0, alpha))
        vd.rectangle([0, h - i - 1, w, h - i], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, vignette)

    out_path = os.path.join(IMG_DIR, "background-canvas.png")
    img.save(out_path, "PNG")
    print(f"[OK] Saved master background canvas: {out_path}")
    return img

if __name__ == "__main__":
    icon = generate_logo_icon()
    generate_logo_full(icon)
    generate_background_canvas()
