from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.authService import AuthService
from ...models.dto.userDTO import TokenResponseDTO, UserCreateDTO
from ...models.dao.userDAO import UserDAO


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user_data: UserCreateDTO, db: Session = Depends(get_db)):
    existing_user = UserDAO.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    created_user = UserDAO.create_user(db, user_data)
    return {"message": "User registered successfully", "user_id": created_user.id}



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
