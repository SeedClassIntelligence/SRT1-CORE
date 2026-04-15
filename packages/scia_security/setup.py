"""SCIA Security Utilities — Standalone installer."""
from setuptools import setup, find_packages

setup(
    name="scia-security",
    version="2.1.0",
    description="SCIA security utilities — execution tracking, integrity validation",
    author="William Darnell Jernigan IV",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
)
