FROM python:3.8-slim

WORKDIR /app

# Install system dependencies for RocksDB and compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    librocksdb-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    libgflags-dev \
    liblz4-dev \
    libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /faust_data && useradd -m appuser && chown -R appuser /app /faust_data
USER appuser

ENTRYPOINT ["python", "main.py", "worker", "-l", "info", "--web-port", "6066"]
