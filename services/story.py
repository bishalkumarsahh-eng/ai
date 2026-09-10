import os, json, re, urllib.request, urllib.error


def gemini(prompt):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is missing.")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.75,
            "responseMimeType": "application/json",
            "maxOutputTokens": 8192,
        },
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("Gemini returned no usable text response.")


def parse_json_response(text):
    if isinstance(text, (dict, list)):
        return text
    text = text.strip().lstrip("\ufeff")
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for start, ch in enumerate(text):
        if ch not in "{[":
            continue
        try:
            obj, _ = decoder.raw_decode(text[start:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    try:
        import ast
        obj = ast.literal_eval(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    preview = text[:1200].replace("\n", " ")
    raise RuntimeError("Story AI returned invalid or truncated JSON. Response begins: " + preview)


async def make_story(idea, language, minutes):
    """Build a compact story bible first, then generate scenes chapter-by-chapter.
    This prevents long-video requests from producing one huge/truncated JSON response.
    """
    lang = "natural Romanized Hindi + English (Hinglish), Latin script" if language == "hinglish" else "natural conversational English"
    chapter_count = max(6, min(10, (minutes + 2) // 3))
    target_scenes = max(30, minutes * 10)
    base = target_scenes // chapter_count
    extra = target_scenes % chapter_count

    plan_prompt = f"""
Create a story bible for a long animated cartoon YouTube video.
Idea: {idea}
Language: {lang}
Duration: {minutes} minutes.
Create exactly {chapter_count} chapters.
Do NOT create scenes yet.
Return ONLY valid JSON with this exact shape:
{{
  "title":"...",
  "characters":[{{"id":"char1","name":"...","description":"stable visual description"}}],
  "chapters":[{{"chapter":1,"title":"...","summary":"..."}}]
}}
Keep character ages appropriate for the story and keep appearances stable.
"""
    bible = parse_json_response(gemini(plan_prompt))
    if not bible.get("characters") or not bible.get("chapters"):
        raise RuntimeError("Story AI returned an incomplete story bible.")

    character_text = "; ".join(f'{c["name"]}: {c["description"]}' for c in bible["characters"])
    all_scenes = []
    chapters = bible["chapters"][:chapter_count]
    for idx, ch in enumerate(chapters):
        count = base + (1 if idx < extra else 0)
        chapter_prompt = f"""
Create ONLY the scenes for chapter {ch.get('chapter', idx+1)} of this animated cartoon.
Story title: {bible.get('title','Untitled')}
Chapter title: {ch.get('title','')}
Chapter summary: {ch.get('summary','')}
Language: {lang}
Create exactly {count} scenes. Each scene should be 5-7 seconds.
Characters (NEVER change their appearance): {character_text}
Return ONLY valid JSON:
{{"scenes":[{{"chapter":{ch.get('chapter',idx+1)},"visual":"...","speaker":"char1 or null","dialogue":"...","duration":6}}]}}
For speaking scenes, make the speaker explicit and keep dialogue short enough for 5-7 seconds.
Use narration only when needed. Make the chapter cinematic and continue naturally from the previous chapter.
"""
        chapter_obj = parse_json_response(gemini(chapter_prompt))
        scenes = chapter_obj.get("scenes") if isinstance(chapter_obj, dict) else None
        if not isinstance(scenes, list) or not scenes:
            raise RuntimeError(f"Story AI returned no scenes for chapter {idx+1}.")
        all_scenes.extend(scenes[:count])

    bible["scenes"] = all_scenes
    return bible
