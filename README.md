# bdh-fastapi-new ⚡

> FastAPI Project Generator CLI — by BackendDeveloperHub (BDH)

## 🚀 Install (Global)

```bash
pip install -e .
```

## 💻 Usage

```bash
bdh-fastapi-new my-project
bdh-fastapi-new blog-api
bdh-fastapi-new ecommerce-backend
```

## 📁 Generated Structure

```
my-project/
├── app/
│   ├── main.py          ← Entry point
│   ├── database.py      ← SQLAlchemy setup
│   ├── routers/
│   │   └── users.py     ← Sample router
│   ├── models/
│   │   └── user.py      ← DB model
│   ├── schemas/
│   │   └── user.py      ← Pydantic schema
│   └── crud/
│       └── user.py      ← CRUD operations
├── .env
├── requirements.txt
└── README.md
```

## ⚡ After Generation

```bash
cd my-project
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open → http://localhost:8000/docs 🔥

![PyPI](https://img.shields.io/pypi/v/bdh-fastapi-new)




![Downloads](https://img.shields.io/pypi/dm/bdh-fastapi-new)




![License](https://img.shields.io/pypi/l/bdh-fastapi-new)