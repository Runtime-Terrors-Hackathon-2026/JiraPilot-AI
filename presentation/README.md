# JiraPilot AI — Hackathon Presentation Package & Assets

> **Product:** JiraPilot AI  
> **Tagline:** *Your investigation copilot.*  
> **Fictional Organization:** Northstar Digital Systems  
> **Visual Identity:** Deep Purple (`#170B2B`) & Near-Black (`#08070D`) with Electric Violet (`#8B5CF6`) and Lavender (`#C4B5FD`) Accents  
> **Design Inspiration:** Instagram PowerPoint-Design Reference (Concentric purple light rings, glass cards, geometric emblem)

---

## 🚀 Quick Start Guide

### 1. View the Presentation
* **Editable PowerPoint:** Open [`JiraPilot-AI-Hackathon.pptx`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/JiraPilot-AI-Hackathon.pptx) in Microsoft PowerPoint, Apple Keynote, or Google Slides.
  * Native 16:9 widescreen format (13.333" × 7.5").
  * All titles, subtitles, and bullet points are editable text boxes.
  * Workflow GIFs are embedded in Slides 3, 4, 5, 6, and 7.
* **Portable PDF Fallback:** Open [`JiraPilot-AI-Hackathon.pdf`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/JiraPilot-AI-Hackathon.pdf) in any web browser or PDF viewer for instant static presentation on mobile or web.

### 2. Watch the Product Demonstration Film
* **Master MP4 Video:** Play [`JiraPilot-AI-Product-Demo.mp4`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/JiraPilot-AI-Product-Demo.mp4).
  * Exactly 60.00 seconds (1800 frames at 30.00 fps).
  * 1920 × 1080 Full HD (16:9).
  * Includes professional English voice-over narration, synchronized background music with voice ducking, and clean typography.

---

## 📁 Package Directory Structure

```
presentation/
├── JiraPilot-AI-Hackathon.pptx          # Editable 16:9 widescreen PowerPoint presentation (8 slides)
├── JiraPilot-AI-Hackathon.pdf           # High-resolution PDF presentation export (all 8 slides)
├── JiraPilot-AI-Product-Demo.mp4        # 60.00-second product demonstration video (1080p @ 30fps)
├── slide-content.md                     # Full slide-by-slide transcript, headlines & notes
├── storyboard.md                        # Complete 60-second timecoded video storyboard
├── README.md                            # This comprehensive guide
│
├── assets/
│   ├── gifs/                            # 5 standalone animated workflow GIFs (1280x720, 16:9)
│   │   ├── 01-jira-ticket-readiness.gif # Ticket completeness audit & amber warning
│   │   ├── 02-log-analysis.gif          # Telemetry extraction & error grouping
│   │   ├── 03-repository-discovery.gif  # Approved repo match & copy-ready clone command
│   │   ├── 04-jira-email-reporting.gif  # Formatted Jira comment & stakeholder email
│   │   └── 05-end-to-end-workflow.gif   # 6-step lifecycle with moving pulse highlight
│   │
│   ├── images/                          # High-resolution slide renders & brand marks
│   │   ├── logo-icon.png                # Original geometric JiraPilot AI flight emblem
│   │   ├── logo-full.png                # Horizontal brand mark with typography
│   │   ├── background-canvas.png        # Master 1080p concentric rings dark-purple canvas
│   │   ├── slide-01.png                 # Slide 1 1080p render (Opening)
│   │   ├── slide-02.png                 # Slide 2 1080p render (The Problem)
│   │   ├── slide-03.png                 # Slide 3 1080p render (Ticket Readiness)
│   │   ├── slide-04.png                 # Slide 4 1080p render (Log Analysis)
│   │   ├── slide-05.png                 # Slide 5 1080p render (Repository Discovery)
│   │   ├── slide-06.png                 # Slide 6 1080p render (Reporting & Notifications)
│   │   ├── slide-07.png                 # Slide 7 1080p render (Connected Architecture)
│   │   └── slide-08.png                 # Slide 8 1080p render (Closing)
│   │
│   ├── video/
│   │   └── scenes/                      # Extracted scene clips
│   │
│   └── voiceover/                       # Isolated audio stems
│       ├── master_voiceover.wav         # 60.0s isolated voice-over speech track
│       ├── mixed_audio.wav              # 60.0s mixed voice-over + ducked ambient music
│       └── vo_scene_01.wav ... 08.wav   # Individual scene narration takes
│
└── source/                              # Python production scripts
    ├── generate_brand_assets.py         # Builds logo emblem, wordmark & canvas
    ├── render_gifs.py                   # Renders all 5 workflow GIFs via FFmpeg palettegen
    ├── generate_presentation.py         # Compiles PPTX via python-pptx & exports PDF
    └── render_demo_video.py             # Renders 60.0s master demo film via FFmpeg
```

