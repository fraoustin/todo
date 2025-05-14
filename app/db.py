import os
import uuid
from sqlalchemy import Column, Integer, String, Boolean, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.engine import make_url
from config import get_settings
import bcrypt

# Hash a password using bcrypt


def hash_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

# Check if the provided password matches the stored password (hashed)


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


settings = get_settings()

DATABASE_URL = os.environ.get('APP_DATABASE_URL', settings.database_url)


def cleanDb():
    url = make_url(DATABASE_URL)
    if os.path.exists(url.database):
        os.remove(url.database)


if os.environ.get('APP_DATABASE_CLEAN', str(settings.database_clean)).lower() in ('1', 'true', 'yes'):
    cleanDb()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     password = Column(String(255))
#     email = Column(String, unique=True, index=True)
#     token = Column(String, unique=True, index=True)
#     disabled = Column(Boolean, default=False)
#     isadmin = Column(Boolean, default=False)
#     onlyapi = Column(Boolean, default=False)
#     todos = relationship("Todo", back_populates="who", cascade="all, delete-orphan")


# # add for Application
# # /!\ add link in User
# class Todo(Base):
#     __tablename__ = "todos"

#     id = Column(Integer, primary_key=True, index=True)
#     text = Column(String, nullable=False)
#     terminated = Column(Boolean, default=False)
#     who_id = Column(Integer, ForeignKey("users.id"), nullable=False)

#     who = relationship("User", back_populates="todos")

import sys
from pydbml import PyDBML
from dbml_to_sqlalchemy import createModel
from pathlib import Path

try:
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        metadata = metadata
except Exception:
    # for sqlalchemy 1.4
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

current_module = sys.modules[__name__]


def add_dbml(path, module=current_module):
    parsed = PyDBML(Path(path))
    for table in parsed.tables:
        createModel(table, Base, module=module)


add_dbml(os.path.join(os.path.dirname(os.path.abspath(__file__)), "map.dbml"), current_module)

# Create DB
Base.metadata.create_all(bind=engine)
db = SessionLocal()
if not db.query(User).filter(User.isadmin == True).first():
    admin = User(
        username="admin",
        password=hash_password("secret"),
        email="admin@example.com",
        token=str(uuid.uuid4()),
        disabled=False,
        isadmin=True,
        onlyapi=False
    )
    db.add(admin)
    db.commit()
    print("admin is created")
db.close()
