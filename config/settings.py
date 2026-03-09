from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Zadarma
    zadarma_api_key: str = ""
    zadarma_api_secret: str = ""
    zadarma_sip_login: str = ""
    zadarma_sip_password: str = ""
    zadarma_sip_server: str = ""

    # Yandex Cloud
    yandex_cloud_api_key: str = ""
    yandex_cloud_folder_id: str = ""

    # OpenAI
    openai_api_key: str = ""

    # Yclients
    yclients_partner_token: str = ""
    yclients_user_token: str = ""
    yclients_company_id: str = ""

    # Chatterbox TTS (self-hosted, MIT license)
    chatterbox_tts_base_url: str = "http://localhost:8150"
    chatterbox_tts_voice: str = "default"
    tts_provider: str = "chatterbox"  # "chatterbox", "fish", or "yandex"

    # Fish Speech TTS (self-hosted) — backup, not used yet
    fish_tts_base_url: str = "http://localhost:8080"
    fish_tts_reference_id: str = ""

    # LLM
    llm_provider: str = "vllm"  # "openai", "yandexgpt", or "vllm"
    vllm_base_url: str = "http://localhost:8100/v1"
    vllm_model_name: str = "voicebook"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
