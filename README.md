# Order Management API

A FastAPI-based order management system with CI/CD pipeline.

## Features

- **FastAPI** web application
- **Health check** endpoint (`/health`)
- **Order management** API endpoints (`/orders`)
- **SQLite** database with SQLAlchemy ORM
- **Minimal UI** to display orders
- **Comprehensive testing** (unit + integration)
- **CI/CD** with GitHub Actions
- **Code quality** checks (flake8, pylint)
- **Test coverage** reports

## Project Structure

```
project_arculus/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── database.py       # Database configuration
│   ├── models.py         # SQLAlchemy models
│   └── schemas.py        # Pydantic schemas
├── tests/
│   ├── __init__.py
│   ├── test_main.py      # Unit tests
│   └── test_integration.py  # Integration tests
├── templates/
│   └── index.html        # UI template
├── .github/
│   └── workflows/
│       └── ci.yml        # CI pipeline
├── requirements.txt
├── .flake8
├── setup.cfg
└── README.md
```

## Setup Instructions

### 1. Activate your conda environment

```bash
conda activate gitops
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

The application will be available at: `http://localhost:8000`

## API Endpoints

- `GET /` - Display orders UI
- `GET /health` - Health check
- `POST /orders` - Create a new order
  ```json
  {
    "amount": 99.99
  }
  ```
- `GET /orders` - Get all orders
- `GET /orders/{id}` - Get specific order

## Testing

### Run all tests

```bash
pytest
```

### Run unit tests only

```bash
pytest tests/test_main.py -v
```

### Run integration tests only

```bash
pytest tests/test_integration.py -v
```

### Run with coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report: `open htmlcov/index.html`

## Linting

### Run flake8

```bash
flake8 app/ tests/
```

### Run pylint

```bash
pylint app/
```

## CI/CD Pipeline

The GitHub Actions CI pipeline automatically runs on:
- Every push to any branch
- Every pull request

Pipeline stages:
1. **Linting** - flake8 and pylint checks
2. **Unit Tests** - with coverage reports
3. **Integration Tests** - database and API validation

## Database

The application uses Postgres by default. The database file `orders.db` will be created automatically on first run.

### Order Schema

| Field  | Type  | Description |
|--------|-------|-------------|
| id     | int   | Auto-increment primary key |
| amount | float | Order amount (must be > 0) |

## Next Steps (Part 2)

- Dockerize the application with multi-stage build
- Configure Docker registry (GitHub Container Registry)
- Tag images with git commit SHA
- Set up non-root user in container
- Optimize image size
