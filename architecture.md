# Architecture

Mikey is a thin private-AI interface rather than a model implementation.

```text
Browser
   │
   ▼
Mikey Flask UI (:5000)
   │
   │ OpenAI-compatible HTTP
   ▼
llama-server (:8080)
   │
   ▼
Qwen3 14B GGUF
   │
   ▼
GPU(s)
```

## Components

### 1. Web interface
`app.py` provides a minimal Windows CMD-inspired browser UI. It intentionally avoids a dashboard/card design.

The interface uses:

- `you>` for user prompts
- `mikey> ... Thinking` while inference is running
- `mikey>` for model output
- Cascadia Mono / Cascadia Code / Consolas fallback fonts
- CMD-like `#0c0c0c` background
- no model weights in the repository

### 2. llama.cpp
`llama-server` is the inference server. It exposes an OpenAI-compatible chat endpoint at:

`/v1/chat/completions`

Mikey sends the user's message to that endpoint and renders the response.

### 3. Model
The default Kaggle setup uses the GGUF Q4_K_M quantization of:

`bartowski/huihui-ai_Qwen3-14B-abliterated-GGUF`

The model itself is not stored in this repository.

### 4. Public access
The Kaggle notebook can create a temporary Cloudflare Quick Tunnel from port 5000. A Quick Tunnel is intended for testing and development; it is not a production hosting solution.
