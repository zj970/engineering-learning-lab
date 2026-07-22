#!/usr/bin/env bash
set -euo pipefail

FRESHRSS_DIR=/srv/freshrss
FRESHRSS_VERSION=1.27.0
FRESHRSS_TARBALL="/tmp/freshrss-${FRESHRSS_VERSION}.tar.gz"
FRESHRSS_URL="https://github.com/FreshRSS/FreshRSS/archive/refs/tags/${FRESHRSS_VERSION}.tar.gz"
NGINX_CONF=/etc/nginx/freshrss.conf
PGDATA=/var/lib/postgres/data
DB_NAME=freshrss
DB_USER=freshrss

if [[ ${EUID} -ne 0 ]]; then
  echo "请使用 sudo 运行：sudo env FRESHRSS_DB_PASSWORD='<强密码>' bash tools/freshrss/install-native-postgresql.sh" >&2
  exit 1
fi

if [[ -z ${FRESHRSS_DB_PASSWORD:-} ]]; then
  echo "请通过 FRESHRSS_DB_PASSWORD 环境变量设置数据库密码。" >&2
  exit 1
fi
DB_PASSWORD=${FRESHRSS_DB_PASSWORD}

require_command() {
  local command_name=$1
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "缺少命令：${command_name}" >&2
    exit 1
  fi
}

require_command curl
require_command nginx
require_command php-fpm
require_command postgres
require_command psql
require_command tar

if [[ ! -s ${PGDATA}/PG_VERSION ]]; then
  echo "初始化 PostgreSQL 数据目录：${PGDATA}"
  install -d -o postgres -g postgres -m 700 "${PGDATA}"
  sudo -u postgres initdb -D "${PGDATA}" --locale=C.UTF-8 --encoding=UTF8
fi

systemctl enable --now postgresql

sudo -u postgres psql -v ON_ERROR_STOP=1 --set=db_password="${DB_PASSWORD}" <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN;
  END IF;
END
\$\$;
ALTER ROLE ${DB_USER} WITH LOGIN PASSWORD :'db_password';
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL

if [[ ! -d ${FRESHRSS_DIR} ]]; then
  echo "下载 FreshRSS ${FRESHRSS_VERSION}"
  curl -L "${FRESHRSS_URL}" -o "${FRESHRSS_TARBALL}"
  tar -xzf "${FRESHRSS_TARBALL}" -C /srv
  mv "/srv/FreshRSS-${FRESHRSS_VERSION}" "${FRESHRSS_DIR}"
fi

chown -R root:http "${FRESHRSS_DIR}"
chmod -R g+rX "${FRESHRSS_DIR}"
chown -R http:http "${FRESHRSS_DIR}/data" "${FRESHRSS_DIR}/extensions"

cat >"${NGINX_CONF}" <<'NGINX'
server {
    listen 127.0.0.1:8989;
    server_name localhost;

    root /srv/freshrss/p;
    index index.php index.html;

    access_log /var/log/nginx/freshrss.access.log;
    error_log /var/log/nginx/freshrss.error.log;

    location / {
        try_files $uri $uri/ index.php$is_args$args;
    }

    location ~ ^.+?\.php(/.*)?$ {
        fastcgi_pass unix:/run/php-fpm/php-fpm.sock;
        fastcgi_split_path_info ^(.+\.php)(/.*)$;
        set $path_info $fastcgi_path_info;
        fastcgi_param PATH_INFO $path_info;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\. {
        deny all;
    }
}
NGINX

if ! grep -q "include /etc/nginx/freshrss.conf;" /etc/nginx/nginx.conf; then
  sed -i '/^http {/a\    include /etc/nginx/freshrss.conf;' /etc/nginx/nginx.conf
fi

nginx -t
systemctl enable --now php-fpm
systemctl enable --now nginx
systemctl reload nginx

cat <<EOF

FreshRSS 本机服务已准备好。

访问地址：http://localhost:8989

安装向导里的 PostgreSQL 参数：
- 数据库类型：PostgreSQL
- 主机：localhost
- 数据库名：${DB_NAME}
- 用户名：${DB_USER}
- 密码：${DB_PASSWORD}

EOF
