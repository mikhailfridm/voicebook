import requests
import json

URL = "http://localhost:8000/v1/chat/completions"
MODEL = "/workspace/voicebook/models/voicebook-qwen2.5-14b"

tests = [
    {
        "name": "Запись на стрижку",
        "messages": [
            {"role": "system", "content": "Ты голосовой ассистент барбершопа TopCut. Отвечай коротко, дружелюбно. Услуги: стрижка, борода, комплекс. Мастера: Денис, Артур, Максим."},
            {"role": "user", "content": "Хочу подстричься"},
        ],
    },
    {
        "name": "Вопрос о цене",
        "messages": [
            {"role": "system", "content": "Ты голосовой ассистент барбершопа TopCut. Отвечай коротко. Стрижка от 1500р, борода от 1000р, комплекс от 2000р."},
            {"role": "user", "content": "Сколько стрижка стоит?"},
        ],
    },
    {
        "name": "Постоянный клиент",
        "messages": [
            {"role": "system", "content": "Ты голосовой ассистент барбершопа. Клиент: Алексей, 8 визитов, любимая услуга: стрижка. Обратись по имени."},
            {"role": "user", "content": "Привет, хочу записаться"},
        ],
    },
    {
        "name": "Отмена",
        "messages": [
            {"role": "system", "content": "Ты голосовой ассистент барбершопа. Отвечай коротко."},
            {"role": "user", "content": "Я передумал, не надо"},
        ],
    },
]

for t in tests:
    print(f"\n=== {t['name']} ===")
    print(f"User: {t['messages'][-1]['content']}")
    try:
        r = requests.post(URL, json={
            "model": MODEL,
            "messages": t["messages"],
            "max_tokens": 150,
        })
        data = r.json()
        reply = data["choices"][0]["message"]["content"]
        print(f"Bot:  {reply}")
    except Exception as e:
        print(f"Error: {e}")

print("\n=== Done ===")
