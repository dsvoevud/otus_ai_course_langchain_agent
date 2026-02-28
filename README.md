# OTUS AI Course MCP Server

## Installation

1. Install Python 3.12 using uv:

```bash
uv python install 3.12.12
```

2. Create a virtual environment with Python 3.12:

```bash
uv venv --python 3.12.12
```

3. Install the required packages:

```bash
uv pip install -r requirements.txt
```

## Sample API

A sample FastAPI application for book storage is included in the `SampleAPI` folder. It provides CRUD operations for books with fields: id, author, name, year.

### Endpoints

- `POST /books` - Create a new book
- `GET /books/all` - Get all books
- `GET /books/{id}` - Get a book by ID
- `GET /books?name={name}` - Get a book by name
- `GET /books/author/{author}` - Get all books by a specific author
- `GET /books/search?author={author}&name={name}` - Search books by author and/or name
- `PUT /books/{id}` - Update a book by ID
- `DELETE /books/{id}` - Delete a book by ID

### Running the Sample API

1. Navigate to the SampleAPI folder:

```bash
cd SampleAPI
```

2. Run the API:

```bash
uv run uvicorn main:app --reload
```

3. Open your browser to `http://localhost:8000/docs` for Swagger UI.

### Data Storage

Books are stored in `data.json` in the SampleAPI folder. Initial stub data is provided.

## MCP Server

The `mcp/mcp_server.py` file implements a **Model Context Protocol (MCP)** server that exposes the Book Storage API as AI-callable tools. This README documents the tools, how to run the MCP server, and how to register it for VS Code (Agent/Copilot) use.

### How It Works

```
User (AI Client)
      │
      │  natural language
      ▼
MCP-Compatible Client (e.g., Claude Desktop)
      │
      │  MCP protocol (JSON-RPC over stdio)
      ▼
mcp_server.py  ←── ToolAnnotations control confirmation prompts
      │
      │  HTTP REST calls
      ▼
SampleAPI (FastAPI on localhost:8000)
      │
      │  read/write
      ▼
data.json (book storage)
```

1. The AI client receives a user query (e.g., "Delete the book with ID 3").
2. The client selects the appropriate MCP tool (`delete_book`).
3. Because `destructiveHint=True`, the client shows a **confirmation dialog** before proceeding.
4. Upon confirmation, the MCP server calls the SampleAPI `DELETE /books/3` endpoint.
5. The result is returned to the AI client and presented to the user.

### Prerequisites

