import os
import shutil
from pathlib import Path

def ffmpeg_bin():
    path = shutil.which("ffmpeg")
    if not path:
        apt_path = "/app/.apt/usr/bin/ffmpeg"
        if os.path.exists(apt_path):
            path = apt_path
    if not path:
        raise RuntimeError(
            "FFmpeg not found. Ensure heroku-buildpack-apt is installed "
            "and Aptfile contains ffmpeg."
        )
    return path

def ffmpeg_env():
    """Environment needed for binaries installed by Heroku Apt buildpack."""
    env = os.environ.copy()
    lib_dirs = [
        "/app/.apt/usr/lib/x86_64-linux-gnu",
        "/app/.apt/usr/lib",
        "/app/.apt/lib/x86_64-linux-gnu",
        "/app/.apt/lib",
    ]
    existing = [p for p in lib_dirs if os.path.isdir(p)]
    old = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = ":".join(existing + ([old] if old else []))
    return env
