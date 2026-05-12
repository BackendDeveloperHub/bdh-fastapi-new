from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

VERSION = "2.2.0"
TEMPLATE_VERSION = "1"

ANSI = {
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}

SAFE_BANNER = """bdh-fastapi-new
FastAPI Project Generator by BackendDeveloperHub
"""

ASCII_BANNER = r"""
  ____  ____  _   _
 | __ )|  _ \| | | |
 |  _ \| | | | |_| |
 | |_) | |_| |  _  |
 |____/|____/|_| |_|

 FastAPI Project Generator
"""

MAIN_PY = """from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title=\"My FastAPI App\",
    description=\"Built with bdh-fastapi-new CLI\",
    version=\"1.0.0\",
)

app.include_router(users.router)


@app.get(\"/\")
async def root() -> dict[str, str]:
    return {\"message\": \"Hello FastAPI!\"}
"""

MAIN_PY_MINIMAL = """from fastapi import FastAPI

app = FastAPI(
    title=\"My FastAPI App\",
    description=\"Built with bdh-fastapi-new CLI\",
    version=\"1.0.0\",
)


@app.get(\"/\")
async def root() -> dict[str, str]:
    return {\"message\": \"Hello FastAPI!\"}
"""

MAIN_PY_ADMIN = """from fastapi import FastAPI
from sqladmin import Admin

from app.admin import UserAdmin
from app.database import engine
from app.routers import users

app = FastAPI(
    title=\"My FastAPI App\",
    description=\"Built with bdh-fastapi-new CLI\",
    version=\"1.0.0\",
)

admin = Admin(app, engine)
admin.add_view(UserAdmin)

app.include_router(users.router)


@app.get(\"/\")
async def root() -> dict[str, str]:
    return {\"message\": \"Hello FastAPI!\"}
"""

ADMIN_PY = """from sqladmin import ModelView

from app.models.user import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email]
    name = \"User\"
    name_plural = \"Users\"
    icon = \"fa-solid fa-user\"
"""

