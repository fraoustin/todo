from typing import Annotated
import uuid
from fastapi import Depends, APIRouter, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from db import User, verify_password, hash_password
from deps import get_db

from .schemas import UserCreate, UserUpdate, UserOut, UserUpdateMe

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user and verify_password(form_data.password, user.password) is True and not user.disabled:
        return {"access_token": user.token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="User or password invalid")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.token == token).first()
    if not user or user.disabled:
        raise HTTPException(status_code=401, detail="Token invalid")
    return user


async def get_current_admin_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.token == token).first()
    if not user.isadmin or user.disabled:
        raise HTTPException(status_code=401, detail="Token invalid")
    return user


@router.get("/me", response_model=UserOut)
async def me(user: Annotated[dict, Depends(get_current_user)]):
    return user


@router.put("/me", response_model=UserOut)
async def update_current_user(user: Annotated[dict, Depends(get_current_user)], user_update: UserUpdateMe, db: Session = Depends(get_db)):
    filter_key = ['isadmin',]
    if len(db.query(User).filter(User.disabled == False).all()) == 1:
        filter_key.append('disabled')
    for attr, value in user_update.model_dump(exclude_unset=True).items():
        if attr not in filter_key:
            if attr == 'password':
                setattr(user, attr, hash_password(attr))
            else:
                setattr(user, attr, value)

    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserOut])
async def list_users(user: Annotated[dict, Depends(get_current_admin_user)], db: Session = Depends(get_db)):
    return db.query(User).order_by(User.username).all()


@router.post("/user", response_model=UserOut)
async def create_user(user: Annotated[dict, Depends(get_current_admin_user)], user_n: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_n.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already in use")

    new_user = User(
        username=user_n.username,
        email=user_n.email,
        password=hash_password(user_n.password),
        token=str(uuid.uuid4()),
        disabled=user_n.disabled or False,
        isadmin=user_n.isadmin or False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/user/{user_id}", response_model=UserOut)
async def get_user(user: Annotated[dict, Depends(get_current_admin_user)], user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/user/{user_id}", response_model=UserOut)
async def update_user(user: Annotated[dict, Depends(get_current_admin_user)], user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user_to_update = db.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    for attr, value in user_update.model_dump(exclude_unset=True).items():
        if attr == 'password':
            setattr(user_to_update, attr, hash_password(attr))
        else:
            if attr == 'isadmin' and user_to_update.id == user.id:
                pass
            else:
                setattr(user_to_update, attr, value)

    db.commit()
    db.refresh(user_to_update)
    return user_to_update


@router.delete("/user/{user_id}")
async def delete_user(user: Annotated[dict, Depends(get_current_admin_user)], user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted"}
