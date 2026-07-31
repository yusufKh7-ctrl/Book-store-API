<div align="center">
  <img src="book-store-api.jpg" width="200" alt="book-stroe-api">
  <h1 align="center">Book-Store API 📚</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-121011?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-121011?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-121011?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-121011?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/uv-121011?style=flat-square&logo=uv&logoColor=white" />
  <img src="https://img.shields.io/badge/Pytest-121011?style=flat-square&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-121011?style=flat-square&logo=githubactions&logoColor=white" />
</p>
</div>
<hr>
> A RESTful API for a bookstore built with **FastAPI** and **PostgreSQL**.  
> This project was developed to practice building production-ready backend systems, covering authentication, authorization, order management, database migrations, testing, and containerization.

---

## Features

- JWT Authentication & Authorization (Admin / User roles)
- Full CRUD for Books
- User management
- Order management (with order items)
- Rate limiting
- Database constraints & data integrity checks
- Alembic migrations
- Docker & Docker Compose support
- Automated tests with **pytest**
- GitHub Actions CI pipeline
- Interactive API docs (Swagger UI & ReDoc)

---

## Tech Stack

| Category              | Technology                          |
|-----------------------|-------------------------------------|
| Framework             | FastAPI                             |
| ORM                   | SQLAlchemy 2.0 (Async)              |
| Database              | PostgreSQL + asyncpg                |
| Migrations            | Alembic                             |
| Validation            | Pydantic v2                         |
| Auth                  | JWT (python-jose) + Passlib/Argon2  |
| Package Manager       | uv                                  |
| Testing               | pytest + pytest-asyncio + httpx     |
| Rate Limiting         | slowapi                             |
| Containerization      | Docker & Docker Compose             |
| CI                    | GitHub Actions                      |

---

## Project Structure

```text
Book-store-API/
├── app/
│   ├── api/              # Route handlers (auth, users, books, orders)
│   ├── core/             # Dependencies, security, rate limiter
│   ├── db/               # Database session & base
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── tests/            # Test suite
│   └── config.py         # Settings (pydantic-settings)
├── migrations/           # Alembic migrations
├── .github/workflows/    # CI pipeline
├── docker-compose.yml
├── dockerfile
├── main.py               # Application entrypoint
├── pyproject.toml
├── alembic.ini
├── seed.py               # Optional data seeding
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- PostgreSQL (or use Docker)
- Docker & Docker Compose (optional but recommended)

### 1. Clone the repository

```bash
git clone https://github.com/yusufKh7-ctrl/Book-store-API.git
cd Book-store-API
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/bookstore_db
DATABASE_PASSWORD=your_password
TEST_DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/bookstore_test
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Never** commit your real `.env` file. Keep secrets out of version control.

### 3. Run with Docker

```bash
docker compose up --build
```

The API will be available at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 4. Run locally (without Docker)

```bash
uv sync

uv run alembic upgrade head

uv run uvicorn main:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Running Tests

```bash
uv run pytest -v
```

The test suite covers authentication, users, books, and orders.  
In CI, tests run automatically on every push/pull request to `main` via GitHub Actions.

---

## API Overview

Interactive documentation is available at `/docs` after starting the server.  
Here’s a high-level summary of the main endpoints:

| Method | Endpoint              | Description              | Access     |
|--------|-----------------------|--------------------------|------------|
| POST   | `/auth/login`         | Login & get JWT token    | Public     |
| GET    | `/api/books`          | List all books           | Public     |
| GET    | `/api/books/{id}`     | Get book by ID           | Public     |
| POST   | `/api/books`          | Create a book            | Admin      |
| PATCH  | `/api/books/{id}`     | Update a book            | Admin      |
| DELETE | `/api/books/{id}`     | Delete a book            | Admin      |
| GET    | `/api/users`          | List users               | Admin      |
| POST   | `/api/order`          | Create an order          | Authenticated |
| GET    | `/api/order`          | List orders              | Authenticated / Admin |

> Exact paths and request/response schemas are fully documented in the Swagger UI.

---

## Authentication

1. Register or use an existing user.
2. Send a `POST` request to `/auth/login` with credentials.
3. Copy the returned `access_token`.
4. Click **Authorize** in Swagger UI and paste: `Bearer <your_token>`.

Admin-only endpoints require a user with `is_admin = true`.

---

## License
*This project is created for educational and portfolio purposes.*

<hr>

