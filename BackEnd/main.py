from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
import hashlib
from authentication import *

app= FastAPI()

origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
)

class UserBase(BaseModel):
    username: str
    email: str
    password: str
    admin: int
    date_created: float 

class BooksBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    page_count: int
    year_published: int
    genre: str

class Reading_ListBase(BaseModel):
    index: int
    isbn: str
    username: str
    folder: str

class Book_to_ListBase(BaseModel):
    list_index: int
    isbn: str

class CommentsBase(BaseModel):
    id: int
    book_isbn: str
    username: str
    content: str
    time_stamp: float

class RatingBase(BaseModel):
    id: int
    book_isbn: str
    username: str
    rating: int

class LoginBase(BaseModel):
    username: str
    password: str

# No matter what this will always close our database since we dont want to keep our databases open for too long
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)



# * Helper functions for endpoints
def hash_password(password: str):
    """Hashes a given password using SHA256

    Args:
        password (str): The password or string to hash

    Returns:
        str: The hashed version of the password.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def compare_passwords(login_password: str, database_password: str):
    """This function compares the password the user entered to login,
    with the password that is in the database.

    Args:
        login_password (str): The password the user entered to login
        database_password (str): The password from the database

    Returns:
        bool: True if the passwords match, or false if they don't 
    """
    return hashlib.sha256(login_password.encode()).hexdigest() == database_password

def user_exists(username: str, db: db_dependency):
    return db.query(models.User).filter(models.User.username == username).first()

# * Below are endpoints related to users, such as signing in, registration,
# * password changes, etc.

# Create user account
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = user.model_dump()
    if not user_exists(db_user['username'], db):
        db_user['password'] = hash_password(db_user['password'])
        db.add(models.User(**db_user))
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User already exists')

# Get information about a user
@app.get("/user/{username}" , status_code=status.HTTP_200_OK)
async def read_user(username: str, db:db_dependency):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

# Allow user to sign in
@app.get("/users/login/", status_code=status.HTTP_200_OK)
async def login(user: LoginBase, db: db_dependency):
    db_user = user.model_dump()
    db_user_search = db.query(models.User).filter(models.User.username == db_user['username']).first()
    if db_user_search:
        if compare_passwords(db_user['password'], db_user_search['password']):
            return sign_jwt(db_user['username'], db_user_search['admin'])
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username or password is incorrect')
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username or password is incorrect')
    
    