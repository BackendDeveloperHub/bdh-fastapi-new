# ⚡ bdh-fastapi-new

> 🚀 FastAPI Project Generator CLI — by BackendDeveloperHub (BDH)

Create a production-ready FastAPI project in seconds — like `create-vite` but for FastAPI ⚡

--


# bdh-fastapi-new

> Scaffold a production-ready FastAPI project in seconds.

# BDH FastAPI New 🚀
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Downloads](https://img.shields.io/pypi/dm/bdh-fastapi-new)
![Version](https://img.shields.io/pypi/v/bdh-fastapi-new)
![Python](https://img.shields.io/pypi/pyversions/bdh-fastapi-new)
[project]
requires-python = ">=3.8"
[![Made by BDH](https://img.shields.io/badge/Made%20by-BackendDeveloperHub-blueviolet)](https://github.com/BackendDeveloperHub)
[project]
requires-python = ">=3.8"

FastAPI Project Generator CLI ⚡

## 📊 Stats
[View Download Stats](https://pypistats.org/packages/bdh-fastapi-new)
## ⚡ Install

```bash
pip install bdh-fastapi-new
```

---

## 🚀 Usage

### 🔹 Normal Project
```bash
bdh-fastapi-new my-project
```
Clean FastAPI structure with SQLAlchemy, dotenv, and Swagger docs.

### 🤖 AI Endpoint Generation
```bash
bdh-fastapi-new my-project --ai
```
Auto-generates API endpoints using AI — powered by BDH's AI server.

### 🔐 Admin Panel
```bash
bdh-fastapi-new my-project --admin
```
Scaffolds project with a ready-to-use `admin.py`.

---

## ✅ What You Get

```
my-project/
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

---

## ▶️ Run the Project

**Windows:**
```bash
cd my-project
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Linux / macOS / Termux:**
```bash
cd my-project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

👉 Open: http://localhost:8000/docs 🔥

---

## 🚧 Roadmap

- [ ] Docker support 🐳
- [ ] JWT Authentication 🔐
- [ ] More CLI options
- [ ] Enhanced AI generation 🤖

---

## ⭐ Support

If this tool helps you, give a ⭐ on GitHub — it motivates us to keep building!

---

## 🛠️ Made by

[BackendDeveloperHub (BDH)](https://github.com/BackendDeveloperHub) — Learn Backend. Together.






