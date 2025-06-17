# Dockerfile for Ollama On-Demand Proxy with Dynamic Server List
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and config
COPY proxy.py .
COPY config/servers.yml config/servers.yml

# Default command
CMD ["python", "proxy.py"]