---

## 🎨 Visual Design System

Inspired by the reference video's sleek aesthetic:
* **Backgrounds:** Near-black (`#08070D`) and deep royal purple (`#170B2B`).
* **Primary Glow:** Electric violet (`#8B5CF6`) for emphasis and progress highlights.
* **Secondary Accent:** Lavender (`#C4B5FD`) for clear, soft secondary typography.
* **Status Colors:**
  * **Teal (`#2DD4BF`):** Validated fields, successful checks, confirmed steps.
  * **Amber (`#FBBF24`):** Missing details, diagnostic gaps, hypotheses needing verification.
  * **Red (`#F87171`):** Errors, HTTP 503 failures, circuit breaker trips.
* **Typography:** Segoe UI / Inter modern sans-serif with Consolas monospace for telemetry.
* **Brand Logo:** An original faceted delta wings emblem with concentric orbital rings symbolizing rapid engineering flight and intelligent triage.

---

## 💡 The 5 Workflow GIFs (Explained in Simple English)

1. **[`01-jira-ticket-readiness.gif`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/assets/gifs/01-jira-ticket-readiness.gif)**
   * *What it shows:* A new Jira bug report arrives (`NOVA-1001`). JiraPilot AI automatically audits whether the reporter gave enough details. When logs or payload are missing, it highlights them in amber and prepares a polite comment asking for the right info before developers waste hours guessing.
2. **[`02-log-analysis.gif`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/assets/gifs/02-log-analysis.gif)**
   * *What it shows:* JiraPilot AI reads the raw server logs, automatically spots the failing URL (`POST /api/v1/resources`), the error code (`HTTP 503`), and the tracking ID (`CORR-DEMO-1001`). It groups related errors together and labels the cause as a hypothesis for developers to verify.
3. **[`03-repository-discovery.gif`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/assets/gifs/03-repository-discovery.gif)**
   * *What it shows:* The system looks up the organization's verified service catalog and finds the exact code repository (`resource-inventory-service`). It generates a copy-ready `git clone` command so developers can start debugging locally in one click.
4. **[`04-jira-email-reporting.gif`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/assets/gifs/04-jira-email-reporting.gif)**
   * *What it shows:* JiraPilot AI packages the findings into a clear, structured summary. It previews a Jira ticket comment and an on-call email notification so the whole team stays informed without repetitive manual writing.
5. **[`05-end-to-end-workflow.gif`](file:///c:/Users/support/Downloads/RUNTIME_Terrors/presentation/assets/gifs/05-end-to-end-workflow.gif)**
   * *What it shows:* A high-level visual journey across all 6 steps: Ticket → Readiness → Log Analysis → Repo Discovery → Reporting → Operations Dashboard, with a moving progress pulse.

---

## 🔁 How to Re-Run or Re-Generate All Assets

All generator scripts are located in `presentation/source/` and run using the local Python environment:

```powershell
# 1. Regenerate Brand Assets (Logo, emblem, master canvas)
python presentation/source/generate_brand_assets.py

# 2. Re-render the 5 Animated Workflow GIFs
python presentation/source/render_gifs.py

# 3. Re-build PowerPoint (.pptx) and Export Multi-page PDF (.pdf)
python presentation/source/generate_presentation.py

# 4. Re-render Master 60-Second Video (.mp4)
python presentation/source/render_demo_video.py
```

---

## 🛡️ Synthetic Data & Public Safety Guarantees

* **Zero Confidential Data:** All issues (`NOVA-1001`), endpoints (`/api/v1/resources`), correlation IDs (`CORR-DEMO-1001`), and emails (`northstar.internal`) are synthetic.
* **No Invented URLs:** All repository clone URLs reference approved catalog entries (`github.com/northstar-labs/...`).
* **Responsible AI:** Root causes are clearly labeled as `Probable Cause — Verification Required`, ensuring engineers always verify findings before deploying fixes.
