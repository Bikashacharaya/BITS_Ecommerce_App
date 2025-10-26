# -------------------------------
# Dockerfile for Catalog Service
# -------------------------------
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 18082

CMD ["python", "app.py"]
