#!/usr/bin/env python3
"""Generate 500 high-quality SFT training dialogs for car wash AI voice receptionist (v2).

Scenario distribution:
  - Simple wash booking: 100
  - Premium/detailing service booking: 60
  - Multiple services combo: 50
  - Car type matters (pricing): 50
  - Time slot selection with preferences: 40
  - Time unavailable -> alternatives: 35
  - Price inquiry -> booking: 35
  - Price inquiry only (no booking): 20
  - Cancellation: 30
  - Reschedule: 30
  - User changes mind: 20
  - Regular customer / membership: 15
  - Walk-in check: 15
  - Aggressive/impatient customer: 10
  - Transfer to admin: 10
  Total: 500
"""

import json
import random
import os

random.seed(789)

SYSTEM_PROMPT = (
    "Вы — администратор автомойки. Помогаете клиентам записаться на мойку, "
    "выбрать тип услуги и удобное время. Говорите вежливо и по делу."
)

# ── Data pools ──────────────────────────────────────────────────────────────

FILLERS = [
    "ну", "эм", "так", "вот", "ааа", "короче", "слушайте", "это самое",
    "как бы", "ну это", "в общем", "типа", "значит", "ну вот", "так сказать",
]
NOISE = ["[неразборчиво]", "[шум]", "[помехи]"]
HESITATIONS = [
    "э... ", "м... ", "ну... ", "так... ", "это... ",
    "подождите... ", "секунду... ", "дайте подумать... ",
]

GREETINGS_CLIENT = [
    "Здравствуйте", "Добрый день", "Привет", "Алло", "Здрасьте", "Алё",
    "Добрый", "Здрасте", "Алло, здравствуйте", "Да, здравствуйте",
    "Добрый день, алло", "Привет, это автомойка?", "Алло, это мойка?",
    "Здравствуйте, мне нужна мойка", "Добрый день, хотел бы записаться",
    "Здрасте, это АвтоБлеск?", "Алло, это АвтоБлеск?",
]
GREETINGS_ADMIN = [
    "Здравствуйте! Автомойка «АвтоБлеск», чем могу помочь?",
    "Добрый день! Автомойка «АвтоБлеск», слушаю вас.",
    "Здравствуйте! «АвтоБлеск», чем могу быть полезен?",
    "Добрый день! Это «АвтоБлеск», слушаю вас.",
    "Здравствуйте! Автомойка «АвтоБлеск», чем помочь?",
    "Добрый день! «АвтоБлеск», рады вашему звонку. Чем могу помочь?",
    "Здравствуйте! Автомойка «АвтоБлеск», слушаю вас внимательно.",
]

CAR_MODELS_SEDAN = [
    ("Тойота Камри", "легковой"), ("Хёндай Солярис", "легковой"),
    ("Киа Рио", "легковой"), ("Фольксваген Поло", "легковой"),
    ("Шкода Октавия", "легковой"), ("Лада Веста", "легковой"),
    ("Рено Логан", "легковой"), ("Мазда 3", "легковой"),
    ("Хонда Цивик", "легковой"), ("Ниссан Альмера", "легковой"),
    ("Шевроле Круз", "легковой"), ("Форд Фокус", "легковой"),
    ("Пежо 408", "легковой"), ("Лада Гранта", "легковой"),
    ("Киа Серато", "легковой"), ("Хёндай Элантра", "легковой"),
    ("Мерседес E-класс", "легковой"), ("БМВ 5 серии", "легковой"),
    ("Ауди А6", "легковой"), ("Лексус ES", "легковой"),
]
CAR_MODELS_CROSSOVER = [
    ("Тойота РАВ4", "кроссовер"), ("Хёндай Туссан", "кроссовер"),
    ("Киа Спортейдж", "кроссовер"), ("Ниссан Кашкай", "кроссовер"),
    ("Мазда CX-5", "кроссовер"), ("Рено Дастер", "кроссовер"),
    ("Шкода Кодиак", "кроссовер"), ("Фольксваген Тигуан", "кроссовер"),
    ("Хавейл Джолион", "кроссовер"), ("Черри Тигго 7 Про", "кроссовер"),
    ("Джили Атлас", "кроссовер"), ("Чанган CS75", "кроссовер"),
    ("Порше Кайен", "кроссовер"), ("Мерседес GLE", "кроссовер"),
    ("БМВ X3", "кроссовер"), ("Ауди Q5", "кроссовер"),
]
CAR_MODELS_SUV = [
    ("Тойота Ленд Крузер", "внедорожник"), ("Мерседес GLS", "внедорожник"),
    ("БМВ X5", "внедорожник"), ("Лексус LX", "внедорожник"),
    ("Ниссан Патрол", "внедорожник"), ("Ленд Ровер", "внедорожник"),
    ("Мицубиси Паджеро", "внедорожник"), ("Кадиллак Эскалейд", "внедорожник"),
    ("Инфинити QX80", "внедорожник"), ("УАЗ Патриот", "внедорожник"),
]
CAR_MODELS_MINIVAN = [
    ("Хёндай Старекс", "минивэн"), ("Киа Карнивал", "минивэн"),
    ("Тойота Альфард", "минивэн"), ("Фольксваген Мультивэн", "минивэн"),
    ("Мерседес V-класс", "минивэн"), ("Форд Торнео", "минивэн"),
    ("Крайслер Пацифика", "минивэн"), ("Ситроен Спейс Турер", "минивэн"),
]

# ── Prices by car class ────────────────────────────────────────────────────

PRICES = {
    "легковой": {
        "экспресс": 500, "комплекс": 1000, "воск": 800,
        "полная": 1500, "химчистка": 3000, "химчистка_частичная": 1500,
        "полировка": 5000, "керамика": 15000, "нанокерамика": 10000,
        "двигатель": 800, "чернение_шин": 300, "антидождь": 1000,
    },
    "кроссовер": {
        "экспресс": 650, "комплекс": 1300, "воск": 1000,
        "полная": 1900, "химчистка": 3900, "химчистка_частичная": 2000,
        "полировка": 6500, "керамика": 19500, "нанокерамика": 13000,
        "двигатель": 1000, "чернение_шин": 400, "антидождь": 1300,
    },
    "минивэн": {
        "экспресс": 750, "комплекс": 1500, "воск": 1150,
        "полная": 2200, "химчистка": 4500, "химчистка_частичная": 2300,
        "полировка": 7500, "керамика": 22500, "нанокерамика": 15000,
        "двигатель": 1100, "чернение_шин": 450, "антидождь": 1500,
    },
    "внедорожник": {
        "экспресс": 700, "комплекс": 1400, "воск": 1100,
        "полная": 2000, "химчистка": 4200, "химчистка_частичная": 2200,
        "полировка": 7000, "керамика": 21000, "нанокерамика": 14000,
        "двигатель": 1100, "чернение_шин": 450, "антидождь": 1400,
    },
}

