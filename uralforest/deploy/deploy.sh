#!/usr/bin/env bash
#
# Автоматическое развёртывание сайта «Уральский лес» на Ubuntu.
# Запуск из корня проекта:
#     sudo DOMAIN=ваш-домен.рф bash deploy/deploy.sh
#
# Переменные (можно задать перед командой):
#   DOMAIN        — домен сайта                      (по умолчанию example.ru)
#   APP_USER      — системный пользователь           (по умолчанию www-data)
#   PORT          — внутренний порт Gunicorn         (по умолчанию 8000)
#   ADMIN_EMAIL   — e-mail администратора            (по умолчанию Ural_forest@bk.ru)
#   ADMIN_USER    — логин админки                    (по умолчанию admin)
#   ADMIN_PASS    — пароль админки                   (по умолчанию генерируется)
#   INSTALL_SSL   — yes / no                         (по умолчанию спросит)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

APP_DIR="${APP_DIR:-$PROJECT_ROOT}"
APP_USER="${APP_USER:-www-data}"
PORT="${PORT:-8000}"
DOMAIN="${DOMAIN:-example.ru}"
ADMIN_EMAIL="${ADMIN_EMAIL:-Ural_forest@bk.ru}"
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-$(openssl rand -base64 12 2>/dev/null || date +%s%N | sha256sum | cut -c1-14)}"
INSTALL_SSL="${INSTALL_SSL:-ask}"
SERVICE_NAME="uralforest"

c() { printf "\n\033[1;32m==> %s\033[0m\n" "$1"; }

if [[ $EUID -ne 0 ]]; then
    echo "Запустите скрипт от root:  sudo DOMAIN=$DOMAIN bash deploy/deploy.sh"
    exit 1
fi

c "1/8 Установка системных пакетов"
apt update -y
apt install -y python3-venv python3-pip nginx openssl

c "2/8 Виртуальное окружение и зависимости"
cd "$APP_DIR"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
./.venv/bin/pip install gunicorn

c "3/8 Файл окружения .env"
if [[ ! -f .env ]]; then
    SECRET="$(./.venv/bin/python -c 'from django.core.management.utils import get_random_secret_key as g; print(g())')"
    cat > .env <<EOF
DJANGO_SECRET_KEY=$SECRET
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

PAYMENTS_ENABLED=False
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=

ORDERS_NOTIFY_EMAIL=$ADMIN_EMAIL
DEFAULT_FROM_EMAIL=$ADMIN_EMAIL
EOF
    echo "  · Создан .env (не забудьте вписать ключи ЮKassa и включить PAYMENTS_ENABLED=True)."
else
    echo "  · .env уже существует — оставляю без изменений."
fi

c "4/8 Миграции, статика, первичная настройка"
./.venv/bin/python manage.py migrate --noinput
./.venv/bin/python manage.py collectstatic --noinput
./.venv/bin/python manage.py init_site --username "$ADMIN_USER" --password "$ADMIN_PASS" --email "$ADMIN_EMAIL"

c "5/8 Права доступа"
mkdir -p "$APP_DIR/media" "$APP_DIR/staticfiles"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

c "6/8 Служба systemd"
sed -e "s|__APP_DIR__|$APP_DIR|g" \
    -e "s|__APP_USER__|$APP_USER|g" \
    -e "s|__PORT__|$PORT|g" \
    "$SCRIPT_DIR/gunicorn.service" > "/etc/systemd/system/$SERVICE_NAME.service"
systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

c "7/8 Nginx"
sed -e "s|__DOMAIN__|$DOMAIN|g" \
    -e "s|__APP_DIR__|$APP_DIR|g" \
    -e "s|__PORT__|$PORT|g" \
    "$SCRIPT_DIR/nginx.conf" > "/etc/nginx/sites-available/$SERVICE_NAME"
ln -sf "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/$SERVICE_NAME"
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

c "8/8 HTTPS (Let's Encrypt)"
if [[ "$INSTALL_SSL" == "ask" ]]; then
    read -r -p "Установить бесплатный SSL-сертификат для $DOMAIN? [y/N] " ans || true
    [[ "${ans:-}" =~ ^[Yy]$ ]] && INSTALL_SSL=yes || INSTALL_SSL=no
fi
if [[ "$INSTALL_SSL" == "yes" ]]; then
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "$ADMIN_EMAIL" --redirect || \
        echo "  · Не удалось выпустить сертификат. Убедитесь, что домен указывает на этот сервер."
else
    echo "  · SSL пропущен (можно позже: sudo certbot --nginx -d $DOMAIN)."
fi

cat <<EOF

============================================================
 Готово! Сайт развёрнут.

 Сайт:      http://$DOMAIN/
 Админка:   http://$DOMAIN/admin/
 Логин:     $ADMIN_USER
 Пароль:    $ADMIN_PASS

 Управление службой:
   sudo systemctl status  $SERVICE_NAME
   sudo systemctl restart $SERVICE_NAME
   sudo journalctl -u $SERVICE_NAME -f

 Логи Nginx: /var/log/nginx/error.log
============================================================
EOF
