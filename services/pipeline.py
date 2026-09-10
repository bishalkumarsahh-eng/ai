import pathlib, tempfile, subprocess, os, shutil
from .story import make_story
from .images import make_scene_image
from .voice import make_voice
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

async def create_video(prompt, progress=None):
    async def p(s):
        if progress: await progress(s)
    work=pathlib.Path(tempfile.mkdtemp(prefix="velocity_cartoon_"))
    try:
        await p("🧠 Writing story + scene plan…")
        story=await make_story(prompt)
        scenes=story.get("scenes",[])[:8]
        if not scenes: raise RuntimeError("No scenes were generated.")
        clips=[]
        for i,scene in enumerate(scenes,1):
            await p(f"🎨 Generating cartoon scene {i}/{len(scenes)}…")
            img=await make_scene_image(scene["visual"],work/f"scene_{i}.jpg")
            await p(f"🗣️ Creating voice {i}/{len(scenes)}…")
            audio=await make_voice(scene["dialogue"],work/f"voice_{i}.mp3")
            clip=work/f"clip_{i}.mp4"; duration=float(scene.get("duration",6))
            vf=("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
                "zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                "d=180:s=1920x1080:fps=30,format=yuv420p")
            cmd=[FFMPEG,"-y","-loop","1","-i",str(img),"-i",str(audio),"-t",str(duration),"-vf",vf,
                 "-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","192k","-shortest",str(clip)]
            r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            if r.returncode:
                raise RuntimeError("FFmpeg scene render failed: " + r.stderr[-1000:])
            clips.append(clip)
        await p("🎞️ Joining scenes + optimizing YouTube output…")
        concat=work/"concat.txt"; concat.write_text("\n".join("file '"+str(c)+"'" for c in clips))
        output=work/"velocity_cartoon_1080p.mp4"
        r=subprocess.run([FFMPEG,"-y","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(output)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if r.returncode: raise RuntimeError("FFmpeg join failed: "+r.stderr[-1000:])
        await p("✅ Video ready — sending it to Telegram…")
        return str(output)
    except Exception:
        shutil.rmtree(work,ignore_errors=True); raise
