"""
Render 5 High-Quality Workflow GIFs for JiraPilot AI
Resolution: 1280x720 (16:9)
Style: Deep purple and black palette (#08070D / #170B2B / #8B5CF6 / #C4B5FD)
Uses Pillow frame generation + FFmpeg palettegen for crisp, smooth GIF encoding.
"""

import os
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIF_DIR = os.path.join(BASE_DIR, "assets", "gifs")
os.makedirs(GIF_DIR, exist_ok=True)

GW, GH = 1280, 720
FPS = 15  # 15 fps gives buttery smooth motion at optimal GIF file size

# Color tokens
C_NEAR_BLACK = (8, 7, 13)       # #08070D
C_DEEP_PURPLE = (23, 11, 43)    # #170B2B
C_SURFACE = (22, 16, 38)        # #161026
C_SURFACE_2 = (30, 22, 52)      # #1e1634
C_LINE = (55, 42, 85)           # #372a55
C_VIOLET = (139, 92, 246)       # #8B5CF6
C_LAVENDER = (196, 181, 253)    # #C4B5FD
C_WHITE = (255, 255, 255)
C_MUTED = (184, 179, 199)       # #B8B3C7
C_TEAL = (45, 212, 191)         # #2dd4bf (Success)
C_AMBER = (251, 191, 36)        # #fbbf24 (Missing info)
C_DANGER = (248, 113, 113)      # #f87171 (Errors)

def get_font(size, bold=False, mono=False):
    if mono:
        path = "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"
    else:
        path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

F_TITLE = get_font(32, bold=True)
F_SUB = get_font(20, bold=False)
F_HEADING = get_font(22, bold=True)
F_BODY = get_font(18, bold=False)
F_BODY_B = get_font(18, bold=True)
F_SM = get_font(15, bold=False)
F_SM_B = get_font(15, bold=True)
F_XS = get_font(13, bold=False)
F_MONO = get_font(16, bold=False, mono=True)
F_MONO_B = get_font(16, bold=True, mono=True)
F_MONO_SM = get_font(13, bold=False, mono=True)

def base_frame():
    img = Image.new("RGBA", (GW, GH), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)
    # Radial purple ambient gradient in background
    cx, cy = GW // 2, GH // 2
    for r in [520, 380, 240, 120]:
        alpha = int(32 * (1 - r / 520))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*C_DEEP_PURPLE, alpha))
    return img

def encode_gif_with_ffmpeg(frame_generator, total_frames, output_path):
    """Pipes raw frames into ffmpeg with two-pass palettegen for ultra-clean GIF."""
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{GW}x{GH}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-vf", "split[s0][s1];[s0]palettegen=max_colors=128:reserve_transparent=0[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
        output_path
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(total_frames):
        img = frame_generator(i / float(FPS), i)
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"[OK] Rendered GIF: {output_path}")

