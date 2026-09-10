import os, asyncio, shutil, subprocess, pathlib, time
from .ffmpeg_utils import ffmpeg_bin, ffmpeg_env
from gradio_client import Client, handle_file

DEFAULT_SPACE = "henrybit/SadTalker-Demo"


def _make_client(space, token):
    if token:
        try:
            return Client(space, token=token)
        except TypeError:
            try:
                return Client(space, hf_token=token)
            except TypeError:
                return Client(space, headers={"Authorization": f"Bearer {token}"})
    return Client(space)


def _result_path(result):
    if isinstance(result, (list, tuple)):
        for x in result:
            p = _result_path(x)
            if p:
                return p
        return None
    if isinstance(result, dict):
        return result.get("path") or result.get("url")
    p = getattr(result, "path", None)
    if p:
        return p
    u = getattr(result, "url", None)
    if u:
        return u
    return result if isinstance(result, str) else None


def _to_wav(audio, workdir):
    out = pathlib.Path(workdir) / "driving.wav"
    subprocess.run([
        ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(audio), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(out)
    ], check=True, env=ffmpeg_env())
    return out


def _run_lipsync(space, token, image, audio):
    client = _make_client(space, token)
    # Current henrybit/SadTalker-Demo exposes /generate with these six inputs.
    return client.predict(
        handle_file(str(image)),
        handle_file(str(audio)),
        "crop",
        False,
        0,
        1.0,
        api_name="/generate",
    )


async def make_lipsync(image, audio, outfile):
    space = os.getenv("LIPSYNC_SPACE", DEFAULT_SPACE)
    token = os.getenv("HF_TOKEN") or None
    workdir = pathlib.Path(outfile).parent / "_lipsync"
    workdir.mkdir(parents=True, exist_ok=True)
    wav = _to_wav(audio, workdir)

    last = None
    for attempt in range(1, 4):
        try:
            result = await asyncio.to_thread(_run_lipsync, space, token, image, wav)
            source = _result_path(result)
            if not source:
                raise RuntimeError(f"Space returned no video: {result!r}")
            if str(source).startswith(("http://", "https://")):
                raise RuntimeError("Space returned a remote URL instead of a local video file")
            if not os.path.exists(str(source)):
                raise RuntimeError(f"Returned video does not exist: {source}")
            shutil.copyfile(str(source), str(outfile))
            if os.path.getsize(str(outfile)) == 0:
                raise RuntimeError("Returned video is empty")
            return str(outfile)
        except Exception as e:
            last = e
            if attempt < 3:
                await asyncio.sleep(5 * attempt)

    raise RuntimeError(
        "Lip-sync service failed after 3 attempts. "
        "The public ZeroGPU Space may be busy or its current runtime may have failed. "
        f"Last error: {last}"
    ) from last
