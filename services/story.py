import os, json, urllib.request, urllib.error

async def make_story(prompt):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is required. Create a free Gemini API key and add it in Heroku Config Vars.")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    instruction = (
        "Create a cinematic cartoon story from the user's idea. Return ONLY valid JSON, no markdown. "
        "Schema: {\"title\":\"...\",\"scenes\":[{\"visual\":\"...\",\"dialogue\":\"...\",\"duration\":6}]}. "
        "Create exactly 6 scenes. Keep the same main characters visually consistent. "
        "Make visual prompts detailed and suitable for a family-friendly YouTube cartoon. "
        "Keep dialogue short enough for a 6-second scene. User idea: " + prompt
    )
    body = json.dumps({"contents":[{"parts":[{"text":instruction}]}],
                       "generationConfig":{"responseMimeType":"application/json"}}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data=json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail=e.read().decode("utf-8","ignore")
        raise RuntimeError(f"Gemini API error {e.code}: {detail[:500]}")
    text=data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)
