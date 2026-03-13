#!/usr/bin/env python3
"""Generate 1500 high-quality SFT training dialogs for car wash AI voice receptionist (v3).

Scenario distribution (1500 total):
  1. Simple wash booking: 300
  2. Premium/detailing: 150
  3. Multiple services combo: 120
  4. Car type pricing: 120
  5. User self-corrects: 120
  6. Time preference + slot selection: 80
  7. Time unavailable -> alternatives: 70
  8. Price inquiry -> booking: 70
  9. Cancellation: 60
  10. Reschedule: 60
  11. User changes mind completely: 40
  12. Walk-in "можно прямо сейчас?": 40
  13. Regular customer / loyalty: 30
  14. Price inquiry only: 30
  15. Emotional — frustrated all slots taken: 30
  16. Emotional — rush "мне срочно": 30
  17. Emotional — surprised at price: 20
  18. Aggressive customer: 20
  19. Background noise disrupts: 20
  20. Transfer to admin: 10
  21. Call back after disconnect: 10
"""

import json
import random
import os

random.seed(3003)

SYSTEM_PROMPT = (
    "Вы — администратор автомойки. Помогаете клиентам записаться на мойку, "
    "выбрать тип услуги и удобное время. Говорите вежливо и по делу."
)

# ── Data pools ──────────────────────────────────────────────────────────────

FILLERS_START = [
    "Ну", "Эм", "Так", "Вот", "Короче", "Слушай", "Значит", "В общем",
    "Ну типа", "Ну это", "Короч", "Слушайте", "Это самое", "Ааа", "Как бы",
]
FILLERS_MID = ["э...", "эм...", "ну...", "типа...", "это...", "так...", "м..."]
FILLERS_END = ["вот", "ну вот", "да", "короче", "как-то так", "в общем"]

NOISE_TAGS = [
    "[неразборчиво]", "[шум]", "[помехи]", "[плохая связь]",
    "[шум двигателя]", "[сигнал машины]", "[шум дороги]",
]

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
    "Ну здрасте", "Здарова, это мойка?", "Алё, мойка?",
    "Добрый день, это АвтоБлеск?", "Здравствуйте, хочу на мойку",
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

# Casual car names users might say
CAR_CASUAL = [
    "у меня тигуан", "ну раф4", "камри", "крета", "солярис",
    "рав четвёрка", "поло", "хендай", "мазда цэ-икс пять",
    "октаха", "гранта", "веста", "дастер", "кашкай",
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
    "восемь... так... девять-ноль-три... двести... сорок пять... шестьдесят семь",
    "восемь, девятьсот шесть, нет, не шесть, семь, семьсот двенадцать, ноль три",
]

# Informal car words
CAR_SLANG = ["тачка", "машинка", "авто", "кузов", "тачила", "железный конь", "ласточка"]
WASH_SLANG = ["помыть", "ополоснуть", "отдраить", "навести красоту", "почапать"]

# ── Helpers ─────────────────────────────────────────────────────────────────


def add_filler(text, prob=0.65):
    """Add fillers to 60-70% of turns."""
    if random.random() < prob:
        pos = random.choice(["start", "start", "mid", "end"])
        if pos == "start":
            filler = random.choice(FILLERS_START)
            text = filler + ", " + text[0].lower() + text[1:]
        elif pos == "mid":
            words = text.split()
            if len(words) > 3:
                idx = random.randint(1, len(words) - 2)
                words.insert(idx, random.choice(FILLERS_MID))
                text = " ".join(words)
        else:  # end
            text = text.rstrip(".!?,") + ", " + random.choice(FILLERS_END)
    return text


def add_noise(text, prob=0.06):
    if random.random() < prob:
        words = text.split()
        if len(words) > 2:
            idx = random.randint(0, len(words) - 1)
            words[idx] = random.choice(NOISE_TAGS)
            text = " ".join(words)
    return text


def add_hesitation(text, prob=0.15):
    if random.random() < prob:
        text = random.choice(HESITATIONS) + text[0].lower() + text[1:]
    return text


def add_repetition(text, prob=0.08):
    """Add repeated words like 'да да да', 'ну ну'."""
    if random.random() < prob:
        reps = random.choice(["да да да", "ну ну", "так так так", "ага ага", "нет нет"])
        text = reps + ", " + text[0].lower() + text[1:]
    return text


def add_cutoff(text, prob=0.04):
    """Simulate STT cut-off: truncate a word."""
    if random.random() < prob:
        words = text.split()
        if len(words) > 4:
            idx = random.randint(2, len(words) - 2)
            w = words[idx]
            if len(w) > 4:
                words[idx] = w[:random.randint(2, len(w) - 2)] + "..."
                text = " ".join(words)
    return text


def naturalize(text):
    """Apply natural speech transformations."""
    text = add_filler(text)
    text = add_noise(text)
    text = add_hesitation(text)
    text = add_repetition(text)
    text = add_cutoff(text)
    if random.random() < 0.35 and len(text) > 0:
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


def casual_car_ref():
    """Return a casual way to refer to a car."""
    return random.choice(CAR_SLANG)


def begin_dialog():
    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    if random.random() < 0.2:
        convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Да, мне бы записаться", "Здравствуйте, хочу на мойку",
            "Алло, мне мойка нужна", "Да, можно записаться?",
            "Ну да, хочу помыть тачку", "Угу, запишите на мойку",
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
            "Ага, спасибо", "Ладно, спасибо, пока", "Збс, спасибо",
            "Ну всё, спасиб", "Окей, пока", "Давайте, до свидания",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(byes))})
        convos.append({"role": "assistant", "content": random.choice([
            "До свидания! Хорошего дня!", "Всего доброго, ждём вас!",
            "До встречи! Хорошего дня!", "Пожалуйста! Всего доброго!",
        ])})
    return convos