SERVICE_NAMES = {
    "экспресс": "экспресс-мойка кузова",
    "комплекс": "комплексная мойка кузова и салона",
    "воск": "мойка кузова с воском",
    "полная": "полная мойка с багажником",
    "химчистка": "химчистка салона",
    "химчистка_частичная": "частичная химчистка сидений",
    "полировка": "полировка кузова",
    "керамика": "керамическое покрытие",
    "нанокерамика": "нанокерамика",
    "двигатель": "мойка двигателя",
    "чернение_шин": "чернение шин",
    "антидождь": "обработка антидождём",
}

DURATIONS = {
    "экспресс": "двадцать минут",
    "комплекс": "сорок минут",
    "воск": "тридцать минут",
    "полная": "один час",
    "химчистка": "три-четыре часа",
    "химчистка_частичная": "два часа",
    "полировка": "четыре-шесть часов",
    "керамика": "один-два дня",
    "нанокерамика": "один день",
    "двигатель": "тридцать минут",
    "чернение_шин": "десять минут",
    "антидождь": "тридцать минут",
}

TIMES = [
    "восемь утра", "восемь тридцать", "девять утра", "девять тридцать",
    "десять утра", "десять тридцать", "одиннадцать утра", "одиннадцать тридцать",
    "двенадцать дня", "двенадцать тридцать", "час дня", "час тридцать",
    "два часа дня", "два тридцать", "три часа дня", "три тридцать",
    "четыре часа дня", "четыре тридцать", "пять вечера", "пять тридцать",
    "шесть вечера", "шесть тридцать", "семь вечера", "семь тридцать",
    "восемь вечера", "половина десятого", "половина одиннадцатого",
    "половина двенадцатого",
]
MORNING_TIMES = TIMES[:8]
EVENING_TIMES = TIMES[18:]

DAYS = [
    "сегодня", "завтра", "послезавтра", "в понедельник", "во вторник",
    "в среду", "в четверг", "в пятницу", "в субботу", "в воскресенье",
    "на этой неделе", "на следующей неделе",
]

CLIENT_NAMES = [
    "Александр", "Дмитрий", "Сергей", "Андрей", "Максим", "Михаил", "Иван",
    "Артём", "Николай", "Евгений", "Владимир", "Олег", "Павел", "Роман",
    "Константин", "Алексей", "Виктор", "Тимур", "Руслан", "Денис",
    "Елена", "Ольга", "Наталья", "Татьяна", "Анна", "Мария", "Светлана",
    "Ирина", "Екатерина", "Юлия",
]

PHONE_NUMBERS = [
    "восемь девятьсот пять три два один ноль ноль ноль один",
    "восемь девятьсот шестнадцать четыреста пятьдесят двенадцать тринадцать",
    "восемь девятьсот три шестьсот сорок пять двадцать три ноль пять",
    "восемь девятьсот двадцать шесть сто двадцать три сорок пять шестьдесят семь",
    "восемь девятьсот девять семьсот восемьдесят девять ноль один два три",
    "восемь девятьсот восемьдесят пять двести тридцать четыре пятьдесят шесть",
    "восемь девятьсот десять три ноль ноль двадцать один ноль пять",
    "восемь девятьсот шестьдесят три четыреста двенадцать ноль семь",
    "восемь девятьсот пятьдесят один семьсот девяносто три сорок два",
    "восемь девятьсот семьдесят четыре шестьсот одиннадцать ноль три",
]

# ── Helpers ─────────────────────────────────────────────────────────────────


def add_filler(text, prob=0.4):
    if random.random() < prob:
        filler = random.choice(FILLERS)
        pos = random.choice(["start", "mid"])
        if pos == "start":
            text = filler + ", " + text[0].lower() + text[1:]
        else:
            words = text.split()
            if len(words) > 3:
                idx = random.randint(1, len(words) - 2)
                words.insert(idx, filler + ",")
                text = " ".join(words)
    return text


def add_noise(text, prob=0.08):
    if random.random() < prob:
        words = text.split()
        if len(words) > 2:
            idx = random.randint(0, len(words) - 1)
            words[idx] = random.choice(NOISE)
            text = " ".join(words)
    return text


def add_hesitation(text, prob=0.15):
    if random.random() < prob:
        text = random.choice(HESITATIONS) + text[0].lower() + text[1:]
    return text


def naturalize(text):
    text = add_filler(text)
    text = add_noise(text)
    text = add_hesitation(text)
    if random.random() < 0.3 and len(text) > 0:
        text = text[0].lower() + text[1:]
    return text


def price_str(price):
    """Convert price integer to spoken Russian."""
    if price >= 1000:
        thousands = price // 1000
        remainder = price % 1000
        t_words = {
            1: "одна тысяча", 2: "две тысячи", 3: "три тысячи",
            4: "четыре тысячи", 5: "пять тысяч", 6: "шесть тысяч",
            7: "семь тысяч", 8: "восемь тысяч", 9: "девять тысяч",
            10: "десять тысяч", 11: "одиннадцать тысяч", 12: "двенадцать тысяч",
            13: "тринадцать тысяч", 14: "четырнадцать тысяч",
            15: "пятнадцать тысяч", 16: "шестнадцать тысяч",
            17: "семнадцать тысяч", 18: "восемнадцать тысяч",
            19: "девятнадцать тысяч", 20: "двадцать тысяч",
            21: "двадцать одна тысяча", 22: "двадцать две тысячи",
            25: "двадцать пять тысяч",
        }
        t = t_words.get(thousands, f"{thousands} тысяч")
        if remainder == 0:
            return t + " рублей"
        r_words = {
            100: "сто", 200: "двести", 300: "триста", 400: "четыреста",
            500: "пятьсот", 600: "шестьсот", 700: "семьсот", 800: "восемьсот",
            900: "девятьсот",
        }
        r = r_words.get(remainder, f"{remainder}")
        return t + " " + r + " рублей"
    else:
        w = {
            300: "триста", 400: "четыреста", 450: "четыреста пятьдесят",
            500: "пятьсот", 600: "шестьсот", 650: "шестьсот пятьдесят",
            700: "семьсот", 750: "семьсот пятьдесят", 800: "восемьсот",
            900: "девятьсот",
        }
        return w.get(price, str(price)) + " рублей"


