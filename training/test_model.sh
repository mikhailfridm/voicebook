#!/bin/bash
# Test script for voicebook model via vLLM

API="http://localhost:8000/v1/chat/completions"
MODEL="/workspace/voicebook/models/voicebook-qwen2.5-14b"

run_test() {
    local desc="$1"
    local system="$2"
    local user="$3"
    echo ""
    echo "=========================================="
    echo "TEST: $desc"
    echo "USER: $user"
    echo "=========================================="

    python3 -c "
import json, urllib.request

data = json.dumps({
    'model': '$MODEL',
    'messages': [
        {'role': 'system', 'content': '''$system'''},
        {'role': 'user', 'content': '''$user'''}
    ],
    'max_tokens': 200,
    'temperature': 0.7
}).encode()

req = urllib.request.Request('$API', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
print('ASSISTANT:', result['choices'][0]['message']['content'])
"
}

SYSTEM="Ты голосовой ассистент барбершопа TopCut. Услуги: стрижка (1500р), борода (1000р), комплекс (2200р). Мастера: Денис, Артур, Максим, Рустам. Работаем 10:00-21:00."

run_test "Простая запись" \
    "$SYSTEM" \
    "Хочу подстричься"

run_test "Вопрос о цене" \
    "$SYSTEM" \
    "Сколько стоит стрижка?"

run_test "Комплекс" \
    "$SYSTEM" \
    "Хочу стрижку и бороду"

run_test "Отмена записи" \
    "$SYSTEM" \
    "Мне нужно отменить запись"

run_test "Жалоба" \
    "$SYSTEM" \
    "Мне стрижка не понравилась в прошлый раз"

run_test "Выбор мастера" \
    "$SYSTEM" \
    "А кто у вас лучший мастер?"

run_test "Неправильный номер" \
    "$SYSTEM" \
    "Алло, это пиццерия?"

run_test "Опоздание" \
    "$SYSTEM" \
    "Я опаздываю минут на 15"

run_test "Дорого" \
    "$SYSTEM" \
    "Дорого у вас"

run_test "Возвращающийся клиент" \
    "Ты голосовой ассистент барбершопа TopCut. Постоянный клиент: Алексей, 10 визитов, обычно стрижка у Дениса." \
    "Привет, это Алексей"

echo ""
echo "=========================================="
echo "ALL TESTS COMPLETE"
echo "=========================================="
