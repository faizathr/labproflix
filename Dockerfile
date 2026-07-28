FROM python:3.12-slim-bookworm

# uv replaces pip as the dependency manager (see pyproject.toml / uv.lock)
COPY --from=ghcr.io/astral-sh/uv:0.5.9 /uv /uvx /bin/

RUN apt-get update \
    # build toolchain and libpq headers: psycopg2 is built from source
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gettext \
    # cleaning up unused files
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/usr/src/app/.venv \
    PATH="/usr/src/app/.venv/bin:$PATH"

# Resolve dependencies before copying the source so this layer is cached
# across code changes and only re-runs when the lockfile moves
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project

COPY . /usr/src/app

EXPOSE 80

CMD ["sh", "./runserver.sh"]
