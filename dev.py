"""
Cross-platform dev runner: starts FastAPI backend and static frontend together.

Usage
-----
macOS/Linux:  python3 dev.py
Windows:      py -3 dev.py

Environment variables (optional)
--------------------------------
PORT_BACKEND  default 8000
PORT_FRONTEND default 5500
"""
import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
PORT_BACKEND = os.getenv("PORT_BACKEND", "8000")
PORT_FRONTEND = os.getenv("PORT_FRONTEND", "5500")

IS_WINDOWS = platform.system() == "Windows"
VENV_DIR = BACKEND / ".venv"
BIN_DIR = "Scripts" if IS_WINDOWS else "bin"
VENV_PY = VENV_DIR / BIN_DIR / ("python.exe" if IS_WINDOWS else "python")


def run(cmd, cwd=None):
    return subprocess.Popen(cmd, cwd=cwd)


def ensure_venv():
    if not VENV_PY.exists():
        print("[dev.py] Creating virtual environment and installing dependencies…")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
        subprocess.check_call([str(VENV_PY), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
        subprocess.check_call([str(VENV_PY), "-m", "pip", "install", "-r", str(BACKEND / "requirements.txt")])
    else:
        # Optional: keep pip up to date silently
        try:
            subprocess.check_call([str(VENV_PY), "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL)
        except Exception:
            pass


def main() -> int:
    ensure_venv()

    procs = []
    try:
        # Start backend (use venv python so uvicorn & deps are available)
        procs.append(
            run([
                str(VENV_PY), "-m", "uvicorn",
                "--app-dir", str(BACKEND),
                "app.main:app", "--reload", "--port", PORT_BACKEND,
            ], cwd=BACKEND)
        )

        # Start frontend (use the interpreter running dev.py)
        procs.append(
            run([sys.executable, "-m", "http.server", PORT_FRONTEND], cwd=FRONTEND)
        )

        print(f"\nBackend  ➜ http://localhost:{PORT_BACKEND}")
        print(f"Frontend ➜ http://localhost:{PORT_FRONTEND}")
        print("Press Ctrl+C to stop both.\n")

        # Keep the parent alive while both children are running
        while True:
            statuses = [p.poll() for p in procs]
            if any(s is not None for s in statuses):
                break
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            if p and p.poll() is None:
                p.terminate()
        # Give them a moment to exit, then force kill if needed
        time.sleep(1.0)
        for p in procs:
            if p and p.poll() is None:
                p.kill()
        for p in procs:
            try:
                p.wait(timeout=2)
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
