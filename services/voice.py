import os, edge_tts

async def make_voice(text,outfile,language):
    if not text.strip():
        # 1 second silence through ffmpeg is generated later if needed.
        return None
    voice = os.getenv(
        "TTS_VOICE_HINGLISH" if language=="hinglish" else "TTS_VOICE_ENGLISH",
        "en-IN-NeerjaNeural" if language=="hinglish" else "en-US-AriaNeural"
    )
    await edge_tts.Communicate(text,voice).save(str(outfile))
    return outfile
