import os

from fastapi import HTTPException
from sqlalchemy import select, insert

from database import database
from models import chats, messages, files

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def create_chat(user_id: int, title: str):
    query = chats.insert().values(user_id=user_id, title=title)
    chat_id = await database.execute(query)
    return {"id": chat_id, "user_id": user_id, "title": title}

async def list_chats(user_id: int):
    query = chats.select().where(chats.c.user_id == user_id).order_by(chats.c.created_at.desc())
    return await database.fetch_all(query)

async def get_chat(user_id: int, chat_id: int):
    query = chats.select().where(chats.c.user_id == user_id).where(chats.c.id == chat_id)
    return await database.fetch_one(query)

async def delete_chat(user_id: int, chat_id: int):
    query = chats.delete().where(chats.c.user_id == user_id).where(chats.c.id == chat_id)
    await database.execute(query)

async def add_message(user_id: int, chat_id: int, role: str, content: str):
    c = await get_chat(user_id, chat_id)
    if not c:
        raise Exception("Chat not found or unauthorized")
    query = messages.insert().values(chat_id=chat_id, role=role, content=content)
    msg_id = await database.execute(query)
    return {"id": msg_id, "chat_id": chat_id, "role": role, "content": content}

async def get_messages(user_id: int, chat_id: int):
    c = await get_chat(user_id, chat_id)
    if not c:
        return []
    query = messages.select().where(messages.c.chat_id == chat_id).order_by(messages.c.created_at.asc())
    return await database.fetch_all(query)

async def rename_chat(user_id: int, chat_id: int, new_title: str):
    # make sure the chat belongs to the user
    c = await get_chat(user_id, chat_id)
    if not c:
        raise Exception("Chat not found or unauthorized")

    query = chats.update().where(
        chats.c.id == chat_id,
        chats.c.user_id == user_id
    ).values(title=new_title)

    await database.execute(query)

    return {"id": chat_id, "user_id": user_id, "title": new_title}


async def save_file(user_id: int, chat_id: int, filename: str, contents: bytes):
    # Ensure chat belongs to this user
    query = select(chats).where(chats.c.id == chat_id, chats.c.user_id == user_id)
    chat = await database.fetch_one(query)
    if not chat:
        raise HTTPException(status_code=403, detail="Unauthorized chat")

    # Save file physically
    file_path = os.path.join(UPLOAD_DIR, f"{chat_id}_{filename}")
    with open(file_path, "wb") as f:
        f.write(contents)

    # Insert into DB
    query = (
        insert(files)
        .values(
            chat_id=chat_id,
            user_id=user_id,
            filename=filename,
            path=file_path,
        )
    )
    file_id = await database.execute(query)

    return {
        "id": file_id,
        "chat_id": chat_id,
        "user_id": user_id,
        "filename": filename,
        "path": file_path,
    }


async def list_files(chat_id: int, user_id: int):
    # Ensure chat belongs to this user
    query = select(chats).where(chats.c.id == chat_id, chats.c.user_id == user_id)
    chat = await database.fetch_one(query)
    if not chat:
        raise HTTPException(status_code=403, detail="Unauthorized chat")

    query = select(files).where(files.c.chat_id == chat_id, files.c.user_id == user_id)
    return await database.fetch_all(query)