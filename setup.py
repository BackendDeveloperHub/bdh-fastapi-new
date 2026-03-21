from setuptools import setup, find_packages

setup(
    name="bdh-fastapi-new",
    version="1.0.0",
    description="⚡ FastAPI Project Generator CLI — by BackendDeveloperHub",
    author="BackendDeveloperHub",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bdh-fastapi-new=fastapi_new.cli:main",
        ],
    },
    python_requires=">=3.8",
)
