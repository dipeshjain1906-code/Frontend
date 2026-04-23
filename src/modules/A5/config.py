import os


def _normalized_base_url() -> str:
    # Preferred explicit API URL (works in cloud/local)
    configured = os.getenv("API_BASE_URL")
    if configured:
        return configured.rstrip("/")

    # Fallback: compose from backend host/port
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = os.getenv("FLASK_PORT", "8000")
    return f"http://{host}:{port}/api"


BASE_URL = _normalized_base_url()
