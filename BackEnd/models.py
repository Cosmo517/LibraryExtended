from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

# Creating users table
class User(Base):
    __tablename__= 'users'
    username = Column(String(25), primary_key=True, index=True)
    email = Column(String(128), nullable=False)
    password = Column(String(256), nullable=False)
    admin= Column(Integer, nullable=False)
    date_created= Column(Float,nullable=False)

# Creating books table
class Books(Base):
    __tablename__= 'books'
    isbn = Column(String(14), primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    author = Column (String(50), nullable=False)
    publisher = Column(String(50), nullable=False)
    page_count = Column(Integer, nullable=False)
    year_published = Column(Integer, nullable=False)
    genre = Column (String(50), nullable=False)

# Creating reading list table
class Reading_List(Base):
    __tablename__= 'reading_list'
    index = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(14), ForeignKey('books.isbn'), nullable=False)
    username = Column(String(25), ForeignKey('users.username'), nullable=False)
    folder = Column(String(50), nullable=False)

# Creating book to list tabe
class Book_to_List(Base):
    __tablename__= 'book _to_list'
    list_index = Column(Integer, ForeignKey('reading_list.index'), primary_key=True, index=True)
    isbn = Column(String(14), ForeignKey('books.isbn'), primary_key=True, index=True)

# Creating comments table
class Comments(Base):
    __tablename__= 'comments'
    id = Column(Integer, primary_key=True, index=True)
    book_isbn = Column(String(14), ForeignKey('books.isbn'), nullable=False)
    username = Column(String(25), ForeignKey('users.username'), nullable=False)
    content = Column(String(1000), nullable=False)
    time_stamp = Column(Float, nullable=False)

# Creating rating table
class Rating(Base):
    __tablename__= 'rating'
    id = Column(Integer, primary_key=True, index=True)
    book_isbn = Column(String(14), ForeignKey('books.isbn'), nullable=False)
    username = Column(String(25), ForeignKey('users.username'), nullable=False)
    rating =  Column(Integer, nullable=False)