# =========================================================================
# GIF 01: 01-jira-ticket-readiness.gif (Duration: 5.0s | 75 frames)
# =========================================================================
def render_gif_01_frame(t, idx):
    # t: 0.0 to 5.0
    img = base_frame()
    draw = ImageDraw.Draw(img)

    # Top Brand / Header bar
    draw.text((50, 30), "JiraPilot AI", font=F_HEADING, fill=C_LAVENDER)
    draw.text((195, 33), "• Automated Ticket Readiness Evaluation", font=F_SM, fill=C_MUTED)

    # 1. Jira Ticket Entry (Slide in from left: 0.0s - 1.0s)
    slide_p = min(1.0, t / 0.8)
    card_x = int(-500 + (50 - (-500)) * (1.0 - (1.0 - slide_p)**2))
    card_y = 80
    cw, ch = 520, 580

    # Ticket Card NOVA-1001
    draw.rounded_rectangle([card_x, card_y, card_x + cw, card_y + ch], radius=12,
                           fill=C_SURFACE, outline=C_LINE, width=1)
    
    # Header bar
    draw.rounded_rectangle([card_x, card_y, card_x + cw, card_y + 46], radius=12, fill=C_SURFACE_2)
    draw.rectangle([card_x, card_y + 26, card_x + cw, card_y + 46], fill=C_SURFACE_2)
    
    # Key badge
    draw.rounded_rectangle([card_x + 18, card_y + 10, card_x + 120, card_y + 36], radius=5,
                           fill=(*C_VIOLET, 60), outline=C_VIOLET, width=1)
    draw.text((card_x + 28, card_y + 14), "NOVA-1001", font=F_MONO_B, fill=C_WHITE)
    draw.text((card_x + 135, card_y + 15), "Status: OPEN  •  Priority: High", font=F_XS, fill=C_MUTED)

    # Summary
    draw.text((card_x + 20, card_y + 60), "Summary:", font=F_XS, fill=C_MUTED)
    draw.text((card_x + 20, card_y + 80), "Resource allocation fails under peak load", font=F_BODY_B, fill=C_WHITE)

    # Fields inside ticket
    t_fields = [
        ("Reporter", "qa-automation@northstar.internal"),
        ("Environment", "production-cluster-04"),
        ("Service", "resource-inventory-service"),
        ("API Endpoint", "POST /api/v1/resources/allocate"),
        ("Server Logs", "[MISSING - Not attached]"),
        ("Payload JSON", "[MISSING - No sample payload]")
    ]
    ty = card_y + 130
    for label, val in t_fields:
        draw.text((card_x + 20, ty), label + ":", font=F_XS, fill=C_MUTED)
        is_missing = "[MISSING" in val
        col = C_AMBER if is_missing else C_WHITE
        draw.text((card_x + 130, ty), val, font=F_MONO_SM if is_missing else F_SM, fill=col)
        ty += 42

    # 2. Validation Checklist (Right Side, appears one by one: 1.0s - 3.0s)
    rx = 600
    rw = 630
    draw.rounded_rectangle([rx, 80, rx + rw, 390], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((rx + 24, 100), "Ticket Completeness Audit", font=F_HEADING, fill=C_WHITE)
    
    score_p = min(1.0, max(0.0, (t - 0.8) / 2.0))
    score_val = int(50 * score_p)
    draw.rounded_rectangle([rx + rw - 130, 96, rx + rw - 24, 130], radius=6, fill=(*C_AMBER, 40), outline=C_AMBER)
    draw.text((rx + rw - 118, 102), f"Score: {score_val}%", font=F_SM_B, fill=C_AMBER)

    checks = [
        ("Description & Environment", True, "Clear problem scope identified"),
        ("API Endpoint & Method", True, "POST /api/v1/resources/allocate"),
        ("Application Server Logs", False, "MISSING: Error stack trace required"),
        ("Request Payload Sample", False, "MISSING: Raw JSON correlation data required")
    ]
    
    cy = 145
    for c_idx, (c_label, c_ok, c_sub) in enumerate(checks):
        c_appear = min(1.0, max(0.0, (t - (1.0 + c_idx * 0.4)) / 0.3))
        if c_appear <= 0:
            continue
        c_alpha = int(255 * c_appear)
        
        c_border = C_TEAL if c_ok else C_AMBER
        c_bg = (16, 42, 38) if c_ok else (45, 32, 14)
        draw.rounded_rectangle([rx + 20, cy, rx + rw - 20, cy + 50], radius=8,
                               fill=(*c_bg, c_alpha), outline=(*c_border, c_alpha), width=1)
        
        icon = "✓" if c_ok else "!"
        draw.text((rx + 36, cy + 14), icon, font=F_BODY_B, fill=(*c_border, c_alpha))
        draw.text((rx + 65, cy + 12), c_label, font=F_SM_B, fill=(*C_WHITE, c_alpha))
        draw.text((rx + 320, cy + 14), c_sub, font=F_XS, fill=(*c_border, c_alpha))
        
        cy += 58

    # 3. Clarification Comment Preview (Bottom Right: appears after 3.0s)
    if t > 2.8:
        comm_p = min(1.0, (t - 2.8) / 0.8)
        c_a = int(255 * comm_p)
        draw.rounded_rectangle([rx, 410, rx + rw, 660], radius=12,
                               fill=(*C_SURFACE_2, c_a), outline=(*C_VIOLET, c_a), width=1)
        draw.text((rx + 24, 428), "⚡ Prepared Jira Clarification Comment", font=F_SM_B, fill=(*C_LAVENDER, c_a))
        
        comm_lines = [
            "\"Hello @reporter — JiraPilot AI scanned NOVA-1001 for diagnostic completeness.",
            "To start deep automated triage, please reply with:",
            "  1. Server logs around the time of the failure",
            "  2. Correlation ID or sample request payload",
            "Status updated to: WAITING_FOR_INFO (Investigation paused).\""
        ]
        cmy = 464
        for cline in comm_lines:
            draw.text((rx + 24, cmy), cline, font=F_SM, fill=(*C_WHITE, c_a))
            cmy += 26

        # Next action state badge
        draw.rounded_rectangle([rx + 24, 615, rx + 330, 645], radius=5, fill=(*C_AMBER, int(c_a * 0.3)), outline=C_AMBER)
        draw.text((rx + 36, 620), "STATUS: WAITING_FOR_INFO", font=F_XS, fill=(*C_AMBER, c_a))

    return img

# =========================================================================
# GIF 02: 02-log-analysis.gif (Duration: 5.0s | 75 frames)
# =========================================================================
def render_gif_02_frame(t, idx):
    img = base_frame()
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((50, 30), "JiraPilot AI", font=F_HEADING, fill=C_LAVENDER)
    draw.text((195, 33), "• Automated Log Evidence Extraction", font=F_SM, fill=C_MUTED)

    # Log viewer panel (Left: 720px wide)
    lx, ly, lw, lh = 50, 80, 700, 580
    draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=12, fill=(6, 5, 12), outline=C_LINE, width=1)
    
    # Terminal header
    draw.rounded_rectangle([lx, ly, lx + lw, ly + 40], radius=12, fill=C_SURFACE_2)
    draw.rectangle([lx, ly + 20, lx + lw, ly + 40], fill=C_SURFACE_2)
    draw.ellipse([lx + 15, ly + 14, lx + 25, ly + 24], fill=C_DANGER)
    draw.ellipse([lx + 32, ly + 14, lx + 42, ly + 24], fill=C_AMBER)
    draw.ellipse([lx + 49, ly + 14, lx + 59, ly + 24], fill=C_TEAL)
    draw.text((lx + 75, ly + 12), "application-demo.log  •  CORR-DEMO-1001", font=F_XS, fill=C_MUTED)

    # Synthetic log lines
    raw_logs = [
        ("14:22:12", "INFO",  "Dispatcher", "Received POST /api/v1/resources/allocate", C_MUTED),
        ("14:22:13", "INFO",  "Validator",  "CorrelationId recognized: CORR-DEMO-1001", C_MUTED),
        ("14:22:15", "WARN",  "DbPool",     "Connection latency spike: 420ms on cluster", C_AMBER),
        ("14:22:17", "ERROR", "Allocation", "HTTP 503 Service Unavailable on /api/v1/resources", C_DANGER),
        ("14:22:18", "ERROR", "Allocation", "Failed to reserve resource-1001 status=503", C_DANGER),
        ("14:22:19", "FATAL", "RetryMgr",   "Exhausted 3 retries for CORR-DEMO-1001", C_DANGER),
        ("14:22:20", "WARN",  "Gateway",    "Circuit breaker OPEN for resource-inventory-service", C_AMBER)
    ]

    log_y = ly + 58
    for l_idx, (ts, lvl, tag, msg, col) in enumerate(raw_logs):
        l_anim = min(1.0, max(0.0, (t - l_idx * 0.3) / 0.2))
        if l_anim <= 0:
            continue
        la = int(255 * l_anim)
        
        # Highlight important evidence lines
        if l_idx in [3, 4, 5] and t > 2.0:
            glow_a = int(45 * min(1.0, (t - 2.0) / 0.8))
            draw.rounded_rectangle([lx + 10, log_y - 2, lx + lw - 10, log_y + 30], radius=4,
                                   fill=(*C_VIOLET, glow_a))

        draw.text((lx + 15, log_y), ts, font=F_MONO_SM, fill=(*C_MUTED, la))
        draw.text((lx + 90, log_y), f"[{lvl:<5}]", font=F_MONO_B, fill=(*col, la))
        draw.text((lx + 160, log_y), f"{tag:<10}", font=F_MONO_SM, fill=(*C_MUTED, la))
        msg_col = C_WHITE if col == C_MUTED else col
        draw.text((lx + 260, log_y), msg, font=F_MONO_SM, fill=(*msg_col, la))
        
        log_y += 38

    # Connecting vector lines between log line 3 and line 5 (t > 2.5)
    if t > 2.5:
        line_p = min(1.0, (t - 2.5) / 1.0)
        v_y1 = ly + 58 + 3 * 38 + 12
        v_y2 = ly + 58 + 5 * 38 + 12
        cur_y = v_y1 + int((v_y2 - v_y1) * line_p)
        draw.line([(lx + lw - 25, v_y1), (lx + lw - 12, v_y1), (lx + lw - 12, cur_y)], fill=C_VIOLET, width=2)
        if line_p >= 0.95:
            draw.polygon([(lx + lw - 18, v_y2), (lx + lw - 12, v_y2 + 6), (lx + lw - 6, v_y2)], fill=C_VIOLET)

    # Right side: Structured Evidence Group + Probable Cause (Right: 460px wide)
    rx = 780
    rw = 450
    if t > 1.2:
        ev_p = min(1.0, (t - 1.2) / 0.8)
        ea = int(255 * ev_p)
        
        # Card 1: Extracted Evidence
        draw.rounded_rectangle([rx, 80, rx + rw, 350], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((rx + 20, 100), "Extracted Evidence Group", font=F_HEADING, fill=(*C_LAVENDER, ea))
        
        ev_items = [
            ("Detected Endpoint", "POST /api/v1/resources", C_TEAL),
            ("HTTP Error Status", "503 Service Unavailable", C_DANGER),
            ("Correlation ID", "CORR-DEMO-1001", C_LAVENDER),
            ("Log Source File", "application-demo.log", C_WHITE),
            ("Circuit Breaker", "OPEN after 3 retries", C_AMBER)
        ]
        ey = 145
        for k, v, c in ev_items:
            draw.text((rx + 20, ey), k + ":", font=F_XS, fill=(*C_MUTED, ea))
            draw.text((rx + 160, ey), v, font=F_MONO_SM, fill=(*c, ea))
            ey += 38

    # Card 2: Probable Cause (t > 3.0)
    if t > 3.0:
        pc_p = min(1.0, (t - 3.0) / 0.8)
        pca = int(255 * pc_p)
        
        draw.rounded_rectangle([rx, 370, rx + rw, 660], radius=12,
                               fill=(*C_SURFACE_2, pca), outline=(*C_AMBER, pca), width=1)
        
        # Pill
        draw.rounded_rectangle([rx + 20, 390, rx + rw - 20, 424], radius=6, fill=(*C_AMBER, int(pca * 0.25)))
        draw.text((rx + 30, 397), "⚠ PROBABLE CAUSE — VERIFICATION REQUIRED", font=F_XS, fill=(*C_AMBER, pca))

        cause_text = (
            "Upstream resource inventory database connection pool\n"
            "timed out under peak allocation traffic.\n\n"
            "Circuit breaker tripped to OPEN, returning 503 to client.\n"
            "Confidence: 88% (Synthesized hypothesis based on logs)."
        )
        draw.text((rx + 20, 440), cause_text, font=F_SM, fill=(*C_WHITE, pca))

    return img

# =========================================================================
# GIF 03: 03-repository-discovery.gif (Duration: 5.0s | 75 frames)
# =========================================================================
def render_gif_03_frame(t, idx):
    img = base_frame()
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((50, 30), "JiraPilot AI", font=F_HEADING, fill=C_LAVENDER)
    draw.text((195, 33), "• Approved Repository Discovery & Matching", font=F_SM, fill=C_MUTED)

    # Step 1: Extracted Endpoint & Service (0.0s - 1.0s)
    ex, ey, ew, eh = 50, 90, 1180, 110
    draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((ex + 25, ey + 20), "INCIDENT EVIDENCE SIGNALS", font=F_XS, fill=C_MUTED)
    draw.text((ex + 25, ey + 50), "Endpoint: POST /api/v1/resources/allocate", font=F_MONO_B, fill=C_TEAL)
    draw.text((ex + 620, ey + 50), "Target Service: resource-inventory-service", font=F_MONO_B, fill=C_LAVENDER)
    draw.text((ex + 25, ey + 80), "Matching Strategy: Route Match + Service ID + Package Hierarchy", font=F_XS, fill=C_MUTED)

    # Step 2: Candidate Repositories Ranked (1.0s - 3.0s)
    repos = [
        ("resource-inventory-service", "https://github.com/northstar-labs/resource-inventory-service.git", "96% MATCH (VERIFIED)", True),
        ("capacity-planning-api", "https://github.com/northstar-labs/capacity-planning-api.git", "42% Match (Related group)", False),
        ("integration-gateway", "https://github.com/northstar-labs/integration-gateway.git", "28% Match (Route proxy)", False)
    ]

    ry = 220
    for r_idx, (r_name, r_url, r_badge, is_best) in enumerate(repos):
        r_anim = min(1.0, max(0.0, (t - (1.0 + r_idx * 0.4)) / 0.3))
        if r_anim <= 0:
            continue
        ra = int(255 * r_anim)
        
        border_col = C_TEAL if is_best else C_LINE
        bg_col = (18, 38, 35) if is_best else C_SURFACE
        
        draw.rounded_rectangle([50, ry, 1230, ry + 75], radius=10,
                               fill=(*bg_col, ra), outline=(*border_col, ra), width=2 if is_best else 1)
        
        draw.text((75, ry + 15), r_name, font=F_BODY_B, fill=(*C_WHITE, ra))
        draw.text((75, ry + 42), r_url, font=F_MONO_SM, fill=(*C_MUTED, ra))
        
        # Badge
        badge_bg = C_TEAL if is_best else C_LINE
        draw.rounded_rectangle([1000, ry + 22, 1205, ry + 52], radius=6, fill=(*badge_bg, int(ra * 0.25)))
        draw.text((1015, ry + 28), r_badge, font=F_XS, fill=(*badge_bg, ra))
        
        ry += 90

    # Step 3: Terminal Clone Command Revealed (t > 2.8s)
    if t > 2.6:
        cmd_p = min(1.0, (t - 2.6) / 0.8)
        ca = int(255 * cmd_p)
        
        tx, ty, tw, th = 50, 500, 1180, 160
        draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=12, fill=(6, 5, 12, ca), outline=(*C_VIOLET, ca), width=1)
        draw.rounded_rectangle([tx, ty, tx + tw, ty + 36], radius=12, fill=(*C_SURFACE_2, ca))
        draw.text((tx + 20, ty + 10), "Quick Clone for Local Debugging (Approved Synthetic Repo)", font=F_XS, fill=(*C_MUTED, ca))

        clone_cmd = "git clone https://github.com/northstar-labs/resource-inventory-service.git"
        draw.text((tx + 25, ty + 55), "$ " + clone_cmd, font=F_MONO_B, fill=(*C_WHITE, ca))

        # Copy animation button
        copied = t > 4.0
        btn_txt = "✓ COPIED TO CLIPBOARD" if copied else "📋 COPY COMMAND"
        btn_col = C_TEAL if copied else C_VIOLET
        draw.rounded_rectangle([tx + tw - 240, ty + 46, tx + tw - 20, ty + 84], radius=6,
                               fill=(*btn_col, int(ca * 0.3)), outline=(*btn_col, ca))
        draw.text((tx + tw - 225, ty + 55), btn_txt, font=F_XS, fill=(*btn_col, ca))

        # Important Note: Recommendation only
        draw.text((tx + 25, ty + 115),
                  "Note: Repository recommendation is an evidence-backed starting point, not proof of root cause.",
                  font=F_XS, fill=(*C_MUTED, ca))

    return img

