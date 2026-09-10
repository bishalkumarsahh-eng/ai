import os, pathlib, requests, time
from .ffmpeg_util import ffmpeg_path
import subprocess

DEFAULT_TIMEOUT = int(os.getenv("LIPSYNC_TIMEOUT", "900"))

def _to_wav(audio, workdir):
    out = pathlib.Path(workdir) / "driving.wav"
    subprocess.run([
        ffmpeg_path(), "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(audio), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(out)
    ], check=True)
    return out

def _remote_lipsync(image, audio, outfile):
    url = os.getenv("LIPSYNC_API_URL")
    if not url:
        raise RuntimeError(
            "LIPSYNC_API_URL is missing. Deploy the included GPU worker and put its "
            "HTTPS URL in the Heroku Config Vars."
        )
    key = os.getenv("LIPSYNC_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    with open(image, "rb") as img, open(audio, "rb") as aud:
        files = {
            "image": (pathlib.Path(image).name, img, "image/jpeg"),
            "audio": (pathlib.Path(audio).name, aud, "audio/wav"),
        }
        r = requests.post(url.rstrip("/") + "/v1/lipsync", files=files,
                           headers=headers, timeout=DEFAULT_TIMEOUT)
    if r.status_code != 200:
        detail = r.text[:1000]
        raise RuntimeError(f"GPU lip-sync worker HTTP {r.status_code}: {detail}")
    ctype = (r.headers.get("content-type") or "").lower()
    if "video" not in ctype and not r.content.startswith(b"\x00\x00\x00"):
        raise RuntimeError(f"GPU worker did not return an MP4 video (content-type={ctype}).")
    pathlib.Path(outfile).write_bytes(r.content)
    if not pathlib.Path(outfile).exists() or pathlib.Path(outfile).stat().st_size < 1024:
        raise RuntimeError("GPU worker returned an empty video.")

async def make_lipsync(image, audio, outfile):
    workdir = pathlib.Path(outfile).parent / "_lipsync"
    workdir.mkdir(parents=True, exist_ok=True)
    wav = _to_wav(audio, workdir)
    attempts = int(os.getenv("LIPSYNC_RETRIES", "2"))
    last = None
    for attempt in range(1, attempts + 1):
        try:
            _remote_lipsync(image, wav, outfile)
            return str(outfile)
        except Exception as e:
            last = e
            if attempt < attempts:
                time.sleep(3 * attempt)
    raise RuntimeError(f"External GPU lip-sync failed after {attempts} attempts: {last}") from last
