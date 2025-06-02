# 1. Base image
FROM python:3.11-slim

# 2. Set workdir
WORKDIR /app

# 3. Install system deps (add OpenCV libs) then Python deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # your Python deps (FastAPI, Mediapipe, etc.)

# 4. Copy app code
COPY . .

# 5. Expose port and run
ENV PORT 8080
EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]