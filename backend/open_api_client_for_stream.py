import os
import json
import httpx

import chat_crud
from chat_crud import list_files

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

async def stream_openai_response(chat_id, user_id, prompt: str):
    if not OPENAI_KEY:
        yield 'data: ' + json.dumps({"error": "OPENAI_API_KEY not configured."}) + "\n\n"
        return

    # Prepare context from uploaded files
    files = await list_files(chat_id, user_id)
    context_text = ""
    for f in files:
        try:
            with open(f["path"], "r", encoding="utf-8", errors="ignore") as fp:
                context_text += f"\n\n--- File: {f['filename']} ---\n"
                context_text += fp.read()[:50]
        except Exception:
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
        "messages": [{"role": "user", "content": full_prompt}],
        "stream": True,
    }


    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", BASE_URL, headers=headers, json=data) as response:
            if response.status_code != 200:
                text = await response.aread()
                yield f"data: {json.dumps({'error': text.decode()})}\n\n"
                return

            assistant_message = ""
            async for line_bytes in response.aiter_lines():
                line = line_bytes.strip()
                if not line:
                    continue
                if line == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                if line.startswith("data: "):
                    line = line[len("data: "):]

                try:
                    chunk = json.loads(line)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        assistant_message += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            if assistant_message:
                await chat_crud.add_message(user_id, chat_id, "assistant", assistant_message)
