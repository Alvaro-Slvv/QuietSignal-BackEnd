from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.authService import AuthService
from ...models.dto.userDTO import TokenResponseDTO, UserCreateDTO, UserOutDTO
from ...models.dao.userDAO import UserDAO
from ...utils.security import hash_password 


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOutDTO)
def register(
    user_data: UserCreateDTO, 
    db: Session = Depends(get_db)
):
    if UserDAO.get_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if UserDAO.get_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user_data.password)          
    created_user = UserDAO.create(db, dto=user_data, hashed_password=hashed_pw)
    return created_user


@router.post("/login", response_model=TokenResponseDTO)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    result = AuthService.authenticate(db, form_data.username, form_data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token, user = result

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,   # True in production HTTPS
        samesite="lax",
        max_age=3600,
        path="/",
    )

    return TokenResponseDTO(access_token=token)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
