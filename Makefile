.PHONY: install run dev proto test

install:
	pip install -r requirements.txt

run:
	cd voicebook && python -m app.main

dev:
	cd voicebook && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

proto:
	@echo "Clone Yandex Cloud API protos and compile..."
	git clone --depth 1 https://github.com/yandex-cloud/cloudapi /tmp/yandex-cloudapi 2>/dev/null || true
	python -m grpc_tools.protoc \
		-I /tmp/yandex-cloudapi \
		--python_out=. \
		--grpc_python_out=. \
		/tmp/yandex-cloudapi/yandex/cloud/ai/stt/v3/*.proto \
		/tmp/yandex-cloudapi/yandex/cloud/ai/tts/v3/*.proto

test:
	pytest tests/ -v
