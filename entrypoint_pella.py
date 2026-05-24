"""
Entrypoint for pella to install uv and run uv
"""

#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def get_uv_path():
    """Find the uv executable path."""
    # Common pip installation locations
    candidates = [
        Path.home() / ".local" / "bin" / "uv",
        Path.home() / ".local" / "bin" / "uv.exe",
        Path(os.environ.get("APPDATA", "")) / "Python" / "Scripts" / "uv.exe",
        Path(sys.prefix) / "Scripts" / "uv.exe",
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return "uv"  # Fallback to system PATH

def install_uv():
    """Install uv using pip."""
    print("Installing uv via pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "uv"],
        check=True,
    )

def run_uv_command(*args):
    """Run a uv command with the located uv executable."""
    uv_path = get_uv_path()
    subprocess.run([uv_path, *args], check=True)

def main():
    # Check if uv is installed
    try:
        run_uv_command("--version")
    except (subprocess.CalledProcessError, FileNotFoundError):
        install_uv()

    # Run uv sync
    print("Running uv sync...")
    run_uv_command("sync")

    # Run uv run with any additional arguments
    print("Running uv run...")
    run_uv_command("run", "dt_archie")

if __name__ == "__main__":
    main()