def get_car():
    pool = random.choice([
        CAR_MODELS_SEDAN, CAR_MODELS_SEDAN, CAR_MODELS_SEDAN,
        CAR_MODELS_CROSSOVER, CAR_MODELS_CROSSOVER,
        CAR_MODELS_SUV, CAR_MODELS_MINIVAN,
    ])
    return random.choice(pool)


def get_car_by_class(cls):
    if cls == "легковой":
        return random.choice(CAR_MODELS_SEDAN)
    elif cls == "кроссовер":
        return random.choice(CAR_MODELS_CROSSOVER)
    elif cls == "внедорожник":
        return random.choice(CAR_MODELS_SUV)
    elif cls == "минивэн":
        return random.choice(CAR_MODELS_MINIVAN)
    return get_car()


def class_label(cls):
    labels = {
        "легковой": "легковой автомобиль",
        "кроссовер": "кроссовер",
        "внедорожник": "внедорожник",
        "минивэн": "минивэн",
    }
    return labels.get(cls, cls)


def begin_dialog():
    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    if random.random() < 0.2:
        convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Да, мне бы записаться", "Здравствуйте, хочу на мойку",
            "Алло, мне мойка нужна", "Да, можно записаться?",
        ]))})
    else:
        convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
        convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})
    return convos


def end_with_goodbye(convos, prob=0.6):
    if random.random() < prob:
        byes = [
            "Спасибо, до свидания!", "Спасибо!", "Ок, спасибо, пока!",
            "До свидания", "Благодарю, до встречи", "Спасибо, всего хорошего",
            "Ага, спасибо", "Ладно, спасибо, пока",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(byes))})
        convos.append({"role": "assistant", "content": random.choice([
            "До свидания! Хорошего дня!", "Всего доброго, ждём вас!",
            "До встречи! Хорошего дня!", "Пожалуйста! Всего доброго!",
        ])})
    return convos


def ask_name_and_confirm(convos, name, car_name, service_key, car_class, day, time):
    """Standard ending: ask name, confirm booking summary."""
    price = PRICES[car_class][service_key]
    sname = SERVICE_NAMES[service_key]
    convos.append({"role": "assistant", "content": (
        f"Записываю вас на {day}, {time}. {sname.capitalize()}, {car_name}, "
        f"стоимость — {price_str(price)}. Как вас зовут?"
    )})
    convos.append({"role": "user", "content": naturalize(name)})
    confirmations = [
        f"Записал вас на {sname} для {car_name}, {day} в {time}. Стоимость {price_str(price)}. Ждём вас!",
        f"Отлично, {name}! Вы записаны: {day}, {time}, {sname}, {car_name}. Стоимость — {price_str(price)}. До встречи!",
        f"Готово, {name}! {sname.capitalize()}, {car_name}, {day}, {time}. Цена — {price_str(price)}. Приезжайте за пять минут. Ждём!",
    ]
    convos.append({"role": "assistant", "content": random.choice(confirmations)})
    return convos


# ── Scenario generators ────────────────────────────────────────────────────

def gen_simple_wash():
    """Simple wash booking — happy path."""
    car_name, car_class = get_car()
    service = random.choice(["экспресс", "комплекс", "экспресс", "экспресс"])
    price = PRICES[car_class][service]
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = begin_dialog()

    requests = [
        "Хотел бы записаться на мойку",
        "Мне бы помыть машину",
        "Нужна мойка, можно записаться?",
        f"Хочу записаться на {SERVICE_NAMES[service]}",
        "Машину бы помыть, когда можно?",
        "Есть свободное время на мойку?",
        "Запишите меня на мойку, пожалуйста",
        "Можно на мойку записаться?",
        "Мне нужно тачку помыть",
        "Машинку бы помыть",
        "Хочу авто помыть, записываете?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(requests))})

    convos.append({"role": "assistant", "content": random.choice([
        "Конечно! Подскажите, пожалуйста, марку и класс вашего автомобиля?",
        "С удовольствием запишу вас! Какой у вас автомобиль?",
        "Хорошо! Скажите, какая у вас машина?",
    ])})

    car_answers = [
        f"У меня {car_name}", f"{car_name}", f"Это {car_name}, {class_label(car_class)}",
        f"Ну {car_name} у меня", f"{car_name}, {class_label(car_class)}",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(car_answers))})

    sname = SERVICE_NAMES[service]
    convos.append({"role": "assistant", "content": (
        f"Отлично, {car_name}. {sname.capitalize()} стоит {price_str(price)}, "
        f"по времени — {DURATIONS[service]}. На какое время вас записать?"
    )})

    time_picks = [
        f"Давайте {day} на {time}", f"Можно {day} в {time}?",
        f"А {day} на {time} есть?", f"Запишите на {day}, {time}",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(time_picks))})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_premium_service():
    """Premium/detailing service booking — полировка, химчистка, керамика."""
    car_name, car_class = get_car()
    service = random.choice([
        "полировка", "химчистка", "керамика", "нанокерамика",
        "полировка", "химчистка",
    ])
    price = PRICES[car_class][service]
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = begin_dialog()

    if service == "полировка":
        reqs = [
            "Хочу полировку сделать, кузов потускнел",
            "Мне бы полировку. Много мелких царапин",
            "Интересует полировка кузова",
            "Можно кузов отполировать? Царапин много",
        ]
    elif service == "химчистка":
        reqs = [
            "Нужна химчистка салона. Что включает и сколько стоит?",
            "Хочу химчистку сделать, салон грязный",
            "Мне бы химчистку. Ребёнок всё заляпал",
            "Салон нужно почистить, можно записаться?",
        ]
    elif service == "керамика":
        reqs = [
            "Хочу нанести керамику на кузов. Сколько стоит?",
            "Интересует керамическое покрытие",
            "Слышал про керамику для кузова. Делаете?",
            "Хочу защитить кузов керамикой",
        ]
    else:  # нанокерамика
        reqs = [
            "У вас есть нанокерамика?",
            "Хочу нанокерамику нанести, сколько стоит?",
            "Интересует нанокерамическое покрытие",
        ]

    convos.append({"role": "user", "content": naturalize(random.choice(reqs))})

    sname = SERVICE_NAMES[service]
    descriptions = {
        "полировка": "Полировка кузова убирает мелкие царапины и восстанавливает блеск. Используем абразивную полировку профессиональными составами.",
        "химчистка": "Полная химчистка включает глубокую чистку всех сидений, потолка, дверных карт, ковриков и багажника. Используем профессиональные средства и экстракторное оборудование.",
        "керамика": "Керамическое покрытие — долговременная защита кузова от царапин, грязи и ультрафиолета. Эффект от одного до трёх лет. Перед нанесением обязательна полировка.",
        "нанокерамика": "Нанокерамика — это защитное покрытие нового поколения. Держится до двух лет, создаёт гидрофобный эффект. Машина дольше остаётся чистой.",
    }
    convos.append({"role": "assistant", "content": f"{descriptions[service]} Подскажите, какой у вас автомобиль?"})

    convos.append({"role": "user", "content": naturalize(f"У меня {car_name}")})

    convos.append({"role": "assistant", "content": (
        f"Для {car_name} стоимость — {price_str(price)}. "
        f"Работа займёт {DURATIONS[service]}. Хотите записаться?"
    )})

    convos.append({"role": "user", "content": naturalize(random.choice([
        "Да, давайте запишусь", "Хорошо, записывайте",
        "Окей, хочу записаться", "Да, подходит",
    ]))})

    convos.append({"role": "assistant", "content": "Отлично! На какой день и время вас записать?"})
    convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {time}")})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_combo_services():
    """Multiple services combo — мойка + полировка, мойка + химчистка etc."""
    car_name, car_class = get_car()
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)
    p = PRICES[car_class]

    combos = [
        (["комплекс", "полировка"], "комплексную мойку и полировку"),
        (["экспресс", "химчистка_частичная"], "экспресс-мойку и химчистку сидений"),
        (["комплекс", "двигатель"], "комплексную мойку и мойку двигателя"),
        (["полировка", "керамика"], "полировку и керамику"),
        (["комплекс", "чернение_шин"], "комплексную мойку и чернение шин"),
        (["экспресс", "антидождь"], "экспресс-мойку и антидождь"),
        (["комплекс", "воск"], "комплексную мойку и мойку с воском"),
        (["химчистка", "полировка"], "химчистку салона и полировку"),
    ]
    services, combo_name = random.choice(combos)
    total = sum(p[s] for s in services)

    convos = begin_dialog()

    combo_requests = [
        f"Мне бы {combo_name} сделать",
        f"Хочу записаться на {combo_name}",
        f"Можно {combo_name}? Сколько выйдет?",
        f"Нужно {combo_name}, берёте за раз?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(combo_requests))})
    convos.append({"role": "assistant", "content": "Конечно, можем сделать всё за один визит! Подскажите, какой у вас автомобиль?"})
    convos.append({"role": "user", "content": naturalize(f"{car_name}")})

    details = ", ".join(f"{SERVICE_NAMES[s]} — {price_str(p[s])}" for s in services)
    convos.append({"role": "assistant", "content": (
        f"Для {car_name}: {details}. Итого — {price_str(total)}. Когда вам удобно?"
    )})
    convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {time}")})

    convos.append({"role": "assistant", "content": (
        f"Записываю: {day}, {time}, {combo_name}, {car_name}. "
        f"Итого — {price_str(total)}. Как вас зовут?"
    )})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": (
        f"Записал вас на {combo_name} для {car_name}, {day} в {time}. "
        f"Стоимость {price_str(total)}. Ждём вас!"
    )})
    convos = end_with_goodbye(convos)
    return convos


