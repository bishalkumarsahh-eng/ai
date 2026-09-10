import os, json, urllib.parse, urllib.request

def _get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent":"Velocity-AI-Cartoon/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

async def make_story(prompt):
    # Free-mode default: Pollinations text endpoint.
    # Optional LLM_API_URL can be used for another OpenAI-compatible provider.
    endpoint = os.getenv("LLM_API_URL")
    if endpoint:
        body = json.dumps({
            "model": os.getenv("LLM_MODEL","openai"),
            "messages":[{"role":"user","content":
                "Create exactly 6 cinematic cartoon scenes for this idea: "+prompt+
                ". Return ONLY JSON: {\"title\":\"...\",\"scenes\":[{\"visual\":\"...\",\"dialogue\":\"...\",\"duration\":6}]}"}]
        }).encode()
        req=urllib.request.Request(endpoint,data=body,headers={
            "Content-Type":"application/json",
            "Authorization":"Bearer "+os.getenv("LLM_API_KEY","")
        })
        with urllib.request.urlopen(req,timeout=180) as r:
            data=json.loads(r.read())
        text=data["choices"][0]["message"]["content"]
    else:
        q = urllib.parse.quote(
            "Create exactly 6 cinematic cartoon scenes for this story idea: "+prompt+
            ". Return ONLY valid JSON with title and scenes. Each scene needs visual, dialogue, duration. duration must be 6."
        )
        text = _get("https://text.pollinations.ai/"+q).decode("utf-8")

    text=text.strip().replace("```json","").replace("```","").strip()
    try:
        return json.loads(text)
    except Exception:
        # Reliable fallback if a free text endpoint returns malformed JSON.
        return {"title":"Velocity Cartoon","scenes":[
            {"visual":f"stylized cinematic 3D cartoon, wide shot, {prompt}","dialogue":"It all began on a beautiful day.","duration":6},
            {"visual":f"stylized cinematic 3D cartoon, expressive characters, {prompt}","dialogue":"Neither of them knew what was coming.","duration":6},
            {"visual":f"stylized cinematic 3D cartoon, emotional close-up, {prompt}","dialogue":"One small moment changed everything.","duration":6},
            {"visual":f"stylized cinematic 3D cartoon, dramatic lighting, {prompt}","dialogue":"They decided to face the challenge together.","duration":6},
            {"visual":f"stylized cinematic 3D cartoon, dynamic camera, {prompt}","dialogue":"Their courage opened a new path.","duration":6},
            {"visual":f"stylized cinematic 3D cartoon, spectacular happy ending, {prompt}","dialogue":"And their story had only just begun.","duration":6}
        ]}
