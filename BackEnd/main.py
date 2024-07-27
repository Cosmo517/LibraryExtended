from fastapi import FastAPI, HTTPException, Depends, status
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
import hashlib
from authentication import *
from sqlalchemy import func
from data_types import *

app = FastAPI()

origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
)

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
    return db.query(models.Users).filter(models.Users.username == username).first()


# * -- Below are endpoints related to users, such as signing in, registration,      -- * #
# * -- password changes, etc.                                                       -- * #


# Create user account
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = user.model_dump()
    if not user_exists(db_user['username'], db):
        db_user['password'] = hash_password(db_user['password'])
        db.add(models.Users(**db_user))
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')


# Delete a users account
@app.delete("/user/{username}", status_code=status.HTTP_200_OK)
async def delete_user(username: str, db: db_dependency):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    else:
        db.delete(user)
        db.commit()


# Get information about a user
@app.get("/user/{username}" , status_code=status.HTTP_200_OK)
async def read_user(username: str, db: db_dependency):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


# Allow user to sign in
@app.get("/users/login/", status_code=status.HTTP_200_OK)
async def login(user: LoginBase, db: db_dependency):
    db_user = user.model_dump()
    db_user_search = db.query(models.Users).filter(models.Users.username == db_user['username']).first()
    if db_user_search:
        if compare_passwords(db_user['password'], db_user_search['password']):
            return sign_jwt(db_user['username'], db_user_search['admin'])
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username or password is incorrect')


# Refresh a users login token
# TODO: Make sure refresh_token works
@app.get("/users/token/refresh/{token}", status_code=status.HTTP_200_OK)
async def refresh_token(token: str):
    return refresh_jwt(token)

# *  -- Below are endpoints dealing with books -- * #


# Create a new book record
@app.post("/book/", status_code=status.HTTP_200_OK)
async def create_book(book: BooksBase, db: db_dependency):
    book_dump = book.model_dump()
    db_check_book = db.query(models.Books).filter(models.Books.isbn == book_dump['isbn']).first()
    if not db_check_book:
        db.add(models.Books(**book_dump))
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Book already exists')


# Get book information from the database
@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books(skip: int, limit: int, db: db_dependency):
    books = db.query(models.Books).order_by(models.Books.title).offset(skip).limit(limit).all()
    return books


# Get information about a certain book
@app.get('/book/{book_isbn}', status_code=status.HTTP_200_OK)
async def get_book(book_isbn: str, db: db_dependency):
    book = db.query(models.Books).filter(models.Books.isbn == book_isbn).first()
    return book


# TODO: Check to make sure remove_book endpoint works
# Delete a book record based on the isbn as well as comments, ratings, etc
@app.delete('/book/{book_isbn}', status_code=status.HTTP_200_OK)
async def remove_book(book_isbn: str, db: db_dependency):
    db_check_book = db.query(models.Books).filter(models.Books.isbn == book_isbn)
    if db_check_book:
        # delete the comments
        comments_for_book = db.query(models.Comments).filter(models.Comments.book_isbn == book_isbn).all()
        
        for comment in comments_for_book:
            db.delete(comment)
        db.commit()
        
        # delete the ratings
        ratings_for_book = db.query(models.Ratings).filter(models.Ratings.book_isbn == book_isbn).all()
        
        for rating in ratings_for_book:
            db.delete(rating)
        db.commit()
        
        # delete books from peoples folders
        books_in_folders = db.query(models.FoldersToBooks).filter(models.FoldersToBooks.book_isbn == book_isbn).all()

        for book in books_in_folders:
            db.delete(book)
        db.commit()
        
        # delete the book
        db_check_book = db.query(models.Books).filter(models.Books.isbn == book_isbn).delete()
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book does not exist')


# * -- Below are endpoints for comments -- * #

# Create comments
@app.post("/comments/", status_code=status.HTTP_200_OK)
async def add_comment(comment: CommentsBase, db: db_dependency):
    comment_dump = comment.model_dump()
    db.add(models.Comments(**comment_dump))
    db.commit()


# Delete comments
@app.delete("/comments/{id}", status_code=status.HTTP_200_OK)
async def delete_comment(id: int, db: db_dependency):
    db_delete_comment = db.query(models.Comments).filter(models.Comments.id == id)
    db.delete(db_delete_comment)
    db.commit()


# * -- Below are endpoints for user folders -- * #


@app.post('/folder/create/', status_code=status.HTTP_200_OK)
async def create_folder(folder: FoldersBase, db: db_dependency):
    folder_dump = folder.model_dump()
    print(folder_dump)
    folder_exists = db.query(models.Folders).filter(
        models.Folders.username == folder_dump['username']).filter(
        models.Folders.folder == folder_dump['folder']).first()
    if folder_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Folder already exists')
    else:
        db.add(models.Folders(**folder_dump))
        db.commit()


@app.delete('/folder/delete/', status_code=status.HTTP_200_OK)
async def delete_folder(folder: FoldersBase, db: db_dependency):
    folder_dump = folder.model_dump()
    folder_exists = db.query(models.Folders).filter(
        models.Folders.username == folder_dump['username']).filter(
        models.Folders.folder == folder_dump['folder']).first()
    
    if folder_exists:
        folder_to_books = db.query(models.FoldersToBooks).filter(models.FoldersToBooks.folder_id == folder_exists.id)
        for book in folder_to_books:
            db.delete(book)
        db.delete(folder_exists)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Folder does not exist')


