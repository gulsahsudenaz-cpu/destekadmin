FROM python:3.12-slim

# Güvenlik güncellemeleri
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Non-root user oluştur
RUN useradd -m -u 1000 app && \
    mkdir -p /app/logs && \
    chown -R app:app /app

# Dependencies yükle
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY --chown=app:app . .

# Non-root user'a geç
USER app

# Port aç
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:10000/health || exit 1

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Uygulamayı çalıştır
CMD ["python", "-m", "server.app"]
