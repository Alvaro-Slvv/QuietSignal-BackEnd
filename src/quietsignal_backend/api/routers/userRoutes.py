from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...models.dto.userDTO import UserCreateDTO, UserOutDTO
from ...services.userService import UserService
from ...database import get_db
from ...api.deps import get_current_user
from ...common.apiResponse import APIResponse

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=APIResponse)
def create_user(user_in: UserCreateDTO, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(db, user_in)
        return APIResponse.success(
            data=UserOutDTO.model_validate(user),
            message="User created",
            code=201,
        )
    except Exception as e:
        logger.exception("User creation failed")
        return APIResponse.error(
            message="User creation failed",
            code=500,
        )


@router.get("/me", response_model=APIResponse)
def me(user=Depends(get_current_user)):
    return APIResponse.success(
        message="Fetched user",
        data=UserOutDTO.model_validate(user),
    )
