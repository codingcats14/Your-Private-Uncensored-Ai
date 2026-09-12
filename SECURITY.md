# Security and deployment notes

## Never commit model weights

The repository deliberately excludes `.gguf` and other large model files.

Download the model from its original model host instead.

## Never commit secrets

Do not commit:

- API keys
- Cloudflare tokens
- SSH keys
- passwords
- `.env` files
- private credentials

`.env` is ignored by Git.

## Public tunnels

A temporary tunnel makes your local Flask port reachable from the internet. Anyone who has the URL may be able to send prompts to your model.

For a real public deployment, add authentication, rate limiting, request limits, logging, and a persistent deployment environment.

## Model licensing

The repository code is separate from the model weights. Review the license and model-card terms for every model you download before redistributing weights or offering a hosted service.
