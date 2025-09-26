import os, json, httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from utils import save_lead, to_agent_json, sanitize_user_text, write_to_sheet

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY","")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL","gpt-4o-mini")
SYSTEM_PROMPT_PATH = os.environ.get("SYSTEM_PROMPT_PATH","prompts/system_es.txt")

with open(SYSTEM_PROMPT_PATH,"r",encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

app = FastAPI(title="Agente Astrolaboral")

SESSIONS = {}
def append_history(session_id, role, content):
    SESSIONS.setdefault(session_id, [])
    SESSIONS[session_id].append({"role": role, "content": content})
    if len(SESSIONS[session_id]) > 20:
        SESSIONS[session_id] = SESSIONS[session_id][-20:]

async def chat_complete(messages):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type":"application/json"}
    payload = {"model": OPENAI_MODEL, "messages": messages, "temperature": 0.2}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

@app.post("/chat")
async def chat(payload: dict):
    session_id = payload.get("session_id","default")
    user_text = sanitize_user_text(payload.get("message",""))

    history = SESSIONS.get(session_id, [])
    messages = [{"role":"system","content": SYSTEM_PROMPT}] + history + [{"role":"user","content": user_text}]

    raw = await chat_complete(messages)

    try:
        agent_json = json.loads(raw)
    except Exception:
        agent_json = to_agent_json(raw, None, [])

    if agent_json.get("lead_update"):
        lead = agent_json["lead_update"]
        saved = write_to_sheet(lead, notes=user_text)
        if not saved:
            save_lead(lead, notes=user_text)

    append_history(session_id, "user", user_text)
    append_history(session_id, "assistant", json.dumps(agent_json, ensure_ascii=False))

    return JSONResponse(agent_json)

@app.post("/twilio")
async def twilio_webhook(request: Request):
    form = await request.form()
    body = form.get("Body","")
    from_num = form.get("From","")
    session_id = from_num.replace(":","_")
    resp = await chat({"session_id": session_id, "message": body})
    content = await resp.body()
    data = json.loads(content)
    return PlainTextResponse(data.get("message",""))

@app.get("/widget")
async def widget():
    with open("static/widget.html","r",encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(html)

@app.get("/healthz")
async def healthz():
    return PlainTextResponse("ok")
