"""
JiraPilot AI — Premium 60-Second Product Demonstration Film (Deep Purple Aesthetic)
Target Output: presentation/JiraPilot-AI-Product-Demo.mp4
Duration: Exactly 60.00 seconds (1800 frames @ 30fps)
Resolution: 1920x1080 (16:9)
Style: Deep purple / black enterprise SaaS film with concentric violet light rings,
       original geometric flight emblem, VO narration, ambient music, and synchronized captions.
"""

import os
import sys
import math
import wave
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
VO_DIR = os.path.join(BASE_DIR, "assets", "voiceover")
VID_DIR = os.path.join(BASE_DIR, "assets", "video")
OUT_MP4 = os.path.join(BASE_DIR, "JiraPilot-AI-Product-Demo.mp4")

for d in [IMG_DIR, VO_DIR, VID_DIR]:
    os.makedirs(d, exist_ok=True)

W, H = 1920, 1080
FPS = 30
TOTAL_DURATION = 60.0
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)  # 1800 frames

# Color Tokens (Black and Deep Purple Design System)
C_NEAR_BLACK = (8, 7, 13)       # #08070D
C_DEEP_PURPLE = (23, 11, 43)    # #170B2B
C_SURFACE = (22, 16, 38)        # #161026
C_SURFACE_2 = (30, 22, 52)      # #1e1634
C_LINE = (55, 42, 85)           # #372a55
C_VIOLET = (139, 92, 246)       # #8B5CF6 (Primary Glow)
C_LAVENDER = (196, 181, 253)    # #C4B5FD (Secondary Accent)
C_WHITE = (255, 255, 255)
C_MUTED = (184, 179, 199)       # #B8B3C7
C_TEAL = (45, 212, 191)         # #2dd4bf (Success)
C_AMBER = (251, 191, 36)        # #fbbf24 (Missing info)
C_DANGER = (248, 113, 113)      # #f87171 (Error)

def get_font(size, bold=False, mono=False):
    if mono:
        path = "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"
    else:
        path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

F_DISPLAY = get_font(64, bold=True)
F_TITLE = get_font(44, bold=True)
F_SUB = get_font(26, bold=False)
F_HEADING = get_font(26, bold=True)
F_BODY = get_font(20, bold=False)
F_BODY_B = get_font(20, bold=True)
F_SM = get_font(16, bold=False)
F_SM_B = get_font(16, bold=True)
F_XS = get_font(14, bold=False)
F_MONO = get_font(18, bold=False, mono=True)
F_MONO_B = get_font(18, bold=True, mono=True)
F_MONO_SM = get_font(14, bold=False, mono=True)

# Logo emblem
LOGO_ICON_PATH = os.path.join(IMG_DIR, "logo-icon.png")
LOGO_ICON = Image.open(LOGO_ICON_PATH).convert("RGBA") if os.path.exists(LOGO_ICON_PATH) else None

