FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# API + crawler modules (single small codebase).
COPY . .

EXPOSE 8000
# DB lives on a mounted volume; compose sets FIBER_DB=/data/fiber.db.
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
