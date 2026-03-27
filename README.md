# ⚡ bdh-fastapi-new

> 🚀 FastAPI Project Generator CLI — by BackendDeveloperHub (BDH)

Create a production-ready FastAPI project in seconds — like `create-vite` but for FastAPI ⚡

---

## 📦 Install

```bash
pip install bdh-fastapi-new

🚀 Usage
Bash
bdh-fastapi-new my-project


⚡ What you get
✅ Clean project structure (routers, models, schemas, CRUD)
✅ SQLAlchemy + dotenv setup
✅ Ready-to-run FastAPI app
✅ Swagger docs enabled (/docs)



📁 Project Structure

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


▶️ Run the project
Bash
cd my-project
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
👉 Open: http://localhost:8000/docs⁠� 🔥



🐧 Linux / 🍎 macOS / Termux
Bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
👉 Open: http://localhost:8000/docs⁠� 🔥



⭐ Support
If this tool helps you, consider giving a ⭐ on GitHub 🙌
It motivates me to improve and add more features!


🚧 Roadmap
[ ] Docker support 🐳
[ ] Authentication (JWT) 🔐
[ ] CLI options (--docker, --auth)
[ ] AI-based code generation 🤖









