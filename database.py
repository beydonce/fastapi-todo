# database.py
# Responsible for setting up the database connection and providing the tools
# that the rest of the app uses to talk to that database.

from sqlalchemy import create_engine        # creates the connection to the DB file
from sqlalchemy.orm import sessionmaker     # factory for creating DB sessions (units of work)
from sqlalchemy.ext.declarative import declarative_base  # base class for all ORM models

# Path to the SQLite database file. The file will be created automatically
# in the project root the first time the app runs.
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todoapp.db'

# The engine is the low-level connection pool to the database.
# check_same_thread=False is required for SQLite when used with FastAPI,
# because FastAPI handles requests on multiple threads and SQLite would
# otherwise block cross-thread access.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# SessionLocal is a factory: calling SessionLocal() returns a new DB session.
# autocommit=False  → changes are not saved until you explicitly call db.commit()
# autoflush=False   → pending changes are not pushed to the DB automatically before a query
# bind=engine       → ties every session to our database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all ORM models (e.g. Todos in models.py).
# When SQLAlchemy sees a class that inherits from Base it knows it maps to a DB table.
# Calling Base.metadata.create_all(engine) creates all those tables in the database.
Base = declarative_base()
