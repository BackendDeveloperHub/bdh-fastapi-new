import os
import sys
import argparse

# ── Boilerplate Content ─────────────────────────────────────────────

MAIN_PY = '''from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="My FastAPI App",
    description="Built with bdh-fastapi-new CLI",
    version="1.0.0"
)

# Include routers
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}
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

USERS_ROUTER = '''from fastapi import APIRouter, Depends, HTTPException
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

USER_SCHEMA = '''from pydantic import BaseModel, EmailStr

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

> Built with [fastapi-new](https://github.com/yourrepo/fastapi-new) CLI ⚡

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate
venv\\Scripts\\activate   # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
uvicorn app.main:app --reload
```

## 📍 Endpoints

- `GET /` → Health check
- `GET /users` → Get all users
- `GET /users/{{id}}` → Get user by ID
- `GET /docs` → Swagger UI

## 📁 Structure

```
{project_name}/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   └── crud/
├── .env
├── requirements.txt
└── README.md
```
'''

# ── Colors ─────────────────────────────────────────────────────────

CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

def banner():
    print(f"""
{CYAN}{BOLD}
  ███████╗ █████╗ ███████╗████████╗ █████╗ ██████╗ ██╗    ███╗   ██╗███████╗██╗    ██╗
  ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║    ████╗  ██║██╔════╝██║    ██║
  █████╗  ███████║███████╗   ██║   ███████║██████╔╝██║    ██╔██╗ ██║█████╗  ██║ █╗ ██║
  ██╔══╝  ██╔══██║╚════██║   ██║   ██╔══██║██╔═══╝ ██║    ██║╚██╗██║██╔══╝  ██║███╗██║
  ██║     ██║  ██║███████║   ██║   ██║  ██║██║     ██║    ██║ ╚████║███████╗╚███╔███╔╝
  ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝
{RESET}{DIM}  ⚡ bdh-fastapi-new — FastAPI Project Generator by BackendDeveloperHub{RESET}
""")

def print_tree(project_name):
    print(f"\n{CYAN}📁 {project_name}/{RESET}")
    tree = [
        ("├── app/", CYAN),
        ("│   ├── __init__.py", DIM),
        ("│   ├── main.py", GREEN),
        ("│   ├── database.py", GREEN),
        ("│   ├── routers/", CYAN),
        ("│   │   ├── __init__.py", DIM),
        ("│   │   └── users.py", GREEN),
        ("│   ├── models/", CYAN),
        ("│   │   ├── __init__.py", DIM),
        ("│   │   └── user.py", GREEN),
        ("│   ├── schemas/", CYAN),
        ("│   │   ├── __init__.py", DIM),
        ("│   │   └── user.py", GREEN),
        ("│   └── crud/", CYAN),
        ("│       ├── __init__.py", DIM),
        ("│       └── user.py", GREEN),
        ("├── .env", YELLOW),
        ("├── .gitignore", DIM),
        ("├── requirements.txt", YELLOW),
        ("└── README.md", DIM),
    ]
    for line, color in tree:
        print(f"  {color}{line}{RESET}")

# ── Core Generator ──────────────────────────────────────────────────

def create_project(project_name: str):
    banner()

    if os.path.exists(project_name):
        print(f"{RED}❌ '{project_name}' already exists!{RESET}")
        sys.exit(1)

    print(f"{BOLD}Creating project: {CYAN}{project_name}{RESET}\n")

    folders = [
        f"{project_name}/app/routers",
        f"{project_name}/app/models",
        f"{project_name}/app/schemas",
        f"{project_name}/app/crud",
    ]

    files = {
        f"{project_name}/app/__init__.py": "",
        f"{project_name}/app/main.py": MAIN_PY,
        f"{project_name}/app/database.py": DATABASE_PY,
        f"{project_name}/app/routers/__init__.py": "",
        f"{project_name}/app/routers/users.py": USERS_ROUTER,
        f"{project_name}/app/models/__init__.py": "",
        f"{project_name}/app/models/user.py": USER_MODEL,
        f"{project_name}/app/schemas/__init__.py": "",
        f"{project_name}/app/schemas/user.py": USER_SCHEMA,
        f"{project_name}/app/crud/__init__.py": "",
        f"{project_name}/app/crud/user.py": USER_CRUD,
        f"{project_name}/.env": ENV_FILE,
        f"{project_name}/.gitignore": GITIGNORE,
        f"{project_name}/requirements.txt": REQUIREMENTS,
        f"{project_name}/README.md": README_TEMPLATE.format(project_name=project_name),
    }

    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Create files
    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)

    # Show tree
    print_tree(project_name)

    # Success message
    print(f"""
{GREEN}{BOLD}✅ Project '{project_name}' created successfully!{RESET}

{BOLD}Next steps:{RESET}

  {CYAN}cd {project_name}{RESET}
  {CYAN}python -m venv venv{RESET}
  {CYAN}venv\\Scripts\\activate{RESET}        {DIM}# Windows{RESET}
  {CYAN}source venv/bin/activate{RESET}      {DIM}# Mac/Linux{RESET}
  {CYAN}pip install -r requirements.txt{RESET}
  {CYAN}uvicorn app.main:app --reload{RESET}

  {DIM}Then open → http://localhost:8000/docs 🚀{RESET}
""")

def main():
    parser = argparse.ArgumentParser(
        prog="bdh-fastapi-new",
        description="⚡ FastAPI Project Generator by BackendDeveloperHub"
    )
    parser.add_argument("project_name", help="Name of your FastAPI project")
    args = parser.parse_args()
    create_project(args.project_name)

if __name__ == "__main__":
    main()
