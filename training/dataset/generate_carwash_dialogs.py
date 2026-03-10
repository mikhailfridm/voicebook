#!/usr/bin/env python3
"""Generate 400 SFT training dialogs for car wash AI voice receptionist."""

import json
import random
import os

random.seed(42)

SYSTEM_PROMPT = "Вы — администратор автомойки. Помогаете клиентам записаться на мойку, выбрать тип услуги и удобное время. Говорите вежливо и по делу."

# --- Data pools ---

FILLERS = ["ну", "эм", "так", "вот", "ааа", "короче", "слушайте", "это самое", "как бы", "ну это", "в общем", "типа", "значит", "ну вот", "так сказать"]
NOISE = ["[неразборчиво]", "[шум]", "[помехи]"]
GREETINGS_CLIENT = [
    "Здравствуйте", "Добрый день", "Привет", "Алло", "Здрасьте", "Алё", "Добрый", "Здрасте",
    "Алло, здравствуйте", "Да, здравствуйте", "Добрый день, алло", "Привет, это автомойка?",
    "Алло, это мойка?", "Здравствуйте, мне нужна мойка", "Добрый день, хотел бы записаться",
]
GREETINGS_ADMIN = [
    "Здравствуйте! Автомойка «Блеск», чем могу помочь?",
    "Добрый день! Автомойка, слушаю вас.",
    "Здравствуйте! Автомойка «Чистый кузов», чем могу быть полезен?",
    "Добрый день! Это автомойка «Аква», слушаю вас.",
    "Здравствуйте! Автомойка «Мойдодыр», чем помочь?",
    "Добрый день! Это автомойка, рады вашему звонку. Чем могу помочь?",
    "Здравствуйте! Автомойка «Кристалл», слушаю вас внимательно.",
    "Добрый день! Автомойка «Премиум Вош», чем могу помочь?",
]

CAR_MODELS_SEDAN = [
    ("Тойота Камри", "седан"), ("Хёндай Солярис", "седан"), ("Киа Рио", "седан"),
    ("Фольксваген Поло", "седан"), ("Шкода Октавия", "седан"), ("Лада Веста", "седан"),
    ("Рено Логан", "седан"), ("Мазда 3", "седан"), ("Хонда Цивик", "седан"),
    ("Ниссан Альмера", "седан"), ("Шевроле Круз", "седан"), ("Форд Фокус", "седан"),
    ("Пежо 408", "седан"), ("Ситроен С4", "седан"), ("Лада Гранта", "седан"),
    ("Киа Серато", "седан"), ("Хёндай Элантра", "седан"),
]
CAR_MODELS_CROSSOVER = [
    ("Тойота РАВ4", "кроссовер"), ("Хёндай Туссан", "кроссовер"), ("Киа Спортейдж", "кроссовер"),
    ("Ниссан Кашкай", "кроссовер"), ("Мазда CX-5", "кроссовер"), ("Рено Дастер", "кроссовер"),
    ("Шкода Кодиак", "кроссовер"), ("Фольксваген Тигуан", "кроссовер"),
    ("Хавейл Джолион", "кроссовер"), ("Черри Тигго 7 Про", "кроссовер"),
    ("Джили Атлас", "кроссовер"), ("Чанган CS75", "кроссовер"),
]
CAR_MODELS_SUV = [
    ("Тойота Ленд Крузер", "внедорожник"), ("Мерседес GLS", "внедорожник"),
    ("БМВ X5", "внедорожник"), ("Лексус LX", "внедорожник"),
    ("Ниссан Патрол", "внедорожник"), ("Ленд Ровер", "внедорожник"),
    ("Мицубиси Паджеро", "внедорожник"), ("Кадиллак Эскалейд", "внедорожник"),
    ("Инфинити QX80", "внедорожник"), ("УАЗ Патриот", "внедорожник"),
]
CAR_MODELS_PREMIUM = [
    ("Мерседес E-класс", "седан"), ("БМВ 5 серии", "седан"), ("Ауди А6", "седан"),
    ("Лексус ES", "седан"), ("Порше Кайен", "кроссовер"), ("Мерседес GLE", "кроссовер"),
    ("БМВ X3", "кроссовер"), ("Ауди Q5", "кроссовер"), ("Вольво XC90", "кроссовер"),
    ("Мерседес S-класс", "седан"), ("БМВ 7 серии", "седан"), ("Ауди А8", "седан"),
    ("Порше Панамера", "седан"), ("Лексус LS", "седан"), ("Генезис G80", "седан"),
]
CAR_MODELS_COMMERCIAL = [
    ("Газель", "коммерческий"), ("Газель Некст", "коммерческий"), ("Форд Транзит", "коммерческий"),
    ("Мерседес Спринтер", "коммерческий"), ("Фиат Дукато", "коммерческий"),
    ("Пежо Боксер", "коммерческий"), ("Ситроен Джампер", "коммерческий"),
    ("ГАЗон Некст", "коммерческий"), ("Соболь", "коммерческий"),
]

# Prices by class
PRICES = {
    "седан": {"экспресс": 500, "комплекс": 1000, "двигатель": 800, "химчистка_частичная": 3000, "химчистка_полная": 7000, "полировка": 5000, "керамика": 15000, "предпродажная": 8000, "детейлинг": 12000},
    "кроссовер": {"экспресс": 700, "комплекс": 1300, "двигатель": 1000, "химчистка_частичная": 3500, "химчистка_полная": 8000, "полировка": 6000, "керамика": 18000, "предпродажная": 10000, "детейлинг": 15000},
    "внедорожник": {"экспресс": 900, "комплекс": 1500, "двигатель": 1200, "химчистка_частичная": 4000, "химчистка_полная": 10000, "полировка": 7000, "керамика": 22000, "предпродажная": 12000, "детейлинг": 18000},
    "коммерческий": {"экспресс": 1200, "комплекс": 2000, "двигатель": 1500, "химчистка_частичная": 5000, "химчистка_полная": 12000, "полировка": 8000, "керамика": 25000, "предпродажная": 15000, "детейлинг": 20000},
}

DURATIONS = {
    "экспресс": "около тридцати минут",
    "комплекс": "примерно один час",
    "двигатель": "около сорока минут",
    "химчистка_частичная": "два-три часа",
    "химчистка_полная": "четыре-шесть часов",
    "полировка": "три-пять часов",
    "керамика": "от шести до восьми часов",
    "предпродажная": "пять-семь часов",
    "детейлинг": "от шести до десяти часов",
}

