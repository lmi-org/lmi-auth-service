# lmi-auth-service

Authentication microservice for the LMI platform.

## Tech

- FastAPI + SQLAlchemy + PostgreSQL
- JWT access/refresh tokens with rotation
- bcrypt password hashing
- Alembic for migrations

## Dev

```bash
uv sync --extra dev
cp .env.example .env
docker compose up -d db          # start PostgreSQL
uv run uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
uv run pytest -v
```
