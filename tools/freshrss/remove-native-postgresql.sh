#!/usr/bin/env bash
set -euo pipefail

FRESHRSS_DIR=/srv/freshrss
NGINX_CONF=/etc/nginx/freshrss.conf
DB_NAME=freshrss
DB_USER=freshrss

if [[ ${EUID} -ne 0 ]]; then
  echo "请使用 sudo 运行：sudo bash tools/freshrss/remove-native-postgresql.sh" >&2
  exit 1
fi

if systemctl is-active --quiet postgresql; then
  sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${DB_NAME};
DROP ROLE IF EXISTS ${DB_USER};
SQL
else
  echo "PostgreSQL 未运行，跳过数据库和角色删除。" >&2
fi

rm -rf "${FRESHRSS_DIR}"
rm -f "${NGINX_CONF}"

if grep -q "include /etc/nginx/freshrss.conf;" /etc/nginx/nginx.conf; then
  sed -i '/include \/etc\/nginx\/freshrss\.conf;/d' /etc/nginx/nginx.conf
fi

if command -v nginx >/dev/null 2>&1; then
  nginx -t
  if systemctl is-active --quiet nginx; then
    systemctl reload nginx
  fi
fi

cat <<'EOF'
FreshRSS native PostgreSQL 部署已移除：
- 删除 /srv/freshrss
- 删除 /etc/nginx/freshrss.conf
- 从 /etc/nginx/nginx.conf 移除 FreshRSS include
- 删除 PostgreSQL 数据库 freshrss
- 删除 PostgreSQL 用户 freshrss

未卸载 nginx、php-fpm、PostgreSQL 软件包。
未停止 nginx、php-fpm、PostgreSQL 服务。
EOF
