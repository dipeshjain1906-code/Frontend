"""Backend process manager for Streamlit-first deployments.

Streamlit Community Cloud only starts the Streamlit entrypoint. This module
attempts to start the Flask API when missing, but never crashes Streamlit.
"""

from __future__ import annotations

import atexit
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import requests

_BACKEND_PROC: Optional[subprocess.Popen] = None
_LOCK = threading.Lock()


def _api_base_url() -> str:
    configured = os.getenv("API_BASE_URL")
    if configured:
        return configured.rstrip("/")

    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = os.getenv("FLASK_PORT", "8000")
    return f"http://{host}:{port}/api"


def _is_backend_healthy(base_url: str, timeout: float = 1.5) -> bool:
    try:
        res = requests.get(f"{base_url}/patients", timeout=timeout)
        return res.status_code in (200, 404)
    except Exception:
        return False


def _stop_backend() -> None:
    global _BACKEND_PROC

    proc = _BACKEND_PROC
    if proc is None or proc.poll() is not None:
        return

    try:
        proc.terminate()
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    finally:
        _BACKEND_PROC = None


def ensure_backend_running() -> bool:
    """Start Flask API when Streamlit is the only launched process.

    Returns True if backend is reachable, False otherwise.
    This function must not raise startup exceptions in Streamlit Cloud.
    """
    global _BACKEND_PROC

    if os.getenv("DISABLE_INTERNAL_FLASK", "0") == "1":
        return _is_backend_healthy(_api_base_url())

    with _LOCK:
        base_url = _api_base_url()

        if _is_backend_healthy(base_url):
            return True

        if _BACKEND_PROC is not None and _BACKEND_PROC.poll() is None:
            return _is_backend_healthy(base_url)

        app_dir = Path(__file__).resolve().parent
        flask_script = str(app_dir / "flask_app.py")
        env = os.environ.copy()
        env.setdefault("FLASK_PORT", os.getenv("FLASK_PORT", "8000"))

        try:
            _BACKEND_PROC = subprocess.Popen(
                [sys.executable, flask_script],
                cwd=app_dir,
                env=env,
            )
        except Exception as exc:
            print(f"[backend_manager] Failed to spawn Flask: {exc}")
            return False

        max_wait = float(os.getenv("BACKEND_HEALTH_TIMEOUT", "20"))
        deadline = time.time() + max_wait
        while time.time() < deadline:
            if _BACKEND_PROC.poll() is not None:
                print("[backend_manager] Flask exited during startup; app will continue without backend.")
                return False
            if _is_backend_healthy(base_url):
                return True
            time.sleep(0.4)

        print("[backend_manager] Flask did not become healthy before timeout.")
        return False


atexit.register(_stop_backend)
