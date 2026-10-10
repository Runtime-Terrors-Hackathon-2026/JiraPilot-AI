"""
JiraPilot AI -- Enhanced 60-Second Hackathon Presentation Video
Output: presentation/JiraPilot-AI-Presentation-Video.mp4
Duration: Exactly 60.00 seconds (1800 frames @ 30fps)
Resolution: 1920x1080 (16:9)
Style: Deep purple / near-black enterprise SaaS film
       -- Animated workflow cards, glowing UI panels, typewriter text,
          concentric violet ring reveals, floating particles, smooth fades
Audio: TTS voiceover (Zira) + ambient electronic music bed
"""

import os, sys, math, wave, struct, subprocess, random, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR     = os.path.join(BASE_DIR, "assets", "images")
VO_DIR      = os.path.join(BASE_DIR, "assets", "voiceover")
SRC_DIR     = os.path.join(BASE_DIR, "source")
OUT_MP4     = os.path.join(BASE_DIR, "JiraPilot-AI-Presentation-Video.mp4")
SCRATCH_DIR = os.path.join(BASE_DIR, "assets", "video", "enhanced_scratch")
for d in [IMG_DIR, VO_DIR, SCRATCH_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Config ─────────────────────────────────────────────────────────────────
W, H   = 1920, 1080
FPS    = 30
TOTAL  = 1800   # frames
TOTAL_FRAMES   = TOTAL
TOTAL_DURATION = TOTAL / FPS   # 60.0 seconds

# ── Color Palette ──────────────────────────────────────────────────────────
BG        = (8,   7,  13)       # #08070D near-black
PURPLE    = (23,  11,  43)      # #170B2B deep purple
SURFACE   = (28,  20,  50)      # card surface
SURFACE2  = (38,  28,  68)      # lighter card
LINE      = (55,  42,  85)      # border
VIOLET    = (139, 92, 246)      # #8B5CF6 primary glow
LAV       = (196,181, 253)      # #C4B5FD lavender
WHITE     = (255,255, 255)
MUTED     = (184,179, 199)      # #B8B3C7
TEAL      = ( 45,212, 191)      # success
AMBER     = (251,191,  36)      # warning
DANGER    = (248,113, 113)      # error
INDIGO    = ( 99,102, 241)      # accent

# ── Easing ────────────────────────────────────────────────────────────────
def ease_out(t):
    return 1 - (1-t)**3

def ease_in_out(t):
    return t*t*(3-2*t)

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def lerp(a, b, t):
    return a + (b-a)*t

def fade_val(frame, start, end):
    """Return 0..1 progress within [start,end] frames"""
    if frame < start: return 0.0
    if frame >= end:  return 1.0
    return (frame-start)/(end-start)

# ── Font helper ───────────────────────────────────────────────────────────
def fnt(size, bold=False, mono=False):
    try:
        if mono:
            p = "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"
        else:
            p = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()

# ── Drawing helpers ────────────────────────────────────────────────────────
def blend_color(c, alpha, bg=BG):
    return tuple(int(bg[i] + (c[i]-bg[i])*alpha) for i in range(3))

def glow_circle(draw, cx, cy, r, color, alpha, width=2, glow_layers=4):
    for i in range(glow_layers, 0, -1):
        a = alpha * (0.15 * i / glow_layers)
        rr = r + (glow_layers - i) * 3
        col = blend_color(color, a)
        draw.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], outline=col, width=width+i)
    a_final = alpha * 0.9
    col = blend_color(color, a_final)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=col, width=width)

def draw_rounded_rect(draw, x1,y1,x2,y2, radius=12, fill=None, outline=None, width=1):
    if fill:
        draw.rounded_rectangle([x1,y1,x2,y2], radius=radius, fill=fill)
    if outline:
        draw.rounded_rectangle([x1,y1,x2,y2], radius=radius, outline=outline, width=width)

