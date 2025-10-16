"""Logging yapılandırması"""
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Uygulama için logging yapılandır"""
    
    # Log seviyesi
    log_level = logging.INFO if os.getenv('FLASK_ENV') == 'production' else logging.DEBUG
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # File handler (sadece production'da)
    if os.getenv('FLASK_ENV') == 'production':
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    
    # App logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Diğer logger'ları sustur
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('eventlet').setLevel(logging.WARNING)
    
    return app.logger