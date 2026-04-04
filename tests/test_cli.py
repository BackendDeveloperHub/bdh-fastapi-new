from __future__ import annotations

import sys
from pathlib import Path

import pytest

from fastapi_new import cli


def test_rejects_invalid_project_name(tmp_path: Path) -> None:
    options = cli.ScaffoldOptions(project_name="bad name", output_dir=tmp_path)
    with pytest.raises(ValueError):
        cli.create_project(options)


def test_create_default_project(tmp_path: Path) -> None:
    options = cli.ScaffoldOptions(project_name="demo", output_dir=tmp_path, plain=True)
    root = cli.create_project(options)

    assert root.exists()
    assert (root / "app" / "main.py").exists()
    main_content = (root / "app" / "main.py").read_text(encoding="utf-8")
    assert "from app.routers import users" in main_content
    assert "FastAPI(" in main_content


def test_create_minimal_template(tmp_path: Path) -> None:
    options = cli.ScaffoldOptions(
        project_name="minimalproj",
        output_dir=tmp_path,
        template="minimal",
        plain=True,
    )
    root = cli.create_project(options)

    assert (root / "app" / "main.py").exists()
    assert not (root / "app" / "routers" / "users.py").exists()


def test_create_admin_template(tmp_path: Path) -> None:
    options = cli.ScaffoldOptions(
        project_name="adminproj",
        output_dir=tmp_path,
        admin_mode=True,
        plain=True,
    )
    root = cli.create_project(options)

    assert (root / "app" / "admin.py").exists()
    requirements = (root / "requirements.txt").read_text(encoding="utf-8")
    assert "sqladmin" in requirements


def test_parse_api_admin_template_sets_admin() -> None:
    args = cli.parse_args(["myproj", "--template", "api-admin"])
    options = cli.namespace_to_options(args)
    assert options.admin_mode is True
    assert options.template == "api"


def test_validate_ai_code_rejects_unsafe() -> None:
    ok, reason = cli.validate_ai_code("import os\nos.system('rm -rf /')")
    assert ok is False
    assert "security policy" in reason


def test_validate_ai_code_accepts_fastapi() -> None:
    code = "from fastapi import FastAPI\napp = FastAPI()\n"
    ok, reason = cli.validate_ai_code(code)
    assert ok is True
    assert reason == "ok"


def test_cli_main_returns_1_on_existing_project(tmp_path: Path) -> None:
    (tmp_path / "dup").mkdir()
    rc = cli.main(["dup", "--output-dir", str(tmp_path), "--plain"])
    assert rc == 1


def test_cli_main_happy_path(tmp_path: Path) -> None:
    rc = cli.main(["okproj", "--output-dir", str(tmp_path), "--plain", "--yes", "--no-network"])
    assert rc == 0
    assert (tmp_path / "okproj" / "app" / "main.py").exists()


def test_generated_main_importable(tmp_path: Path) -> None:
    options = cli.ScaffoldOptions(project_name="runproj", output_dir=tmp_path, plain=True)
    root = cli.create_project(options)

    sys.path.insert(0, str(root))
    __import__("app.main")
    sys.path.pop(0)
