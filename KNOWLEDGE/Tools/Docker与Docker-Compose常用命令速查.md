# Docker 与 Docker Compose 常用命令速查

## 本质

这篇文档不是完整的 Docker 参数手册，而是一份面向日常开发、部署和排障的命令速查。

使用 Docker 命令前，先区分两种操作范围：

- `docker ...`：直接管理单个容器、镜像、网络、卷和 Docker daemon。
- `docker compose ...`：按照 `compose.yaml` 管理一组相关服务及其网络、卷和生命周期。

当前文档统一使用 Compose V2 写法：

```bash
docker compose
```

旧教程中的下面写法属于 Compose V1：

```bash
docker-compose
```

两者不要在同一个项目操作流程里混用。

---

## 原理

### Docker 对象关系

```text
Docker CLI
    │
    ▼
Docker daemon
    ├── Image：只读镜像模板
    ├── Container：镜像的运行实例
    ├── Network：容器之间的通信网络
    └── Volume：独立于容器生命周期的数据存储
```

最关键的理解是：

- 删除容器不等于删除镜像。
- 删除容器不一定删除数据卷。
- 删除镜像不影响已经写入命名卷的数据。
- 容器自己的可写层不适合保存重要数据。

### Docker Compose 对象关系

```text
compose.yaml
    │
    ▼
Compose Project
    ├── Service: web
    │     └── Container: project-web-1
    ├── Service: db
    │     └── Container: project-db-1
    ├── Network
    └── Volume
```

Compose 中通常操作的是服务名，例如 `web`、`db`，而不是自动生成的容器名。

---

## 使用约定

文档中的占位符含义如下：

| 占位符 | 含义 | 示例 |
| --- | --- | --- |
| `<container>` | 容器名称或 ID | `my-nginx` |
| `<image>` | 镜像名称和标签 | `nginx:alpine` |
| `<service>` | Compose 服务名 | `web` |
| `<volume>` | Docker 卷名 | `app-data` |
| `<network>` | Docker 网络名 | `app-net` |

执行命令时需要将占位符整体替换，不能保留尖括号。

---

## 一、环境与 daemon

### 查看版本

```bash
docker --version
docker version
docker compose version
```

区别：

- `docker --version`：只显示 CLI 简要版本。
- `docker version`：同时显示客户端和服务端版本；daemon 不可用时服务端部分会报错。
- `docker compose version`：显示 Compose 插件版本。

### 检查 Docker daemon

```bash
docker info
```

这是判断 Docker 是否真正可用的第一条命令。

如果只看到类似错误：

```text
Cannot connect to the Docker daemon
```

说明 CLI 已安装，但 daemon 没有运行、socket 不可访问，或者当前 context 指向了错误目标。

### Linux systemd 管理

```bash
sudo systemctl status docker
sudo systemctl start docker
sudo systemctl stop docker
sudo systemctl restart docker
sudo systemctl enable --now docker
sudo systemctl disable --now docker
```

`enable --now` 同时完成开机自启和立即启动。

### 查看当前 Docker context

```bash
docker context ls
docker context show
```

当 CLI 明明可用却连接到错误 daemon 时，需要检查 context 或 `DOCKER_HOST`。

### 关于 docker 用户组

```bash
sudo usermod -aG docker "$USER"
```

重新登录后，用户可以不加 `sudo` 执行 Docker 命令。

风险：`docker` 用户组通常等价于拥有宿主机 root 级控制能力，不应把不可信用户加入该组。

---

## 二、容器常用命令

### 查看容器

```bash
docker ps
docker ps -a
docker ps -q
docker ps --filter status=exited
```

| 命令 | 作用 |
| --- | --- |
| `docker ps` | 查看正在运行的容器 |
| `docker ps -a` | 查看所有容器，包括已退出容器 |
| `docker ps -q` | 只输出容器 ID |
| `--filter` | 按状态、名称、标签等条件过滤 |

### 创建并启动容器

