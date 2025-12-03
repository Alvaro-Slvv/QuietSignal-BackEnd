from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...models.dto.userDTO import UserCreateDTO, UserOutDTO
from ...services.userService import UserService
from ...database import get_db
from ...api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOutDTO)
def create_user(user_in: UserCreateDTO, db: Session = Depends(get_db)):
    return UserService.create_user(db, user_in)


@router.get("/me", response_model=UserOutDTO)
def me(user=Depends(get_current_user)): # if admin admin_user = Depends(require_role("admin"))
    return UserOutDTO.model_validate(user)
