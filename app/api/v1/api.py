import os
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from deps import get_db
from api.auth.api import get_current_user
from db import User, Todo

from .schemas import TodoCreate, TodoUpdate, TodoOut


router = APIRouter()


@router.get("/version")
async def version():
    return {"version": "1.0.0"}


@router.post("/todo", response_model=TodoOut)
async def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    todo = Todo(**todo_in.model_dump(), who=user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.get("/todos", response_model=list[TodoOut])
def get_my_todos(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.who == user.id).all()


@router.get("/todo/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.who == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/todo/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo_in: TodoUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.who == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    for attr, value in todo_in.model_dump(exclude_unset=True).items():
        setattr(todo, attr, value)

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/todo/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.who == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()
    return
