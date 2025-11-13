import os

bind = f"{os.getenv('RUN_HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}"
workers = int(os.getenv('GUNICORN_WORKERS', '3'))
timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')
