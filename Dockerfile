FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir grpcio-tools

# Compile Yandex Cloud proto files
RUN git clone --depth 1 https://github.com/yandex-cloud/cloudapi /tmp/yandex-cloudapi \
    && python -m grpc_tools.protoc \
        -I /tmp/yandex-cloudapi \
        --python_out=/app \
        --grpc_python_out=/app \
        /tmp/yandex-cloudapi/yandex/cloud/ai/stt/v3/*.proto \
        /tmp/yandex-cloudapi/yandex/cloud/ai/tts/v3/*.proto \
    && rm -rf /tmp/yandex-cloudapi

COPY . .

EXPOSE 8000

CMD ["python", "-m", "app.main"]
