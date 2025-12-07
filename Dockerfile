FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/dependencies /usr/local/lib/python3.11/site-packages
COPY . .

ENV PYTHONPATH=/app

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
