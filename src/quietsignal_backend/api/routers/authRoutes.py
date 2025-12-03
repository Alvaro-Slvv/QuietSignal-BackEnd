from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.authService import AuthService
from ...models.dto.userDTO import (
    TokenResponseDTO,
    UserCreateDTO,
    UserOutDTO,
    LoginRequestDTO,
)
from ..deps import get_current_user_or_none

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user_data: UserCreateDTO, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, user_data)
        return {
            "success": True,
            "status_code": 201,
            "message": "User registered successfully",
            "data": UserOutDTO.model_validate(user),
        }
    except HTTPException as e:
        return {
            "success": False,
            "status_code": e.status_code,
            "message": "Registration failed",
            "errors": e.detail,
        }


@router.post("/login")
def login(response: Response, login_data: LoginRequestDTO, db: Session = Depends(get_db)):
    try:
        result = AuthService.authenticate(db, login_data.username, login_data.password)

        if not result:
            return {
                "success": False,
                "status_code": 401,
                "message": "Incorrect username or password",
                "errors": "Invalid credentials",
            }

        token, user = result

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24,
        )

        return {
            "success": True,
            "status_code": 200,
            "message": "Login successful",
            "data": {
                "access_token": token,
                "user": UserOutDTO.model_validate(user),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "message": "Login error",
            "errors": str(e),
        }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {
        "success": True,
        "status_code": 200,
        "message": "Logged out",
    }


@router.get("/me")
def me(user=Depends(get_current_user_or_none)):
    if not user:
        return {
            "success": False,
            "status_code": 401,
            "message": "Not authenticated",
            "data": None,
        }

    return {
        "success": True,
        "status_code": 200,
        "message": "Fetched user",
        "data": UserOutDTO.model_validate(user),
    }