SERVICE_NAMES = {
    "экспресс": "экспресс-мойка кузова",
    "комплекс": "комплексная мойка кузова и салона",
    "двигатель": "мойка двигателя",
    "химчистка_частичная": "частичная химчистка салона",
    "химчистка_полная": "полная химчистка салона",
    "полировка": "полировка кузова",
    "керамика": "нанесение керамического покрытия",
    "предпродажная": "предпродажная подготовка",
    "детейлинг": "детейлинг",
}

TIMES = [
    "девять утра", "десять утра", "одиннадцать утра", "двенадцать дня",
    "час дня", "два часа дня", "три часа дня", "четыре часа дня",
    "пять вечера", "девять тридцать", "десять тридцать", "одиннадцать тридцать",
    "двенадцать тридцать", "половина десятого", "половина одиннадцатого",
    "половина двенадцатого", "половина первого", "половина второго",
]

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
]


def add_filler(text, prob=0.4):
    """Randomly add fillers to client speech."""
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
    """Randomly add noise markers."""
    if random.random() < prob:
        words = text.split()
        if len(words) > 2:
            idx = random.randint(0, len(words) - 1)
            words[idx] = random.choice(NOISE)
            text = " ".join(words)
    return text


def add_hesitation(text, prob=0.15):
    """Add hesitations like incomplete words or repeated starts."""
    if random.random() < prob:
        hesitations = [
            "э... ", "м... ", "ну... ", "так... ", "это... ",
            "подождите... ", "секунду... ", "дайте подумать... ",
        ]
        text = random.choice(hesitations) + text[0].lower() + text[1:]
    return text


def naturalize(text):
    """Make client speech natural."""
    text = add_filler(text)
    text = add_noise(text)
    text = add_hesitation(text)
    # Randomly lowercase first letter (informal)
    if random.random() < 0.3 and len(text) > 0:
        text = text[0].lower() + text[1:]
    return text


def price_str(price):
    """Convert price to spelled-out Russian."""
    if price >= 1000:
        thousands = price // 1000
        remainder = price % 1000
        t_words = {1: "одна тысяча", 2: "две тысячи", 3: "три тысячи", 4: "четыре тысячи",
                    5: "пять тысяч", 6: "шесть тысяч", 7: "семь тысяч", 8: "восемь тысяч",
                    9: "девять тысяч", 10: "десять тысяч", 12: "двенадцать тысяч",
                    15: "пятнадцать тысяч", 18: "восемнадцать тысяч", 20: "двадцать тысяч",
                    22: "двадцать две тысячи", 25: "двадцать пять тысяч"}
        t = t_words.get(thousands, f"{thousands} тысяч")
        if remainder == 0:
            return t + " рублей"
        r_words = {300: "триста", 500: "пятьсот", 200: "двести", 100: "сто"}
        r = r_words.get(remainder, f"{remainder}")
        return t + " " + r + " рублей"
    else:
        w = {500: "пятьсот", 600: "шестьсот", 700: "семьсот", 800: "восемьсот", 900: "девятьсот"}
        return w.get(price, str(price)) + " рублей"


def get_car():
    """Pick a random car."""
    pool = random.choice([
        CAR_MODELS_SEDAN, CAR_MODELS_SEDAN, CAR_MODELS_SEDAN,  # weighted
        CAR_MODELS_CROSSOVER, CAR_MODELS_CROSSOVER,
        CAR_MODELS_SUV,
        CAR_MODELS_PREMIUM,
    ])
    return random.choice(pool)


def get_car_for_persona(persona):
    if persona == "premium":
        return random.choice(CAR_MODELS_PREMIUM)
    elif persona == "taxi":
        return random.choice([("Хёндай Солярис", "седан"), ("Киа Рио", "седан"), ("Шкода Октавия", "седан"), ("Рено Логан", "седан"), ("Фольксваген Поло", "седан")])
    elif persona == "sale":
        return random.choice(CAR_MODELS_SEDAN + CAR_MODELS_CROSSOVER)
    elif persona == "fleet":
        return random.choice(CAR_MODELS_COMMERCIAL + [("Лада Ларгус", "седан")])
    elif persona == "newbie":
        return get_car()
    else:
        return get_car()


# ---- Dialog generators by scenario ----

def gen_simple_wash():
    """Simple wash booking (40%)"""
    car_name, car_class = get_car()
    service = random.choice(["экспресс", "комплекс"])
    price = PRICES[car_class][service]
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Greeting
    g_client = random.choice(GREETINGS_CLIENT)
    g_admin = random.choice(GREETINGS_ADMIN)
    convos.append({"role": "user", "content": naturalize(g_client)})
    convos.append({"role": "assistant", "content": g_admin})

    # Request variants
    service_label = SERVICE_NAMES[service]
    requests = [
        f"Хотел бы записаться на мойку",
        f"Мне бы помыть машину",
        f"Нужна мойка, можно записаться?",
        f"Хочу записаться на {service_label}",
        f"Машину бы помыть, когда можно?",
        f"Есть свободное время на мойку?",
        f"Запишите меня на мойку, пожалуйста",
        f"Можно на мойку записаться?",
        f"Мне нужно машину помыть",
        f"Здравствуйте, мойка нужна",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(requests))})

    # Admin asks car class
    car_asks = [
        "Конечно! Подскажите, пожалуйста, марку и класс вашего автомобиля?",
        "С удовольствием запишу вас! Какой у вас автомобиль?",
        "Хорошо! Скажите, пожалуйста, какая у вас машина — марка и тип кузова?",
        "Отлично! А какой у вас автомобиль? Нам важно знать класс для расчёта стоимости.",
    ]
    convos.append({"role": "assistant", "content": random.choice(car_asks)})

    # Client answers car
    car_answers = [
        f"У меня {car_name}",
        f"{car_name}",
        f"Это {car_name}, {car_class}",
        f"Ну {car_name} у меня",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(car_answers))})

    # Admin confirms service and price
    if service == "экспресс":
        upsell = random.choice([
            f" Также могу предложить комплексную мойку с уборкой салона за {price_str(PRICES[car_class]['комплекс'])}.",
            f" Если хотите, можем добавить уборку салона — это будет комплексная мойка за {price_str(PRICES[car_class]['комплекс'])}.",
            "",
            "",
        ])
    else:
        upsell = random.choice([
            " После мойки можем нанести воск для дополнительной защиты кузова.",
            " Также рекомендую обработку воском — защитит кузов на пару недель.",
            "",
            "",
        ])

    price_text = price_str(price)
    duration = DURATIONS[service]
    convos.append({"role": "assistant", "content": f"Отлично, {car_name}. {service_label.capitalize()} для вашего автомобиля стоит {price_text}. По времени — {duration}.{upsell} На какое время вас записать?"})

    # Client picks time
    time_picks = [
        f"Давайте {day} на {time}",
        f"Можно {day} в {time}?",
        f"А {day} на {time} есть?",
        f"Запишите на {day}, {time}",
        f"Хотелось бы {day} часов в {time}",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(time_picks))})

    # Admin confirms
    convos.append({"role": "assistant", "content": f"Записываю вас на {day}, {time}. {service_label.capitalize()}, {car_name}, стоимость — {price_text}. Как вас зовут?"})

    convos.append({"role": "user", "content": naturalize(name)})

    confirmations = [
        f"Отлично, {name}, вы записаны! Ждём вас {day} к {time}. Если планы изменятся, пожалуйста, позвоните заранее. Хорошего дня!",
        f"Готово, {name}! Ваша запись: {day}, {time}, {service_label}. Пожалуйста, приезжайте за пять минут до начала. До встречи!",
        f"Записала вас, {name}. {day.capitalize()}, {time} — {service_label}, {car_name}. Будем ждать! Всего доброго!",
    ]
    convos.append({"role": "assistant", "content": random.choice(confirmations)})

    # Optionally add goodbye
    if random.random() < 0.6:
        byes = ["Спасибо, до свидания!", "Спасибо!", "Ок, спасибо, пока!", "До свидания", "Благодарю, до встречи"]
        convos.append({"role": "user", "content": naturalize(random.choice(byes))})
        convos.append({"role": "assistant", "content": random.choice(["До свидания! Хорошего дня!", "Всего доброго, ждём вас!", "До встречи! Хорошего дня!"])})

    return convos


