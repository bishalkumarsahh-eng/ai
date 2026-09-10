# VELOCITY LONG-FORM TALKING CARTOON BOT V5

Chapter-wise long-form Telegram cartoon generator with Hinglish/English, AI story planning,
cartoon scenes, Edge-TTS voices, audio-driven SadTalker lip-sync and 1080p final rendering.

## Heroku Config Vars
BOT_TOKEN=...
GEMINI_API_KEY=...
POLLINATIONS_API_KEY=...
HF_TOKEN=...

Optional:
GEMINI_MODEL=gemini-3.5-flash-lite
IMAGE_MODEL=flux
LIPSYNC_SPACE=henrybit/SadTalker-Demo
TTS_VOICE_HINGLISH=en-IN-NeerjaNeural
TTS_VOICE_ENGLISH=en-US-AriaNeural

## Buildpack
https://github.com/heroku/heroku-buildpack-python

## Notes
The lip-sync client converts generated MP3 speech to mono 16 kHz WAV, retries the public
ZeroGPU Space up to three times, and uses the current /generate API. The Space expects a
clear face portrait; dialogue prompts therefore request large, unobstructed faces.

The public Space is shared infrastructure and can queue/fail. SadTalker animates a portrait,
not full-body cinematic acting. Long videos are assembled from many short scene clips.
