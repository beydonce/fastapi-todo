from fastapi import Depends, FastAPI, HTTPException, Path, status
from pydantic import BaseModel, Field
import models
from models import Todos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get('/')
async def get_all(db: db_dependency):
    return db.query(Todos).all()


@app.get('/todos/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="the todo was not found")


@app.post('/todos/create_todo', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo: TodoRequest):
    todo_model = Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()


@app.put('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, updated_todo: TodoRequest, todo_id: int = Path(gt=0)):
    current_todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if current_todo is None:
        raise HTTPException(status_code=404, detail="todo was not found")
    current_todo.title = updated_todo.title
    current_todo.description = updated_todo.description
    current_todo.priority = updated_todo.priority
    current_todo.complete = updated_todo.complete

    db.commit()


@app.delete('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(ge=1)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo was not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()