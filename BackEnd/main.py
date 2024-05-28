from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
import hashlib
from authentication import *

app = FastAPI()

origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
)

# This is the data that the frontend should pass when a user
# creates an account
class UserBase(BaseModel):
    username: str
    email: str
    password: str
    admin: int
    date_created: float 

# This is the data that the frontend should pass when
# a book is being added to the database
class BooksBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    page_count: int
    year_published: int
    genre: str

# Unused at the moment
class Reading_ListBase(BaseModel):
    id: int
    username: str
    isbn: str
    folder: str

# This is the data that the frontend needs to pass
# when a user creates a comment
class CommentsBase(BaseModel):
    book_isbn: str
    username: str
    content: str
    time_stamp: float

# This is the data that the frontend needs to pass
# when a user leaves a rating
class RatingBase(BaseModel):
    book_isbn: str
    username: str
    rating: int

# This is the data that the frontend needs to pass
# when a user tries to login
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



# * -- Helper functions for endpoints -- * #
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

# A simple boolean to check if a user exists or not.
def user_exists(username: str, db: db_dependency):
    return db.query(models.User).filter(models.User.username == username).first()


# * -- Below are endpoints related to users, such as signing in, registration,      -- * #
# * -- password changes, etc.                                                       -- * #


# Create user account
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = user.model_dump()
    if not user_exists(db_user['username'], db):
        db_user['password'] = hash_password(db_user['password'])
        db.add(models.User(**db_user))
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')


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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username or password is incorrect')


# *  -- Below are endpoints dealing with books -- * #


@app.post("/book/", status_code=status.HTTP_200_OK)
async def create_book(book: BooksBase, db: db_dependency):
    book_dump = book.model_dump()
    db_check_book = db.query(models.Books).filter(models.Books.isbn == book_dump['isbn']).first()
    if not db_check_book:
        db.add(models.Books(**book_dump))
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Book already exists')


@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books(skip: int, limit: int, db: db_dependency):
    books = db.query(models.Books).order_by(models.Books.title).offset(skip).limit(limit).all()
    return books


@app.get('/book/{book_isbn}', status_code=status.HTTP_200_OK)
async def get_book(book_isbn: str, db: db_dependency):
    book = db.query(models.Books).filter(models.Books.isbn == book_isbn).first()
    return book


# TODO: need to add the deletion of comments that are on that isbn
# TODO: need to add the deletion of the book within a users reading list
@app.delete('/book/{book_isbn}', status_code=status.HTTP_200_OK)
async def remove_book(book_isbn: str, db: db_dependency):
    db_check_book = db.query(models.Books).filter(models.Books.isbn == book_isbn)
    if db_check_book:
        db_check_book = db.query(models.Books).filter(models.Books.isbn == book_isbn).delete()
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book does not exist')


# * Below are endpoints for comments


@app.post("/comments/", status_code=status.HTTP_200_OK)
async def add_comment(comment: CommentsBase, db: db_dependency):
    comment_dump = comment.model_dump()
    db.add(**comment_dump)
    db.commit()


