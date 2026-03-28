import os
import sys
import argparse
import urllib.request
import urllib.error
import json

# ── Boilerplate Content ─────────────────────────────────────────────

MAIN_PY = '''from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="My FastAPI App",
    description="Built with bdh-fastapi-new CLI",
    version="1.0.0"
)

app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
'''

MAIN_PY_ADMIN = '''from fastapi import FastAPI
from app.routers import users
from app.database import engine
from app.admin import UserAdmin
from sqladmin import Admin

app = FastAPI(
    title="My FastAPI App",
    description="Built with bdh-fastapi-new CLI",
    version="1.0.0"
)

# Admin Panel → /admin
admin = Admin(app, engine)
admin.add_view(UserAdmin)

# Routers
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
'''

ADMIN_PY = '''from sqladmin import ModelView
from app.models.user import User

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
'''

DATABASE_PY = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

USERS_ROUTER = '''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_users(db: Session = Depends(get_db)):
    """Get all users."""
    return {"users": []}

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    return {"user_id": user_id}
'''

USER_MODEL = '''from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
'''

USER_SCHEMA = '''from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
'''

USER_CRUD = '''from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
'''

REQUIREMENTS = '''fastapi
uvicorn[standard]
sqlalchemy
python-dotenv
pydantic[email]
'''

REQUIREMENTS_ADMIN = '''fastapi
uvicorn[standard]
sqlalchemy
python-dotenv
pydantic[email]
sqladmin
'''

GITIGNORE = '''venv/
__pycache__/
*.pyc
.env
*.db
.DS_Store
'''

ENV_FILE = '''DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
'''

README_TEMPLATE = '''# {project_name}

> Built with [bdh-fastapi-new](https://pypi.org/project/bdh-fastapi-new/) CLI

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

- GET / -> Health check
- GET /docs -> Swagger UI
{admin_line}
'''

# ── Colors ─────────────────────────────────────────────────────────

CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

# ── Config ─────────────────────────────────────────────────────────

CONFIG_PATH = os.path.expanduser("~/.bdh_fastapi_config.json")

def save_api_key(api_key: str):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"groq_api_key": api_key}, f)

def load_api_key():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("groq_api_key")
    return None

# ── AI Generator ───────────────────────────────────────────────────

def generate_with_groq(api_key: str, description: str, project_name: str):
    print(f"\n{CYAN}AI generating your FastAPI backend...{RESET}\n")

    prompt = f"""You are a FastAPI expert. Generate production-ready FastAPI backend code for: "{description}"

Return ONLY a JSON object (no markdown, no explanation):
{{
  "router": "complete router file content",
  "model": "complete SQLAlchemy model file content",
  "schema": "complete Pydantic schema file content",
  "crud": "complete CRUD operations file content",
  "main_include": "e.g: from app.routers import posts"
}}"""

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.3
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content.strip())
    except Exception as e:
        print(f"{RED}AI Error: {e} - using default template{RESET}")
        return None

# ── Banner ─────────────────────────────────────────────────────────

def banner():
    print(f"""
{CYAN}{BOLD}  bdh-fastapi-new v2.0{RESET}
{DIM}  AI-Powered FastAPI Generator by BackendDeveloperHub{RESET}
""")

def print_tree(project_name, admin_mode=False):
    print(f"\n{CYAN}  {project_name}/{RESET}")
    print(f"  {CYAN}app/{RESET}")
    print(f"  {GREEN}  main.py{RESET}")
    print(f"  {GREEN}  database.py{RESET}")
    if admin_mode:
        print(f"  {YELLOW}  admin.py{RESET}")
    print(f"  {CYAN}  routers/{RESET}")
    print(f"  {CYAN}  models/{RESET}")
    print(f"  {CYAN}  schemas/{RESET}")
    print(f"  {CYAN}  crud/{RESET}")
    print(f"  {YELLOW}  .env{RESET}")
    print(f"  {YELLOW}  requirements.txt{RESET}")

# ── Core Generator ─────────────────────────────────────────────────