def gen_complex_inquiry():
    """Complex service inquiry + booking (20%)"""
    persona = random.choice(["premium", "regular", "sale", "newbie"])
    car_name, car_class = get_car_for_persona(persona)
    services_pool = ["химчистка_полная", "химчистка_частичная", "полировка", "керамика", "предпродажная", "детейлинг"]
    service = random.choice(services_pool)
    price = PRICES[car_class][service]
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    # Complex request with questions
    if service == "химчистка_полная":
        req_variants = [
            "Мне нужна химчистка салона. Что это включает и сколько стоит?",
            "Хочу химчистку полную сделать. Расскажите подробнее.",
            "Салон нужно почистить, весь грязный. Что посоветуете?",
            "Мне бы химчистку. У меня ребёнок всё заляпал в салоне.",
        ]
    elif service == "химчистка_частичная":
        req_variants = [
            "Можно только сиденья почистить? Полная химчистка не нужна.",
            "Мне бы коврики и сиденья почистить, можно?",
            "Нужна частичная химчистка, только потолок и сиденья.",
            "Не хочу полную химчистку, только передние сиденья бы почистить.",
        ]
    elif service == "полировка":
        req_variants = [
            "Хочу полировку сделать, кузов уже потускнел.",
            "Можно полировку кузова? Много мелких царапин.",
            "Мне бы полировку. Машина выглядит уставшей.",
            "Интересует полировка. Это абразивная или защитная?",
        ]
    elif service == "керамика":
        req_variants = [
            "Хочу нанести керамику на кузов. Сколько это стоит?",
            "Интересует керамическое покрытие. Расскажите подробнее.",
            "Слышал про жидкое стекло. Это вы делаете?",
            "Хочу защитить кузов. Что лучше — керамика или жидкое стекло?",
        ]
    elif service == "предпродажная":
        req_variants = [
            "Продаю машину, нужна предпродажная подготовка.",
            "Хочу подготовить авто к продаже. Что входит в предпродажную?",
            "Мне бы машину в порядок привести перед продажей.",
            "Нужна предпродажная подготовка, что включает?",
        ]
    else:  # детейлинг
        req_variants = [
            "Интересует детейлинг. Что это такое и сколько стоит?",
            "Хочу детейлинг сделать. Расскажите, что входит.",
            "Мне посоветовали детейлинг. Это полировка с покрытием?",
            "Нужен детейлинг автомобиля. Есть такая услуга?",
        ]

    convos.append({"role": "user", "content": naturalize(random.choice(req_variants))})

    # Admin explains service
    explanations = {
        "химчистка_полная": f"Полная химчистка салона включает глубокую чистку всех сидений, потолка, дверных карт, ковриков и багажника. Используем профессиональные средства и экстракторное оборудование. Для вашего автомобиля {car_name} стоимость составит {price_str(price)}. По времени — {DURATIONS[service]}. Подскажите, какой у вас автомобиль, чтобы я уточнил детали?",
        "химчистка_частичная": f"Конечно, частичная химчистка возможна! Вы можете выбрать конкретные элементы: сиденья, потолок, коврики, двери. Стоимость зависит от объёма работ, начинается от {price_str(price)}. Подскажите, какой у вас автомобиль?",
        "полировка": f"Полировка кузова включает абразивную обработку для удаления царапин и восстановления блеска. Для вашего {car_name} стоимость — от {price_str(price)}, работа займёт {DURATIONS[service]}. После полировки рекомендую защитное покрытие. Какой у вас автомобиль?",
        "керамика": f"Керамическое покрытие — это долговременная защита кузова от царапин, грязи и ультрафиолета. Эффект держится от одного до трёх лет. Стоимость для легкового автомобиля — от {price_str(PRICES['седан']['керамика'])}. Перед нанесением обязательна полировка. Какой у вас автомобиль?",
        "предпродажная": f"Предпродажная подготовка включает полную мойку, химчистку салона, полировку кузова и обработку пластика. Машина будет выглядеть как новая! Стоимость зависит от класса автомобиля. Подскажите марку и модель?",
        "детейлинг": f"Детейлинг — это комплексный уход за автомобилем: глубокая мойка, полировка, защитное покрытие, химчистка салона, обработка всех элементов. Стоимость зависит от класса авто и выбранных процедур. Какой у вас автомобиль?",
    }
    admin_resp = explanations.get(service, "")
    # If admin already asked about car but included car name, fix:
    if car_name in admin_resp:
        admin_resp = admin_resp.replace(f"Какой у вас автомобиль?", "")
    convos.append({"role": "assistant", "content": admin_resp.strip()})

    # Client confirms car (if not already mentioned)
    if "Какой у вас автомобиль?" in admin_resp or "Подскажите" in admin_resp:
        car_resp = [f"У меня {car_name}", f"{car_name}", f"Это {car_name}"]
        convos.append({"role": "user", "content": naturalize(random.choice(car_resp))})
        convos.append({"role": "assistant", "content": f"Хорошо, {car_name}. Стоимость {SERVICE_NAMES[service]} для вашего автомобиля составит {price_str(price)}. Работа займёт {DURATIONS[service]}. Хотите записаться?"})

    # Client agrees
    agrees = [
        "Да, давайте запишусь",
        "Хорошо, записывайте",
        "Ладно, давайте",
        "Окей, хочу записаться",
        "Да, подходит",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(agrees))})

    convos.append({"role": "assistant", "content": f"Отлично! На какой день и время вас записать?"})

    convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {time}")})

    convos.append({"role": "assistant", "content": f"Записываю: {day}, {time}, {SERVICE_NAMES[service]}, {car_name}. Стоимость — {price_str(price)}. Как вас зовут?"})

    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Спасибо, {name}! Вы записаны на {day}, {time}. Пожалуйста, учтите, что работа займёт {DURATIONS[service]}, планируйте время. Будем ждать вас!"})

    return convos


