"""FFmpeg resolver for Heroku.

Uses a self-contained static FFmpeg downloaded by static-ffmpeg instead of
Heroku Apt FFmpeg, avoiding distro shared-library mismatches such as
libpulsecommon-16.1.so.
"""
from functools import lru_cache
from static_ffmpeg import run

@lru_cache(maxsize=1)
def ffmpeg_path() -> str:
    ffmpeg, _ = run.get_or_fetch_platform_executables_else_raise()
    return str(ffmpeg)
