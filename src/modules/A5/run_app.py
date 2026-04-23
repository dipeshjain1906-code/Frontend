"""Unified process runner for MedTrackPro.

Starts Flask API as a background child process, waits for readiness,
then starts Streamlit in the foreground.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


def _terminate_process(proc: Optional[subprocess.Popen], name: str) -> None:
    if proc is None or proc.poll() is not None:
        return

    try:
        proc.terminate()
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        print(f"[run_app] {name} did not terminate in time; killing.")
        proc.kill()
        proc.wait(timeout=5)
    except Exception as exc:  # pragma: no cover - defensive cleanup
        print(f"[run_app] Failed to stop {name}: {exc}")


def main() -> int:
    base_dir = Path(__file__).resolve().parent

    flask_port = os.getenv("FLASK_PORT", "8000")
    streamlit_port = os.getenv("STREAMLIT_PORT", "8501")
    startup_delay = float(os.getenv("FLASK_STARTUP_DELAY", "3"))

    python_executable = sys.executable
    flask_script = str(base_dir / "flask_app.py")
    streamlit_script = str(base_dir / "main.py")

    env = os.environ.copy()
    # Ensure frontend can resolve local backend service URL.
    env.setdefault("API_BASE_URL", f"http://127.0.0.1:{flask_port}/api")

    flask_proc: Optional[subprocess.Popen] = None
    streamlit_proc: Optional[subprocess.Popen] = None

    def _shutdown(signum=None, frame=None):  # noqa: ANN001,ANN202
        print("[run_app] Shutdown requested. Stopping child processes...")
        _terminate_process(streamlit_proc, "Streamlit")
        _terminate_process(flask_proc, "Flask")

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        print(f"[run_app] Starting Flask on port {flask_port}...")
        flask_proc = subprocess.Popen(
            [python_executable, flask_script],
            cwd=base_dir,
            env={**env, "FLASK_PORT": flask_port},
        )

        time.sleep(startup_delay)

        if flask_proc.poll() is not None:
            print("[run_app] Flask process exited during startup.")
            return 1

        print(f"[run_app] Starting Streamlit on port {streamlit_port}...")
        streamlit_proc = subprocess.Popen(
            [
                python_executable,
                "-m",
                "streamlit",
                "run",
                streamlit_script,
                "--server.port",
                streamlit_port,
                "--server.address",
                "0.0.0.0",
            ],
            cwd=base_dir,
            env=env,
        )

        # Keep parent alive while watching both processes.
        while True:
            if flask_proc.poll() is not None:
                print("[run_app] Flask stopped unexpectedly; shutting down Streamlit.")
                return 1

            if streamlit_proc.poll() is not None:
                print("[run_app] Streamlit stopped; shutting down Flask.")
                return streamlit_proc.returncode or 0

            time.sleep(1)

    except Exception as exc:
        print(f"[run_app] Fatal startup error: {exc}")
        return 1
    finally:
        _shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
