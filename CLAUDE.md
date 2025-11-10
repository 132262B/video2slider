# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`video2slider` is a Python project for converting videos into slides/presentations. This is a new project with minimal initial structure.

## Environment Setup

This project uses **uv** for Python package management with Python 3.13.

```bash
# Create virtual environment (already done)
uv venv --python 3.13

# Sync dependencies from pyproject.toml
uv sync

# Run the application
uv run python main.py
```

Note: With uv, you don't need to manually activate the virtual environment. uv commands automatically detect and use the project's `.venv`.

## Project Structure

- `main.py` - Entry point for the application
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Specifies Python 3.13 requirement

## Development Commands

Since this is a new project, standard development commands will need to be established as the project grows. Currently:

```bash
# Run the application
uv run python main.py

# Add new dependencies
uv add <package-name>

# Sync dependencies from pyproject.toml
uv sync
```
