from fastapi import Depends, HTTPException, APIRouter

from starlette import status

from auth import create_access_token, get_current_user, authenticate_user
import user_crud
from fastapi.security import OAuth2PasswordRequestForm

from schemas import RegisterIn

router = APIRouter(
    prefix="",
    tags=["User"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "User API does not exists"}},
)


@router.post("/register")
async def register(payload: RegisterIn):
    exists = await user_crud.get_user_by_email(payload.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await user_crud.create_user(payload.email, payload.password, payload.name)
    return {"id": user["id"], "email": user["email"]}


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["id"]) })
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"], "name": user.get("name")}
