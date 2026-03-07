"""
Generate synthetic training dialogs for VoiceBook fine-tuning.

Uses GPT-4o as "teacher" to generate realistic booking conversations
with proper tool calling format for Qwen2.5.

Usage:
    python generate_dialogs.py --output raw/dialogs.jsonl --count 600
"""

import argparse
import asyncio
import json
import random
import logging
from pathlib import Path

from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Salon variations for diverse training data
SALONS = [
    {
        "name": "Барбершоп TopCut",
        "services": ["Мужская стрижка", "Стрижка бороды", "Комплекс стрижка + борода", "Королевское бритьё"],
        "masters": ["Денис", "Артур", "Максим", "Илья"],
        "hours": "10:00–21:00",
    },
    {
        "name": "Салон красоты Луна",
        "services": ["Женская стрижка", "Окрашивание", "Маникюр", "Укладка", "Кератиновое выпрямление"],
        "masters": ["Анна", "Екатерина", "Мария", "Ольга"],
        "hours": "09:00–20:00",
    },
    {
        "name": "Барбершоп Бритва",
        "services": ["Мужская стрижка", "Моделирование бороды", "Камуфляж седины", "Детская стрижка"],
        "masters": ["Алексей", "Дмитрий", "Кирилл"],
        "hours": "10:00–22:00",
    },
]

SCENARIOS = [
    {
        "type": "happy_path",
        "description": "Клиент хочет записаться, выбирает услугу, мастера, слот, называет имя. Полный цикл.",
        "weight": 200,
    },
    {
        "type": "any_master",
        "description": "Клиент хочет записаться, но ему всё равно к какому мастеру.",
        "weight": 50,
    },
    {
        "type": "cancel_early",
        "description": "Клиент начинает записываться, но на этапе выбора услуги или мастера говорит 'не надо' / 'передумал'.",
        "weight": 40,
    },
    {
        "type": "cancel_late",
        "description": "Клиент дошёл до выбора слота, но передумал и отказался.",
        "weight": 40,
    },
    {
        "type": "question_during_booking",
        "description": "Клиент задаёт вопрос посреди записи (сколько стоит? как долго? есть ли парковка?).",
        "weight": 80,
    },
    {
        "type": "slot_deny_retry",
        "description": "Клиенту не подходят предложенные слоты, он просит другой день/время.",
        "weight": 60,
    },
    {
        "type": "unclear_speech",
        "description": "Клиент говорит невнятно, с ошибками STT, бот переспрашивает.",
        "weight": 50,
    },
    {
        "type": "existing_client_cancel",
        "description": "Клиент звонит чтобы отменить существующую запись.",
        "weight": 40,
    },
    {
        "type": "change_mind",
        "description": "Клиент сначала выбрал одну услугу, потом передумал на другую.",
        "weight": 40,
    },
]

INTENTS = [
    "book", "cancel", "question", "select_service", "select_master",
    "any_master", "select_slot", "provide_name", "confirm", "deny", "unclear"
]

TOOL_DEFINITIONS = """Available functions (MUST use extract_intent for every user turn):
1. extract_intent(intent, service_name?, master_name?, preferred_date?, preferred_time?, client_name?)
   - intent: one of [book, cancel, question, select_service, select_master, any_master, select_slot, provide_name, confirm, deny, unclear]
2. check_slots(staff_id, service_id, date)
3. create_booking(staff_id, service_id, datetime, client_name, client_phone)
4. cancel_booking(record_id)"""

