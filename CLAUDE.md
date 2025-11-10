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

## Coding Standards

### Type Hinting
- **MUST** add type hints to all function definitions
- Include return type hints for all functions (use `-> None` for functions that don't return a value)
- Add type hints to function parameters
- Add type hints to variables where beneficial for clarity
- Use appropriate types from `typing` module when needed (e.g., `Callable`, `Optional`, `List`, `Dict`)

Example:
```python
def process_data(text: str, max_length: int) -> str:
    result: str = text[:max_length]
    return result
```
