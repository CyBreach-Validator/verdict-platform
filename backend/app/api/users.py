from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.security.security import get_current_user

# B11: this router had no authentication at all, so `POST /users` let an
# anonymous caller create accounts and `GET /users` enumerated every user in
# the platform. The guard is declared on the router rather than repeated on
# each handler: every route here needs it, and a per-route `Depends` is exactly
# what was forgotten the last time this router was extended.
#
# Requiring auth on `POST /users` does not lock out the first user: tokens come
# from `/auth/login`, which authenticates against ADMIN_USERNAME/ADMIN_PASSWORD
# from the environment and is independent of this table.
router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "id": new_user.id
    }


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user