```bash
docker run -d \
  --name nginx-demo \
  -p 8080:80 \
  --restart unless-stopped \
  nginx:alpine
```

关键参数：

| 参数 | 含义 |
| --- | --- |
| `-d` | 后台运行 |
| `--name` | 指定容器名 |
| `-p 8080:80` | 宿主机 8080 映射到容器 80 |
| `--restart unless-stopped` | daemon 重启后自动恢复，除非用户主动停止 |

### 前台交互运行

```bash
docker run --rm -it alpine sh
```

这里：

- `-i` 保持标准输入。
- `-t` 分配伪终端。
- `--rm` 在进程退出后自动删除容器和关联匿名卷。

适合临时测试，不适合保存重要状态。

### 设置环境变量

```bash
docker run --rm \
  -e APP_ENV=production \
  -e LOG_LEVEL=info \
  nginx:alpine
```

从文件读取：

```bash
docker run --rm --env-file .env nginx:alpine
```

不要把密码直接写进会被记录到 Shell 历史的命令中。

### 挂载宿主机目录

推荐使用可读性更强的 `--mount`：

```bash
docker run --rm \
  --mount type=bind,src="$PWD/html",dst=/usr/share/nginx/html,readonly \
  nginx:alpine
```

传统简写：

```bash
docker run --rm \
  -v "$PWD/html:/usr/share/nginx/html:ro" \
  nginx:alpine
```

Bind mount 直接依赖宿主机路径。宿主机文件被删除或覆盖，容器内看到的内容也会变化。

### 使用命名卷

```bash
docker run -d \
  --name app \
  --mount type=volume,src=app-data,dst=/data \
  alpine sleep infinity
```

命名卷适合保存数据库、应用状态等需要独立于容器存在的数据。

### 限制资源

```bash
docker run -d \
  --name limited-app \
  --cpus 1.5 \
  --memory 512m \
  nginx:alpine
```

资源限制用于防止单个容器占满宿主机 CPU 或内存。

### 启停和重启

```bash
docker start <container>
docker stop <container>
docker restart <container>
docker kill <container>
```

区别：

- `stop` 先发送正常终止信号，超时后才强制结束。
- `kill` 默认立即发送 `SIGKILL`，进程没有清理机会。
- 排障时不要把 `kill` 当作普通停止命令。

### 删除容器

```bash
docker rm <container>
docker rm -f <container>
```

`-f` 会强制停止并删除运行中的容器，使用前应确认容器内没有未持久化数据。

### 进入运行中的容器

```bash
docker exec -it <container> sh
```

如果镜像安装了 Bash：

```bash
docker exec -it <container> bash
```

指定用户或工作目录：

```bash
docker exec -it -u root -w /app <container> sh
```

### 查看日志

```bash
docker logs <container>
docker logs -f <container>
docker logs --tail 200 <container>
docker logs --since 30m -t <container>
```

排障时通常先使用：

```bash
docker logs --tail 200 <container>
```

确认没有持续刷屏后，再决定是否使用 `-f`。

### 查看详细信息

```bash
docker inspect <container>
```

只看状态：

```bash
docker inspect -f '{{.State.Status}}' <container>
```

