# VELOCITY AI CARTOON YOUTUBE BOT

A Heroku Telegram bot that turns a story idea into a 16:9 cartoon-style MP4.

## Free-mode stack
- Story: Pollinations text endpoint
- Images: Pollinations image generation
- Voice: edge-tts
- Video assembly/animation: FFmpeg
- Hosting/orchestration: Heroku

No paid AI API key is required by the default code, although free endpoints can have
rate limits, availability changes, or terms that change. If you monetize the videos,
verify the current commercial-use terms of every provider/model you use.

## Heroku setup

Config Vars:
BOT_TOKEN = your Telegram bot token

Optional:
IMAGE_MODEL=flux
IMAGE_WIDTH=1536
IMAGE_HEIGHT=864
TTS_VOICE=en-US-AriaNeural
POLLINATIONS_API_KEY=your key if you later want authenticated/higher-quota access

Do NOT put secrets in source code.

## Use
/cartoon A funny story about two friends who discover a magical train.

The bot creates six scenes, voice narration, gentle camera motion, and a 1920x1080 MP4.

## Important limitation
This free build intentionally uses image-to-video-like camera animation rather than a
heavy diffusion video model. True generative motion (walking, fighting, lip-sync, etc.)
requires a GPU-backed video model. Open models such as Wan/LTX/CogVideoX can be added
behind a separate GPU worker later without changing the Telegram interface.

## YouTube
The output is 16:9, 1920x1080, H.264/AAC, 30 fps, and fast-start enabled.