# Helper for radial purple glow
def create_glow(size, color, max_alpha=0.35):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size // 2
    for dr in range(r, 0, -max(1, r // 16)):
        ratio = dr / r
        alpha = int(255 * max_alpha * (1 - ratio) ** 1.7)
        d.ellipse([r - dr, r - dr, r + dr, r + dr], fill=(*color, alpha))
    return img.filter(ImageFilter.GaussianBlur(size // 8))

GLOW_VIOLET_LG = create_glow(800, C_VIOLET, 0.35)
GLOW_LAVENDER_MD = create_glow(500, C_LAVENDER, 0.22)
GLOW_TEAL_MD = create_glow(500, C_TEAL, 0.18)

# -------------------------------------------------------------
# Voice-Over Timings from Master Prompt Section 7
# -------------------------------------------------------------
VO_SEGMENTS = [
    (0.5, "Every software incident starts with a question: where do we begin?"),
    (5.5, "JiraPilot AI turns a new Jira issue into a structured investigation."),
    (12.5, "It checks ticket readiness and helps teams request the details they need."),
    (20.5, "It analyzes logs, connects related errors, and surfaces evidence behind possible failure points."),
    (30.5, "It recommends relevant repositories and prepares a clearer starting point for debugging."),
    (38.5, "It prepares readable investigation updates and helps keep the team informed."),
    (47.5, "Evidence, next steps, and investigation status stay in one place."),
    (54.4, "Less repetitive triage. More time for developers to solve.")
]

def synthesize_audio():
    print("[1/4] Synthesizing Voice-Over with Windows Speech Engine...")
    ps_script = """
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SelectVoice("Microsoft Zira Desktop")
    $synth.Rate = 0
    """
    clip_files = []
    for idx, (start_time, text) in enumerate(VO_SEGMENTS, 1):
        wav_path = os.path.join(VO_DIR, f"vo_scene_{idx:02d}.wav").replace("\\", "/")
        clip_files.append((start_time, wav_path))
        safe_text = text.replace('"', '`"')
        ps_script += f"""
        $synth.SetOutputToWaveFile("{wav_path}")
        $synth.Speak("{safe_text}")
        """
    ps_script += "\n$synth.Dispose()\n"
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)

    # Master VO track
    sample_rate = 44100
    total_samples = int(60.0 * sample_rate)
    master_vo = np.zeros((total_samples, 2), dtype=np.float32)

    for start_time, clip_path in clip_files:
        with wave.open(clip_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            audio_bytes = wf.readframes(wf.getnframes())
            
            samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            if n_channels == 1:
                samples = np.column_stack([samples, samples])
            else:
                samples = samples.reshape(-1, 2)

            if framerate != sample_rate:
                target_len = int(len(samples) * sample_rate / framerate)
                resampled = np.zeros((target_len, 2), dtype=np.float32)
                for ch in range(2):
                    resampled[:, ch] = np.interp(
                        np.linspace(0, len(samples), target_len, endpoint=False),
                        np.arange(len(samples)),
                        samples[:, ch]
                    )
                samples = resampled

            start_s = int(start_time * sample_rate)
            end_s = min(total_samples, start_s + len(samples))
            fit_l = end_s - start_s
            if fit_l > 0:
                master_vo[start_s:end_s] += samples[:fit_l]

    max_v = np.max(np.abs(master_vo))
    if max_v > 0:
        master_vo = master_vo / max_v * 0.90

    vo_master_path = os.path.join(VO_DIR, "master_voiceover.wav")
    with wave.open(vo_master_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((master_vo * 32767.0).astype(np.int16).tobytes())

    # Master Ambient Soundtrack
    print("[2/4] Mixing Ambient Music Track with Intelligent Voice Ducking...")
    sample_wav = os.path.join(PROJECT_ROOT, "sample_audio.wav")
    if os.path.exists(sample_wav):
        with wave.open(sample_wav, 'rb') as wf:
            bed = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            if wf.getnchannels() == 1:
                bed = np.column_stack([bed, bed])
            else:
                bed = bed.reshape(-1, 2)
    else:
        t_arr = np.linspace(0, 60.0, total_samples, endpoint=False)
        pad = (0.28 * np.sin(2 * np.pi * 146.83 * t_arr) +
               0.22 * np.sin(2 * np.pi * 174.61 * t_arr) +
               0.18 * np.sin(2 * np.pi * 220.00 * t_arr))
        bed = np.column_stack([pad, pad])

    music_track = np.zeros((total_samples, 2), dtype=np.float32)
    bed_l = len(bed)
    overlap = int(0.5 * sample_rate)
    step = max(1, bed_l - overlap)
    pos = 0
    while pos < total_samples:
        chunk = min(bed_l, total_samples - pos)
        music_track[pos:pos+chunk] += bed[:chunk]
        pos += step

    # Smooth ducking envelope
    vo_env = np.abs(master_vo[:, 0]) + np.abs(master_vo[:, 1])
    w = int(0.2 * sample_rate)
    padded = np.pad(vo_env, (w, w), mode='edge')
    cs = np.cumsum(padded)
    smoothed_vo = (cs[2*w:] - cs[:-2*w]) / float(2*w)
    gain = 0.38 - 0.22 * np.clip(smoothed_vo * 3.5, 0.0, 1.0)

    # Intro fade-in & outro fade-out
    t_axis = np.linspace(0, 60.0, total_samples)
    gain *= np.clip(t_axis / 1.5, 0.0, 1.0) * np.clip((60.0 - t_axis) / 3.0, 0.0, 1.0)

    music_track[:, 0] *= gain
    music_track[:, 1] *= gain

    mixed = np.clip(master_vo * 0.95 + music_track * 0.85, -1.0, 1.0)
    mixed_path = os.path.join(VO_DIR, "mixed_audio.wav")
    with wave.open(mixed_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((mixed * 32767.0).astype(np.int16).tobytes())

    return mixed_path

# -------------------------------------------------------------
# Video Scene Renderers (1080p @ 30fps)
# -------------------------------------------------------------

def scene_1(t, f_idx):
    # 0.0s – 5.0s (Opening)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    cx, cy = W // 2, H // 2
    
    # Concentric glowing rings expand
    glow_p = min(1.0, 0.3 + t * 0.15)
    gw = int(GLOW_VIOLET_LG.width * glow_p)
    gh = int(GLOW_VIOLET_LG.height * glow_p)
    glow_resized = GLOW_VIOLET_LG.resize((gw, gh), Image.Resampling.BILINEAR)
    img.paste(glow_resized, (cx - gw // 2, cy - 80 - gh // 2), glow_resized)

    draw = ImageDraw.Draw(img)
    # Concentric rings
    for r in [220, 360, 520, 700]:
        ra = int(40 * min(1.0, t / 1.5))
        draw.ellipse([cx - r, cy - 80 - r, cx + r, cy - 80 + r], outline=(*C_VIOLET, ra), width=1)

    # Logo reveal
    if LOGO_ICON:
        logo_a = min(1.0, t / 1.2)
        icon_w = int(220 * min(1.0, 0.7 + t * 0.06))
        icon_resized = LOGO_ICON.resize((icon_w, icon_w), Image.Resampling.LANCZOS)
        # Apply alpha
        img.paste(icon_resized, (cx - icon_w // 2, cy - 200), icon_resized)

    # Typewriter caption
    txt = "Every incident starts with a question."
    tw_p = min(1.0, max(0.0, (t - 0.6) / 2.2))
    cur_txt = txt[:int(len(txt) * tw_p)]
    if cur_txt:
        bbox = draw.textbbox((0, 0), txt, font=F_DISPLAY)
        tw_w = bbox[2] - bbox[0]
        draw.text(((W - tw_w) // 2, cy + 60), cur_txt, font=F_DISPLAY, fill=C_WHITE)

    # Fade from black
    if t < 0.6:
        fade = 1.0 - (t / 0.6)
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fade))))

    return img.convert("RGB")

def scene_2(t, f_idx):
    # 5.0s – 12.0s (Jira Ticket NOVA-1001)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((100, 50), "JiraPilot AI", font=F_TITLE, fill=C_LAVENDER)
    draw.text((360, 60), "• Turn Jira issues into structured investigations", font=F_SUB, fill=C_MUTED)

    # Card Camera Push (scale 0.95 -> 1.02)
    zoom = 0.95 + 0.07 * (t / 7.0)
    cw = int(1040 * zoom)
    ch = int(600 * zoom)
    cx = (W - cw) // 2
    cy = int(220 - (zoom - 0.95) * 50)

    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.rounded_rectangle([cx, cy, cx + cw, cy + 56], radius=14, fill=C_SURFACE_2)
    draw.rectangle([cx, cy + 34, cx + cw, cy + 56], fill=C_SURFACE_2)

    # NOVA-1001 Badge
    draw.rounded_rectangle([cx + 24, cy + 12, cx + 160, cy + 44], radius=6, fill=(*C_VIOLET, 50), outline=C_VIOLET)
    draw.text((cx + 36, cy + 17), "NOVA-1001", font=F_MONO_B, fill=C_WHITE)
    draw.text((cx + 180, cy + 18), "• Project: Nova Platform  •  Status: OPEN", font=F_SM, fill=C_MUTED)

    # Summary
    draw.text((cx + 32, cy + 85), "Issue Summary:", font=F_SM_B, fill=C_MUTED)
    draw.text((cx + 32, cy + 115), "Resource allocation fails under peak load (HTTP 503)", font=F_HEADING, fill=C_WHITE)

    # Metadata
    meta = [
        ("Reporter", "qa.eng@northstar.internal", "Environment", "production-cluster-04"),
        ("Detected API", "POST /api/v1/resources/allocate", "Component", "resource-inventory-service"),
        ("Correlation ID", "CORR-DEMO-1001", "Reported Time", "2026-10-10 14:22 UTC")
    ]
    my = cy + 185
    for k1, v1, k2, v2 in meta:
        draw.text((cx + 32, my), k1 + ":", font=F_XS, fill=C_MUTED)
        draw.text((cx + 32, my + 20), v1, font=F_MONO_SM, fill=C_WHITE)
        draw.text((cx + 560, my), k2 + ":", font=F_XS, fill=C_MUTED)
        draw.text((cx + 560, my + 20), v2, font=F_MONO_SM, fill=C_WHITE)
        my += 66

    # Restrained Animated Cursor
    if t > 2.5:
        cur_x = cx + 32 + int(math.sin((t - 2.5) * 1.5) * 70 + 420)
        cur_y = cy + 124
        draw.polygon([(cur_x, cur_y), (cur_x, cur_y + 18), (cur_x + 5, cur_y + 14), (cur_x + 12, cur_y + 24),
                      (cur_x + 16, cur_y + 22), (cur_x + 9, cur_y + 12), (cur_x + 16, cur_y + 12)],
                     fill=(*C_LAVENDER, 240), outline=(*C_WHITE, 255))

    return img.convert("RGB")

def scene_3(t, f_idx):
    # 12.0s – 20.0s (Readiness Validation)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    draw.text((100, 50), "Diagnostic Information Readiness", font=F_TITLE, fill=C_WHITE)
    draw.text((100, 106), "Validate ticket completeness and identify missing logs before investigation begins.", font=F_SUB, fill=C_LAVENDER)

    # Score Panel
    score_p = min(1.0, t / 4.0)
    cur_score = int(50 * score_p)
    draw.rounded_rectangle([100, 180, 460, 480], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((130, 210), "Ticket Readiness", font=F_SM_B, fill=C_MUTED)
    draw.text((130, 250), f"{cur_score}%", font=get_font(76, bold=True), fill=C_AMBER)
    draw.text((130, 360), "Status: WAITING FOR INFORMATION", font=F_XS, fill=C_AMBER)
    draw.text((130, 390), "Missing: Server Logs, Request Payload", font=F_XS, fill=C_MUTED)

    # Checklist
    fields = [
        ("Description & Context", True, "Clear problem scope provided"),
        ("API Endpoint & Method", True, "POST /api/v1/resources/allocate"),
        ("Application Server Logs", False, "Missing diagnostic error traces"),
        ("Request Payload Sample", False, "Missing raw JSON correlation headers")
    ]
    gy = 180
    for idx, (lbl, ok, sub) in enumerate(fields):
        f_p = min(1.0, max(0.0, (t - idx * 0.5) / 0.4))
        if f_p <= 0:
            continue
        fa = int(255 * f_p)
        fy = gy + idx * 80
        col = C_TEAL if ok else C_AMBER
        bg = (16, 42, 38) if ok else (45, 32, 14)
        draw.rounded_rectangle([500, fy, 1820, fy + 68], radius=10, fill=(*bg, fa), outline=(*col, fa), width=1)
        draw.text((530, fy + 20), "✓" if ok else "!", font=F_BODY_B, fill=(*col, fa))
        draw.text((570, fy + 16), lbl, font=F_BODY_B, fill=(*C_WHITE, fa))
        draw.text((570, fy + 42), sub, font=F_XS, fill=(*col, fa))

    if t > 4.5:
        pa = int(255 * min(1.0, (t - 4.5) / 1.0))
        draw.rounded_rectangle([100, 860, 1820, 940], radius=12, fill=(*C_SURFACE_2, pa), outline=(*C_VIOLET, pa), width=1)
        draw.text((130, 888), "⚡ Automated Clarification Request Generated:", font=F_BODY_B, fill=(*C_LAVENDER, pa))
        draw.text((580, 890), "\"Please attach server logs and correlation ID CORR-DEMO-1001 to resume automated triage.\"",
                  font=F_BODY, fill=(*C_WHITE, pa))

    return img.convert("RGB")

def scene_4(t, f_idx):
    # 20.0s – 30.0s (Log Analysis)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    draw.text((100, 50), "From raw logs to evidence-backed insights.", font=F_TITLE, fill=C_WHITE)
    draw.text((100, 106), "Recognizes correlation IDs, HTTP 503 anomalies, and circuit breaker trip states.", font=F_SUB, fill=C_LAVENDER)

    # Left: Log Viewer (1060px)
    lx, ly, lw, lh = 100, 170, 1060, 810
    draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=12, fill=(6, 5, 12), outline=C_LINE, width=1)
    draw.rounded_rectangle([lx, ly, lx + lw, ly + 44], radius=12, fill=C_SURFACE_2)
    draw.text((lx + 24, ly + 14), "application-demo.log  (CORR-DEMO-1001)", font=F_XS, fill=C_MUTED)

    logs = [
        ("14:22:12", "INFO",  "Dispatcher", "Received POST /api/v1/resources/allocate", C_MUTED),
        ("14:22:13", "INFO",  "Validator",  "CorrelationId recognized: CORR-DEMO-1001", C_LAVENDER),
        ("14:22:15", "WARN",  "DbPool",     "Connection latency spike: 420ms on cluster", C_AMBER),
        ("14:22:17", "ERROR", "Allocation", "HTTP 503 Service Unavailable on /api/v1/resources", C_DANGER),
        ("14:22:18", "ERROR", "Allocation", "Failed to reserve resource-1001 status=503", C_DANGER),
        ("14:22:19", "FATAL", "RetryMgr",   "Exhausted 3 retries for CORR-DEMO-1001", C_DANGER),
        ("14:22:20", "WARN",  "Gateway",    "Circuit breaker OPEN for resource-inventory-service", C_AMBER)
    ]
    ly_pos = ly + 64
    for idx, (ts, lvl, comp, msg, col) in enumerate(logs):
        la = int(255 * min(1.0, max(0.0, (t - idx * 0.4) / 0.3)))
        if la <= 0:
            continue
        if idx in [3, 4, 5]:
            draw.rounded_rectangle([lx + 10, ly_pos - 4, lx + lw - 10, ly_pos + 36], radius=4, fill=(*C_VIOLET, int(40 * la / 255)))
        draw.text((lx + 20, ly_pos), ts, font=F_MONO_SM, fill=(*C_MUTED, la))
        draw.text((lx + 130, ly_pos), f"[{lvl:<5}]", font=F_MONO_B, fill=(*col, la))
        draw.text((lx + 220, ly_pos), comp, font=F_MONO_SM, fill=(*C_MUTED, la))
        m_col = C_WHITE if col == C_MUTED else col
        draw.text((lx + 360, ly_pos), msg, font=F_MONO_SM, fill=(*m_col, la))
        ly_pos += 44

    # Right: Evidence Group
    rx = 1200
    rw = 620
    if t > 1.5:
        ea = int(255 * min(1.0, (t - 1.5) / 1.0))
        draw.rounded_rectangle([rx, 170, rx + rw, 500], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((rx + 28, 195), "Grouped Diagnostic Evidence", font=F_HEADING, fill=(*C_LAVENDER, ea))
        ev_items = [
            ("Endpoint", "POST /api/v1/resources/allocate", C_TEAL),
            ("Status", "HTTP 503 Service Unavailable", C_DANGER),
            ("Correlation ID", "CORR-DEMO-1001", C_LAVENDER),
            ("Failure Point", "Circuit breaker OPEN after 3 retries", C_AMBER)
        ]
        ey = 245
        for ek, ev, ec in ev_items:
            draw.text((rx + 28, ey), ek + ":", font=F_XS, fill=(*C_MUTED, ea))
            draw.text((rx + 28, ey + 22), ev, font=F_MONO_SM, fill=(*ec, ea))
            ey += 58

    if t > 5.0:
        pca = int(255 * min(1.0, (t - 5.0) / 1.0))
        draw.rounded_rectangle([rx, 530, rx + rw, 940], radius=12, fill=C_SURFACE_2, outline=(*C_AMBER, pca), width=1)
        draw.text((rx + 28, 555), "⚠ Probable Cause — Verification Required", font=F_HEADING, fill=(*C_AMBER, pca))
        cause_p = [
            "DB connection pool exhausted on resource-inventory-service.",
            "Circuit breaker tripped to OPEN, returning 503 to client.",
            "Confidence: 88% (Synthesized hypothesis based on logs)."
        ]
        cy = 610
        for cp in cause_p:
            draw.text((rx + 28, cy), "• " + cp, font=F_BODY, fill=(*C_WHITE, pca))
            cy += 48
        draw.text((rx + 28, 880), "Evidence-backed hypothesis. Human verification required.", font=F_XS, fill=(*C_MUTED, pca))

    return img.convert("RGB")

def scene_5(t, f_idx):
    # 30.0s – 38.0s (Repository Discovery)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    draw.text((100, 50), "Find a relevant place to start debugging.", font=F_TITLE, fill=C_WHITE)
    draw.text((100, 106), "Recommends verified synthetic repositories and prepares copy-ready clone commands.", font=F_SUB, fill=C_LAVENDER)

    # Endpoint Box
    draw.rounded_rectangle([100, 190, 600, 340], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((125, 215), "DETECTED ENDPOINT", font=F_XS, fill=C_MUTED)
    draw.text((125, 250), "POST /api/v1/resources/allocate", font=F_MONO_B, fill=C_TEAL)
    draw.text((125, 290), "Service: resource-inventory-service", font=F_SM, fill=C_LAVENDER)

    # Verified Repo Card
    if t > 1.2:
        ra = int(255 * min(1.0, (t - 1.2) / 1.0))
        rx, ry, rw, rh = 720, 190, 1100, 180
        draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=14, fill=C_SURFACE, outline=(*C_TEAL, ra), width=2)
        draw.rounded_rectangle([rx + 24, ry + 20, rx + 240, ry + 52], radius=6, fill=(*C_TEAL, int(ra * 0.2)))
        draw.text((rx + 36, ry + 26), "✓ VERIFIED SERVICE REPO", font=F_XS, fill=(*C_TEAL, ra))
        draw.text((rx + 24, ry + 68), "resource-inventory-service", font=F_TITLE, fill=(*C_WHITE, ra))
        draw.text((rx + 24, ry + 125), "https://github.com/northstar-labs/resource-inventory-service.git", font=F_MONO, fill=(*C_LAVENDER, ra))

    # Terminal Clone Panel
    if t > 2.8:
        ta = int(255 * min(1.0, (t - 2.8) / 1.0))
        tx, ty, tw, th = 100, 420, 1720, 360
        draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=14, fill=(6, 5, 12, ta), outline=(*C_VIOLET, ta), width=1)
        draw.rounded_rectangle([tx, ty, tx + tw, ty + 44], radius=14, fill=(*C_SURFACE_2, ta))
        draw.text((tx + 24, ty + 14), "Quick Clone Command — Approved Internal Synthetic Catalog", font=F_XS, fill=(*C_MUTED, ta))

        cmd = "git clone https://github.com/northstar-labs/resource-inventory-service.git"
        draw.text((tx + 36, ty + 90), "$ " + cmd, font=F_MONO_B, fill=(*C_WHITE, ta))

        # Copy button animation
        copied = t > 5.0
        btn_txt = "✓ COPIED TO CLIPBOARD" if copied else "📋 COPY COMMAND"
        btn_col = C_TEAL if copied else C_VIOLET
        draw.rounded_rectangle([tx + tw - 320, ty + 80, tx + tw - 30, ty + 125], radius=6,
                               fill=(*btn_col, int(ta * (0.8 if copied else 0.3))), outline=(*btn_col, ta))
        draw.text((tx + tw - 295, ty + 92), btn_txt, font=F_SM_B, fill=(*C_WHITE, ta))

        draw.text((tx + 36, ty + 240), "Note: Repository matching is an evidence-backed starting point, not proof of root cause.",
                  font=F_SM, fill=(*C_MUTED, ta))

    return img.convert("RGB")

def scene_6(t, f_idx):
    # 38.0s – 47.0s (Reporting)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    draw.text((100, 50), "Clear findings. Better handoffs.", font=F_TITLE, fill=C_WHITE)
    draw.text((100, 106), "Prepare consistent investigation updates without repetitive manual writing.", font=F_SUB, fill=C_LAVENDER)

    # Split Screen: Jira Comment (Left) + Email (Right)
    # Left: Jira Comment
    jx, jy, jw, jh = 100, 170, 820, 810
    draw.rounded_rectangle([jx, jy, jx + jw, jy + jh], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.rounded_rectangle([jx, jy, jx + jw, jy + 48], radius=12, fill=C_SURFACE_2)
    draw.text((jx + 24, jy + 14), "Jira Investigation Comment (NOVA-1001)", font=F_SM_B, fill=C_LAVENDER)

    j_items = [
        ("📋 Investigation Summary", F_HEADING, C_WHITE),
        ("POST /api/v1/resources/allocate returned HTTP 503.", F_BODY, C_MUTED),
        ("", F_XS, C_MUTED),
        ("Evidence Observed:", F_BODY_B, C_WHITE),
        ("• Correlation ID: CORR-DEMO-1001", F_MONO, C_LAVENDER),
        ("• Circuit breaker tripped after 3 retries", F_BODY, C_AMBER),
        ("", F_XS, C_MUTED),
        ("Recommended Next Steps:", F_BODY_B, C_WHITE),
        ("1. Inspect DB pool sizing in resource-inventory-service", F_BODY, C_TEAL),
        ("2. Clone: github.com/northstar-labs/resource-inventory-service", F_MONO_SM, C_MUTED),
        ("", F_XS, C_MUTED),
        ("Limitations: Requires engineer verification before merge.", F_XS, C_MUTED)
    ]
    jy_pos = jy + 72
    for it, font_it, col_it in j_items:
        if it:
            draw.text((jx + 28, jy_pos), it, font=font_it, fill=col_it)
        jy_pos += 34

    # Right: Email Preview
    ex, ey, ew, eh = 960, 170, 860, 810
    ea = int(255 * min(1.0, max(0.0, (t - 0.8) / 0.8)))
    draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=12, fill=(248, 246, 252, ea), outline=(*C_LINE, ea), width=1)
    draw.rounded_rectangle([ex, ey, ex + ew, ey + 64], radius=12, fill=(235, 230, 245, ea))
    draw.text((ex + 24, ey + 12), "Subject: [JiraPilot AI] NOVA-1001 Investigation Findings", font=F_BODY_B, fill=(*C_NEAR_BLACK, ea))
    draw.text((ex + 24, ey + 38), "To: SRE-OnCall@northstar.internal", font=F_XS, fill=(80, 70, 100, ea))

    email_body = [
        ("Team,", F_BODY, C_NEAR_BLACK),
        ("JiraPilot AI completed the automated triage for NOVA-1001.", F_BODY, C_NEAR_BLACK),
        ("", F_XS, C_NEAR_BLACK),
        ("FINDINGS SUMMARY", F_BODY_B, (110, 65, 215)),
        ("• Service: resource-inventory-service", F_BODY, C_NEAR_BLACK),
        ("• Error: HTTP 503 SocketTimeout", F_BODY, (180, 40, 40)),
        ("• Probable Cause: DB Connection Pool Exhaustion", F_BODY, C_NEAR_BLACK),
        ("", F_XS, C_NEAR_BLACK),
        ("NEXT STEPS", F_BODY_B, (30, 120, 110)),
        ("• Review patch branch: fix/db-pool-timeout", F_BODY, C_NEAR_BLACK),
        ("• Full telemetry: https://dashboard.northstar.internal", F_BODY, (60, 80, 180)),
    ]
    ey_pos = ey + 84
    for et, ef, ec in email_body:
        if et:
            draw.text((ex + 28, ey_pos), et, font=ef, fill=(*ec, ea))
        ey_pos += 34

    # Simulated Delivery Status
    if t > 3.0:
        sa = int(255 * min(1.0, (t - 3.0) / 0.6))
        draw.rounded_rectangle([ex + 28, ey + eh - 65, ex + ew - 28, ey + eh - 18], radius=6, fill=(35, 120, 100, sa))
        draw.text((ex + 45, ey + eh - 50), "✓ NOTIFICATION DELIVERED (Simulated Demo Mode)", font=F_BODY_B, fill=(*C_WHITE, sa))

    return img.convert("RGB")

def scene_7(t, f_idx):
    # 47.0s – 54.0s (Dashboard)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    # Top App Nav
    draw.rectangle([0, 0, W, 64], fill=C_SURFACE)
    draw.line([(0, 64), (W, 64)], fill=C_LINE, width=1)
    draw.text((32, 18), "JiraPilot AI", font=F_HEADING, fill=C_WHITE)
    draw.text((220, 22), "• Incident Operations Workspace", font=F_SM, fill=C_MUTED)

    draw.text((60, 95), "One workspace. A clearer investigation.", font=F_TITLE, fill=C_WHITE)
    draw.text((60, 150), "Evidence, next steps, and investigation status stay in one place.", font=F_SUB, fill=C_LAVENDER)

    # 4 Cards
    metrics = [
        ("Total Ingested", "24 Issues", C_WHITE),
        ("Awaiting Info", "3 Tickets", C_AMBER),
        ("Ready for Review", "5 Validated", C_TEAL),
        ("RCA Concluded", "16 Solved", C_VIOLET)
    ]
    mx = 60
    for m_t, m_v, m_c in metrics:
        draw.rounded_rectangle([mx, 205, mx + 420, 310], radius=10, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((mx + 20, 222), m_t, font=F_XS, fill=C_MUTED)
        draw.text((mx + 20, 248), m_v, font=F_TITLE, fill=m_c)
        mx += 460

    # 3-col panels
    py = 335
    ph = 680
    # Left: Timeline
    draw.rounded_rectangle([60, py, 600, py + ph], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((84, py + 20), "Incident Activity Stream", font=F_HEADING, fill=C_WHITE)
    stream = [
        ("NOVA-1001", "14:23 UTC", "Root cause synthesis complete (88% conf)", C_TEAL),
        ("NOVA-1001", "14:22 UTC", "Extracted HTTP 503 & correlation CORR-DEMO", C_AMBER),
        ("NOVA-1002", "13:45 UTC", "Clarification prompt sent to reporter", C_MUTED),
        ("NOVA-1003", "12:10 UTC", "Repo matched: resource-inventory-service", C_TEAL),
    ]
    sy = py + 70
    for sk, st, sd, sc in stream:
        draw.rounded_rectangle([80, sy, 580, sy + 80], radius=8, fill=C_SURFACE_2)
        draw.text((95, sy + 14), sk, font=F_MONO_B, fill=C_LAVENDER)
        draw.text((220, sy + 16), st, font=F_XS, fill=C_MUTED)
        draw.text((95, sy + 44), sd, font=F_SM, fill=sc)
        sy += 98

    # Mid: Evidence Summary
    draw.rounded_rectangle([630, py, 1270, py + ph], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((654, py + 20), "Synthesized Root Cause Analysis", font=F_HEADING, fill=C_WHITE)
    draw.text((654, py + 70), "Incident: NOVA-1001 • Severity: Tier-1 Outage", font=F_BODY_B, fill=C_AMBER)
    draw.text((654, py + 115),
              "• Primary Failure: HTTP 503 Service Unavailable\n"
              "• Path: POST /api/v1/resources/allocate\n"
              "• Root Cause: Database connection pool exhausted under peak traffic.\n"
              "• Verified Repo: https://github.com/northstar-labs/resource-inventory-service.git\n"
              "• Automated Reproduction cURL and regression tests compiled.",
              font=F_BODY, fill=C_WHITE)

    # Right: Next Steps
    draw.rounded_rectangle([1300, py, 1860, py + ph], radius=12, fill=C_SURFACE, outline=C_LINE, width=1)
    draw.text((1324, py + 20), "Next Developer Actions", font=F_HEADING, fill=C_WHITE)
    actions = [
        ("Review Suggested PR #482", "Timeout threshold config update", C_LAVENDER),
        ("Run Local Reproduction", "Replay CORR-DEMO-1001 in test harness", C_TEAL),
        ("Sync Jira Status to IN PROGRESS", "Assigned to on-call engineer", C_MUTED),
    ]
    ay = py + 70
    for at, asub, ac in actions:
        draw.rounded_rectangle([1320, ay, 1840, ay + 90], radius=8, fill=C_SURFACE_2)
        draw.text((1335, ay + 18), at, font=F_BODY_B, fill=ac)
        draw.text((1335, ay + 48), asub, font=F_XS, fill=C_MUTED)
        ay += 110

    return img.convert("RGB")

def scene_8(t, f_idx):
    # 54.0s – 60.0s (Closing)
    img = Image.new("RGBA", (W, H), (*C_NEAR_BLACK, 255))
    cx, cy = W // 2, H // 2
    
    # Concentric rings & violet glow
    glow_p = min(1.0, 0.4 + t * 0.1)
    gw = int(GLOW_VIOLET_LG.width * glow_p)
    gh = int(GLOW_VIOLET_LG.height * glow_p)
    glow_resized = GLOW_VIOLET_LG.resize((gw, gh), Image.Resampling.BILINEAR)
    img.paste(glow_resized, (cx - gw // 2, cy - 80 - gh // 2), glow_resized)

    draw = ImageDraw.Draw(img)
    for r in [220, 360, 520, 700]:
        draw.ellipse([cx - r, cy - 80 - r, cx + r, cy - 80 + r], outline=(*C_VIOLET, 50), width=1)

    # Centered Logo
    if LOGO_ICON:
        icon_w = 220
        img.paste(LOGO_ICON.resize((icon_w, icon_w), Image.Resampling.LANCZOS), (cx - icon_w // 2, cy - 200), LOGO_ICON.resize((icon_w, icon_w)))

    # On-screen Closing Text:
    # JiraPilot AI
    # Your investigation copilot.
    b_txt = "JiraPilot AI"
    bbox_b = draw.textbbox((0, 0), b_txt, font=F_DISPLAY)
    bw = bbox_b[2] - bbox_b[0]
    draw.text(((W - bw) // 2, cy + 40), b_txt, font=F_DISPLAY, fill=C_WHITE)

    # Accent bar
    draw.rectangle([(W // 2 - 140, cy + 125), (W // 2 + 140, cy + 129)], fill=C_VIOLET)

    t_txt = "Your investigation copilot."
    bbox_t = draw.textbbox((0, 0), t_txt, font=F_TITLE)
    tw = bbox_t[2] - bbox_t[0]
    draw.text(((W - tw) // 2, cy + 150), t_txt, font=F_TITLE, fill=C_LAVENDER)

    # Fade to black at very end (last 1.2s)
    if t > 4.8:
        fade = min(1.0, (t - 4.8) / 1.2)
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fade))))

    return img.convert("RGB")

SCENE_DISPATCH = [
    (0.0, 5.0, scene_1),
    (5.0, 12.0, scene_2),
    (12.0, 20.0, scene_3),
    (20.0, 30.0, scene_4),
    (30.0, 38.0, scene_5),
    (38.0, 47.0, scene_6),
    (47.0, 54.0, scene_7),
    (54.0, 60.0, scene_8),
]

def get_demo_frame(global_f_idx):
    global_t = global_f_idx / float(FPS)
    for start_t, end_t, fn in SCENE_DISPATCH:
        if start_t <= global_t < end_t:
            return fn(global_t - start_t, global_f_idx)
    return scene_8(6.0, global_f_idx)

def render_demo_video(mixed_audio_path):
    print("[3/4] Encoding Master 60.0s Product Demonstration Film (1080p @ 30fps)...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", "30",
        "-i", "-",
        "-i", mixed_audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUT_MP4
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    total_frames = TOTAL_FRAMES
    for f_idx in range(total_frames):
        frame = get_demo_frame(f_idx)
        proc.stdin.write(frame.tobytes())
        if (f_idx + 1) % 150 == 0 or f_idx == total_frames - 1:
            pct = int((f_idx + 1) / total_frames * 100)
            elapsed = (f_idx + 1) / 30.0
            print(f"  -> Frame {f_idx + 1:4d}/{total_frames} ({pct:3d}%) | Timeline: {elapsed:4.1f}s / 60.0s")

    proc.stdin.close()
    proc.wait()
    print(f"\n[OK] Master Demonstration Video Rendered: {OUT_MP4}")

def main():
    print("=" * 60)
    print("Rendering JiraPilot AI Product Demo Video (Deep Purple Film)")
    print("=" * 60)
    audio_path = synthesize_audio()
    render_demo_video(audio_path)
    print("\n[OK] Video Production Complete: 60.00 seconds exactly.")

if __name__ == "__main__":
    main()
