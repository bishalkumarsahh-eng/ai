# Velocity Cartoon GPU Worker

This is the GPU side of the long-video pipeline. The Heroku bot stays CPU-only and sends each
portrait + WAV to this service. The worker runs SadTalker locally on an NVIDIA CUDA GPU and
returns the generated MP4.

## Deploy
Use a GPU VM/container service that supports Docker + NVIDIA GPUs. Build this folder as a
Docker image and expose port 8000 over HTTPS.

Set:
GPU_WORKER_KEY=your-long-random-secret
SADTALKER_TIMEOUT=900

Then set these Heroku Config Vars:
LIPSYNC_API_URL=https://YOUR-GPU-HOST
LIPSYNC_API_KEY=the-same-secret

## Health
GET /health

## Important
A persistent free public GPU is not generally available. Heroku remains the controller; the
GPU worker needs a GPU runtime. SadTalker itself is designed for audio-driven talking-face
animation from a still image. See the official project for model/checkpoint details.
