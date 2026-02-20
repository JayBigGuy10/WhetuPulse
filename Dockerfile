FROM python:3.12-slim

ENV SNAPSHOT_INTERVAL=30
ENV DAILY_VIDEO_TIME=08:00
ENV DIR=/srv/whetupulse/
ENV TZ=America/Chicago

# Install system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /srv/whetupulse

# Copy dependency files first (for Docker layer caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies into system environment
RUN uv sync --frozen --no-dev

# Copy application code
COPY app.py ./

# Create required directories
RUN mkdir -p data/images data/output

ENTRYPOINT ["uv", "run", "python", "-u", "app.py"]
