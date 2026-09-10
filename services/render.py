import subprocess, pathlib

def render_lipsync_video(clips, output):
    concat = output.parent / "concat.txt"
    lines = []
    for p in clips:
        safe = str(p).replace("\\", "/").replace("'", "'\\''")
        lines.append("file '" + safe + "'")
    concat.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),
        "-vf","scale=1920:1080:force_original_aspect_ratio=decrease,"
              "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-c:v","libx264","-preset","veryfast","-r","30",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",
        str(output)
    ], check=True)
    return output
