# URL Shortener

A simple, RESTful URL shortener API

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Development Setup](#development-setup)
  - [Running Tests](#running-tests)
- [Production Deployment](#production-deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Features

- Shorten long URLs into concise, memorable short links.
- Redirect short links to their original long URLs.
- Links expire after fixed time

## Technologies Used

- **FastAPI** - A modern, fast (high-performance) web framework for building APIs with Python 3.8+ based on standard Python type hints.
- **PostgreSQL** - A powerful, open-source object-relational database system.
- **SQLAlchemy** - The Python SQL Toolkit and Object Relational Mapper that gives developers the full power of SQL.
- **Pydantic** - Data validation and settings management using Python type hints.

## Getting Started

### Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) package & project manager
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/install/) (for production deployment and local database setup)

### Development Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/jkwlsn/url-shortener.git
    cd url-shortener
    ```

2.  **Install dependencies using `uv`**

    ```bash
    uv sync
    ```

3.  **Set environment variables**

    Create a `.env` file in the root directory of the project and add the following:

    ```env
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=password
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=url_shortener

    BASE_URL="http://localhost:8000"
    SLUG_LENGTH=7

    MAX_URL_LENGTH=2048
    MIN_URL_LENGTH=15
    MAX_URL_AGE=30
    ```

    You can replace these values with your own.

4.  **Start the PostgreSQL database and FastAPI application using Docker Compose**

    ```bash
    docker compose up
    ```

    The API will be accessible at [`http://localhost:8000`](http://localhost:8000).

### Running Tests

To run the tests and check code coverage:

```bash
uv run pytest
uv run coverage report
```

## Production Deployment

To deploy the application using Docker Compose:

1.  **Environment Variables for Production:**

    Ensure your `.env` file is properly configured for your production environment.

    Docker Compose expects `POSTGRES_HOST` to be set to `url_shortener_db`, the service defined in `compose.yml`.

2.  **Build and run the Docker containers:**

    ```bash
    docker compose up --build -d
    ```

    This will start both the PostgreSQL database and the FastAPI application.

    The API will be accessible on port `8000` of your host machine.

## API Documentation

Once the application is running, you can access the interactive API documentation at [`http://localhost:8000/docs`](http://localhost:8000/docs)

### Routes

- `POST /shorten`
    - Accepts json payload of `{"long_url": "http://www.example.com/page/sub-folder/a-long-document-name.html"}`
    - Returns a json payload of `{"short_url": "http://abc.de/1234"}`
- `GET /{slug}`
    - Returns `307` redirect to original URL, e.g. `http://www.example.com/page/sub-folder/a-long-document-name.html`

### Status codes

Clients should handle the following error codes:

- `200` - OK
- `307` - Temporary redirect (used when returning long URLs)
- `404` - Not found
- `410` - Gone (used for expired links)
- `422` - Unprocessable content
- `500` - Internal error

## Project Structure

```
.
├───.github/                 # GitHub Actions workflows (CI/CD)
├───config/                  # Application configuration
├───database/                # Database connection and session management
├───docs/                    # Project documentation (diagrams, brief)
├───exceptions/              # Custom exception definitions
├───models/                  # SQLAlchemy ORM models
├───routes/                  # FastAPI route definitions
├───schemas/                 # Pydantic schemas for request/response validation
├───services/                # Business logic and service layer
├───tests/                   # Unit and integration tests
├───.coveragerc              # Coverage.py configuration
├───.dockerignore            # Files to ignore when building Docker image
├───.gitignore               # Git ignore rules
├───.python-version          # Specifies Python version for tools like pyenv
├───compose.yml              # Docker Compose configuration
├───Dockerfile               # Dockerfile for the FastAPI application
├───main.py                  # Main application entry point
├───pyproject.toml           # Project metadata and dependencies (PEP 621)
├───README.md                # This README file
└───uv.lock                  # uv dependency lock file
```

## Contributing

Contributions are welcome!

Before you start, make sure you have the following tools installed:

- `Docker & Docker Compose`
- `Ruff`
- `Pytest`
- `Coverage.py`