# =========================================================================
# GIF 04: 04-jira-email-reporting.gif (Duration: 5.0s | 75 frames)
# =========================================================================
def render_gif_04_frame(t, idx):
    img = base_frame()
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((50, 30), "JiraPilot AI", font=F_HEADING, fill=C_LAVENDER)
    draw.text((195, 33), "• Automated Investigation Reports & Notifications", font=F_SM, fill=C_MUTED)

    # Split Screen: Left (Jira Comment) & Right (Email Preview)
    # Left: Jira Comment Card (570px wide)
    jx, jy, jw, jh = 50, 80, 570, 580
    draw.rounded_rectangle([jx, jy, jx + jw, jy + jh], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    
    draw.rounded_rectangle([jx, jy, jx + jw, jy + 44], radius=12, fill=C_SURFACE_2)
    draw.rectangle([jx, jy + 24, jx + jw, jy + 44], fill=C_SURFACE_2)
    draw.text((jx + 20, jy + 13), "Jira Issue Comment (NOVA-1001)", font=F_SM_B, fill=C_LAVENDER)

    j_content = [
        ("📋 Investigation Summary", F_BODY_B, C_WHITE),
        ("POST /api/v1/resources/allocate returned HTTP 503.", F_SM, C_MUTED),
        ("", F_XS, C_MUTED),
        ("Key Evidence:", F_SM_B, C_WHITE),
        ("• Correlation ID: CORR-DEMO-1001", F_MONO_SM, C_LAVENDER),
        ("• Circuit breaker tripped after 3 retries", F_SM, C_AMBER),
        ("", F_XS, C_MUTED),
        ("Suggested Action:", F_SM_B, C_WHITE),
        ("• Inspect DB pool sizing in resource-inventory-service", F_SM, C_TEAL),
        ("• Clone: github.com/northstar-labs/resource-inventory-service", F_MONO_SM, C_MUTED),
        ("", F_XS, C_MUTED),
        ("Note: Requires engineer verification before merge.", F_XS, C_MUTED)
    ]
    cur_jy = jy + 60
    for txt, f, col in j_content:
        if txt:
            draw.text((jx + 20, cur_jy), txt, font=f, fill=col)
        cur_jy += 30

    # Right: Email Preview Card (appears at t > 1.2s)
    ex, ey, ew, eh = 660, 80, 570, 580
    if t > 1.0:
        ep_anim = min(1.0, (t - 1.0) / 0.8)
        ea = int(255 * ep_anim)
        
        draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=12,
                               fill=(248, 246, 252, ea), outline=(*C_LINE, ea), width=1)
        
        draw.rounded_rectangle([ex, ey, ex + ew, ey + 60], radius=12, fill=(235, 230, 245, ea))
        draw.text((ex + 20, ey + 10), "Subject: [JiraPilot AI] NOVA-1001 Investigation Findings",
                  font=F_SM_B, fill=(*C_NEAR_BLACK, ea))
        draw.text((ex + 20, ey + 34), "To: SRE-OnCall@northstar.internal", font=F_XS, fill=(80, 70, 100, ea))

        email_lines = [
            ("Team,", F_SM, C_NEAR_BLACK),
            ("JiraPilot AI finished diagnostic analysis for NOVA-1001.", F_SM, C_NEAR_BLACK),
            ("", F_XS, C_NEAR_BLACK),
            ("INCIDENT FINDINGS", F_SM_B, (110, 65, 215)),
            ("• Service: resource-inventory-service", F_SM, C_NEAR_BLACK),
            ("• Error: HTTP 503 SocketTimeout", F_SM, (180, 40, 40)),
            ("• Probable Cause: DB Connection Pool Exhaustion", F_SM, C_NEAR_BLACK),
            ("", F_XS, C_NEAR_BLACK),
            ("NEXT STEPS", F_SM_B, (30, 120, 110)),
            ("• Review patch branch: fix/db-pool-timeout", F_SM, C_NEAR_BLACK),
            ("• Full telemetry: https://dashboard.northstar.internal", F_SM, (60, 80, 180)),
        ]
        ey_body = ey + 75
        for etxt, ef, ecol in email_lines:
            if etxt:
                draw.text((ex + 20, ey_body), etxt, font=ef, fill=(*ecol, ea))
            ey_body += 28

        # Simulated Delivery Badge (t > 3.0s)
        if t > 2.8:
            sent_p = min(1.0, (t - 2.8) / 0.6)
            sa = int(255 * sent_p)
            draw.rounded_rectangle([ex + 20, ey + eh - 60, ex + ew - 20, ey + eh - 18], radius=6,
                                   fill=(35, 120, 100, sa))
            draw.text((ex + 35, ey + eh - 46), "✓ NOTIFICATION DELIVERED (Simulated Demo Mode)",
                      font=F_SM_B, fill=(*C_WHITE, sa))

    return img