查看容器 IP：

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container>
```

查看健康检查状态：

```bash
docker inspect -f '{{json .State.Health}}' <container>
```

### 查看资源、进程和端口

```bash
docker stats
docker stats <container>
docker top <container>
docker port <container>
```

### 在宿主机和容器之间复制文件

```bash
docker cp ./config.yaml <container>:/app/config.yaml
docker cp <container>:/var/log/app.log ./app.log
```

`docker cp` 不是持续同步工具，只执行一次复制。

### 查看容器文件变化

```bash
docker diff <container>
```

输出中的 `A`、`C`、`D` 分别代表新增、修改和删除。

---

## 三、镜像与构建

### 查看镜像

```bash
docker image ls
docker images
```

两者作用相同，推荐使用对象化写法 `docker image ls`。

### 拉取镜像

```bash
docker pull nginx:alpine
```

不要默认认为本地 `latest` 会自动更新；需要显式 `pull` 或使用对应拉取策略。

### 构建镜像

```bash
docker build -t myapp:1.0 .
```

重新拉取基础镜像：

```bash
docker build --pull -t myapp:1.0 .
```

完全不使用构建缓存：

```bash
docker build --no-cache --pull -t myapp:1.0 .
```

`--no-cache` 会明显增加构建时间，不应作为每次构建的默认参数。

### 查看构建历史

```bash
docker history <image>
```

可以帮助判断镜像层大小，但不能保证发现所有敏感信息泄漏。

### 标记、登录和推送

```bash
docker tag myapp:1.0 registry.example.com/team/myapp:1.0
docker login registry.example.com
docker push registry.example.com/team/myapp:1.0
docker logout registry.example.com
```

### 删除镜像

```bash
docker rmi <image>
docker image rm <image>
```

如果镜像仍被容器引用，Docker 通常会拒绝删除。应先确认相关容器是否还需要，而不是立即使用强制删除。

### 导出和导入镜像

```bash
docker save -o myapp-1.0.tar myapp:1.0
docker load -i myapp-1.0.tar
```

不要混淆：

- `docker save/load`：保存和恢复镜像及其层、标签。
- `docker export/import`：处理容器文件系统快照，会丢失镜像历史和部分元数据。

---

## 四、网络

### 查看、创建和检查网络

```bash
docker network ls
docker network create app-net
docker network inspect app-net
```

### 连接和断开网络

```bash
docker network connect app-net <container>
docker network disconnect app-net <container>
```

### 删除网络

```bash
docker network rm app-net
docker network prune
```

正在被容器使用的网络不能直接删除。

### 容器之间如何访问

同一个用户自定义网络中的容器，优先通过容器名或网络别名访问：

```text
http://db:5432
http://api:8080
```

不要长期依赖容器 IP，因为容器重建后 IP 可能变化。

### 容器访问宿主机

Docker Desktop 通常可以使用：

```text
host.docker.internal
```

Linux Docker Engine 环境可能需要显式添加：

```bash
docker run --add-host=host.docker.internal:host-gateway ...
```

容器内的 `127.0.0.1` 指向容器自身，不是宿主机。

---

## 五、数据卷

### 查看、创建和检查卷

```bash
docker volume ls
docker volume create app-data
docker volume inspect app-data
```

### 删除卷

```bash
docker volume rm app-data
```

删除卷通常意味着删除其中的数据。数据库卷不能仅凭“当前没有容器使用”就判断为无价值。

### 查看卷中的文件

```bash
docker run --rm \
  -v app-data:/data:ro \
  alpine ls -la /data
```

### 备份命名卷

```bash
docker run --rm \
  -v app-data:/data:ro \
  -v "$PWD:/backup" \
  alpine tar -czf /backup/app-data.tar.gz -C /data .
```

数据库卷最好先停止写入或使用数据库自身的一致性备份工具。直接打包正在写入的数据库文件不一定得到可恢复备份。

---

## 六、Docker Compose 常用命令

### 默认配置文件

推荐文件名：

```text
compose.yaml
```

在配置文件所在目录执行：

```bash
docker compose <command>
```

指定其他配置文件：

```bash
docker compose -f compose.prod.yaml <command>
```

叠加多个配置文件：

```bash
docker compose \
  -f compose.yaml \
  -f compose.prod.yaml \
  config
