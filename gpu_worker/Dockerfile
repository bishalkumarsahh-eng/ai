FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    git python3 python3-pip ffmpeg wget ca-certificates && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/OpenTalker/SadTalker.git /opt/SadTalker
WORKDIR /opt/SadTalker

# SadTalker is an older project; install its pinned dependencies, then CUDA PyTorch.
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    python3 -m pip install -r requirements.txt

# Download the official SadTalker checkpoints.
RUN bash scripts/download_models.sh

WORKDIR /worker
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY app.py .

ENV SADTALKER_DIR=/opt/SadTalker
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
