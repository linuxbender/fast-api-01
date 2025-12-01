"""FastAPI application"""

from fastapi import FastAPI

app = FastAPI(title="FastAPI 01", version="0.1.0")


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "Hello World with FastAPI"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None) -> dict[str, int | str | None]:
    """Get an item by ID"""
    return {"item_id": item_id, "q": q}
