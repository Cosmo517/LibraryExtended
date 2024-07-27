from pydantic import BaseModel

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
class FoldersBase(BaseModel):
    username: str
    folder: str

class FoldersToBooksBase(BaseModel):
    folder: str
    book_isbn: str
    
    
class AddFolderToBook(BaseModel):
    username: str
    folder: str
    book_isbn: str
    
class RemoveFolderToBook(BaseModel):
    username: str
    folder_id: int
    book_isbn: str

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
    
# This is for when a user wants to move books between
# folders
class MoveBookFolder(BaseModel):
    username: str
    isbn: str
    from_folder_id: int
    to_folder_id: int