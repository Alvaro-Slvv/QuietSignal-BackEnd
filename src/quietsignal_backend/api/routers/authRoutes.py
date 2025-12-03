from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.authService import AuthService
from ...models.dto.userDTO import TokenResponseDTO, UserCreateDTO, UserOutDTO, LoginRequestDTO
from ..deps import get_current_user, get_current_user_or_none

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOutDTO)
def register(user_data: UserCreateDTO, db: Session = Depends(get_db)):
    return AuthService.register(db, user_data)


@router.post("/login", response_model=TokenResponseDTO)
def login(response: Response, login_data: LoginRequestDTO, db: Session = Depends(get_db)):
    result = AuthService.authenticate(db, login_data.username, login_data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token, user = result

    # Set cookie - adjust secure=True for HTTPS in prod
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24  # optional
    )
    return TokenResponseDTO(access_token=token)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"msg": "logged out"}

@router.get("/me", response_model=UserOutDTO)
def me(user = Depends(get_current_user_or_none)):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
