import json

from starlette import status

from fastapi.responses import StreamingResponse
from fastapi import APIRouter, FastAPI, Depends, HTTPException, UploadFile, File


import chat_crud
from auth import get_current_user
from open_api_client_for_stream import stream_openai_response
from schemas import ChatUpdate
from openai_client import ask_openai_for_response

router = APIRouter(
    prefix="",
    tags=["Chat"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Chat API does not exists"}},
)




@router.post("/chats")
async def create_chat(payload: dict, user=Depends(get_current_user)):
    chat = await chat_crud.create_chat(user["id"], payload.get("title") or "New chat")
    return chat

@router.get("/chats")
async def list_chats(user=Depends(get_current_user)):
    return await chat_crud.list_chats(user["id"])

@router.get("/chats/{chat_id}")
async def get_chat(chat_id: int, user=Depends(get_current_user)):
    chat = await chat_crud.get_chat(user["id"], chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Not found")
    return chat

@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: int, user=Depends(get_current_user)):
    await chat_crud.delete_chat(user["id"], chat_id)
    return {"ok": True}

@router.post("/chats/{chat_id}/messages")
async def post_message(chat_id: int, payload: dict, user=Depends(get_current_user)):
    message = await chat_crud.add_message(user["id"], chat_id, payload.get("role","user"), payload.get("content",""))
    if payload.get("role","user") == "user" and payload.get("content",""):
        assistant = await ask_openai_for_response(chat_id, user["id"], payload.get("content",""))
        await chat_crud.add_message(user["id"], chat_id, "assistant", assistant)
        return {"assistant": assistant, "message": message}
    return message







@router.post("/chats/{chat_id}/messages/stream")

async def post_message_stream(chat_id: int, payload: dict, user=Depends(get_current_user)):
    await chat_crud.add_message(user["id"], chat_id, payload.get("role", "user"), payload.get("content", ""))

    if payload.get("role") != "user" or not payload.get("content"):
        return {"error": "Invalid request"}

    async def event_generator():
        try:
            async for chunk in stream_openai_response(chat_id, user["id"], payload["content"]):
                yield chunk
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")








@router.get("/chats/{chat_id}/messages")
async def get_messages(chat_id: int, user=Depends(get_current_user)):
    return await chat_crud.get_messages(user["id"], chat_id)



@router.put("/chats/{chat_id}")
async def update_chat(chat_id: int, update: ChatUpdate, user=Depends(get_current_user)):
    try:
        chat = await chat_crud.rename_chat(user["id"], chat_id, update.title)
        return chat
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))




# ------------------ FILES ------------------ #
@router.post("/chats/{chat_id}/files")
async def upload_file(
    chat_id: int,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    contents = await file.read()
    saved = await chat_crud.save_file(user["id"], chat_id, file.filename, contents)
    return {"message": "File uploaded successfully", "file": saved}


@router.get("/chats/{chat_id}/files")
async def get_files(chat_id: int, user=Depends(get_current_user)):
    return await chat_crud.list_files(chat_id, user["id"])