def draw_text_centered(draw, text, cx, cy, font, color):
    bb = draw.textbbox((0,0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx - tw//2, cy - th//2), text, font=font, fill=color)

def typewriter(draw, text, cx, cy, font, color, progress):
    n = max(1, int(len(text)*progress))
    partial = text[:n]
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    draw.text((cx - tw//2, cy), partial, font=font, fill=color)

def draw_badge(draw, x, y, text, color, size=18):
    f = fnt(size, bold=True)
    bb = draw.textbbox((0,0), text, font=f)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    pad = 10
    bg_col = tuple(int(c*0.25) for c in color)
    draw_rounded_rect(draw, x, y, x+tw+pad*2, y+th+pad*2-4, radius=8,
                      fill=bg_col, outline=color, width=1)
    draw.text((x+pad, y+pad-2), text, font=f, fill=color)
    return tw + pad*2

def particles_field(draw, frame, count=60, color=VIOLET, alpha_base=0.4):
    rng = random.Random(42)
    for _ in range(count):
        sx = rng.randint(0, W)
        sy = rng.randint(0, H)
        speed = rng.uniform(0.3, 1.2)
        offset = rng.uniform(0, math.pi*2)
        y = (sy + frame * speed) % H
        phase = math.sin(frame * 0.03 + offset)
        a = alpha_base * (0.4 + 0.6 * abs(phase))
        col = blend_color(color, a)
        r = rng.randint(1, 3)
        draw.ellipse([sx-r, y-r, sx+r, y+r], fill=col)

def concentric_rings(draw, cx, cy, frame, color=VIOLET, rings=6, base_r=80, spacing=70, alpha_base=0.6):
    for i in range(rings):
        phase = (frame * 0.015 + i * 0.4) % (math.pi * 2)
        pulse = 0.5 + 0.5 * math.sin(phase)
        r = base_r + i * spacing
        a = alpha_base * (0.2 + 0.8 * (1 - i/rings)) * pulse
        glow_circle(draw, cx, cy, r, color, a, width=1 if i>1 else 2, glow_layers=3)

def draw_logo_icon(draw, cx, cy, size, alpha=1.0):
    """Geometric delta-wing flight emblem"""
    s = size
    # Outer orbit ring
    col_ring = blend_color(LAV, alpha * 0.7)
    draw.ellipse([cx-s, cy-s, cx+s, cy+s], outline=col_ring, width=2)
    # Inner delta wings
    col_body = blend_color(VIOLET, alpha)
    col_glow = blend_color(LAV, alpha * 0.9)
    pts_left  = [cx-s*0.6, cy+s*0.4,  cx, cy-s*0.55,  cx, cy+s*0.1]
    pts_right = [cx+s*0.6, cy+s*0.4,  cx, cy-s*0.55,  cx, cy+s*0.1]
    draw.polygon([(p) for p in zip(pts_left[::2], pts_left[1::2])],  fill=col_body)
    draw.polygon([(p) for p in zip(pts_right[::2], pts_right[1::2])], fill=col_glow)
    # Core dot
    cr = max(3, s//8)
    draw.ellipse([cx-cr, cy-cr-int(s*0.1), cx+cr, cy+cr-int(s*0.1)], fill=blend_color(WHITE, alpha))

# ── Background ─────────────────────────────────────────────────────────────
def make_base_bg(frame, style="dark"):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # Radial gradient: deep purple center
    cx, cy = W//2, H//2
    for r in range(600, 0, -20):
        t = 1 - r/600
        col = (
            int(BG[0] + (PURPLE[0]-BG[0])*t*0.7),
            int(BG[1] + (PURPLE[1]-BG[1])*t*0.7),
            int(BG[2] + (PURPLE[2]-BG[2])*t*0.7),
        )
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    return img, draw

# ═══════════════════════════════════════════════════════════════════════════
# SCENE RENDERERS
# Each returns a PIL Image for one frame.
# ═══════════════════════════════════════════════════════════════════════════

# Scene 1: 0-150 (0-5s) — THE PROBLEM (darkness, particles, opening line)
def scene_01(f):
    img, draw = make_base_bg(f)
    # Animate bg: start very dark, brighten a bit
    p = fade_val(f, 0, 150)
    particles_field(draw, f, count=40, color=VIOLET, alpha_base=0.25*p)
    # Floating log fragments
    rng = random.Random(7)
    log_lines = [
        "[ERROR] 503 Service Unavailable — POST /api/v1/resources/allocate",
        "CorrelationID: CORR-DEMO-1001  |  timestamp: 2024-10-10T02:41:18Z",
        "[WARN]  Upstream timeout after 30000ms — retry 3/3",
        "java.lang.NullPointerException at ResourceController.java:142",
        "[INFO]  Request queued — worker pool saturated (queue depth: 512)",
    ]
    f_log = fnt(18, mono=True)
    for i, line in enumerate(log_lines):
        base_y = 150 + i * 90
        drift_y = base_y + math.sin(f*0.02 + i) * 8
        a = clamp((p - 0.1*i) * 0.35, 0, 0.35)
        col = blend_color(MUTED, a)
        bb = draw.textbbox((0,0), line, font=f_log)
        draw.text((W//2 - (bb[2]-bb[0])//2, int(drift_y)), line, font=f_log, fill=col)

    # Main text fade in at frame 30
    f_title = fnt(58, bold=True)
    f_sub   = fnt(28)
    txt_p   = clamp(fade_val(f, 30, 90), 0, 1)
    col_t   = blend_color(WHITE, txt_p)
    col_s   = blend_color(MUTED, txt_p * 0.8)
    draw_text_centered(draw, "Every incident starts with a question.", W//2, H//2-30, f_title, col_t)
    draw_text_centered(draw, "Where do we begin?", W//2, H//2+55, f_sub, col_s)
    return img

# Scene 2: 150-360 (5-12s) — LOGO REVEAL + JIRA TICKET
def scene_02(f):
    lf = f - 150
    img, draw = make_base_bg(f)
    particles_field(draw, f, count=30, color=VIOLET, alpha_base=0.15)

    total = 210
    p_logo = clamp(ease_out(fade_val(lf, 0, 60)), 0, 1)
    p_card = clamp(ease_out(fade_val(lf, 50, 130)), 0, 1)
    p_text = clamp(fade_val(lf, 100, 160), 0, 1)

    # Logo reveal (top-center area)
    logo_cx, logo_cy = W//2, 200
    concentric_rings(draw, logo_cx, logo_cy, lf, rings=4, base_r=60, spacing=50, alpha_base=0.5*p_logo)
    draw_logo_icon(draw, logo_cx, logo_cy, size=48, alpha=p_logo)
    f_brand = fnt(36, bold=True)
    f_tag   = fnt(20)
    col_b   = blend_color(WHITE, p_logo)
    col_tg  = blend_color(LAV, p_logo * 0.8)
    draw_text_centered(draw, "JiraPilot AI", W//2, 270, f_brand, col_b)
    draw_text_centered(draw, "Your investigation copilot.", W//2, 312, f_tag, col_tg)

    # Jira ticket card sliding in from right
    card_w, card_h = 780, 370
    card_x = int(lerp(W, W//2 - card_w//2, p_card))
    card_y = 340

    if p_card > 0:
        draw_rounded_rect(draw, card_x, card_y, card_x+card_w, card_y+card_h,
                          radius=14, fill=SURFACE, outline=VIOLET, width=1)
        # Header bar
        draw_rounded_rect(draw, card_x, card_y, card_x+card_w, card_y+52,
                          radius=14, fill=SURFACE2)
        draw_rounded_rect(draw, card_x, card_y+38, card_x+card_w, card_y+52,
                          radius=0, fill=SURFACE2)

        f_key  = fnt(18, bold=True, mono=True)
        f_sum  = fnt(22, bold=True)
        f_meta = fnt(17)
        f_lbl  = fnt(15)

        col_c = blend_color(WHITE, p_card)
        col_m = blend_color(MUTED, p_card)
        col_v = blend_color(VIOLET, p_card)
        col_a = blend_color(AMBER, p_card)

        # Key badge
        draw.text((card_x+16, card_y+14), "NOVA-1001", font=f_key, fill=blend_color(LAV, p_card))
        # Status badge
        draw_badge(draw, card_x+160, card_y+12, "In Progress", AMBER)
        draw_badge(draw, card_x+310, card_y+12, "Priority: High", DANGER)
        # Summary
        draw.text((card_x+16, card_y+62), "Resource allocation API returning 503 errors", font=f_sum, fill=col_c)
        # Meta rows
        meta = [
            ("Reporter",     "Northstar Digital Systems"),
            ("Environment",  "Production — us-east-1"),
            ("Endpoint",     "POST /api/v1/resources/allocate"),
            ("Correlation",  "CORR-DEMO-1001"),
            ("Logs Attached","Yes — 48 lines captured"),
        ]
        for i, (label, val) in enumerate(meta):
            row_y = card_y + 108 + i * 42
            draw.text((card_x+16,  row_y), label+":", font=f_lbl, fill=col_m)
            draw.text((card_x+170, row_y), val,       font=f_meta, fill=col_c)

    # Caption text
    f_cap = fnt(32, bold=True)
    f_sub = fnt(22)
    col_cap = blend_color(WHITE, p_text)
    col_sub = blend_color(LAV, p_text * 0.85)
    draw_text_centered(draw, "A new Jira issue. A clearer path forward.", W//2, 756, f_cap, col_cap)
    return img

# Scene 3: 360-600 (12-20s) — TICKET READINESS VALIDATION
def scene_03(f):
    lf = f - 360
    img, draw = make_base_bg(f)
    particles_field(draw, f, count=20, color=VIOLET, alpha_base=0.1)

    p_in   = clamp(ease_out(fade_val(lf, 0, 40)), 0, 1)
    p_text = clamp(fade_val(lf, 150, 210), 0, 1)

    # Left panel: readiness checklist
    panel_x, panel_y = 90, 130
    panel_w, panel_h = 700, 470

    draw_rounded_rect(draw, panel_x, panel_y, panel_x+panel_w, panel_y+panel_h,
                      radius=16, fill=SURFACE, outline=LINE, width=1)
    # Panel title
    f_ptitle = fnt(20, bold=True)
    f_item   = fnt(18)
    f_badge  = fnt(15, bold=True)
    col_p = blend_color(WHITE, p_in)
    col_m = blend_color(MUTED, p_in)

    draw.text((panel_x+20, panel_y+18), "Ticket Readiness Check", font=f_ptitle, fill=blend_color(LAV, p_in))
    draw.text((panel_x+20, panel_y+50), "NOVA-1001", font=fnt(16, bold=True, mono=True), fill=blend_color(VIOLET, p_in))

    # Divider
    draw.line([(panel_x+10, panel_y+75), (panel_x+panel_w-10, panel_y+75)], fill=LINE, width=1)

    # Checklist items with animated reveal
    items = [
        ("Summary",          True,  "Resource allocation API 503 errors"),
        ("Environment",      True,  "Production — us-east-1"),
        ("API Endpoint",     True,  "POST /api/v1/resources/allocate"),
        ("Expected Behavior",True,  "HTTP 200 with allocated resources"),
        ("Actual Behavior",  True,  "HTTP 503 — Service Unavailable"),
        ("Error Logs",       True,  "48 lines captured"),
        ("Steps to Reproduce",False,"Missing — required for analysis"),
        ("Correlation ID",   True,  "CORR-DEMO-1001"),
    ]
    for i, (label, ok, detail) in enumerate(items):
        item_p = clamp(ease_out(fade_val(lf, 10+i*10, 50+i*10)), 0, 1)
        row_y = panel_y + 95 + i * 46
        # Icon
        icon_col = TEAL if ok else AMBER
        icon_txt  = "[OK]" if ok else "[!]"
        col_ic = blend_color(icon_col, item_p)
        draw.text((panel_x+18, row_y), icon_txt, font=fnt(16, bold=True, mono=True), fill=col_ic)
        # Label
        draw.text((panel_x+68, row_y), label+":", font=fnt(17, bold=True), fill=blend_color(WHITE, item_p))
        # Detail
        draw.text((panel_x+68, row_y+20), detail, font=fnt(15), fill=blend_color(MUTED if ok else AMBER, item_p * 0.8))

    # Right panel: readiness score
    right_x, right_y = 840, 130
    right_w, right_h = 550, 220
    draw_rounded_rect(draw, right_x, right_y, right_x+right_w, right_y+right_h,
                      radius=16, fill=SURFACE, outline=VIOLET, width=1)

    score_p = clamp(ease_out(fade_val(lf, 60, 120)), 0, 1)
    f_score = fnt(80, bold=True)
    f_slbl  = fnt(20)
    col_sc = blend_color(TEAL, score_p)
    draw_text_centered(draw, "87%", right_x+right_w//2, right_y+90, f_score, col_sc)
    draw_text_centered(draw, "Readiness Score", right_x+right_w//2, right_y+165, f_slbl, blend_color(MUTED, score_p))

    # Score progress bar
    bar_x = right_x+30
    bar_y = right_y + 180
    bar_w = right_w - 60
    draw_rounded_rect(draw, bar_x, bar_y, bar_x+bar_w, bar_y+12, radius=6, fill=LINE)
    fill_w = int(bar_w * 0.87 * score_p)
    if fill_w > 0:
        draw_rounded_rect(draw, bar_x, bar_y, bar_x+fill_w, bar_y+12, radius=6, fill=TEAL)

    # Right panel 2: Missing fields action
    act_y = right_y + 240
    act_h = 210
    draw_rounded_rect(draw, right_x, act_y, right_x+right_w, act_y+act_h,
                      radius=16, fill=SURFACE, outline=AMBER, width=1)
    act_p = clamp(ease_out(fade_val(lf, 100, 160)), 0, 1)
    draw.text((right_x+20, act_y+18), "Action Required", font=fnt(18, bold=True), fill=blend_color(AMBER, act_p))
    draw.text((right_x+20, act_y+50), "1 field needs attention:", font=fnt(16), fill=blend_color(MUTED, act_p))
    draw.text((right_x+20, act_y+78), "  Steps to Reproduce — not provided", font=fnt(16, mono=True), fill=blend_color(AMBER, act_p))
    draw.text((right_x+20, act_y+116), "JiraPilot AI will post a comment", font=fnt(16), fill=blend_color(MUTED, act_p))
    draw.text((right_x+20, act_y+138), "requesting this information from the", font=fnt(16), fill=blend_color(MUTED, act_p))
    draw.text((right_x+20, act_y+160), "reporter automatically.", font=fnt(16), fill=blend_color(MUTED, act_p))

    # Bottom caption
    f_cap = fnt(30, bold=True)
    col_cap = blend_color(WHITE, p_text)
    draw_text_centered(draw, "Validate. Identify gaps. Request the right details.", W//2, 920, f_cap, col_cap)
    return img

# Scene 4: 600-900 (20-30s) — LOG ANALYSIS
def scene_04(f):
    lf = f - 600
    img, draw = make_base_bg(f)
    particles_field(draw, f, count=15, color=TEAL, alpha_base=0.08)

    p_panel = clamp(ease_out(fade_val(lf, 0, 50)), 0, 1)
    p_text  = clamp(fade_val(lf, 220, 280), 0, 1)

    # Log viewer panel
    lv_x, lv_y = 60, 110
    lv_w, lv_h = 1050, 520
    draw_rounded_rect(draw, lv_x, lv_y, lv_x+lv_w, lv_y+lv_h,
                      radius=16, fill=(12,10,22), outline=LINE, width=1)
    # Header bar
    draw_rounded_rect(draw, lv_x, lv_y, lv_x+lv_w, lv_y+48,
                      radius=16, fill=SURFACE)
    draw_rounded_rect(draw, lv_x, lv_y+35, lv_x+lv_w, lv_y+48, radius=0, fill=SURFACE)
    draw.text((lv_x+16, lv_y+13), "Log Viewer — NOVA-1001", font=fnt(18, bold=True), fill=blend_color(LAV, p_panel))
    draw.text((lv_x+lv_w-160, lv_y+13), "48 lines | LIVE", font=fnt(16), fill=blend_color(TEAL, p_panel))

    # Log lines with color coding and animated reveal
    log_entries = [
        ("02:41:10", "INFO",  "Service health check OK — all 8 workers responsive", MUTED,   False),
        ("02:41:15", "INFO",  "Incoming request: POST /api/v1/resources/allocate",   MUTED,   True ),
        ("02:41:15", "INFO",  "CorrelationID: CORR-DEMO-1001  |  userID: svc-north", VIOLET,  True ),
        ("02:41:17", "WARN",  "Worker pool nearing capacity: 498/512 slots used",    AMBER,   False),
        ("02:41:18", "ERROR", "Upstream timeout: resource-db.internal:5432 30000ms", DANGER,  True ),
        ("02:41:18", "ERROR", "HTTP 503 Service Unavailable — POST /api/v1/resources/allocate", DANGER, True),
        ("02:41:18", "ERROR", "Retry 1/3 failed — circuit breaker OPEN",              DANGER,  False),
        ("02:41:19", "ERROR", "Retry 2/3 failed — circuit breaker OPEN",              DANGER,  False),
        ("02:41:19", "ERROR", "Retry 3/3 failed — circuit breaker OPEN",              DANGER,  False),
        ("02:41:19", "INFO",  "Request terminated. Response: 503. Elapsed: 31041ms",  MUTED,   True ),
    ]
    f_mono_sm = fnt(15, mono=True)
    for i, (ts, level, msg, col, highlight) in enumerate(log_entries):
        line_p = clamp(ease_out(fade_val(lf, 20 + i*15, 60 + i*15)), 0, 1)
        row_y = lv_y + 58 + i*46
        # Highlight background
        if highlight and line_p > 0:
            bg_col = tuple(int(c*0.18) for c in col)
            draw.rectangle([lv_x+4, row_y-4, lv_x+lv_w-4, row_y+38], fill=bg_col)
        draw.text((lv_x+14, row_y+5), ts, font=f_mono_sm, fill=blend_color(MUTED, line_p*0.7))
        lv_col = {"INFO": TEAL, "WARN": AMBER, "ERROR": DANGER}.get(level, MUTED)
        draw.text((lv_x+110, row_y+5), f"[{level:<5}]", font=f_mono_sm, fill=blend_color(lv_col, line_p))
        draw.text((lv_x+210, row_y+5), msg[:72], font=f_mono_sm, fill=blend_color(col, line_p))

    # AI Analysis panel (right side)
    ai_x, ai_y = 1140, 110
    ai_w, ai_h = 720, 520
    draw_rounded_rect(draw, ai_x, ai_y, ai_x+ai_w, ai_y+ai_h,
                      radius=16, fill=SURFACE, outline=VIOLET, width=1)
    ai_p = clamp(ease_out(fade_val(lf, 80, 140)), 0, 1)
    draw.text((ai_x+20, ai_y+16), "AI Analysis", font=fnt(20, bold=True), fill=blend_color(LAV, ai_p))
    draw.line([(ai_x+10, ai_y+52), (ai_x+ai_w-10, ai_y+52)], fill=LINE, width=1)

    ai_sections = [
        ("Observed Facts", TEAL, [
            "HTTP 503 on POST /api/v1/resources/allocate",
            "All 3 retries failed — circuit breaker tripped",
            "DB timeout: resource-db.internal:5432 (30s)",
            "Worker pool: 498/512 slots at time of failure",
        ]),
        ("Probable Cause", AMBER, [
            "Database connection pool exhaustion leading",
            "to cascading upstream service timeout",
            "(Hypothesis — not yet verified)",
        ]),
        ("Suggested Next Step", VIOLET, [
            "Clone resource-inventory-service repository",
            "Check DB pool config & connection limits",
        ]),
    ]
    row = ai_y + 64
    for title, col, lines in ai_sections:
        sect_p = clamp(ease_out(fade_val(lf, 100, 180)), 0, 1)
        draw.text((ai_x+20, row), title, font=fnt(16, bold=True), fill=blend_color(col, sect_p))
        row += 24
        for line in lines:
            draw.text((ai_x+30, row), line, font=fnt(15), fill=blend_color(MUTED, sect_p*0.9))
            row += 22
        row += 14

    # Connecting animated lines from log highlights to AI panel
    conn_p = clamp(ease_out(fade_val(lf, 150, 220)), 0, 1)
    if conn_p > 0:
        # Lines from error entries to AI panel
        for i, (ey, col) in enumerate([(lv_y+286, DANGER), (lv_y+330, DANGER), (lv_y+420, TEAL)]):
            x1 = lv_x + lv_w
            x2 = ai_x
            xm = (x1+x2)//2
            col_c = blend_color(col, conn_p * 0.5)
            ey2 = ai_y + 100 + i * 40
            # Bezier-like with 3 line segments
            draw.line([(x1, ey), (xm, ey)], fill=col_c, width=1)
            draw.line([(xm, ey), (xm, ey2)], fill=col_c, width=1)
            draw.line([(xm, ey2), (x2, ey2)], fill=col_c, width=1)

    # Bottom caption
    f_cap = fnt(28, bold=True)
    col_cap = blend_color(WHITE, p_text)
    draw_text_centered(draw, "From raw logs to evidence-backed insights.", W//2, 920, f_cap, col_cap)
    return img

# Scene 5: 900-1110 (30-37s) — REPOSITORY DISCOVERY
def scene_05(f):
    lf = f - 900
    img, draw = make_base_bg(f)
    particles_field(draw, f, count=25, color=INDIGO, alpha_base=0.12)

    p_in    = clamp(ease_out(fade_val(lf, 0, 60)), 0, 1)
    p_term  = clamp(ease_out(fade_val(lf, 80, 150)), 0, 1)
    p_copy  = clamp(fade_val(lf, 160, 200), 0, 1)
    p_text  = clamp(fade_val(lf, 180, 210), 0, 1)

    # Endpoint detection banner
    ep_y = 130
    draw_rounded_rect(draw, 60, ep_y, W-60, ep_y+70, radius=12, fill=SURFACE, outline=VIOLET, width=1)
    draw.text((80, ep_y+14), "Detected Endpoint:", font=fnt(18), fill=blend_color(MUTED, p_in))
    draw.text((280, ep_y+14), "POST /api/v1/resources/allocate", font=fnt(18, bold=True, mono=True), fill=blend_color(LAV, p_in))
    draw.text((720, ep_y+14), "  Confidence: 96%", font=fnt(16), fill=blend_color(TEAL, p_in))

    # Repository cards
    repos = [
        ("resource-inventory-service", "northstar-labs", "PRIMARY MATCH", VIOLET, "Handles resource allocation API endpoints"),
        ("workflow-orchestrator",       "northstar-labs", "RELATED",       INDIGO, "Orchestrates multi-service workflows"),
        ("capacity-planning-api",       "northstar-labs", "RELATED",       INDIGO, "Manages capacity and quota enforcement"),
    ]
    cards_y = ep_y + 100
    card_h  = 120

    for i, (name, org, badge, col, desc) in enumerate(repos):
        cx1 = 60
        cx2 = W - 60
        cy1 = cards_y + i * (card_h + 16)
        cy2 = cy1 + card_h
        cp  = clamp(ease_out(fade_val(lf, 20+i*20, 80+i*20)), 0, 1)

        is_primary = (i == 0)
        border_col = VIOLET if is_primary else LINE
        bg_col     = SURFACE2 if is_primary else SURFACE

        draw_rounded_rect(draw, cx1, cy1, cx2, cy2, radius=12, fill=bg_col, outline=border_col, width=1 if not is_primary else 2)
        # Left: icon
        icon_cx = cx1 + 42
        icon_cy = cy1 + card_h//2
        glow_circle(draw, icon_cx, icon_cy, 22, col, cp*0.7, width=1, glow_layers=2)
        draw_logo_icon(draw, icon_cx, icon_cy, 14, alpha=cp)
        # Name + org
        draw.text((cx1+80, cy1+20), name, font=fnt(20, bold=True), fill=blend_color(WHITE, cp))
        draw.text((cx1+80, cy1+48), org + "/",                     font=fnt(16), fill=blend_color(MUTED, cp*0.8))
        draw.text((cx1+80, cy1+70), desc,                          font=fnt(16), fill=blend_color(MUTED, cp*0.7))
        # Badge
        draw_badge(draw, cx2-160, cy1+30, badge, col, size=15)

    # Terminal panel
    term_x, term_y = 60, cards_y + 3*(card_h+16) + 20
    term_w, term_h = W-120, 130
    draw_rounded_rect(draw, term_x, term_y, term_x+term_w, term_y+term_h,
                      radius=12, fill=(6,6,14), outline=LINE, width=1)
    draw.text((term_x+16, term_y+14), "Terminal — Copy-ready clone command", font=fnt(16), fill=blend_color(MUTED, p_term))
    draw.line([(term_x+8, term_y+40), (term_x+term_w-8, term_y+40)], fill=LINE, width=1)
    cmd = "git clone https://github.com/northstar-labs/resource-inventory-service.git"
    draw.text((term_x+16, term_y+50), "$ " + cmd, font=fnt(17, mono=True), fill=blend_color(TEAL, p_term))

    # Copy button animation
    if p_copy > 0:
        btn_x = term_x + term_w - 160
        btn_y = term_y + 50
        btn_col = VIOLET if p_copy < 0.5 else TEAL
        draw_rounded_rect(draw, btn_x, btn_y, btn_x+130, btn_y+34, radius=8,
                          fill=tuple(int(c*0.25) for c in btn_col), outline=btn_col, width=1)
        btn_txt = "Copy Command" if p_copy < 0.5 else "[OK] Copied!"
        draw_text_centered(draw, btn_txt, btn_x+65, btn_y+17, fnt(16, bold=True), blend_color(btn_col, 1.0))

    # Bottom caption
    f_cap = fnt(28, bold=True)
    col_cap = blend_color(WHITE, p_text)
    draw_text_centered(draw, "Find the right repository. Start debugging faster.", W//2, 940, f_cap, col_cap)
    return img

# Scene 6: 1110-1410 (37-47s) — JIRA COMMENT + EMAIL REPORT
def scene_06(f):
    lf = f - 1110
    img, draw = make_base_bg(f)
    particles_field(draw, f, count=15, color=LAV, alpha_base=0.08)

    p_left  = clamp(ease_out(fade_val(lf, 0, 70)), 0, 1)
    p_right = clamp(ease_out(fade_val(lf, 40, 110)), 0, 1)
    p_text  = clamp(fade_val(lf, 240, 290), 0, 1)

    # Divider line (split screen)
    div_x = W//2
    col_div = blend_color(LINE, max(p_left, p_right))
    draw.line([(div_x, 100), (div_x, H-130)], fill=col_div, width=1)

    # LEFT: Jira Comment
    jl_x, jl_y = 40, 100
    jl_w, jl_h = div_x - 60, H - 240
    draw_rounded_rect(draw, jl_x, jl_y, jl_x+jl_w, jl_y+jl_h,
                      radius=14, fill=SURFACE, outline=LINE, width=1)
    draw.text((jl_x+18, jl_y+16), "Jira Comment — NOVA-1001", font=fnt(19, bold=True), fill=blend_color(LAV, p_left))
    draw.line([(jl_x+8, jl_y+50), (jl_x+jl_w-8, jl_y+50)], fill=LINE, width=1)

    jira_lines = [
        ("JiraPilot AI", VIOLET, True,  "Investigation Report — NOVA-1001"),
        ("",            MUTED,  False, ""),
        ("Summary",     LAV,   True,  "Resource Allocation API returning HTTP 503"),
        ("Evidence",    LAV,   True,  "DB timeout on resource-db.internal:5432"),
        ("",            MUTED,  False, "Circuit breaker OPEN after 3 retries"),
        ("",            MUTED,  False, "CorrelationID: CORR-DEMO-1001"),
        ("Probable",    LAV,   True,  "DB connection pool exhaustion"),
        ("Cause",       MUTED,  False, "(hypothesis — not verified)"),
        ("",            MUTED,  False, ""),
        ("Next Step",   LAV,   True,  "Clone: resource-inventory-service"),
        ("",            MUTED,  False, "Check DB pool config & connection limits"),
    ]
    row_y = jl_y + 60
    for label, lbl_col, bold, text in jira_lines:
        lp = clamp(ease_out(fade_val(lf, 30, 100)), 0, 1)
        if label:
            draw.text((jl_x+18, row_y), label+":", font=fnt(14, bold=True), fill=blend_color(lbl_col, lp))
        draw.text((jl_x+130, row_y), text, font=fnt(15, bold=bold), fill=blend_color(WHITE if bold else MUTED, lp))
        row_y += 26 if text else 10

    # RIGHT: Email notification
    er_x, er_y = div_x + 20, 100
    er_w, er_h = W - div_x - 60, H - 240
    draw_rounded_rect(draw, er_x, er_y, er_x+er_w, er_y+er_h,
                      radius=14, fill=SURFACE, outline=LINE, width=1)
    draw.text((er_x+18, er_y+16), "Email Notification", font=fnt(19, bold=True), fill=blend_color(LAV, p_right))
    draw.line([(er_x+8, er_y+50), (er_x+er_w-8, er_y+50)], fill=LINE, width=1)

    email_fields = [
        ("To:",      "team@northstardigital.demo"),
        ("From:",    "jirapilot@notifications.demo"),
        ("Subject:", "[NOVA-1001] Investigation Update"),
    ]
    row_y = er_y + 60
    for lbl, val in email_fields:
        ep = clamp(ease_out(fade_val(lf, 60, 120)), 0, 1)
        draw.text((er_x+18, row_y), lbl, font=fnt(14, bold=True), fill=blend_color(MUTED, ep))
        draw.text((er_x+100, row_y), val, font=fnt(14), fill=blend_color(WHITE, ep))
        row_y += 28
    draw.line([(er_x+8, row_y+4), (er_x+er_w-8, row_y+4)], fill=LINE, width=1)
    row_y += 16
    email_body = [
        "Hi Team,",
        "",
        "JiraPilot AI has completed an investigation",
        "of ticket NOVA-1001.",
        "",
        "Summary: Resource allocation API returning",
        "HTTP 503 errors in Production (us-east-1).",
        "",
        "Evidence:",
        "  - DB timeout on resource-db.internal:5432",
        "  - Circuit breaker opened after 3 retries",
        "  - CorrelationID: CORR-DEMO-1001",
        "",
        "Probable Cause (Hypothesis):",
        "  Database connection pool exhaustion",
        "",
        "Next Action:",
        "  Clone resource-inventory-service",
        "  and check DB pool configuration.",
    ]
    for line in email_body:
        ep = clamp(ease_out(fade_val(lf, 90, 160)), 0, 1)
        draw.text((er_x+18, row_y), line, font=fnt(14), fill=blend_color(WHITE if line and not line.startswith(" ") else MUTED, ep))
        row_y += 22

    # Bottom caption
    f_cap = fnt(28, bold=True)
    col_cap = blend_color(WHITE, p_text)
    draw_text_centered(draw, "Clear reports. Better handoffs.", W//2, 920, f_cap, col_cap)
    return img

# Scene 7: 1410-1620 (47-54s) — DASHBOARD OVERVIEW
def scene_07(f):
    lf = f - 1410
    img, draw = make_base_bg(f)
    particles_field(draw, f, count=20, color=VIOLET, alpha_base=0.12)

    p_in   = clamp(ease_out(fade_val(lf, 0, 60)), 0, 1)
    p_text = clamp(fade_val(lf, 160, 210), 0, 1)

    # Dashboard header
    draw.text((60, 90), "JiraPilot AI — Investigation Dashboard", font=fnt(26, bold=True), fill=blend_color(WHITE, p_in))
    draw.text((60, 128), "NOVA-1001 — Active Investigation", font=fnt(18), fill=blend_color(LAV, p_in * 0.8))

    # Stat cards row
    stats = [
        ("Ticket Score", "87%",  TEAL,   "Readiness"),
        ("Log Lines",    "48",   VIOLET, "Analyzed"),
        ("Repos Found",  "3",    INDIGO, "Matched"),
        ("Time Elapsed", "4.2s", AMBER,  "Investigation"),
    ]
    sc_y = 170
    sc_w = (W - 120 - 3*20) // 4
    for i, (title, val, col, sub) in enumerate(stats):
        sc_x = 60 + i * (sc_w + 20)
        sp = clamp(ease_out(fade_val(lf, 10+i*12, 60+i*12)), 0, 1)
        draw_rounded_rect(draw, sc_x, sc_y, sc_x+sc_w, sc_y+110,
                          radius=12, fill=SURFACE, outline=col, width=1)
        draw.text((sc_x+16, sc_y+14), title, font=fnt(16), fill=blend_color(MUTED, sp))
        f_val = fnt(42, bold=True)
        draw_text_centered(draw, val, sc_x+sc_w//2, sc_y+64, f_val, blend_color(col, sp))
        draw.text((sc_x+16, sc_y+88), sub, font=fnt(14), fill=blend_color(MUTED, sp*0.7))

    # Evidence timeline
    tl_y = 300
    tl_x = 60
    tl_w = W - 120
    draw_rounded_rect(draw, tl_x, tl_y, tl_x+tl_w, tl_y+180,
                      radius=12, fill=SURFACE, outline=LINE, width=1)
    draw.text((tl_x+18, tl_y+14), "Evidence Timeline", font=fnt(18, bold=True), fill=blend_color(LAV, p_in))
    tl_p = clamp(ease_out(fade_val(lf, 40, 100)), 0, 1)
    tl_steps = [
        ("Ticket Created",     TEAL,   "NOVA-1001"),
        ("Readiness: 87%",     TEAL,   "7/8 fields OK"),
        ("Log Analysis",       TEAL,   "48 lines scanned"),
        ("Evidence Found",     TEAL,   "503 + DB timeout"),
        ("Repo Discovered",    TEAL,   "resource-inventory"),
        ("Report Generated",   TEAL,   "Jira + Email"),
        ("Team Notified",      VIOLET, "Pending action"),
    ]
    step_x = tl_x + 30
    for i, (label, col, detail) in enumerate(tl_steps):
        sp2 = clamp(ease_out(fade_val(lf, 30+i*15, 90+i*15)), 0, 1)
        sx = step_x + i * 205
        sy = tl_y + 60
        # Dot
        glow_circle(draw, sx+8, sy, 8, col, sp2*0.8, width=2, glow_layers=2)
        # Connecting line
        if i < len(tl_steps)-1:
            col_l = blend_color(col, sp2 * 0.4)
            draw.line([(sx+18, sy), (sx+195, sy)], fill=col_l, width=1)
        draw.text((sx-10, sy+18), label,  font=fnt(13, bold=True), fill=blend_color(col, sp2))
        draw.text((sx-10, sy+36), detail, font=fnt(12),            fill=blend_color(MUTED, sp2*0.8))

    # Next steps panel
    ns_y = 500
    ns_x = 60
    ns_w = W//2 - 80
    draw_rounded_rect(draw, ns_x, ns_y, ns_x+ns_w, ns_y+160,
                      radius=12, fill=SURFACE, outline=VIOLET, width=1)
    draw.text((ns_x+18, ns_y+14), "Recommended Next Steps", font=fnt(18, bold=True), fill=blend_color(LAV, p_in))
    ns_items = [
        "1. Clone resource-inventory-service repository",
        "2. Review DB connection pool configuration",
        "3. Check circuit breaker thresholds",
        "4. Verify resource-db.internal health",
    ]
    for i, item in enumerate(ns_items):
        np2 = clamp(ease_out(fade_val(lf, 60+i*15, 120+i*15)), 0, 1)
        draw.text((ns_x+18, ns_y+44+i*28), item, font=fnt(15), fill=blend_color(MUTED, np2))

    # Repo suggestions panel
    rs_x = W//2 + 20
    rs_w = W - rs_x - 60
    draw_rounded_rect(draw, rs_x, ns_y, rs_x+rs_w, ns_y+160,
                      radius=12, fill=SURFACE, outline=INDIGO, width=1)
    draw.text((rs_x+18, ns_y+14), "Approved Repositories", font=fnt(18, bold=True), fill=blend_color(LAV, p_in))
    repos2 = ["resource-inventory-service [PRIMARY]", "workflow-orchestrator", "capacity-planning-api"]
    for i, r in enumerate(repos2):
        rp = clamp(ease_out(fade_val(lf, 70+i*15, 130+i*15)), 0, 1)
        col_r = VIOLET if i == 0 else MUTED
        draw.text((rs_x+18, ns_y+44+i*36), r, font=fnt(15, mono=True), fill=blend_color(col_r, rp))

    # Bottom caption
    f_cap = fnt(28, bold=True)
    col_cap = blend_color(WHITE, p_text)
    draw_text_centered(draw, "One workspace. Full visibility. Faster resolution.", W//2, 720, f_cap, col_cap)
    return img

# Scene 8: 1620-1800 (54-60s) — CLOSING / CTA
def scene_08(f):
    lf = f - 1620
    total = 180
    img, draw = make_base_bg(f)
    particles_field(draw, f, count=50, color=VIOLET, alpha_base=0.3*(lf/total))
    concentric_rings(draw, W//2, H//2, lf, rings=7, base_r=80, spacing=80, alpha_base=0.6*(lf/total))

    p_logo  = clamp(ease_out(fade_val(lf, 0, 50)), 0, 1)
    p_title = clamp(ease_out(fade_val(lf, 30, 90)), 0, 1)
    p_tag   = clamp(ease_out(fade_val(lf, 60, 120)), 0, 1)
    p_cta   = clamp(ease_out(fade_val(lf, 100, 160)), 0, 1)
    # Final fade out
    p_out   = clamp(fade_val(lf, 150, 180), 0, 1)
    if p_out > 0:
        overlay = Image.new("RGB", (W,H), BG)
        img = Image.blend(img, overlay, p_out)
        draw = ImageDraw.Draw(img)

    draw_logo_icon(draw, W//2, H//2 - 80, size=72, alpha=p_logo)
    f_big  = fnt(72, bold=True)
    f_tag  = fnt(32)
    f_cta  = fnt(24)
    f_sub  = fnt(20)

    col_title = blend_color(WHITE, p_title)
    col_tag   = blend_color(LAV,   p_tag * 0.9)
    col_cta   = blend_color(MUTED, p_cta * 0.8)
    col_h     = blend_color(VIOLET, p_cta)

    draw_text_centered(draw, "JiraPilot AI", W//2, H//2 + 20, f_big, col_title)
    draw_text_centered(draw, "Your investigation copilot.", W//2, H//2 + 95, f_tag, col_tag)
    draw_text_centered(draw, "Turn every Jira issue into a structured, evidence-backed investigation.", W//2, H//2 + 155, f_cta, col_cta)
    draw_text_centered(draw, "Built for Hackathon — Northstar Digital Systems", W//2, H//2 + 195, f_sub, col_cta)

    # Feature pills
    pills = ["Ticket Readiness", "Log Analysis", "Repo Discovery", "AI Reports", "Team Handoffs"]
    pill_total_w = sum(160 for _ in pills) + 16*(len(pills)-1)
    pill_start_x = W//2 - pill_total_w//2
    for i, pill in enumerate(pills):
        pp = clamp(ease_out(fade_val(lf, 110+i*8, 160+i*8)), 0, 1)
        px = pill_start_x + i*176
        py = H//2 + 250
        col_pp = VIOLET if i % 2 == 0 else INDIGO
        draw_rounded_rect(draw, px, py, px+160, py+36, radius=18,
                          fill=tuple(int(c*0.2) for c in col_pp), outline=col_pp, width=1)
        draw_text_centered(draw, pill, px+80, py+18, fnt(15, bold=True), blend_color(WHITE, pp))

    return img

# ═══════════════════════════════════════════════════════════════════════════
# AUDIO: Generate ambient music + TTS voiceover mix
# ═══════════════════════════════════════════════════════════════════════════

SAMPLE_RATE = 44100
AUDIO_TOTAL  = int(TOTAL_DURATION * SAMPLE_RATE)

def generate_ambient_music(duration_s=60.0):
    """Synthesize a simple electronic ambient bed — arpeggiated chords, pad."""
    n = int(duration_s * SAMPLE_RATE)
    t = np.linspace(0, duration_s, n, dtype=np.float32)
    music = np.zeros(n, dtype=np.float32)

    # Pad — slow chord swell: F minor pentatonic
    freqs_pad = [174.61, 207.65, 261.63, 311.13, 349.23]
    for freq in freqs_pad:
        phase = np.random.uniform(0, math.pi*2)
        env = 0.5 + 0.5 * np.sin(2*math.pi*0.07*t + phase)
        music += 0.03 * env * np.sin(2*math.pi*freq*t)

    # Arpeggio — 8th-note pattern at 80 BPM
    bpm = 80
    beat = 60.0 / bpm
    eighth = beat / 2.0
    arp_notes = [261.63, 311.13, 349.23, 392.00, 466.16, 392.00, 349.23, 311.13]
    for step, freq in enumerate(arp_notes * 100):
        start = step * eighth
        if start >= duration_s: break
        end = min(start + eighth * 0.8, duration_s)
        si = int(start * SAMPLE_RATE)
        ei = int(end * SAMPLE_RATE)
        if ei <= si: continue
        seg_t = np.linspace(0, end-start, ei-si, dtype=np.float32)
        env = np.exp(-3.0 * seg_t / (end-start))
        music[si:ei] += 0.025 * env * np.sin(2*math.pi*freq*seg_t)

    # Sub bass pulse
    bass_f = 87.31
    bass_env = 0.3 + 0.7 * np.abs(np.sin(2*math.pi*0.25*t))
    music += 0.015 * bass_env * np.sin(2*math.pi*bass_f*t)

    # Fade in/out
    fi = min(int(2*SAMPLE_RATE), n)
    fo = min(int(3*SAMPLE_RATE), n)
    music[:fi] *= np.linspace(0, 1, fi)
    music[-fo:] *= np.linspace(1, 0, fo)

    # Normalize
    pk = np.max(np.abs(music))
    if pk > 0:
        music = music / pk * 0.28
    return music

def generate_tts_voiceover():
    """Generate TTS using Windows SAPI (Zira) into separate WAV files per scene."""
    scripts = [
        (1, "Every software incident starts with a question. Where do we begin?"),
        (2, "JiraPilot AI turns a new Jira issue into a structured investigation path."),
        (3, "It checks ticket readiness and helps teams request the details they actually need."),
        (4, "It analyzes logs, connects related errors, and surfaces evidence behind likely failure points."),
        (5, "It recommends approved repositories and prepares copy-ready clone commands for debugging."),
        (6, "It prepares readable investigation reports and keeps the whole team informed."),
        (7, "One unified workspace. Full visibility across tickets, logs, repositories, and next steps."),
        (8, "JiraPilot AI. Your investigation copilot. Built for software teams that move fast."),
    ]
    scene_wavs = []
    for scene_num, text in scripts:
        out_path = os.path.join(VO_DIR, f"vo_enh_{scene_num:02d}.wav")
        scene_wavs.append(out_path)
        if os.path.exists(out_path):
            print(f"  [SKIP] vo_enh_{scene_num:02d}.wav already exists")
            continue
        ps_script = f"""
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Zira Desktop')
$synth.Rate = -1
$synth.SetOutputToWaveFile('{out_path.replace(chr(92), "/")}')
$synth.Speak('{text.replace("'", "")}')
$synth.Dispose()
Write-Host 'TTS done: {scene_num}'
"""
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True, timeout=30
            )
            print(f"  [TTS] scene {scene_num}: {r.stdout.strip()}")
        except Exception as e:
            print(f"  [TTS ERR] scene {scene_num}: {e}")
    return scene_wavs

def load_wav_as_array(path):
    try:
        with wave.open(path, 'rb') as wf:
            ch  = wf.getnchannels()
            sw  = wf.getsampwidth()
            fr  = wf.getframerate()
            n   = wf.getnframes()
            raw = wf.readframes(n)
        if sw == 2:
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif sw == 3:
            arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1,3)
            data = ((arr[:,2].astype(np.int32) << 16 |
                     arr[:,1].astype(np.int32) << 8  |
                     arr[:,0].astype(np.int32)) - (1<<24 if True else 0)).astype(np.float32)/8388608.0
        else:
            data = np.frombuffer(raw, dtype=np.float32)
        if ch == 2:
            data = data.reshape(-1,2).mean(axis=1)
        # Resample naively if needed
        if fr != SAMPLE_RATE:
            ratio = SAMPLE_RATE / fr
            new_n = int(len(data) * ratio)
            data = np.interp(np.linspace(0,len(data)-1,new_n), np.arange(len(data)), data)
        return data
    except Exception as e:
        print(f"  [WAV ERR] {path}: {e}")
        return np.zeros(SAMPLE_RATE, dtype=np.float32)

def build_mixed_audio(scene_wavs):
    """Mix TTS voice + ambient music into a 60s mono float32 array."""
    music = generate_ambient_music(TOTAL_DURATION)

    # Scene timing (frames): map to seconds
    scene_starts_s = [0, 5, 12, 20, 30, 37, 47, 54]

    voice_track = np.zeros(AUDIO_TOTAL, dtype=np.float32)
    for i, wav_path in enumerate(scene_wavs):
        start_s = scene_starts_s[i]
        start_smp = int(start_s * SAMPLE_RATE)
        vo_arr = load_wav_as_array(wav_path)
        end_smp = min(start_smp + len(vo_arr), AUDIO_TOTAL)
        length = end_smp - start_smp
        if length > 0:
            voice_track[start_smp:end_smp] += vo_arr[:length] * 0.85

    # Side-chain duck music when voice is present
    voice_envelope = np.abs(voice_track)
    # Smooth envelope
    smooth = 800
    kernel = np.ones(smooth)/smooth
    voice_env_smooth = np.convolve(voice_envelope, kernel, mode='same')
    duck_factor = 1.0 - np.clip(voice_env_smooth * 5, 0, 0.7)
    music_ducked = music * duck_factor

    mix = music_ducked + voice_track
    pk = np.max(np.abs(mix))
    if pk > 0:
        mix = mix / pk * 0.92

    # Stereo
    stereo = np.stack([mix, mix], axis=1)
    stereo_int = (stereo * 32767).clip(-32768, 32767).astype(np.int16)

    audio_path = os.path.join(VO_DIR, "enhanced_mixed_audio.wav")
    with wave.open(audio_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(stereo_int.tobytes())
    print(f"  [AUDIO] Mixed audio saved: {audio_path}")
    return audio_path

# ═══════════════════════════════════════════════════════════════════════════
# MAIN RENDER PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

SCENE_MAP = [
    (0,    150,  scene_01),   # 0–5s
    (150,  360,  scene_02),   # 5–12s
    (360,  600,  scene_03),   # 12–20s
    (600,  900,  scene_04),   # 20–30s
    (900,  1110, scene_05),   # 30–37s
    (1110, 1410, scene_06),   # 37–47s
    (1410, 1620, scene_07),   # 47–54s
    (1620, 1800, scene_08),   # 54–60s
]

def get_scene_func(frame):
    for start, end, fn in SCENE_MAP:
        if start <= frame < end:
            return fn
    return scene_08

def render_video_frames_to_ffmpeg(audio_path):
    """Pipe raw RGB frames to FFmpeg, mux with audio."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        OUT_MP4
    ]
    print(f"\n[FFMPEG] Starting encode → {OUT_MP4}")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    t0 = time.time()
    for frame in range(TOTAL_FRAMES):
        img = get_scene_func(frame)(frame)
        proc.stdin.write(img.tobytes())
        if frame % 150 == 0:
            pct = frame/TOTAL_FRAMES*100
            elapsed = time.time()-t0
            fps_actual = frame / elapsed if elapsed > 0 else 0
            eta = (TOTAL_FRAMES - frame) / fps_actual if fps_actual > 0 else 0
            print(f"  Frame {frame:4d}/{TOTAL_FRAMES} ({pct:5.1f}%) | {fps_actual:.1f} fps | ETA {eta:.0f}s", flush=True)

    proc.stdin.close()
    proc.wait()
    elapsed = time.time()-t0
    print(f"\n[DONE] Render complete in {elapsed:.0f}s → {OUT_MP4}")

def main():
    print("=" * 60)
    print("JiraPilot AI — Enhanced Presentation Video Render")
    print("=" * 60)

    print("\n[1/3] Generating TTS voiceover...")
    scene_wavs = generate_tts_voiceover()

    print("\n[2/3] Building mixed audio track...")
    audio_path = build_mixed_audio(scene_wavs)

    print("\n[3/3] Rendering video frames (1800 @ 30fps)...")
    render_video_frames_to_ffmpeg(audio_path)

    # Verify
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration,bit_rate", "-of", "csv=p=0", OUT_MP4],
            capture_output=True, text=True
        )
        print(f"[VERIFY] {r.stdout.strip()}")
        sz = os.path.getsize(OUT_MP4)
        print(f"[VERIFY] File size: {sz/1024/1024:.1f} MB")
    except Exception:
        pass

if __name__ == "__main__":
    main()
