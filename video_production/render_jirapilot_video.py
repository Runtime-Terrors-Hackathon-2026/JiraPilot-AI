"""
JiraPilot AI — 60-Second Product Video Renderer
================================================
Renders a cinematic 60-second enterprise product explainer at 1920×1080 / 30fps.

Dependencies:
    pip install moviepy==1.0.3 pillow numpy

Run:
    python render_jirapilot_video.py

Output:
    output/jirapilot_60s_final.mp4          — final composite
    output/jirapilot_60s_noaudio.mp4        — video-only (for external VO/music mix)
    output/scenes/scene_01_problem.mp4      — individual scene clips
    output/scenes/scene_02_logo.mp4
    output/scenes/scene_03_readiness.mp4
    output/scenes/scene_04_logs.mp4
    output/scenes/scene_05_repo.mp4
    output/scenes/scene_06_reports.mp4
    output/scenes/scene_07_dashboard.mp4
    output/scenes/scene_08_closing.mp4

Notes:
  • All fictional data (ticket keys, endpoints, repos) is clearly synthetic.
  • No AI-generated frame text for critical labels — all key strings are rendered
    via Pillow as clean composited layers before MoviePy assembly.
  • Captions / VO text are in companion files (see video_production/captions/).
  • For a version with embedded captions, burn the provided SRT with:
      ffmpeg -i jirapilot_60s_final.mp4 -vf subtitles=captions/jirapilot_captions.srt \
             jirapilot_60s_captioned.mp4
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------------------
# Attempt moviepy import – give a friendly message if missing
# ---------------------------------------------------------------------------
try:
    from moviepy.editor import (
        VideoClip, CompositeVideoClip, concatenate_videoclips,
        TextClip, ColorClip, ImageClip,
    )
    MOVIEPY_OK = True
except ImportError:
    MOVIEPY_OK = False
    print("[WARNING] moviepy not installed. Run:  pip install moviepy==1.0.3 pillow numpy")
    print("          This script will still write all storyboard/caption assets.")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
W, H = 1920, 1080
FPS = 30
DURATION = 60.0          # seconds

# Brand colours (from index.css dark theme)
BG       = (11, 18, 32)       # #0b1220  deep charcoal/near-black
SURFACE  = (18, 26, 43)       # #121a2b
LINE     = (36, 48, 68)       # #243044
INK      = (232, 238, 248)    # #e8eef8  white typography
MUTED    = (139, 155, 179)    # #8b9bb3
ACCENT   = (107, 139, 255)    # #6b8bff  indigo
TEAL     = (45, 212, 191)     # #2dd4bf
AMBER    = (251, 191, 36)     # #fbbf24
DANGER   = (248, 113, 113)    # #f87171

# Copper-orange warm glow (reference video style)
COPPER   = (210, 120, 40)
COPPER_S = (255, 160, 60)     # bright highlight tip

OUT_DIR   = os.path.join(os.path.dirname(__file__), "output")
SCENE_DIR = os.path.join(OUT_DIR, "scenes")
os.makedirs(SCENE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Utility: base canvas
# ---------------------------------------------------------------------------
def base_canvas(w=W, h=H, color=BG) -> Image.Image:
    return Image.new("RGB", (w, h), color)

def np_frame(img: Image.Image) -> np.ndarray:
    return np.array(img)

# ---------------------------------------------------------------------------
# Utility: font loading with fallback
# ---------------------------------------------------------------------------
def load_font(size: int, bold: bool = False):
    """Try common system fonts; fall back to Pillow default."""
    candidates = (
        # Windows
        ["C:/Windows/Fonts/segoeuib.ttf",
         "C:/Windows/Fonts/segoeui.ttf",
         "C:/Windows/Fonts/arialbd.ttf",
         "C:/Windows/Fonts/arial.ttf",
         "C:/Windows/Fonts/calibrib.ttf",
         "C:/Windows/Fonts/calibri.ttf",
         "C:/Windows/Fonts/consolab.ttf",
         "C:/Windows/Fonts/consola.ttf",
        ]
    )
    for path in candidates[0]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def load_mono_font(size: int):
    mono = ["C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/cour.ttf"]
    for path in mono:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def draw_text_centered(draw: ImageDraw.ImageDraw, y: int, text: str,
                        font, color=INK, w=W):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (w - tw) // 2
    draw.text((x, y), text, font=font, fill=color)

def draw_glow_circle(img: Image.Image, cx: int, cy: int,
                     radius: int, color: tuple, alpha: float = 0.35):
    """Soft radial glow using Gaussian-blurred circle."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r, g, b = color
    a = int(255 * alpha)
    for dr in range(radius, 0, -max(1, radius // 10)):
        ratio = dr / radius
        cur_a = int(a * (1 - ratio))
        d.ellipse(
            [cx - dr, cy - dr, cx + dr, cy + dr],
            fill=(r, g, b, cur_a)
        )
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius // 3))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
    return img

def draw_light_streak(img: Image.Image, y: int, alpha: float = 0.18):
    """Horizontal copper light streak."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for dy in range(-12, 13):
        fade = max(0, 1 - abs(dy) / 12)
        a = int(255 * alpha * fade)
        d.line([(0, y + dy), (W, y + dy)], fill=(*COPPER, a), width=1)
    blurred = overlay.filter(ImageFilter.GaussianBlur(4))
    return Image.alpha_composite(img.convert("RGBA"), blurred).convert("RGB")

def draw_card(draw: ImageDraw.ImageDraw, x1, y1, x2, y2,
              fill=SURFACE, border=LINE, radius=12):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                            fill=fill, outline=border, width=1)

def typewriter_fraction(text: str, t: float, duration: float) -> str:
    """Return the visible prefix of text at time t within duration."""
    chars = int(len(text) * min(1.0, t / max(0.01, duration)))
    return text[:chars]

# ---------------------------------------------------------------------------
# Scene 1: The Problem  (0–5 s)
# ---------------------------------------------------------------------------
def make_scene_01(t: float) -> np.ndarray:
    """
    Near-total darkness. Orange particles animate in. Typewriter text:
    'Every incident starts with a question.'
    """
    img = base_canvas()

    # Ambient copper glow in centre-left
    glow_alpha = min(0.45, t * 0.12)
    img = draw_glow_circle(img, W // 3, H // 2, 380, COPPER, glow_alpha)

    # Floating synthetic log fragments (static seed positions, gentle fade-in)
    rng = np.random.default_rng(42)
    log_lines = [
        "NOVA-1001  HTTP 503  /api/payment/process",
        "correlationId=CORR-8821  ts=2026-10-09T08:14:22Z",
        "ERROR [NOVA-SVC] Upstream timeout after 30000ms",
        "WARN  [NOVA-GW]  Retry attempt 3/3 — giving up",
        "[EXCEPTION] java.net.SocketTimeoutException",
        "POST /api/cart/checkout  →  503 Service Unavailable",
    ]
    mono_sm = load_mono_font(18)
    fragment_alpha = min(1.0, t * 0.30)
    for i, line in enumerate(log_lines):
        x = int(rng.integers(80, W - 400))
        y = int(rng.integers(80, H - 80))
        # Very dim fragments
        a = int(80 * fragment_alpha)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dov = ImageDraw.Draw(overlay)
        dov.text((x, y), line, font=mono_sm, fill=(*MUTED, a))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Light particles (dots)
    draw = ImageDraw.Draw(img)
    rng2 = np.random.default_rng(7)
    n_particles = 60
    for i in range(n_particles):
        px = int(rng2.integers(0, W))
        py = int(rng2.integers(0, H))
        phase = rng2.random() * 2 * math.pi
        brightness = 0.4 + 0.6 * math.sin(t * 1.5 + phase)
        r = max(1, int(rng2.integers(1, 4)))
        a_p = int(180 * brightness * min(1.0, t * 0.5))
        col = (*COPPER_S, a_p)
        overlay2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d2 = ImageDraw.Draw(overlay2)
        d2.ellipse([px - r, py - r, px + r, py + r], fill=col)
        img = Image.alpha_composite(img.convert("RGBA"), overlay2).convert("RGB")

    # Typewriter main text
    font_h1 = load_font(58, bold=True)
    full_text = "Every incident starts with a question."
    tw_text = typewriter_fraction(full_text, t - 0.5, 3.0)
    if tw_text:
        draw = ImageDraw.Draw(img)
        draw_text_centered(draw, H // 2 + 120, tw_text, font_h1, INK)

    # Fade in from black for first 0.5s
    if t < 0.5:
        black_alpha = int(255 * (1 - t / 0.5))
        black_overlay = Image.new("RGBA", img.size, (0, 0, 0, black_alpha))
        img = Image.alpha_composite(img.convert("RGBA"), black_overlay).convert("RGB")

    return np_frame(img)

# ---------------------------------------------------------------------------
# Scene 2: Logo reveal + NOVA-1001 Jira ticket  (5–12 s)
# ---------------------------------------------------------------------------
def make_scene_02(t: float) -> np.ndarray:
    """
    JiraPilot AI logo fades in, then camera pushes into a Jira ticket.
    """
    img = base_canvas()
    draw = ImageDraw.Draw(img)

    # Subtle copper glow
    img = draw_glow_circle(img, W // 2, H // 2 - 200, 260, COPPER, 0.30)

    scene_t = t  # local 0–7
    logo_alpha = min(1.0, scene_t / 1.2)

    # --- Logo block ---
    font_logo = load_font(72, bold=True)
    font_sub  = load_font(28)
    logo_y    = 180

    # Copper accent bar above logo
    bar_w = int(120 * logo_alpha)
    if bar_w > 0:
        draw.rectangle([(W // 2 - bar_w // 2, logo_y - 24),
                         (W // 2 + bar_w // 2, logo_y - 18)],
                        fill=COPPER)

    # Logo text
    logo_text = "JiraPilot AI"
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dov = ImageDraw.Draw(overlay)
    bbox = dov.textbbox((0, 0), logo_text, font=font_logo)
    lw = bbox[2] - bbox[0]
    a_logo = int(255 * logo_alpha)
    dov.text(((W - lw) // 2, logo_y), logo_text, font=font_logo,
             fill=(*INK, a_logo))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    sub_text = "AI-Powered Jira Triage & Log Investigation"
    overlay2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dov2 = ImageDraw.Draw(overlay2)
    bbox2 = dov2.textbbox((0, 0), sub_text, font=font_sub)
    sw = bbox2[2] - bbox2[0]
    dov2.text(((W - sw) // 2, logo_y + 90), sub_text, font=font_sub,
              fill=(*MUTED, a_logo))
    img = Image.alpha_composite(img.convert("RGBA"), overlay2).convert("RGB")

    # --- Jira ticket card appears after t=1.5 ---
    if scene_t > 1.5:
        card_progress = min(1.0, (scene_t - 1.5) / 1.8)
        card_alpha    = int(255 * card_progress)

        # Simulate slow camera push: card grows slightly
        scale = 0.82 + 0.18 * card_progress
        cw = int(860 * scale)
        ch = int(480 * scale)
        cx = (W - cw) // 2
        cy = int(H // 2 - ch // 2 + 60)

        card_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(card_img)

        # Card background
        cd.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=14,
                               fill=(*SURFACE, card_alpha),
                               outline=(*LINE, card_alpha), width=1)

        # Ticket header bar (indigo strip)
        cd.rounded_rectangle([cx, cy, cx + cw, cy + 48], radius=14,
                               fill=(*ACCENT, card_alpha))
        cd.rectangle([cx, cy + 30, cx + cw, cy + 48],
                      fill=(*ACCENT, card_alpha))

        font_key  = load_mono_font(22)
        font_body = load_font(20)
        font_sm   = load_font(16)

        def t_alpha(txt, f, col, x, y):
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
            dov_l = ImageDraw.Draw(ov)
            dov_l.text((x, y), txt, font=f, fill=(*col, card_alpha))
            return ov

        card_img = Image.alpha_composite(card_img,
            t_alpha("NOVA-1001", font_key, INK, cx + 20, cy + 14))
        card_img = Image.alpha_composite(card_img,
            t_alpha("● OPEN  |  Priority: HIGH  |  Project: Nova Platform",
                    font_sm, INK, cx + 180, cy + 20))

        # Fields
        fields = [
            ("Summary",       "Payment service returns 503 during peak load periods"),
            ("Environment",   "Production — EU-WEST-1"),
            ("Reporter",      "alex.morgan@nova.example.com"),
            ("API Endpoint",  "POST /api/payment/process"),
            ("Created",       "2026-10-09  08:14 UTC"),
        ]
        fy = cy + 68
        for label, value in fields:
            card_img = Image.alpha_composite(card_img,
                t_alpha(label + ":", font_sm, MUTED, cx + 24, fy))
            card_img = Image.alpha_composite(card_img,
                t_alpha(value, font_body, INK, cx + 220, fy))
            fy += 42

        # "A new Jira issue. A clearer path forward."
        caption_font = load_font(36, bold=True)
        cap = "A new Jira issue. A clearer path forward."
        ov3 = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dov3 = ImageDraw.Draw(ov3)
        bbox3 = dov3.textbbox((0, 0), cap, font=caption_font)
        cw3 = bbox3[2] - bbox3[0]
        dov3.text(((W - cw3) // 2, cy + ch + 28), cap, font=caption_font,
                  fill=(*INK, card_alpha))
        card_img = Image.alpha_composite(card_img, ov3)

        img = Image.alpha_composite(img.convert("RGBA"), card_img).convert("RGB")

    # Cursor blink (appears after card)
    if scene_t > 3.0:
        cursor_blink = math.sin(scene_t * 4) > 0
        if cursor_blink:
            draw2 = ImageDraw.Draw(img)
            # Cursor positioned at end of Summary field
            draw2.rectangle([W // 2 + 100, H // 2 + 82,
                              W // 2 + 103, H // 2 + 100],
                             fill=COPPER)

    return np_frame(img)

# ---------------------------------------------------------------------------
# Scene 3: Ticket Readiness  (12–20 s)
# ---------------------------------------------------------------------------
def make_scene_03(t: float) -> np.ndarray:
    """
    Diagnostic readiness checklist animates in field by field.
    """
    img = base_canvas()
    img = draw_glow_circle(img, W // 2, 300, 200, ACCENT, 0.18)
    draw = ImageDraw.Draw(img)

    font_title = load_font(44, bold=True)
    font_body  = load_font(22)
    font_sm    = load_font(16)

    # Title
    title = "Diagnostic Information Readiness"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 80), title, font=font_title, fill=INK)

    # Subtitle caption
    cap = "Validate. Identify gaps. Request the right details."
    font_cap = load_font(30)
    bbox2 = draw.textbbox((0, 0), cap, font=font_cap)
    cw2 = bbox2[2] - bbox2[0]
    draw.text(((W - cw2) // 2, 148), cap, font=font_cap, fill=COPPER_S)

    # Readiness score bar
    score = min(1.0, t / 6.0)  # grows over 6s
    bar_x, bar_y, bar_w, bar_h = 600, 230, 720, 20
    draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                            radius=10, fill=LINE)
    filled_w = int(bar_w * score * 0.75)  # max 75% (some missing)
    if filled_w > 0:
        draw.rounded_rectangle([bar_x, bar_y, bar_x + filled_w, bar_y + bar_h],
                                radius=10, fill=TEAL)
    score_pct = int(score * 75)
    draw.text((bar_x + bar_w + 16, bar_y - 2), f"{score_pct}%",
              font=font_body, fill=TEAL)

    # Fields checklist — 6 items, animate in one by one
    fields = [
        ("Description",   True),
        ("API Endpoint",  True),
        ("Server Logs",   False),   # missing
        ("Payload (JSON)",True),
        ("Environment",   True),
        ("Error Pattern", False),   # missing
    ]
    grid_x_start = 260
    grid_y_start = 290
    cell_w, cell_h = 540, 90
    gap = 20

    for idx, (label, available) in enumerate(fields):
        col = idx % 3
        row = idx // 3
        cx_cell = grid_x_start + col * (cell_w + gap)
        cy_cell = grid_y_start + row * (cell_h + gap)

        # Animate staggered appearance
        appear_t = idx * 0.55
        if t < appear_t:
            continue
        cell_alpha = min(1.0, (t - appear_t) / 0.4)
        a = int(255 * cell_alpha)

        fill_col  = (*TEAL,   30) if available else (*DANGER, 30)
        border_col= (*TEAL,  120) if available else (*DANGER, 120)
        text_col  = TEAL          if available else DANGER
        icon_text = "✓"           if available else "!"

        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dov = ImageDraw.Draw(ov)
        dov.rounded_rectangle([cx_cell, cy_cell,
                                cx_cell + cell_w, cy_cell + cell_h],
                               radius=10, fill=fill_col, outline=border_col, width=1)
        dov.text((cx_cell + 18, cy_cell + 18), label, font=font_body, fill=(*text_col, a))
        font_icon = load_font(30, bold=True)
        dov.text((cx_cell + cell_w - 46, cy_cell + 26), icon_text,
                 font=font_icon, fill=(*text_col, a))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    # Missing fields message
    if t > 3.8:
        msg_alpha = min(1.0, (t - 3.8) / 0.8)
        ov_msg = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dov_m  = ImageDraw.Draw(ov_msg)
        msg = "⚠  Missing: Server Logs, Error Pattern — JiraPilot AI will request these from the reporter."
        font_msg = load_font(20)
        bbox_m = dov_m.textbbox((0, 0), msg, font=font_msg)
        mw = bbox_m[2] - bbox_m[0]
        a_m = int(255 * msg_alpha)
        dov_m.text(((W - mw) // 2, 590), msg, font=font_msg,
                   fill=(*AMBER, a_m))
        img = Image.alpha_composite(img.convert("RGBA"), ov_msg).convert("RGB")

    return np_frame(img)

# ---------------------------------------------------------------------------
# Scene 4: AI Log Analysis  (20–30 s)
# ---------------------------------------------------------------------------
def make_scene_04(t: float) -> np.ndarray:
    """
    Dark log viewer. Highlight endpoint, HTTP 503, correlationId.
    Animated connectors. Observed facts vs probable cause.
    """
    img = base_canvas()
    img = draw_glow_circle(img, W // 4, H // 2, 280, TEAL, 0.12)
    draw = ImageDraw.Draw(img)

    font_title = load_font(40, bold=True)
    font_mono  = load_mono_font(16)
    font_sm    = load_font(18)

    # Title / caption
    draw.text((80, 44), "From raw logs to evidence-backed insights.", font=font_title, fill=INK)

    # Log panel card
    lp_x, lp_y, lp_w, lp_h = 60, 110, 1000, 580
    draw.rounded_rectangle([lp_x, lp_y, lp_x + lp_w, lp_y + lp_h],
                            radius=12, fill=(7, 11, 20), outline=LINE, width=1)
    draw.rectangle([lp_x, lp_y, lp_x + lp_w, lp_y + 34],
                    fill=(14, 22, 36))
    draw.text((lp_x + 16, lp_y + 10), "nova-payment-service.log", font=font_sm, fill=MUTED)

    # Log lines
    log_entries = [
        (1, "2026-10-09 08:12:01.021 INFO  [NOVA-PAY] Starting PaymentProcessor v2.4.1"),
        (2, "2026-10-09 08:13:55.412 INFO  [NOVA-PAY] Received POST /api/payment/process"),
        (3, "2026-10-09 08:13:55.890 WARN  [NOVA-PAY] Circuit breaker state: HALF_OPEN"),
        (4, "2026-10-09 08:13:56.003 ERROR [NOVA-PAY] Upstream call failed: POST /api/payment/process"),
        (5, "                               correlationId=CORR-NOVA-8821  status=503"),
        (6, "2026-10-09 08:13:56.004 ERROR [NOVA-GW]  Service Unavailable — retrying (1/3)"),
        (7, "2026-10-09 08:13:57.218 ERROR [NOVA-GW]  Service Unavailable — retrying (2/3)"),
        (8, "2026-10-09 08:13:58.523 ERROR [NOVA-GW]  Service Unavailable — retrying (3/3) — giving up"),
        (9, "2026-10-09 08:13:58.524 ERROR [NOVA-PAY] Max retries exhausted for correlationId=CORR-NOVA-8821"),
        (10,"2026-10-09 08:13:58.525 INFO  [NOVA-PAY] Returning HTTP 503 to client"),
    ]

    # Highlight keywords
    HIGHLIGHT_MAP = {
        "POST /api/payment/process": TEAL,
        "503":                        DANGER,
        "CORR-NOVA-8821":             AMBER,
        "08:13:5":                    COPPER_S,
        "ERROR":                      DANGER,
        "WARN":                       AMBER,
    }

    ly = lp_y + 44
    for line_num, text in log_entries:
        appear_t = (line_num - 1) * 0.55
        if t < appear_t:
            break
        line_alpha = min(1.0, (t - appear_t) / 0.3)
        a = int(255 * line_alpha)
        # Default muted color, detect highlights
        col = MUTED
        for kw, kwcol in HIGHLIGHT_MAP.items():
            if kw in text:
                col = kwcol
                break
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dov = ImageDraw.Draw(ov)
        ln_text = f"{line_num:>3}  {text}"
        dov.text((lp_x + 12, ly), ln_text, font=font_mono, fill=(*col, a))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        ly += 50

    # Animated thin connector lines (after t=4)
    if t > 4.0:
        line_prog = min(1.0, (t - 4.0) / 2.0)
        conn_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(conn_img)
        # Connect line 4 to line 9 (CORR ID)
        x1, y1_c = lp_x + lp_w + 4, lp_y + 44 + 3 * 50 + 25
        x2, y2_c = lp_x + lp_w + 4, lp_y + 44 + 8 * 50 + 25
        ym = (y1_c + y2_c) // 2
        end_y = int(y1_c + (y2_c - y1_c) * line_prog)
        dc.line([(x1, y1_c), (x1 + 32, y1_c), (x1 + 32, end_y)],
                fill=(*AMBER, 180), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), conn_img).convert("RGB")

    # Right panel: Observed Facts & Probable Cause
    rp_x, rp_y, rp_w, rp_h = 1100, 110, 760, 580
    draw2 = ImageDraw.Draw(img)
    draw2.rounded_rectangle([rp_x, rp_y, rp_x + rp_w, rp_y + rp_h],
                             radius=12, fill=SURFACE, outline=LINE, width=1)
    font_panel_h = load_font(22, bold=True)
    font_fact    = load_font(17)

    # Observed facts section
    if t > 2.0:
        facts_alpha = min(1.0, (t - 2.0) / 1.2)
        ov_f = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dof  = ImageDraw.Draw(ov_f)
        a_f  = int(255 * facts_alpha)
        dof.text((rp_x + 24, rp_y + 24), "Observed Facts", font=font_panel_h,
                 fill=(*TEAL, a_f))
        facts = [
            "• Endpoint: POST /api/payment/process",
            "• HTTP 503 — Service Unavailable",
            "• Correlation ID: CORR-NOVA-8821",
            "• Timestamp: 2026-10-09 08:13:56 UTC",
            "• Retry chain: 3 attempts, all failed",
            "• Circuit breaker was in HALF_OPEN state",
        ]
        ffy = rp_y + 68
        for fact in facts:
            ov_f = Image.alpha_composite(ov_f, _text_overlay(
                fact, font_fact, (*INK, a_f), (rp_x + 24, ffy), img.size))
            ffy += 38
        img = Image.alpha_composite(img.convert("RGBA"), ov_f).convert("RGB")

    # Probable cause section
    if t > 5.5:
        cause_alpha = min(1.0, (t - 5.5) / 1.5)
        ov_c = Image.new("RGBA", img.size, (0, 0, 0, 0))
        doc  = ImageDraw.Draw(ov_c)
        a_c  = int(255 * cause_alpha)
        sep_y = rp_y + 320
        doc.line([(rp_x + 20, sep_y), (rp_x + rp_w - 20, sep_y)],
                 fill=(*LINE, a_c), width=1)
        doc.text((rp_x + 24, sep_y + 20), "Probable Cause", font=font_panel_h,
                 fill=(*AMBER, a_c))
        cause_text = (
            "Upstream payment gateway appears unavailable.\n"
            "Circuit breaker in HALF_OPEN state unable to\n"
            "recover — all 3 retries exhausted. Likely a\n"
            "transient dependency failure or misconfigured\n"
            "timeout on the payment gateway service."
        )
        cfy = sep_y + 66
        for line in cause_text.split("\n"):
            ov_c = Image.alpha_composite(ov_c, _text_overlay(
                line, font_fact, (*INK, a_c), (rp_x + 24, cfy), img.size))
            cfy += 36
        note = "Note: This is an evidence-backed hypothesis, not a confirmed root cause."
        ov_c = Image.alpha_composite(ov_c, _text_overlay(
            note, load_font(14), (*MUTED, a_c), (rp_x + 24, cfy + 10), img.size))
        img = Image.alpha_composite(img.convert("RGBA"), ov_c).convert("RGB")

    return np_frame(img)

def _text_overlay(text, font, fill, pos, size):
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.text(pos, text, font=font, fill=fill)
    return ov

# ---------------------------------------------------------------------------
# Scene 5: Repository Discovery  (30–38 s)
# ---------------------------------------------------------------------------
def make_scene_05(t: float) -> np.ndarray:
    """
    Endpoint → verified repo card → terminal with clone command → Copy animation.
    """
    img = base_canvas()
    img = draw_glow_circle(img, W * 3 // 4, H // 2, 300, TEAL, 0.14)
    draw = ImageDraw.Draw(img)

    font_title = load_font(40, bold=True)
    font_body  = load_font(22)
    font_mono  = load_mono_font(18)
    font_sm    = load_font(17)

    draw.text((80, 44), "Find the right repository. Start debugging faster.", font=font_title, fill=INK)

    # Endpoint bubble
    if t > 0.3:
        ep_alpha = min(1.0, (t - 0.3) / 0.8)
        a = int(255 * ep_alpha)
        ep_x, ep_y, ep_w, ep_h = 80, 130, 720, 100
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dov = ImageDraw.Draw(ov)
        dov.rounded_rectangle([ep_x, ep_y, ep_x + ep_w, ep_y + ep_h],
                               radius=10, fill=(*SURFACE, a), outline=(*TEAL, a // 2), width=1)
        dov.text((ep_x + 20, ep_y + 14), "Detected Endpoint", font=font_sm, fill=(*MUTED, a))
        dov.text((ep_x + 20, ep_y + 44), "POST /api/payment/process", font=font_mono, fill=(*TEAL, a))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    # Arrow connector
    if t > 1.4:
        arr_alpha = min(1.0, (t - 1.4) / 0.6)
        a_arr = int(255 * arr_alpha)
        arr_prog = min(1.0, (t - 1.4) / 0.6)
        ov_a = Image.new("RGBA", img.size, (0, 0, 0, 0))
        da = ImageDraw.Draw(ov_a)
        x_start, y_start = 800, 180
        x_end = x_start + int(120 * arr_prog)
        da.line([(x_start, y_start), (x_end, y_start)], fill=(*COPPER, a_arr), width=3)
        if arr_prog > 0.8:
            da.polygon([(x_end, y_start - 10), (x_end + 18, y_start),
                         (x_end, y_start + 10)], fill=(*COPPER, a_arr))
        img = Image.alpha_composite(img.convert("RGBA"), ov_a).convert("RGB")

    # Repository card
    if t > 2.2:
        repo_alpha = min(1.0, (t - 2.2) / 1.0)
        a_r = int(255 * repo_alpha)
        rx, ry, rw, rh = 950, 110, 900, 200
        ov_r = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dor = ImageDraw.Draw(ov_r)
        dor.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=12,
                               fill=(*SURFACE, a_r), outline=(*TEAL, a_r // 2), width=2)
        # Header bar with teal accent
        dor.rounded_rectangle([rx, ry, rx + rw, ry + 44], radius=12,
                               fill=(*TEAL, a_r // 3))
        dor.rectangle([rx, ry + 28, rx + rw, ry + 44], fill=(*TEAL, a_r // 3))
        dor.text((rx + 20, ry + 12), "✓  Verified Repository Match", font=font_sm, fill=(*TEAL, a_r))
        dor.text((rx + 20, ry + 60), "nova-payment-service", font=load_font(28, bold=True), fill=(*INK, a_r))
        dor.text((rx + 20, ry + 102), "Service: NOVA-PAY  |  Language: Java  |  Team: Payments Engineering", font=font_sm, fill=(*MUTED, a_r))
        dor.text((rx + 20, ry + 136), "git.internal.example.com/nova-platform/nova-payment-service", font=font_mono, fill=(*ACCENT, a_r))
        img = Image.alpha_composite(img.convert("RGBA"), ov_r).convert("RGB")

    # Terminal panel with clone command
    if t > 3.5:
        term_alpha = min(1.0, (t - 3.5) / 1.0)
        a_t = int(255 * term_alpha)
        tx, ty, tw_panel, th = 80, 280, 1760, 200
        ov_t = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dot = ImageDraw.Draw(ov_t)
        dot.rounded_rectangle([tx, ty, tx + tw_panel, ty + th], radius=12,
                               fill=(7, 11, 20, a_t), outline=(*LINE, a_t), width=1)
        dot.rectangle([tx, ty, tx + tw_panel, ty + 32], fill=(14, 22, 36, a_t))
        # Traffic lights
        for ci, cc in enumerate([(DANGER, 0), (AMBER, 24), (TEAL, 48)]):
            dot.ellipse([tx + 14 + cc[1], ty + 10, tx + 24 + cc[1], ty + 22],
                         fill=(*cc[0], a_t))
        dot.text((tx + 80, ty + 9), "terminal", font=font_sm, fill=(*MUTED, a_t))

        clone_cmd = "git clone git@git.internal.example.com:nova-platform/nova-payment-service.git"
        dot.text((tx + 20, ty + 52), "$ " + clone_cmd, font=font_mono, fill=(*INK, a_t))
        img = Image.alpha_composite(img.convert("RGBA"), ov_t).convert("RGB")

    # Copy button + animation
    if t > 5.2:
        copy_alpha = min(1.0, (t - 5.2) / 0.5)
        a_cp = int(255 * copy_alpha)
        copied = t > 6.2
        btn_x, btn_y = 1680, 330
        ov_cp = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dcp = ImageDraw.Draw(ov_cp)
        btn_col = TEAL if copied else ACCENT
        dcp.rounded_rectangle([btn_x, btn_y, btn_x + 130, btn_y + 40], radius=8,
                               fill=(*btn_col, a_cp))
        btn_text = "✓ Copied!" if copied else "Copy"
        dcp.text((btn_x + 24, btn_y + 10), btn_text, font=font_sm, fill=(*INK, a_cp))
        if copied:
            # Pulse glow around button
            dcp.rounded_rectangle([btn_x - 4, btn_y - 4, btn_x + 134, btn_y + 44],
                                   radius=12, outline=(*TEAL, min(a_cp, 160)), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), ov_cp).convert("RGB")

    # Caption bottom
    if t > 1.0:
        cap_alpha = min(1.0, (t - 1.0) / 1.0)
        ov_cap = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(ov_cap)
        cap = "Approved repositories & copy-ready clone commands — ready for debugging."
        bbox_cap = dc.textbbox((0, 0), cap, font=font_sm)
        wc = bbox_cap[2] - bbox_cap[0]
        dc.text(((W - wc) // 2, H - 80), cap, font=font_sm,
                fill=(*MUTED, int(255 * cap_alpha)))
        img = Image.alpha_composite(img.convert("RGBA"), ov_cap).convert("RGB")

    return np_frame(img)

# ---------------------------------------------------------------------------
# Scene 6: Jira Comment + Email  (38–47 s)
# ---------------------------------------------------------------------------
def make_scene_06(t: float) -> np.ndarray:
    """
    Split-screen: Jira investigation comment (left) | Email notification (right).
    """
    img = base_canvas()
    draw = ImageDraw.Draw(img)

    font_title  = load_font(38, bold=True)
    font_body   = load_font(18)
    font_sm     = load_font(15)
    font_mono   = load_mono_font(15)

    draw.text((80, 40), "Clear reports. Better handoffs.", font=font_title, fill=INK)

    # Divider line fades in
    div_alpha = min(1.0, t / 0.8)
    draw.line([(W // 2, 110), (W // 2, H - 60)],
               fill=(*LINE, int(255 * div_alpha)), width=1)

    # --- LEFT: Jira Comment ---
    lx, ly = 60, 110
    lw_panel = W // 2 - 80

    if t > 0.3:
        jira_alpha = min(1.0, (t - 0.3) / 1.2)
        a_j = int(255 * jira_alpha)
        ov_j = Image.new("RGBA", img.size, (0, 0, 0, 0))
        doj  = ImageDraw.Draw(ov_j)

        # Panel
        doj.rounded_rectangle([lx, ly, lx + lw_panel, ly + 860],
                               radius=12, fill=(*SURFACE, a_j), outline=(*LINE, a_j), width=1)
        # Header
        doj.rounded_rectangle([lx, ly, lx + lw_panel, ly + 44], radius=12,
                               fill=(*ACCENT, a_j // 3))
        doj.rectangle([lx, ly + 28, lx + lw_panel, ly + 44], fill=(*ACCENT, a_j // 3))
        doj.text((lx + 16, ly + 13), "Jira Investigation Comment  —  NOVA-1001", font=font_sm, fill=(*INK, a_j))

        comment_lines = [
            "📋  Investigation Report — NOVA-1001",
            "",
            "Summary:",
            "  Payment service returning HTTP 503 during peak load.",
            "",
            "Observed Evidence:",
            "  • POST /api/payment/process  →  503",
            "  • Correlation ID: CORR-NOVA-8821",
            "  • Circuit breaker state: HALF_OPEN at failure time",
            "  • 3 retry attempts, all exhausted",
            "",
            "Probable Cause (Hypothesis):",
            "  Upstream payment gateway appears unreachable.",
            "  Circuit breaker could not recover. Dependency",
            "  timeout may be misconfigured.",
            "",
            "Recommended Next Steps:",
            "  1. Inspect payment-gateway health at 08:13 UTC",
            "  2. Review circuit breaker config & timeout values",
            "  3. Clone nova-payment-service for local reproduction",
            "",
            "Repository: nova-payment-service",
            "Clone: git clone git@git.internal…/nova-payment-service.git",
        ]
        cly = ly + 56
        for line in comment_lines:
            col = TEAL if line.startswith("Probable") or line.startswith("Observed") \
                       or line.startswith("Recommended") or line.startswith("Summary") else INK
            col = MUTED if line == "" else col
            col = AMBER if line.startswith("  •") else col
            doj.text((lx + 20, cly), line, font=font_sm, fill=(*col, a_j))
            cly += 34
        img = Image.alpha_composite(img.convert("RGBA"), ov_j).convert("RGB")

    # --- RIGHT: Email Notification ---
    rx = W // 2 + 40
    rw_panel = W // 2 - 80

    if t > 1.2:
        email_alpha = min(1.0, (t - 1.2) / 1.2)
        a_e = int(255 * email_alpha)
        ov_e = Image.new("RGBA", img.size, (0, 0, 0, 0))
        doe  = ImageDraw.Draw(ov_e)

        # Email panel (white-ish background like a real email client)
        doe.rounded_rectangle([rx, ly, rx + rw_panel, ly + 860],
                               radius=12, fill=(255, 255, 255, a_e), outline=(*LINE, a_e), width=1)
        # Email header
        doe.rounded_rectangle([rx, ly, rx + rw_panel, ly + 60], radius=12,
                               fill=(240, 245, 255, a_e))
        doe.rectangle([rx, ly + 44, rx + rw_panel, ly + 60], fill=(240, 245, 255, a_e))

        dark_ink = (15, 23, 42)
        dark_muted = (91, 107, 130)
        dark_accent = (59, 92, 204)
        dark_teal   = (15, 118, 110)
        dark_amber  = (180, 83, 9)

        doe.text((rx + 16, ly + 10), "Subject: [JiraPilot AI] NOVA-1001 Investigation Update",
                 font=font_sm, fill=(*dark_ink, a_e))
        doe.text((rx + 16, ly + 36), "To: engineering-team@nova.example.com", font=load_font(13),
                 fill=(*dark_muted, a_e))

        email_body = [
            ("Hi team,", dark_ink),
            ("", dark_ink),
            ("JiraPilot AI has completed the initial investigation", dark_ink),
            ("for NOVA-1001 — Payment service returning HTTP 503.", dark_ink),
            ("", dark_ink),
            ("SUMMARY", dark_accent),
            ("Issue: POST /api/payment/process → 503", dark_ink),
            ("Correlation: CORR-NOVA-8821", dark_ink),
            ("", dark_ink),
            ("KEY EVIDENCE", dark_teal),
            ("• Circuit breaker was HALF_OPEN at failure", dark_ink),
            ("• All 3 retries exhausted in under 3 seconds", dark_ink),
            ("• Payment gateway appears unavailable", dark_ink),
            ("", dark_ink),
            ("NEXT ACTIONS", dark_amber),
            ("1. Review gateway health at 08:13 UTC", dark_ink),
            ("2. Check circuit breaker configuration", dark_ink),
            ("3. Reproduce locally using:", dark_ink),
            ("   nova-payment-service (git clone ready)", dark_accent),
            ("", dark_ink),
            ("This is an AI-generated hypothesis, not a", dark_muted),
            ("confirmed root cause. Engineering judgment required.", dark_muted),
        ]
        ely = ly + 72
        for line, col in email_body:
            doe.text((rx + 20, ely), line, font=font_sm, fill=(*col, a_e))
            ely += 32
        img = Image.alpha_composite(img.convert("RGBA"), ov_e).convert("RGB")

    return np_frame(img)

# ---------------------------------------------------------------------------
# Scene 7: Unified Dashboard  (47–54 s)
# ---------------------------------------------------------------------------
def make_scene_07(t: float) -> np.ndarray:
    """
    JiraPilot AI dashboard — ticket status, evidence timeline,
    repo recommendations, next steps. Subtle parallax pull-back.
    """
    img = base_canvas()
    img = draw_glow_circle(img, W // 2, H // 2, 420, ACCENT, 0.10)
    draw = ImageDraw.Draw(img)

    font_title = load_font(38, bold=True)
    font_nav   = load_font(16)
    font_body  = load_font(18)
    font_sm    = load_font(14)
    font_mono  = load_mono_font(14)

    # Parallax: simulate slight pull-back (scale from 1.08 to 1.0)
    scale = max(1.0, 1.08 - 0.08 * min(1.0, t / 5.0))

    # Top bar
    draw.rectangle([(0, 0), (W, 52)], fill=SURFACE)
    draw.line([(0, 52), (W, 52)], fill=LINE, width=1)
    draw.text((20, 16), "JiraPilot AI", font=load_font(22, bold=True), fill=INK)
    nav_items = ["Dashboard", "Issues", "Logs", "Repositories", "Notifications", "Settings"]
    nx = 240
    for item in nav_items:
        active = item == "Dashboard"
        col = ACCENT if active else MUTED
        draw.text((nx, 18), item, font=font_nav, fill=col)
        if active:
            draw.rectangle([(nx - 2, 48), (nx + 76, 52)], fill=ACCENT)
        nx += 140

    # Sidebar
    draw.rectangle([(0, 52), (200, H)], fill=SURFACE)
    draw.line([(200, 52), (200, H)], fill=LINE, width=1)
    sidebar_items = [
        ("◉ Dashboard", True),
        ("⊞  Issues",   False),
        ("≡  Logs",     False),
        ("⎇  Repos",    False),
        ("✉  Notify",   False),
    ]
    sy = 80
    for label, active in sidebar_items:
        col = INK if active else MUTED
        bg  = (36, 48, 68) if active else None
        if bg:
            draw.rectangle([(0, sy - 4), (200, sy + 32)], fill=bg)
        draw.text((18, sy), label, font=font_sm, fill=col)
        sy += 52

    # Main content area
    content_x = 220
    draw.text((content_x, 70), "Incident Operations", font=font_title, fill=INK)
    draw.text((content_x, 118), "Ticket readiness, investigation progress and recommended next actions.",
              font=font_sm, fill=MUTED)

    # Metric cards
    metrics = [
        ("Total Issues",            "7",  None),
        ("Awaiting Info",           "2",  AMBER),
        ("Ready",                   "3",  TEAL),
        ("Investigations Running",  "1",  ACCENT),
        ("Completed",               "1",  TEAL),
    ]
    mc_x, mc_y = content_x, 148
    mc_w, mc_h = 278, 88
    for i, (label, value, col) in enumerate(metrics):
        mx = mc_x + i * (mc_w + 12)
        my = mc_y
        appear_t = i * 0.5
        if t < appear_t:
            continue
        card_alpha = min(1.0, (t - appear_t) / 0.5)
        a = int(255 * card_alpha)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dov = ImageDraw.Draw(ov)
        dov.rounded_rectangle([mx, my, mx + mc_w, my + mc_h], radius=10,
                               fill=(*SURFACE, a), outline=(*LINE, a), width=1)
        dov.text((mx + 14, my + 14), label, font=font_sm, fill=(*MUTED, a))
        val_col = col or INK
        dov.text((mx + 14, my + 40), value, font=load_font(36, bold=True), fill=(*val_col, a))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    # Investigation timeline (left panel)
    if t > 2.5:
        tl_alpha = min(1.0, (t - 2.5) / 1.0)
        a_tl = int(255 * tl_alpha)
        tl_x, tl_y, tl_w, tl_h = content_x, 258, 520, 380
        ov_tl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dtl   = ImageDraw.Draw(ov_tl)
        dtl.rounded_rectangle([tl_x, tl_y, tl_x + tl_w, tl_y + tl_h], radius=10,
                               fill=(*SURFACE, a_tl), outline=(*LINE, a_tl), width=1)
        dtl.text((tl_x + 16, tl_y + 14), "Investigation Activity", font=font_body, fill=(*INK, a_tl))
        events = [
            ("NOVA-1001", "Ticket validation passed",            "08:15 UTC", TEAL),
            ("NOVA-1001", "Log analysis started",                "08:16 UTC", ACCENT),
            ("NOVA-1001", "Endpoint POST /api/payment detected", "08:16 UTC", ACCENT),
            ("NOVA-1001", "Repository matched: nova-payment-svc","08:17 UTC", TEAL),
            ("NOVA-1001", "Investigation report generated",       "08:18 UTC", TEAL),
            ("NOVA-1002", "Awaiting diagnostic information",      "09:01 UTC", AMBER),
        ]
        ev_y = tl_y + 52
        for key, desc, ts, col in events:
            dtl.text((tl_x + 16, ev_y), key, font=font_mono, fill=(*col, a_tl))
            dtl.text((tl_x + 130, ev_y), desc, font=font_sm, fill=(*INK, a_tl))
            dtl.text((tl_x + tl_w - 90, ev_y), ts, font=font_sm, fill=(*MUTED, a_tl))
            ev_y += 44
        img = Image.alpha_composite(img.convert("RGBA"), ov_tl).convert("RGB")

    # API errors panel (middle)
    if t > 3.2:
        ae_alpha = min(1.0, (t - 3.2) / 1.0)
        a_ae = int(255 * ae_alpha)
        ae_x, ae_y, ae_w, ae_h = content_x + 540, 258, 380, 380
        ov_ae = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dae   = ImageDraw.Draw(ov_ae)
        dae.rounded_rectangle([ae_x, ae_y, ae_x + ae_w, ae_y + ae_h], radius=10,
                               fill=(*SURFACE, a_ae), outline=(*LINE, a_ae), width=1)
        dae.text((ae_x + 16, ae_y + 14), "API Errors", font=font_body, fill=(*INK, a_ae))
        api_errs = [
            ("POST /api/payment/process", "503", "NOVA-1001"),
            ("GET  /api/cart/summary",    "504", "NOVA-1002"),
            ("POST /api/auth/token",      "401", "NOVA-1003"),
        ]
        ery = ae_y + 52
        for ep, code, key in api_errs:
            col = DANGER if code.startswith("5") else AMBER
            dae.text((ae_x + 14, ery),       ep,   font=font_mono, fill=(*TEAL, a_ae))
            dae.text((ae_x + 14, ery + 22),  f"HTTP {code} · {key}", font=font_sm, fill=(*col, a_ae))
            ery += 72
        img = Image.alpha_composite(img.convert("RGBA"), ov_ae).convert("RGB")

    # Repo recommendations (right)
    if t > 3.8:
        rr_alpha = min(1.0, (t - 3.8) / 1.0)
        a_rr = int(255 * rr_alpha)
        rr_x, rr_y, rr_w, rr_h = content_x + 940, 258, 780, 380
        ov_rr = Image.new("RGBA", img.size, (0, 0, 0, 0))
        drr   = ImageDraw.Draw(ov_rr)
        drr.rounded_rectangle([rr_x, rr_y, rr_x + rr_w, rr_y + rr_h], radius=10,
                               fill=(*SURFACE, a_rr), outline=(*LINE, a_rr), width=1)
        drr.text((rr_x + 16, rr_y + 14), "Repository Recommendations", font=font_body, fill=(*INK, a_rr))
        repos = [
            ("nova-payment-service",   "NOVA-1001", "POST /api/payment/process"),
            ("nova-cart-service",      "NOVA-1002", "GET /api/cart/summary"),
            ("nova-auth-service",      "NOVA-1003", "POST /api/auth/token"),
        ]
        rry = rr_y + 52
        for repo, key, ep in repos:
            drr.rounded_rectangle([rr_x + 12, rry, rr_x + rr_w - 12, rry + 72],
                                   radius=8, fill=(*LINE, a_rr // 3), outline=(*LINE, a_rr // 2), width=1)
            drr.text((rr_x + 24, rry + 12), repo, font=font_body, fill=(*INK, a_rr))
            drr.text((rr_x + 24, rry + 40), f"{key}  ·  {ep}", font=font_sm, fill=(*MUTED, a_rr))
            rry += 88
        img = Image.alpha_composite(img.convert("RGBA"), ov_rr).convert("RGB")

    # Caption
    cap_alpha = min(1.0, t / 1.5)
    ov_cap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(ov_cap)
    cap = "One workspace. A clearer investigation."
    font_cap = load_font(34, bold=True)
    bbox_cap = dc.textbbox((0, 0), cap, font=font_cap)
    wc = bbox_cap[2] - bbox_cap[0]
    dc.text(((W - wc) // 2, H - 80), cap, font=font_cap, fill=(*INK, int(255 * cap_alpha)))
    img = Image.alpha_composite(img.convert("RGBA"), ov_cap).convert("RGB")

    return np_frame(img)

# ---------------------------------------------------------------------------
# Scene 8: Closing Brand Reveal  (54–60 s)
# ---------------------------------------------------------------------------
def make_scene_08(t: float) -> np.ndarray:
    """
    Fade in on black. Logo + copper glow + light sweep.
    Headline + tagline. Clean quiet finish.
    """
    img = base_canvas()

    scene_t = t  # 0–6

    # Fade in from black
    fade_in = min(1.0, scene_t / 1.5)

    # Copper glow grows
    glow_r = int(200 + 100 * min(1.0, scene_t / 3.0))
    img = draw_glow_circle(img, W // 2, H // 2, glow_r, COPPER, 0.28 * fade_in)

    # Light sweep (horizontal streak at 2.2s)
    if scene_t > 2.2:
        sweep_prog = min(1.0, (scene_t - 2.2) / 0.8)
        sweep_x = int(-200 + (W + 400) * sweep_prog)
        sweep_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ds = ImageDraw.Draw(sweep_img)
        for dx in range(-40, 41):
            fade = 1 - abs(dx) / 40
            a_s = int(140 * fade * fade_in)
            ds.line([(sweep_x + dx, 0), (sweep_x + dx, H)],
                     fill=(*COPPER_S, a_s), width=1)
        sweep_img = sweep_img.filter(ImageFilter.GaussianBlur(8))
        img = Image.alpha_composite(img.convert("RGBA"), sweep_img).convert("RGB")

    # Logo
    if scene_t > 0.5:
        logo_alpha = min(1.0, (scene_t - 0.5) / 1.5)
        a_l = int(255 * logo_alpha)
        ov_logo = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dol = ImageDraw.Draw(ov_logo)
        font_logo = load_font(88, bold=True)
        logo_text = "JiraPilot AI"
        bbox_l = dol.textbbox((0, 0), logo_text, font=font_logo)
        lw = bbox_l[2] - bbox_l[0]
        # Copper accent in "AI"
        prefix = "JiraPilot "
        bbox_p = dol.textbbox((0, 0), prefix, font=font_logo)
        pw = bbox_p[2] - bbox_p[0]
        dol.text(((W - lw) // 2, H // 2 - 120), prefix, font=font_logo, fill=(*INK, a_l))
        dol.text(((W - lw) // 2 + pw, H // 2 - 120), "AI", font=font_logo, fill=(*COPPER_S, a_l))
        img = Image.alpha_composite(img.convert("RGBA"), ov_logo).convert("RGB")

    # Copper underline bar
    if scene_t > 1.8:
        bar_alpha = min(1.0, (scene_t - 1.8) / 0.8)
        bar_w = int(280 * bar_alpha)
        draw = ImageDraw.Draw(img)
        bx = (W - bar_w) // 2
        draw.rectangle([(bx, H // 2 - 10), (bx + bar_w, H // 2 - 4)], fill=COPPER)

    # Main headline
    if scene_t > 2.0:
        hl_alpha = min(1.0, (scene_t - 2.0) / 1.2)
        a_hl = int(255 * hl_alpha)
        font_hl = load_font(56, bold=True)
        headline = "Less repetitive triage. More time to solve."
        ov_hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dh = ImageDraw.Draw(ov_hl)
        bbox_hl = dh.textbbox((0, 0), headline, font=font_hl)
        hlw = bbox_hl[2] - bbox_hl[0]
        dh.text(((W - hlw) // 2, H // 2 + 20), headline, font=font_hl, fill=(*INK, a_hl))
        img = Image.alpha_composite(img.convert("RGBA"), ov_hl).convert("RGB")

    # Supporting line
    if scene_t > 3.0:
        sl_alpha = min(1.0, (scene_t - 3.0) / 1.0)
        a_sl = int(255 * sl_alpha)
        font_sl = load_font(30)
        sl_text = "JiraPilot AI  —  Your investigation copilot."
        ov_sl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ds2 = ImageDraw.Draw(ov_sl)
        bbox_sl = ds2.textbbox((0, 0), sl_text, font=font_sl)
        slw = bbox_sl[2] - bbox_sl[0]
        ds2.text(((W - slw) // 2, H // 2 + 100), sl_text, font=font_sl, fill=(*MUTED, a_sl))
        img = Image.alpha_composite(img.convert("RGBA"), ov_sl).convert("RGB")

    # Fade out at the very end
    if scene_t > 5.0:
        fade_out = min(1.0, (scene_t - 5.0) / 1.0)
        black_a = int(255 * fade_out)
        bl_ov = Image.new("RGBA", img.size, (0, 0, 0, black_a))
        img = Image.alpha_composite(img.convert("RGBA"), bl_ov).convert("RGB")

    return np_frame(img)

# ---------------------------------------------------------------------------
# Scene router
# ---------------------------------------------------------------------------
SCENES = [
    # (start_s, end_s, maker_fn, local_t_offset)
    (0,  5,  make_scene_01),
    (5,  12, make_scene_02),
    (12, 20, make_scene_03),
    (20, 30, make_scene_04),
    (30, 38, make_scene_05),
    (38, 47, make_scene_06),
    (47, 54, make_scene_07),
    (54, 60, make_scene_08),
]

def get_frame(t: float) -> np.ndarray:
    for start, end, fn in SCENES:
        if start <= t < end:
            return fn(t - start)
    # Last frame
    return make_scene_08(6.0)

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def render():
    if not MOVIEPY_OK:
        print("[ERROR] moviepy is not available. Install it and re-run.")
        return

    print("=" * 60)
    print("JiraPilot AI — 60-Second Product Video Renderer")
    print("=" * 60)
    print(f"Output resolution: {W}×{H}  |  FPS: {FPS}  |  Duration: {DURATION}s")
    print(f"Output directory:  {OUT_DIR}")
    print()

    # Render individual scenes
    for idx, (start, end, fn) in enumerate(SCENES, 1):
        scene_dur = end - start
        print(f"[{idx}/8] Rendering Scene {idx:02d}  ({start}s–{end}s, {scene_dur}s)…")

        clip = VideoClip(lambda t, fn=fn: fn(t), duration=scene_dur)
        clip = clip.set_fps(FPS)
        out_path = os.path.join(SCENE_DIR, f"scene_{idx:02d}.mp4")
        clip.write_videofile(out_path, fps=FPS, codec="libx264",
                              preset="medium", audio=False,
                              logger=None)
        print(f"    → {out_path}")

    # Concatenate full video
    print("\n[●] Concatenating all scenes…")
    from moviepy.editor import concatenate_videoclips
    scene_clips = []
    for idx, (start, end, fn) in enumerate(SCENES, 1):
        scene_dur = end - start
        clip = VideoClip(lambda t, fn=fn: fn(t), duration=scene_dur)
        clip = clip.set_fps(FPS)
        scene_clips.append(clip)

    full_clip = concatenate_videoclips(scene_clips, method="compose")

    # Video-only version (no audio)
    noaudio_path = os.path.join(OUT_DIR, "jirapilot_60s_noaudio.mp4")
    print(f"[●] Writing video-only: {noaudio_path}")
    full_clip.write_videofile(noaudio_path, fps=FPS, codec="libx264",
                               preset="medium", audio=False, logger=None)

    print(f"\n{'=' * 60}")
    print("All renders complete.")
    print(f"  Video-only:  {noaudio_path}")
    print()
    print("Next steps:")
    print("  1. Add voice-over and music track in your DAW / video editor.")
    print("  2. Burn captions:  ffmpeg -i jirapilot_60s_noaudio.mp4 \\")
    print("       -vf subtitles=captions/jirapilot_captions.srt \\")
    print("       jirapilot_60s_captioned.mp4")
    print("  3. Mix with audio:  ffmpeg -i jirapilot_60s_noaudio.mp4 \\")
    print("       -i voiceover.wav -i ambient_music.wav \\")
    print("       -filter_complex '[1:a]volume=1.0[vo];[2:a]volume=0.35[mu];[vo][mu]amix=2[out]' \\")
    print("       -map 0:v -map '[out]' jirapilot_60s_final.mp4")
    print("=" * 60)

if __name__ == "__main__":
    render()
