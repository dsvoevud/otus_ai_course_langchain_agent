import subprocess
import json
import time
import pathlib

server_cmd = [
    r"E:\AI_Course\1_12\otus_ai_course_langchain_agent\.venv\Scripts\python.exe",
    r"E:\AI_Course\1_12\otus_ai_course_langchain_agent\mcp\mcp_server.py"
]

msg = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0"}
    }
}) + "\n"

p = subprocess.Popen(
    server_cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=r"E:\AI_Course\1_12\otus_ai_course_langchain_agent\mcp"
)

try:
    # Give the server a moment to start
    out, err = p.communicate(input=msg.encode(), timeout=3)
except subprocess.TimeoutExpired:
    # If the server stays running, terminate the child process we started
    p.terminate()
    out, err = p.communicate()

print("=== STDOUT ===")
print(out.decode() if out else "(empty)")
print("=== STDERR ===")
print(err.decode() if err else "(empty)")

# Additionally, import the mcp_server module directly and call the tool function
spec_path = pathlib.Path(__file__).parent / "mcp" / "mcp_server.py"
import importlib.util
spec = importlib.util.spec_from_file_location("sample_mcp_server", str(spec_path))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

try:
    print('\nCalling get_all_books() directly to exercise logging...')
    books = mod.get_all_books()
    # mod.get_all_books() returns a JSON string in current implementation
    try:
        parsed = json.loads(books)
        print('Fetched', len(parsed), 'books')
    except Exception:
        print('Fetched (raw):', books)
except Exception as e:
    print('Error calling get_all_books():', e)

# Show the log file contents
log_path = pathlib.Path(__file__).parent / "mcp" / "mcp_server.log"
if log_path.exists():
    print('\n--- MCP Server Log ---')
    print(log_path.read_text())
else:
    print('\nLog file not found:', log_path)