@app.get('/folder/get/{username}', status_code=status.HTTP_200_OK)
async def get_user_folders(username: str, db: db_dependency):
    user_exists = db.query(models.Users).filter(models.Users.username == username).first()
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    all_folders = db.query(models.Folders).filter(models.Folders.username == username).all()
    return all_folders


@app.post('/folder/book/add/', status_code=status.HTTP_200_OK)
async def add_book_to_folder(book: AddFolderToBook, db: db_dependency):
    book_info = book.model_dump()
    
    # Make sure the user exists
    user_exists = db.query(models.Users).filter(models.Users.username == book_info['username']).first()
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    # Get ID of the folder
    id_of_folder = db.query(models.Folders).filter(
        models.Folders.folder == book_info['folder']).filter(
        models.Folders.username == book_info['username']).first()

    # Make sure folder exists
    if not id_of_folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Folder does not exist')

    # Now we can create the entry
    book_to_add = { 'folder_id': id_of_folder.id, 'book_isbn': book_info['book_isbn'] }

    db.add(models.FoldersToBooks(**book_to_add))
    db.commit()


# TODO: Check to make sure remove_book_from_folder works
@app.delete('/folder/book/delete/', status_code=status.HTTP_200_OK)
async def remove_book_from_folder(book: RemoveFolderToBook, db: db_dependency):
    user_exists = db.query(models.Users).filter(models.Users.username == book.username).first()
    
    # Make sure the user exists
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    folder_to_search = db.query(models.Folders).filter(
        models.Folders.id == book.folder_id).filter(
        models.Folders.username == book.username).first()
    
    if not folder_to_search:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Folder does not exist')
    
    book_in_folder = db.query(models.FoldersToBooks.folder_id == book.folder_id).filter(
        models.FoldersToBooks.book_isbn == book.book_isbn).first()
    
    if not book_in_folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book does not exist in the selected folder")
    
    db.delete(book_in_folder)


# TODO: Make sure get_all_books_in_folder works
@app.get('/folder/book/get/{folder}/{username}', status_code=status.HTTP_200_OK)
async def get_all_books_in_folder(username: str, folder: str, db: db_dependency):
    user_exists = db.query(models.Users).filter(models.Users.username == username).first()
    
    # Make sure the user exists
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    folder_to_search = db.query(models.Folders).filter(
        models.Folders.folder == folder).filter(
        models.Folders.username == username).first()
    
    if not folder_to_search:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Folder does not exist')
    
    books = db.query(models.Folders).filter(
        models.FoldersToBooks.folder_id == folder_to_search.id).all()
    
    return books


# TODO: Check to make sure move_book works
@app.post('/folder/book/move/', status_code=status.HTTP_200_OK)
async def move_book(bookToFolder: MoveBookFolder, db: db_dependency):
    user_exists = db.query(models.Users).filter(models.Users.username == bookToFolder.username).first()
    
    # Make sure the user exists
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    # Make sure both folders exist
    from_folder = db.query(models.Folders).filter(models.Folders.id == bookToFolder.from_folder_id).first()
    to_folder = db.query(models.Folders).filter(models.Folders.id == bookToFolder.to_folder_id).first()
    
    if not from_folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The folder you are trying to move from does not exist')
    
    if not to_folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The folder you are trying to move to does not exist')
    
    # Make sure the book exists, and it exists within the folder we are trying to move from
    book_exists = db.query(models.Books).filter(models.Books.isbn == bookToFolder.isbn).first()
    
    if not book_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The book you are trying to move does not exist')
    
    book_from_folder_exists = db.query(models.FoldersToBooks).filter(
        models.FoldersToBooks.book_isbn == bookToFolder.isbn).filter(
            models.FoldersToBooks.folder_id == bookToFolder.from_folder_id)
    
    if not book_from_folder_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The book does not exist in the current folder')
    
    # We can now move the book
    db.add(models.FoldersToBooks({"folder_id": bookToFolder.to_folder_id, "book_isbn": bookToFolder.isbn}))
    db.commit()
    
    db.delete(models.FoldersToBooks({"folder_id": bookToFolder.from_folder_id, "book_isbn": bookToFolder.isbn}))
    db.commit()

# * -- Below are endpoints for ratings -- * #


@app.post("/ratings/", status_code=status.HTTP_200_OK)
async def add_rating(rating: RatingBase, db: db_dependency):
    rating_dump = rating.model_dump()
    
    user_exists = db.query(models.Users).filter(models.Users.username == rating_dump['username']).first()
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    book_exists = db.query(models.Books).filter(models.Books.isbn == rating_dump['book_isbn']).first()
    if not book_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book does not exist')
    
    already_rated = db.query(models.Ratings).filter(models.Ratings.username == rating_dump['username']).filter(models.Ratings.book_isbn == rating_dump['book_isbn']).first()
    if not already_rated:
        db.add(models.Ratings(**rating_dump))
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already rated this book')


@app.get("/ratings/{book_isbn}", status_code=status.HTTP_200_OK)
async def average_ratings(book_isbn: str, db: db_dependency):
    rating_total = db.query(func.sum(models.Ratings.book_isbn)).filter(models.Ratings.book_isbn == book_isbn).scalar()
    if rating_total is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No ratings exist for this book')
    amount_of_ratings = db.query(models.Ratings).filter(models.Ratings.book_isbn == book_isbn).count()
    average_rating = rating_total / amount_of_ratings
    return {'rating' : rating_total, 'votes' : amount_of_ratings, 'average' : average_rating}

