from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.journalService import JournalService
from ...services.authService import AuthService
from ...models.dto.userDTO import (
    UserCreateDTO,
    UserOutDTO,
    LoginRequestDTO,
)
from ..deps import get_current_user_or_none
from ...common.apiResponse import APIResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=APIResponse)
def register(user_data: UserCreateDTO, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, user_data)

        JournalService.create_journal(
            db=db,
            user_id=user.id,
            title=f"{user.username} Journal"
        )

        return APIResponse.success(
            data=UserOutDTO.model_validate(user),
            message="User registered successfully",
            code=201,
        )

    except HTTPException as e:
        return APIResponse.error(
            message=e.detail,
            code=e.status_code,
        )

@router.post("/login", response_model=APIResponse)
def login(response: Response, login_data: LoginRequestDTO, db: Session = Depends(get_db)):
    try:
        result = AuthService.authenticate(db, login_data.username, login_data.password)

        if not result:
            return APIResponse.error(
                message="Incorrect username or password",
                code=401,
            )

        token, user = result

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24,
        )

        return APIResponse.success(
            message="Login successful",
            data={
                "access_token": token,
                "user": UserOutDTO.model_validate(user),
            },
        )

    except Exception as e:
        return APIResponse.error(
            message=f"Login error: {str(e)}",
            code=500,
        )


@router.post("/logout", response_model=APIResponse)
def logout(response: Response):
    response.delete_cookie("access_token")
    return APIResponse.success(message="Logged out")


@router.get("/me", response_model=APIResponse)
def me(user=Depends(get_current_user_or_none)):
    if not user:
        return APIResponse.error(
            message="Not authenticated",
            code=401,
        )

    return APIResponse.success(
        message="Fetched user",
        data=UserOutDTO.model_validate(user),
    )
