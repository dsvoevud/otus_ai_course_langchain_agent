from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
import os

app = FastAPI(title="Book Storage API", description="A simple API for managing books")

class Book(BaseModel):
    id: int
    author: str
    name: str
    year: int

class BookCreate(BaseModel):
    author: str
    name: str
    year: int

DATA_FILE = "data.json"

def load_books():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_books(books):
    with open(DATA_FILE, "w") as f:
        json.dump(books, f, indent=4)

books = load_books()

@app.post("/books", response_model=Book)
def create_book(book: BookCreate):
    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {"id": new_id, **book.dict()}
    books.append(new_book)
    save_books(books)
    return new_book

@app.get("/books/{book_id}", response_model=Book)
def get_book_by_id(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books", response_model=Book)
def get_book_by_name(name: str = Query(..., description="Name of the book")):
    for book in books:
        if book["name"].lower() == name.lower():
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/search", response_model=list[Book])
def search_books(author: str = Query(None, description="Author of the book"), name: str = Query(None, description="Name of the book")):
    filtered = books
    if author:
        filtered = [b for b in filtered if author.lower() in b['author'].lower()]
    if name:
        filtered = [b for b in filtered if name.lower() in b['name'].lower()]
    return filtered

@app.get("/books/author/{author}", response_model=list[Book])
def get_books_by_author(author: str):
    filtered = [b for b in books if author.lower() in b['author'].lower()]
    return filtered

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, updated_book: BookCreate):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            books[i] = {"id": book_id, **updated_book.dict()}
            save_books(books)
            return books[i]
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            del books[i]
            save_books(books)
            return {"message": "Book deleted"}
    raise HTTPException(status_code=404, detail="Book not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)