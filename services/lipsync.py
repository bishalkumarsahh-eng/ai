import os
import asyncio
import shutil
from gradio_client import Client, handle_file

DEFAULT_SPACE = "henrybit/SadTalker-Demo"


def _make_client(space, token):
    """Support both old and new gradio_client authentication APIs."""
    if not token:
        return Client(space)
    try:
        return Client(space, token=token)
    except TypeError:
        try:
            return Client(space, hf_token=token)
        except TypeError:
            return Client(space, headers={"Authorization": f"Bearer {token}"})


def _result_path(result):
    """Extract a local file path from common Gradio result formats."""
    if isinstance(result, (list, tuple)):
        if not result:
            return None
        # Current SadTalker returns one video output, but tolerate nested values.
        for item in result:
            path = _result_path(item)
            if path:
                return path
        return None
    if isinstance(result, dict):
        for key in ("path", "url"):
            value = result.get(key)
            if value:
                return value
        return None
    path = getattr(result, "path", None)
    if path:
        return path
    url = getattr(result, "url", None)
    if url:
        return url
    if isinstance(result, str):
        return result
    return None


def _run_lipsync(space, token, image, audio):
    client = _make_client(space, token)

    # Verified against the current henrybit/SadTalker-Demo app.py.
    # Its /generate function has exactly these six inputs:
    # source_image, driven_audio, preprocess, still_mode,
    # pose_style, expression_scale.
    return client.predict(
        handle_file(str(image)),
        handle_file(str(audio)),
        "crop",       # preprocess
        False,         # still_mode
        0,             # pose_style
        1.0,           # expression_scale
        api_name="/generate",
    )


async def make_lipsync(image, audio, outfile):
    space = os.getenv("LIPSYNC_SPACE", DEFAULT_SPACE)
    token = os.getenv("HF_TOKEN") or None

    try:
        result = await asyncio.to_thread(
            _run_lipsync, space, token, image, audio
        )
        source = _result_path(result)
        if not source:
            raise RuntimeError(f"Lip-sync Space returned no video file: {result!r}")

        # Gradio normally downloads file outputs to a local cache path.
        # If a URL is returned, gradio_client should generally have downloaded it;
        # reject a remote URL rather than creating a corrupt output.
        if str(source).startswith(("http://", "https://")):
            raise RuntimeError(
                "Lip-sync Space returned a remote URL instead of a local file. "
                "Please retry or use a newer gradio_client."
            )

        if not os.path.exists(str(source)):
            raise RuntimeError(f"Lip-sync output file does not exist: {source}")

        shutil.copyfile(str(source), str(outfile))
        if not os.path.exists(str(outfile)) or os.path.getsize(str(outfile)) == 0:
            raise RuntimeError("Lip-sync output video is empty.")
        return outfile
    except Exception as e:
        raise RuntimeError(
            "Lip-sync generation failed. The Hugging Face Space may be busy, "
            "out of ZeroGPU quota, or temporarily unavailable. "
            f"Details: {e}"
        ) from e
