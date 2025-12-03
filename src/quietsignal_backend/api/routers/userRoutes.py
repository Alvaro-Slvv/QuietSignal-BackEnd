from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...models.dto.userDTO import UserCreateDTO, UserOutDTO
from ...services.userService import UserService
from ...database import get_db
from ...api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(user_in: UserCreateDTO, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(db, user_in)
        return {
            "success": True,
            "status_code": 201,
            "message": "User created",
            "data": UserOutDTO.model_validate(user),
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "message": "User creation failed",
            "errors": str(e),
        }


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "success": True,
        "status_code": 200,
        "message": "Fetched user",
        "data": UserOutDTO.model_validate(user),
    }
