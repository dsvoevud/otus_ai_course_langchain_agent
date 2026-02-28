"""
mcp_stop.py — Stop all running mcp_server.py processes and clear the log file.

Usage (from workspace root):
    .\.venv\Scripts\python.exe mcp\mcp_stop.py

Exit codes:
    0 — one or more processes were found and terminated
    2 — no running mcp_server.py processes found
    3 — error (e.g., missing dependencies)
"""

import sys
import os


TARGET = "mcp_server.py"
LOG_FILE = os.path.join(os.path.dirname(__file__), "mcp_server.log")


def _clear_log():
    """Truncate mcp_server.log if it exists."""
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
        print(f"[mcp_stop] Cleared log file: {LOG_FILE}")
    else:
        print(f"[mcp_stop] Log file not found, skipping: {LOG_FILE}")


def _stop_with_psutil():
    import psutil

    found = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"] or []
            if any(TARGET in part for part in cmdline):
                found.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not found:
        return []

    stopped = []
    for proc in found:
        try:
            pid = proc.pid
            cmdline = " ".join(proc.cmdline())
            proc.terminate()
            proc.wait(timeout=5)
            stopped.append((pid, cmdline))
            print(f"[mcp_stop] Terminated PID {pid}: {cmdline}")
        except psutil.TimeoutExpired:
            proc.kill()
            stopped.append((pid, cmdline))
            print(f"[mcp_stop] Force-killed PID {pid}: {cmdline}")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"[mcp_stop] Warning: could not stop PID {proc.pid}: {e}")

    return stopped


def _stop_with_powershell():
    import subprocess
    import re

    # Find PIDs via PowerShell
    ps_find = (
        'Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*mcp_server.py*" } '
        '| Select-Object ProcessId, CommandLine | ConvertTo-Json -Compress'
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_find],
        capture_output=True,
        text=True,
    )
    raw = result.stdout.strip()
    if not raw or raw == "null":
        return []

    import json

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    # PowerShell may return a single object or a list
    if isinstance(data, dict):
        data = [data]

    stopped = []
    for item in data:
        pid = item.get("ProcessId")
        cmdline = item.get("CommandLine", "")
        if pid is None:
            continue
        kill_result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {pid} -Force"],
            capture_output=True,
        )
        if kill_result.returncode == 0:
            stopped.append((pid, cmdline))
            print(f"[mcp_stop] Terminated PID {pid}: {cmdline}")
        else:
            print(f"[mcp_stop] Warning: could not stop PID {pid}: {kill_result.stderr.decode().strip()}")

    return stopped


def main():
    try:
        import psutil  # noqa: F401
        use_psutil = True
    except ImportError:
        use_psutil = False

    try:
        if use_psutil:
            stopped = _stop_with_psutil()
        else:
            if sys.platform != "win32":
                print("[mcp_stop] Error: psutil is required on non-Windows platforms.")
                sys.exit(3)
            print("[mcp_stop] psutil not available, using PowerShell fallback.")
            stopped = _stop_with_powershell()
    except Exception as e:
        print(f"[mcp_stop] Error: {e}")
        sys.exit(3)

    if not stopped:
        print(f"[mcp_stop] No running '{TARGET}' processes found.")
        sys.exit(2)

    print(f"[mcp_stop] Done. Stopped {len(stopped)} process(es).")
    _clear_log()
    sys.exit(0)


if __name__ == "__main__":
    main()