```

后面的文件会覆盖或扩展前面的配置，最终结果应使用 `config` 检查。

### 验证配置

```bash
docker compose config
docker compose config -q
```

推荐在每次部署前先执行：

```bash
docker compose config -q
```

它只验证，不输出展开后的完整配置。

查看解析出的对象：

```bash
docker compose config --services
docker compose config --images
docker compose config --volumes
docker compose config --profiles
```

### 创建并启动项目

```bash
docker compose up
docker compose up -d
docker compose up -d --wait
```

区别：

- `up`：前台启动并聚合日志。
- `up -d`：后台启动。
- `up -d --wait`：后台启动，并等待服务进入 running 或 healthy。

### 启动前构建镜像

```bash
docker compose up -d --build
```

强制重建容器：

```bash
docker compose up -d --force-recreate
```

只有配置、镜像更新没有被正确识别时，才考虑强制重建。

### 拉取和构建

```bash
docker compose pull
docker compose build
docker compose build --pull
docker compose build --no-cache --pull
```

注意：

- `pull` 只拉镜像，不启动容器。
- `build` 只构建镜像，不启动服务。
- 真正应用变更通常还需要执行 `docker compose up -d`。

### 查看项目和服务状态

```bash
docker compose ls
docker compose ps
docker compose ps -a
docker compose ps --services
```

`docker compose ls` 查看 Compose 项目；`docker compose ps` 查看当前项目的服务容器。

### 查看日志

```bash
docker compose logs
docker compose logs -f
docker compose logs --tail 200 <service>
docker compose logs --since 30m -t <service>
```

### 在服务容器中执行命令

```bash
docker compose exec <service> sh
```

例如：

```bash
docker compose exec web sh
docker compose exec db psql -U postgres
```

`exec` 要求服务容器已经运行。

### 运行一次性任务

```bash
docker compose run --rm <service> <command>
```

例如：

```bash
docker compose run --rm web python manage.py migrate
```

与 `exec` 的区别：

| 命令 | 行为 |
| --- | --- |
| `compose exec` | 在已有运行容器中执行命令 |
| `compose run --rm` | 基于服务配置创建一个新的临时容器 |

默认情况下，`compose run` 不会发布服务端口；确实需要端口时可使用 `--service-ports`。

### 启停和重启服务

```bash
docker compose stop
docker compose start
docker compose restart
docker compose restart <service>
```

`restart` 只重启现有容器，不会应用 `compose.yaml` 的配置变化。配置修改后应使用：

```bash
docker compose up -d
```

### 停止并删除项目容器

```bash
docker compose down
```

默认会删除：

- Compose 创建的服务容器。
- Compose 创建的默认网络和非外部网络。

默认不会删除声明的命名卷。

删除孤儿容器：

```bash
docker compose down --remove-orphans
```

### 删除项目及数据卷

```bash
docker compose down -v
```

高风险：该命令会删除 Compose 文件声明的命名卷和容器附加的匿名卷。数据库和应用状态可能永久丢失。

声明为 `external: true` 的外部卷不由 Compose 删除，但仍应在执行前检查最终配置。

### 删除停止的服务容器

```bash
docker compose rm
docker compose rm -f <service>
```

### 查看端口、进程和资源

```bash
docker compose port <service> <container-port>
docker compose top
docker compose stats
```

例如：

```bash
docker compose port web 80
```

### 复制文件

```bash
docker compose cp ./config.yaml web:/app/config.yaml
docker compose cp web:/app/output.log ./output.log
```

### 指定项目名

```bash
docker compose -p myproject up -d
```

项目名会影响生成的容器、网络和卷名称。使用不同项目名可能创建另一套资源，而不是更新原项目。

### 使用其他环境变量文件

```bash
docker compose --env-file .env.production up -d
```

容易混淆：

- `.env` 和 `--env-file` 可用于 Compose 文件变量插值。
- 服务中的 `env_file:` 用于向容器进程注入环境变量。
- 两者作用层级不同。

### 使用 profile

```bash
docker compose --profile debug up -d
```

适合按需启动调试工具、管理后台等非默认服务。

### 临时扩容服务

```bash
docker compose up -d --scale worker=3
```

如果多个副本绑定同一个固定宿主机端口，会发生端口冲突。

### 开发时监听文件变化

```bash
docker compose watch
```

需要在 Compose 文件中配置相应的开发同步或重建规则。

---

## 七、常见操作流程

### 第一次部署 Compose 项目

```bash
docker compose config -q
docker compose pull
docker compose up -d --wait
docker compose ps
docker compose logs --tail 100
```

顺序不能颠倒的核心原因是：先验证配置，再获取镜像，最后启动并检查。

### 更新使用远程镜像的项目

```bash
docker compose pull
docker compose up -d --remove-orphans
docker compose ps
docker compose logs --tail 100
```

仅执行 `pull` 不会自动替换正在运行的容器。

### 更新需要本地构建的项目

```bash
docker compose build --pull
docker compose up -d --remove-orphans
docker compose ps
```

### 重建单个服务

```bash
docker compose build <service>
docker compose up -d --no-deps <service>
```

`--no-deps` 表示不启动或重建依赖服务，使用前要确认依赖已经正常运行。

### 排查启动失败

```bash
docker compose config -q
docker compose ps -a
docker compose logs --tail 200 <service>
docker inspect <container>
docker stats
```

建议按层排查：

1. daemon 是否可用。
2. Compose 配置是否能解析。
3. 容器是 created、running、exited 还是 unhealthy。
4. 应用日志是否报错。
5. 端口、网络、卷和权限是否符合预期。
6. CPU、内存、磁盘是否不足。

### 查看 Docker 磁盘占用

```bash
docker system df
docker system df -v
```

清理前先看详细占用，不要凭感觉删除。

---

## 八、清理命令与风险

### 按对象清理

```bash
docker container prune
docker image prune
docker network prune
docker volume prune
docker buildx prune
```

含义：

- `container prune`：删除所有停止的容器。
- `image prune`：默认删除悬空镜像。
- `network prune`：删除未使用网络。
- `volume prune`：默认删除未使用的匿名卷；增加 `-a` 后也会删除未使用的命名卷。
- `buildx prune`：删除构建缓存，后续构建会变慢。

### 全局清理

```bash
docker system prune
```

更激进：

```bash
docker system prune -a
```

包括未使用的匿名卷：

```bash
docker system prune -a --volumes
```

风险逐级增加。推荐顺序：

1. `docker system df -v` 查看占用。
2. 明确要释放的是容器、镜像、构建缓存还是卷。
3. 优先执行对应对象的 prune。
4. 最后才考虑 `docker system prune -a --volumes`。

### 高风险命令表

| 命令 | 风险 |
| --- | --- |
| `docker rm -f` | 强制停止并删除容器，未持久化数据丢失 |
| `docker volume rm` | 删除指定数据卷 |
| `docker volume prune -a` | 删除所有未使用的本地卷，包括命名卷 |
| `docker compose down -v` | 删除当前 Compose 项目的命名卷和匿名卷 |
| `docker system prune -a` | 删除所有未使用镜像，之后需要重新拉取或构建 |
| `docker system prune -a --volumes` | 同时清理匿名卷，风险最高 |
| `docker run --privileged` | 容器获得扩展宿主机权限，显著扩大安全边界 |

---

## 九、常见错误与判断方法

### Cannot connect to the Docker daemon

检查：

```bash
docker info
systemctl status docker
docker context show
ls -l /var/run/docker.sock
```

可能原因：

- daemon 未启动。
- 当前用户没有访问 socket 的权限。
- Docker context 或 `DOCKER_HOST` 配置错误。
- 当前命令运行在无法访问宿主机 socket 的沙箱或容器中。

### port is already allocated

说明宿主机端口已经被占用：

```bash
ss -ltnp
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

