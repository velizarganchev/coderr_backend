# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION}-slim as base

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# Copy project files
COPY . .

# Set permissions for non-privileged user
RUN chown -R appuser:appuser /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Use non-privileged user
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "coderr_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
