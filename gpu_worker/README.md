# Velocity Cartoon GPU Lip-Sync Worker

The Telegram bot runs on Heroku as a worker. Lip-sync inference runs on a separate NVIDIA GPU server.

## Heroku bot app

Procfile:
- `worker: python bot.py`
- `web: uvicorn gpu_worker.app:app --host 0.0.0.0 --port $PORT`

The web dyno is included only so `/` and `/health` work on the Heroku app. It is **not** a GPU runtime.

Set these Heroku Config Vars on the bot app:

`LIPSYNC_API_URL=https://YOUR-GPU-SERVER`
`LIPSYNC_API_KEY=your-secret-key`

## GPU server

Build the `gpu_worker` directory with its Dockerfile on a service that provides an NVIDIA GPU and Docker + NVIDIA runtime.

Set:

`GPU_WORKER_KEY=the-same-secret-key`
`SADTALKER_TIMEOUT=900`

Expose port 8000 over HTTPS and use that URL as `LIPSYNC_API_URL`.

## Important

A normal Heroku web dyno does not provide NVIDIA CUDA. Adding a web dyno fixes the H14 routing error, but cannot turn Heroku into a GPU machine. The actual SadTalker process must run on the separate GPU server.
