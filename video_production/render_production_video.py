"""
JiraPilot AI — Premium 60-Second Enterprise Product Video Production Engine
Direct Pillow-to-FFmpeg pipeline for high performance rendering.
"""

import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS = 30
TOTAL_DURATION = 60.0
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)  # 1800 frames

# Output paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "output")
SCENES_DIR = os.path.join(OUT_DIR, "scenes")
AUDIO_DIR = os.path.join(OUT_DIR, "audio")
CAPTIONS_DIR = os.path.join(OUT_DIR, "captions")

for d in [OUT_DIR, SCENES_DIR, AUDIO_DIR, CAPTIONS_DIR]:
    os.makedirs(d, exist_ok=True)

# Typography
FONT_SANS = "C:/Windows/Fonts/segoeui.ttf"
FONT_SANS_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"
FONT_MONO_BOLD = "C:/Windows/Fonts/consolab.ttf"

def get_font(size, bold=False, mono=False):
    try:
        if mono:
            path = FONT_MONO_BOLD if bold else FONT_MONO
        else:
            path = FONT_SANS_BOLD if bold else FONT_SANS
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# Color Palette (Dark Mode Enterprise SaaS with Warm Copper Accents)
C_BG = (11, 18, 32)            # #0b1220
C_SURFACE = (18, 26, 43)       # #121a2b
C_SURFACE_2 = (14, 22, 36)     # #0e1624
C_LINE = (36, 48, 68)          # #243044
C_INK = (232, 238, 248)        # #e8eef8
C_MUTED = (139, 155, 179)      # #8b9bb3
C_ACCENT = (107, 139, 255)     # #6b8bff (Restrained Indigo)
C_TEAL = (45, 212, 191)        # #2dd4bf
C_AMBER = (251, 191, 36)       # #fbbf24
C_DANGER = (248, 113, 113)     # #f87171

# Warm Copper Accents (Reference Video visual language)
C_COPPER = (210, 120, 40)
C_COPPER_BRIGHT = (255, 160, 60)
C_COPPER_DEEP = (160, 80, 20)

# Pre-cached fonts for speed
F_TITLE_LG = get_font(52, bold=True)
F_TITLE_MD = get_font(38, bold=True)
F_TITLE_SM = get_font(28, bold=True)
F_BODY = get_font(20, bold=False)
F_BODY_BOLD = get_font(20, bold=True)
F_SM = get_font(16, bold=False)
F_SM_BOLD = get_font(16, bold=True)
F_XS = get_font(13, bold=False)
F_MONO = get_font(17, bold=False, mono=True)
F_MONO_SM = get_font(14, bold=False, mono=True)
F_MONO_BOLD = get_font(17, bold=True, mono=True)