GENERATION_PROMPT = """You are generating training data for a Russian-language voice booking AI assistant.

Generate a COMPLETE phone dialog in Russian between a client and a voice assistant of "{salon_name}".

Salon info:
- Services: {services}
- Masters: {masters}
- Hours: {hours}

Scenario: {scenario_description}

{tool_definitions}

Rules:
- Dialog must be in Russian, natural spoken language (no markdown, no emoji)
- Client speaks casually, may use slang, incomplete sentences
- Assistant is short, friendly, 1-2 sentences max
- EVERY assistant turn MUST include an extract_intent tool call BEFORE the text response
- When checking slots, use check_slots with made-up but realistic IDs
- When booking, use create_booking
- Include realistic dates/times (within next 2 weeks)
- Client phone: use random +7999XXXXXXX format

Output format: JSON array of messages in OpenAI ChatML format.
Each message has "role" (user/assistant/tool) and "content".
Assistant messages with tool calls use "tool_calls" field.
Tool results use "role": "tool" with "tool_call_id".

Generate ONLY the JSON array, no explanation."""


async def generate_one_dialog(
    client: AsyncOpenAI,
    salon: dict,
    scenario: dict,
) -> list[dict]:
    """Generate one training dialog."""
    prompt = GENERATION_PROMPT.format(
        salon_name=salon["name"],
        services=", ".join(salon["services"]),
        masters=", ".join(salon["masters"]),
        hours=salon["hours"],
        scenario_description=scenario["description"],
        tool_definitions=TOOL_DEFINITIONS,
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )

    text = response.choices[0].message.content
    try:
        data = json.loads(text)
        messages = data if isinstance(data, list) else data.get("messages", data.get("dialog", []))
        return messages
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON: {text[:200]}")
        return []


def build_system_prompt(salon: dict) -> str:
    """Build the system prompt that will be used during training."""
    return f"""Ты — голосовой ассистент {salon['name']}. Твоя задача — записать клиента на услугу.

Правила:
- Отвечай коротко (1-2 предложения), дружелюбно, по делу
- Говори на русском языке
- Не используй markdown, эмодзи, скобки — ты говоришь голосом
- Если клиент хочет записаться, спроси какую услугу и к какому мастеру
- Если клиент не определился с мастером — предложи любого свободного
- Предлагай 2-3 варианта времени
- Если 2 раза подряд не понял клиента — скажи "Одну секунду, соединяю с администратором"

Доступные услуги: {', '.join(salon['services'])}
Мастера: {', '.join(salon['masters'])}
Часы работы: {salon['hours']}

ВАЖНО: После КАЖДОГО ответа клиента ОБЯЗАТЕЛЬНО вызови функцию extract_intent.
Когда нужно проверить свободные слоты — вызови check_slots.
Когда все данные собраны — вызови create_booking."""


def build_training_example(salon: dict, dialog_messages: list[dict]) -> dict:
    """Wrap dialog in training format with system prompt."""
    system_msg = {"role": "system", "content": build_system_prompt(salon)}
    return {"messages": [system_msg] + dialog_messages}


async def main(output_path: str, total_count: int):
    client = AsyncOpenAI()

    # Build weighted scenario list
    scenarios_weighted = []
    for s in SCENARIOS:
        count = int(s["weight"] * total_count / sum(sc["weight"] for sc in SCENARIOS))
        scenarios_weighted.extend([s] * max(1, count))
    random.shuffle(scenarios_weighted)
    scenarios_weighted = scenarios_weighted[:total_count]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    generated = 0
    batch_size = 10

    with open(output, "w", encoding="utf-8") as f:
        for i in range(0, len(scenarios_weighted), batch_size):
            batch = scenarios_weighted[i:i + batch_size]
            tasks = []
            for scenario in batch:
                salon = random.choice(SALONS)
                tasks.append(generate_one_dialog(client, salon, scenario))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for j, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Generation failed: {result}")
                    continue
                if not result:
                    continue

                salon = random.choice(SALONS)
                example = build_training_example(salon, result)
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
                generated += 1

            logger.info(f"Generated {generated}/{total_count} dialogs")

    logger.info(f"Done! {generated} dialogs saved to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="raw/dialogs.jsonl")
    parser.add_argument("--count", type=int, default=600)
    args = parser.parse_args()

    asyncio.run(main(args.output, args.count))
