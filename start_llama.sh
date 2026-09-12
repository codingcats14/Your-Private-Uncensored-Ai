#!/usr/bin/env bash
set -e

# Adjust MODEL_PATH and LLAMA_SERVER to your machine.
MODEL_PATH="${MODEL_PATH:-./models/huihui-ai_Qwen3-14B-abliterated-Q4_K_M.gguf}"
LLAMA_SERVER="${LLAMA_SERVER:-./llama-server}"

"$LLAMA_SERVER"   -m "$MODEL_PATH"   --host 127.0.0.1   --port 8080
