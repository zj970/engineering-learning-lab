# FreshRSS 本机部署

## 非 Docker：nginx + php-fpm + PostgreSQL

```bash
sudo env FRESHRSS_DB_PASSWORD='<请设置强密码>' \
  bash tools/freshrss/install-native-postgresql.sh
```

访问：`http://localhost:8989`

首次打开页面后按向导填写 PostgreSQL 参数：

- 数据库类型：PostgreSQL
- 主机：`localhost`
- 数据库名：`freshrss`
- 用户名：`freshrss`
- 密码：运行脚本时通过 `FRESHRSS_DB_PASSWORD` 设置的值

相关服务：

```bash
systemctl status postgresql
systemctl status php-fpm
systemctl status nginx
```

移除本机 FreshRSS 部署：

```bash
sudo bash tools/freshrss/remove-native-postgresql.sh
```

该脚本只删除 FreshRSS 目录、nginx FreshRSS 配置、`freshrss` 数据库和 `freshrss` 用户；不会卸载 nginx、php-fpm、PostgreSQL，也不会删除 PostgreSQL 整个数据目录。

## Docker Compose 旧方案

```bash
docker compose -f tools/freshrss/compose.yml up -d
```

访问：`http://localhost:8080`

首次打开页面后按向导创建管理员账户。当前配置使用 SQLite，数据保存在 `tools/freshrss/data/`。

## 维护命令

```bash
docker compose -f tools/freshrss/compose.yml ps
docker compose -f tools/freshrss/compose.yml logs -f
docker compose -f tools/freshrss/compose.yml pull
docker compose -f tools/freshrss/compose.yml up -d
docker compose -f tools/freshrss/compose.yml down
```