def gen_price_comparison():
    """Price comparison between services (15%)"""
    car_name, car_class = get_car()
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    comparison_type = random.choice(["wash_types", "cleaning_types", "protection_types"])

    if comparison_type == "wash_types":
        convos.append({"role": "user", "content": naturalize("Подскажите, а какие у вас виды мойки и сколько стоят?")})
        p = PRICES[car_class]
        convos.append({"role": "assistant", "content": f"Конечно! У нас есть несколько вариантов. Подскажите сначала, какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        convos.append({"role": "assistant", "content": f"Для {car_name} у нас доступны: экспресс-мойка кузова — {price_str(p['экспресс'])}, {DURATIONS['экспресс']}; комплексная мойка кузова и салона — {price_str(p['комплекс'])}, {DURATIONS['комплекс']}. Также есть мойка двигателя — {price_str(p['двигатель'])}. Что вас интересует?"})

        choice = random.choice(["экспресс", "комплекс"])
        if choice == "экспресс":
            convos.append({"role": "user", "content": naturalize("Давайте экспресс, мне быстро надо")})
        else:
            convos.append({"role": "user", "content": naturalize("Лучше комплексную, раз уж приехал")})

        chosen_price = p[choice]
        convos.append({"role": "assistant", "content": f"Хорошо, {SERVICE_NAMES[choice]} за {price_str(chosen_price)}. На когда вас записать?"})

    elif comparison_type == "cleaning_types":
        convos.append({"role": "user", "content": naturalize("Хочу почистить салон. Какие варианты есть и цены?")})
        convos.append({"role": "assistant", "content": f"Подскажите, пожалуйста, марку вашего автомобиля?"})
        convos.append({"role": "user", "content": naturalize(f"Это {car_name}")})
        p = PRICES[car_class]
        convos.append({"role": "assistant", "content": f"Для {car_name} есть два варианта: частичная химчистка — от {price_str(p['химчистка_частичная'])}, включает чистку отдельных элементов на ваш выбор, займёт {DURATIONS['химчистка_частичная']}. Полная химчистка — {price_str(p['химчистка_полная'])}, включает всё: сиденья, потолок, двери, коврики, багажник. Занимает {DURATIONS['химчистка_полная']}. Что предпочтёте?"})

        choice = random.choice(["химчистка_частичная", "химчистка_полная"])
        if choice == "химчистка_частичная":
            convos.append({"role": "user", "content": naturalize("Давайте частичную, мне только сиденья и коврики")})
        else:
            convos.append({"role": "user", "content": naturalize("Наверное полную лучше, раз уж делать")})

        chosen_price = p[choice]
        convos.append({"role": "assistant", "content": f"Хорошо, {SERVICE_NAMES[choice]} за {price_str(chosen_price)}. Когда вам удобно?"})

    else:  # protection
        convos.append({"role": "user", "content": naturalize("Хочу защитить кузов. Что у вас есть? Полировка, керамика?")})
        convos.append({"role": "assistant", "content": "Подскажите, какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        p = PRICES[car_class]
        convos.append({"role": "assistant", "content": f"Для {car_name} доступны: полировка кузова — от {price_str(p['полировка'])}, восстанавливает блеск и убирает мелкие царапины, занимает {DURATIONS['полировка']}. Керамическое покрытие — от {price_str(p['керамика'])}, это долговременная защита на один-три года, занимает {DURATIONS['керамика']}. Перед керамикой обязательна полировка. Что вас больше интересует?"})

        choice = random.choice(["полировка", "керамика"])
        if choice == "полировка":
            convos.append({"role": "user", "content": naturalize("Пока полировку сделаю, а потом может на керамику приеду")})
        else:
            convos.append({"role": "user", "content": naturalize("Давайте сразу керамику с полировкой, чтобы два раза не ездить")})
            total = p["полировка"] + p["керамика"]
            convos.append({"role": "assistant", "content": f"Отличное решение! Полировка плюс керамическое покрытие — итого {price_str(total)}. Работа займёт примерно полтора дня, оставите автомобиль у нас. Когда вам удобно?"})

        if choice == "полировка":
            convos.append({"role": "assistant", "content": f"Хорошо, полировка за {price_str(p['полировка'])}. Когда вам удобно записаться?"})

    convos.append({"role": "user", "content": naturalize(f"Давайте {day} на {time}")})
    convos.append({"role": "assistant", "content": f"Записываю вас на {day}, {time}. Как вас зовут?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Готово, {name}! Ждём вас {day} к {time}. Хорошего дня!"})

    return convos


def gen_reschedule():
    """Rescheduling/cancellation (10%)"""
    name = random.choice(CLIENT_NAMES)
    car_name, car_class = get_car()
    old_day = random.choice(["сегодня", "завтра", "в среду", "в четверг", "в пятницу"])
    old_time = random.choice(TIMES)
    new_day = random.choice(["послезавтра", "в субботу", "в понедельник", "на следующей неделе", "в воскресенье"])
    new_time = random.choice(TIMES)
    action = random.choice(["reschedule", "reschedule", "cancel"])

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    if action == "reschedule":
        req_variants = [
            f"Я записан на {old_day}, хотел бы перенести",
            f"Мне нужно перенести запись. Я на {old_day} на {old_time} записан",
            f"Слушайте, не смогу приехать {old_day}. Можно перенести?",
            f"Можно перезаписаться? У меня было на {old_day}",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(req_variants))})
        convos.append({"role": "assistant", "content": f"Конечно! Подскажите, пожалуйста, ваше имя, чтобы я нашёл запись."})
        convos.append({"role": "user", "content": naturalize(name)})

        service = random.choice(["экспресс", "комплекс", "полировка", "химчистка_полная"])
        convos.append({"role": "assistant", "content": f"Нашла вашу запись, {name}. {SERVICE_NAMES[service].capitalize()}, {old_day}, {old_time}. На какое время хотите перенести?"})
        convos.append({"role": "user", "content": naturalize(f"Можно {new_day} на {new_time}?")})
        convos.append({"role": "assistant", "content": f"{new_day.capitalize()}, {new_time} — свободно! Переношу вашу запись. Всё остальное без изменений. Ждём вас!"})

    else:  # cancel
        req_variants = [
            f"Хочу отменить запись на {old_day}",
            f"Мне нужно отменить мойку. Я был записан на {old_day}",
            f"Не смогу приехать, отмените мою запись, пожалуйста",
        ]
        convos.append({"role": "user", "content": naturalize(random.choice(req_variants))})
        convos.append({"role": "assistant", "content": f"Хорошо, подскажите ваше имя, пожалуйста."})
        convos.append({"role": "user", "content": naturalize(name)})
        convos.append({"role": "assistant", "content": f"Нашла вашу запись, {name}, на {old_day}, {old_time}. Отменяю. Будем рады видеть вас в другой раз! Хорошего дня."})

    if random.random() < 0.5:
        convos.append({"role": "user", "content": naturalize("Спасибо!")})
        convos.append({"role": "assistant", "content": "Пожалуйста! Всего доброго!"})

    return convos


def gen_first_time():
    """First-time client questions (10%)"""
    car_name, car_class = get_car_for_persona("newbie")
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    question_type = random.choice(["general", "specific_service", "process", "timing"])

    if question_type == "general":
        convos.append({"role": "user", "content": naturalize("Я первый раз к вам звоню. Расскажите, какие услуги у вас есть?")})
        convos.append({"role": "assistant", "content": "Добро пожаловать! У нас полный спектр услуг: экспресс-мойка кузова, комплексная мойка с уборкой салона, химчистка салона — полная и частичная, мойка двигателя, полировка кузова, нанесение керамического покрытия, предпродажная подготовка и детейлинг. Что вас интересует в первую очередь?"})
        convos.append({"role": "user", "content": naturalize(f"Ну мне просто помыть машину. У меня {car_name}")})
        p = PRICES[car_class]
        convos.append({"role": "assistant", "content": f"Для {car_name} экспресс-мойка кузова стоит {price_str(p['экспресс'])}, занимает {DURATIONS['экспресс']}. Если хотите ещё и салон — комплексная мойка за {price_str(p['комплекс'])}, {DURATIONS['комплекс']}. Что предпочитаете?"})
    elif question_type == "specific_service":
        svc = random.choice(["химчистка", "полировка", "керамика"])
        if svc == "химчистка":
            convos.append({"role": "user", "content": naturalize("А у вас химчистка есть? Это что вообще такое?")})
            convos.append({"role": "assistant", "content": "Конечно! Химчистка салона — это глубокая чистка всех тканевых и кожаных поверхностей внутри автомобиля с помощью специальных средств и оборудования. Удаляем пятна, запахи, загрязнения. Есть полная химчистка — весь салон, и частичная — отдельные элементы на выбор. Подскажите, какой у вас автомобиль?"})
        elif svc == "полировка":
            convos.append({"role": "user", "content": naturalize("Что такое полировка? Это как мойка, только лучше?")})
            convos.append({"role": "assistant", "content": "Полировка — это отдельная процедура для восстановления лакокрасочного покрытия кузова. Мы убираем мелкие царапины, потёртости, окисление. После полировки кузов выглядит как новый и блестит. Это не мойка — это уход за покрытием. Какой у вас автомобиль?"})
        else:
            convos.append({"role": "user", "content": naturalize("А что такое керамика для машины? Это что, как плитка?")})
            convos.append({"role": "assistant", "content": "Нет, конечно! Керамическое покрытие — это жидкий состав, который наносится на кузов и образует прочную защитную плёнку. Она защищает от царапин, грязи, ультрафиолета. Эффект держится от одного до трёх лет. Машина дольше остаётся чистой и блестящей. Какой у вас автомобиль?"})

        convos.append({"role": "user", "content": naturalize(f"У меня {car_name}")})
        p = PRICES[car_class]
        if svc == "химчистка":
            convos.append({"role": "assistant", "content": f"Для {car_name}: частичная химчистка — от {price_str(p['химчистка_частичная'])}, полная — {price_str(p['химчистка_полная'])}. Хотите записаться?"})
        elif svc == "полировка":
            convos.append({"role": "assistant", "content": f"Полировка для {car_name} — от {price_str(p['полировка'])}, занимает {DURATIONS['полировка']}. Записать вас?"})
        else:
            convos.append({"role": "assistant", "content": f"Керамическое покрытие для {car_name} — от {price_str(p['керамика'])}. Перед нанесением нужна полировка. Всё вместе — {DURATIONS['керамика']}. Хотите записаться?"})
    elif question_type == "process":
        convos.append({"role": "user", "content": naturalize("А как у вас происходит? Нужно записываться или можно просто приехать?")})
        convos.append({"role": "assistant", "content": "Лучше записаться заранее, чтобы не ждать в очереди. Но если есть свободные места, мы принимаем и без записи. При записи вы приезжаете к назначенному времени, оставляете автомобиль, и мы начинаем работу. Хотите записаться сейчас?"})
        convos.append({"role": "user", "content": naturalize("Да, давайте. Мне просто мойку")})
        convos.append({"role": "assistant", "content": "Хорошо! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})
        p = PRICES[car_class]
        convos.append({"role": "assistant", "content": f"Экспресс-мойка для {car_name} — {price_str(p['экспресс'])}, {DURATIONS['экспресс']}. Комплексная с салоном — {price_str(p['комплекс'])}. Что выберете?"})
    else:  # timing
        convos.append({"role": "user", "content": naturalize("А вы до скольки работаете? И в выходные есть?")})
        convos.append({"role": "assistant", "content": "Мы работаем ежедневно с девяти утра до девяти вечера, включая выходные и праздники. Чем могу помочь?"})
        convos.append({"role": "user", "content": naturalize(f"Хочу записаться на мойку. У меня {car_name}")})
        p = PRICES[car_class]
        convos.append({"role": "assistant", "content": f"Отлично! Для {car_name} экспресс-мойка — {price_str(p['экспресс'])}, комплексная — {price_str(p['комплекс'])}. Когда вам удобно?"})

    # Booking conclusion
    choice = random.choice(["экспресс", "комплекс"])
    if question_type not in ["process", "timing"]:
        convos.append({"role": "user", "content": naturalize(f"Давайте на {day}, {time}")})
    else:
        convos.append({"role": "user", "content": naturalize(f"Давайте {random.choice(['экспресс', 'комплексную'])} на {day}, {time}")})

    convos.append({"role": "assistant", "content": f"Записываю вас на {day}, {time}. Как вас зовут?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Отлично, {name}! Ждём вас {day} к {time}. Если возникнут вопросы — звоните. Хорошего дня!"})

    return convos


def gen_fleet():
    """Fleet/corporate client (5%)"""
    car_name, car_class = get_car_for_persona("fleet")
    name = random.choice(CLIENT_NAMES)
    day = random.choice(DAYS)
    time = random.choice(TIMES)
    num_cars = random.choice([3, 5, 7, 10, 12, 15, 20])
    company = random.choice(["ООО «Логистик»", "ИП Сидоров", "компания «ТрансАвто»", "ООО «Доставка плюс»", "наша фирма", "курьерская служба"])

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    fleet_type = random.choice(["regular_fleet", "commercial_fleet"])

    if fleet_type == "regular_fleet":
        convos.append({"role": "user", "content": naturalize(f"У нас {company}, нужно помыть {num_cars} машин. Работаете с юрлицами?")})
        convos.append({"role": "assistant", "content": f"Здравствуйте! Да, мы работаем с корпоративными клиентами. Для постоянных партнёров предлагаем скидки от десяти процентов. Подскажите, какие автомобили в вашем автопарке?"})

        fleet_cars = random.choice([
            "В основном легковые — Солярисы и Рио",
            "Газели и пара легковых",
            f"Всё кроссоверы — {car_name}",
            "Разные — и легковые, и газели",
        ])
        convos.append({"role": "user", "content": naturalize(fleet_cars)})

        convos.append({"role": "assistant", "content": f"Понятно. Для корпоративных клиентов с автопарком от пяти машин мы предлагаем скидку десять процентов на все виды мойки. При регулярном обслуживании — до пятнадцати процентов. Можем составить удобный график. Какие услуги вас интересуют?"})

        convos.append({"role": "user", "content": naturalize("Нам нужна регулярная мойка, раз в неделю. Экспресс достаточно")})
        convos.append({"role": "assistant", "content": f"Отлично! Предлагаю оформить договор на регулярное обслуживание. {num_cars} автомобилей, экспресс-мойка раз в неделю. Я подготовлю коммерческое предложение с точными ценами. Могу отправить на электронную почту. Подскажите ваш email или удобнее обсудить лично?"})

    else:  # commercial
        convos.append({"role": "user", "content": naturalize(f"У нас {num_cars} газелей, нужно регулярно мыть. Берёте коммерческий транспорт?")})
        convos.append({"role": "assistant", "content": f"Да, мы моем коммерческий транспорт! Газели, фургоны, микроавтобусы. Стоимость экспресс-мойки для Газели — от {price_str(PRICES['коммерческий']['экспресс'])}, комплексная — от {price_str(PRICES['коммерческий']['комплекс'])}. Для корпоративных клиентов скидки. Как часто нужно мыть?"})

        convos.append({"role": "user", "content": naturalize("Два раза в неделю минимум. А скидка какая будет?")})
        convos.append({"role": "assistant", "content": f"При регулярном обслуживании {num_cars} автомобилей два раза в неделю мы готовы предложить скидку пятнадцать процентов. Также можем организовать удобный график, чтобы машины не простаивали. Хотите обсудить детали и заключить договор?"})

    convos.append({"role": "user", "content": naturalize("Да, давайте обсудим. Можно приехать к вам?")})
    convos.append({"role": "assistant", "content": f"Конечно! Приезжайте, мы работаем с девяти до девяти ежедневно. Спросите администратора. Как вас зовут, чтобы мы были готовы к вашему визиту?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Спасибо, {name}! Будем ждать вас. Хорошего дня!"})

    return convos


# --- Additional variation generators for more diversity ---

def gen_simple_wash_v2():
    """Simple wash variant — taxi driver needing quick wash."""
    car_name, car_class = get_car_for_persona("taxi")
    time = random.choice(TIMES[:6])  # morning times
    day = random.choice(["сегодня", "завтра"])
    name = random.choice(CLIENT_NAMES[:15])  # male names mostly

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    taxi_requests = [
        "Мне быстро помыть машину надо, я таксист. Сколько по времени?",
        "Слушайте, я таксист, мне экспресс-мойку бы побыстрее",
        "Работаю в такси, машину надо помыть срочно. Есть места?",
        "Мне мойку побыстрее, я между заказами, такси",
        "Быстрая мойка нужна, я в такси работаю",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(taxi_requests))})

    convos.append({"role": "assistant", "content": f"Понимаю, для вас время — деньги! Экспресс-мойка занимает {DURATIONS['экспресс']}. Какой у вас автомобиль?"})
    convos.append({"role": "user", "content": naturalize(f"{car_name}")})

    price = PRICES[car_class]["экспресс"]
    convos.append({"role": "assistant", "content": f"Экспресс-мойка для {car_name} — {price_str(price)}. Есть свободное место {day} на {time}. Подойдёт?"})

    convos.append({"role": "user", "content": naturalize("Да, отлично, записывайте")})
    convos.append({"role": "assistant", "content": f"Записала! {day.capitalize()}, {time}, экспресс-мойка. Как вас зовут?"})
    convos.append({"role": "user", "content": naturalize(name)})

    # Suggest regular visits
    convos.append({"role": "assistant", "content": f"Готово, {name}! Кстати, для таксистов у нас есть абонемент на десять моек со скидкой двадцать процентов. Могу рассказать подробнее при визите. Ждём вас!"})

    if random.random() < 0.5:
        convos.append({"role": "user", "content": naturalize("О, интересно, расскажете когда приеду. Спасибо!")})
        convos.append({"role": "assistant", "content": "Обязательно! До встречи, хорошего дня!"})

    return convos


def gen_simple_wash_v3():
    """Simple wash variant — premium car owner concerned about quality."""
    car_name, car_class = get_car_for_persona("premium")
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    premium_requests = [
        f"У меня {car_name}, хочу помыть, но переживаю за покрытие. У вас аккуратно моют?",
        f"Мне нужна мойка для {car_name}. Вы бесконтактную делаете? Не хочу царапин.",
        f"Здравствуйте, у меня {car_name}. Очень важно, чтобы мыли аккуратно, без тряпок.",
        f"Хочу помыть {car_name}. У вас какие материалы? Губки, тряпки?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(premium_requests))})

    convos.append({"role": "assistant", "content": f"Понимаю ваше беспокойство! Мы используем бесконтактную мойку высокого давления и только профессиональные микрофибровые материалы. Для автомобилей премиум-класса, таких как {car_name}, рекомендую комплексную мойку с особым вниманием к деталям. Стоимость — {price_str(PRICES[car_class]['комплекс'])}."})

    quality_questions = [
        "А химия какая? Не повредит лак?",
        "А вы сушите машину после мойки? Чтобы разводов не было",
        "А диски тоже моете? У меня литые дорогие",
        "Хорошо. А воск нужен или нет?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(quality_questions))})

    quality_answers = [
        "Мы используем только pH-нейтральные шампуни премиум-класса, абсолютно безопасные для лакокрасочного покрытия. После мойки обязательно сушим воздухом и протираем микрофиброй, чтобы не было разводов.",
        "Конечно! Мы тщательно моем и сушим автомобиль, включая диски и арки. Используем только безопасные средства. Рекомендую также обработку воском — он дополнительно защитит покрытие.",
        "Все наши средства сертифицированы и безопасны. После мойки наносим осушитель и протираем. Если хотите дополнительную защиту, можем нанести жидкий воск — это плюс двести рублей.",
    ]
    convos.append({"role": "assistant", "content": random.choice(quality_answers)})

    convos.append({"role": "user", "content": naturalize(f"Хорошо, убедили. Запишите на {day}, {time}")})
    convos.append({"role": "assistant", "content": f"Записываю вас на {day}, {time}. Комплексная мойка, {car_name}. Как вас зовут?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Спасибо, {name}! Ваш {car_name} будет в надёжных руках. Ждём вас {day} к {time}. До встречи!"})

    return convos


def gen_presale():
    """Pre-sale preparation variant."""
    car_name, car_class = get_car_for_persona("sale")
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    sale_requests = [
        "Продаю машину, хочу привести в порядок перед показом",
        "Нужно подготовить авто к продаже. Что посоветуете?",
        "Хочу продать машину подороже. Какие услуги помогут?",
        "Мне бы предпродажную подготовку сделать",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(sale_requests))})

    convos.append({"role": "assistant", "content": f"Отличная идея! У нас есть комплексная предпродажная подготовка: полная мойка, химчистка салона, полировка кузова, обработка пластика, чернение шин. Автомобиль будет выглядеть максимально привлекательно. Какой у вас автомобиль?"})

    convos.append({"role": "user", "content": naturalize(f"{car_name}")})
    p = PRICES[car_class]
    convos.append({"role": "assistant", "content": f"Для {car_name} предпродажная подготовка стоит {price_str(p['предпродажная'])}. Работа занимает {DURATIONS['предпродажная']}. Это включает всё для идеального вида. Также можем отдельно сделать полировку за {price_str(p['полировка'])} или химчистку за {price_str(p['химчистка_полная'])}. Что предпочтёте?"})

    choice = random.choice(["full", "partial"])
    if choice == "full":
        convos.append({"role": "user", "content": naturalize("Давайте полную предпродажную, мне важно продать подороже")})
        convos.append({"role": "assistant", "content": f"Правильное решение! Записываю на предпродажную подготовку, {price_str(p['предпродажная'])}. Машину нужно будет оставить на {DURATIONS['предпродажная']}. Когда удобно?"})
    else:
        convos.append({"role": "user", "content": naturalize("А может полировку и мойку? Салон в нормальном состоянии")})
        total = p["полировка"] + p["комплекс"]
        convos.append({"role": "assistant", "content": f"Хорошо! Полировка плюс комплексная мойка — {price_str(total)}. Займёт около пяти-шести часов. Когда вам удобно?"})

    convos.append({"role": "user", "content": naturalize(f"{day} с утра, на {time}")})
    convos.append({"role": "assistant", "content": f"Записываю на {day}, {time}. Как вас зовут?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Отлично, {name}! Ждём вас {day} к {time}. После наших процедур ваш {car_name} будет как новый — покупатели оценят! До встречи!"})

    return convos


def gen_engine_wash():
    """Engine wash dialog."""
    car_name, car_class = get_car()
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    engine_requests = [
        "Мне нужно помыть двигатель. Делаете?",
        "Хочу двигатель помыть, можно?",
        "Под капотом всё грязное, можно помыть?",
        "Мне мойку двигателя, это возможно?",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(engine_requests))})

    convos.append({"role": "assistant", "content": "Да, мы делаем мойку двигателя! Используем специальные средства и пар, чтобы не повредить электрику. Подскажите, какой у вас автомобиль?"})

    convos.append({"role": "user", "content": naturalize(f"{car_name}")})
    p = PRICES[car_class]
    convos.append({"role": "assistant", "content": f"Мойка двигателя для {car_name} — {price_str(p['двигатель'])}, занимает {DURATIONS['двигатель']}. Хотите заодно помыть и кузов? Экспресс-мойка — ещё {price_str(p['экспресс'])}."})

    add_wash = random.choice([True, False])
    if add_wash:
        convos.append({"role": "user", "content": naturalize("Да, давайте и кузов тоже")})
        total = p["двигатель"] + p["экспресс"]
        convos.append({"role": "assistant", "content": f"Отлично! Мойка двигателя плюс экспресс-мойка кузова — итого {price_str(total)}. На когда записать?"})
    else:
        convos.append({"role": "user", "content": naturalize("Нет, только двигатель")})
        convos.append({"role": "assistant", "content": f"Хорошо, только мойка двигателя — {price_str(p['двигатель'])}. На когда записать?"})

    convos.append({"role": "user", "content": naturalize(f"На {day}, {time}")})
    convos.append({"role": "assistant", "content": f"Записываю: {day}, {time}. Как вас зовут?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Готово, {name}! Ждём вас {day} к {time}. До свидания!"})

    return convos


