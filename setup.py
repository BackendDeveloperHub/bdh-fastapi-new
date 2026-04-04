from setuptools import find_packages, setup

setup(
    name="bdh-fastapi-new",
    version="2.2.0",
    description="FastAPI Project Generator CLI by BackendDeveloperHub",
    author="BackendDeveloperHub",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "dev": [
            "bandit[toml]>=1.7.0",
            "fastapi",
            "mypy>=1.8.0",
            "pydantic",
            "python-dotenv",
            "pytest>=8.0.0",
            "ruff>=0.6.0",
            "sqladmin",
            "sqlalchemy",
            "uvicorn",
        ],
    },
    entry_points={
        "console_scripts": [
            "bdh-fastapi-new=fastapi_new.cli:main",
        ],
    },
    python_requires=">=3.10",
)
