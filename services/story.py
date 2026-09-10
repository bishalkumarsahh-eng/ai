import os,json,urllib.request,urllib.error

def gemini(prompt):
    key=os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is missing.")
    model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite")
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body={"contents":[{"parts":[{"text":prompt}]}],
          "generationConfig":{"temperature":0.8,"responseMimeType":"application/json"}}
    req=urllib.request.Request(url,data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r:
        data=json.loads(r.read())
    return data["candidates"][0]["content"]["parts"][0]["text"]

async def make_story(idea,language,minutes):
    target_scenes=max(30,minutes*10)
    lang_instruction=("natural Romanized Hindi + English (Hinglish), written in Latin script"
                       if language=="hinglish" else "natural conversational English")
    prompt=f"""
Create a long animated cartoon YouTube story from this idea:
{idea}

Language: {lang_instruction}
Target duration: {minutes} minutes.
Create {target_scenes} short scenes. Each scene is about 5-7 seconds of screen time.
Keep the same characters and locations consistent throughout the entire story.

Return ONLY valid JSON:
{{
 "title":"...",
 "characters":[
   {{"id":"char1","name":"...","description":"stable visual description"}}
 ],
 "scenes":[
   {{
     "chapter":1,
     "visual":"detailed cartoon visual prompt, include character names",
     "speaker":"char1 or null",
     "dialogue":"short dialogue or narration",
     "duration":6
   }}
 ]
}}

The story should have 6-10 chapters, escalating conflict and a satisfying ending.
Do not change character appearance between scenes.
"""
    text=gemini(prompt)
    return json.loads(text)
