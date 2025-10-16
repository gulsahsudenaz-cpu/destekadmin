FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m app && chown -R app:app /app

# Copy application
COPY . .

# Switch to non-root user
USER app

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:10000/health', timeout=5)" || exit 1

# Run application
CMD ["python", "-m", "server.app"]