def gen_car_type_matters():
    """Car type matters — sedan vs SUV vs minivan, different pricing."""
    target_class = random.choice(["кроссовер", "внедорожник", "минивэн"])
    car_name, car_class = get_car_by_class(target_class)
    service = random.choice(["экспресс", "комплекс", "полная", "химчистка"])
    price = PRICES[car_class][service]
    base_price = PRICES["легковой"][service]
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = begin_dialog()

    reqs = [
        f"Хочу на мойку записаться. У меня {car_name}",
        f"Мне помыть {car_name}, сколько будет стоить?",
        f"Здравствуйте, нужна мойка для {car_name}",
        f"Мне бы на {SERVICE_NAMES[service]}, у меня {class_label(car_class)}",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(reqs))})

    sname = SERVICE_NAMES[service]
    convos.append({"role": "assistant", "content": (
        f"{car_name} — это {class_label(car_class)}, стоимость будет чуть выше, чем для легкового. "
        f"{sname.capitalize()} для вашего автомобиля — {price_str(price)}, "
        f"по времени — {DURATIONS[service]}. Хотите записаться?"
    )})

    # Sometimes client reacts to price difference
    if random.random() < 0.4:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "А почему дороже? На сайте другая цена была",
            "А чё так дорого? На легковую же дешевле",
            "Хм, а для обычной машины сколько?",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Для легкового автомобиля {sname} стоит {price_str(base_price)}. "
            f"Для {class_label(car_class)} цена выше, потому что площадь кузова больше "
            f"и расход материалов увеличивается. Это стандартная практика."
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Ладно, понятно. Давайте записывайте",
            "Ну окей, логично. Записывайте тогда",
            "Хорошо, понял. Давайте",
        ]))})
        convos.append({"role": "assistant", "content": f"На какой день и время вас записать?"})
    else:
        convos.append({"role": "user", "content": naturalize("Да, давайте")})
        convos.append({"role": "assistant", "content": f"Отлично! На какой день и время?"})

    convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_time_preference():
    """Time slot selection with preferences — утром, после работы etc."""
    car_name, car_class = get_car()
    service = random.choice(["экспресс", "комплекс", "воск"])
    price = PRICES[car_class][service]
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS[:6])

    convos = begin_dialog()
    convos.append({"role": "user", "content": naturalize(random.choice([
        f"Хочу на мойку записаться, у меня {car_name}",
        f"Мне бы {SERVICE_NAMES[service]} для {car_name}",
    ]))})

    convos.append({"role": "assistant", "content": (
        f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(price)}, "
        f"{DURATIONS[service]}. Когда вам удобно?"
    )})

    pref_type = random.choice(["morning", "evening", "lunch", "weekend"])
    if pref_type == "morning":
        prefs = ["Мне бы утром пораньше", "С утра можно? Часов в восемь-девять",
                 "Пораньше бы, до обеда"]
        slots = random.sample(MORNING_TIMES, min(3, len(MORNING_TIMES)))
    elif pref_type == "evening":
        prefs = ["После работы, часов в шесть-семь", "Вечером можно?",
                 "Мне бы после пяти"]
        slots = random.sample(EVENING_TIMES, min(3, len(EVENING_TIMES)))
    elif pref_type == "lunch":
        prefs = ["В обед бы, часов в двенадцать-час", "Где-то в обеденное время"]
        slots = [random.choice(TIMES[8:12]) for _ in range(3)]
    else:
        prefs = ["Только в выходные могу", "В субботу или воскресенье"]
        day = random.choice(["в субботу", "в воскресенье"])
        slots = random.sample(TIMES[:16], 3)

    convos.append({"role": "user", "content": naturalize(random.choice(prefs))})

    slot_list = ", ".join(slots[:3])
    convos.append({"role": "assistant", "content": (
        f"{day.capitalize()} могу предложить: {slot_list}. Какое время подойдёт?"
    )})

    chosen = random.choice(slots[:3])
    convos.append({"role": "user", "content": naturalize(f"Давайте на {chosen}")})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, chosen)
    convos = end_with_goodbye(convos)
    return convos


