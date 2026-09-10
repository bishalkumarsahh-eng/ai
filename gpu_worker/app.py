import os, secrets, subprocess, tempfile, pathlib, shutil
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import FileResponse

app = FastAPI(title="Velocity Cartoon GPU Lip-Sync Worker")
API_KEY = os.getenv("GPU_WORKER_KEY", "")
SADTALKER_DIR = pathlib.Path(os.getenv("SADTALKER_DIR", "/opt/SadTalker"))
TIMEOUT = int(os.getenv("SADTALKER_TIMEOUT", "900"))

def auth(value):
    if API_KEY and value != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"ok": True, "service": "velocity-cartoon-gpu", "sadtalker": str(SADTALKER_DIR)}

@app.post("/v1/lipsync")
async def lipsync(image: UploadFile = File(...), audio: UploadFile = File(...),
                  authorization: str | None = Header(default=None)):
    auth(authorization)
    work = pathlib.Path(tempfile.mkdtemp(prefix="velocity_gpu_"))
    try:
        img = work / "source.jpg"
        wav = work / "audio.wav"
        outdir = work / "results"
        outdir.mkdir()
        img.write_bytes(await image.read())
        wav.write_bytes(await audio.read())

        cmd = [
            "python", str(SADTALKER_DIR / "inference.py"),
            "--driven_audio", str(wav),
            "--source_image", str(img),
            "--result_dir", str(outdir),
            "--preprocess", "crop",
            "--still",
            "--expression_scale", "1.0",
        ]
        enhancer = os.getenv("SADTALKER_ENHANCER", "").strip()
        if enhancer:
            cmd += ["--enhancer", enhancer]

        p = subprocess.run(cmd, cwd=str(SADTALKER_DIR), capture_output=True,
                           text=True, timeout=TIMEOUT)
        if p.returncode != 0:
            detail = (p.stderr or p.stdout or "SadTalker failed")[-4000:]
            raise HTTPException(status_code=500, detail=detail)

        videos = sorted(outdir.rglob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not videos:
            raise HTTPException(status_code=500, detail="SadTalker completed but produced no MP4.")
        return FileResponse(str(videos[0]), media_type="video/mp4", filename="lipsync.mp4")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="SadTalker timed out.")
    finally:
        shutil.rmtree(work, ignore_errors=True)