# Helper: Radial copper glow
def create_glow(size, color, max_alpha=0.3):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size // 2
    for dr in range(r, 0, -max(1, r // 15)):
        ratio = dr / r
        alpha = int(255 * max_alpha * (1 - ratio) ** 1.8)
        d.ellipse([r - dr, r - dr, r + dr, r + dr], fill=(*color, alpha))
    return img.filter(ImageFilter.GaussianBlur(size // 8))

GLOW_COPPER_LG = create_glow(700, C_COPPER, 0.32)
GLOW_COPPER_MD = create_glow(450, C_COPPER, 0.28)
GLOW_TEAL_MD = create_glow(450, C_TEAL, 0.15)
GLOW_INDIGO_MD = create_glow(500, C_ACCENT, 0.18)

# -------------------------------------------------------------
# SCENE 1: The Problem (0.0s – 5.0s | 150 frames)
# -------------------------------------------------------------
def render_scene_1(t, frame_idx):
    # t: 0.0 to 5.0
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    
    # Warm copper glow expanding from center-left
    glow_scale = min(1.0, 0.4 + t * 0.12)
    gw = int(GLOW_COPPER_LG.width * glow_scale)
    gh = int(GLOW_COPPER_LG.height * glow_scale)
    glow_resized = GLOW_COPPER_LG.resize((gw, gh), Image.Resampling.BILINEAR)
    img.paste(glow_resized, (int(W * 0.32 - gw // 2), int(H * 0.48 - gh // 2)), glow_resized)

    # Ghost log fragments drifting in darkness
    draw = ImageDraw.Draw(img)
    fragments = [
        ("NOVA-1001", 160, 220, 0.18),
        ("HTTP 503 Service Unavailable", 1100, 260, 0.22),
        ("correlationId=CORR-8821", 240, 780, 0.16),
        ("ERROR [NOVA-PAY] Upstream timeout after 30000ms", 840, 720, 0.20),
        ("POST /api/payment/process", 1240, 480, 0.15),
        ("WARN  Circuit breaker HALF_OPEN", 180, 440, 0.14)
    ]
    for text, x, y, alpha_factor in fragments:
        drift_x = int(math.sin(t * 0.8 + x) * 15)
        drift_y = int(t * 8)
        alpha = int(255 * alpha_factor * min(1.0, t / 1.5))
        draw.text((x + drift_x, y - drift_y), text, font=F_MONO_SM, fill=(*C_MUTED, alpha))

    # Copper particle flecks
    rng = np.random.default_rng(101)
    for i in range(45):
        bx = int(rng.integers(100, W - 100))
        by = int(rng.integers(100, H - 100))
        speed = 10 + (i % 7) * 4
        px = bx + int(math.sin(t * 1.2 + i) * 20)
        py = (by - int(t * speed)) % H
        p_alpha = int(180 * (0.4 + 0.6 * math.sin(t * 2.5 + i)))
        r = 1.5 + (i % 3)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(*C_COPPER_BRIGHT, p_alpha))

    # Typewriter text reveal: "Every incident starts with a question."
    full_text = "Every incident starts with a question."
    tw_progress = min(1.0, max(0.0, (t - 0.6) / 2.5))
    visible_chars = int(len(full_text) * tw_progress)
    displayed_text = full_text[:visible_chars]

    if displayed_text:
        bbox = draw.textbbox((0, 0), full_text, font=F_TITLE_LG)
        tw_w = bbox[2] - bbox[0]
        tx = (W - tw_w) // 2
        ty = H // 2 - 20
        draw.text((tx, ty), displayed_text, font=F_TITLE_LG, fill=C_INK)
        
        # Blinking cursor
        if t < 4.2 and int(t * 4) % 2 == 0:
            cur_bbox = draw.textbbox((0, 0), displayed_text, font=F_TITLE_LG)
            cur_x = tx + (cur_bbox[2] - cur_bbox[0]) + 6
            draw.rectangle([cur_x, ty + 6, cur_x + 3, ty + 56], fill=C_COPPER_BRIGHT)

    # Initial fade in from black (first 0.6s)
    if t < 0.6:
        fade = 1.0 - (t / 0.6)
        fade_img = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fade)))
        img = Image.alpha_composite(img, fade_img)

    return img.convert("RGB")

# -------------------------------------------------------------
# SCENE 2: Jira Issue Created (5.0s – 12.0s | 210 frames)
# -------------------------------------------------------------
def render_scene_2(t, frame_idx):
    # t: 0.0 to 7.0 (absolute 5.0 to 12.0)
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    
    # Ambient copper accent glow
    img.paste(GLOW_COPPER_MD, (int(W * 0.5 - 225), int(H * 0.2 - 225)), GLOW_COPPER_MD)

    draw = ImageDraw.Draw(img)

    # JiraPilot AI Logo Reveal (top center)
    logo_alpha = min(1.0, t / 1.0)
    a_logo = int(255 * logo_alpha)
    
    # Brand mark + text
    logo_str = "JiraPilot"
    ai_str = " AI"
    bbox_logo = draw.textbbox((0, 0), logo_str, font=F_TITLE_MD)
    bbox_ai = draw.textbbox((0, 0), ai_str, font=F_TITLE_MD)
    total_logo_w = (bbox_logo[2] - bbox_logo[0]) + (bbox_ai[2] - bbox_ai[0])
    lx = (W - total_logo_w) // 2
    ly = 80
    
    draw.text((lx, ly), logo_str, font=F_TITLE_MD, fill=(*C_INK, a_logo))
    draw.text((lx + (bbox_logo[2] - bbox_logo[0]), ly), ai_str, font=F_TITLE_MD, fill=(*C_COPPER_BRIGHT, a_logo))

    # Thin copper accent line under logo
    bar_w = int(140 * logo_alpha)
    if bar_w > 0:
        bx = (W - bar_w) // 2
        draw.rectangle([bx, ly + 52, bx + bar_w, ly + 55], fill=(*C_COPPER, a_logo))

    # Headline
    sub_text = "A new Jira issue. A clearer path forward."
    bbox_sub = draw.textbbox((0, 0), sub_text, font=F_BODY_BOLD)
    sw = bbox_sub[2] - bbox_sub[0]
    draw.text(((W - sw) // 2, ly + 68), sub_text, font=F_BODY_BOLD, fill=(*C_MUTED, a_logo))

    # Jira Ticket NOVA-1001 Card with Smooth Camera Push
    card_prog = min(1.0, max(0.0, (t - 0.8) / 1.5))
    card_alpha = int(255 * card_prog)
    
    # Slow cinematic camera push (scale increases from 0.94 to 1.02 over time)
    zoom = 0.94 + 0.08 * (t / 7.0)
    card_w = int(980 * zoom)
    card_h = int(580 * zoom)
    cx = (W - card_w) // 2
    cy = int(240 - (zoom - 0.94) * 60)

    # Card background and border
    draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=14,
                           fill=(*C_SURFACE, card_alpha), outline=(*C_LINE, card_alpha), width=1)

    # Card top header bar (Atlassian Jira inspired styling)
    draw.rounded_rectangle([cx, cy, cx + card_w, cy + 54], radius=14,
                           fill=(*C_SURFACE_2, card_alpha))
    draw.rectangle([cx, cy + 34, cx + card_w, cy + 54], fill=(*C_SURFACE_2, card_alpha))
    draw.line([(cx, cy + 54), (cx + card_w, cy + 54)], fill=(*C_LINE, card_alpha), width=1)

    # Ticket key badge
    draw.rounded_rectangle([cx + 24, cy + 12, cx + 154, cy + 42], radius=6,
                           fill=(*C_ACCENT, int(card_alpha * 0.25)), outline=(*C_ACCENT, card_alpha), width=1)
    draw.text((cx + 36, cy + 17), "NOVA-1001", font=F_MONO_BOLD, fill=(*C_INK, card_alpha))

    # Status Pill (OPEN) & Priority
    draw.rounded_rectangle([cx + 170, cy + 14, cx + 245, cy + 40], radius=5, fill=(*C_AMBER, int(card_alpha * 0.25)))
    draw.text((cx + 182, cy + 18), "OPEN", font=F_SM_BOLD, fill=(*C_AMBER, card_alpha))

    draw.text((cx + 265, cy + 18), "•  Priority: High  •  Project: Nova Core Platform",
              font=F_SM, fill=(*C_MUTED, card_alpha))

    # Ticket Summary Field (Typewriter/Cursor effect)
    draw.text((cx + 32, cy + 82), "Summary:", font=F_SM_BOLD, fill=(*C_MUTED, card_alpha))
    summary_text = "Payment service returns HTTP 503 during checkout peak load"
    draw.text((cx + 32, cy + 110), summary_text, font=F_TITLE_SM, fill=(*C_INK, card_alpha))

    # Metadata Grid
    meta_rows = [
        ("Reporter", "alex.chen@nova-eng.internal", "Environment", "production-us-east-1"),
        ("Detected API", "POST /api/v1/checkout/payment", "Component", "payment-service"),
        ("Created", "2026-10-09 14:22:18 UTC", "Correlation ID", "CORR-9921-X9")
    ]
    my = cy + 180
    for r1_k, r1_v, r2_k, r2_v in meta_rows:
        draw.text((cx + 32, my), r1_k + ":", font=F_XS, fill=(*C_MUTED, card_alpha))
        draw.text((cx + 32, my + 18), r1_v, font=F_MONO_SM, fill=(*C_INK, card_alpha))
        draw.text((cx + 520, my), r2_k + ":", font=F_XS, fill=(*C_MUTED, card_alpha))
        draw.text((cx + 520, my + 18), r2_v, font=F_MONO_SM, fill=(*C_INK, card_alpha))
        my += 64

    # Restrained Animated Cursor interacting with ticket
    if t > 3.0:
        cursor_x = cx + 32 + int(math.sin((t - 3.0) * 1.5) * 80 + 350)
        cursor_y = cy + 120
        # Draw pointer cursor
        draw.polygon([(cursor_x, cursor_y),
                      (cursor_x, cursor_y + 18),
                      (cursor_x + 5, cursor_y + 14),
                      (cursor_x + 11, cursor_y + 24),
                      (cursor_x + 15, cursor_y + 22),
                      (cursor_x + 9, cursor_y + 12),
                      (cursor_x + 16, cursor_y + 12)],
                     fill=(*C_COPPER_BRIGHT, 230), outline=(*C_INK, 255))

    return img.convert("RGB")

# -------------------------------------------------------------
# SCENE 3: Ticket Readiness (12.0s – 20.0s | 240 frames)
# -------------------------------------------------------------
def render_scene_3(t, frame_idx):
    # t: 0.0 to 8.0 (absolute 12.0 to 20.0)
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    draw = ImageDraw.Draw(img)

    # Ambient teal/indigo light
    img.paste(GLOW_TEAL_MD, (int(W * 0.7 - 225), int(H * 0.3 - 225)), GLOW_TEAL_MD)

    # Header
    draw.text((120, 80), "Diagnostic Information Readiness", font=F_TITLE_MD, fill=C_INK)
    draw.text((120, 134), "Validate. Identify gaps. Request the right details.", font=F_BODY_BOLD, fill=C_COPPER_BRIGHT)

    # Readiness Score Progress Ring / Bar (Animates from 0% to 75%)
    score_target = 0.75
    anim_progress = min(1.0, t / 4.0)
    cur_score = int(score_target * anim_progress * 100)

    # Score Card
    draw.rounded_rectangle([120, 190, 480, 480], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((150, 220), "Readiness Score", font=F_SM_BOLD, fill=C_MUTED)
    
    # Large score number
    draw.text((150, 260), f"{cur_score}%", font=get_font(72, bold=True), fill=C_TEAL)
    draw.text((150, 360), "Status: WAITING FOR INFORMATION", font=F_XS, fill=C_AMBER)
    draw.text((150, 390), "2 required diagnostic fields missing", font=F_XS, fill=C_MUTED)
    draw.text((150, 415), "Auto-triage request queued for reporter", font=F_XS, fill=C_COPPER_BRIGHT)

    # 6 Diagnostic Fields Checklist (Right Grid)
    fields = [
        ("Issue Summary & Description", True, "Detailed problem statement provided"),
        ("Environment & Service Tier", True, "Production / Tier-1 Payment Cluster"),
        ("API Endpoint & Method", True, "POST /api/v1/checkout/payment"),
        ("Expected Behavior", True, "HTTP 200 within 450ms threshold"),
        ("Application Server Logs", False, "Missing: Full stack trace and error logs"),
        ("Payload & Correlation ID", False, "Missing: Raw JSON request and correlation header")
    ]

    gx = 520
    gy = 190
    for idx, (label, is_ready, detail) in enumerate(fields):
        # Staggered reveal
        field_anim = min(1.0, max(0.0, (t - idx * 0.45) / 0.5))
        if field_anim <= 0.0:
            continue
        
        a = int(255 * field_anim)
        fy = gy + idx * 78
        
        # Row card
        border_col = C_TEAL if is_ready else C_DANGER
        bg_col = (16, 42, 40) if is_ready else (42, 20, 22)
        
        draw.rounded_rectangle([gx, fy, gx + 1280, fy + 66], radius=10,
                               fill=(*bg_col, a), outline=(*border_col, int(a * 0.5)), width=1)
        
        # Check / Warning Icon
        icon_str = "✓" if is_ready else "!"
        icon_col = C_TEAL if is_ready else C_DANGER
        draw.ellipse([gx + 18, fy + 16, gx + 52, fy + 50], fill=(*border_col, int(a * 0.25)))
        draw.text((gx + 28, fy + 19), icon_str, font=F_SM_BOLD, fill=(*icon_col, a))

        # Field Name & Detail
        draw.text((gx + 72, fy + 13), label, font=F_BODY_BOLD, fill=(*C_INK, a))
        detail_col = C_MUTED if is_ready else C_AMBER
        draw.text((gx + 72, fy + 38), detail, font=F_XS, fill=(*detail_col, a))

        # Status badge
        status_txt = "VALIDATED" if is_ready else "MISSING"
        draw.rounded_rectangle([gx + 1150, fy + 18, gx + 1260, fy + 48], radius=6,
                               fill=(*border_col, int(a * 0.2)))
        draw.text((gx + 1162, fy + 24), status_txt, font=F_XS, fill=(*border_col, a))

    # Bottom Callout: JiraPilot AI Action Prompt
    if t > 4.5:
        cp_alpha = min(1.0, (t - 4.5) / 1.0)
        draw.rounded_rectangle([120, 880, 1800, 960], radius=12,
                               fill=(*C_SURFACE_2, int(255 * cp_alpha)),
                               outline=(*C_COPPER, int(200 * cp_alpha)), width=1)
        draw.text((150, 908), "⚡ JiraPilot AI automated prompt:", font=F_BODY_BOLD, fill=(*C_COPPER_BRIGHT, int(255 * cp_alpha)))
        draw.text((470, 910), "\"Alex, could you attach the server logs around 14:22 UTC and the CORR-9921 payload to resume automated triage?\"",
                  font=F_BODY, fill=(*C_INK, int(255 * cp_alpha)))

    return img.convert("RGB")

# -------------------------------------------------------------
# SCENE 4: AI Log Analysis (20.0s – 30.0s | 300 frames)
# -------------------------------------------------------------
def render_scene_4(t, frame_idx):
    # t: 0.0 to 10.0 (absolute 20.0 to 30.0)
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    draw = ImageDraw.Draw(img)

    # Ambient glow
    img.paste(GLOW_COPPER_MD, (int(W * 0.2 - 225), int(H * 0.5 - 225)), GLOW_COPPER_MD)

    # Header
    draw.text((100, 60), "From raw logs to evidence-backed insights.", font=F_TITLE_MD, fill=C_INK)
    draw.text((100, 114), "Analyzing correlation chains, endpoint anomalies, and circuit breaker state.",
              font=F_BODY, fill=C_MUTED)

    # Left: Dark Log Console (Width: 1040px)
    lx, ly, lw, lh = 100, 170, 1060, 830
    draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=12, fill=(6, 10, 18), outline=C_LINE, width=1)
    
    # Terminal top bar
    draw.rounded_rectangle([lx, ly, lx + lw, ly + 44], radius=12, fill=C_SURFACE_2)
    draw.rectangle([lx, ly + 24, lx + lw, ly + 44], fill=C_SURFACE_2)
    draw.line([(lx, ly + 44), (lx + lw, ly + 44)], fill=C_LINE, width=1)
    
    # Window dots
    draw.ellipse([lx + 16, ly + 16, lx + 26, ly + 26], fill=C_DANGER)
    draw.ellipse([lx + 34, ly + 16, lx + 44, ly + 26], fill=C_AMBER)
    draw.ellipse([lx + 52, ly + 16, lx + 62, ly + 26], fill=C_TEAL)
    draw.text((lx + 80, ly + 14), "nova-payment-cluster-stdout.log  (correlationId=CORR-9921-X9)", font=F_XS, fill=C_MUTED)

    # Synthetic Log Lines
    log_lines = [
        ("14:22:15.102", "INFO",  "c.n.gateway.HttpInboundHandler", "Received POST /api/v1/checkout/payment", C_MUTED),
        ("14:22:15.108", "INFO",  "c.n.auth.TokenValidator", "JWT verification succeeded subject=alex.chen", C_MUTED),
        ("14:22:16.420", "WARN",  "c.n.payment.CircuitBreaker", "Circuit breaker failure rate 48.5% threshold=50%", C_AMBER),
        ("14:22:17.892", "ERROR", "c.n.payment.UpstreamClient", "HTTP 503 Service Unavailable on /upstream/charge", C_DANGER),
        ("14:22:18.004", "ERROR", "c.n.payment.RetryCoordinator", "Retry 1/3 failed: Connection reset by peer", C_DANGER),
        ("14:22:18.312", "ERROR", "c.n.payment.RetryCoordinator", "Retry 2/3 failed: SocketTimeoutException (3000ms)", C_DANGER),
        ("14:22:18.625", "FATAL", "c.n.payment.CircuitBreaker", "State transitioned to OPEN. Dropping inbound requests", C_COPPER_BRIGHT),
        ("14:22:18.630", "WARN",  "c.n.gateway.ErrorHandler", "Returning HTTP 503 to caller corrId=CORR-9921-X9", C_AMBER),
        ("14:22:19.010", "INFO",  "c.n.telemetry.MetricExporter", "Published metric payment_failure_count tags=[tier1]", C_MUTED),
        ("14:22:19.450", "INFO",  "c.n.payment.HealthCheck", "Dependency 'stripe-relay' unhealthy (lastPing=503)", C_DANGER)
    ]

    line_y = ly + 64
    for idx, (ts, level, logger, msg, col) in enumerate(log_lines):
        line_anim = min(1.0, max(0.0, (t - idx * 0.4) / 0.3))
        if line_anim <= 0.0:
            continue
        la = int(255 * line_anim)
        
        # Highlight key error lines with background glow
        if idx in [3, 6, 7]:
            draw.rounded_rectangle([lx + 12, line_y - 4, lx + lw - 12, line_y + 32], radius=4,
                                   fill=(*col, int(35 * line_anim)))

        draw.text((lx + 20, line_y), ts, font=F_MONO_SM, fill=(*C_MUTED, la))
        draw.text((lx + 150, line_y), f"[{level:<5}]", font=F_MONO_BOLD, fill=(*col, la))
        draw.text((lx + 230, line_y), f"{logger:<28}", font=F_MONO_SM, fill=(*C_MUTED, la))
        msg_col = C_INK if col == C_MUTED else col
        draw.text((lx + 520, line_y), msg, font=F_MONO_SM, fill=(*msg_col, la))
        
        line_y += 42

    # Animated Vector connecting log line 4 (503) to line 7 (Circuit Breaker OPEN)
    if t > 4.5:
        vec_prog = min(1.0, (t - 4.5) / 1.5)
        v_y1 = ly + 64 + 3 * 42 + 10
        v_y2 = ly + 64 + 6 * 42 + 10
        cur_vy = v_y1 + int((v_y2 - v_y1) * vec_prog)
        draw.line([(lx + lw - 30, v_y1), (lx + lw - 15, v_y1), (lx + lw - 15, cur_vy)],
                  fill=C_COPPER_BRIGHT, width=2)
        if vec_prog >= 0.95:
            draw.polygon([(lx + lw - 25, v_y2), (lx + lw - 15, v_y2 + 8), (lx + lw - 5, v_y2)], fill=C_COPPER_BRIGHT)

    # Right: Analysis Panels (Observed Facts vs Probable Cause)
    rx = 1200
    rw = 620

    # Panel 1: Observed Facts
    if t > 1.5:
        p1_alpha = min(1.0, (t - 1.5) / 1.0)
        a1 = int(255 * p1_alpha)
        draw.rounded_rectangle([rx, 170, rx + rw, 520], radius=12,
                               fill=(*C_SURFACE, a1), outline=(*C_LINE, a1), width=1)
        draw.text((rx + 28, 195), "Observed Facts (Extracted Telemetry)", font=F_SM_BOLD, fill=(*C_TEAL, a1))
        
        facts = [
            ("API Endpoint", "POST /api/v1/checkout/payment", C_TEAL),
            ("Primary Failure", "HTTP 503 Service Unavailable", C_DANGER),
            ("Correlation ID", "CORR-9921-X9", C_AMBER),
            ("Circuit Breaker", "Tripped to OPEN state at 14:22:18", C_COPPER_BRIGHT),
            ("Retry Exhaustion", "3 attempts failed within 1.2s", C_DANGER),
        ]
        fy = 240
        for label, val, c_val in facts:
            draw.text((rx + 28, fy), label, font=F_XS, fill=(*C_MUTED, a1))
            draw.text((rx + 28, fy + 20), val, font=F_MONO_SM, fill=(*c_val, a1))
            fy += 52

    # Panel 2: Probable Cause (Hypothesis, Separated)
    if t > 5.0:
        p2_alpha = min(1.0, (t - 5.0) / 1.0)
        a2 = int(255 * p2_alpha)
        draw.rounded_rectangle([rx, 550, rx + rw, 940], radius=12,
                               fill=(*C_SURFACE, a2), outline=(*C_COPPER, a2), width=1)
        draw.text((rx + 28, 575), "Probable Cause (AI Synthesis)", font=F_SM_BOLD, fill=(*C_COPPER_BRIGHT, a2))
        
        cause_paragraphs = [
            "Upstream dependency 'stripe-relay' encountered socket timeout under peak load.",
            "Circuit breaker threshold (50%) breached, tripping to OPEN and failing fast on subsequent customer checkouts.",
            "Confidence category: HIGH (88%) based on correlation ID match across all 3 retry traces."
        ]
        cy = 620
        for p in cause_paragraphs:
            draw.text((rx + 28, cy), "• " + p[:42], font=F_BODY_BOLD, fill=(*C_INK, a2))
            draw.text((rx + 42, cy + 24), p[42:], font=F_BODY, fill=(*C_INK, a2))
            cy += 64

        # Compliance disclaimer
        draw.text((rx + 28, 880), "Evidence-backed hypothesis. Engineering verification recommended.",
                  font=F_XS, fill=(*C_MUTED, a2))

    return img.convert("RGB")

# -------------------------------------------------------------
# SCENE 5: Repository Discovery (30.0s – 38.0s | 240 frames)
# -------------------------------------------------------------
def render_scene_5(t, frame_idx):
    # t: 0.0 to 8.0 (absolute 30.0 to 38.0)
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    draw = ImageDraw.Draw(img)

    img.paste(GLOW_TEAL_MD, (int(W * 0.5 - 225), int(H * 0.4 - 225)), GLOW_TEAL_MD)

    # Header
    draw.text((120, 80), "Find the right repository. Start debugging faster.", font=F_TITLE_MD, fill=C_INK)
    draw.text((120, 134), "Automated service catalog lookup maps the failing endpoint to verified source code.",
              font=F_BODY, fill=C_MUTED)

    # Endpoint Box (Left)
    ex, ey, ew, eh = 120, 220, 500, 160
    draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((ex + 24, ey + 24), "DETECTED ENDPOINT", font=F_XS, fill=C_MUTED)
    draw.text((ex + 24, ey + 58), "POST /api/v1/checkout/payment", font=F_MONO_BOLD, fill=C_TEAL)
    draw.text((ex + 24, ey + 104), "Service: Nova Payment Gateway v2.4", font=F_SM, fill=C_MUTED)

    # Animated Copper Connection Arrow
    arr_prog = min(1.0, max(0.0, (t - 0.6) / 1.0))
    if arr_prog > 0:
        a_x1 = ex + ew + 20
        a_x2 = a_x1 + int(120 * arr_prog)
        a_y = ey + eh // 2
        draw.line([(a_x1, a_y), (a_x2, a_y)], fill=C_COPPER_BRIGHT, width=3)
        if arr_prog >= 0.9:
            draw.polygon([(a_x2, a_y - 8), (a_x2 + 16, a_y), (a_x2, a_y + 8)], fill=C_COPPER_BRIGHT)

    # Verified Repository Card (Right)
    if t > 1.2:
        rc_alpha = min(1.0, (t - 1.2) / 1.0)
        a_rc = int(255 * rc_alpha)
        rx, ry, rw, rh = 780, 200, 1020, 200
        draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=14,
                               fill=(*C_SURFACE, a_rc), outline=(*C_TEAL, a_rc), width=1)
        
        # Verified Badge
        draw.rounded_rectangle([rx + 28, ry + 24, rx + 240, ry + 56], radius=6, fill=(*C_TEAL, int(a_rc * 0.2)))
        draw.text((rx + 42, ry + 30), "✓ VERIFIED SERVICE REPO", font=F_XS, fill=(*C_TEAL, a_rc))

        # Repo Name
        draw.text((rx + 28, ry + 74), "nova-platform / payment-service", font=F_TITLE_SM, fill=(*C_INK, a_rc))
        draw.text((rx + 28, ry + 120), "Primary Owner: Team-Payment-Core  •  Language: Kotlin / Spring Boot  •  Default Branch: main",
                  font=F_SM, fill=(*C_MUTED, a_rc))
        draw.text((rx + 28, ry + 150), "Catalog Match Confidence: 100% (Endpoint registered in OpenAPI spec)",
                  font=F_XS, fill=(*C_COPPER_BRIGHT, a_rc))

    # Terminal Panel with Copy-Ready Command (Bottom)
    if t > 2.8:
        tm_alpha = min(1.0, (t - 2.8) / 1.0)
        a_tm = int(255 * tm_alpha)
        tx, ty, tw, th = 120, 460, 1680, 380
        draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=14,
                               fill=(6, 10, 18, a_tm), outline=(*C_LINE, a_tm), width=1)
        
        # Terminal Header Bar
        draw.rounded_rectangle([tx, ty, tx + tw, ty + 46], radius=14, fill=(*C_SURFACE_2, a_tm))
        draw.rectangle([tx, ty + 26, tx + tw, ty + 46], fill=(*C_SURFACE_2, a_tm))
        draw.ellipse([tx + 18, ty + 18, tx + 28, ty + 28], fill=C_DANGER)
        draw.ellipse([tx + 36, ty + 18, tx + 46, ty + 28], fill=C_AMBER)
        draw.ellipse([tx + 54, ty + 18, tx + 64, ty + 28], fill=C_TEAL)
        draw.text((tx + 84, ty + 16), "Quick Debug Shell — Approved Internal Clone URL", font=F_XS, fill=C_MUTED)

        # Clone Command
        draw.text((tx + 36, ty + 80), "# Clone approved service repository and checkout incident context branch:",
                  font=F_MONO_SM, fill=(*C_MUTED, a_tm))
        cmd_str = "git clone git@github.internal:nova-platform/payment-service.git"
        draw.text((tx + 36, ty + 124), "$ " + cmd_str, font=F_MONO_BOLD, fill=(*C_INK, a_tm))
        
        cmd_str_2 = "cd payment-service && ./scripts/replay-incident.sh --corrId=CORR-9921-X9"
        draw.text((tx + 36, ty + 174), "$ " + cmd_str_2, font=F_MONO, fill=(*C_TEAL, a_tm))

        # Copy Action Visual Animation
        copied_state = t > 5.0
        btn_col = C_TEAL if copied_state else C_ACCENT
        btn_txt = "✓ COPIED TO CLIPBOARD" if copied_state else "📋 COPY COMMAND"
        
        btn_x = tx + tw - 320
        btn_y = ty + 114
        draw.rounded_rectangle([btn_x, btn_y, btn_x + 280, btn_y + 50], radius=8,
                               fill=(*btn_col, int(a_tm * (0.9 if copied_state else 0.3))),
                               outline=(*btn_col, a_tm), width=1)
        draw.text((btn_x + 36, btn_y + 14), btn_txt, font=F_SM_BOLD, fill=(*C_INK, a_tm))

        # Helpful explanation
        draw.text((tx + 36, ty + 280), "Security policy: Only approved corporate git hosts and synthetic demo keys are permitted.",
                  font=F_XS, fill=(*C_MUTED, a_tm))

    return img.convert("RGB")

# -------------------------------------------------------------
# SCENE 6: Jira Comments & Email (38.0s – 47.0s | 270 frames)
# -------------------------------------------------------------
def render_scene_6(t, frame_idx):
    # t: 0.0 to 9.0 (absolute 38.0 to 47.0)
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((100, 50), "Clear reports. Better handoffs.", font=F_TITLE_MD, fill=C_INK)
    draw.text((100, 104), "Automated Jira root-cause comment and structured stakeholder notification email.",
              font=F_BODY, fill=C_MUTED)

    # Smooth Split Screen: Left (Jira Comment) & Right (Email Notification)
    split_prog = min(1.0, t / 1.0)
    a_split = int(255 * split_prog)

    # Center vertical subtle divider line
    div_x = W // 2
    draw.line([(div_x, 160), (div_x, 980)], fill=(*C_LINE, a_split), width=1)

    # LEFT: Jira Comment Card (Width: 800px)
    jx, jy, jw, jh = 100, 170, 800, 810
    draw.rounded_rectangle([jx, jy, jx + jw, jy + jh], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    
    # Jira Comment Header
    draw.rounded_rectangle([jx, jy, jx + jw, jy + 52], radius=12, fill=C_SURFACE_2)
    draw.rectangle([jx, jy + 32, jx + jw, jy + 52], fill=C_SURFACE_2)
    draw.text((jx + 24, jy + 16), "Jira Issue NOVA-1001 • Automated Investigation Comment", font=F_SM_BOLD, fill=C_ACCENT)

    # Jira Comment Content
    j_lines = [
        ("🤖 JiraPilot AI — Root Cause Analysis & Investigation Findings", F_BODY_BOLD, C_COPPER_BRIGHT),
        ("", F_XS, C_MUTED),
        ("Summary of Findings:", F_SM_BOLD, C_INK),
        ("• Upstream Dependency: stripe-relay timeout on /upstream/charge", F_SM, C_MUTED),
        ("• Error Pattern: 503 Service Unavailable cascading to circuit breaker", F_SM, C_MUTED),
        ("• Affected Correlation ID: CORR-9921-X9", F_MONO_SM, C_AMBER),
        ("", F_XS, C_MUTED),
        ("Remediation & Action Plan:", F_SM_BOLD, C_INK),
        ("1. Increase circuit breaker timeout threshold from 3000ms to 6000ms", F_SM, C_TEAL),
        ("2. Enable fallback degraded response for non-critical checkout items", F_SM, C_TEAL),
        ("3. Run synthetic load test suite in staging before production redeploy", F_SM, C_TEAL),
        ("", F_XS, C_MUTED),
        ("Source Code & Reproduction:", F_SM_BOLD, C_INK),
        ("Repo: nova-platform/payment-service (branch: fix/circuit-breaker-timeout)", F_MONO_SM, C_ACCENT),
        ("Generated Test Case: tests/regression/Nova1001CircuitBreakerTest.kt", F_MONO_SM, C_MUTED),
    ]
    cur_jy = jy + 76
    for txt, f, col in j_lines:
        if txt:
            draw.text((jx + 28, cur_jy), txt, font=f, fill=col)
        cur_jy += 34

    # RIGHT: Stakeholder Notification Email (Width: 800px)
    ex, ey, ew, eh = 1020, 170, 800, 810
    draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=12, fill=(248, 250, 252), outline=C_LINE, width=1)

    # Email Header
    draw.rounded_rectangle([ex, ey, ex + ew, ey + 64], radius=12, fill=(238, 242, 246))
    draw.rectangle([ex, ey + 44, ex + ew, ey + 64], fill=(238, 242, 246))
    draw.text((ex + 24, ey + 12), "From: JiraPilot AI <noreply@jirapilot.internal>", font=F_XS, fill=(71, 85, 105))
    draw.text((ex + 24, ey + 36), "Subject: [INCIDENT UPDATE] NOVA-1001 Payment 503 Investigation Complete",
              font=F_SM_BOLD, fill=(15, 23, 42))

    # Email Body (clean corporate typography)
    e_lines = [
        ("Hi Engineering Team,", F_SM, (51, 65, 85)),
        ("", F_XS, (0, 0, 0)),
        ("JiraPilot AI has concluded the automated diagnostic triage for NOVA-1001.", F_SM, (15, 23, 42)),
        ("The investigation report and suggested remediation have been posted to Jira.", F_SM, (15, 23, 42)),
        ("", F_XS, (0, 0, 0)),
        ("EXECUTIVE SUMMARY", F_SM_BOLD, (15, 118, 110)),
        ("• Incident Status: Root cause identified (High Confidence 88%)", F_SM, (15, 23, 42)),
        ("• Impacted Path: POST /api/v1/checkout/payment", F_MONO_SM, (30, 41, 59)),
        ("• Root Cause: SocketTimeoutException tripping upstream circuit breaker", F_SM, (185, 28, 28)),
        ("", F_XS, (0, 0, 0)),
        ("RECOMMENDED NEXT ACTIONS", F_SM_BOLD, (180, 83, 9)),
        ("• PR #482 created with circuit breaker configuration patch", F_SM, (15, 23, 42)),
        ("• Clone command and replay script ready in investigation card", F_SM, (15, 23, 42)),
        ("", F_XS, (0, 0, 0)),
        ("View full incident timeline: https://jirapilot.internal/issues/NOVA-1001", F_SM, (59, 92, 204))
    ]
    cur_ey = ey + 90
    for txt, f, col in e_lines:
        if txt:
            draw.text((ex + 28, cur_ey), txt, font=f, fill=col)
        cur_ey += 34

    return img.convert("RGB")

# -------------------------------------------------------------
# SCENE 7: Unified Workspace (47.0s – 54.0s | 210 frames)
# -------------------------------------------------------------
def render_scene_7(t, frame_idx):
    # t: 0.0 to 7.0 (absolute 47.0 to 54.0)
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    draw = ImageDraw.Draw(img)

    # Camera Pull-Back Parallax (Scale 1.05 down to 1.0)
    scale = 1.05 - 0.05 * min(1.0, t / 4.0)
    
    # Top Application Header Bar
    draw.rectangle([0, 0, W, 64], fill=C_SURFACE)
    draw.line([(0, 64), (W, 64)], fill=C_LINE, width=1)
    
    draw.text((32, 18), "JiraPilot AI", font=F_TITLE_SM, fill=C_INK)
    draw.text((220, 22), "• Incident Operations Workspace", font=F_SM, fill=C_MUTED)

    # Nav Tabs
    tabs = ["Dashboard", "Active Incidents", "Log Intelligence", "Service Catalog", "Audit History"]
    tx = 600
    for idx, tab in enumerate(tabs):
        is_active = (idx == 0)
        col = C_ACCENT if is_active else C_MUTED
        draw.text((tx, 22), tab, font=F_SM_BOLD if is_active else F_SM, fill=col)
        if is_active:
            draw.rectangle([tx - 4, 60, tx + 84, 64], fill=C_ACCENT)
        tx += 170

    # Main Dashboard Title & Tagline
    draw.text((60, 95), "One workspace. A clearer investigation.", font=F_TITLE_MD, fill=C_INK)
    draw.text((60, 146), "Evidence, next steps, and investigation status stay in one place.", font=F_BODY, fill=C_COPPER_BRIGHT)

    # 4 Top Metrics Cards
    metrics = [
        ("Total Ingested Issues", "24", C_INK, "Across all Jira cloud boards"),
        ("Awaiting Reporter Info", "3", C_AMBER, "Automated prompts delivered"),
        ("Ready for Investigation", "5", C_TEAL, "All diagnostic fields validated"),
        ("RCA Investigations Done", "16", C_COPPER_BRIGHT, "Findings & fixes synthesized")
    ]
    mx = 60
    for title, val, col, sub in metrics:
        draw.rounded_rectangle([mx, 190, mx + 420, 290], radius=10, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((mx + 20, 206), title, font=F_XS, fill=C_MUTED)
        draw.text((mx + 20, 228), val, font=get_font(38, bold=True), fill=col)
        draw.text((mx + 20, 268), sub, font=F_XS, fill=C_MUTED)
        mx += 460

    # 3-Column Workspace Layout (Bottom)
    col_y = 315
    col_h = 710

    # Col 1: Active Ticket Timeline
    c1_x, c1_w = 60, 560
    draw.rounded_rectangle([c1_x, col_y, c1_x + c1_w, col_y + col_h], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((c1_x + 24, col_y + 20), "Incident Activity Stream", font=F_SM_BOLD, fill=C_INK)
    
    stream = [
        ("NOVA-1001", "14:23 UTC", "Root cause synthesis complete (88% conf)", C_TEAL),
        ("NOVA-1001", "14:22 UTC", "Extracted HTTP 503 & correlation CORR-9921", C_AMBER),
        ("NOVA-1001", "14:22 UTC", "Ingested diagnostic log attachment (2.4MB)", C_ACCENT),
        ("NOVA-1002", "13:45 UTC", "Automated clarification sent to reporter", C_MUTED),
        ("NOVA-1003", "12:10 UTC", "Repository matched: nova-auth-service", C_TEAL),
        ("NOVA-1004", "11:05 UTC", "Reproduction test suite executed in CI", C_COPPER_BRIGHT),
    ]
    sy = col_y + 64
    for key, ts, desc, col in stream:
        draw.rounded_rectangle([c1_x + 20, sy, c1_x + c1_w - 20, sy + 76], radius=8, fill=C_SURFACE_2)
        draw.text((c1_x + 32, sy + 12), key, font=F_MONO_BOLD, fill=C_ACCENT)
        draw.text((c1_x + 150, sy + 14), ts, font=F_XS, fill=C_MUTED)
        draw.text((c1_x + 32, sy + 40), desc, font=F_SM, fill=col)
        sy += 92

    # Col 2: Evidence Timeline & Service Dependency Graph
    c2_x, c2_w = 660, 620
    draw.rounded_rectangle([c2_x, col_y, c2_x + c2_w, col_y + col_h], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((c2_x + 24, col_y + 20), "Service Dependency & Failure Graph", font=F_SM_BOLD, fill=C_INK)
    
    # Visual Service Graph Nodes
    # Client -> Gateway -> Payment -> Stripe
    nodes = [
        ("API Gateway", c2_x + 60, col_y + 120, C_TEAL, "Healthy"),
        ("Payment Service", c2_x + 240, col_y + 240, C_AMBER, "Degraded (503)"),
        ("Stripe Relay", c2_x + 440, col_y + 360, C_DANGER, "Timeout (Down)"),
        ("Database Cluster", c2_x + 120, col_y + 460, C_TEAL, "Healthy")
    ]
    # Draw connections
    draw.line([(c2_x + 130, col_y + 155), (c2_x + 270, col_y + 250)], fill=C_LINE, width=2)
    draw.line([(c2_x + 340, col_y + 280), (c2_x + 460, col_y + 370)], fill=C_DANGER, width=2)
    draw.line([(c2_x + 260, col_y + 285), (c2_x + 160, col_y + 460)], fill=C_LINE, width=2)

    for name, nx, ny, ncol, nsub in nodes:
        draw.rounded_rectangle([nx, ny, nx + 150, ny + 70], radius=8, fill=C_SURFACE_2, outline=ncol, width=1)
        draw.text((nx + 14, ny + 14), name, font=F_XS, fill=C_INK)
        draw.text((nx + 14, ny + 38), nsub, font=F_XS, fill=ncol)

    # Col 3: Recommended Next Actions
    c3_x, c3_w = 1320, 540
    draw.rounded_rectangle([c3_x, col_y, c3_x + c3_w, col_y + col_h], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((c3_x + 24, col_y + 20), "Next Developer Actions", font=F_SM_BOLD, fill=C_INK)

    actions = [
        ("Review Suggested PR #482", "Timeout threshold config update", C_ACCENT),
        ("Run Local Reproduction", "Replay CORR-9921 payload in test harness", C_TEAL),
        ("Sync Jira Status to IN PROGRESS", "Assigned to alex.chen", C_MUTED),
        ("Audit Telemetry Thresholds", "Update Prometheus alert rules", C_COPPER_BRIGHT)
    ]
    ay = col_y + 70
    for atitle, asub, acol in actions:
        draw.rounded_rectangle([c3_x + 20, ay, c3_x + c3_w - 20, ay + 90], radius=8, fill=C_SURFACE_2)
        draw.text((c3_x + 32, ay + 18), atitle, font=F_SM_BOLD, fill=acol)
        draw.text((c3_x + 32, ay + 48), asub, font=F_XS, fill=C_MUTED)
        ay += 110

    return img.convert("RGB")

# -------------------------------------------------------------
# SCENE 8: Closing Brand Reveal (54.0s – 60.0s | 180 frames)
# -------------------------------------------------------------
def render_scene_8(t, frame_idx):
    # t: 0.0 to 6.0 (absolute 54.0 to 60.0)
    img = Image.new("RGBA", (W, H), (*C_BG, 255))
    
    # Central warm copper radial glow
    glow_alpha = min(0.35, t * 0.1)
    gw = int(GLOW_COPPER_LG.width * (0.8 + t * 0.05))
    gh = int(GLOW_COPPER_LG.height * (0.8 + t * 0.05))
    glow_resized = GLOW_COPPER_LG.resize((gw, gh), Image.Resampling.BILINEAR)
    img.paste(glow_resized, (int(W * 0.5 - gw // 2), int(H * 0.45 - gh // 2)), glow_resized)

    draw = ImageDraw.Draw(img)

    # Elegant horizontal light sweep (t: 1.5 to 3.5)
    if 1.2 <= t <= 4.0:
        sweep_p = (t - 1.2) / 2.8
        sx = int(-200 + (W + 400) * sweep_p)
        for dx in range(-35, 36):
            fade = 1.0 - abs(dx) / 35.0
            a = int(120 * fade * (1.0 - abs(sweep_p - 0.5) * 1.5))
            if a > 0:
                draw.line([(sx + dx, H // 2 - 140), (sx + dx + 120, H // 2 + 140)],
                          fill=(*C_COPPER_BRIGHT, a), width=1)

    # Brand Title: "JiraPilot AI"
    logo_prog = min(1.0, max(0.0, (t - 0.4) / 1.2))
    a_logo = int(255 * logo_prog)

    font_brand = get_font(76, bold=True)
    part1 = "JiraPilot"
    part2 = " AI"
    b1 = draw.textbbox((0, 0), part1, font=font_brand)
    b2 = draw.textbbox((0, 0), part2, font=font_brand)
    w1 = b1[2] - b1[0]
    w2 = b2[2] - b2[0]
    bx = (W - (w1 + w2)) // 2
    by = H // 2 - 150

    draw.text((bx, by), part1, font=font_brand, fill=(*C_INK, a_logo))
    draw.text((bx + w1, by), part2, font=font_brand, fill=(*C_COPPER_BRIGHT, a_logo))

    # Copper accent underline bar
    bar_prog = min(1.0, max(0.0, (t - 1.2) / 0.8))
    bw = int(280 * bar_prog)
    if bw > 0:
        draw.rectangle([(W - bw) // 2, by + 104, (W + bw) // 2, by + 108], fill=C_COPPER)

    # Main Headline: "Less repetitive triage. More time to solve."
    head_prog = min(1.0, max(0.0, (t - 1.8) / 1.2))
    a_head = int(255 * head_prog)
    h_text = "Less repetitive triage. More time to solve."
    b_h = draw.textbbox((0, 0), h_text, font=F_TITLE_MD)
    hw = b_h[2] - b_h[0]
    draw.text(((W - hw) // 2, by + 135), h_text, font=F_TITLE_MD, fill=(*C_INK, a_head))

    # Supporting line: "JiraPilot AI — Your investigation copilot."
    sub_prog = min(1.0, max(0.0, (t - 2.8) / 1.0))
    a_sub = int(255 * sub_prog)
    s_text = "JiraPilot AI — Your investigation copilot."
    b_s = draw.textbbox((0, 0), s_text, font=F_BODY_BOLD)
    sw = b_s[2] - b_s[0]
    draw.text(((W - sw) // 2, by + 205), s_text, font=F_BODY_BOLD, fill=(*C_MUTED, a_sub))

    # Final quiet fadeout to black at 5.2s – 6.0s (59.2s – 60.0s)
    if t > 4.8:
        fade_out = min(1.0, (t - 4.8) / 1.2)
        fade_img = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fade_out)))
        img = Image.alpha_composite(img, fade_img)

    return img.convert("RGB")

# -------------------------------------------------------------
# Frame Dispatcher
# -------------------------------------------------------------
SCENE_TIMINGS = [
    (0.0, 5.0, render_scene_1, "Scene 1: The Problem"),
    (5.0, 12.0, render_scene_2, "Scene 2: Jira Issue Created"),
    (12.0, 20.0, render_scene_3, "Scene 3: Ticket Readiness"),
    (20.0, 30.0, render_scene_4, "Scene 4: AI Log Analysis"),
    (30.0, 38.0, render_scene_5, "Scene 5: Repository Discovery"),
    (38.0, 47.0, render_scene_6, "Scene 6: Jira Comments & Email"),
    (47.0, 54.0, render_scene_7, "Scene 7: Unified Workspace"),
    (54.0, 60.0, render_scene_8, "Scene 8: Closing Brand Reveal")
]

def get_frame(global_frame_idx):
    global_t = global_frame_idx / float(FPS)
    for start_t, end_t, fn, name in SCENE_TIMINGS:
        if start_t <= global_t < end_t:
            local_t = global_t - start_t
            return fn(local_t, global_frame_idx)
    # Fallback to last frame of scene 8
    return render_scene_8(6.0, global_frame_idx)

# Export standalone closing title card
def export_title_card():
    card_img = render_scene_8(3.5, 0)
    card_path = os.path.join(OUT_DIR, "closing_title_card.png")
    card_img.save(card_path, "PNG")
    print(f"[OK] Saved closing title card: {card_path}")

if __name__ == "__main__":
    export_title_card()
    print("Renderer loaded successfully.")
