#!/usr/bin/env bash
set -e

cd /app

echo "==> Миграции базы данных"
python manage.py migrate --noinput

echo "==> Сбор статики"
python manage.py collectstatic --noinput

mkdir -p /app/media /app/data
MARKER=/app/media/.initialized

if [ ! -f "$MARKER" ]; then
    echo "==> Первичная настройка сайта"
    : "${ADMIN_USERNAME:=admin}"
    if [ -z "${ADMIN_PASSWORD:-}" ]; then
        ADMIN_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(9))')"
        echo ">>> Сгенерирован пароль администратора: $ADMIN_PASSWORD"
    fi
    python manage.py init_site \
        --username "$ADMIN_USERNAME" \
        --password "$ADMIN_PASSWORD" \
        --email "${ADMIN_EMAIL:-Ural_forest@bk.ru}"
    touch "$MARKER"
else
    echo "==> Сайт уже настроен, пропускаю первичную инициализацию"
fi

echo "==> Запуск Gunicorn на 0.0.0.0:8000"
exec gunicorn uralforest.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