def ask_name_and_confirm(convos, name, car_name, service_key, car_class, day, time):
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
    service = random.choice(["экспресс", "комплекс", "воск", "экспресс", "экспресс", "комплекс"])
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
        f"Мне нужно {casual_car_ref()} помыть",
        "Машинку бы помыть",
        f"Хочу {random.choice(WASH_SLANG)} {random.choice(CAR_SLANG)}, записываете?",
        f"Ну мне бы {random.choice(['помыть', 'ополоснуть'])} машину, чё по времени?",
        "Здрасте, запишите на мойку",
        "Короче, мне мойку надо",
        f"Седня можно {random.choice(['помыть', 'записаться'])}?",
        "Чё, свободно у вас? Мне бы помыться",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(requests))})

    convos.append({"role": "assistant", "content": random.choice([
        "Конечно! Подскажите, пожалуйста, марку и класс вашего автомобиля?",
        "С удовольствием запишу вас! Какой у вас автомобиль?",
        "Хорошо! Скажите, какая у вас машина?",
        "Конечно, записываю! Какой автомобиль?",
    ])})

    car_answers = [
        f"У меня {car_name}", f"{car_name}", f"Это {car_name}, {class_label(car_class)}",
        f"Ну {car_name} у меня", f"{car_name}, {class_label(car_class)}",
        f"У меня {car_name.lower()}", f"Ну это {car_name}",
        f"Ну {car_name}, {class_label(car_class)}, вот",
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
        f"Ну давайте {day}, {time}", f"На {day} в {time} можно?",
        f"Мне бы {day} на {time}", f"Окей, {day}, {time}",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(time_picks))})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_premium_service():
    """Premium/detailing service booking."""
    car_name, car_class = get_car()
    service = random.choice([
        "полировка", "химчистка", "керамика", "нанокерамика",
        "полировка", "химчистка", "полировка",
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
            f"Короче, надо {casual_car_ref()} отполировать, весь в царапинах",
            "Слушайте, кузов матовый стал, полировка нужна",
        ]
    elif service == "химчистка":
        reqs = [
            "Нужна химчистка салона. Что включает и сколько стоит?",
            "Хочу химчистку сделать, салон грязный",
            "Мне бы химчистку. Ребёнок всё заляпал",
            "Салон нужно почистить, можно записаться?",
            "Слушайте, собака всё обляпала в салоне, химчистка нужна",
            "Короче, салон убитый, нужна химчистка",
        ]
    elif service == "керамика":
        reqs = [
            "Хочу нанести керамику на кузов. Сколько стоит?",
            "Интересует керамическое покрытие",
            "Слышал про керамику для кузова. Делаете?",
            "Хочу защитить кузов керамикой",
            "Короче, хочу керамику нанести, чё по ценам?",
        ]
    else:
        reqs = [
            "У вас есть нанокерамика?",
            "Хочу нанокерамику нанести, сколько стоит?",
            "Интересует нанокерамическое покрытие",
            "Мне бы нанокерамику, делаете?",
        ]

    convos.append({"role": "user", "content": naturalize(random.choice(reqs))})

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
        "Ну давайте", "Го, записывайте", "Ладно, записывайте",
    ]))})

    convos.append({"role": "assistant", "content": "Отлично! На какой день и время вас записать?"})
    convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {time}")})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_combo_services():
    """Multiple services combo."""
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
        (["экспресс", "двигатель", "чернение_шин"], "экспресс-мойку, двигатель и чернение шин"),
        (["комплекс", "антидождь", "чернение_шин"], "комплексную мойку, антидождь и чернение"),
    ]
    services, combo_name = random.choice(combos)
    total = sum(p[s] for s in services)

    convos = begin_dialog()

    combo_requests = [
        f"Мне бы {combo_name} сделать",
        f"Хочу записаться на {combo_name}",
        f"Можно {combo_name}? Сколько выйдет?",
        f"Нужно {combo_name}, берёте за раз?",
        f"Короче, надо {combo_name}, можно всё сразу?",
        f"Слушайте, а можно {combo_name} за один заезд?",
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
    """Car type matters — pricing differs for crossover/SUV/minivan."""
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
        f"Короче, у меня {car_name}, скока мойка стоит?",
        f"Ну у меня {car_name}, чё по ценам на мойку?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(reqs))})

    sname = SERVICE_NAMES[service]
    convos.append({"role": "assistant", "content": (
        f"{car_name} — это {class_label(car_class)}, стоимость будет чуть выше, чем для легкового. "
        f"{sname.capitalize()} для вашего автомобиля — {price_str(price)}, "
        f"по времени — {DURATIONS[service]}. Хотите записаться?"
    )})

    if random.random() < 0.4:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "А почему дороже? На сайте другая цена была",
            "А чё так дорого? На легковую же дешевле",
            "Хм, а для обычной машины сколько?",
            "Скока-скока?! А чё так?",
            "Ого, дорого. А почему не как для седана?",
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
            "Ну ладн, чё делать. Записывайте",
        ]))})
        convos.append({"role": "assistant", "content": "На какой день и время вас записать?"})
    else:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Да, давайте", "Окей, пойдёт", "Ну давайте", "Норм, записывайте",
        ]))})
        convos.append({"role": "assistant", "content": "Отлично! На какой день и время?"})

    convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
    return convos


