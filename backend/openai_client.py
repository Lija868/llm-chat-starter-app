import os, httpx
from chat_crud import list_files  # <-- make sure you import this
OPENAI_KEY = os.getenv('OPENAI_API_KEY')


async def ask_openai_stream(chat_id, user_id, prompt: str):

    # Similar to your ask_openai_for_response but streaming
    files = await list_files(chat_id, user_id)
    context_text = ""
    for f in files:
        try:
            with open(f["path"], "r", encoding="utf-8", errors="ignore") as fp:
                context_text += f"\n\n--- File: {f['filename']} ---\n"
                context_text += fp.read()[:5000]
        except Exception as e:
            context_text += f"\n\n[Could not read file {f['filename']}]\n"

    full_prompt = f"""
You are an assistant helping the user answer questions.

User's message:
{prompt}

Attached file context:
{context_text if context_text else '[No files uploaded for this chat]'}
"""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

    data = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": full_prompt},
        ],
        "stream": True  # ask Gemini API to stream results
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", BASE_URL, headers=headers, json=data) as response:
            async for chunk in response.aiter_text():
                yield chunk


if not OPENAI_KEY:
    async def ask_openai_for_response(chat_id, user_id, prompt: str):
        return "OPENAI_API_KEY not configured. Set OPENAI_API_KEY to enable assistant responses."
else:
    async def ask_openai_for_response(chat_id, user_id, prompt: str):
        # ---- Gather uploaded file content for context ----
        files = await list_files(chat_id, user_id)
        context_text = ""
        for f in files:
            try:
                with open(f["path"], "r", encoding="utf-8", errors="ignore") as fp:
                    context_text += f"\n\n--- File: {f['filename']} ---\n"
                    context_text += fp.read()[:5000]  # limit to avoid token overflow
            except Exception as e:
                context_text += f"\n\n[Could not read file {f['filename']}]\n"

        # ---- Construct prompt ----
        full_prompt = f"""
You are an assistant helping the user answer questions.

User's message:
{prompt}

Attached file context:
{context_text if context_text else '[No files uploaded for this chat]'}
"""

        BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

        data = {
            "model": "gemini-2.5-flash",
            "messages": [
                {"role": "user", "content": full_prompt},
            ],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(BASE_URL, headers=headers, json=data)
            if r.status_code != 200:
                return f"Gemini error: {r.status_code} {r.text}"
            j = r.json()
            return j["choices"][0]["message"]["content"]
