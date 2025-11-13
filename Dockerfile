# Learning Extension MCP Server Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DATA_PATH=/data

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY learning_server.py .

# Create non-root user
RUN useradd -m -u 1000 mcp && \
    mkdir -p /data && \
    chown -R mcp:mcp /app /data

USER mcp

# Run the server
CMD ["python", "-u", "learning_server.py"]