def gen_self_correction():
    """User self-corrects during dialog — changes service/time/car type/date."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    correction_type = random.choice([
        "car_type", "service", "time", "date", "add_service",
        "car_type", "service", "time",
    ])

    if correction_type == "car_type":
        wrong_class = random.choice(["легковой", "кроссовер"])
        wrong_car, _ = get_car_by_class(wrong_class)
        real_class = random.choice([c for c in ["кроссовер", "внедорожник", "минивэн"] if c != wrong_class])
        car_name, car_class = get_car_by_class(real_class)
        service = random.choice(["экспресс", "комплекс"])

        convos.append({"role": "user", "content": naturalize(f"Хочу на мойку, у меня {wrong_car}")})
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} для {wrong_car} — "
            f"{price_str(PRICES[wrong_class][service])}. На какое время записать?"
        )})
        corrections = [
            f"Ой, подождите, у меня не {wrong_car.split()[0].lower()}, а {car_name}",
            f"Стоп, я ошибся — у меня {car_name}, не {wrong_car}",
            f"Нет, вру, у меня не {wrong_car.lower()}, а {car_name}. Перепутал",
            f"Ой, подождите, у меня не седан, а {class_label(car_class)}. {car_name} у меня",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(corrections))})
        convos.append({"role": "assistant", "content": (
            f"Понял, значит {car_name}, {class_label(car_class)}. "
            f"Тогда {SERVICE_NAMES[service]} будет стоить {price_str(p[service])}. На какое время?"
        )})

    elif correction_type == "service":
        first_service = random.choice(["экспресс", "комплекс", "воск"])
        second_service = random.choice([s for s in ["экспресс", "комплекс", "воск", "полная"] if s != first_service])
        service = second_service

        convos.append({"role": "user", "content": naturalize(f"Запишите на {SERVICE_NAMES[first_service]}")})
        convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[first_service].capitalize()} для {car_name} — {price_str(p[first_service])}. "
            f"Когда вам удобно?"
        )})
        corrections = [
            f"Стоп, я передумал — давайте лучше {SERVICE_NAMES[second_service]}",
            f"Хотя знаете что, давайте {SERVICE_NAMES[second_service]} лучше",
            f"А нет, давайте {SERVICE_NAMES[second_service]}, а не {SERVICE_NAMES[first_service]}",
            f"Стоп, передумал. Мне {SERVICE_NAMES[second_service]}",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(corrections))})
        convos.append({"role": "assistant", "content": (
            f"Понял, меняю на {SERVICE_NAMES[second_service]} — {price_str(p[second_service])}. "
            f"На какое время записать?"
        )})

    elif correction_type == "time":
        wrong_time = random.choice(TIMES)
        service = random.choice(["экспресс", "комплекс"])

        convos.append({"role": "user", "content": naturalize(f"Мне на мойку, {car_name}")})
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}. Когда удобно?"
        )})
        convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {wrong_time}")})
        convos.append({"role": "assistant", "content": (
            f"Записываю на {day}, {wrong_time}. Как вас зовут?"
        )})
        corrections = [
            f"А нет, вру — мне на {time}, не на {wrong_time}",
            f"Стоп, не {wrong_time}, а {time}. Перепутал",
            f"Подождите, мне не на {wrong_time}, а на {time}",
            f"Ой, нет, на {time} давайте, не на {wrong_time}",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(corrections))})
        convos.append({"role": "assistant", "content": (
            f"Понял, значит {day}, {time}. Как вас зовут?"
        )})
        convos.append({"role": "user", "content": naturalize(name)})
        convos.append({"role": "assistant", "content": (
            f"Записал вас на {SERVICE_NAMES[service]}, {car_name}, {day} в {time}. "
            f"Стоимость {price_str(p[service])}. Ждём!"
        )})
        convos = end_with_goodbye(convos)
        return convos

    elif correction_type == "date":
        wrong_day = random.choice(DAYS[:6])
        new_day = random.choice([d for d in DAYS if d != wrong_day])
        service = random.choice(["экспресс", "комплекс"])

        convos.append({"role": "user", "content": naturalize(f"Запишите на мойку, у меня {car_name}")})
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}. Когда удобно?"
        )})
        convos.append({"role": "user", "content": naturalize(f"Давайте {wrong_day} на {time}")})
        corrections = [
            f"Нет, стоп, не {wrong_day}, {new_day}",
            f"Ой, подождите, {new_day}, не {wrong_day}",
            f"А нет, {new_day} давайте, {wrong_day} я занят",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(corrections))})
        convos.append({"role": "assistant", "content": (
            f"Понял, значит {new_day}, {time}. Записываю. Как вас зовут?"
        )})
        day = new_day

    else:  # add_service
        service = random.choice(["экспресс", "комплекс"])
        extra = random.choice(["чернение_шин", "антидождь", "двигатель"])

        convos.append({"role": "user", "content": naturalize(f"Мне бы {SERVICE_NAMES[service]}, {car_name}")})
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}. Когда удобно?"
        )})
        convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {time}")})
        additions = [
            f"Хотя знаете что, давайте ещё {SERVICE_NAMES[extra]} добавьте",
            f"А можно ещё {SERVICE_NAMES[extra]}? Заодно",
            f"Стоп, а давайте ещё {SERVICE_NAMES[extra]} сделаем",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(additions))})
        total = p[service] + p[extra]
        convos.append({"role": "assistant", "content": (
            f"Конечно! {SERVICE_NAMES[service].capitalize()} плюс {SERVICE_NAMES[extra]} — "
            f"итого {price_str(total)}. Записываю на {day}, {time}. Как вас зовут?"
        )})

    convos.append({"role": "user", "content": naturalize(name)})
    svc_for_confirm = service if correction_type != "add_service" else service
    convos.append({"role": "assistant", "content": (
        f"Готово, {name}! Записал вас на {day}, {time}, {car_name}. "
        f"Стоимость — {price_str(p[svc_for_confirm])}. Ждём вас!"
    )})
    convos = end_with_goodbye(convos)
    return convos


def gen_time_preference():
    """Time slot selection with preferences."""
    car_name, car_class = get_car()
    service = random.choice(["экспресс", "комплекс", "воск"])
    price = PRICES[car_class][service]
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS[:6])

    convos = begin_dialog()
    convos.append({"role": "user", "content": naturalize(random.choice([
        f"Хочу на мойку записаться, у меня {car_name}",
        f"Мне бы {SERVICE_NAMES[service]} для {car_name}",
        f"Запишите на мойку, {car_name} у меня",
    ]))})

    convos.append({"role": "assistant", "content": (
        f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(price)}, "
        f"{DURATIONS[service]}. Когда вам удобно?"
    )})

    pref_type = random.choice(["morning", "evening", "lunch", "weekend", "after_work"])
    if pref_type == "morning":
        prefs = ["Мне бы утром пораньше", "С утра можно? Часов в восемь-девять",
                 "Пораньше бы, до обеда", "Ну с утра бы, часов в девять"]
        slots = random.sample(MORNING_TIMES, min(3, len(MORNING_TIMES)))
    elif pref_type == "evening":
        prefs = ["После работы, часов в шесть-семь", "Вечером можно?",
                 "Мне бы после пяти", "Ну вечерком бы, после шести"]
        slots = random.sample(EVENING_TIMES, min(3, len(EVENING_TIMES)))
    elif pref_type == "lunch":
        prefs = ["В обед бы, часов в двенадцать-час", "Где-то в обеденное время",
                 "Ну в обед, часик-два"]
        slots = [random.choice(TIMES[8:12]) for _ in range(3)]
    elif pref_type == "after_work":
        prefs = ["После работы, часов в пять-шесть", "Мне бы к вечеру, но не поздно",
                 "Часов в пять, после работы"]
        slots = random.sample(TIMES[16:22], min(3, len(TIMES[16:22])))
    else:
        prefs = ["Только в выходные могу", "В субботу или воскресенье",
                 "Ну токо на выходных свободен"]
        day = random.choice(["в субботу", "в воскресенье"])
        slots = random.sample(TIMES[:16], 3)

    convos.append({"role": "user", "content": naturalize(random.choice(prefs))})

    slot_list = ", ".join(slots[:3])
    convos.append({"role": "assistant", "content": (
        f"{day.capitalize()} могу предложить: {slot_list}. Какое время подойдёт?"
    )})

    chosen = random.choice(slots[:3])
    convos.append({"role": "user", "content": naturalize(random.choice([
        f"Давайте на {chosen}", f"Ну {chosen} пойдёт", f"Окей, {chosen}",
        f"На {chosen} давайте", f"Пусть будет {chosen}",
    ]))})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, chosen)
    convos = end_with_goodbye(convos)
    return convos


def gen_time_unavailable():
    """Time unavailable — slot taken, offer alternatives."""
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
        f"Короче, надо помыть {casual_car_ref()}, записываете?",
    ]))})
    convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
    convos.append({"role": "user", "content": naturalize(f"{car_name}")})
    convos.append({"role": "assistant", "content": (
        f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(price)}. "
        f"На какое время хотите записаться?"
    )})
    convos.append({"role": "user", "content": naturalize(f"Можно {day} на {wanted_time}?")})

    alts = random.sample([t for t in TIMES if t != wanted_time], 3)
    convos.append({"role": "assistant", "content": (
        f"К сожалению, {day} на {wanted_time} уже занято. "
        f"Могу предложить: {alts[0]}, {alts[1]} или {alts[2]}. Какое время подойдёт?"
    )})

    reaction = random.choice(["pick", "another_day"])
    if reaction == "pick":
        chosen = random.choice(alts)
        convos.append({"role": "user", "content": naturalize(random.choice([
            f"Давайте на {chosen}", f"Ну ладно, {chosen} пойдёт",
            f"Окей, тогда на {chosen}", f"Пусть будет {chosen}",
        ]))})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, chosen)
    else:
        new_day = random.choice([d for d in DAYS if d != day])
        convos.append({"role": "user", "content": naturalize(f"А {new_day} на {wanted_time} свободно?")})
        convos.append({"role": "assistant", "content": f"Да, {new_day} на {wanted_time} свободно!"})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Отлично, давайте тогда", "О, нормально, записывайте",
            "Збс, давайте", "Окей, пойдёт",
        ]))})
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
        "Скока стоит помыть тачку?",
        "Ну чё по прайсу?",
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
        "экспресс": ["Давайте экспресс, мне быстро надо", "Экспресс хватит", "Самую простую давайте",
                      "Ну экспресс давайте, мне побыстрее"],
        "комплекс": ["Комплексную давайте", "Лучше комплексную, раз уж приеду", "Комплекс возьму",
                      "Ну давайте комплексную, нормально будет"],
        "воск": ["С воском давайте", "Мойку с воском хочу", "Давайте с воском",
                  "Ну с воском, чтоб блестела"],
        "полная": ["Полную давайте, раз уж всё равно", "Давайте полную, чтобы нормально",
                    "Полную мойку", "Давайте полную, чё уж"],
    }
    convos.append({"role": "user", "content": naturalize(random.choice(choice_phrases[service]))})

    convos.append({"role": "assistant", "content": (
        f"Хорошо, {SERVICE_NAMES[service]} за {price_str(p[service])}. На когда вас записать?"
    )})
    convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
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
        f"Короче, отмените запись мне, не смогу",
        f"Ну в общем, не приеду {old_day}, отменяйте",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(cancel_reqs))})
    convos.append({"role": "assistant", "content": "Хорошо, подскажите, пожалуйста, ваше имя."})
    convos.append({"role": "user", "content": naturalize(name)})

    convos.append({"role": "assistant", "content": (
        f"Нашла вашу запись, {name}. {SERVICE_NAMES[service].capitalize()}, "
        f"{old_day}, {old_time}. Отменяю."
    )})

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
                "Да не, потом как-нибудь",
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
        f"Короче, мне надо перенести, {old_day} не могу",
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
        alt_time = random.choice([t for t in TIMES if t != new_time])
        convos.append({"role": "assistant", "content": (
            f"К сожалению, {new_day} на {new_time} занято. "
            f"Есть свободное место на {alt_time}. Подойдёт?"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            f"Да, давайте на {alt_time}", "Ладно, пусть будет", "Хорошо, записывайте",
            f"Ну ладн, давайте на {alt_time}",
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
    """User changes mind completely mid-dialog."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    change_type = random.choice(["upgrade", "downgrade", "switch_service", "cancel_mid"])

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
            "Ну... давайте лучше комплексную, чё уж",
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
            "Ну не, давайте просто экспресс, некогда мне",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Хорошо, экспресс-мойка — {price_str(p['экспресс'])}, "
            f"{DURATIONS['экспресс']}. На какое время?"
        )})
        final_service = "экспресс"

    elif change_type == "switch_service":
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
            "Ну нет, давайте лучше химчистку, салон грязнее кузова",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Хорошо, химчистка салона — {price_str(p['химчистка'])}, "
            f"{DURATIONS['химчистка']}. На когда записать?"
        )})
        final_service = "химчистка"

    else:  # cancel_mid
        convos.append({"role": "user", "content": naturalize("Хочу записаться на мойку")})
        convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        service = random.choice(["экспресс", "комплекс"])
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} — {price_str(p[service])}. Когда удобно?"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Ой, знаете что, я передумал. Не надо пока",
            "А, стоп, я забыл — мне сегодня не надо. Отбой",
            "Нет, подождите, я потом перезвоню. Спасибо",
            "Ну ладно, я подумаю ещё. Перезвоню",
        ]))})
        convos.append({"role": "assistant", "content": random.choice([
            "Хорошо, ждём вашего звонка! Хорошего дня.",
            "Без проблем! Звоните в любое время. Всего доброго!",
        ])})
        convos = end_with_goodbye(convos, prob=0.2)
        return convos

    convos.append({"role": "user", "content": naturalize(f"На {day}, {time}")})
    convos = ask_name_and_confirm(convos, name, car_name, final_service, car_class, day, time)
    convos = end_with_goodbye(convos)
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
        "Слушайте, я щас мимо еду, можно заехать?",
        "Короче, я рядом, можно без записи?",
        "Ну чё, есть место щас?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(walkin_reqs))})

    available = random.choice([True, True, False])
    if available:
        wait = random.choice(["без ожидания", "минут через десять-пятнадцать",
                               "через полчаса будет место", "минут через пять"])
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
            "Збс, еду", "О, нормально, щас буду",
        ]))})
        convos.append({"role": "assistant", "content": "Ждём вас! Как подъедете, подходите к администратору."})
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
            convos.append({"role": "user", "content": naturalize(random.choice([
                "Нет, я в другое место поеду тогда",
                "Не, долго, в другой раз",
                "Ну блин, ладно, поеду в другое место",
            ]))})
            convos.append({"role": "assistant", "content": "Понимаю! Будем рады видеть вас в другой раз. Хорошего дня!"})

    convos = end_with_goodbye(convos, prob=0.3)
    return convos


