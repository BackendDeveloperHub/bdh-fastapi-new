from __future__ import annotations

import importlib.util
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from fastapi_new import cli


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location("scaffold_app", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_project_module_loads(tmp_path: Path) -> None:
    options = cli.ScaffoldOptions(project_name="runtimeproj", output_dir=tmp_path, plain=True)
    root = cli.create_project(options)

    module = _load_module(root / "app" / "main.py")
    assert hasattr(module, "app")


def test_generated_app_serves_endpoints(tmp_path: Path) -> None:
    options = cli.ScaffoldOptions(project_name="httpproj", output_dir=tmp_path, plain=True)
    root = cli.create_project(options)

    port = _find_free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                with urlopen(f"http://127.0.0.1:{port}/", timeout=1) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(0.25)
        else:
            raise AssertionError("Server did not start in time")

        with urlopen(f"http://127.0.0.1:{port}/", timeout=2) as response:
            assert response.status == 200
            body = json.loads(response.read().decode("utf-8"))
            assert body == {"message": "Hello FastAPI!"}

        with urlopen(f"http://127.0.0.1:{port}/users/", timeout=2) as response:
            assert response.status == 200
            body = json.loads(response.read().decode("utf-8"))
            assert body == {"users": []}

    finally:
        proc.terminate()
        proc.wait(timeout=10)
