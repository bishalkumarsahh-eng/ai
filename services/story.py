import os, json, re, urllib.request, urllib.error, asyncio


def gemini(prompt):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is missing.")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.55,"responseMimeType":"application/json","maxOutputTokens":8192}}
    req = urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r: data=json.loads(r.read())
    try: return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError,IndexError): raise RuntimeError("Gemini returned no usable text response.")


def parse_json_response(text):
    if isinstance(text,(dict,list)): return text
    text=text.strip().lstrip("\ufeff")
    text=re.sub(r"^```(?:json)?\s*","",text,flags=re.I); text=re.sub(r"\s*```$","",text)
    try: return json.loads(text)
    except json.JSONDecodeError: pass
    decoder=json.JSONDecoder()
    for start,ch in enumerate(text):
        if ch not in "{[": continue
        try:
            obj,_=decoder.raw_decode(text[start:]); return obj
        except json.JSONDecodeError: continue
    try:
        import ast; return ast.literal_eval(text)
    except Exception: pass
    raise RuntimeError("Story AI returned invalid or truncated JSON. Response begins: "+text[:1200].replace("\n"," "))


def extract_scenes(obj):
    """Accept minor schema variations returned by the model."""
    if isinstance(obj,dict):
        for key in ("scenes","scene_list","story_scenes","items"):
            value=obj.get(key)
            if isinstance(value,list) and value: return value
        # Sometimes the model wraps the chapter inside another object.
        for value in obj.values():
            found=extract_scenes(value)
            if found: return found
    elif isinstance(obj,list) and obj and all(isinstance(x,dict) for x in obj):
        if any("visual" in x or "dialogue" in x for x in obj): return obj
    return []


async def make_story(idea,language,minutes):
    lang="natural Romanized Hindi + English (Hinglish), Latin script" if language=="hinglish" else "natural conversational English"
    chapter_count=max(4,min(10,(minutes+2)//3)); target=max(24,minutes*8)
    base,extra=divmod(target,chapter_count)
    plan=f'''Create a story bible for an animated cartoon YouTube video. Idea: {idea}\nLanguage: {lang}\nDuration: {minutes} minutes.\nCreate exactly {chapter_count} chapters. Return ONLY JSON with title, characters, chapters. Each chapter must have chapter, title, summary.'''
    bible=parse_json_response(gemini(plan))
    if not bible.get("characters") or not bible.get("chapters"): raise RuntimeError("Story AI returned an incomplete story bible.")
    character_text="; ".join(f'{c.get("name","Character")}: {c.get("description","")}' for c in bible["characters"])
    all_scenes=[]
    chapters=bible["chapters"][:chapter_count]
    for idx,ch in enumerate(chapters):
        count=base+(1 if idx<extra else 0); chapter_no=idx+1
        prompt=f'''Create exactly {count} short scenes for chapter {chapter_no}. Return ONLY one JSON object: {{"scenes":[{{"chapter":{chapter_no},"visual":"...","speaker":"character id or null","dialogue":"short dialogue or narration","duration":6}}]}}. Never return an empty scenes array.\nTitle: {bible.get("title","Untitled")}\nChapter: {ch.get("title","")}\nSummary: {ch.get("summary","")}\nLanguage: {lang}\nCharacters: {character_text}\nEvery scene MUST contain visual, speaker, dialogue and duration. Keep dialogue short for 5-7 seconds. Continue from earlier chapters.'''
        scenes=[]
        last_error=None
        for attempt in range(3):
            try:
                obj=parse_json_response(gemini(prompt)); scenes=extract_scenes(obj)
                scenes=[s for s in scenes if isinstance(s,dict) and s.get("visual")]
                if scenes: break
            except Exception as e: last_error=e
            await asyncio.sleep(1.5*(attempt+1))
        if not scenes:
            raise RuntimeError(f"Story AI failed to create scenes for chapter {chapter_no} after 3 attempts. {last_error or 'Empty scenes response.'}")
        for s in scenes[:count]:
            s["chapter"]=chapter_no
            s["duration"]=float(s.get("duration",6) or 6)
            s["dialogue"]=str(s.get("dialogue","") or "").strip()
            s["speaker"]=s.get("speaker")
        all_scenes.extend(scenes[:count])
    if not all_scenes: raise RuntimeError("Story AI created no scenes.")
    bible["scenes"]=all_scenes
    return bible
