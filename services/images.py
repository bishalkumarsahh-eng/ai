import urllib.parse, urllib.request, os

async def make_scene_image(prompt, output):
    # Free image route. A Pollinations key may be supplied later for higher quotas.
    model=os.getenv("IMAGE_MODEL","flux")
    width=os.getenv("IMAGE_WIDTH","1536")
    height=os.getenv("IMAGE_HEIGHT","864")
    q=urllib.parse.quote(prompt)
    url=f"https://gen.pollinations.ai/image/{q}?model={urllib.parse.quote(model)}&width={width}&height={height}&nologo=true"
    headers={"User-Agent":"Velocity-AI-Cartoon/1.0"}
    key=os.getenv("POLLINATIONS_API_KEY")
    if key:
        headers["Authorization"]="Bearer "+key
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=240) as r:
        output.write_bytes(r.read())
    return output
