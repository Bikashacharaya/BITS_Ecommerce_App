# -----------------------------
# Dockerfile for Order Service
# -----------------------------
FROM python:3.10-slim

# Create working directory
WORKDIR /app

# Copy dependency list first (for Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . .

# Expose service port
EXPOSE 18081

# Start Flask application
CMD ["python", "app.py"]
