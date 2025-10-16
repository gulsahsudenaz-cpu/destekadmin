"""Güvenlik ve performans middleware'leri"""
import time
from functools import wraps
from flask import request, jsonify
import logging

# Rate limiting için basit in-memory store
_rate_limits = {}

def rate_limit(max_requests=60, window=60):
    """Basit rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            now = time.time()
            key = f"{client_ip}:{request.endpoint}"
            
            # Eski kayıtları temizle
            if key in _rate_limits:
                _rate_limits[key] = [t for t in _rate_limits[key] if now - t < window]
            else:
                _rate_limits[key] = []
            
            # Limit kontrolü
            if len(_rate_limits[key]) >= max_requests:
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            _rate_limits[key].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def request_logger(f):
    """Request logging middleware"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        response = f(*args, **kwargs)
        duration = time.time() - start_time
        logging.info(f"{request.method} {request.path} - {duration:.3f}s")
        return response
    return wrapper

def security_headers(response):
    """Güvenlik header'larını ekle"""
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    })
    return response