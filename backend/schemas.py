from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None

class ChatUpdate(BaseModel):
    title: str