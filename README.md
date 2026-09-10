# VELOCITY LONG-FORM TALKING CARTOON BOT V13

Heroku controls the Telegram bot, story/chapter generation, images, TTS and final 1080p
rendering. Lip-sync is moved to a separate GPU worker so the bot no longer depends on the
public Hugging Face ZeroGPU Space or its daily quota.

## Heroku Config Vars
BOT_TOKEN=...
GEMINI_API_KEY=...
POLLINATIONS_API_KEY=...
LIPSYNC_API_URL=https://YOUR-GPU-WORKER
LIPSYNC_API_KEY=...

Optional:
GEMINI_MODEL=gemini-3.5-flash-lite
IMAGE_MODEL=flux
TTS_VOICE_HINGLISH=en-IN-NeerjaNeural
TTS_VOICE_ENGLISH=en-US-AriaNeural
LIPSYNC_TIMEOUT=900
LIPSYNC_RETRIES=2

HF_TOKEN and LIPSYNC_SPACE are NO LONGER USED.

## Heroku
Buildpack: python only is sufficient for the bot. static-ffmpeg supplies the app's local
FFmpeg binary; Apt FFmpeg is no longer required.

## GPU worker
See gpu_worker/README.md and gpu_worker/Dockerfile. It runs SadTalker locally on an NVIDIA
GPU and exposes POST /v1/lipsync. The official SadTalker project documents its pretrained
checkpoints and Docker/Linux setup. https://github.com/OpenTalker/SadTalker

## Long videos
Stories remain chapter-wise. Each dialogue scene is sent to the external GPU worker and the
resulting clips are joined by Heroku into a 1920x1080 MP4.