1. The SampleAPI must be running before starting the MCP server (see [Running the Sample API](#running-the-sample-api)).

### Available MCP Tools

| Tool | Type | Human Confirmation | Description |
|---|---:|---:|---|
| `get_all_books()` | Read-only | No | Returns a list of all books (list of objects with `id`, `name`, `author`, `year`). Returns JSON string when called via MCP. |
| `get_book_by_id(book_id)` | Read-only | No | Returns a single book object for the given `book_id`. If not found, returns `{"error": "Book with ID X not found"}`. |
| `search_books(author=None, name=None)` | Read-only | No | Searches books by `author` and/or `name`. At least one parameter required; returns matching list. If no parameters provided, returns an error object. |
| `add_book(name, author, year)` | Mutating | Yes | Adds a new book. Annotated `destructiveHint=False`, `idempotentHint=False`. Returns the created book object (with assigned `id`). Client should prompt user for confirmation before calling. |
| `delete_book(book_id)` | Mutating | Yes | Permanently deletes the book with `book_id`. Annotated `destructiveHint=True`. Returns a success message or error if not found. Client must prompt for confirmation. |

### Running the MCP Server

1. Start the SampleAPI (terminal A):

```powershell
cd SampleAPI
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Or (simple runner):

```powershell
cd SampleAPI
python main.py
```

2. Start the MCP server (terminal B):

From the workspace root:

```powershell
.\.venv\Scripts\python.exe mcp\mcp_server.py
```

Or change to the `mcp` folder and run:

```powershell
cd mcp
.\.venv\Scripts\python.exe mcp_server.py
..\.venv\Scripts\python.exe mcp_server.py
```

3. Stop the MCP server:

- Press `Ctrl+C` in the running terminal.
- Or kill the process from PowerShell (search for `mcp_server.py` in the python command line) or Task Manager.

### Registering the MCP server for VS Code (Agent/Copilot)

Use workspace-level `.vscode/mcp.json` or a user-level `%APPDATA%\Code\User\mcp.json` if workspace settings are restricted by policy. Example user-level entry:

```json
{
      "mcpServers": {
            "books-api": {
                  "command": "E:\\AI_Course\\1_12\\otus_ai_course_langchain_agent\\.venv\\Scripts\\python.exe",
                  "args": ["E:\\AI_Course\\1_12\\otus_ai_course_langchain_agent\\mcp\\mcp_server.py"]
            }
      }
}
```

- Restart VS Code. Open the Agent / Copilot Tools panel and enable the `books-api` MCP tools. When a tool is mutating, the client will show a confirmation prompt before executing.

Note: workspace or org policies may block workspace-level MCP registrations — in that case use the user-level `mcp.json` or contact your administrator.

### How It Works (high-level)

1. The AI client (VS Code Agent / Copilot) sends a JSON-RPC request over stdio to the MCP server.
2. `mcp_server.py` maps tool calls to HTTP requests to the local SampleAPI.
3. SampleAPI performs the requested operation and updates `data.json` as needed.
4. Results (JSON strings) are returned via MCP to the AI client for display or further actions.

Example flow: user asks the agent to delete book ID 3 → client selects `delete_book(3)` → client prompts the user (destructive operation) → upon confirmation MCP server calls `DELETE /books/3` → result returned to client.

### Verifying the MCP server (helper script)

A small helper script `mcp/mcp_healthcheck.py` is included to detect whether `mcp_server.py` is running and to show recent entries from the MCP server log.

Run from the workspace root (uses the workspace venv):

```powershell
.\.venv\Scripts\python.exe mcp\mcp_healthcheck.py
```

Or change to the `mcp` folder and run (use the parent venv):

```powershell
cd mcp
..\.venv\Scripts\python.exe mcp_healthcheck.py
```

Options:
- `--tail N` — show the last N lines from `mcp/mcp_server.log` (default 20).

What the script does:
- Attempts to detect `mcp_server.py` using `psutil` (if installed).
- If `psutil` is not available on Windows it falls back to a PowerShell query to find running `python.exe` processes whose command line contains `mcp_server.py`.
- If a process is found, it prints the PID(s) and command line(s) and tails `mcp/mcp_server.log`.
- Exit codes: `0` = found and printed info, `2` = not found, `3` = error (e.g., missing dependencies).

If `psutil` is not installed and you prefer it, install it using `uv`:

```powershell
uv pip install psutil
```

### Stopping the MCP server (helper script)

A small helper script `mcp/mcp_stop.py` is included to terminate all running `mcp_server.py` processes at once.

Run from the workspace root (uses the workspace venv):

```powershell
.\.venv\Scripts\python.exe mcp\mcp_stop.py
```

Or change to the `mcp` folder and run (use the parent venv):

```powershell
cd mcp
..\.venv\Scripts\python.exe mcp_stop.py
```

What the script does:
- Uses `psutil` (if installed) to find and terminate any Python process whose command line contains `mcp_server.py`.
- On Windows, falls back to a PowerShell `Stop-Process` query if `psutil` is not available.
- Sends `SIGTERM` first; if the process does not exit within 5 seconds, sends `SIGKILL`.
- Prints the PID and command line of every process stopped.

Exit codes:
- `0` — one or more processes were found and terminated
- `2` — no running `mcp_server.py` processes found
- `3` — error (e.g., missing dependencies or permission denied)

### MCP Sample prompts
1. What books do you have? - should return all the books from data.json
2. Add a book called Test Book written by Test Author in 1234 - should ask the user to add the book
3. Delete the Test Book - should delete the book with this name from data.json.
4. What books by J.K. Rowling do you have? - should return only 2 books by J.K. Rowling


### MCP Logs
Logs can be found in mcp_server.log or in the console.