修改端口映射或停止真正占用端口的进程，不要随意结束不认识的服务。

### container name is already in use

```bash
docker ps -a --filter name=<container>
```

判断是继续使用、重命名，还是删除旧容器。不要看到冲突就直接 `rm -f`。

### no space left on device

```bash
df -h
df -i
docker system df -v
```

既要看磁盘容量，也要看 inode；确认空间来源后再清理。

### 容器能运行但访问不到服务

依次检查：

```bash
docker ps
docker port <container>
docker logs --tail 200 <container>
docker inspect <container>
```

重点区分：

- 应用是否监听 `0.0.0.0`。
- 容器端口是否正确。
- 是否使用 `-p` 发布到宿主机。
- 宿主机防火墙是否允许访问。

### Compose 服务之间无法通信

优先使用服务名：

```text
db:5432
redis:6379
```

不要在一个容器中使用 `localhost` 访问另一个容器。

---

## 十、最常见的概念误区

### `docker run` 和 `docker start`

- `run`：创建新容器并启动。
- `start`：启动已经存在的停止容器。

重复执行 `run` 通常会创建多个容器或产生名称冲突。

### `docker compose stop` 和 `down`

- `stop`：只停止容器，资源仍保留。
- `down`：停止并删除项目容器和网络。
- `down -v`：额外删除数据卷。