def gen_time_unavailable():
    """Time unavailable — slot taken, offer 2-3 alternatives."""
    car_name, car_class = get_car()
    service = random.choice(["экспресс", "комплекс", "воск", "полная"])
    price = PRICES[car_class][service]
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS[:6])
    wanted_time = random.choice(TIMES)

    convos = begin_dialog()
    convos.append({"role": "user", "content": naturalize(random.choice([
        f"Хочу записаться на мойку на {day}",
        f"Мне бы {SERVICE_NAMES[service]}",
        "Запишите на мойку, пожалуйста",
    ]))})
    convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
    convos.append({"role": "user", "content": naturalize(f"{car_name}")})
    convos.append({"role": "assistant", "content": (
        f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(price)}. "
        f"На какое время хотите записаться?"
    )})
    convos.append({"role": "user", "content": naturalize(f"Можно {day} на {wanted_time}?")})

    # Time not available
    alts = random.sample([t for t in TIMES if t != wanted_time], 3)
    convos.append({"role": "assistant", "content": (
        f"К сожалению, {day} на {wanted_time} уже занято. "
        f"Могу предложить: {alts[0]}, {alts[1]} или {alts[2]}. Какое время подойдёт?"
    )})

    reaction = random.choice(["pick", "another_day"])
    if reaction == "pick":
        chosen = random.choice(alts)
        convos.append({"role": "user", "content": naturalize(f"Давайте на {chosen}")})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, chosen)
    else:
        new_day = random.choice([d for d in DAYS if d != day])
        convos.append({"role": "user", "content": naturalize(f"А {new_day} на {wanted_time} свободно?")})
        convos.append({"role": "assistant", "content": f"Да, {new_day} на {wanted_time} свободно!"})
        convos.append({"role": "user", "content": naturalize("Отлично, давайте тогда")})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, new_day, wanted_time)

    convos = end_with_goodbye(convos)
    return convos


