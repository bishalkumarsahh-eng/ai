import os, asyncio, pathlib

async def make_voice(text, output):
    # Edge TTS is used because it requires no paid API account.
    # For a production/commercial channel, verify the provider's current terms.
    import edge_tts
    voice=os.getenv("TTS_VOICE","en-US-AriaNeural")
    communicate=edge_tts.Communicate(text, voice)
    await communicate.save(str(output))
    return output