def gen_detailing():
    """Detailing dialog."""
    car_name, car_class = random.choice([get_car_for_persona("premium"), get_car()])
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]
    convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
    convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})

    detail_requests = [
        "Интересует детейлинг. Что входит и сколько стоит?",
        "Хочу полный детейлинг сделать",
        "Расскажите про детейлинг, пожалуйста",
        "Мне посоветовали у вас детейлинг сделать",
    ]
    convos.append({"role": "user", "content": naturalize(random.choice(detail_requests))})

    convos.append({"role": "assistant", "content": "Детейлинг — это максимально комплексный уход за автомобилем. Включает: глубокую мойку кузова и колёс, удаление битума и железа, полировку лакокрасочного покрытия, нанесение защитного состава, полную химчистку салона, обработку кожи, пластика и стёкол. Машина преображается полностью. Какой у вас автомобиль?"})

    convos.append({"role": "user", "content": naturalize(f"У меня {car_name}")})
    p = PRICES[car_class]
    convos.append({"role": "assistant", "content": f"Для {car_name} стоимость детейлинга — от {price_str(p['детейлинг'])}. Работа занимает {DURATIONS['детейлинг']}. Автомобиль нужно будет оставить у нас. Хотите записаться?"})

    convos.append({"role": "user", "content": naturalize("Да, давайте. А можно ещё керамику нанести?")})
    total = p["детейлинг"] + p["керамика"]
    convos.append({"role": "assistant", "content": f"Конечно! Детейлинг с нанесением керамического покрытия — отличная комбинация. Стоимость — {price_str(total)}. По времени — около двух дней. Когда вам удобно?"})

    convos.append({"role": "user", "content": naturalize(f"Давайте {day}, привезу с утра")})
    convos.append({"role": "assistant", "content": f"Записываю: {day}, привозите к девяти утра. Детейлинг плюс керамика, {car_name}. Как вас зовут?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"Спасибо, {name}! Ваш {car_name} будет в идеальном состоянии. Ждём вас {day} утром. Всего доброго!"})

    return convos


def gen_simple_wash_varied():
    """Another simple wash variant with more natural variation."""
    car_name, car_class = get_car()
    service = random.choice(["экспресс", "комплекс", "экспресс", "экспресс"])
    price = PRICES[car_class][service]
    time = random.choice(TIMES)
    day = random.choice(DAYS)
    name = random.choice(CLIENT_NAMES)

    convos = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Some dialogs start with admin greeting (incoming call scenario)
    if random.random() < 0.3:
        convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})
        convos.append({"role": "user", "content": naturalize(random.choice([
            "Да, мне бы на мойку записаться",
            "Здравствуйте, хочу машину помыть",
            "Алло, мне мойка нужна",
            "Да, можно записаться?",
        ]))})
    else:
        convos.append({"role": "user", "content": naturalize(random.choice(GREETINGS_CLIENT))})
        convos.append({"role": "assistant", "content": random.choice(GREETINGS_ADMIN)})
        convos.append({"role": "user", "content": naturalize(random.choice([
            f"Мне бы помыть {car_name}",
            "Хочу записаться на мойку",
            "Машину помыть надо",
            "Нужна мойка, есть время?",
            f"Можно на мойку? У меня {car_name}",
        ]))})

    if car_name not in convos[-1]["content"]:
        convos.append({"role": "assistant", "content": "Конечно! Какой у вас автомобиль?"})
        convos.append({"role": "user", "content": naturalize(f"{car_name}")})

    service_label = SERVICE_NAMES[service]
    convos.append({"role": "assistant", "content": f"{car_name}, хорошо! {service_label.capitalize()} — {price_str(price)}, {DURATIONS[service]}. Когда вам удобно?"})

    convos.append({"role": "user", "content": naturalize(f"{day}, {time}")})
    convos.append({"role": "assistant", "content": f"Записала вас на {day}, {time}. Ваше имя?"})
    convos.append({"role": "user", "content": naturalize(name)})
    convos.append({"role": "assistant", "content": f"{name}, записаны! Ждём вас. Хорошего дня!"})

    return convos


