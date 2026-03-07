"""
Generate intent classification pairs for VoiceBook fine-tuning.

Generates 2000+ pairs of (user utterance -> intent) covering:
- All 11 intents
- Colloquial Russian
- STT artifacts (missing words, merged words, typos)

Usage:
    python generate_intent_pairs.py --output raw/intent_pairs.jsonl --count 2000
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

INTENTS_WITH_EXAMPLES = {
    "book": [
        "Хочу записаться",
        "Запишите меня",
        "Можно записаться на стрижку?",
        "Ну давай запишусь",
        "Мне бы подстричься",
    ],
    "cancel": [
        "Хочу отменить запись",
        "Не приду, отмените",
        "Можно отменить?",
        "Передумал",
        "Не надо, отмена",
    ],
    "question": [
        "Сколько стоит стрижка?",
        "А как долго это займёт?",
        "У вас есть парковка?",
        "А какие услуги есть?",
        "Во сколько вы закрываетесь?",
    ],
    "select_service": [
        "Мужскую стрижку",
        "Стрижку бороды хочу",
        "Давайте комплекс",
        "Окрашивание",
        "Маникюр пожалуйста",
    ],
    "select_master": [
        "К Денису",
        "Хочу к Анне",
        "Запишите к Максиму",
        "К Кириллу если можно",
        "Давайте к Артуру",
    ],
    "any_master": [
        "Без разницы",
        "К любому",
        "Мне всё равно",
        "Кто свободен",
        "Не важно к кому",
    ],
    "select_slot": [
        "В пятницу в два",
        "Давайте в 14:30",
        "Завтра утром",
        "В субботу если можно",
        "Первый вариант подходит",
    ],
    "provide_name": [
        "Артём",
        "Меня зовут Дмитрий",
        "Александр",
        "Я Мария",
        "Анна Петровна",
    ],
    "confirm": [
        "Да",
        "Угу",
        "Ага, всё верно",
        "Подтверждаю",
        "Да, записывайте",
    ],
    "deny": [
        "Нет",
        "Не подходит",
        "Давайте другое время",
        "Неа",
        "Не, это не то",
    ],
    "unclear": [
        "Эээ...",
        "Ну такое...",
        "Я не знаю",
        "Что?",
        "А?",
    ],
}

GENERATION_PROMPT = """Generate {count} unique Russian utterances that a phone caller might say,
each expressing the intent "{intent}".

The utterances should be:
- Natural spoken Russian (not written)
- Varied: casual, formal, with slang, with hesitation
- Some with STT artifacts: missing words, merged words, wrong endings
- Different lengths: 1 word to full sentence
- Realistic for a barbershop/salon booking phone call

Examples of this intent:
{examples}

Output: JSON array of strings. No duplicates. Russian only.
Generate ONLY the JSON array."""


async def generate_utterances(
    client: AsyncOpenAI,
    intent: str,
    examples: list[str],
    count: int,
) -> list[str]:
    prompt = GENERATION_PROMPT.format(
        count=count,
        intent=intent,
        examples="\n".join(f"- {e}" for e in examples),
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    text = response.choices[0].message.content
    try:
        data = json.loads(text)
        utterances = data if isinstance(data, list) else data.get("utterances", data.get("data", []))
        return [u for u in utterances if isinstance(u, str)]
    except json.JSONDecodeError:
        logger.error(f"Failed to parse: {text[:200]}")
        return []


def to_training_pair(utterance: str, intent: str) -> dict:
    """Convert to ChatML training format with extract_intent tool call."""
    return {
        "messages": [
            {"role": "user", "content": utterance},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "id": f"call_{random.randint(100000, 999999)}",
                    "type": "function",
                    "function": {
                        "name": "extract_intent",
                        "arguments": json.dumps({"intent": intent}, ensure_ascii=False),
                    },
                }],
            },
            {
                "role": "tool",
                "tool_call_id": "placeholder",
                "content": json.dumps({"status": "ok", "intent": intent}),
            },
        ],
    }


async def main(output_path: str, total_count: int):
    client = AsyncOpenAI()

    per_intent = total_count // len(INTENTS_WITH_EXAMPLES)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    all_pairs = []

    tasks = []
    for intent, examples in INTENTS_WITH_EXAMPLES.items():
        tasks.append(generate_utterances(client, intent, examples, per_intent))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for (intent, _), result in zip(INTENTS_WITH_EXAMPLES.items(), results):
        if isinstance(result, Exception):
            logger.error(f"Failed for {intent}: {result}")
            continue
        for utterance in result:
            all_pairs.append(to_training_pair(utterance, intent))
        logger.info(f"Intent '{intent}': {len(result)} utterances")

    random.shuffle(all_pairs)

    with open(output, "w", encoding="utf-8") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    logger.info(f"Done! {len(all_pairs)} intent pairs saved to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="raw/intent_pairs.jsonl")
    parser.add_argument("--count", type=int, default=2000)
    args = parser.parse_args()

    asyncio.run(main(args.output, args.count))