def gen_regular_customer():
    """Regular customer / loyalty."""
    name = random.choice(CLIENT_NAMES)
    car_name, car_class = get_car()
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    membership_reqs = [
        "Я часто к вам езжу, есть какие-то скидки для постоянных?",
        "Здравствуйте, я у вас постоянный клиент. Есть программа лояльности?",
        "Слышал, у вас абонементы есть. Расскажите",
        "Мне бы абонемент на мойку оформить",
        "Хочу узнать про скидки для постоянных клиентов",
        "Короче, я у вас часто моюсь, скидки есть?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(membership_reqs))})

    loyalty_type = random.choice(["5_washes", "10_washes", "both"])
    if loyalty_type == "5_washes":
        convos.append({"role": "assistant", "content": (
            "У нас есть абонемент на пять моек со скидкой пятнадцать процентов! "
            "Оплата сразу, пользуетесь в течение трёх месяцев."
        )})
    elif loyalty_type == "10_washes":
        convos.append({"role": "assistant", "content": (
            "У нас есть абонемент на десять моек со скидкой двадцать пять процентов! "
            "Оплата сразу, действует полгода."
        )})
    else:
        convos.append({"role": "assistant", "content": (
            "У нас два абонемента: на пять моек — скидка пятнадцать процентов, "
            "на десять моек — скидка двадцать пять процентов. "
            "Можно оформить при визите."
        )})

    if random.random() < 0.6:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "О, интересно. А заодно запишите меня на мойку",
            "Хорошо, оформлю когда приеду. А запишите на мойку пока",
            "Класс! Тогда запишите на экспресс заодно",
            "Збс, ну и запишите заодно на мойку",
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
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Хорошо, спасибо за информацию. Подумаю",
            "Ага, понял, спасибо",
            "Ну ладно, подумаю. Спасиб",
        ]))})
        convos.append({"role": "assistant", "content": "Пожалуйста! Приезжайте, всё расскажем подробнее. Хорошего дня!"})

    convos = end_with_goodbye(convos, prob=0.4)
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
        "Чё по ценам у вас?",
        "Скока мойка стоит?",
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

    if random.random() < 0.5:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "А по времени сколько занимает?",
            "А сколько по времени мойка?",
            "Долго делаете?",
            "А долго ждать?",
        ]))})
        convos.append({"role": "assistant", "content": (
            f"Экспресс-мойка — {DURATIONS['экспресс']}, комплексная — {DURATIONS['комплекс']}."
        )})

    convos.append({"role": "user", "content": naturalize(random.choice([
        "Спасибо, подумаю и перезвоню",
        "Хорошо, спасибо за информацию",
        "Ладно, я подумаю. Спасибо",
        "Понял, спасибо. Если что, позвоню",
        "Ага, спасибо, буду иметь в виду",
        "Ну окей, спасиб",
    ]))})
    convos.append({"role": "assistant", "content": random.choice([
        "Будем рады видеть вас! Звоните в любое время. Хорошего дня!",
        "Пожалуйста! Ждём вашего звонка. Всего доброго!",
        "Хорошо, будем ждать! До свидания!",
    ])})
    return convos


