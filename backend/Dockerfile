# syntax=docker/dockerfile:1
#
# CyBreach Verdict Platform -- Pod Delta backend.
#
# N-D3: this file was tracked at 0 bytes, so the backend could not be
# containerized at all. The build context is `backend/`, because that is where
# `requirements.txt` and the `app/` package live -- an earlier attempt placed a
# Dockerfile at the repo root, where `COPY requirements.txt` cannot resolve.
#
#   docker build -f backend/Dockerfile -t cybreach-delta-backend backend
#   docker run --rm -p 8000:8000 \
#     -e DATABASE_URL=postgresql+psycopg2://validator:<pw>@host.docker.internal:5432/verdict_db \
#     -e SECRET_KEY=<secret> \
#     -e ADMIN_USERNAME=<analyst> \
#     -e ADMIN_PASSWORD=<password> \
#     cybreach-delta-backend
#
# The variable is `SECRET_KEY`, not `JWT_SECRET_KEY`: the application reads
# `SECRET_KEY` (`app/security/security.py`) and has no `JWT_SECRET_KEY` path, so
# passing the latter would leave the service unable to sign a token -- it fails
# closed rather than using a built-in key. There are no defaults for any of
# these; see `.env.example`.
#
# The image serves on 8000 (the port the registry assigns Delta's backend);
# Kong is a separate optional container in front of it on 8010/8011.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# psycopg2-binary ships wheels, so no build toolchain is needed. `libpq` is
# still linked by some of its transitive imports on slim images.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Dependencies first, so editing application code does not invalidate the
# layer holding the installed packages.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# The schema is owned by Alembic (N-D2). The app refuses to serve if the
# database is not at head rather than creating tables itself, so the image
# deliberately ships no schema-ownership shortcut.
RUN useradd --create-home --uid 10001 cybreach \
    && chown -R cybreach:cybreach /app
USER cybreach

EXPOSE 8000

# /health reports liveness without touching the database, so an orchestrator
# can use it as a container healthcheck.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