def gen_price_then_booking():
    """Price inquiry followed by booking."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    convos.append({"role": "user", "content": naturalize(random.choice([
        "Скажите, сколько у вас мойка стоит?",
        "А сколько стоит помыть машину?",
        "Подскажите цены на мойку",
        "Какие у вас цены?",
        "Мне бы узнать стоимость мойки",
        "Чё по ценам у вас?",
    ]))})

    convos.append({"role": "assistant", "content": "Стоимость зависит от типа автомобиля. Подскажите, какая у вас машина?"})

    convos.append({"role": "user", "content": naturalize(f"{car_name}")})

    convos.append({"role": "assistant", "content": (
        f"Для {car_name} у нас: экспресс-мойка кузова — {price_str(p['экспресс'])}, "
        f"комплексная мойка с салоном — {price_str(p['комплекс'])}, "
        f"мойка с воском — {price_str(p['воск'])}, "
        f"полная мойка с багажником — {price_str(p['полная'])}. "
        f"Что вас интересует?"
    )})

    service = random.choice(["экспресс", "комплекс", "воск", "полная"])
    choice_phrases = {
        "экспресс": ["Давайте экспресс, мне быстро надо", "Экспресс хватит", "Самую простую давайте"],
        "комплекс": ["Комплексную давайте", "Лучше комплексную, раз уж приеду", "Комплекс возьму"],
        "воск": ["С воском давайте", "Мойку с воском хочу", "Давайте с воском"],
        "полная": ["Полную давайте, раз уж всё равно", "Давайте полную, чтобы нормально", "Полную мойку"],
    }
    convos.append({"role": "user", "content": naturalize(random.choice(choice_phrases[service]))})

    convos.append({"role": "assistant", "content": (
        f"Хорошо, {SERVICE_NAMES[service]} за {price_str(p[service])}. На когда вас записать?"
    )})
    convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_price_only():
    """Price inquiry only, no booking."""
    car_name, car_class = get_car()
    p = PRICES[car_class]

    convos = begin_dialog()

    convos.append({"role": "user", "content": naturalize(random.choice([
        "Просто узнать цены хотел",
        "Сколько у вас стоит мойка?",
        "Подскажите прайс",
        "Мне бы цены узнать, пока не записываюсь",
    ]))})

    convos.append({"role": "assistant", "content": "Конечно! Подскажите, какой у вас автомобиль, чтобы назвать точные цены?"})
    convos.append({"role": "user", "content": naturalize(f"{car_name}")})

    inquiry_type = random.choice(["basic", "premium", "all"])
    if inquiry_type == "basic":
        convos.append({"role": "assistant", "content": (
            f"Для {car_name}: экспресс-мойка — {price_str(p['экспресс'])}, "
            f"комплексная — {price_str(p['комплекс'])}, с воском — {price_str(p['воск'])}, "
            f"полная мойка — {price_str(p['полная'])}."
        )})
    elif inquiry_type == "premium":
        convos.append({"role": "assistant", "content": (
            f"Для {car_name}: химчистка салона — {price_str(p['химчистка'])}, "
            f"частичная химчистка — {price_str(p['химчистка_частичная'])}, "
            f"полировка — {price_str(p['полировка'])}, "
            f"керамика — {price_str(p['керамика'])}."
        )})
    else:
        convos.append({"role": "assistant", "content": (
            f"Для {car_name}: экспресс — {price_str(p['экспресс'])}, комплексная — {price_str(p['комплекс'])}, "
            f"полная — {price_str(p['полная'])}, химчистка — {price_str(p['химчистка'])}, "
            f"полировка — {price_str(p['полировка'])}, керамика — {price_str(p['керамика'])}. "
            f"Полный прайс могу отправить в мессенджер."
        )})

    # Additional question or not
    if random.random() < 0.5:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "А по времени сколько занимает?",
            "А сколько по времени мойка?",
            "Долго делаете?",
        ]))})
        svc = random.choice(["экспресс", "комплекс"])
        convos.append({"role": "assistant", "content": (
            f"Экспресс-мойка — {DURATIONS['экспресс']}, комплексная — {DURATIONS['комплекс']}."
        )})

    convos.append({"role": "user", "content": naturalize(random.choice([
        "Спасибо, подумаю и перезвоню",
        "Хорошо, спасибо за информацию",
        "Ладно, я подумаю. Спасибо",
        "Понял, спасибо. Если что, позвоню",
        "Ага, спасибо, буду иметь в виду",
    ]))})
    convos.append({"role": "assistant", "content": random.choice([
        "Будем рады видеть вас! Звоните в любое время. Хорошего дня!",
        "Пожалуйста! Ждём вашего звонка. Всего доброго!",
        "Хорошо, будем ждать! До свидания!",
    ])})
    return convos


def gen_cancellation():
    """Cancellation — polite, offer reschedule."""
    name = random.choice(CLIENT_NAMES)
    car_name, car_class = get_car()
    old_day = random.choice(["сегодня", "завтра", "в среду", "в четверг", "в пятницу"])
    old_time = random.choice(TIMES)
    service = random.choice(["экспресс", "комплекс", "полировка", "химчистка"])

    convos = begin_dialog()

    cancel_reqs = [
        f"Хочу отменить запись на {old_day}",
        f"Мне нужно отменить мойку. Я записан на {old_day}",
        f"Не смогу приехать, отмените запись, пожалуйста",
        f"Слушайте, мне надо отменить запись",
        f"Мне нужно отменить, не получается приехать",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(cancel_reqs))})
    convos.append({"role": "assistant", "content": "Хорошо, подскажите, пожалуйста, ваше имя."})
    convos.append({"role": "user", "content": naturalize(name)})

    convos.append({"role": "assistant", "content": (
        f"Нашла вашу запись, {name}. {SERVICE_NAMES[service].capitalize()}, "
        f"{old_day}, {old_time}. Отменяю."
    )})

    # Offer reschedule
    if random.random() < 0.6:
        convos.append({"role": "assistant", "content": "Может быть, хотите перенести на другой день?"})
        if random.random() < 0.4:
            new_day = random.choice([d for d in DAYS if d != old_day])
            new_time = random.choice(TIMES)
            convos.append({"role": "user", "content": naturalize(f"Да, давайте на {new_day}, {new_time}")})
            convos.append({"role": "assistant", "content": (
                f"Отлично! Перенесла на {new_day}, {new_time}. Всё остальное без изменений. Ждём вас!"
            )})
        else:
            convos.append({"role": "user", "content": naturalize(random.choice([
                "Нет, пока не надо. Я потом позвоню",
                "Нет, спасибо. Перезвоню когда определюсь",
                "Не, пока отмените просто",
            ]))})
            convos.append({"role": "assistant", "content": "Хорошо, запись отменена. Будем рады видеть вас в другой раз! Хорошего дня."})
    else:
        convos.append({"role": "assistant", "content": "Запись отменена. Будем рады видеть вас в другой раз! Хорошего дня."})

    convos = end_with_goodbye(convos, prob=0.4)
    return convos


def gen_reschedule():
    """Reschedule — change date/time."""
    name = random.choice(CLIENT_NAMES)
    car_name, car_class = get_car()
    old_day = random.choice(["сегодня", "завтра", "в среду", "в четверг", "в пятницу"])
    old_time = random.choice(TIMES)
    new_day = random.choice(["послезавтра", "в субботу", "в понедельник", "на следующей неделе", "в воскресенье"])
    new_time = random.choice(TIMES)
    service = random.choice(["экспресс", "комплекс", "полировка", "химчистка", "полная"])

    convos = begin_dialog()

    resched_reqs = [
        f"Я записан на {old_day}, хотел бы перенести",
        f"Мне нужно перенести запись. Я на {old_day} в {old_time} записан",
        f"Слушайте, не смогу приехать {old_day}. Можно перенести?",
        f"Можно перезаписаться? У меня было на {old_day}",
        f"Перенесите мне запись, пожалуйста",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(resched_reqs))})
    convos.append({"role": "assistant", "content": "Конечно! Подскажите, пожалуйста, ваше имя, чтобы я нашёл запись."})
    convos.append({"role": "user", "content": naturalize(name)})

    convos.append({"role": "assistant", "content": (
        f"Нашла вашу запись, {name}. {SERVICE_NAMES[service].capitalize()}, "
        f"{old_day}, {old_time}. На какое время хотите перенести?"
    )})
    convos.append({"role": "user", "content": naturalize(f"Можно {new_day} на {new_time}?")})

    if random.random() < 0.3:
        # New time also busy
        alt_time = random.choice([t for t in TIMES if t != new_time])
        convos.append({"role": "assistant", "content": (
            f"К сожалению, {new_day} на {new_time} занято. "
            f"Есть свободное место на {alt_time}. Подойдёт?"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            f"Да, давайте на {alt_time}", "Ладно, пусть будет", "Хорошо, записывайте",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Перенесла вашу запись на {new_day}, {alt_time}. "
            f"Всё остальное без изменений. Ждём вас!"
        )})
    else:
        convos.append({"role": "assistant", "content": (
            f"{new_day.capitalize()}, {new_time} — свободно! "
            f"Переношу вашу запись. Всё остальное без изменений. Ждём вас!"
        )})

    convos = end_with_goodbye(convos)
    return convos


def gen_change_mind():
    """User changes mind mid-dialog — upgrades or downgrades service."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    change_type = random.choice(["upgrade", "downgrade", "switch_service"])

    if change_type == "upgrade":
        convos.append({"role": "user", "content": naturalize("Хочу записаться на экспресс-мойку")})
        convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": (
            f"Экспресс-мойка для {car_name} — {price_str(p['экспресс'])}, "
            f"{DURATIONS['экспресс']}. На когда записать?"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "А знаете, давайте лучше комплексную. Раз уж приеду",
            "Стоп, передумал. Давайте комплексную мойку лучше",
            "Хотя нет, давайте комплекс, салон тоже грязный",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Хорошо, меняю на комплексную мойку — {price_str(p['комплекс'])}, "
            f"{DURATIONS['комплекс']}. На какое время?"
        )})
        final_service = "комплекс"

    elif change_type == "downgrade":
        convos.append({"role": "user", "content": naturalize("Хочу записаться на комплексную мойку")})
        convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": (
            f"Комплексная мойка для {car_name} — {price_str(p['комплекс'])}, "
            f"{DURATIONS['комплекс']}. На когда записать?"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "А знаете, давайте просто экспресс. Времени мало",
            "Нет, передумал, мне только кузов помыть. Экспресс давайте",
            "Хм, дороговато. Давайте просто экспресс",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Хорошо, экспресс-мойка — {price_str(p['экспресс'])}, "
            f"{DURATIONS['экспресс']}. На какое время?"
        )})
        final_service = "экспресс"

    else:  # switch service entirely
        convos.append({"role": "user", "content": naturalize("Мне бы полировку записаться")})
        convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": (
            f"Полировка для {car_name} — {price_str(p['полировка'])}, "
            f"{DURATIONS['полировка']}. Хотите записаться?"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Слушайте, а давайте лучше химчистку. Салон важнее",
            "Нет, стоп. Мне важнее химчистку сделать, салон убитый",
            "Передумал, давайте химчистку лучше",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Хорошо, химчистка салона — {price_str(p['химчистка'])}, "
            f"{DURATIONS['химчистка']}. На когда записать?"
        )})
        final_service = "химчистка"

    convos.append({"role": "user", "content": naturalize(f"На {day}, {time}")})
    convos = ask_name_and_confirm(convos, name, car_name, final_service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_regular_customer():
    """Regular customer / membership question."""
    name = random.choice(CLIENT_NAMES)
    car_name, car_class = get_car()
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    membership_reqs = [
        f"Я часто к вам езжу, есть какие-то скидки для постоянных?",
        f"Здравствуйте, я у вас постоянный клиент. Есть программа лояльности?",
        f"Слышал, у вас абонементы есть. Расскажите",
        f"Мне бы абонемент на мойку оформить",
        f"Хочу узнать про скидки для постоянных клиентов",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(membership_reqs))})

    loyalty_type = random.choice(["abonement", "discount_card", "both"])
    if loyalty_type == "abonement":
        convos.append({"role": "assistant", "content": (
            "У нас есть абонементы! Десять экспресс-моек со скидкой двадцать процентов, "
            "или пять комплексных моек со скидкой пятнадцать процентов. "
            "Оплата сразу, пользуетесь в течение трёх месяцев."
        )})
    elif loyalty_type == "discount_card":
        convos.append({"role": "assistant", "content": (
            "Да, у нас есть накопительная карта! Каждая шестая мойка — бесплатно. "
            "Карту можно оформить при следующем визите, это бесплатно."
        )})
    else:
        convos.append({"role": "assistant", "content": (
            "У нас две программы: абонемент на десять моек со скидкой двадцать процентов "
            "и накопительная карта — каждая шестая мойка бесплатно. "
            "Можно оформить при визите."
        )})

    if random.random() < 0.6:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "О, интересно. А заодно запишите меня на мойку",
            "Хорошо, оформлю когда приеду. А запишите на мойку пока",
            "Класс! Тогда запишите на экспресс заодно",
        ]))})
        convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        service = random.choice(["экспресс", "комплекс"])
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}. Когда удобно?"
        )})
        convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    else:
        convos.append({"role": "user", "content": naturalize("Хорошо, спасибо за информацию. Подумаю")})
        convos.append({"role": "assistant", "content": "Пожалуйста! Приезжайте, всё расскажем подробнее. Хорошего дня!"})

    convos = end_with_goodbye(convos, prob=0.4)
    return convos


