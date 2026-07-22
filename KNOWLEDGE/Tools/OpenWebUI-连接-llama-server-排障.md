# Open WebUI 连接 llama-server 排障

## 本质

Open WebUI 可以连接 `llama.cpp` 的 `llama-server`，连接方式是 OpenAI-compatible API。关键不是选择 Ollama 后端，而是在 Open WebUI 的 OpenAI API Connections 中配置 `llama-server` 的 `/v1` 地址。

## 基本链路

```text
GGUF 模型
  -> llama-server
  -> OpenAI-compatible HTTP API
  -> Open WebUI
  -> 浏览器聊天界面
```

典型启动命令：

```bash
llama-server \
  -m /path/to/model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --alias local-gguf
```

最小验证命令：

```bash
curl http://127.0.0.1:8080/v1/models
```

能返回模型列表，才继续配置 Open WebUI。

## 常见错误

### curl: (7) Failed to connect

现象：

```text
curl: (7) Failed to connect to 127.0.0.1 port 8080: Could not connect to server
```

含义：TCP 连接没有建立成功。此时还没有进入 HTTP API 层，通常不是 OpenAI 协议问题。

优先检查：

```bash
ps -ef | grep llama-server
ss -ltnp | grep 8080
```

可能原因：

- `llama-server` 没有启动。
- 端口不是 `8080`。
- 服务启动失败后退出。
- 监听地址不是当前访问的地址。
- Open WebUI 在 Docker 容器里，容器内的 `localhost` 不是宿主机。

## Open WebUI 配置

宿主机直接运行 Open WebUI：

```text
Base URL: http://127.0.0.1:8080/v1
API Key: sk-no-key-required
```

Open WebUI 在 Docker 中，`llama-server` 在宿主机中：

```text
Base URL: http://host.docker.internal:8080/v1
API Key: sk-no-key-required
```

两个服务都在同一个 Docker Compose 网络中：

```text
Base URL: http://llama-server:8080/v1
API Key: sk-no-key-required
```

## 个人理解

本地模型 Web UI 的问题要分层看：

1. 进程层：`llama-server` 有没有运行。
2. 端口层：目标地址和端口有没有监听。
3. HTTP 层：`/v1/models`、`/v1/chat/completions` 是否能返回。
4. Web UI 层：Open WebUI 的 Base URL、API Key、模型选择是否正确。

只有前一层成立，后一层排查才有意义。
