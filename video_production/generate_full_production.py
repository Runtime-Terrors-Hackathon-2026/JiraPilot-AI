"""
JiraPilot AI — Master Audio & Video Production Orchestrator
Renders complete 60-second enterprise film with audio, captions, and individual clips.
"""

import os
import sys
import subprocess
import wave
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
OUT_DIR = os.path.join(BASE_DIR, "output")
SCENES_DIR = os.path.join(OUT_DIR, "scenes")
AUDIO_DIR = os.path.join(OUT_DIR, "audio")
CAPTIONS_DIR = os.path.join(OUT_DIR, "captions")

for d in [OUT_DIR, SCENES_DIR, AUDIO_DIR, CAPTIONS_DIR]:
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, BASE_DIR)

PYTHON_EXE = r"C:\Users\support\AppData\Local\Programs\Python\Python312\python.exe"

# Voice-over script segments
VO_SEGMENTS = [
    (0.5, "Every software incident starts with a question: where do we begin?"),
    (5.5, "JiraPilot AI turns a new Jira issue into a structured investigation."),
    (12.5, "It checks ticket readiness and helps developers request the details they need."),
    (20.5, "It analyzes logs, connects related errors, and surfaces evidence behind likely failure points."),
    (30.5, "It recommends approved repositories and prepares copy-ready clone commands for debugging."),
    (38.5, "It prepares readable investigation reports and keeps the team informed."),
    (47.5, "Evidence, next steps and investigation status stay in one place."),
    (54.4, "Less repetitive triage. Clearer investigations. More time for developers to solve problems.")
]

def generate_voiceover_clips():
    print("=" * 60)
    print("[1/5] Synthesizing Voice-Over Audio Tracks...")
    print("=" * 60)
    
    ps_script = """
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SelectVoice("Microsoft Zira Desktop")
    $synth.Rate = 0
    """
    
    clip_files = []
    for idx, (start_time, text) in enumerate(VO_SEGMENTS, 1):
        wav_path = os.path.join(AUDIO_DIR, f"vo_scene_{idx:02d}.wav").replace("\\", "/")
        clip_files.append((start_time, wav_path))
        safe_text = text.replace('"', '`"')
        ps_script += f"""
        $synth.SetOutputToWaveFile("{wav_path}")
        $synth.Speak("{safe_text}")
        """
    
    ps_script += "\n$synth.Dispose()\n"
    
    # Run powershell synthesis
    proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
    if proc.returncode != 0:
        print("PowerShell TTS error:", proc.stderr)
        raise RuntimeError("TTS generation failed")
    
    print("[OK] All 8 scene voice-over clips synthesized.")
    return clip_files

