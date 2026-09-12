# Mikey — Private AI

> A personal AI chatbot with a Windows Command Prompt-inspired interface, powered by a local GGUF model through `llama.cpp`.

![Mikey terminal UI](https://placehold.co/1200x650/0c0c0c/cccccc?text=Mikey+%7C+your+private+AI)

## What is Mikey?

Mikey is a lightweight web interface around a locally running LLM.

The project separates the **AI inference engine** from the **user interface**:

```text
                    ┌─────────────────────┐
                    │       Browser       │
                    │   CMD-style UI      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask / Mikey    │
                    │      :5000          │
                    └──────────┬──────────┘
                               │
                    OpenAI-compatible API
                               │
                               ▼
                    ┌─────────────────────┐
                    │     llama.cpp       │
                    │      :8080          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Qwen3 14B GGUF      │
                    │      Q4_K_M         │
                    └─────────────────────┘
```

The default Kaggle configuration uses `bartowski/huihui-ai_Qwen3-14B-abliterated-GGUF` and its Q4_K_M GGUF file. The model repository currently lists the model as Apache-2.0 licensed and provides llama.cpp usage instructions. citeturn0search0turn0search3

## Features

- 🧠 Local/self-hosted LLM inference
- ⚡ `llama.cpp` backend
- 🎮 Kaggle GPU notebook workflow
- 🖥️ Windows CMD-inspired browser UI
- `you>` user prompt
- `mikey> ... Thinking` inference state
- `mikey>` assistant output
- 🕶️ No chat bubbles or dashboard cards
- 🔌 OpenAI-compatible llama.cpp API
- 🧹 Removes `<think>...</think>` blocks from displayed output
- 🌐 Optional temporary Cloudflare Quick Tunnel in the Kaggle notebook
- 🔒 Model weights and secrets are excluded from Git

## Repository structure

```text
Mikey-private-ai/
│
├── app.py
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docs/
│   ├── architecture.md
│   └── SECURITY.md
│
├── scripts/
│   ├── run_app.sh
│   └── start_llama.sh
│
└── kaggle/
    └── Mikey_Kaggle_FINAL.ipynb
```

## Quick start — Kaggle

The easiest way to reproduce the GPU setup is the notebook:

**`kaggle/Mikey_Kaggle_FINAL.ipynb`**

### 1. Create a Kaggle Notebook

Create a new Kaggle notebook and enable GPU acceleration.

The supplied notebook is designed around the working two-GPU Kaggle setup used for this project.

### 2. Upload/open the notebook

Open:

```text
kaggle/Mikey_Kaggle_FINAL.ipynb
```

### 3. Run cells from top to bottom

The notebook:

1. prepares the environment
2. downloads the selected GGUF model
3. prepares `llama-server`
4. starts the model server on port `8080`
5. starts Mikey's Flask UI on port `5000`
6. verifies the UI
7. can start a temporary Cloudflare Quick Tunnel

### 4. Open the public URL

The final Cloudflare cell prints a `trycloudflare.com` URL.

Open that URL in your browser.

If the tunnel is unavailable, first verify the local Flask service:

```text
http://127.0.0.1:5000
```

inside the Kaggle runtime.

## Local setup

You can also run the Flask application outside Kaggle.

### Requirements

- Python 3.10+
- Flask
- Requests
- a running `llama-server`
- a compatible GGUF model
- enough RAM/VRAM for the model and context you choose

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Start llama.cpp

Install `llama.cpp` using its official instructions or a suitable prebuilt binary.

Then start:

```bash
./llama-server   -m ./models/huihui-ai_Qwen3-14B-abliterated-Q4_K_M.gguf   --host 127.0.0.1   --port 8080
```

`llama-server` provides an OpenAI-compatible HTTP API, including `/v1/chat/completions`. citeturn0search2

### Start Mikey

In another terminal:

```bash
python app.py
```

Then visit:

```text
http://127.0.0.1:5000
```

## Environment variables

Copy `.env.example` and configure your environment as needed.

| Variable | Default | Purpose |
|---|---|---|
| `AI_NAME` | `Mikey` | UI branding |
| `WEB_PORT` | `5000` | Flask web port |
| `LLAMA_URL` | `http://127.0.0.1:8080` | llama.cpp server |
| `TEMPERATURE` | `0.8` | Sampling temperature |
| `TOP_P` | `0.95` | Nucleus sampling |
| `MAX_TOKENS` | `2000` | Maximum generated tokens |

## Changing the AI's name

Set:

```bash
AI_NAME=YourName
```

or change the default in `app.py`.

The browser title and UI use the configured name.

The command prompts remain intentionally:

```text
you>
mikey>
```

because that is the project's current visual identity.

## API endpoints

### Health

```http
GET /health
```

Example:

```json
{
  "status": "ok",
  "service": "Mikey",
  "llama_url": "http://127.0.0.1:8080"
}
```

### Chat

```http
POST /chat
Content-Type: application/json
```

Body:

```json
{
  "message": "Hello Mikey"
}
```

Response:

```json
{
  "response": "Hello! How can I help?"
}
```

## Model

The default notebook uses:

```text
bartowski/huihui-ai_Qwen3-14B-abliterated-GGUF
```

with:

```text
huihui-ai_Qwen3-14B-abliterated-Q4_K_M.gguf
```

The model card describes this as a GGUF quantization of `huihui-ai/Qwen3-14B-abliterated` and provides llama.cpp instructions. citeturn0search3turn0search4

**The model file is intentionally not included in this GitHub repository.**

It is several gigabytes in size and should be downloaded from the model host.

## Why llama.cpp?

`llama.cpp` provides a lightweight inference runtime and an OpenAI-compatible `llama-server`. Its server exposes `/v1/chat/completions`, which makes it straightforward for a small Flask application to act as the UI layer. citeturn0search2

## Privacy

Mikey is designed around local inference:

```text
Your browser
     ↓
Your Flask server
     ↓
Your llama.cpp process
     ↓
Your model
```

When running locally, prompts do not need to be sent to a third-party AI API.

**Important:** if you expose the Flask server using a public tunnel, requests can reach your machine/runtime from the internet. Treat the public URL as public access and add authentication/rate limiting before using this as a real service.

## Cloudflare Quick Tunnel

The Kaggle notebook can use a temporary Cloudflare Quick Tunnel for testing.

This is useful for:

- sharing a prototype
- testing the UI from another device
- demonstrating the project

It is **not** the recommended architecture for production hosting.

For a persistent deployment, use a proper server/VM and configure authentication, TLS, rate limiting, monitoring, and a persistent tunnel or reverse proxy.

## Important: model licensing

The code in this repository is released under the MIT License.

That does **not** mean the model weights are MIT licensed.

The default GGUF model repository currently lists Apache-2.0 for its model artifact, but you should review the model card and upstream/base-model terms before redistributing weights or using the model commercially. citeturn0search0turn0search11

## Contributing

Pull requests are welcome.

Good areas for contributions:

- conversation history
- streaming responses
- authentication
- multi-user sessions
- configurable system prompts
- model switching
- better GPU detection
- persistent chat storage
- rate limiting
- production deployment configuration
- mobile terminal styling

## Roadmap

- [ ] Conversation memory
- [ ] Streaming token output
- [ ] System prompt editor
- [ ] Model selector
- [ ] Authentication
- [ ] Multi-user support
- [ ] Persistent conversations
- [ ] Production deployment guide
- [ ] Optional voice interface

## Disclaimer

This project is a personal/self-hosting framework. The model's responses are generated by the selected model and are not guaranteed to be accurate, safe, or appropriate.

Do not expose an unauthenticated inference server to the public internet for production use.

## License

The Mikey application code is licensed under the MIT License.

See [`LICENSE`](LICENSE).

Model weights are **not included** and remain subject to their own licenses and terms.
