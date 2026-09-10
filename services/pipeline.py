import pathlib,tempfile,shutil,os,asyncio
from .story import make_story
from .images import make_image
from .voice import make_voice
from .lipsync import make_lipsync
from .render import render_lipsync_video

async def generate_project(idea,language,minutes,progress=None):
    async def p(x):
        if progress: await progress(x)

    work=pathlib.Path(tempfile.mkdtemp(prefix="velocity_long_"))
    try:
        await p("🧠 Building the full story and chapters…")
        story=await make_story(idea,language,minutes)
        scenes=story["scenes"]
        # Safety cap for a single Heroku job. Long videos are still built chapter-wise.
        max_scenes=minutes*10
        scenes=scenes[:max_scenes]

        chapter_dirs={}
        final_clips=[]
        for i,scene in enumerate(scenes,1):
            ch=int(scene.get("chapter",1))
            cdir=work/f"chapter_{ch}"
            cdir.mkdir(exist_ok=True)
            await p(f"📚 Chapter {ch} • Scene {i}/{len(scenes)}")

            visual=scene["visual"]
            # Strong consistency prompt is carried through every scene.
            character_text="; ".join(
                f'{c["name"]}: {c["description"]}' for c in story.get("characters",[])
            )
            prompt=(
                "High-quality 2D/3D animated cartoon movie frame, cinematic lighting, "
                "consistent character design. For dialogue scenes, show the main speaking "
                "character in a clear medium close-up, face large and unobstructed, front-facing "
                "or 3/4 view, visible mouth, eyes and chin, no sunglasses, no text, no watermark. "
                + character_text + " | " + visual
            )
            img=await make_image(prompt,cdir/f"scene_{i}.jpg")

            dialogue=scene.get("dialogue","").strip()
            if dialogue:
                audio=await make_voice(dialogue,cdir/f"voice_{i}.mp3",language)
                clip=cdir/f"talk_{i}.mp4"
                try:
                    await p(f"👄 Lip-sync • Chapter {ch} • Scene {i}/{len(scenes)}")
                    await make_lipsync(img,audio,clip)
                    final_clips.append(clip)
                except Exception:
                    # Don't silently create a fake lip-sync clip. Tell the user exactly why.
                    raise
            else:
                # Narration-only scenes use a short image clip.
                clip=cdir/f"scene_{i}.mp4"
                import subprocess
                subprocess.run([
                    "ffmpeg","-y","-loop","1","-i",str(img),
                    "-t",str(scene.get("duration",6)),
                    "-vf","scale=1920:1080:force_original_aspect_ratio=decrease,"
                          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-c:v","libx264","-preset","veryfast","-r","30",
                    "-an",str(clip)
                ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                final_clips.append(clip)

        await p("🎞️ Joining all chapters into the final YouTube video…")
        output=work/(story.get("title","velocity_cartoon").replace(" ","_")[:60]+".mp4")
        render_lipsync_video(final_clips,output)
        await p("✅ Final YouTube video ready.")
        return str(output),story.get("title","Velocity Cartoon")
    except Exception:
        shutil.rmtree(work,ignore_errors=True)
        raise
