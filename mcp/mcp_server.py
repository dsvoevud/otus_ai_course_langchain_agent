import requests
import logging
import os
import json
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

SAMPLE_API_URL = "http://localhost:8000"

mcp = FastMCP("Books MCP Server")

# Configure logging: console + file in the mcp folder
log = logging.getLogger("mcp_server")
log.setLevel(logging.INFO)
if not log.handlers:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    log.addHandler(ch)
    log_path = os.path.join(os.path.dirname(__file__), "mcp_server.log")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    log.addHandler(fh)


# --- Read-only tools (no confirmation required) ---

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_all_books() -> list:
    """Returns all books from the storage."""
    tool = "get_all_books"
    log.info("Tool call: %s params=%s", tool, None)
    try:
        response = requests.get(f"{SAMPLE_API_URL}/books/all")
        response.raise_for_status()
        result = response.json()
        log.info("Tool success: %s status=success items=%d", tool, len(result) if isinstance(result, list) else 0)
        # serialize to a JSON string so callers always see JSON text
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        log.exception("Tool error: %s", tool)
        raise


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_book_by_id(book_id: int) -> dict:
    """Returns a single book by its ID."""
    tool = "get_book_by_id"
    log.info("Tool call: %s params=book_id=%s", tool, book_id)
    try:
        response = requests.get(f"{SAMPLE_API_URL}/books/{book_id}")
        if response.status_code == 404:
            log.info("Tool result: %s status=not_found book_id=%s", tool, book_id)
            return json.dumps({"error": f"Book with ID {book_id} not found"}, ensure_ascii=False, indent=2)
        response.raise_for_status()
        result = response.json()
        log.info("Tool success: %s status=success book_id=%s", tool, book_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        log.exception("Tool error: %s book_id=%s", tool, book_id)
        raise


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def search_books(author: str = None, name: str = None) -> list:
    """Searches books by author and/or title. At least one parameter must be provided."""
    tool = "search_books"
    log.info("Tool call: %s params=author=%s name=%s", tool, author, name)
    if not author and not name:
        log.warning("Tool %s missing parameters", tool)
        return json.dumps({"error": "Provide at least one search parameter: author or name"}, ensure_ascii=False, indent=2)
    params = {}
    if author:
        params["author"] = author
    if name:
        params["name"] = name
    try:
        response = requests.get(f"{SAMPLE_API_URL}/books/search", params=params)
        response.raise_for_status()
        result = response.json()
        log.info("Tool success: %s status=success results=%d", tool, len(result) if isinstance(result, list) else 0)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        log.exception("Tool error: %s", tool)
        raise


# --- Mutating tools (human confirmation required) ---

@mcp.tool(annotations=ToolAnnotations(
    destructiveHint=False,  # creates new data, does not destroy
    idempotentHint=False,   # each call creates a new entry
))
def add_book(name: str, author: str, year: int) -> dict:
    """Adds a new book to the storage. REQUIRES HUMAN CONFIRMATION before executing."""
    tool = "add_book"
    params = {"name": name, "author": author, "year": year}
    log.info("Tool call: %s params=%s", tool, params)
    try:
        response = requests.post(
            f"{SAMPLE_API_URL}/books",
            json=params,
        )
        response.raise_for_status()
        result = response.json()
        log.info("Tool success: %s status=success book_id=%s", tool, result.get("id"))
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        log.exception("Tool error: %s params=%s", tool, params)
        raise


@mcp.tool(annotations=ToolAnnotations(
    destructiveHint=True,   # permanently removes data
    idempotentHint=False,
))
def delete_book(book_id: int) -> dict:
    """Permanently deletes a book from the storage by its ID. REQUIRES HUMAN CONFIRMATION before executing."""
    tool = "delete_book"
    log.info("Tool call: %s params=book_id=%s", tool, book_id)
    try:
        response = requests.delete(f"{SAMPLE_API_URL}/books/{book_id}")
        if response.status_code == 404:
            log.info("Tool result: %s status=not_found book_id=%s", tool, book_id)
            return json.dumps({"error": f"Book with ID {book_id} not found"}, ensure_ascii=False, indent=2)
        response.raise_for_status()
        result = response.json()
        log.info("Tool success: %s status=success book_id=%s", tool, book_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        log.exception("Tool error: %s book_id=%s", tool, book_id)
        raise


if __name__ == "__main__":
    mcp.run()
