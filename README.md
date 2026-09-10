# Velocity AI Cartoon YouTube Bot

Heroku worker Telegram bot.

## Config Vars
BOT_TOKEN=Telegram bot token
GEMINI_API_KEY=Google AI Studio API key
POLLINATIONS_API_KEY=Pollinations API key for image generation
GEMINI_MODEL=gemini-3.5-flash-lite (optional; code auto-selects an available Flash model if needed)
IMAGE_MODEL=flux (optional)
TTS_VOICE=en-US-AriaNeural (optional)

The project bundles FFmpeg through imageio-ffmpeg, so an APT buildpack is not required.
Use the Python buildpack only.
