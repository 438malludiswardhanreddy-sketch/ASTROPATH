FROM python:3.12-slim

# Install minimal system deps (adjust as needed for OpenCV/TensorFlow)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl ca-certificates \
    libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy sources
COPY . /app

# Install Python deps (use a smaller requirements file in CI/production if needed)
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Use waitress in production (lightweight WSGI)
EXPOSE 5000
CMD ["waitress-serve", "--call", "src.dashboard:create_app", "--listen=0.0.0.0:5000"]