def gen_frustrated_slots():
    """Emotional — frustrated all slots taken."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    service = random.choice(["экспресс", "комплекс"])
    p = PRICES[car_class]

    convos = begin_dialog()

    convos.append({"role": "user", "content": naturalize(f"Мне на мойку, {car_name}")})
    convos.append({"role": "assistant", "content": (
        f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}. Когда удобно?"
    )})

    day1 = random.choice(DAYS[:4])
    time1 = random.choice(TIMES)
    convos.append({"role": "user", "content": naturalize(f"Давайте {day1}, {time1}")})
    convos.append({"role": "assistant", "content": f"К сожалению, {day1} на {time1} занято."})

    frustrations = [
        "Да блин, опять всё занято", "Ну что за дела",
        "Вот вечно так, ни одного свободного места",
        "Ну ёлки, а когда свободно-то?",
        "Ну блин, ну а когда можно тогда?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(frustrations))})

    day2 = random.choice([d for d in DAYS if d != day1])
    alts = random.sample(TIMES, 3)
    convos.append({"role": "assistant", "content": (
        f"Понимаю, неудобно получается. Могу предложить {day2}: "
        f"{alts[0]}, {alts[1]} или {alts[2]}. Подойдёт?"
    )})

    if random.random() < 0.7:
        chosen = random.choice(alts)
        convos.append({"role": "user", "content": naturalize(random.choice([
            f"Ну ладно, давайте {chosen}",
            f"Ну окей, {chosen} пойдёт",
            f"Блин, ну давайте {chosen} тогда",
        ]))})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day2, chosen)
    else:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Не, ну это не вариант. Я в другое место поеду",
            "Нет, не подходит. Ладно, перезвоню",
            "Да ну, не удобно. Ладно, в другой раз",
        ]))})
        convos.append({"role": "assistant", "content": "Жаль! Будем рады видеть вас в другой раз. Хорошего дня!"})

    convos = end_with_goodbye(convos, prob=0.3)
    return convos


def gen_rush():
    """Emotional — rush, 'мне срочно'."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    p = PRICES[car_class]

    convos = begin_dialog()

    rush_reqs = [
        "Слушайте, мне срочно надо помыть машину",
        "Короче, быстро — когда можно?",
        "Мне прям щас надо, есть места?",
        "Ну слушайте, мне очень срочно на мойку",
        "Мне через час на встречу, а машина грязная, помогите",
        "Короче, срочно надо тачку помыть, можно побыстрее?",
        "Ну очень надо, быстро можно помыть?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(rush_reqs))})

    available = random.choice([True, True, False])
    if available:
        convos.append({"role": "assistant", "content": (
            "Сейчас проверю... Есть свободный бокс! Можем принять вас прямо сейчас. "
            "Какой у вас автомобиль?"
        )})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": (
            f"Экспресс-мойка для {car_name} — {price_str(p['экспресс'])}, "
            f"всего {DURATIONS['экспресс']}. Самый быстрый вариант. Приезжайте!"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Супер, еду! Спасибо!", "Отлично, щас буду!", "Збс, выезжаю!",
            "О, класс, через пять минут буду", "Ну наконец-то, еду",
        ]))})
        convos.append({"role": "assistant", "content": "Ждём вас! Подъезжайте к первому боксу."})
    else:
        next_time = random.choice(TIMES[:10])
        convos.append({"role": "assistant", "content": (
            f"К сожалению, сейчас все боксы заняты. Ближайшее время — {next_time}. "
            f"Но это самое раннее. Записать?"
        )})
        convos.append({"role": "user", "content": naturalize(random.choice([
            f"Блин... ну ладно, давайте на {next_time}",
            "Ну ёлки, ладно, записывайте",
            f"Ну чё делать, давайте на {next_time}",
        ]))})
        convos.append({"role": "assistant", "content": "Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos = ask_name_and_confirm(convos, name, car_name, "экспресс", car_class, "сегодня", next_time)

    convos = end_with_goodbye(convos, prob=0.3)
    return convos


def gen_price_surprise():
    """Emotional — surprised at price."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)

    service = random.choice(["полировка", "химчистка", "керамика", "нанокерамика", "полная"])
    price = PRICES[car_class][service]

    convos = begin_dialog()

    convos.append({"role": "user", "content": naturalize(f"Мне бы {SERVICE_NAMES[service]}, у меня {car_name}")})
    convos.append({"role": "assistant", "content": (
        f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(price)}, "
        f"работа займёт {DURATIONS[service]}."
    )})

    surprises = [
        "Скока-скока?!", "Ого, дорого", "Это серьёзно?", "Ничё себе цены",
        "Ого, а чё так дорого?", "Ну нифига себе", "Серьёзно? Столько?",
        "Вау, не дешёвое удовольствие", "Ого, ну и цены у вас",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(surprises))})

    explanations = {
        "полировка": "В стоимость входит абразивная полировка профессиональными составами, удаление всех мелких царапин и финишная обработка. Результат держится до года.",
        "химчистка": "Это полная глубокая чистка: сиденья, потолок, дверные карты, коврики, багажник. Используем экстракторное оборудование и профессиональную химию.",
        "керамика": "Керамическое покрытие — это долговременная защита на один-три года. Включает подготовку, полировку и само нанесение. Машина дольше остаётся чистой.",
        "нанокерамика": "Нанокерамика — защитное покрытие нового поколения с гидрофобным эффектом. Держится до двух лет. Включает полировку перед нанесением.",
        "полная": "Полная мойка включает мойку кузова, салона, багажника, чистку ковриков, продувку замков. Максимально тщательная обработка.",
    }
    convos.append({"role": "assistant", "content": (
        f"Понимаю, сумма немаленькая. {explanations[service]} "
        f"Если хотите сэкономить, могу предложить более бюджетный вариант."
    )})

    if random.random() < 0.6:
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Ну ладно, раз так, давайте записывайте",
            "Хорошо, убедили. Записывайте",
            "Ну окей, понял. Давайте",
            "Ну раз качество, тогда ладно",
        ]))})
        convos.append({"role": "assistant", "content": "На какой день и время вас записать?"})
        convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    else:
        cheaper = random.choice(["экспресс", "комплекс"])
        convos.append({"role": "user", "content": naturalize(random.choice([
            f"Не, дорого. Давайте просто {SERVICE_NAMES[cheaper]}",
            f"Ну нет, давайте лучше {SERVICE_NAMES[cheaper]}",
            "А чё подешевле есть?",
        ]))})
        price2 = PRICES[car_class][cheaper]
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[cheaper].capitalize()} для {car_name} — {price_str(price2)}. Записать?"
        )})
        convos.append({"role": "user", "content": naturalize("Да, давайте")})
        convos.append({"role": "assistant", "content": "На какой день и время?"})
        convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
        convos = ask_name_and_confirm(convos, name, car_name, cheaper, car_class, day, time)

    convos = end_with_goodbye(convos)
    return convos


def gen_aggressive_customer():
    """Aggressive customer — model stays calm."""
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
            "Ну вы обнаглели, такие цены ломить",
        ]))})
        convos.append({"role": "assistant", "content": (
            "Понимаю ваше беспокойство. Наши цены включают качественные материалы "
            "и профессиональное оборудование. Мы гарантируем результат. "
            "Если хотите сэкономить, могу предложить экспресс-мойку — она дешевле."
        )})
        service = random.choice(["экспресс", "комплекс"])
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Ладно, давайте экспресс тогда",
            "Ну ладно, записывайте на комплексную",
            "Хорошо, уговорили. Давайте комплекс",
        ]))})
        convos.append({"role": "assistant", "content": "Хорошо! Когда вам удобно?"})

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


def gen_background_noise():
    """Background noise disrupts conversation."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    service = random.choice(["экспресс", "комплекс", "воск"])
    p = PRICES[car_class]

    convos = begin_dialog()

    # First attempt with noise
    noisy_req = random.choice([
        f"[шум дороги] мне бы на мойку [неразборчиво]",
        f"Здравствуйте, мне... [шум двигателя] ...мойку нужно",
        f"[помехи] ...записаться на мойку [шум]",
        f"Алло [плохая связь] мне бы помыть [неразборчиво]",
        f"[сигнал машины] Короче, мне мойку надо [шум дороги]",
    ])
    convos.append({"role": "user", "content": noisy_req})

    convos.append({"role": "assistant", "content": random.choice([
        "Здравствуйте! Вас плохо слышно. Вы хотите записаться на мойку?",
        "Добрый день! Связь плохая, повторите, пожалуйста. Вам нужна мойка?",
        "Алло! Вас почти не слышно. Вы сказали — мойка?",
    ])})

    convos.append({"role": "user", "content": naturalize(random.choice([
        "Да да да, на мойку записаться",
        "Ну да, на мойку! Сейчас окно закрою... вот, так лучше?",
        "Ага, мойка нужна. Подождите, отъеду от дороги... Так лучше слышно?",
        "Да, на мойку! Извините, на улице шумно",
    ]))})

    convos.append({"role": "assistant", "content": "Теперь слышу вас хорошо! Какой у вас автомобиль?"})
    convos.append({"role": "user", "content": naturalize(f"{car_name}")})
    convos.append({"role": "assistant", "content": (
        f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}. Когда удобно?"
    )})

    # Sometimes noise again mid-dialog
    if random.random() < 0.4:
        convos.append({"role": "user", "content": f"Давайте [шум] ...{day}... [помехи] ...{time}"})
        convos.append({"role": "assistant", "content": f"Извините, плохо расслышала. Вы сказали {day}, {time}?"})
        convos.append({"role": "user", "content": naturalize(f"Да, {day}, {time}")})
    else:
        convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {time}")})

    convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    convos = end_with_goodbye(convos)
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


def gen_callback_after_disconnect():
    """Call back after disconnect."""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    service = random.choice(["экспресс", "комплекс", "воск"])
    p = PRICES[car_class]

    convos = begin_dialog()

    callbacks = [
        "Алло, меня только что разъединило. Я записывался на мойку",
        "Здравствуйте, связь оборвалась. Мы не договорили, я записывался",
        "Это я только что звонил, связь пропала. Мы на мойку записывались",
        "Алло, ну вот, опять связь. Я записывался на мойку, нас разъединило",
        "Ну вот, дозвонился опять. Мы с вами разговаривали, связь пропала",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(callbacks))})

    convos.append({"role": "assistant", "content": random.choice([
        "Здравствуйте! Да, извините за неудобство. Давайте продолжим. Подскажите ваше имя?",
        "Добрый день! Приносим извинения за обрыв связи. Как вас зовут, чтобы я нашла запись?",
    ])})

    convos.append({"role": "user", "content": naturalize(name)})

    if random.random() < 0.5:
        # Was mid-booking
        convos.append({"role": "assistant", "content": (
            f"{name}, мы остановились на выборе времени. "
            f"{SERVICE_NAMES[service].capitalize()} для {car_name}. На какое время записать?"
        )})
        convos.append({"role": "user", "content": naturalize(f"Давайте {day}, {time}")})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)
    else:
        # Start fresh
        convos.append({"role": "assistant", "content": "Не нашла незавершённую запись. Давайте начнём заново. Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": (
            f"{SERVICE_NAMES[service].capitalize()} для {car_name} — {price_str(p[service])}. Когда удобно?"
        )})
        convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
        convos = ask_name_and_confirm(convos, name, car_name, service, car_class, day, time)

    convos = end_with_goodbye(convos)
    return convos


