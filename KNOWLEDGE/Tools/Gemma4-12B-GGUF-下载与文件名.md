# Gemma 4 12B GGUF 下载与文件名

## 本质

Gemma 4 12B 的官方本地部署路径，优先选 Hugging Face 的 GGUF 量化仓库，而不是 ModelScope 上的 BF16 safetensors 仓库。

对本地 `llama.cpp` 来说，真正可直接部署的是 GGUF 文件；多模态版本还需要单独的 `mmproj` 文件。

## 已验证仓库

官方 GGUF 仓库：

- `google/gemma-4-12B-it-qat-q4_0-gguf`

已验证文件名：

- `gemma-4-12b-it-qat-q4_0.gguf`
- `mmproj-gemma-4-12b-it-qat-q4_0.gguf`

## 下载经验

在当前环境里，Hugging Face 直连下载需要：

```bash
curl -k --http1.1 -L ...
```

如果不加 `-k` 或 `--http1.1`，容易遇到 TLS 中断。

## 本地位置

建议放在：

```text
/home/zj970/models/multimodal
```

例如：

```text
/home/zj970/models/multimodal/gemma-4-12b-it-qat-q4_0.gguf
/home/zj970/models/multimodal/mmproj-gemma-4-12b-it-qat-q4_0.gguf
```

## 启动验证

在 8GB 显存机器上，先按文本模型启动：

```bash
llama-server \
  -m /home/zj970/models/multimodal/gemma-4-12b-it-qat-q4_0.gguf \
  --host 127.0.0.1 \
  --port 8088 \
  --alias gemma-4-12b-it-q4 \
  --ctx-size 4096 \
  --gpu-layers auto \
  --fit on \
  --reasoning off
```

验证模型列表：

```bash
curl -sS http://127.0.0.1:8088/v1/models
```

验证对话：

```bash
curl -sS -H 'Content-Type: application/json' \
  -d '{"model":"gemma-4-12b-it-q4","messages":[{"role":"user","content":"请用一句话说明你是什么模型。"}],"max_tokens":80,"temperature":0.2}' \
  http://127.0.0.1:8088/v1/chat/completions
```

## 当前限制

旧版 `llama.cpp b8840` 会在加载 `mmproj` 时失败：

```text
unknown projector type: gemma4uv
```

这说明问题不是模型文件本身，而是运行时使用的 `llama.cpp` / `libmtmd` 版本过旧。  
升级到包含 `PROJECTOR_TYPE_GEMMA4UV` 的新源码后，`mmproj` 可以正常加载。

## 已验证结果

当前已验证：

- 新构建的 `llama-server` 能识别 `gemma4uv`
- `mmproj` 加载成功
- `/v1/models` 返回 `capabilities: ["completion","multimodal"]`
- 文本对话可正常返回

实际启动时需要注意：

- 旧安装目录和新构建目录不要混用
- 如遇到旧库干扰，可用 `LD_LIBRARY_PATH=/home/zj970/github/llama.cpp/build/bin` 强制指向新库

## 个人理解

判断一个多模态模型能不能本地跑，除了看参数和量化，还要看仓库是否同时提供主权重和 `mmproj`。  
如果只有主权重，没有投影文件，多模态能力通常无法完整落地。  
如果投影文件已经有了，还要再确认运行时库是否真的支持对应的 projector 类型。
