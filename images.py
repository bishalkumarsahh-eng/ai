import os, urllib.parse, urllib.request

async def make_image(prompt, outfile):
    key = os.getenv("POLLINATIONS_API_KEY")
    if not key:
        raise RuntimeError("POLLINATIONS_API_KEY is missing.")
    model = os.getenv("IMAGE_MODEL", "flux")
    url = (
        "https://gen.pollinations.ai/image/"
        + urllib.parse.quote(prompt, safe="")
        + f"?model={urllib.parse.quote(model)}&width=1536&height=864&nologo=true"
    )
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + key,
        "User-Agent": "Velocity-Cartoon/3.0"
    })
    with urllib.request.urlopen(req, timeout=240) as r:
        outfile.write_bytes(r.read())
    return outfile
