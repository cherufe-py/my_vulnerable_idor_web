FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    RUN_HOST=0.0.0.0 \
    GUNICORN_WORKERS=3 \
    GUNICORN_TIMEOUT=30 \
    GUNICORN_LOGLEVEL=info

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN python init_db.py && python add_sample_files.py

EXPOSE ${PORT}

CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
