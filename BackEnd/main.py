from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
import hashlib 

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

def user_exists(username: str, db: db_dependency):
    return db.query(models.User).filter(models.User.username == username).first()

# * Below are endpoints related to users, such as signing in, registration,
# * password changes, etc.
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = user.model_dump()
    if not user_exists(db_user['username'], db):
        db_user['password'] = hash_password(db_user['password'])
        db.add(models.User(**db_user))
        db.commit()
    else:
        raise HTTPException(status_code=404, detail='User already exists')

@app.get("/user/{username}" , status_code=status.HTTP_200_OK)
async def read_user(username: str, db:db_dependency):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User Not Found')
    return user