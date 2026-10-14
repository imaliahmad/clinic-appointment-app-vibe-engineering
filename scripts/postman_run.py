"""Run the Postman collection against a fresh database and a temporary server.

Usage (from the project root):
    uv run python scripts/postman_run.py

Steps:
1. Delete instance/postman.db and recreate it with `init-db` and `seed`.
2. Start the Flask server on port 5001 using that database.
3. Run the collection with Newman (npx newman).
4. Stop the server and exit with Newman's exit code (0 = all passed).

The server runs on its own port, so your normal dev server on 5000 is not affected.
Needs Node.js (for npx).
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "instance" / "postman.db"
COLLECTION = ROOT / "postman" / "clinic.postman_collection.json"
ENVIRONMENT = ROOT / "postman" / "local.postman_environment.json"
HOST = "127.0.0.1"
PORT = 5001
STARTUP_TIMEOUT_SECONDS = 30


def run_flask_command(env: dict[str, str], *args: str) -> None:
    """Run a Flask CLI command (e.g. init-db) with the current Python environment."""
    command = [sys.executable, "-m", "flask", "--app", "app", *args]
    print(f"$ flask {' '.join(args)}")
    result = subprocess.run(command, cwd=ROOT, env=env)
    if result.returncode != 0:
        sys.exit(f"Command failed: flask {' '.join(args)}")


def wait_for_port(host: str, port: int, timeout: float) -> bool:
    """Return True once something accepts connections on host:port."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


def main() -> int:
    npx = shutil.which("npx")
    if npx is None:
        sys.exit("npx not found. Install Node.js to run Newman.")
    if port_in_use(HOST, PORT):
        sys.exit(f"Port {PORT} is already in use. Stop whatever is running there and try again.")

    env = os.environ.copy()
    env["CLINIC_DATABASE"] = str(DB_PATH)
    env.setdefault("SECRET_KEY", "postman-run")

    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    run_flask_command(env, "init-db")
    run_flask_command(env, "seed")

    print(f"Starting server on http://{HOST}:{PORT} with {DB_PATH.name} ...")
    server = subprocess.Popen(
        [sys.executable, "-m", "flask", "--app", "app", "run", "--host", HOST, "--port", str(PORT)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_port(HOST, PORT, STARTUP_TIMEOUT_SECONDS):
            print("Server did not start. Run it by hand to see the error:")
            print(f"  $env:CLINIC_DATABASE='{DB_PATH}'; uv run flask --app app run --port {PORT}")
            return 1

        newman = subprocess.run(
            [
                npx, "--yes", "newman@6", "run", str(COLLECTION),
                "-e", str(ENVIRONMENT),
                "--env-var", f"baseUrl=http://{HOST}:{PORT}",
            ],
            cwd=ROOT,
        )
        print("\nPostman run: " + ("PASSED" if newman.returncode == 0 else "FAILED"))
        return newman.returncode
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    sys.exit(main())
