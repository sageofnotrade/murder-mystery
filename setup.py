from setuptools import setup, find_packages

setup(
    name="murder-mystery",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pytest",
        "pytest-asyncio",
        "pytest-flask",
        "pydantic",
        "pydantic-ai",
        "openai",
        "supabase",
        "redis",
        "fastapi",
        "flask-jwt-extended"
    ],
) 