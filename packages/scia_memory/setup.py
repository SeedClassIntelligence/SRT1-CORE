"""SCIA Memory — Standalone installer."""
from setuptools import setup, find_packages

setup(
    name="scia-memory",
    version="2.1.0",
    description="SCIA adaptive memory system with reflex, regenerative, and multi-tier storage",
    author="William Darnell Jernigan IV",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "redis": ["redis>=5.0"],
        "api": ["fastapi>=0.110", "uvicorn>=0.27", "pydantic>=2.5", "aiohttp>=3.9"],
        "all": ["redis>=5.0", "fastapi>=0.110", "uvicorn>=0.27", "pydantic>=2.5", "aiohttp>=3.9"],
    },
)
