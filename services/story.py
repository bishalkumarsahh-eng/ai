import os, json, urllib.request, urllib.error

PREFERRED = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def _request_json(url, payload=None, headers=None, timeout=180):
    req = urllib.request.Request(url, data=(json.dumps(payload).encode() if payload is not None else None), headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _pick_model(api_key):
    # If the configured model is unavailable, ask Gemini which generateContent models
    # are actually enabled for this key and select a Flash model automatically.
    try:
        data = _request_json(
            "https://generativelanguage.googleapis.com/v1beta/models?key=" + urllib.request.quote(api_key)
        )
        names=[]
        for m in data.get("models",[]):
            methods=m.get("supportedGenerationMethods",[])
            name=m.get("name","")
            if "generateContent" in methods:
                names.append(name.replace("models/", ""))
        if PREFERRED in names:
            return PREFERRED
        for n in names:
            if "flash" in n.lower() and "image" not in n.lower():
                return n
        if names:
            return names[0]
    except Exception:
        pass
    return PREFERRED


async def make_story(prompt):
    key=os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is missing in Heroku Config Vars.")

    model=_pick_model(key)
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.request.quote(model)}:generateContent?key={urllib.request.quote(key)}"
    instruction=(
        "Create a cinematic cartoon story from this idea: " + prompt +
        " Return ONLY valid JSON. Exactly 6 scenes. Format: "
        '{"title":"...","scenes":[{"visual":"...","dialogue":"...","duration":6}]} '
        "Keep visual descriptions detailed, consistent in character appearance, colorful, family-friendly and suitable for YouTube."
    )
    payload={"contents":[{"parts":[{"text":instruction}]}],"generationConfig":{"temperature":0.8,"responseMimeType":"application/json"}}
    try:
        data=_request_json(url,payload,{"Content-Type":"application/json"})
    except urllib.error.HTTPError as e:
        detail=e.read().decode("utf-8","ignore")
        raise RuntimeError(f"Gemini API error {e.code}: {detail[:800]}")
    try:
        text=data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return json.loads(text)
    except Exception as e:
        raise RuntimeError("Gemini returned an invalid story response.") from e