# --- Main generation ---

def generate_all_dialogs():
    """Generate 400 dialogs according to scenario distribution."""
    dialogs = []

    # Simple wash booking (40% = 160)
    # Split across variants for diversity
    for _ in range(60):
        dialogs.append(gen_simple_wash())
    for _ in range(30):
        dialogs.append(gen_simple_wash_v2())  # taxi
    for _ in range(30):
        dialogs.append(gen_simple_wash_v3())  # premium
    for _ in range(20):
        dialogs.append(gen_engine_wash())
    for _ in range(20):
        dialogs.append(gen_simple_wash_varied())

    # Complex service inquiry + booking (20% = 80)
    for _ in range(80):
        dialogs.append(gen_complex_inquiry())

    # Price comparison (15% = 60)
    for _ in range(60):
        dialogs.append(gen_price_comparison())

    # Rescheduling/cancellation (10% = 40)
    for _ in range(40):
        dialogs.append(gen_reschedule())

    # First-time client questions (10% = 40)
    for _ in range(40):
        dialogs.append(gen_first_time())

    # Fleet/corporate (5% = 20)
    for _ in range(10):
        dialogs.append(gen_fleet())
    for _ in range(5):
        dialogs.append(gen_presale())
    for _ in range(5):
        dialogs.append(gen_detailing())

    # Shuffle to mix scenarios
    random.shuffle(dialogs)

    return dialogs


if __name__ == "__main__":
    dialogs = generate_all_dialogs()

    output_path = os.path.join(os.path.dirname(__file__), "carwash_dialogs.jsonl")

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
                assert len(obj["conversations"]) >= 4  # system + at least 2 turns
                assert obj["conversations"][0]["role"] == "system"
                valid += 1
            except Exception as e:
                print(f"ERROR line {i+1}: {e}")
        print(f"Validated: {valid}/{len(lines)} lines OK")
