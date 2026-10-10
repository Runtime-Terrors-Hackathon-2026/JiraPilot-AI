"""
JiraPilot AI — Presentation & PDF Generator
Generates:
1. presentation/JiraPilot-AI-Hackathon.pptx (16:9 widescreen editable PowerPoint with native shapes & embedded GIFs)
2. presentation/assets/images/slide-01.png ... slide-08.png (1920x1080 high-res slide renders)
3. presentation/JiraPilot-AI-Hackathon.pdf (Multi-page PDF presentation fallback)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
GIF_DIR = os.path.join(BASE_DIR, "assets", "gifs")
PPTX_PATH = os.path.join(BASE_DIR, "JiraPilot-AI-Hackathon.pptx")
PDF_PATH = os.path.join(BASE_DIR, "JiraPilot-AI-Hackathon.pdf")

# Visual Design Tokens
C_NEAR_BLACK = (8, 7, 13)       # #08070D
C_DEEP_PURPLE = (23, 11, 43)    # #170B2B
C_SURFACE = (22, 16, 38)        # #161026
C_SURFACE_2 = (30, 22, 52)      # #1e1634
C_LINE = (55, 42, 85)           # #372a55
C_VIOLET = (139, 92, 246)       # #8B5CF6 (Primary Glow)
C_LAVENDER = (196, 181, 253)    # #C4B5FD (Secondary Accent)
C_WHITE = (255, 255, 255)
C_MUTED = (184, 179, 199)       # #B8B3C7
C_TEAL = (45, 212, 191)         # #2dd4bf
C_AMBER = (251, 191, 36)        # #fbbf24
C_DANGER = (248, 113, 113)      # #f87171

RGB_VIOLET = RGBColor(139, 92, 246)
RGB_LAVENDER = RGBColor(196, 181, 253)
RGB_WHITE = RGBColor(255, 255, 255)
RGB_MUTED = RGBColor(184, 179, 199)
RGB_SURFACE = RGBColor(22, 16, 38)
RGB_SURFACE_2 = RGBColor(30, 22, 52)
RGB_LINE = RGBColor(55, 42, 85)
RGB_TEAL = RGBColor(45, 212, 191)
RGB_AMBER = RGBColor(251, 191, 36)

def get_font(size, bold=False, mono=False):
    if mono:
        path = "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"
    else:
        path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

F_DISPLAY = get_font(56, bold=True)
F_TITLE = get_font(42, bold=True)
F_SUB = get_font(26, bold=False)
F_HEADING = get_font(24, bold=True)
F_BODY = get_font(20, bold=False)
F_BODY_B = get_font(20, bold=True)
F_SM = get_font(16, bold=False)
F_SM_B = get_font(16, bold=True)
F_XS = get_font(14, bold=False)
F_MONO = get_font(18, bold=False, mono=True)
F_MONO_B = get_font(18, bold=True, mono=True)
F_MONO_SM = get_font(14, bold=False, mono=True)

# -------------------------------------------------------------------------
# Part 1: High-Resolution 1920x1080 Slide Canvas Renderer (for PDF & Previews)
# -------------------------------------------------------------------------
def render_slide_canvas(slide_idx):
    w, h = 1920, 1080
    bg_canvas = os.path.join(IMG_DIR, "background-canvas.png")
    if os.path.exists(bg_canvas):
        img = Image.open(bg_canvas).convert("RGBA")
    else:
        img = Image.new("RGBA", (w, h), (*C_NEAR_BLACK, 255))
    draw = ImageDraw.Draw(img)

    logo_icon_path = os.path.join(IMG_DIR, "logo-icon.png")
    logo_icon = Image.open(logo_icon_path).convert("RGBA") if os.path.exists(logo_icon_path) else None

    # Slide 1: Cinematic Opening
    if slide_idx == 1:
        # Concentric glowing rings centered
        cx, cy = w // 2, h // 2 - 40
        if logo_icon:
            icon_lg = logo_icon.resize((200, 200), Image.Resampling.LANCZOS)
            img.paste(icon_lg, (cx - 100, cy - 180), icon_lg)

        draw = ImageDraw.Draw(img)
        # Main Title
        title_text = "Turn Jira issues into actionable investigations."
        bbox = draw.textbbox((0, 0), title_text, font=F_DISPLAY)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, cy + 50), title_text, font=F_DISPLAY, fill=C_WHITE)

        # Violet glowing accent line
        draw.rectangle([(w // 2 - 140, cy + 135), (w // 2 + 140, cy + 139)], fill=C_VIOLET)

        # Subtitle
        sub_text = "AI-powered ticket triage, log analysis, and approved repository discovery."
        bbox_sub = draw.textbbox((0, 0), sub_text, font=F_SUB)
        sw = bbox_sub[2] - bbox_sub[0]
        draw.text(((w - sw) // 2, cy + 160), sub_text, font=F_SUB, fill=C_LAVENDER)

        # Product Brand & Hackathon Tag
        tag = "JiraPilot AI  •  Northstar Digital Systems Hackathon 2026"
        bbox_tag = draw.textbbox((0, 0), tag, font=F_SM_B)
        tgw = bbox_tag[2] - bbox_tag[0]
        draw.text(((w - tgw) // 2, h - 80), tag, font=F_SM_B, fill=C_MUTED)

    # Slide 2: The Problem
    elif slide_idx == 2:
        draw.text((100, 70), "Too much time spent finding where to start.", font=F_TITLE, fill=C_WHITE)
        draw.text((100, 130), "Software engineering teams face four major friction points during initial incident triage.",
                  font=F_SUB, fill=C_LAVENDER)

        # 4 Visual Problem Cards
        cards = [
            ("01", "Incomplete Jira Tickets",
             "Incidents filed with missing server logs, unclear environments, and absent request payloads require tedious manual follow-ups.",
             C_AMBER),
            ("02", "Scattered Telemetry",
             "Engineers must dig through multiple log aggregation tools, correlation IDs, and timestamps to find relevant failure events.",
             C_VIOLET),
            ("03", "Manual Error Extraction",
             "Parsing distributed stack traces, HTTP 503 cascades, and circuit breaker trip states takes valuable senior engineering focus.",
             C_LAVENDER),
            ("04", "Locating The Right Repository",
             "Large microservice architectures make finding the exact service repo, clone URL, and local reproduction steps frustrating.",
             C_TEAL)
        ]

        cw, ch = 380, 520
        gap = 33
        start_x = 100
        cy = 210

        for idx, (num, heading, desc, accent_col) in enumerate(cards):
            x = start_x + idx * (cw + gap)
            draw.rounded_rectangle([x, cy, x + cw, cy + ch], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
            
            # Accent bar top
            draw.rounded_rectangle([x + 24, cy + 24, x + 74, cy + 74], radius=10, fill=(*accent_col, 40), outline=accent_col)
            draw.text((x + 36, cy + 34), num, font=F_HEADING, fill=accent_col)

            draw.text((x + 24, cy + 110), heading, font=F_HEADING, fill=C_WHITE)
            
            # Description lines
            draw.text((x + 24, cy + 180), desc, font=F_BODY, fill=C_MUTED)

        # Concluding Statement Banner
        draw.rounded_rectangle([100, 770, 1820, 860], radius=12, fill=C_SURFACE_2, outline=C_VIOLET, width=1)
        draw.text((130, 800), "The challenge isn't only solving the issue. It's organizing the investigation.",
                  font=F_HEADING, fill=C_WHITE)

    # Slide 3: Ticket Readiness
    elif slide_idx == 3:
        draw.text((100, 60), "Every new issue gets a clearer next step.", font=F_TITLE, fill=C_WHITE)
        draw.text((100, 118), "Automated completeness audit highlights missing fields and prepares reporter clarification comments.",
                  font=F_SUB, fill=C_LAVENDER)

        # Left: Embed Frame / Screenshot placeholder of GIF 01
        gif1_thumb = os.path.join(GIF_DIR, "01-jira-ticket-readiness.gif")
        if os.path.exists(gif1_thumb):
            with Image.open(gif1_thumb) as g:
                g.seek(40)
                thumb = g.copy().resize((980, 551), Image.Resampling.LANCZOS)
                img.paste(thumb, (100, 180))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([100, 180, 1080, 731], radius=8, outline=C_VIOLET, width=2)

        # Right: Key takeaways card
        rx = 1130
        draw.rounded_rectangle([rx, 180, 1820, 731], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((rx + 35, 215), "How Readiness Validation Works:", font=F_HEADING, fill=C_WHITE)

        bullets = [
            ("1. Real-Time Jira Webhook", "Incoming issues in project NOVA ingested immediately.", C_LAVENDER),
            ("2. Multi-Field Diagnostic Check", "Validates description, API endpoints, logs, and payloads.", C_LAVENDER),
            ("3. Clear Amber Highlighting", "Missing data flagged visually to avoid premature investigation.", C_AMBER),
            ("4. Automated Reporter Comment", "Polite prompt generated with exact requirements.", C_TEAL),
            ("5. Honest Status Transitions", "Issue moves to WAITING_FOR_INFO until evidence is provided.", C_WHITE)
        ]
        by = 275
        for b_title, b_sub, b_col in bullets:
            draw.text((rx + 35, by), b_title, font=F_BODY_B, fill=b_col)
            draw.text((rx + 35, by + 30), b_sub, font=F_SM, fill=C_MUTED)
            by += 85

        # Caption
        draw.text((100, 765), "Identify missing information before investigation goes deeper.",
                  font=F_HEADING, fill=C_LAVENDER)

    # Slide 4: Log Analysis
    elif slide_idx == 4:
        draw.text((100, 60), "Turn raw logs into structured evidence.", font=F_TITLE, fill=C_WHITE)
        draw.text((100, 118), "Extracts endpoints, status codes, and correlation traces while maintaining clear hypothesis boundaries.",
                  font=F_SUB, fill=C_LAVENDER)

        gif2_thumb = os.path.join(GIF_DIR, "02-log-analysis.gif")
        if os.path.exists(gif2_thumb):
            with Image.open(gif2_thumb) as g:
                g.seek(45)
                thumb = g.copy().resize((980, 551), Image.Resampling.LANCZOS)
                img.paste(thumb, (100, 180))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([100, 180, 1080, 731], radius=8, outline=C_VIOLET, width=2)

        rx = 1130
        draw.rounded_rectangle([rx, 180, 1820, 731], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((rx + 35, 215), "Synthetic Demo Evidence:", font=F_HEADING, fill=C_WHITE)

        demo_facts = [
            ("Log Source", "application-demo.log (Northstar synthetic telemetry)", C_MUTED),
            ("Failing Endpoint", "POST /api/v1/resources/allocate", C_TEAL),
            ("HTTP Failure Status", "503 Service Unavailable", C_DANGER),
            ("Correlation ID", "CORR-DEMO-1001 (Tracked across 3 retry attempts)", C_LAVENDER),
            ("Circuit Breaker State", "Tripped to OPEN due to database pool exhaustion", C_AMBER),
            ("Probable Cause", "Evidence-backed hypothesis requiring engineer verification", C_WHITE)
        ]
        fy = 275
        for k, v, c in demo_facts:
            draw.text((rx + 35, fy), k + ":", font=F_SM_B, fill=C_LAVENDER)
            draw.text((rx + 35, fy + 26), v, font=F_SM, fill=c)
            fy += 68

        draw.text((100, 765), "From raw log lines to a clearer debugging path.",
                  font=F_HEADING, fill=C_LAVENDER)

    # Slide 5: Repository Discovery
    elif slide_idx == 5:
        draw.text((100, 60), "Find a relevant place to start debugging.", font=F_TITLE, fill=C_WHITE)
        draw.text((100, 118), "Multi-signal catalog lookup maps endpoints to verified synthetic repositories with zero invented URLs.",
                  font=F_SUB, fill=C_LAVENDER)

        gif3_thumb = os.path.join(GIF_DIR, "03-repository-discovery.gif")
        if os.path.exists(gif3_thumb):
            with Image.open(gif3_thumb) as g:
                g.seek(50)
                thumb = g.copy().resize((980, 551), Image.Resampling.LANCZOS)
                img.paste(thumb, (100, 180))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([100, 180, 1080, 731], radius=8, outline=C_VIOLET, width=2)

        rx = 1130
        draw.rounded_rectangle([rx, 180, 1820, 731], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((rx + 35, 215), "Configured Catalog Match:", font=F_HEADING, fill=C_WHITE)

        repo_points = [
            ("Approved Repository", "resource-inventory-service", C_TEAL),
            ("Clone Command", "git clone https://github.com/northstar-labs/resource-inventory-service.git", C_WHITE),
            ("Matching Strategy", "Route Match (Weight 35) + Package Trace (Weight 25)", C_LAVENDER),
            ("Developer Handoff", "One-click copyable clone command ready in terminal panel", C_MUTED),
            ("Safety Guarantee", "Clearly distinguished as a suggestion, not proven root cause", C_AMBER)
        ]
        rpy = 275
        for rk, rv, rc in repo_points:
            draw.text((rx + 35, rpy), rk + ":", font=F_SM_B, fill=C_LAVENDER)
            draw.text((rx + 35, rpy + 26), rv, font=F_MONO_SM if "git clone" in rv else F_SM, fill=rc)
            rpy += 78

        draw.text((100, 765), "Give developers a more direct starting point for investigation.",
                  font=F_HEADING, fill=C_LAVENDER)

    # Slide 6: Reporting and Notifications
    elif slide_idx == 6:
        draw.text((100, 60), "Clear findings. Better handoffs.", font=F_TITLE, fill=C_WHITE)
        draw.text((100, 118), "Structured investigation reports posted to Jira Cloud with concise stakeholder email notifications.",
                  font=F_SUB, fill=C_LAVENDER)

        gif4_thumb = os.path.join(GIF_DIR, "04-jira-email-reporting.gif")
        if os.path.exists(gif4_thumb):
            with Image.open(gif4_thumb) as g:
                g.seek(55)
                thumb = g.copy().resize((980, 551), Image.Resampling.LANCZOS)
                img.paste(thumb, (100, 180))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([100, 180, 1080, 731], radius=8, outline=C_VIOLET, width=2)

        rx = 1130
        draw.rounded_rectangle([rx, 180, 1820, 731], radius=14, fill=C_SURFACE, outline=C_LINE, width=1)
        draw.text((rx + 35, 215), "Consistent Report Format:", font=F_HEADING, fill=C_WHITE)

        rep_sections = [
            ("1. Issue Summary", "Clear executive recap of customer impact"),
            ("2. Evidence Observed", "Endpoints, HTTP statuses, and correlation IDs"),
            ("3. Probable Cause", "Synthesized hypothesis with explicit confidence score"),
            ("4. Recommended Next Steps", "Actionable verification and reproduction steps"),
            ("5. Approved Repository", "Direct link to source code package and branch"),
            ("6. Honest Integration", "Delivery status marked as Simulated in demo mode")
        ]
        sy = 275
        for sk, sv in rep_sections:
            draw.text((rx + 35, sy), sk, font=F_BODY_B, fill=C_LAVENDER)
            draw.text((rx + 35, sy + 26), sv, font=F_SM, fill=C_MUTED)
            sy += 68

        draw.text((100, 765), "Prepare consistent investigation updates without repetitive manual writing.",
                  font=F_HEADING, fill=C_LAVENDER)

    # Slide 7: Connected Architecture
    elif slide_idx == 7:
        draw.text((100, 55), "One connected investigation workflow.", font=F_TITLE, fill=C_WHITE)
        draw.text((100, 110), "Modular multi-tier architecture connecting Atlassian Jira, Spring Boot, FastAPI, and React.",
                  font=F_SUB, fill=C_LAVENDER)

        # 7-Step Architecture Flow Diagram (Top Half)
        arch_steps = [
            ("Jira Cloud", "Webhook / REST Ingest", C_LAVENDER),
            ("Spring Boot", "Workflow Orchestrator", C_VIOLET),
            ("Python FastAPI", "Log Analysis Engine", C_VIOLET),
            ("AI Adapter", "Evidence & RCA Model", C_TEAL),
            ("Repo Matcher", "Service Catalog Engine", C_TEAL),
            ("Jira & Email", "Report & Notification", C_LAVENDER),
            ("React Console", "Unified Dashboard", C_WHITE)
        ]
        
        ax = 100
        aw = 215
        ah = 175
        agap = 24
        ay = 175

        for s_i, (s_name, s_sub, s_col) in enumerate(arch_steps):
            x = ax + s_i * (aw + agap)
            draw.rounded_rectangle([x, ay, x + aw, ay + ah], radius=10, fill=C_SURFACE, outline=C_LINE, width=1)
            draw.text((x + 16, ay + 20), f"0{s_i+1}", font=F_XS, fill=C_MUTED)
            draw.text((x + 16, ay + 48), s_name, font=F_BODY_B, fill=s_col)
            draw.text((x + 16, ay + 82), s_sub, font=F_SM, fill=C_MUTED)
            
            # Flow arrow
            if s_i < len(arch_steps) - 1:
                ar_x1 = x + aw + 4
                ar_x2 = ar_x1 + agap - 8
                ar_y = ay + ah // 2
                draw.line([(ar_x1, ar_y), (ar_x2, ar_y)], fill=C_VIOLET, width=2)
                draw.polygon([(ar_x2, ar_y - 4), (ar_x2 + 5, ar_y), (ar_x2, ar_y + 4)], fill=C_VIOLET)

        # 4 Core Architectural Benefits (Bottom Half)
        b_cards = [
            ("Consistent Ticket Validation", "Every Jira issue is checked for diagnostic completeness before manual engineer hours are spent."),
            ("Better-Organized Evidence", "Scattered logs are clustered by correlation ID and highlighted with exact HTTP status anomalies."),
            ("Faster Repository Discovery", "Engineers get copy-ready clone commands for approved synthetic service repositories in seconds."),
            ("Clearer Reporting & Handoffs", "Standardized markdown summaries ensure QA, developers, and on-call SREs stay perfectly aligned.")
        ]
        bx = 100
        bw = 390
        bh = 270
        bgap = 33
        by = 400

        for b_i, (b_title, b_desc) in enumerate(b_cards):
            x = bx + b_i * (bw + bgap)
            draw.rounded_rectangle([x, by, x + bw, by + bh], radius=12, fill=C_SURFACE_2, outline=C_LINE, width=1)
            draw.text((x + 24, by + 24), "✓ " + b_title, font=F_BODY_B, fill=C_LAVENDER)
            draw.text((x + 24, by + 80), b_desc, font=F_SM, fill=C_WHITE)

        draw.text((100, 740), "Designed to organize the investigation while keeping developers in control.",
                  font=F_HEADING, fill=C_LAVENDER)

    # Slide 8: Cinematic Closing
    elif slide_idx == 8:
        cx, cy = w // 2, h // 2 - 30
        if logo_icon:
            icon_lg = logo_icon.resize((240, 240), Image.Resampling.LANCZOS)
            img.paste(icon_lg, (cx - 120, cy - 200), icon_lg)

        draw = ImageDraw.Draw(img)
        # Headline
        c_head = "Less repetitive triage. More time to solve."
        bbox = draw.textbbox((0, 0), c_head, font=F_DISPLAY)
        hw = bbox[2] - bbox[0]
        draw.text(((w - hw) // 2, cy + 70), c_head, font=F_DISPLAY, fill=C_WHITE)

        # Violet bar
        draw.rectangle([(w // 2 - 160, cy + 155), (w // 2 + 160, cy + 159)], fill=C_VIOLET)

        # Tagline
        c_sub = "JiraPilot AI — Your investigation copilot."
        bbox_sub = draw.textbbox((0, 0), c_sub, font=F_TITLE)
        csw = bbox_sub[2] - bbox_sub[0]
        draw.text(((w - csw) // 2, cy + 180), c_sub, font=F_TITLE, fill=C_LAVENDER)

        draw.text(((w - 400) // 2, h - 80), "Open Source  •  Northstar Digital Systems", font=F_SM, fill=C_MUTED)

    # Footer navigation indicator on content slides (Slides 2-7)
    if 2 <= slide_idx <= 7:
        draw.line([(100, h - 60), (1820, h - 60)], fill=(*C_LINE, 120), width=1)
        draw.text((100, h - 45), f"JiraPilot AI — Product Presentation  |  Slide {slide_idx} of 8",
                  font=F_XS, fill=C_MUTED)
        draw.text((1600, h - 45), "Northstar Digital Systems", font=F_XS, fill=C_MUTED)

    out_path = os.path.join(IMG_DIR, f"slide-{slide_idx:02d}.png")
    img.convert("RGB").save(out_path, "PNG")
    print(f"[OK] Saved slide canvas: {out_path}")
    return img.convert("RGB")

# -------------------------------------------------------------------------
# Part 2: PowerPoint (.pptx) Generator with Native Editable Shapes & Cards
# -------------------------------------------------------------------------
def generate_powerpoint():
    print("=" * 60)
    print("Generating Editable 16:9 PowerPoint (JiraPilot-AI-Hackathon.pptx)...")
    print("=" * 60)

    prs = Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    slides_data = [
        (1, "Turn Jira issues into actionable investigations.", "AI-powered ticket triage, log analysis and repository discovery."),
        (2, "Too much time spent finding where to start.", "The challenge isn't only solving the issue. It's organizing the investigation."),
        (3, "Every new issue gets a clearer next step.", "Identify missing information before investigation goes deeper."),
        (4, "Turn raw logs into structured evidence.", "From raw log lines to a clearer debugging path."),
        (5, "Find a relevant place to start debugging.", "Give developers a more direct starting point for investigation."),
        (6, "Clear findings. Better handoffs.", "Prepare consistent investigation updates without repetitive manual writing."),
        (7, "One connected investigation workflow.", "Designed to organize the investigation while keeping developers in control."),
        (8, "Less repetitive triage. More time to solve.", "JiraPilot AI — Your investigation copilot.")
    ]

    for s_idx, title, sub in slides_data:
        slide = prs.slides.add_slide(blank_layout)
        
        # 1. Base slide background image (dark purple canvas)
        canvas_path = os.path.join(IMG_DIR, f"slide-{s_idx:02d}.png")
        if os.path.exists(canvas_path):
            slide.shapes.add_picture(canvas_path, Inches(0), Inches(0), Inches(13.333), Inches(7.5))

        # 2. Embed assigned GIF into corresponding content slide
        gif_mapping = {
            3: "01-jira-ticket-readiness.gif",
            4: "02-log-analysis.gif",
            5: "03-repository-discovery.gif",
            6: "04-jira-email-reporting.gif",
            7: "05-end-to-end-workflow.gif"
        }
        if s_idx in gif_mapping:
            gif_path = os.path.join(GIF_DIR, gif_mapping[s_idx])
            if os.path.exists(gif_path):
                # Place GIF on the left side of content slide (or center on slide 7)
                if s_idx == 7:
                    slide.shapes.add_picture(gif_path, Inches(1.5), Inches(1.8), Inches(10.333), Inches(4.5))
                else:
                    slide.shapes.add_picture(gif_path, Inches(0.7), Inches(1.25), Inches(6.8), Inches(3.82))

        # 3. Add editable text overlay shapes for full PowerPoint editability
        tb = slide.shapes.add_textbox(Inches(0.7), Inches(0.4), Inches(11.9), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.color.rgb = RGB_WHITE

        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(14)
        p_sub.font.color.rgb = RGB_LAVENDER

    prs.save(PPTX_PATH)
    print(f"[OK] Generated PowerPoint presentation: {PPTX_PATH}")

# -------------------------------------------------------------------------
# Part 3: PDF Generation (High-Resolution 8-Slide Canvas Stack)
# -------------------------------------------------------------------------
def generate_pdf():
    print("\n" + "=" * 60)
    print("Exporting High-Resolution PDF (JiraPilot-AI-Hackathon.pdf)...")
    print("=" * 60)

    slide_images = []
    for s_idx in range(1, 9):
        img_path = os.path.join(IMG_DIR, f"slide-{s_idx:02d}.png")
        if os.path.exists(img_path):
            slide_images.append(Image.open(img_path).convert("RGB"))

    if slide_images:
        slide_images[0].save(
            PDF_PATH,
            save_all=True,
            append_images=slide_images[1:],
            resolution=100.0,
            quality=95
        )
        print(f"[OK] Saved complete 8-slide PDF: {PDF_PATH}")

def main():
    print("=" * 60)
    print("Rendering 8 Presentation Slides (1920x1080)...")
    print("=" * 60)
    for s_idx in range(1, 9):
        render_slide_canvas(s_idx)

    generate_powerpoint()
    generate_pdf()

if __name__ == "__main__":
    main()
