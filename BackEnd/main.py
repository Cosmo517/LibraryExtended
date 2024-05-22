from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated , List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

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

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()

@app.get("/user/{user_id}" , status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db:db_dependency):
    user = db.query(models.User).filter(models.User.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail= 'User Not Found')
    return user
