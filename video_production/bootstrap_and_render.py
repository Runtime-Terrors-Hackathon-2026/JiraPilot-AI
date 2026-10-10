#!/usr/bin/env python3
"""
JiraPilot AI — One-click install + render bootstrap
====================================================
Run this first if moviepy / pillow aren't installed yet.
Installs dependencies, then renders the title card immediately
and launches the full video render.

Usage:
    python bootstrap_and_render.py
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(__file__)

def pip_install(*packages):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])

print("=" * 60)
print("JiraPilot AI — Video Production Bootstrap")
print("=" * 60)

# 1. Install dependencies
print("\n[1/3] Installing Python dependencies…")
try:
    pip_install("moviepy==1.0.3", "pillow", "numpy", "decorator<5", "imageio[ffmpeg]")
    print("      ✓ Dependencies installed.")
except Exception as e:
    print(f"      ✗ pip install failed: {e}")
    print("      Please run manually:  pip install moviepy==1.0.3 pillow numpy")
    sys.exit(1)

# 2. Generate title card (Pillow only — fast)
print("\n[2/3] Generating closing title card…")
title_card_script = os.path.join(ROOT, "generate_title_card.py")
subprocess.check_call([sys.executable, title_card_script])

# 3. Render full video
print("\n[3/3] Rendering full 60-second video (this may take 10–30 minutes)…")
print("      Progress will be shown below. Do not close this window.\n")
render_script = os.path.join(ROOT, "render_jirapilot_video.py")
subprocess.check_call([sys.executable, render_script])

print("\n" + "=" * 60)
print("Bootstrap complete. Check the output/ folder for your files.")
print("=" * 60)