# ── Main generation ────────────────────────────────────────────────────────

def generate_all_dialogs():
    """Generate exactly 1500 dialogs according to specified distribution."""
    dialogs = []

    # Distribution: 1500 total
    for _ in range(300):      # 1. Simple wash booking
        dialogs.append(gen_simple_wash())
    for _ in range(150):      # 2. Premium/detailing
        dialogs.append(gen_premium_service())
    for _ in range(120):      # 3. Multiple services combo
        dialogs.append(gen_combo_services())
    for _ in range(120):      # 4. Car type pricing
        dialogs.append(gen_car_type_matters())
    for _ in range(120):      # 5. User self-corrects
        dialogs.append(gen_self_correction())
    for _ in range(100):      # 6. Time preference + slot selection
        dialogs.append(gen_time_preference())
    for _ in range(80):       # 7. Time unavailable -> alternatives
        dialogs.append(gen_time_unavailable())
    for _ in range(80):       # 8. Price inquiry -> booking
        dialogs.append(gen_price_then_booking())
    for _ in range(60):       # 9. Cancellation
        dialogs.append(gen_cancellation())
    for _ in range(60):       # 10. Reschedule
        dialogs.append(gen_reschedule())
    for _ in range(40):       # 11. User changes mind completely
        dialogs.append(gen_change_mind())
    for _ in range(40):       # 12. Walk-in
        dialogs.append(gen_walkin_check())
    for _ in range(30):       # 13. Regular customer / loyalty
        dialogs.append(gen_regular_customer())
    for _ in range(30):       # 14. Price inquiry only
        dialogs.append(gen_price_only())
    for _ in range(30):       # 15. Frustrated all slots taken
        dialogs.append(gen_frustrated_slots())
    for _ in range(30):       # 16. Rush "мне срочно"
        dialogs.append(gen_rush())
    for _ in range(30):       # 17. Surprised at price
        dialogs.append(gen_price_surprise())
    for _ in range(30):       # 18. Aggressive customer
        dialogs.append(gen_aggressive_customer())
    for _ in range(20):       # 19. Background noise disrupts
        dialogs.append(gen_background_noise())
    for _ in range(20):       # 20. Transfer to admin
        dialogs.append(gen_transfer_to_admin())
    for _ in range(10):       # 21. Call back after disconnect
        dialogs.append(gen_callback_after_disconnect())

    random.shuffle(dialogs)
    return dialogs


if __name__ == "__main__":
    dialogs = generate_all_dialogs()

    output_path = os.path.join(os.path.dirname(__file__), "carwash_dialogs_v3.jsonl")

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
                assert len(obj["conversations"]) >= 3
                assert obj["conversations"][0]["role"] == "system"
                valid += 1
            except Exception as e:
                print(f"ERROR line {i+1}: {e}")
        print(f"Validated: {valid}/{len(lines)} lines OK")
