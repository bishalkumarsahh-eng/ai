import os
import shutil


def ffmpeg_bin():
    """Use the FFmpeg installed by Heroku Apt buildpack."""
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("FFmpeg not found. Ensure heroku-buildpack-apt is installed and Aptfile contains ffmpeg.")
    return path
