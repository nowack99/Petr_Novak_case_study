FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml 2>/dev/null || true

COPY . .
RUN uv pip install --system --no-cache .


FROM python:3.12-slim

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build/app ./app
COPY --from=builder /build/alembic ./alembic
COPY --from=builder /build/alembic.ini .

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
