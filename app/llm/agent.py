"""
LLM Agent for VoiceBook — handles dialog generation and intent extraction.
Supports OpenAI and YandexGPT via provider abstraction.
"""

import json
import logging
from app.llm.provider import LLMProvider, LLMResponse, create_provider
from app.core.state_machine import Intent, SessionContext

logger = logging.getLogger(__name__)

# Function definitions for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_slots",
            "description": "Check available time slots for a master on a specific date",
            "parameters": {
                "type": "object",
                "properties": {
                    "staff_id": {"type": "integer", "description": "Master/staff ID"},
                    "service_id": {"type": "integer", "description": "Service ID"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                },
                "required": ["staff_id", "service_id", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Create a booking for the client",
            "parameters": {
                "type": "object",
                "properties": {
                    "staff_id": {"type": "integer"},
                    "service_id": {"type": "integer"},
                    "datetime": {"type": "string", "description": "Booking datetime in YYYY-MM-DD HH:MM format"},
                    "client_name": {"type": "string"},
                    "client_phone": {"type": "string"},
                },
                "required": ["staff_id", "service_id", "datetime", "client_name", "client_phone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Cancel an existing booking by record ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_id": {"type": "integer", "description": "Booking record ID to cancel"},
                },
                "required": ["record_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_client",
            "description": "Look up a client by phone number to get their name and visit history",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Client phone number"},
                },
                "required": ["phone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_intent",
            "description": "ALWAYS call this function to extract user intent and relevant data from user message",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": [i.value for i in Intent],
                        "description": "The detected user intent",
                    },
                    "service_name": {"type": "string", "description": "Service name if mentioned"},
                    "master_name": {"type": "string", "description": "Master name if mentioned"},
                    "preferred_date": {"type": "string", "description": "Date preference if mentioned"},
                    "preferred_time": {"type": "string", "description": "Time preference if mentioned"},
                    "client_name": {"type": "string", "description": "Client name if provided"},
                },
                "required": ["intent"],
            },
        },
    },
]


def build_system_prompt(salon_config: dict, client_info: dict = None) -> str:
    name = salon_config.get("name", "нашего салона")
    services_text = ", ".join(salon_config.get("services", ["стрижка", "окрашивание", "укладка"]))
    masters_text = ", ".join(salon_config.get("masters", []))
    hours = salon_config.get("hours", "10:00–21:00")

    prompt = f"""Ты — голосовой ассистент {name}. Твоя задача — записать клиента на услугу.

Правила:
- Отвечай коротко (1-2 предложения), дружелюбно, по делу
- Обращайся на вы
- Говори на русском языке
- Не используй markdown, эмодзи, скобки — ты говоришь голосом
- Если клиент хочет записаться, спроси какую услугу и к какому мастеру
- Если клиент не определился с мастером — предложи любого свободного
- Предлагай 2-3 варианта времени
- Если 2 раза подряд не понял клиента — скажи "Одну секунду, соединяю с администратором"

Доступные услуги: {services_text}
Мастера: {masters_text}
Часы работы: {hours}"""

    if client_info and client_info.get("name"):
        client_name = client_info["name"]
        visits = client_info.get("visits_count", 0)
        favorite = client_info.get("favorite_service")
        history = client_info.get("service_history", {})

        prompt += f"""

ИНФОРМАЦИЯ О КЛИЕНТЕ (определён по номеру телефона):
- Имя: {client_name}
- Количество визитов: {visits}"""
        if favorite:
            prompt += f"\n- Любимая услуга: {favorite}"
        if history:
            history_text = ", ".join(f"{svc} ({cnt} раз)" for svc, cnt in history.items())
            prompt += f"\n- История услуг: {history_text}"
        prompt += """

ВАЖНО для постоянного клиента:
- Обратись по имени в приветствии
- Предложи привычную услугу (например: "Как обычно, стрижку?")
- Не спрашивай имя повторно — оно уже известно"""

    prompt += """

ВАЖНО: После КАЖДОГО ответа клиента ОБЯЗАТЕЛЬНО вызови функцию extract_intent.
Когда нужно проверить свободные слоты — вызови check_slots.
Когда все данные собраны — вызови create_booking."""

    return prompt


class DialogAgent:
    def __init__(self, salon_config: dict, provider: LLMProvider = None):
        self.provider = provider or create_provider()
        self.salon_config = salon_config
        self.system_prompt = build_system_prompt(salon_config)

    def set_client_info(self, client_info: dict):
        """Update system prompt with known client info for personalized service."""
        self.system_prompt = build_system_prompt(self.salon_config, client_info)

    async def process_message(
        self, session: SessionContext, user_text: str
    ) -> tuple[str, Intent, dict]:
        session.messages.append({"role": "user", "content": user_text})

        messages = [
            {"role": "system", "content": self.system_prompt},
            *session.messages,
        ]

        response = await self.provider.chat(
            messages=messages,
            tools=TOOLS,
            tool_choice="required",
            temperature=0.3,
            max_tokens=300,
        )

        agent_reply = response.content
        detected_intent = Intent.UNCLEAR
        extracted_data = {}

        if response.tool_calls:
            # Store assistant message with tool_calls for correct context
            assistant_msg = {
                "role": "assistant",
                "content": agent_reply,
                "tool_calls": [
                    {"id": tc["id"], "type": "function", "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"]),
                    }}
                    for tc in response.tool_calls
                ],
            }
            session.messages.append(assistant_msg)

            function_calls = []
            for tc in response.tool_calls:
                fn_name = tc["name"]
                fn_args = tc["arguments"]

                if fn_name == "extract_intent":
                    detected_intent = Intent(fn_args.get("intent", "unclear"))
                    extracted_data.update({
                        k: v for k, v in fn_args.items() if k != "intent" and v
                    })
                    session.messages.append({
                        "role": "tool", "tool_call_id": tc["id"],
                        "content": json.dumps({"status": "ok", "intent": detected_intent.value}),
                    })
                elif fn_name in ("check_slots", "create_booking", "cancel_booking", "lookup_client"):
                    function_calls.append({
                        "name": fn_name,
                        "arguments": fn_args,
                        "tool_call_id": tc["id"],
                    })

            if function_calls:
                extracted_data["_function_calls"] = function_calls
        else:
            session.messages.append({"role": "assistant", "content": agent_reply})

        logger.info(f"[{session.call_id}] LLM -> intent={detected_intent}, reply={agent_reply[:80]}")
        return agent_reply, detected_intent, extracted_data

    async def generate_greeting(self, session: SessionContext) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "[Клиент позвонил. Поприветствуй его.]"},
        ]

        response = await self.provider.chat(
            messages=messages,
            temperature=0.3,
            max_tokens=100,
        )

        greeting = response.content or "Здравствуйте! Чем могу помочь?"
        session.messages.append({"role": "assistant", "content": greeting})
        return greeting
