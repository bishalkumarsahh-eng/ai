import urllib.parse, urllib.request, os, urllib.error

async def make_scene_image(prompt, output):
    # Pollinations now requires an API key for generation. Put a key in Heroku as POLLINATIONS_API_KEY.
    key=os.getenv("POLLINATIONS_API_KEY")
    if not key:
        raise RuntimeError("POLLINATIONS_API_KEY is required for image generation. Add your Pollinations API key in Heroku Config Vars.")
    model=os.getenv("IMAGE_MODEL","flux")
    width=os.getenv("IMAGE_WIDTH","1536")
    height=os.getenv("IMAGE_HEIGHT","864")
    q=urllib.parse.quote(prompt)
    url=f"https://gen.pollinations.ai/image/{q}?model={urllib.parse.quote(model)}&width={width}&height={height}&nologo=true"
    req=urllib.request.Request(url,headers={"User-Agent":"Velocity-AI-Cartoon/1.0","Authorization":"Bearer "+key})
    try:
        with urllib.request.urlopen(req,timeout=240) as r:
            output.write_bytes(r.read())
    except urllib.error.HTTPError as e:
        detail=e.read().decode("utf-8","ignore")
        raise RuntimeError(f"Image API error {e.code}: {detail[:500]}")
    return output
