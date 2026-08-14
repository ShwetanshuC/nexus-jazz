FROM python:3.10-slim

EXPOSE 8000/tcp
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

COPY . .

RUN DJANGO_SECRET_KEY=build-placeholder python3 manage.py collectstatic --noinput

CMD ["sh", "-c", "\
  python3 manage.py restore_db || true && \
  python3 manage.py migrate --noinput && \
  python3 manage.py create_superusers || true && \
  python3 manage.py sync_media || true && \
  python3 manage.py backup_db || true && \
  trap 'echo \"[startup] SIGTERM received — backing up DB before shutdown\" && python3 manage.py backup_db && exit 0' TERM INT && \
  gunicorn nexus_jazz.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 300 --keep-alive 5 --log-level info & \
  wait $!"]
