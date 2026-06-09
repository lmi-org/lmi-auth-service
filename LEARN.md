# Learning Log: lmi-auth-service

## Day 1 — Project Scaffold

### What I did
- Created the FastAPI project structure with layers: models, schemas, repositories, services, API
- Set up pyproject.toml with dependencies (FastAPI, SQLAlchemy, JWT, bcrypt)
- Configured pydantic-settings for environment variables
- Set up SQLAlchemy with PostgreSQL
- Created User and Session database models
- Implemented JWT access + refresh token flow
- Created REST API endpoints: register, login, refresh, logout, profile
- Set up test infrastructure with pytest + TestClient

### Key concepts
- **Layered architecture**: API → Service → Repository → Model (separation of concerns)
- **Repository pattern**: Abstracts database queries, makes services testable
- **Dependency injection**: FastAPI's `Depends()` wires everything together
- **JWT token rotation**: Refresh token is revoked when used, new one issued
- **pydantic-settings**: Type-safe environment config

### Test yourself
1. Why separate repositories from services?
2. What happens during token refresh? Walk through the flow.
3. Why is the refresh token hashed before storing in the database?
4. What's the difference between `access_token` and `refresh_token` expiry?
5. Why use UUIDs for primary keys instead of auto-increment integers?

### Answers (unfold after trying)
<details>
1. Repositories handle raw DB queries. Services handle business logic. This lets you test business logic without touching the database — mock the repository.
2. Client sends refresh token → decode JWT → find session in DB → check not revoked → revoke old session → create new access + refresh tokens.
3. If the database is compromised, the attacker can't use the refresh tokens directly — they'd need to crack the bcrypt hash first.
4. Access token: short-lived (15 min), no DB check needed, fast auth. Refresh token: long-lived (7 days), checked against DB, can be revoked server-side.
5. UUIDs don't leak information (sequential IDs reveal user count), are safe to expose in URLs, and work across distributed systems without collisions.
</details>

---

## Day 2 — Fixes & Debugging

### What I did
- Fixed `expires_at=...` bug (Python `Ellipsis` isn't a valid datetime)
- Fixed refresh token storage: now hashed with SHA-256 before saving to DB
- Fixed token lookup: `refresh()` and `logout()` now hash the incoming token before searching
- Fixed login flow: session ID is generated first, then tokens are created with that ID
- Added SQLite support for tests (`check_same_thread=False`)
- Set `DATABASE_URL` env var in conftest.py to use SQLite during tests
- Ran into `uv sync --group dev` → doesn't work. Correct command is `uv sync --extra dev`

### Key concepts
- **Token rotation flow**: Generate session ID → create JWT with that JTI → hash refresh token → store session → return tokens
- **`Ellipsis` bug**: Using `...` as a placeholder in Python won't work with databases. Always use explicit values.
- **SQLite vs PostgreSQL**: SQLite needs `check_same_thread=False` when used across threads (FastAPI async). PostgreSQL doesn't.
- **Test isolation**: Override `DATABASE_URL` to use SQLite so tests don't need a running PostgreSQL

### Common Commands
```bash
# Install dependencies (including dev extras)
uv sync --extra dev

# Run tests
uv run pytest -v

# Run server
uv run uvicorn app.main:app --reload --port 8000

# Start PostgreSQL
docker compose up -d db

# Create .env from example
cp .env.example .env
```

### Test yourself
1. Why did `expires_at=...` crash the server?
2. What's the purpose of hashing the refresh token before storing it?
3. Why override `DATABASE_URL` in conftest.py?
4. What does `check_same_thread=False` do?

### Answers (unfold after trying)
<details>
1. `...` is Python's `Ellipsis` literal — it's not a `datetime` object. PostgreSQL doesn't know how to serialize it. Always use `datetime.now(timezone.utc) + timedelta(...)` for timestamps.
2. If the database is breached, the raw refresh tokens aren't exposed. An attacker would need to SHA-256 hash each candidate to find a match — computationally expensive at scale.
3. Tests should run without external dependencies (no PostgreSQL needed). SQLite is file-based and works everywhere. The env var override makes the app use SQLite during tests.
4. SQLite connections are single-thread by default. FastAPI is async and may call the DB from different threads. This flag allows sharing the connection across threads.
</details>
