#!/usr/bin/env python3
"""Check whether the MCP server is running and show recent logs.

Usage:
  python mcp_healthcheck.py        # basic check + show last 20 log lines if available
  python mcp_healthcheck.py --tail 100   # show last 100 log lines

This script prefers `psutil` (if installed) to detect running processes.
On Windows, if `psutil` is not available it will try a PowerShell query.
Exit code 0 = running, 2 = not found, 3 = error.
"""
import os
import sys
import argparse
import subprocess

LOG_FILE = os.path.join(os.path.dirname(__file__), "mcp_server.log")


def find_process_psutil():
    try:
        import psutil
    except Exception:
        return None
    found = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = p.info.get('cmdline') or []
            cmd = ' '.join(cmdline)
            if 'mcp_server.py' in cmd or 'mcp_server' in cmd:
                found.append((p.pid, cmd))
        except Exception:
            continue
    return found


def find_process_powershell():
    # Use PowerShell to query processes and return JSON-ish output
    try:
        ps_cmd = (
            "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'mcp_server.py' } "
            "| Select-Object ProcessId, CommandLine | ConvertTo-Json -Depth 3"
        )
        completed = subprocess.run([
            "powershell", "-NoProfile", "-Command", ps_cmd
        ], capture_output=True, text=True, check=False)
        out = completed.stdout.strip()
        if not out:
            return []
        # PowerShell returns either an object or an array; print raw lines
        return out
    except Exception:
        return None


def tail_log(lines=20):
    if not os.path.exists(LOG_FILE):
        print(f"Log file not found: {LOG_FILE}")
        return
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            buf = f.readlines()
        for line in buf[-lines:]:
            sys.stdout.write(line)
    except Exception as e:
        print(f"Error reading log file: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tail', type=int, default=20, help='Show last N log lines')
    args = ap.parse_args()

    print('Checking for mcp_server.py process...')

    found = find_process_psutil()
    if found is None:
        # psutil not installed; try PowerShell on Windows
        if os.name == 'nt':
            ps_out = find_process_powershell()
            if ps_out is None:
                print('Could not query processes (no psutil and PowerShell failed).')
                print('Install psutil: pip install psutil')
                sys.exit(3)
            if ps_out == '':
                print('No mcp_server.py process found (PowerShell).')
                sys.exit(2)
            print('Process found (PowerShell output):')
            print(ps_out)
            print('\nLast log lines (if present):')
            tail_log(args.tail)
            sys.exit(0)
        else:
            print('psutil not installed and no platform-specific fallback available.')
            print('Install psutil: pip install psutil')
            sys.exit(3)

    if not found:
        print('No mcp_server.py process found (psutil).')
        sys.exit(2)

    print('Found MCP server process(es):')
    for pid, cmd in found:
        print(f'  PID={pid} CMD={cmd}')

    print('\nLast log lines (if present):')
    tail_log(args.tail)
    sys.exit(0)


if __name__ == '__main__':
    main()
