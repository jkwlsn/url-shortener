# Install Bookwork image
FROM python:3.13.5-slim-bookworm AS builder

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# Second stage, run app
FROM python:3.13.5-slim-bookworm

WORKDIR /app

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy app code
COPY --from=builder /app /app

# Use virtual env
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port your application runs on (e.g., 8000 for FastAPI/Uvicorn)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