def create_project(project_name: str, ai_mode: bool = False, admin_mode: bool = False):
    banner()

    if os.path.exists(project_name):
        print(f"{RED}'{project_name}' already exists!{RESET}")
        sys.exit(1)

    ai_data = None
    if ai_mode:
        api_key = load_api_key()
        if not api_key:
            print(f"{YELLOW}Enter Groq API key:{RESET} ", end="")
            api_key = input().strip()
            save_api_key(api_key)
            print(f"{GREEN}API key saved!{RESET}")

        print(f"\n{CYAN}Describe your API:{RESET} ", end="")
        description = input().strip()

        if description:
            ai_data = generate_with_groq(api_key, description, project_name)

    print(f"{BOLD}Creating: {CYAN}{project_name}{RESET}\n")

    folders = [
        f"{project_name}/app/routers",
        f"{project_name}/app/models",
        f"{project_name}/app/schemas",
        f"{project_name}/app/crud",
    ]

    router_name    = "generated" if ai_data else "users"
    router_content = ai_data.get("router", USERS_ROUTER) if ai_data else USERS_ROUTER
    model_content  = ai_data.get("model", USER_MODEL) if ai_data else USER_MODEL
    schema_content = ai_data.get("schema", USER_SCHEMA) if ai_data else USER_SCHEMA
    crud_content   = ai_data.get("crud", USER_CRUD) if ai_data else USER_CRUD
    main_content   = MAIN_PY_ADMIN if admin_mode else MAIN_PY
    req_content    = REQUIREMENTS_ADMIN if admin_mode else REQUIREMENTS
    admin_line     = "- GET /admin -> Admin Panel" if admin_mode else ""

    files = {
        f"{project_name}/app/__init__.py": "",
        f"{project_name}/app/main.py": main_content,
        f"{project_name}/app/database.py": DATABASE_PY,
        f"{project_name}/app/routers/__init__.py": "",
        f"{project_name}/app/routers/{router_name}.py": router_content,
        f"{project_name}/app/models/__init__.py": "",
        f"{project_name}/app/models/{router_name}.py": model_content,
        f"{project_name}/app/schemas/__init__.py": "",
        f"{project_name}/app/schemas/{router_name}.py": schema_content,
        f"{project_name}/app/crud/__init__.py": "",
        f"{project_name}/app/crud/{router_name}.py": crud_content,
        f"{project_name}/.env": ENV_FILE,
        f"{project_name}/.gitignore": GITIGNORE,
        f"{project_name}/requirements.txt": req_content,
        f"{project_name}/README.md": README_TEMPLATE.format(
            project_name=project_name,
            admin_line=admin_line
        ),
    }

    if admin_mode:
        files[f"{project_name}/app/admin.py"] = ADMIN_PY

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)

    print_tree(project_name, admin_mode)

    flags = []
    if ai_data:
        flags.append(f"{GREEN}AI Generated{RESET}")
    if admin_mode:
        flags.append(f"{YELLOW}Admin Panel{RESET}")
    if not flags:
        flags.append(f"{CYAN}Default Template{RESET}")

    print(f"\n{GREEN}{BOLD}'{project_name}' ready! {' + '.join(flags)}{RESET}")

    admin_note = f"\n  {YELLOW}Admin -> http://localhost:8000/admin{RESET}" if admin_mode else ""
    print(f"""
  cd {project_name}
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload
{admin_note}
  {DIM}Swagger -> http://localhost:8000/docs{RESET}
""")

def main():
    parser = argparse.ArgumentParser(
        prog="bdh-fastapi-new",
        description="AI-Powered FastAPI Generator by BackendDeveloperHub"
    )
    parser.add_argument("project_name", help="Project name")
    parser.add_argument("--ai", action="store_true", help="AI-powered code generation")
    parser.add_argument("--admin", action="store_true", help="Include SQLAdmin panel")
    parser.add_argument("--config", metavar="API_KEY", help="Save Groq API key")

    args = parser.parse_args()

    if args.config:
        save_api_key(args.config)
        print(f"{GREEN}Groq API key saved!{RESET}")
        return

    create_project(args.project_name, ai_mode=args.ai, admin_mode=args.admin)

if __name__ == "__main__":
    main()