# =========================================================================
# GIF 05: 05-end-to-end-workflow.gif (Duration: 6.0s | 90 frames)
# =========================================================================
def render_gif_05_frame(t, idx):
    img = base_frame()
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((50, 40), "JiraPilot AI — End-to-End Investigation Lifecycle", font=F_TITLE, fill=C_WHITE)
    draw.text((50, 85), "Turn incoming incident tickets into actionable developer handoffs in 6 connected steps.",
              font=F_SUB, fill=C_MUTED)

    # 6 Workflow Step Nodes
    steps = [
        ("1. Jira Issue", "NOVA-1001 Created", "Ingest webhook"),
        ("2. Readiness", "Validate Fields", "Identify gaps"),
        ("3. Log Analysis", "Extract Telemetry", "Group evidence"),
        ("4. Repo Match", "Service Catalog", "Generate clone"),
        ("5. Reporting", "Jira & Email", "Clear updates"),
        ("6. Dashboard", "Unified View", "Track status")
    ]

    # Node positions
    node_w, node_h = 175, 260
    gap = 24
    start_x = 50
    node_y = 180

    # Moving progress highlight pulse (cycles across the 6 steps)
    active_idx = int((t / 6.0) * len(steps)) % len(steps)
    pulse_fraction = (t * 2.0) % 1.0

    for s_idx, (s_title, s_sub, s_detail) in enumerate(steps):
        nx = start_x + s_idx * (node_w + gap)
        is_active = (s_idx == active_idx)
        is_past = (s_idx < active_idx)

        # Connector arrow to next step
        if s_idx < len(steps) - 1:
            ax1 = nx + node_w + 4
            ax2 = ax1 + gap - 8
            ay = node_y + node_h // 2
            arr_col = C_VIOLET if is_past or is_active else C_LINE
            draw.line([(ax1, ay), (ax2, ay)], fill=arr_col, width=2)
            draw.polygon([(ax2, ay - 4), (ax2 + 6, ay), (ax2, ay + 4)], fill=arr_col)

        # Node Box
        border_col = C_VIOLET if is_active else (C_TEAL if is_past else C_LINE)
        bg_col = C_SURFACE_2 if is_active else C_SURFACE
        
        draw.rounded_rectangle([nx, node_y, nx + node_w, node_y + node_h], radius=12,
                               fill=bg_col, outline=border_col, width=2 if is_active else 1)

        # Active glowing border
        if is_active:
            glow_box = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow_box)
            gd.rounded_rectangle([nx - 4, node_y - 4, nx + node_w + 4, node_y + node_h + 4],
                                 radius=14, outline=(*C_VIOLET, 120), width=3)
            img = Image.alpha_composite(img, glow_box)
            draw = ImageDraw.Draw(img)

        # Step Icon Circle
        circ_col = C_VIOLET if is_active else (C_TEAL if is_past else C_LINE)
        draw.ellipse([nx + node_w // 2 - 24, node_y + 24, nx + node_w // 2 + 24, node_y + 72],
                     fill=(*circ_col, 50), outline=circ_col, width=2)
        draw.text((nx + node_w // 2 - 6, node_y + 36), str(s_idx + 1), font=F_HEADING, fill=C_WHITE)

        # Step Text
        draw.text((nx + 14, node_y + 90), s_title, font=F_SM_B, fill=C_LAVENDER if is_active else C_WHITE)
        draw.text((nx + 14, node_y + 125), s_sub, font=F_SM, fill=C_WHITE if is_active else C_MUTED)
        draw.text((nx + 14, node_y + 155), s_detail, font=F_XS, fill=C_MUTED)

        # Status badge at bottom of node
        status_txt = "ACTIVE" if is_active else ("DONE" if is_past else "QUEUED")
        st_col = C_VIOLET if is_active else (C_TEAL if is_past else C_MUTED)
        draw.rounded_rectangle([nx + 14, node_y + 205, nx + node_w - 14, node_y + 235],
                               radius=5, fill=(*st_col, 40))
        draw.text((nx + 24, node_y + 212), status_txt, font=F_XS, fill=st_col)

    # Bottom summary card
    draw.rounded_rectangle([50, 480, 1230, 660], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((80, 505), "Key Operational Guarantee:", font=F_HEADING, fill=C_LAVENDER)
    draw.text((80, 545),
              "• Developers remain in complete control: AI synthesizes evidence and prepares reproduction,\n"
              "  while engineers verify root causes and approve remediation before production deploy.",
              font=F_BODY, fill=C_WHITE)
    draw.text((80, 615),
              "• Zero invented URLs: All repositories, API paths, and correlation keys are strictly verified against the catalog.",
              font=F_SM, fill=C_MUTED)

    return img

def render_all_gifs():
    print("=" * 60)
    print("Rendering 5 JiraPilot AI Workflow GIFs (1280x720)...")
    print("=" * 60)

    gif_specs = [
        ("01-jira-ticket-readiness.gif", render_gif_01_frame, 75),  # 5.0s
        ("02-log-analysis.gif",          render_gif_02_frame, 75),  # 5.0s
        ("03-repository-discovery.gif",   render_gif_03_frame, 75),  # 5.0s
        ("04-jira-email-reporting.gif",   render_gif_04_frame, 75),  # 5.0s
        ("05-end-to-end-workflow.gif",   render_gif_05_frame, 90),  # 6.0s
    ]

    for filename, fn, n_frames in gif_specs:
        out_path = os.path.join(GIF_DIR, filename)
        print(f"Rendering {filename} ({n_frames} frames @ {FPS} fps)...")
        encode_gif_with_ffmpeg(fn, n_frames, out_path)

    print("\n[OK] All 5 workflow GIFs rendered successfully in:", GIF_DIR)

if __name__ == "__main__":
    render_all_gifs()
