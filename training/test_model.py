#!/usr/bin/env python3
"""Test vLLM model across all verticals."""
import requests

URL = "http://localhost:8100/v1/chat/completions"
MODEL = "voicebook"

tests = [
    {
        "name": "Барбершоп — запись на стрижку",
        "messages": [
            {"role": "system", "content": "Ты администратор барбершопа TopCut. Веди диалог с клиентом по телефону. Помоги записаться. Услуги: стрижка, борода, комплекс. Мастера: Денис, Артур, Максим."},
            {"role": "user", "content": "Здравствуйте, хочу записаться на стрижку"},
        ],
    },
    {
        "name": "Салон красоты — маникюр",
        "messages": [
            {"role": "system", "content": "Ты администратор салона красоты Glamour. Веди диалог с клиентом по телефону. Помоги записаться. Услуги: маникюр, педикюр, окрашивание, стрижка. Мастера: Анна, Елена, Ольга."},
            {"role": "user", "content": "Добрый день, можно на маникюр записаться?"},
        ],
    },
    {
        "name": "Ресторан — бронь столика",
        "messages": [
            {"role": "system", "content": "Ты администратор ресторана Оливье. Веди диалог с клиентом по телефону. Помоги забронировать столик."},
            {"role": "user", "content": "Алло, хочу забронировать столик на вечер"},
        ],
    },
    {
        "name": "Автомойка — запись",
        "messages": [
            {"role": "system", "content": "Ты администратор автомойки АвтоБлеск. Веди диалог с клиентом по телефону. Помоги записаться. Услуги: экспресс-мойка, комплексная мойка, полировка, химчистка салона."},
            {"role": "user", "content": "Здравствуйте, хочу машину помыть, есть свободное время?"},
        ],
    },
    {
        "name": "Постоянный клиент барбершопа",
        "messages": [
            {"role": "system", "content": "Ты администратор барбершопа. Клиент: Алексей, 8 визитов, любимая услуга: стрижка. Обратись по имени."},
            {"role": "user", "content": "Привет, хочу записаться"},
        ],
    },
    {
        "name": "Отмена записи",
        "messages": [
            {"role": "system", "content": "Ты администратор барбершопа. Отвечай коротко, дружелюбно."},
            {"role": "user", "content": "Я передумал, не надо"},
        ],
    },
]

for t in tests:
    print(f"\n{'='*60}")
    print(f"ТЕСТ: {t['name']}")
    print(f"{'='*60}")
    print(f"Клиент: {t['messages'][-1]['content']}")
    try:
        r = requests.post(URL, json={
            "model": MODEL,
            "messages": t["messages"],
            "max_tokens": 200,
            "temperature": 0.7,
        }, timeout=30)
        data = r.json()
        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]
            print(f"Модель: {reply}")
        else:
            print(f"ОТВЕТ API: {data}")
    except Exception as e:
        print(f"ОШИБКА: {e}")

print(f"\n{'='*60}")
print("Тесты завершены")
