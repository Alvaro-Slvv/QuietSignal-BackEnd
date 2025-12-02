from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...models.dto.userDTO import UserCreateDTO, TokenResponseDTO
from ...models.dao.userDAO import UserDAO
from ...services.authService import AuthService
from ...database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponseDTO, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreateDTO, db: Session = Depends(get_db)):
    try:
        token, user = AuthService.register_user(db, user_in.name, user_in.username, user_in.password, user_in.email)
        return TokenResponseDTO(access_token=token)
    except ValueError as e:
        if str(e) == "username_taken":
            raise HTTPException(status_code=400, detail="Username already registered")
        raise HTTPException(status_code=400, detail="Registration error")


@router.post("/login", response_model=TokenResponseDTO)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    res = AuthService.authenticate(db, form_data.username, form_data.password)
    if not res:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token, user = res
    return TokenResponseDTO(access_token=token)