### `docker compose exec` 和 `run`

- `exec`：进入现有运行容器。
- `run`：创建一次性新容器。

### 镜像和容器

- 镜像是模板。
- 容器是模板的运行实例。
- 更新镜像不会自动更新已经存在的容器。

### `EXPOSE` 和 `-p`

- Dockerfile 的 `EXPOSE` 是镜像元数据和端口意图说明。
- `-p` 或 Compose `ports:` 才真正发布宿主机端口。

### Bind mount 和 Volume

- Bind mount：由宿主机路径管理，透明但与主机目录强耦合。
- Volume：由 Docker 管理，更适合持久数据和迁移。

---

## 十一、任务速查表

| 任务 | 命令 |
| --- | --- |
| 检查 daemon | `docker info` |
| 查看运行容器 | `docker ps` |
| 查看全部容器 | `docker ps -a` |
| 查看日志 | `docker logs --tail 200 <container>` |
| 进入容器 | `docker exec -it <container> sh` |
| 查看资源 | `docker stats` |
| 查看详细配置 | `docker inspect <container>` |
| 查看镜像 | `docker image ls` |
| 拉取镜像 | `docker pull <image>` |
| 构建镜像 | `docker build -t <image> .` |
| 查看磁盘占用 | `docker system df -v` |
| 验证 Compose | `docker compose config -q` |
| 启动 Compose | `docker compose up -d --wait` |
| 查看 Compose 状态 | `docker compose ps` |
| 查看服务日志 | `docker compose logs --tail 200 <service>` |
| 进入服务容器 | `docker compose exec <service> sh` |
| 更新远程镜像 | `docker compose pull` 后执行 `docker compose up -d` |
| 应用配置变化 | `docker compose up -d` |
| 停止但保留资源 | `docker compose stop` |
| 删除项目容器和网络 | `docker compose down` |
| 删除项目及卷 | `docker compose down -v`，高风险 |

---

## 个人理解

Docker 命令不应该靠孤立记忆，而应该围绕对象生命周期理解：

```text
镜像：pull/build -> tag -> push -> rmi
容器：run/create -> start -> logs/exec/inspect -> stop -> rm
网络：create -> connect -> inspect -> disconnect -> rm
卷：create -> mount -> backup -> rm
Compose：config -> pull/build -> up -> ps/logs -> down
```

排障时也应遵循分层顺序：

```text
CLI/daemon
  -> 配置解析
  -> 容器状态
  -> 应用日志
  -> 网络和端口
  -> 卷和权限
  -> CPU、内存、磁盘
```

只要能先判断“当前操作的对象是什么、希望它进入什么状态”，大部分 Docker 命令就不需要死记。

---

## 官方资料

- [Docker CLI reference](https://docs.docker.com/reference/cli/docker/)
- [docker container run](https://docs.docker.com/reference/cli/docker/container/run/)
- [Docker Compose CLI reference](https://docs.docker.com/reference/cli/docker/compose/)
- [docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [docker compose down](https://docs.docker.com/reference/cli/docker/compose/down/)
- [docker compose config](https://docs.docker.com/reference/cli/docker/compose/config/)
- [docker system prune](https://docs.docker.com/reference/cli/docker/system/prune/)
- [Migrate from Docker Compose V1 to V2](https://docs.docker.com/compose/releases/migrate/)
