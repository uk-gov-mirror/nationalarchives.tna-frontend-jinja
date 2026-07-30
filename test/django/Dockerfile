FROM ghcr.io/nationalarchives/tna-python-dev:latest

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
COPY ./README.md /app/README.md
COPY ./LICENCE /app/LICENCE
COPY ./tna_frontend_jinja /app/tna_frontend_jinja
COPY ./test/django/app /app/test/django/app

RUN pip install -e ".[django]"