def assemble_voiceover_track(clip_files):
    print("\n[2/5] Assembling 60-Second Master Voice-Over Track...")
    sample_rate = 44100
    total_samples = int(60.0 * sample_rate)
    master_vo = np.zeros((total_samples, 2), dtype=np.float32)

    for start_time, clip_path in clip_files:
        with wave.open(clip_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_data = wf.readframes(n_frames)

            # Convert to float32
            if sampwidth == 2:
                samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                samples = np.frombuffer(audio_data, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0

            if n_channels == 1:
                samples = np.column_stack([samples, samples])
            else:
                samples = samples.reshape(-1, 2)

            # Resample to 44100 if necessary
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

            start_sample = int(start_time * sample_rate)
            end_sample = min(total_samples, start_sample + len(samples))
            fit_len = end_sample - start_sample
            if fit_len > 0:
                master_vo[start_sample:end_sample] += samples[:fit_len]

    # Normalize VO
    max_val = np.max(np.abs(master_vo))
    if max_val > 0:
        master_vo = master_vo / max_val * 0.90

    vo_master_path = os.path.join(AUDIO_DIR, "voiceover_track.wav")
    out_int16 = (master_vo * 32767.0).astype(np.int16)
    with wave.open(vo_master_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(out_int16.tobytes())

    print(f"[OK] Master Voice-Over track exported: {vo_master_path}")
    return vo_master_path, master_vo

def assemble_ambient_soundtrack(master_vo):
    print("\n[3/5] Building Ambient Soundtrack & Intelligent Audio Mix...")
    sample_rate = 44100
    total_samples = int(60.0 * sample_rate)
    
    # Check sample audio from Reference Video
    sample_wav = os.path.join(PROJECT_ROOT, "sample_audio.wav")
    if os.path.exists(sample_wav):
        with wave.open(sample_wav, 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
            bed_samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            if wf.getnchannels() == 2:
                bed_samples = bed_samples.reshape(-1, 2)
            else:
                bed_samples = np.column_stack([bed_samples, bed_samples])
    else:
        # Generate soothing electronic ambient chord pad
        t = np.linspace(0, 60.0, total_samples, endpoint=False)
        # Minor 9th chord (D - F - A - C - E)
        pad = (0.25 * np.sin(2 * np.pi * 146.83 * t) +
               0.20 * np.sin(2 * np.pi * 174.61 * t) +
               0.20 * np.sin(2 * np.pi * 220.00 * t) +
               0.15 * np.sin(2 * np.pi * 261.63 * t) +
               0.10 * np.sin(2 * np.pi * 329.63 * t))
        bed_samples = np.column_stack([pad, pad])

    # Loop and crossfade ambient bed across 60.0s
    music_track = np.zeros((total_samples, 2), dtype=np.float32)
    bed_len = len(bed_samples)
    overlap = int(0.5 * sample_rate)
    step = max(1, bed_len - overlap)
    pos = 0
    while pos < total_samples:
        chunk = min(bed_len, total_samples - pos)
        music_track[pos:pos+chunk] += bed_samples[:chunk]
        pos += step

    # Intelligent Ducking Envelope based on VO activity
    vo_envelope = np.abs(master_vo[:, 0]) + np.abs(master_vo[:, 1])
    # Fast O(N) moving average box filter
    w = int(0.2 * sample_rate)
    padded = np.pad(vo_envelope, (w, w), mode='edge')
    cs = np.cumsum(padded)
    smoothed_vo = (cs[2*w:] - cs[:-2*w]) / float(2*w)
    
    # Duck music volume: 0.18 when VO is active, 0.40 during musical gaps
    gain = 0.40 - 0.22 * np.clip(smoothed_vo * 3.5, 0.0, 1.0)
    
    # Master Fade In (first 1.5s) & Fade Out (last 3.0s)
    t_axis = np.linspace(0, 60.0, total_samples)
    fade_in = np.clip(t_axis / 1.5, 0.0, 1.0)
    fade_out = np.clip((60.0 - t_axis) / 3.0, 0.0, 1.0)
    master_gain = gain * fade_in * fade_out

    music_track[:, 0] *= master_gain
    music_track[:, 1] *= master_gain

    # Export separate soundtrack
    music_path = os.path.join(AUDIO_DIR, "soundtrack_ambient.wav")
    m_int16 = (np.clip(music_track, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(music_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(m_int16.tobytes())

    # Master Mixed Audio Track
    mix_track = np.clip(master_vo * 0.95 + music_track * 0.85, -1.0, 1.0)
    mix_path = os.path.join(AUDIO_DIR, "mixed_audio.wav")
    mix_int16 = (mix_track * 32767.0).astype(np.int16)
    with wave.open(mix_path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(mix_int16.tobytes())

    print(f"[OK] Standalone Soundtrack exported: {music_path}")
    print(f"[OK] Mixed Audio Track exported:      {mix_path}")
    return mix_path

def render_video_with_ffmpeg(mixed_audio_path):
    print("\n[4/5] Rendering High-Definition 1080p Video Stream via FFmpeg...")
    import render_production_video as rpv
    
    # Target video output
    final_mp4 = os.path.join(OUT_DIR, "jirapilot_60s_final.mp4")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", "30",
        "-i", "-",  # Video frames from stdin
        "-i", mixed_audio_path,  # Audio from WAV
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_mp4
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    total_frames = rpv.TOTAL_FRAMES  # 1800
    print(f"Encoding {total_frames} frames (60.0s @ 30fps)...")

    for f_idx in range(total_frames):
        frame_img = rpv.get_frame(f_idx)
        raw_bytes = frame_img.tobytes()
        proc.stdin.write(raw_bytes)
        
        if (f_idx + 1) % 150 == 0 or f_idx == total_frames - 1:
            pct = int((f_idx + 1) / total_frames * 100)
            elapsed_sec = (f_idx + 1) / 30.0
            print(f"  -> Frame {f_idx + 1:4d}/{total_frames} ({pct:3d}%) | Timeline: {elapsed_sec:4.1f}s / 60.0s")

    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        err = proc.stderr.read().decode('utf-8', errors='ignore')
        print("FFmpeg encode error:", err)
        raise RuntimeError("Video encoding failed")

    print(f"\n[OK] Master 60-second video rendered successfully: {final_mp4}")
    return final_mp4

def burn_captions_and_render_individual_scenes(final_mp4):
    print("\n[5/5] Burning Captions & Exporting Scene Clips...")
    
    # 1. Captioned MP4
    srt_file = os.path.join(BASE_DIR, "captions", "jirapilot_captions.srt")
    captioned_mp4 = os.path.join(OUT_DIR, "jirapilot_60s_captioned.mp4")
    
    if os.path.exists(srt_file):
        # Escape path for ffmpeg subtitles filter
        escaped_srt = srt_file.replace("\\", "/").replace(":", "\\:")
        sub_filter = f"subtitles='{escaped_srt}':force_style='FontSize=22,FontName=Segoe UI,PrimaryColour=&H00F8EEE8,BackColour=&H80000000,BorderStyle=4,MarginV=35'"
        
        cmd_sub = [
            "ffmpeg", "-y",
            "-i", final_mp4,
            "-vf", sub_filter,
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "copy",
            captioned_mp4
        ]
        res = subprocess.run(cmd_sub, capture_output=True)
        if res.returncode == 0:
            print(f"[OK] Captioned version rendered: {captioned_mp4}")
        else:
            print("Note on burning subtitles:", res.stderr.decode('utf-8', errors='ignore')[-300:])

    # 2. Individual Scene Clips
    scenes = [
        ("scene_01_problem.mp4", 0.0, 5.0),
        ("scene_02_logo.mp4", 5.0, 7.0),
        ("scene_03_readiness.mp4", 12.0, 8.0),
        ("scene_04_logs.mp4", 20.0, 10.0),
        ("scene_05_repo.mp4", 30.0, 8.0),
        ("scene_06_reports.mp4", 38.0, 9.0),
        ("scene_07_dashboard.mp4", 47.0, 7.0),
        ("scene_08_closing.mp4", 54.0, 6.0),
    ]

    for clip_name, start_t, dur in scenes:
        out_clip = os.path.join(SCENES_DIR, clip_name)
        cmd_clip = [
            "ffmpeg", "-y",
            "-ss", str(start_t),
            "-i", final_mp4,
            "-t", str(dur),
            "-c", "copy",
            out_clip
        ]
        subprocess.run(cmd_clip, capture_output=True)
    
    print(f"[OK] All 8 individual scene clips exported to: {SCENES_DIR}")

def main():
    print("=" * 70)
    print("  JIRAPILOT AI — 60-SECOND ENTERPRISE VIDEO MASTER PRODUCTION")
    print("=" * 70)
    
    # 1. Voiceover
    vo_clips = generate_voiceover_clips()
    vo_master, vo_matrix = assemble_voiceover_track(vo_clips)

    # 2. Music & mix
    mixed_audio = assemble_ambient_soundtrack(vo_matrix)

    # 3. Master video render
    final_video = render_video_with_ffmpeg(mixed_audio)

    # 4. Captioned video & scene clips
    burn_captions_and_render_individual_scenes(final_video)

    # 5. Title card export
    import render_production_video as rpv
    rpv.export_title_card()

    print("\n" + "=" * 70)
    print("  PRODUCTION COMPLETE — ALL DELIVERABLES READY")
    print(f"  • Final Video (60s):      {final_video}")
    print(f"  • Captioned Video (60s):  {os.path.join(OUT_DIR, 'jirapilot_60s_captioned.mp4')}")
    print(f"  • Voice-Over Audio:       {vo_master}")
    print(f"  • Ambient Music:          {os.path.join(AUDIO_DIR, 'soundtrack_ambient.wav')}")
    print(f"  • Closing Title Card:     {os.path.join(OUT_DIR, 'closing_title_card.png')}")
    print(f"  • Scene Clips (1 to 8):   {SCENES_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
