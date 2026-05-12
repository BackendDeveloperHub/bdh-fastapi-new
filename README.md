# bdh-fastapi-new

FastAPI project generator CLI by BackendDeveloperHub.

## Install

```bash
pip install bdh-fastapi-new
```

## Quick Usage

### Standard API scaffold

```bash
bdh-fastapi-new my-project
```

### Admin scaffold

```bash
bdh-fastapi-new my-project --template api-admin
```

### AI-assisted scaffold

```bash
bdh-fastapi-new my-project --ai --ai-description "task manager API"
```

## CLI Options

- `--template minimal|api|api-admin`: select scaffold preset
- `--output-dir PATH`: destination folder
- `--ai`: enable AI main.py generation with safe fallback
- `--ai-description TEXT`: non-interactive AI prompt
- `--no-network`: disable network calls (AI off)
- `--no-color`: disable ANSI colors
- `--plain`: plain text output
- `--yes`: non-interactive mode
- `--template-version VERSION`: stamp generated README with template version
- `--version`: show CLI version

## Generated Project Features

- `app.main` import-safe entrypoint (`uvicorn app.main:app --reload`)
- Layered structure (`routers`, `models`, `schemas`, `crud`)
- `.env` and SQLAlchemy session boilerplate
- Optional SQLAdmin integration
- Local quality baseline (`pyproject.toml` with Ruff and pytest config)

## Run Generated Project

### Windows

```bash
cd my-project
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Linux / macOS

```bash
cd my-project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Development

```bash
pip install -e .[dev]
ruff check .
mypy fastapi_new
pytest
bandit -q -r fastapi_new
```

## Security Notes

- AI code is validated with syntax and unsafe-pattern checks.
- AI responses automatically fall back to the safe built-in template when validation fails.
- Use `--no-network` when you need deterministic offline scaffolding.