def gen_walkin_check():
    """Walk-in check — 'Можно прямо сейчас?'"""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    walkin_reqs = [
        "Можно прямо сейчас подъехать на мойку?",
        "Я тут рядом, есть место помыть машину?",
        "А без записи можно? Я буквально через десять минут приеду",
        "Щас можно заехать? Машина грязная, срочно надо",
        "Есть свободное место прямо сейчас?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(walkin_reqs))})

    available = random.choice([True, True, False])
    if available:
        wait = random.choice(["без ожидания", "минут через десять-пятнадцать",
                               "через полчаса будет место"])
        convos.append({"role": "assistant", "content": (
            f"Сейчас проверю... Да, можем принять вас {wait}! "
            f"Какой у вас автомобиль?"
        )})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        service = random.choice(["экспресс", "комплекс"])
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}, "
            f"{DURATIONS[service]}. Приезжайте!"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Отлично, еду!", "Супер, буду минут через десять",
            "Ага, щас подъеду", "Класс, выезжаю",
        ]))})
        convos.append({"role": "assistant", "content": f"Ждём вас! Как подъедете, подходите к администратору."})
    else:
        next_time = random.choice(TIMES)
        convos.append({"role": "assistant", "content": (
            f"К сожалению, сейчас все боксы заняты. "
            f"Ближайшее свободное время — {next_time}. Записать вас?"
        )})
        if random.random() < 0.6:
            convos.append({"role": "user", "content": naturalize(f"Ладно, давайте на {next_time}")})
            convos.append({"role": "assistant", "content": "Какой у вас автомобиль?"})
            convos.append({"role": "user", "content": naturalize(f"{car_name}")})
            service = "экспресс"
            convos = ask_name_and_confirm(convos, name, car_name, service, car_class, "сегодня", next_time)
        else:
            convos.append({"role": "user", "content": naturalize("Нет, я в другое место поеду тогда")})
            convos.append({"role": "assistant", "content": "Понимаю! Будем рады видеть вас в другой раз. Хорошего дня!"})

    convos = end_with_goodbye(convos, prob=0.3)
    return convos


