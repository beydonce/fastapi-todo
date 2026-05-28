# models.py
# Defines the database tables as Python classes (ORM models).
# Each class = one table, each class attribute = one column.

from sqlalchemy import Column, Integer, Boolean, String
from database import Base  # all models must inherit from Base so SQLAlchemy can track them


class Todos(Base):
    # The actual table name in the SQLite database file
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)  # auto-incrementing unique ID
    title = Column(String)        # short name for the todo item
    description = Column(String)  # longer details about the todo item
    priority = Column(Integer)    # importance level (1–5 in this app)
    complete = Column(Boolean, default=False)  # whether the todo is done; starts as False
