# VELOCITY LONG-FORM TALKING CARTOON BOT v3

## What it does
- Telegram `/cartoon` command
- Hinglish or English
- 5 / 10 / 20 / 30 minute planning
- 6-10 story chapters
- character descriptions kept in every scene prompt
- cartoon scene generation
- AI voice
- actual audio-driven talking-head lip-sync through a public Hugging Face ZeroGPU SadTalker Space
- 1920x1080 final MP4

## Usage
/cartoon hinglish 10 A poor boy falls in love with a rich girl.
/cartoon english 20 A magical adventure story about two friends.

## Heroku Config Vars
BOT_TOKEN=...
GEMINI_API_KEY=...
POLLINATIONS_API_KEY=...

Optional:
GEMINI_MODEL=gemini-3.5-flash-lite
IMAGE_MODEL=flux
HF_TOKEN=...
LIPSYNC_SPACE=henrybit/SadTalker-Demo
TTS_VOICE_HINGLISH=en-IN-NeerjaNeural
TTS_VOICE_ENGLISH=en-US-AriaNeural

HF_TOKEN is optional for a public Space, but authenticated access can improve reliability/rate limits.

## Buildpacks
Python:
https://github.com/heroku/heroku-buildpack-python

APT:
https://github.com/heroku/heroku-buildpack-apt

Aptfile installs ffmpeg.

## Important reality check
The public ZeroGPU lip-sync Space is shared infrastructure. Hugging Face documents
that ZeroGPU Spaces are free to use but have account-based quotas and can have queueing.
The included code therefore fails clearly if the Space is unavailable instead of pretending
a video is lip-synced.

SadTalker is a talking-head model: it animates a portrait/full image with speech, not
full-body cinematic acting. For higher-end full-scene animation, add a video-generation
stage (for example image-to-video) before/around lip-sync.

Long jobs may exceed Heroku's request/process constraints or temporary disk limits.
The bot is a prototype for chapter-wise generation; for production, use a persistent
job queue and object storage.