def gen_aggressive_customer():
    """Aggressive/impatient customer — model stays calm."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    aggro_type = random.choice(["price_complaint", "wait_complaint", "quality_complaint", "rude"])

    if aggro_type == "price_complaint":
        convos.append({"role": "user", "content": naturalize("Сколько у вас мойка стоит?")})
        convos.append({"role": "assistant", "content": "Подскажите, какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": (
            f"Экспресс-мойка для {car_name} — {price_str(p['экспресс'])}, "
            f"комплексная — {price_str(p['комплекс'])}."
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Чё так дорого?! За углом дешевле моют!",
            "Вы с ума сошли, такие цены? Это же грабёж",
            "Обалдеть, дорого. Раньше дешевле было",
        ]))})
        convos.append({"role": "assistant", "content": (
            "Понимаю ваше беспокойство. Наши цены включают качественные материалы "
            "и профессиональное оборудование. Мы гарантируем результат. "
            "Если хотите сэкономить, могу предложить экспресс-мойку — она дешевле."
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Ладно, давайте экспресс тогда",
            "Ну ладно, записывайте на комплексную",
            "Хорошо, уговорили. Давайте комплекс",
        ]))})
        service = random.choice(["экспресс", "комплекс"])
        convos.append({"role": "assistant", "content": f"Хорошо! Когда вам удобно?"})

    elif aggro_type == "wait_complaint":
        convos.append({"role": "user", "content": naturalize("Мне на мойку записаться, но чтобы без очереди! Прошлый раз час ждал")})
        convos.append({"role": "assistant", "content": (
            "Приносим извинения за прошлый опыт. При записи мы гарантируем "
            "обслуживание в назначенное время без ожидания. Какой у вас автомобиль?"
        )})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        service = "комплекс"
        convos.append({"role": "assistant", "content": (
            f"Комплексная мойка для {car_name} — {price_str(p[service])}, "
            f"{DURATIONS[service]}. Когда вам удобно?"
        )})

    elif aggro_type == "quality_complaint":
        convos.append({"role": "user", "content": naturalize("Прошлый раз плохо помыли! Разводы остались. Вы вообще нормально работаете?")})
        convos.append({"role": "assistant", "content": (
            "Очень жаль, что вы остались недовольны. Это не наш стандарт работы. "
            "Если такое повторится, пожалуйста, сообщите администратору сразу — мы перемоем бесплатно. "
            "Хотите записаться снова? Проконтролирую качество лично."
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Ладно, попробую ещё раз. Но если опять плохо — больше не приеду",
            "Хорошо, давайте попробуем. Какой у вас автомобиль?",
            "Ну давайте. Но чтобы нормально в этот раз",
        ]))})
        convos.append({"role": "assistant", "content": "Гарантирую качество! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        service = "комплекс"
        convos.append({"role": "assistant", "content": (
            f"Комплексная мойка для {car_name} — {price_str(p[service])}. Когда удобно?"
        )})

    else:  # rude
        convos.append({"role": "user", "content": naturalize("Алё, мне машину помыть, побыстрее давайте")})
        convos.append({"role": "assistant", "content": "Здравствуйте! Конечно, помогу. Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}. Давайте побыстрее, мне некогда")})
        service = "экспресс"
        convos.append({"role": "assistant", "content": (
            f"Экспресс-мойка для {car_name} — {price_str(p[service])}, "
            f"всего {DURATIONS[service]}. Самый быстрый вариант. Когда приедете?"
        )})

    convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos, prob=0.3)
    return convos


def gen_transfer_to_admin():
    """Transfer to admin — complex request beyond bot's capability."""
    convos = begin_dialog()

    transfer_reqs = [
        "Мне нужно поговорить с администратором",
        "Соедините с менеджером, пожалуйста",
        "Я хочу оставить жалобу, переключите на администратора",
        "У меня вопрос по договору на обслуживание, можно с администратором?",
        "Мне нужна консультация по сложной услуге, соедините с мастером",
        "Хочу обсудить корпоративный контракт на автопарк",
        "У меня рекламация, хочу с руководством поговорить",
        "Мне нужно обсудить нестандартный заказ",
        "Хочу заказать оклейку плёнкой, у вас есть такое?",
        "Мне нужна полная реставрация салона, это возможно?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(transfer_reqs))})

    convos.append({"role": "assistant", "content": random.choice([
        "Конечно, сейчас переключу вас на администратора. Одну секунду, пожалуйста.",
        "Понимаю. Сейчас соединю вас с администратором, не кладите трубку.",
        "Хорошо, переключаю на старшего администратора. Пожалуйста, оставайтесь на линии.",
    ])})

    if random.random() < 0.5:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Хорошо, жду", "Ага, спасибо", "Ладно",
        ]))})
        convos.append({"role": "assistant", "content": "Соединяю. Спасибо за ожидание!"})

    return convos


# ── Main generation ────────────────────────────────────────────────────────

def generate_all_dialogs():
    """Generate exactly 500 dialogs according to specified distribution."""
    dialogs = []

    # Simple wash booking (100)
    for _ in range(100):
        dialogs.append(gen_simple_wash())

    # Premium/detailing service booking (60)
    for _ in range(60):
        dialogs.append(gen_premium_service())

    # Multiple services combo (50)
    for _ in range(50):
        dialogs.append(gen_combo_services())

    # Car type matters (50)
    for _ in range(50):
        dialogs.append(gen_car_type_matters())

    # Time slot selection with preferences (40)
    for _ in range(40):
        dialogs.append(gen_time_preference())

    # Time unavailable -> alternatives (35)
    for _ in range(35):
        dialogs.append(gen_time_unavailable())

    # Price inquiry -> booking (35)
    for _ in range(35):
        dialogs.append(gen_price_then_booking())

    # Price inquiry only (no booking) (20)
    for _ in range(20):
        dialogs.append(gen_price_only())

    # Cancellation (30)
    for _ in range(30):
        dialogs.append(gen_cancellation())

    # Reschedule (30)
    for _ in range(30):
        dialogs.append(gen_reschedule())

    # User changes mind (20)
    for _ in range(20):
        dialogs.append(gen_change_mind())

    # Regular customer / membership (15)
    for _ in range(15):
        dialogs.append(gen_regular_customer())

    # Walk-in check (15)
    for _ in range(15):
        dialogs.append(gen_walkin_check())

    # Aggressive/impatient customer (10)
    for _ in range(10):
        dialogs.append(gen_aggressive_customer())

    # Transfer to admin (10)
    for _ in range(10):
        dialogs.append(gen_transfer_to_admin())

    # Shuffle to mix scenarios
    random.shuffle(dialogs)

    return dialogs


if __name__ == "__main__":
    dialogs = generate_all_dialogs()

    output_path = os.path.join(os.path.dirname(__file__), "carwash_dialogs_v2.jsonl")

    with open(output_path, "w", encoding="utf-8") as f:
        for d in dialogs:
            line = json.dumps({"conversations": d}, ensure_ascii=False)
            f.write(line + "\n")

    print(f"Generated {len(dialogs)} dialogs -> {output_path}")

    # Validate
    with open(output_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        valid = 0
        for i, line in enumerate(lines):
            try:
                obj = json.loads(line.strip())
                assert "conversations" in obj
                assert len(obj["conversations"]) >= 3  # system + at least 1 turn pair
                assert obj["conversations"][0]["role"] == "system"
                valid += 1
            except Exception as e:
                print(f"ERROR line {i+1}: {e}")
        print(f"Validated: {valid}/{len(lines)} lines OK")
