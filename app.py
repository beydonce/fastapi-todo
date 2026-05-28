# app.py
# The main entry point of the FastAPI application.
# Defines all HTTP endpoints (routes) and the request/response logic.

from fastapi import Depends, FastAPI, HTTPException, Path, status
from pydantic import BaseModel, Field
import models
from models import Todos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

app = FastAPI()

# Creates all tables defined in models.py inside the SQLite database file.
# Safe to call every startup — it skips tables that already exist.
models.Base.metadata.create_all(bind=engine)


# --- Database dependency ---

def get_db():
    # Opens a new DB session for each request and closes it when the request is done.
    # Using `yield` makes this a FastAPI dependency that cleans up automatically.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Shorthand type for injecting a DB session into route functions via FastAPI's DI system.
db_dependency = Annotated[Session, Depends(get_db)]


# --- Request schema ---

class TodoRequest(BaseModel):
    # Pydantic model that validates the JSON body sent by the client.
    # FastAPI rejects requests that don't match these rules before they reach the route logic.
    title: str = Field(min_length=3)                    # at least 3 characters
    description: str = Field(min_length=3, max_length=100)  # 3–100 characters
    priority: int = Field(gt=0, lt=6)                   # integer between 1 and 5 (exclusive bounds)
    complete: bool                                       # true or false, no default


# --- Routes ---

@app.get('/')
async def get_all(db: db_dependency):
    # Returns every todo item in the database as a JSON list.
    return db.query(Todos).all()


@app.get('/todos/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    # Returns a single todo by its ID. todo_id must be a positive integer.
    # Raises 404 if no todo with that ID exists.
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="the todo was not found")


@app.post('/todos/create_todo', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo: TodoRequest):
    # Creates a new todo row from the validated request body and saves it to the DB.
    # model_dump() converts the Pydantic object into a plain dict that Todos(**...) can unpack.
    todo_model = Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()


@app.put('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, updated_todo: TodoRequest, todo_id: int = Path(gt=0)):
    # Replaces every field of an existing todo with the values from the request body.
    # Raises 404 if the todo doesn't exist.
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
    # Deletes the todo with the given ID from the database.
    # Raises 404 if no matching todo is found.
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo was not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()


print("hello world")