DATABASE_PY = """from collections.abc import Generator
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(\"DATABASE_URL\", \"sqlite:///./app.db\")

connect_args = {\"check_same_thread\": False} if DATABASE_URL.startswith(\"sqlite\") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

USERS_ROUTER = """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(prefix=\"/users\", tags=[\"Users\"])


@router.get(\"/\")
async def get_users(db: Session = Depends(get_db)) -> dict[str, list[dict[str, str]]]:
    _ = db
    return {\"users\": []}


@router.get(\"/{user_id}\")
async def get_user(user_id: int, db: Session = Depends(get_db)) -> dict[str, int]:
    _ = db
    return {\"user_id\": user_id}
"""

USER_MODEL = """from sqlalchemy import Column, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = \"users\"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
"""

USER_SCHEMA = """from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
"""

USER_CRUD = """from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
"""

REQUIREMENTS = """fastapi
uvicorn[standard]
sqlalchemy
python-dotenv
pydantic[email]
"""

REQUIREMENTS_ADMIN = """fastapi
uvicorn[standard]
sqlalchemy
python-dotenv
pydantic[email]
sqladmin
"""

GITIGNORE = """venv/
__pycache__/
*.pyc
.env
*.db
.DS_Store
.pytest_cache/
.mypy_cache/
.ruff_cache/
"""

ENV_FILE = """DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-me
"""

PYPROJECT_TEMPLATE = """[tool.ruff]
line-length = 100
target-version = \"py310\"

[tool.ruff.lint]
select = [\"E\", \"F\", \"I\", \"UP\", \"B\"]

[tool.pytest.ini_options]
addopts = \"-q\"
pythonpath = [\".\"]
"""

TEST_MAIN = """from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello FastAPI!"}


def test_users_list() -> None:
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == {"users": []}
"""

README_TEMPLATE = """# {project_name}

Built with [bdh-fastapi-new](https://pypi.org/project/bdh-fastapi-new/)
(template v{template_version}).

## Quick Start

### Windows

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

- GET / -> health check
- GET /docs -> Swagger UI
{users_line}{admin_line}

## Quality Checks

```bash
ruff check .
pytest
```
"""

UNSAFE_PATTERNS = [
    r"(?i)os\.system\(",
    r"(?i)subprocess\.",
    r"(?i)eval\(",
    r"(?i)exec\(",
    r"(?i)__import__\(",
    r"(?i)pickle\.loads\(",
]


@dataclass
class ScaffoldOptions:
    project_name: str
    output_dir: Path
    ai_mode: bool = False
    ai_description: str | None = None
    admin_mode: bool = False
    template: str = "api"
    template_version: str = TEMPLATE_VERSION
    no_color: bool = False
    plain: bool = False
    assume_yes: bool = False
    no_network: bool = False


def supports_color(no_color: bool = False) -> bool:
    if no_color or os.getenv("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def c(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{ANSI[color]}{text}{ANSI['reset']}"


def print_banner(color: bool, plain: bool) -> None:
    if plain:
        print(SAFE_BANNER)
        return
    banner = ASCII_BANNER
    if color:
        banner = c(ASCII_BANNER, "cyan", True)
    print(banner)


def sanitize_project_name(name: str) -> str:
    cleaned = name.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", cleaned):
        raise ValueError(
            "Invalid project name. Use letters, numbers, '-' or '_' and start with alphanumeric."
        )
    return cleaned


def validate_ai_code(api_code: str) -> tuple[bool, str]:
    if not api_code.strip():
        return False, "AI response was empty"

    try:
        ast.parse(api_code)
    except SyntaxError as exc:
        return False, f"AI code syntax error: {exc.msg}"

    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, api_code):
            return False, f"AI code rejected by security policy: {pattern}"

    if "FastAPI(" not in api_code:
        return False, "AI code missing FastAPI app declaration"

    return True, "ok"


def generate_from_bdh(description: str, timeout: int = 45) -> tuple[str | None, str]:
    payload = json.dumps({"prompt": f"Create a {description}"}).encode("utf-8")
    req = urllib.request.Request(
        "https://ai-api-builder.onrender.com/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:  # nosec B310
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return None, f"AI request failed: {exc}"
    except TimeoutError:
        return None, "AI request timed out"
    except json.JSONDecodeError:
        return None, "AI service returned invalid JSON"

    api_code = result.get("api_code", "")
    valid, reason = validate_ai_code(api_code)
    if not valid:
        return None, reason
    return api_code, "ok"


def build_files(options: ScaffoldOptions, main_content: str, project_name: str) -> dict[Path, str]:
    project_root = options.output_dir / project_name

    requirements_content = REQUIREMENTS_ADMIN if options.admin_mode else REQUIREMENTS

    files: dict[Path, str] = {
        project_root / ".env": ENV_FILE,
        project_root / ".gitignore": GITIGNORE,
        project_root / "requirements.txt": requirements_content,
        project_root / "README.md": README_TEMPLATE.format(
            project_name=project_name,
            template_version=options.template_version,
            users_line="- GET /users -> user routes\n" if options.template != "minimal" else "",
            admin_line="- GET /admin -> Admin Panel\n" if options.admin_mode else "",
        ),
        project_root / "pyproject.toml": PYPROJECT_TEMPLATE,
        project_root / "app" / "__init__.py": "",
        project_root / "app" / "main.py": main_content,
    }

    if options.template != "minimal":
        files.update(
            {
                project_root / "app" / "database.py": DATABASE_PY,
                project_root / "app" / "routers" / "__init__.py": "",
                project_root / "app" / "routers" / "users.py": USERS_ROUTER,
                project_root / "app" / "models" / "__init__.py": "",
                project_root / "app" / "models" / "user.py": USER_MODEL,
                project_root / "app" / "schemas" / "__init__.py": "",
                project_root / "app" / "schemas" / "user.py": USER_SCHEMA,
                project_root / "app" / "crud" / "__init__.py": "",
                project_root / "app" / "crud" / "user.py": USER_CRUD,
                project_root / "tests" / "test_main.py": TEST_MAIN,
            }
        )

    if options.admin_mode:
        files[project_root / "app" / "admin.py"] = ADMIN_PY

    return files


def create_project(options: ScaffoldOptions) -> Path:
    project_name = sanitize_project_name(options.project_name)
    project_root = options.output_dir / project_name

    if project_root.exists():
        raise FileExistsError(f"'{project_name}' already exists")

    color = supports_color(options.no_color)
    print_banner(color=color, plain=options.plain)
    print(c(f"Creating project: {project_name}", "bold", color))

    ai_main = None
    if options.ai_mode:
        if options.no_network:
            print(c("AI mode skipped: --no-network set", "yellow", color))
        else:
            description = options.ai_description
            if not description and not options.assume_yes:
                description = input("Describe your API: ").strip()
            if description:
                ai_main, reason = generate_from_bdh(description)
                if ai_main:
                    print(c("AI generation successful", "green", color))
                else:
                    print(c(f"AI fallback to safe template: {reason}", "yellow", color))

    if options.template == "minimal":
        main_content = ai_main or MAIN_PY_MINIMAL
    elif options.admin_mode:
        main_content = ai_main or MAIN_PY_ADMIN
    else:
        main_content = ai_main or MAIN_PY

    files = build_files(options, main_content, project_name)
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    print(c("Project created successfully.", "green", color))
    print("Next steps:")
    print(f"  cd {project_name}")
    print("  python -m venv venv")
    if os.name == "nt":
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  uvicorn app.main:app --reload")
    print("  Open http://127.0.0.1:8000/docs")

    return project_root


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bdh-fastapi-new",
        description="FastAPI scaffolder by BackendDeveloperHub",
    )
    parser.add_argument("project_name", help="Project name")
    parser.add_argument("--ai", action="store_true", help="Enable AI-generated main.py")
    parser.add_argument("--ai-description", help="Non-interactive prompt for AI mode")
    parser.add_argument("--admin", action="store_true", help="Include SQLAdmin panel")
    parser.add_argument(
        "--template",
        choices=["minimal", "api", "api-admin"],
        default="api",
        help="Scaffold template preset",
    )
    parser.add_argument("--output-dir", default=".", help="Destination directory")
    parser.add_argument("--template-version", default=TEMPLATE_VERSION, help="Template version")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--plain", action="store_true", help="Use plain output")
    parser.add_argument("--yes", action="store_true", help="Assume defaults and avoid prompts")
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Disable network calls (including AI)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser.parse_args(argv)


def namespace_to_options(args: argparse.Namespace) -> ScaffoldOptions:
    if args.admin and args.template == "minimal":
        raise ValueError("--admin cannot be combined with --template minimal")

    admin_mode = args.admin or args.template == "api-admin"
    template = "api" if args.template == "api-admin" else args.template
    return ScaffoldOptions(
        project_name=args.project_name,
        output_dir=Path(args.output_dir).resolve(),
        ai_mode=args.ai,
        ai_description=args.ai_description,
        admin_mode=admin_mode,
        template=template,
        template_version=args.template_version,
        no_color=args.no_color,
        plain=args.plain,
        assume_yes=args.yes,
        no_network=args.no_network,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    options = namespace_to_options(args)

    try:
        create_project(options)
    except (ValueError, FileExistsError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Aborted by user.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
