#!/usr/bin/env python3
"""Generate 400 SFT beauty salon dialogs in JSONL format."""
import json
import random
import os

random.seed(42)

SYSTEM_PROMPT = "Вы — администратор салона красоты. Помогаете клиентам записаться на услуги, выбрать мастера и удобное время. Говорите вежливо, профессионально и тепло."

# Masters by specialty
MASTERS = {
    "hair": ["Анна", "Светлана", "Марина", "Ольга", "Екатерина", "Ирина"],
    "nails": ["Юлия", "Татьяна", "Наталья", "Алёна", "Кристина"],
    "brows": ["Дарья", "Елена", "Виктория", "Мария"],
    "lashes": ["Дарья", "Елена", "Виктория", "Анастасия"],
    "cosmetology": ["Людмила Сергеевна", "Оксана Викторовна", "Ирина Андреевна"],
    "massage": ["Андрей", "Сергей", "Елена"],
    "men": ["Дмитрий", "Артём", "Кирилл"],
}

# Services with prices
SERVICES = {
    "Стрижка женская": {"price": (2500, 4500), "duration": "час", "masters": "hair"},
    "Стрижка мужская": {"price": (1200, 2000), "duration": "сорок минут", "masters": "men"},
    "Стрижка детская": {"price": (800, 1500), "duration": "тридцать минут", "masters": "hair"},
    "Окрашивание в один тон": {"price": (4000, 7000), "duration": "два часа", "masters": "hair"},
    "Балаяж": {"price": (7000, 12000), "duration": "три часа", "masters": "hair"},
    "Мелирование": {"price": (5000, 9000), "duration": "два с половиной часа", "masters": "hair"},
    "Тонирование": {"price": (3000, 5000), "duration": "полтора часа", "masters": "hair"},
    "Маникюр классический": {"price": (1500, 2500), "duration": "час", "masters": "nails"},
    "Маникюр аппаратный": {"price": (2000, 3000), "duration": "час", "masters": "nails"},
    "Маникюр с гель-лаком": {"price": (2500, 3500), "duration": "полтора часа", "masters": "nails"},
    "Педикюр": {"price": (2500, 4000), "duration": "полтора часа", "masters": "nails"},
    "Коррекция бровей": {"price": (800, 1500), "duration": "двадцать минут", "masters": "brows"},
    "Окрашивание бровей": {"price": (1000, 1800), "duration": "тридцать минут", "masters": "brows"},
    "Ламинирование бровей": {"price": (2000, 3500), "duration": "сорок минут", "masters": "brows"},
    "Наращивание ресниц": {"price": (3000, 5500), "duration": "два часа", "masters": "lashes"},
    "Ламинирование ресниц": {"price": (2500, 4000), "duration": "час", "masters": "lashes"},
    "Чистка лица": {"price": (3500, 6000), "duration": "полтора часа", "masters": "cosmetology"},
    "Пилинг": {"price": (3000, 5000), "duration": "сорок минут", "masters": "cosmetology"},
    "Уходовая процедура для лица": {"price": (4000, 7000), "duration": "час", "masters": "cosmetology"},
    "Массаж": {"price": (3000, 5000), "duration": "час", "masters": "massage"},
    "Укладка": {"price": (1500, 3000), "duration": "сорок минут", "masters": "hair"},
    "Свадебная причёска": {"price": (5000, 10000), "duration": "два часа", "masters": "hair"},
    "Вечерняя причёска": {"price": (3500, 6000), "duration": "полтора часа", "masters": "hair"},
    "Кератиновое выпрямление": {"price": (6000, 12000), "duration": "три часа", "masters": "hair"},
    "Ботокс для волос": {"price": (5000, 10000), "duration": "два с половиной часа", "masters": "hair"},
}

DAYS = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу"]
DAYS_NOM = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
TIMES = ["десять утра", "одиннадцать", "двенадцать", "час дня", "два часа", "три часа", "четыре часа", "пять часов", "полдвенадцатого", "полвторого", "половину третьего"]
TIMES_SHORT = ["10:00", "11:00", "11:30", "12:00", "13:00", "14:00", "14:30", "15:00", "16:00", "17:00"]

CLIENT_NAMES_F = ["Анна", "Мария", "Елена", "Наталья", "Ольга", "Татьяна", "Ирина", "Светлана", "Юлия", "Екатерина",
                  "Алина", "Дарья", "Ксения", "Полина", "Виктория", "Софья", "Валерия", "Карина", "Диана", "Кристина",
                  "Людмила", "Галина", "Нина", "Тамара", "Зинаида", "Марина", "Алёна", "Вера", "Надежда", "Любовь"]
CLIENT_NAMES_M = ["Алексей", "Дмитрий", "Сергей", "Андрей", "Максим", "Артём", "Иван", "Михаил", "Николай", "Павел"]
CHILD_NAMES = ["Маша", "Даша", "Соня", "Алиса", "Ваня", "Петя", "Миша", "Саша", "Катя", "Лиза"]

PHONES = [f"+7{random.randint(900,999)}{random.randint(1000000,9999999)}" for _ in range(100)]

# Fillers and hesitations
FILLERS = ["ну", "эм", "так", "вот", "ааа", "короче", "слушайте", "это", "ну это", "как бы", "ну вот",
           "в общем", "значит", "типа", "ну типа", "это самое", "как его", "ну как бы"]

GREETINGS_CLIENT = [
    "Здравствуйте", "Добрый день", "Здрасте", "Алло, здравствуйте", "Привет", "Добрый вечер",
    "Алло", "Да, здравствуйте", "Алло, добрый день", "Здрасьте"
]

GREETINGS_ADMIN = [
    "Салон красоты «Гармония», здравствуйте! Чем могу помочь?",
    "Салон красоты «Гармония», добрый день! Слушаю вас.",
    "Добрый день! Салон «Гармония», чем могу быть полезна?",
    "Здравствуйте! Салон красоты «Гармония». Как я могу вам помочь?",
    "Салон «Гармония», добрый день! Рада вас слышать!",
    "Добрый день, салон «Гармония»! Подскажите, чем могу помочь?",
]

def filler():
    if random.random() < 0.4:
        return random.choice(FILLERS) + ", "
    return ""

def add_filler(text):
    """Add filler to beginning of text."""
    if random.random() < 0.5:
        f = random.choice(FILLERS)
        return f"{f}, {text[0].lower()}{text[1:]}"
    return text

def noise():
    """Random noise marker."""
    if random.random() < 0.08:
        return " [неразборчиво] "
    return ""

def hesitation():
    """Add hesitation."""
    opts = ["...", "… ", "— ", ""]
    return random.choice(opts)

def price_text(price_range):
    p = random.randrange(price_range[0], price_range[1] + 1, 500)
    return p, spell_price(p)

def spell_price(p):
    """Spell out price in Russian."""
    thousands = p // 1000
    hundreds = (p % 1000) // 100
    remainder = p % 100

    parts = []
    if thousands == 1:
        parts.append("тысяча")
    elif thousands in (2, 3, 4):
        t_words = {2: "две", 3: "три", 4: "четыре"}
        parts.append(f"{t_words[thousands]} тысячи")
    elif thousands >= 5:
        t_words = {5: "пять", 6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять",
                   11: "одиннадцать", 12: "двенадцать"}
        parts.append(f"{t_words.get(thousands, str(thousands))} тысяч")

    if hundreds:
        h_words = {1: "сто", 2: "двести", 3: "триста", 4: "четыреста", 5: "пятьсот",
                   6: "шестьсот", 7: "семьсот", 8: "восемьсот", 9: "девятьсот"}
        parts.append(h_words[hundreds])

    if not parts:
        return f"{p} рублей"

    return " ".join(parts) + " рублей"

def get_master(service_key):
    cat = SERVICES[service_key]["masters"]
    return random.choice(MASTERS[cat])

def get_price(service_key):
    return price_text(SERVICES[service_key]["price"])

def get_duration(service_key):
    return SERVICES[service_key]["duration"]

def random_day():
    idx = random.randint(0, len(DAYS) - 1)
    return DAYS[idx], DAYS_NOM[idx]

def random_time():
    return random.choice(TIMES)

def make_dialog(turns):
    """Build a dialog from list of (role, content) tuples."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for role, content in turns:
        messages.append({"role": role, "content": content})
    return {"conversations": messages}

# ============================================================
# Dialog generators by scenario
# ============================================================

def gen_new_booking_simple(service_key=None):
    """Simple new client booking."""
    if service_key is None:
        service_key = random.choice(list(SERVICES.keys()))

    is_male = service_key in ("Стрижка мужская",)
    name = random.choice(CLIENT_NAMES_M if is_male else CLIENT_NAMES_F)
    master = get_master(service_key)
    price_num, price_str = get_price(service_key)
    duration = get_duration(service_key)
    day_acc, day_nom = random_day()
    time = random_time()
    phone = random.choice(PHONES)

    greeting_admin = random.choice(GREETINGS_ADMIN)
    greeting_client = random.choice(GREETINGS_CLIENT)

    # Client request variants
    request_variants = [
        f"{filler()}хотела бы записаться на {service_key.lower()}",
        f"{filler()}мне бы на {service_key.lower()} записаться",
        f"{filler()}можно записаться на {service_key.lower()}?",
        f"хочу на {service_key.lower()}{hesitation()} записаться",
        f"{filler()}а можно к вам на {service_key.lower()}?",
        f"мне нужна {service_key.lower()}, можно записаться?",
        f"хотела узнать{hesitation()} можно ли записаться на {service_key.lower()}",
        f"запишите меня{hesitation()} на {service_key.lower()}, пожалуйста",
    ]
    if is_male:
        request_variants = [v.replace("хотела", "хотел") for v in request_variants]

    request = random.choice(request_variants)

    turns = []
    turns.append(("assistant", greeting_admin))
    turns.append(("user", f"{greeting_client}! {noise()}{request}"))

    # Admin suggests master
    master_suggest_variants = [
        f"Конечно! На {service_key.lower()} могу предложить мастера {master}. Процедура занимает примерно {duration}, стоимость — {price_str}. На какой день вас записать?",
        f"С удовольствием! У нас {service_key.lower()} делает мастер {master}. По времени это {duration}, стоимость {price_str}. Когда вам удобно?",
        f"Отлично! Могу записать вас к мастеру {master}. {service_key} стоит {price_str}, длительность — {duration}. Какой день вам подходит?",
    ]
    turns.append(("assistant", random.choice(master_suggest_variants)))

    # Client picks day
    day_variants = [
        f"{filler()}а в {day_acc} есть что-нибудь?",
        f"давайте в {day_acc}",
        f"можно на {day_acc}?",
        f"в {day_acc} можно?{noise()}",
        f"{filler()}на {day_acc} есть свободное время?",
    ]
    turns.append(("user", random.choice(day_variants)))

    time2 = random_time()
    time3 = random_time()
    while time2 == time or time3 == time or time2 == time3:
        time2 = random_time()
        time3 = random_time()

    slot_variants = [
        f"В {day_acc} у {master} есть окошки в {time}, в {time2} и в {time3}. Какое время удобнее?",
        f"Давайте посмотрю... В {day_acc} свободно в {time} и в {time2}. Что предпочитаете?",
        f"В {day_acc} {master} может принять вас в {time} или в {time3}. Какой вариант вам больше подходит?",
    ]
    turns.append(("assistant", random.choice(slot_variants)))

    # Client picks time
    time_pick_variants = [
        f"{filler()}давайте в {time}",
        f"в {time} отлично, давайте",
        f"запишите на {time}, пожалуйста",
        f"мне удобно в {time}",
        f"на {time}{hesitation()} подойдёт",
    ]
    turns.append(("user", random.choice(time_pick_variants)))

    # Ask name
    name_ask = [
        "Хорошо! Подскажите, пожалуйста, ваше имя.",
        "Отлично! Как вас зовут?",
        "Записываю! Подскажите ваше имя, пожалуйста.",
        "Замечательно! Как я могу вас записать — ваше имя?",
    ]
    turns.append(("assistant", random.choice(name_ask)))
    turns.append(("user", f"{name}"))

    # Confirm
    confirm_variants = [
        f"{name}, записала вас на {service_key.lower()} к мастеру {master} в {day_acc} в {time}. Стоимость — {price_str}. Всё верно?",
        f"Отлично, {name}! Итак, {service_key.lower()}, мастер {master}, {day_nom}, {time}. Всё правильно?",
        f"Подтверждаю: {name}, {service_key.lower()} у мастера {master}, {day_nom} в {time}. Верно?",
    ]
    turns.append(("assistant", random.choice(confirm_variants)))

    yes_variants = [
        "да, всё верно",
        "да, спасибо",
        "ага, правильно",
        "всё так, спасибо",
        "да, записывайте",
        "да-да, всё ок",
    ]
    turns.append(("user", random.choice(yes_variants)))

    farewell_variants = [
        f"Отлично, {name}! Ждём вас в {day_acc} в {time}. Хорошего дня!",
        f"Замечательно! Запись подтверждена. Ждём вас, {name}! До свидания!",
        f"Готово! {name}, ждём вас в {day_acc}. Если что-то изменится, звоните, мы всегда на связи. До встречи!",
        f"Прекрасно! Всё записала. {name}, будем рады видеть вас! Хорошего дня!",
    ]
    turns.append(("assistant", random.choice(farewell_variants)))

    return make_dialog(turns)


def gen_new_booking_with_master_choice(service_key=None):
    """New booking where client asks about available masters."""
    if service_key is None:
        service_key = random.choice(list(SERVICES.keys()))

    cat = SERVICES[service_key]["masters"]
    masters_list = MASTERS[cat]
    master1, master2 = random.sample(masters_list, min(2, len(masters_list)))
    is_male = service_key in ("Стрижка мужская",)
    name = random.choice(CLIENT_NAMES_M if is_male else CLIENT_NAMES_F)
    price_num, price_str = get_price(service_key)
    duration = get_duration(service_key)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
    turns.append(("user", f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу записаться на {service_key.lower()}{noise()}"))

    turns.append(("assistant", f"Добро пожаловать! На {service_key.lower()} у нас работают мастера {master1} и {master2}. К кому бы вы хотели попасть?"))

    master_choice_variants = [
        f"{filler()}а кто из них лучше?",
        f"а кого посоветуете?",
        f"мне без разницы, {filler()}кто свободен",
        f"к {master1}, пожалуйста",
        f"давайте к {master2}",
        f"а можно к {master1}?",
    ]
    choice = random.choice(master_choice_variants)
    turns.append(("user", choice))

    if "без разницы" in choice or "посоветуете" in choice or "лучше" in choice:
        chosen_master = random.choice([master1, master2])
        turns.append(("assistant", f"Обе прекрасные мастера! Могу предложить {chosen_master} — у неё есть свободное время в {day_acc}. {service_key} стоит {price_str}, занимает {duration}. В {day_acc} удобно?"))
    else:
        chosen_master = master1 if master1 in choice else master2
        turns.append(("assistant", f"Отличный выбор! У {chosen_master} есть время в {day_acc}. {service_key} — {price_str}, длительность {duration}. Подходит?"))

    turns.append(("user", f"{filler()}да, давайте в {day_acc}{hesitation()} а во сколько?"))

    time2 = random_time()
    turns.append(("assistant", f"В {day_acc} {chosen_master} может принять вас в {time} или в {time2}. Что удобнее?"))

    turns.append(("user", f"в {time} давайте"))
    turns.append(("assistant", "Замечательно! Подскажите, пожалуйста, ваше имя."))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, записала вас к {chosen_master} на {service_key.lower()} в {day_acc} в {time}. Ждём вас!"))
    turns.append(("user", "спасибо большое!"))
    turns.append(("assistant", f"Вам спасибо, {name}! До встречи!"))

    return make_dialog(turns)


def gen_regular_rebooking():
    """Regular client rebooking."""
    name = random.choice(CLIENT_NAMES_F)
    service_key = random.choice(list(SERVICES.keys()))
    master = get_master(service_key)
    price_num, price_str = get_price(service_key)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    regular_greetings = [
        f"{random.choice(GREETINGS_CLIENT)}, это {name}, я у вас постоянный клиент. Хочу снова записаться.",
        f"Здравствуйте! {name} беспокоит. {filler()}Как обычно хотела бы записаться.",
        f"Алло, это {name}! Я к вам регулярно хожу на {service_key.lower()}{hesitation()} можно записаться?",
        f"Добрый день, это {name}. Мне бы к {master} как обычно.",
    ]
    turns.append(("user", random.choice(regular_greetings)))

    turns.append(("assistant", f"Здравствуйте, {name}! Рада вас слышать! Конечно, запишу вас. Как обычно, {service_key.lower()} к мастеру {master}?"))

    yes_custom_variants = [
        f"да, как обычно",
        f"да-да, к {master}, всё как всегда",
        f"ага, как обычно, только{hesitation()} может, на этот раз ещё и укладку?",
        f"да, к {master}",
    ]
    choice = random.choice(yes_custom_variants)
    turns.append(("user", choice))

    if "укладку" in choice:
        turns.append(("assistant", f"Конечно! {service_key} и укладку к {master}. Когда вам удобно, {name}?"))
    else:
        turns.append(("assistant", f"Отлично! Когда вам удобно, {name}?"))

    turns.append(("user", f"{filler()}а в {day_acc} есть что-нибудь?"))
    turns.append(("assistant", f"В {day_acc} у {master} свободно в {time}. Подойдёт?"))
    turns.append(("user", f"да, идеально, записывайте"))
    turns.append(("assistant", f"Готово, {name}! Ждём вас в {day_acc} в {time} к {master}. Как всегда, будем рады видеть!"))
    turns.append(("user", "спасибо! до встречи"))
    turns.append(("assistant", f"До свидания, {name}! Хорошего дня!"))

    return make_dialog(turns)


def gen_reschedule():
    """Rescheduling or cancellation."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    service_key = random.choice(list(SERVICES.keys()))
    master = get_master(service_key)
    old_day_acc, old_day_nom = random_day()
    new_day_acc, new_day_nom = random_day()
    while new_day_acc == old_day_acc:
        new_day_acc, new_day_nom = random_day()
    time = random_time()
    new_time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    is_cancel = random.random() < 0.4

    if is_cancel:
        cancel_variants = [
            f"Здравствуйте! Это {name}. {filler()}мне нужно отменить запись на {old_day_acc}",
            f"Добрый день, {name} говорит. К сожалению, не смогу прийти в {old_day_acc}{hesitation()} можно отменить?",
            f"Алло, здравствуйте. Это {name}, {filler()}у меня была запись в {old_day_acc}, но планы поменялись{noise()}",
        ]
        turns.append(("user", random.choice(cancel_variants)))
        turns.append(("assistant", f"Здравствуйте, {name}! Конечно, я отменю вашу запись на {old_day_acc}. Может быть, перенесём на другой день?"))

        if random.random() < 0.5:
            turns.append(("user", f"{filler()}нет, пока не надо, я позвоню позже"))
            turns.append(("assistant", f"Хорошо, {name}! Запись отменена. Будем ждать вашего звонка. Хорошего дня!"))
        else:
            turns.append(("user", f"а можно перенести на {new_day_acc}?"))
            turns.append(("assistant", f"Конечно! В {new_day_acc} у мастера {master} свободно в {new_time}. Устроит?"))
            turns.append(("user", "да, отлично"))
            turns.append(("assistant", f"Перенесла вашу запись на {new_day_acc} в {new_time}. {name}, ждём вас! До свидания!"))
    else:
        reschedule_variants = [
            f"Здравствуйте! Это {name}. {filler()}у меня запись на {old_day_acc}, хотела бы перенести",
            f"Добрый день, {name}. Можно мне перенести запись с {old_day_nom} на другой день?",
            f"Алло! Я {name}, записана в {old_day_acc}{hesitation()} но не получается прийти. Можно перенести?",
        ]
        turns.append(("user", random.choice(reschedule_variants)))
        turns.append(("assistant", f"Здравствуйте, {name}! Конечно, давайте перенесём. На какой день вам удобно?"))
        turns.append(("user", f"а в {new_day_acc} есть время?"))
        turns.append(("assistant", f"В {new_day_acc} могу предложить {new_time}. Подходит?"))
        turns.append(("user", f"да, давайте"))
        turns.append(("assistant", f"Готово! Перенесла вашу запись на {new_day_acc} в {new_time}. {name}, ждём вас!"))
        turns.append(("user", "спасибо!"))
        turns.append(("assistant", "Пожалуйста! Хорошего дня!"))

    return make_dialog(turns)


def gen_price_inquiry():
    """Price inquiry dialog."""
    services_ask = random.sample(list(SERVICES.keys()), random.randint(1, 3))
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    price_q_variants = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хотела узнать цены на ваши услуги",
        f"Здравствуйте! Подскажите, сколько стоит {services_ask[0].lower()}?",
        f"Добрый день! {filler()}интересуют цены{hesitation()} на {services_ask[0].lower()}",
        f"Алло, здравствуйте! А сколько у вас {services_ask[0].lower()} стоит?{noise()}",
    ]
    turns.append(("user", random.choice(price_q_variants)))

    p1_num, p1_str = get_price(services_ask[0])
    d1 = get_duration(services_ask[0])
    turns.append(("assistant", f"Добрый день! {services_ask[0]} у нас стоит {p1_str}, процедура занимает примерно {d1}. Могу я ещё чем-то помочь?"))

    if len(services_ask) > 1:
        turns.append(("user", f"а ещё{hesitation()} сколько стоит {services_ask[1].lower()}?"))
        p2_num, p2_str = get_price(services_ask[1])
        d2 = get_duration(services_ask[1])
        turns.append(("assistant", f"{services_ask[1]} — {p2_str}, длительность {d2}. Желаете записаться?"))

    if len(services_ask) > 2:
        turns.append(("user", f"и {services_ask[2].lower()}?"))
        p3_num, p3_str = get_price(services_ask[2])
        turns.append(("assistant", f"{services_ask[2]} — {p3_str}. Записать вас на какую-нибудь из этих услуг?"))

    # Sometimes books, sometimes doesn't
    if random.random() < 0.5:
        turns.append(("user", f"{filler()}да, запишите на {services_ask[0].lower()}, пожалуйста"))
        master = get_master(services_ask[0])
        day_acc, _ = random_day()
        time = random_time()
        turns.append(("assistant", f"С удовольствием! Мастер {master} может принять вас в {day_acc} в {time}. Подходит?"))
        turns.append(("user", "да, отлично"))
        turns.append(("assistant", "Подскажите ваше имя, пожалуйста."))
        turns.append(("user", name))
        turns.append(("assistant", f"{name}, записала вас! Ждём в {day_acc} в {time}. До встречи!"))
    else:
        no_variants = [
            "нет, спасибо, я подумаю",
            f"{filler()}пока нет, позвоню попозже",
            "не сейчас, спасибо за информацию",
            "я подумаю и перезвоню",
        ]
        turns.append(("user", random.choice(no_variants)))
        turns.append(("assistant", "Конечно! Будем рады видеть вас. Звоните в любое время. Хорошего дня!"))

    return make_dialog(turns)


def gen_multiple_services():
    """Multiple services in one visit."""
    service_keys = random.sample(list(SERVICES.keys()), random.randint(2, 3))
    name = random.choice(CLIENT_NAMES_F)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    multi_variants = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}мне бы на несколько процедур записаться",
        f"Добрый день! Хочу записаться на {service_keys[0].lower()} и {service_keys[1].lower()}",
        f"Здравствуйте! {filler()}можно в один день сделать {service_keys[0].lower()} и {service_keys[1].lower()}?",
    ]
    turns.append(("user", random.choice(multi_variants)))

    total_price = 0
    details = []
    for sk in service_keys:
        p, ps = get_price(sk)
        total_price += p
        m = get_master(sk)
        details.append((sk, ps, m))

    detail_str = ", ".join([f"{d[0].lower()} ({d[1]}, мастер {d[2]})" for d in details])
    total_str = spell_price(total_price)
    turns.append(("assistant", f"Конечно, можно всё в один визит! Вот что могу предложить: {detail_str}. Общая стоимость — {total_str}. Когда вам удобно?"))

    turns.append(("user", f"а в {day_acc} можно?"))
    turns.append(("assistant", f"В {day_acc} можем начать в {time}. Подходит?"))
    turns.append(("user", f"да, записывайте!"))
    turns.append(("assistant", "Подскажите ваше имя, пожалуйста."))
    turns.append(("user", name))

    services_list = ", ".join([d[0].lower() for d in details])
    turns.append(("assistant", f"{name}, записала вас на {day_acc} в {time}: {services_list}. Общая стоимость — {total_str}. Ждём вас!"))
    turns.append(("user", "спасибо огромное!"))
    turns.append(("assistant", f"Вам спасибо, {name}! До свидания!"))

    return make_dialog(turns)


def gen_gift_certificate():
    """Gift certificate or special occasion."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    is_male = name in CLIENT_NAMES_M

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    gift_variants = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу подарить подруге сертификат в ваш салон",
        f"Добрый день! Скажите, а у вас есть подарочные сертификаты?",
        f"Здравствуйте! {filler()}у мамы скоро день рождения, хотела бы купить подарочный сертификат",
        f"Алло! {filler()}я хочу подарить девушке сертификат на услуги салона{hesitation()} это возможно?",
        f"Здрасте! У вас есть подарочные сертификаты? Хочу на 8 марта подарить",
    ]
    turns.append(("user", random.choice(gift_variants)))

    amounts = [3000, 5000, 7000, 10000]
    turns.append(("assistant", f"Здравствуйте! Да, у нас есть подарочные сертификаты на {spell_price(amounts[0])}, {spell_price(amounts[1])}, {spell_price(amounts[2])} и {spell_price(amounts[3])}. Также можем оформить на любую сумму. Какой вариант вам подходит?"))

    chosen = random.choice(amounts)
    turns.append(("user", f"{filler()}давайте на {spell_price(chosen).replace(' рублей', '')}{hesitation()} нет, лучше на {spell_price(chosen + 2000)}"))

    final_amount = chosen + 2000
    turns.append(("assistant", f"Хорошо, оформлю сертификат на {spell_price(final_amount)}. Сертификат будет в красивой подарочной упаковке. Его можно использовать на любые услуги салона в течение шести месяцев. Когда вам удобно забрать?"))

    turns.append(("user", f"а можно сегодня?{noise()}"))
    turns.append(("assistant", "Конечно! Можете подъехать в любое удобное время, мы работаем до девяти вечера. Подскажите ваше имя, чтобы я подготовила сертификат."))
    turns.append(("user", name))
    turns.append(("assistant", f"Отлично, {name}! Сертификат на {spell_price(final_amount)} будет готов. Ждём вас сегодня!"))
    turns.append(("user", "спасибо, до свидания!"))
    turns.append(("assistant", f"Пожалуйста, {name}! Замечательный подарок получится. До встречи!"))

    return make_dialog(turns)


def gen_confused_client():
    """Client who doesn't know what they want."""
    name = random.choice(CLIENT_NAMES_F)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    confused_variants = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}слушайте, мне нужно что-то с волосами сделать{hesitation()} но я не знаю что",
        f"Добрый день! {filler()}я хочу обновить образ, но не знаю, с чего начать{noise()}",
        f"Здрасте! У меня{hesitation()} ну, волосы в ужасном состоянии{hesitation()} что посоветуете?",
        f"Алло, здравствуйте! {filler()}мне подруга посоветовала к вам обратиться{hesitation()} хочу что-то поменять в внешности",
    ]
    turns.append(("user", random.choice(confused_variants)))

    turns.append(("assistant", "Здравствуйте! Это замечательно, что вы решили обновить образ! Подскажите, что именно вас беспокоит — хотите изменить причёску, цвет волос, или, может быть, интересует уход за лицом?"))

    confused_reply = [
        f"{filler()}ну, волосы тусклые какие-то{hesitation()} и секутся",
        f"хочу что-то{hesitation()} ну, модное, как у блогеров",
        f"я давно не была в салоне{hesitation()} наверное, и стрижку, и покраситься не мешало бы",
        f"даже не знаю{hesitation()} {filler()}может, посоветуете что-нибудь?",
    ]
    turns.append(("user", random.choice(confused_reply)))

    master = random.choice(MASTERS["hair"])
    turns.append(("assistant", f"Понимаю! Для начала я бы рекомендовала вам записаться на консультацию к мастеру {master} — она оценит состояние волос и подберёт оптимальный уход. Если нужно, можно сразу сделать стрижку и тонирование. Консультация у нас бесплатная! Хотите записаться?"))

    turns.append(("user", f"о, {filler()}бесплатная консультация — это здорово! Да, давайте"))

    day_acc, _ = random_day()
    time = random_time()
    turns.append(("assistant", f"Отлично! {master} может принять вас в {day_acc} в {time}. Подходит?"))
    turns.append(("user", f"да, подходит"))
    turns.append(("assistant", "Как вас зовут?"))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, записала вас на консультацию к мастеру {master} в {day_acc} в {time}. Мастер всё подробно расскажет и подберёт идеальный вариант для вас. Ждём!"))
    turns.append(("user", "спасибо большое, до свидания!"))
    turns.append(("assistant", f"До свидания, {name}! Будем рады помочь!"))

    return make_dialog(turns)


def gen_mother_booking():
    """Mother booking for daughter."""
    mother_name = random.choice(["Елена", "Наталья", "Ольга", "Татьяна", "Светлана", "Ирина"])
    child_name = random.choice(["Маша", "Даша", "Соня", "Алиса", "Катя", "Лиза", "Аня"])
    child_age = random.randint(5, 15)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    if child_age < 10:
        turns.append(("user", f"Здравствуйте! {filler()}хочу записать дочку на стрижку. Ей {child_age} лет{hesitation()} вы стрижёте маленьких?"))
        turns.append(("assistant", f"Здравствуйте! Конечно, мы работаем с детками! Детская стрижка у нас стоит {get_price('Стрижка детская')[1]}, занимает примерно {get_duration('Стрижка детская')}. Наши мастера умеют находить подход к маленьким клиентам. Когда хотите прийти?"))
    else:
        service = random.choice(["стрижку", "маникюр", "стрижку и укладку"])
        turns.append(("user", f"Добрый день! {filler()}хочу дочку записать на {service}, ей {child_age} лет"))
        if "маникюр" in service:
            p_str = get_price("Маникюр классический")[1]
            turns.append(("assistant", f"Добрый день! Для девочки {child_age} лет подойдёт классический маникюр — {p_str}. Это займёт около часа. Когда удобно?"))
        else:
            p_str = get_price("Стрижка детская")[1] if child_age < 13 else get_price("Стрижка женская")[1]
            turns.append(("assistant", f"Добрый день! Конечно! Стрижка будет стоить {p_str}. Когда хотите записаться?"))

    day_acc, _ = random_day()
    time = random_time()
    master = random.choice(MASTERS["hair"])
    turns.append(("user", f"в {day_acc} можно?"))
    turns.append(("assistant", f"В {day_acc} мастер {master} свободна в {time}. Подходит?"))
    turns.append(("user", "да, запишите"))
    turns.append(("assistant", f"Как зовут дочку?"))
    turns.append(("user", child_name))
    turns.append(("assistant", f"Записала {child_name} в {day_acc} в {time} к мастеру {master}. Ждём вас!"))
    turns.append(("user", f"спасибо!"))
    turns.append(("assistant", f"Пожалуйста! До встречи!"))

    return make_dialog(turns)


def gen_bride_booking():
    """Bride preparing for wedding."""
    name = random.choice(CLIENT_NAMES_F)
    wedding_day = random.choice(["двадцатого июня", "пятого июля", "десятого августа", "пятнадцатого сентября", "третьего октября"])

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    bride_intros = [
        f"Здравствуйте! {filler()}у меня свадьба {wedding_day}, хочу записаться на причёску и макияж",
        f"Добрый день! Я невеста{hesitation()} свадьба {wedding_day}. Нужна свадебная причёска",
        f"Алло, здравствуйте! {filler()}мне нужен полный образ на свадьбу — причёска, макияж, маникюр{hesitation()} {wedding_day} свадьба",
    ]
    turns.append(("user", random.choice(bride_intros)))

    hair_master = random.choice(MASTERS["hair"])
    nail_master = random.choice(MASTERS["nails"])
    p_hair_num, p_hair_str = get_price("Свадебная причёска")
    p_nail_num, p_nail_str = get_price("Маникюр с гель-лаком")

    turns.append(("assistant", f"Здравствуйте! Поздравляю вас с предстоящей свадьбой! Мы с удовольствием поможем создать идеальный образ. Свадебная причёска — {p_hair_str}, делает мастер {hair_master}. Также рекомендую маникюр с гель-лаком — {p_nail_str}, мастер {nail_master}. Хотите записаться на пробную причёску заранее?"))

    turns.append(("user", f"да, {filler()}а на пробную сколько стоит?"))
    p_trial = random.choice([2000, 2500, 3000])
    turns.append(("assistant", f"Пробная причёска стоит {spell_price(p_trial)}. Рекомендую сделать её за две-три недели до свадьбы, чтобы мы могли подобрать идеальный вариант. Когда вам удобно?"))

    day_acc, _ = random_day()
    time = random_time()
    turns.append(("user", f"давайте в {day_acc}"))
    turns.append(("assistant", f"В {day_acc} у {hair_master} свободно в {time}. Устроит?"))
    turns.append(("user", "да, отлично"))

    total = p_hair_num + p_nail_num + p_trial
    turns.append(("assistant", f"Прекрасно! Записываю вас. Пробная причёска в {day_acc} в {time}, и основной день — свадебная причёска и маникюр. Подскажите ваше имя."))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, всё записала! Пробная причёска — {day_acc}, {time}, мастер {hair_master}. На день свадьбы {wedding_day} забронирую для вас и {hair_master}, и {nail_master}. Вы будете самой красивой невестой! Ждём вас!"))
    turns.append(("user", "ой, спасибо большое!"))
    turns.append(("assistant", f"Пожалуйста, {name}! Если будут вопросы — звоните в любое время. Счастливой свадьбы!"))

    return make_dialog(turns)


def gen_man_grooming():
    """Man asking about grooming services."""
    name = random.choice(CLIENT_NAMES_M)
    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    man_intros = [
        f"Здрасте. {filler()}а у вас мужчин стригут?",
        f"Добрый день. {filler()}хочу записаться на мужскую стрижку",
        f"Алло, здравствуйте. Мне бы{hesitation()} подстричься",
        f"Здравствуйте! А вы работаете с мужчинами? {filler()}хочу стрижку",
        f"Добрый день! Нужна мужская стрижка и{hesitation()} может, бороду подровнять",
    ]
    turns.append(("user", random.choice(man_intros)))

    master = random.choice(MASTERS["men"])
    p_num, p_str = get_price("Стрижка мужская")

    turns.append(("assistant", f"Здравствуйте! Конечно, у нас есть мастер {master}, он специализируется на мужских стрижках. Стрижка стоит {p_str}, занимает {get_duration('Стрижка мужская')}. Когда вам удобно?"))

    day_acc, _ = random_day()
    time = random_time()
    turns.append(("user", f"{filler()}а завтра можно? или в {day_acc}"))
    turns.append(("assistant", f"В {day_acc} у {master} есть свободное время в {time}. Подходит?"))
    turns.append(("user", f"да, пойдёт"))
    turns.append(("assistant", "Отлично! Как вас зовут?"))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, записал вас на мужскую стрижку к мастеру {master} в {day_acc} в {time}. Ждём!"))
    turns.append(("user", "спасибо"))
    turns.append(("assistant", f"Пожалуйста, {name}! До встречи!"))

    return make_dialog(turns)


def gen_price_objection():
    """Client objects to price."""
    service_key = random.choice(["Балаяж", "Кератиновое выпрямление", "Ботокс для волос", "Наращивание ресниц", "Свадебная причёска"])
    name = random.choice(CLIENT_NAMES_F)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, _ = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
    turns.append(("user", f"{random.choice(GREETINGS_CLIENT)}! Сколько стоит {service_key.lower()} у вас?"))
    turns.append(("assistant", f"Добрый день! {service_key} у нас стоит {p_str}. Процедуру выполняет мастер {master}, используются профессиональные материалы. Длительность — {get_duration(service_key)}."))

    objections = [
        f"ой{hesitation()} {filler()}это дороговато как-то",
        f"ааа{hesitation()} а подешевле нет?",
        f"хм, дорого{hesitation()} а скидки есть какие-нибудь?",
        f"ого{hesitation()} {filler()}а в другом салоне дешевле",
        f"это что так дорого-то?{noise()}",
    ]
    turns.append(("user", random.choice(objections)))

    handle_variants = [
        f"Понимаю ваше беспокойство! Дело в том, что мы работаем на профессиональной косметике премиум-класса, и результат держится значительно дольше. Кроме того, у нас сейчас действует акция — при первом посещении скидка десять процентов. Итого получится {spell_price(int(p_num * 0.9))}.",
        f"Я вас понимаю! Стоимость обусловлена качеством материалов и опытом мастера. У {master} огромный опыт, и клиенты всегда остаются довольны результатом. Могу предложить рассрочку на два платежа, если вам так удобнее.",
        f"Конечно, это инвестиция в себя! Но поверьте, результат того стоит — эффект сохраняется несколько месяцев. Также у нас есть программа лояльности: после третьего посещения — скидка пятнадцать процентов на все услуги.",
    ]
    turns.append(("assistant", random.choice(handle_variants)))

    if random.random() < 0.7:
        turns.append(("user", f"{filler()}ладно, уговорили. Запишите меня"))
        turns.append(("assistant", f"Отлично! {master} может принять вас в {day_acc} в {time}. Устроит?"))
        turns.append(("user", "да, давайте"))
        turns.append(("assistant", "Как вас зовут?"))
        turns.append(("user", name))
        turns.append(("assistant", f"{name}, записала вас на {service_key.lower()} к мастеру {master} в {day_acc} в {time}. Уверена, вам понравится! Ждём!"))
    else:
        turns.append(("user", "нет, всё равно дорого, я подумаю"))
        turns.append(("assistant", f"Конечно, подумайте! Мы всегда на связи. Если будут вопросы или решите записаться — звоните. Хорошего дня!"))

    return make_dialog(turns)


def gen_upsell():
    """Dialog where admin naturally upsells."""
    base_services = {
        "Стрижка женская": ["Укладка", "Тонирование", "Ботокс для волос"],
        "Маникюр классический": ["Педикюр", "Маникюр с гель-лаком"],
        "Маникюр с гель-лаком": ["Педикюр"],
        "Окрашивание в один тон": ["Укладка", "Ботокс для волос"],
        "Коррекция бровей": ["Окрашивание бровей", "Ламинирование бровей"],
        "Наращивание ресниц": ["Коррекция бровей", "Окрашивание бровей"],
        "Чистка лица": ["Пилинг", "Уходовая процедура для лица"],
    }
    base_key = random.choice(list(base_services.keys()))
    upsell_key = random.choice(base_services[base_key])
    name = random.choice(CLIENT_NAMES_F)
    master = get_master(base_key)
    p1_num, p1_str = get_price(base_key)
    p2_num, p2_str = get_price(upsell_key)
    day_acc, _ = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
    turns.append(("user", f"{random.choice(GREETINGS_CLIENT)}! {filler()}запишите меня на {base_key.lower()}, пожалуйста"))
    turns.append(("assistant", f"Добрый день! С удовольствием! {base_key} — {p1_str}. Кстати, многие наши клиентки также делают {upsell_key.lower()} — это отличное дополнение, всего {p2_str}. Хотите добавить?"))

    if random.random() < 0.6:
        turns.append(("user", f"{filler()}а почему бы и нет, давайте оба"))
        total = p1_num + p2_num
        turns.append(("assistant", f"Отлично! Итого: {base_key.lower()} и {upsell_key.lower()} — {spell_price(total)}. Мастер {master}, {day_acc} в {time}. Подходит?"))
    else:
        turns.append(("user", f"нет, спасибо, {filler()}только {base_key.lower()}"))
        turns.append(("assistant", f"Конечно! {base_key} у мастера {master}. В {day_acc} в {time} устроит?"))

    turns.append(("user", "да"))
    turns.append(("assistant", "Как вас зовут?"))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, всё записала! Ждём вас в {day_acc} в {time}. До встречи!"))

    return make_dialog(turns)


def gen_elderly_client():
    """Elderly client dialog - slower pace, more patient."""
    name = random.choice(["Галина Петровна", "Нина Ивановна", "Тамара Сергеевна", "Зинаида Михайловна", "Людмила Фёдоровна", "Валентина Николаевна"])
    service = random.choice(["Стрижка женская", "Укладка", "Окрашивание в один тон"])
    master = get_master(service)
    p_num, p_str = get_price(service)
    day_acc, _ = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
    turns.append(("user", f"Алло? Здравствуйте!{hesitation()} это салон красоты?"))
    turns.append(("assistant", "Да, здравствуйте! Салон красоты «Гармония». Чем могу помочь?"))
    turns.append(("user", f"Ой, хорошо{hesitation()} {filler()}мне бы подстричься. А то давно не была{hesitation()} А сколько это стоит у вас?"))
    turns.append(("assistant", f"Женская стрижка у нас стоит {p_str}. Наш мастер {master} с удовольствием вас примет. Когда вам удобно прийти?"))
    turns.append(("user", f"А{hesitation()} в {day_acc} можно? Только мне утром удобнее{hesitation()} я потом устаю"))
    turns.append(("assistant", f"Конечно! В {day_acc} утром {master} может вас принять в {random.choice(['десять утра', 'одиннадцать'])}. Подойдёт?"))
    turns.append(("user", f"да, в десять утра{hesitation()} Хорошо. А как вас найти-то? Мне дочка дала ваш номер"))
    turns.append(("assistant", "Мы находимся по адресу: улица Ленина, дом пятнадцать. Это рядом с аптекой, на первом этаже. Вход со двора. Подскажите, как вас зовут?"))
    turns.append(("user", f"{name}"))
    turns.append(("assistant", f"{name}, записала вас на стрижку в {day_acc} в десять утра. Будем вас ждать! Если понадобится помощь найти нас — звоните, мы подскажем."))
    turns.append(("user", "Спасибо, деточка! До свидания!"))
    turns.append(("assistant", f"До свидания, {name}! Будем рады вас видеть!"))

    return make_dialog(turns)


def gen_cosmetology_booking():
    """Cosmetology service booking with consultation."""
    name = random.choice(CLIENT_NAMES_F)
    services = ["Чистка лица", "Пилинг", "Уходовая процедура для лица"]
    service_key = random.choice(services)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, _ = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    cosmo_intros = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хотела бы к косметологу записаться{hesitation()} у меня проблемы с кожей",
        f"Добрый день! Мне посоветовали сделать {service_key.lower()}{hesitation()} можно записаться?",
        f"Здравствуйте! {filler()}хочу на чистку лица или пилинг{hesitation()} не знаю, что мне больше подходит",
    ]
    turns.append(("user", random.choice(cosmo_intros)))

    turns.append(("assistant", f"Здравствуйте! Наш косметолог {master} проведёт осмотр и подберёт оптимальную процедуру. {service_key} стоит {p_str}, длительность — {get_duration(service_key)}. Хотите записаться на консультацию?"))

    turns.append(("user", f"да{hesitation()} а консультация платная?"))
    turns.append(("assistant", "Консультация бесплатная, если вы сразу записываетесь на процедуру. Отдельно консультация стоит пятьсот рублей. Когда вам удобно?"))
    turns.append(("user", f"давайте в {day_acc}"))
    turns.append(("assistant", f"В {day_acc} {master} свободна в {time}. Записать вас?"))
    turns.append(("user", "да, пожалуйста"))
    turns.append(("assistant", "Как вас зовут?"))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, записала вас к косметологу {master} в {day_acc} в {time}. Рекомендую прийти без макияжа, чтобы мастер могла лучше оценить состояние кожи. Ждём вас!"))
    turns.append(("user", "хорошо, спасибо!"))
    turns.append(("assistant", f"Пожалуйста, {name}! До встречи!"))

    return make_dialog(turns)


def gen_keratin_botox():
    """Keratin or botox for hair with detailed consultation."""
    service_key = random.choice(["Кератиновое выпрямление", "Ботокс для волос"])
    name = random.choice(CLIENT_NAMES_F)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, _ = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    intros = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу сделать {service_key.lower()}{hesitation()} расскажите подробнее",
        f"Добрый день! Думаю о {service_key.lower()}{hesitation()} это правда помогает?",
        f"Здрасте! {filler()}волосы пушатся, посоветовали {service_key.lower()}{hesitation()} сколько стоит и как долго эффект держится?",
    ]
    turns.append(("user", random.choice(intros)))

    if service_key == "Кератиновое выпрямление":
        turns.append(("assistant", f"Добрый день! Кератиновое выпрямление — отличная процедура для гладких, блестящих волос. Эффект держится от трёх до шести месяцев. Стоимость — {p_str}, длительность — {get_duration(service_key)}. Мастер {master} работает на профессиональных составах. Хотите записаться?"))
    else:
        turns.append(("assistant", f"Добрый день! Ботокс для волос восстанавливает структуру, убирает пушистость и придаёт блеск. Эффект до четырёх месяцев. Стоимость — {p_str}, процедура занимает {get_duration(service_key)}. Мастер {master} — специалист по восстановительным процедурам. Записать вас?"))

    turns.append(("user", f"а{hesitation()} {filler()}это не вредно для волос?"))
    turns.append(("assistant", f"Нет, наоборот! Мы используем безформальдегидные составы, которые не только выпрямляют, но и лечат волосы. Многие клиентки отмечают, что волосы становятся значительно здоровее после процедуры."))
    turns.append(("user", f"ладно{hesitation()} давайте запишусь"))
    turns.append(("assistant", f"С удовольствием! В {day_acc} в {time} у {master} — подходит?"))
    turns.append(("user", "да"))
    turns.append(("assistant", "Подскажите ваше имя, пожалуйста."))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, записала вас на {service_key.lower()} к мастеру {master} в {day_acc} в {time}. Важно: приходите с чистыми волосами без укладочных средств. Ждём вас!"))
    turns.append(("user", "поняла, спасибо!"))
    turns.append(("assistant", f"Пожалуйста! До встречи, {name}!"))

    return make_dialog(turns)


def gen_brow_lash_booking():
    """Brow or lash service booking."""
    is_brow = random.random() < 0.5
    if is_brow:
        service_key = random.choice(["Коррекция бровей", "Окрашивание бровей", "Ламинирование бровей"])
        upsell_key = random.choice(["Окрашивание бровей", "Ламинирование бровей"])
        while upsell_key == service_key:
            upsell_key = random.choice(["Окрашивание бровей", "Ламинирование бровей"])
    else:
        service_key = random.choice(["Наращивание ресниц", "Ламинирование ресниц"])
        upsell_key = "Коррекция бровей"

    name = random.choice(CLIENT_NAMES_F)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    pu_num, pu_str = get_price(upsell_key)
    day_acc, _ = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
    turns.append(("user", f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу на {service_key.lower()}{noise()}"))
    turns.append(("assistant", f"Здравствуйте! {service_key} стоит {p_str}, займёт {get_duration(service_key)}. Мастер {master}. Кстати, многие клиентки также делают {upsell_key.lower()} — всего {pu_str}. Хотите добавить?"))

    if random.random() < 0.5:
        turns.append(("user", f"да, давайте и то, и другое"))
        total = p_num + pu_num
        turns.append(("assistant", f"Отлично! {service_key} и {upsell_key.lower()} — итого {spell_price(total)}. Когда вам удобно?"))
    else:
        turns.append(("user", f"нет{hesitation()} только {service_key.lower()}"))
        turns.append(("assistant", f"Конечно! Когда вам удобно прийти?"))

    turns.append(("user", f"в {day_acc} можно?"))
    turns.append(("assistant", f"В {day_acc} {master} свободна в {time}. Подходит?"))
    turns.append(("user", "да"))
    turns.append(("assistant", "Подскажите ваше имя."))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, записала! Ждём вас в {day_acc} в {time}. До встречи!"))

    return make_dialog(turns)


def gen_massage_booking():
    """Massage booking."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    is_male = name in CLIENT_NAMES_M
    master = random.choice(MASTERS["massage"])
    p_num, p_str = get_price("Массаж")
    day_acc, _ = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    intros = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}у вас есть массаж?",
        f"Добрый день! Хочу записаться на массаж{hesitation()} спина болит",
        f"Здравствуйте! А можно на расслабляющий массаж записаться?",
    ]
    turns.append(("user", random.choice(intros)))

    massage_types = ["расслабляющий", "классический", "спортивный", "антицеллюлитный"]
    mt = random.choice(massage_types)
    turns.append(("assistant", f"Здравствуйте! Конечно! У нас есть {', '.join(massage_types)} массаж. Стоимость — {p_str} за сеанс, длительность — {get_duration('Массаж')}. Массажист {master}. Какой вид массажа вас интересует?"))

    turns.append(("user", f"{filler()}{mt} давайте"))
    turns.append(("assistant", f"Отлично! {mt.capitalize()} массаж у мастера {master}. В {day_acc} в {time} — подходит?"))
    turns.append(("user", "да, записывайте"))
    turns.append(("assistant", "Ваше имя, пожалуйста?"))
    turns.append(("user", name))
    turns.append(("assistant", f"{name}, записал{'а' if not is_male else ''} вас на {mt} массаж к мастеру {master} в {day_acc} в {time}. Ждём!"))
    turns.append(("user", "спасибо"))
    turns.append(("assistant", "Пожалуйста! До встречи!"))

    return make_dialog(turns)


def gen_specific_variant(variant_num):
    """Generate specific dialog variants for more diversity."""
    if variant_num == 0:
        # Client calls to ask about working hours
        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"Здравствуйте! А вы до скольки работаете?{noise()}"))
        turns.append(("assistant", "Здравствуйте! Мы работаем ежедневно с десяти утра до девяти вечера, без выходных. Хотите записаться на какую-нибудь услугу?"))
        name = random.choice(CLIENT_NAMES_F)
        service = random.choice(list(SERVICES.keys()))
        master = get_master(service)
        p_num, p_str = get_price(service)
        turns.append(("user", f"да, {filler()}хотела бы на {service.lower()}"))
        day_acc, _ = random_day()
        time = random_time()
        turns.append(("assistant", f"Отлично! {service} — {p_str}. Мастер {master} может принять вас в {day_acc} в {time}. Устроит?"))
        turns.append(("user", "да, подходит"))
        turns.append(("assistant", "Как вас зовут?"))
        turns.append(("user", name))
        turns.append(("assistant", f"{name}, записала! Ждём в {day_acc} в {time}. До встречи!"))
        return make_dialog(turns)

    elif variant_num == 1:
        # Client asks about specific master's schedule
        cat = random.choice(list(MASTERS.keys()))
        master = random.choice(MASTERS[cat])
        name = random.choice(CLIENT_NAMES_F)
        day_acc, _ = random_day()
        time = random_time()
        service_keys = [k for k, v in SERVICES.items() if v["masters"] == cat]
        service_key = random.choice(service_keys) if service_keys else random.choice(list(SERVICES.keys()))
        p_num, p_str = get_price(service_key)

        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"Добрый день! {filler()}подскажите, когда работает мастер {master}?"))
        turns.append(("assistant", f"Добрый день! {master} работает по графику: вторник, четверг и субботу. Ближайшее свободное время — в {day_acc} в {time}. На какую услугу хотите записаться?"))
        turns.append(("user", f"на {service_key.lower()}"))
        turns.append(("assistant", f"Хорошо! {service_key} у {master} — {p_str}. Записываю вас в {day_acc} в {time}?"))
        turns.append(("user", "да, пожалуйста"))
        turns.append(("assistant", "Подскажите ваше имя."))
        turns.append(("user", name))
        turns.append(("assistant", f"{name}, вы записаны к {master} в {day_acc} в {time} на {service_key.lower()}. До встречи!"))
        return make_dialog(turns)

    elif variant_num == 2:
        # Very short quick booking
        name = random.choice(CLIENT_NAMES_F)
        service_key = random.choice(list(SERVICES.keys()))
        master = get_master(service_key)
        day_acc, _ = random_day()
        time = random_time()

        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"Добрый день, это {name}. Запишите меня к {master} на {service_key.lower()} на {day_acc}{hesitation()} утром если можно"))
        turns.append(("assistant", f"Здравствуйте, {name}! В {day_acc} у {master} свободно в {time}. Записываю?"))
        turns.append(("user", "да"))
        turns.append(("assistant", f"Готово! {name}, ждём вас в {day_acc} в {time}. Хорошего дня!"))
        return make_dialog(turns)

    elif variant_num == 3:
        # Client complains about previous service
        name = random.choice(CLIENT_NAMES_F)
        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"Здравствуйте{hesitation()} {filler()}я была у вас на прошлой неделе на окрашивании, и мне не очень понравился результат"))
        turns.append(("assistant", f"Здравствуйте! Мне очень жаль, что результат вас не устроил. Подскажите, пожалуйста, ваше имя и к какому мастеру вы ходили, чтобы я могла разобраться в ситуации."))
        master = random.choice(MASTERS["hair"])
        turns.append(("user", f"это {name}{hesitation()} была у {master}. Цвет получился не такой, как я хотела"))
        turns.append(("assistant", f"{name}, я понимаю ваше разочарование. Могу предложить вам бесплатную коррекцию цвета у {master} или у другого мастера — как вам удобнее. Когда сможете прийти?"))
        day_acc, _ = random_day()
        time = random_time()
        turns.append(("user", f"ну{hesitation()} лучше к другому мастеру. В {day_acc} можно?"))
        other_master = random.choice([m for m in MASTERS["hair"] if m != master])
        turns.append(("assistant", f"Конечно! Запишу вас к мастеру {other_master}. В {day_acc} в {time} — удобно?"))
        turns.append(("user", "да, спасибо"))
        turns.append(("assistant", f"{name}, записала вас на бесплатную коррекцию к мастеру {other_master} в {day_acc} в {time}. Приносим извинения за неудобства, мы обязательно всё исправим!"))
        return make_dialog(turns)

    elif variant_num == 4:
        # Client asks to book for a friend too
        name1 = random.choice(CLIENT_NAMES_F)
        name2 = random.choice([n for n in CLIENT_NAMES_F if n != name1])
        service_key = random.choice(list(SERVICES.keys()))
        master1 = get_master(service_key)
        master2 = random.choice([m for m in MASTERS[SERVICES[service_key]["masters"]] if m != master1]) if len(MASTERS[SERVICES[service_key]["masters"]]) > 1 else master1
        p_num, p_str = get_price(service_key)
        day_acc, _ = random_day()
        time1 = random_time()
        time2 = random_time()

        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"Здравствуйте! {filler()}хочу записаться на {service_key.lower()} и ещё подругу записать{hesitation()} можно вместе?"))
        turns.append(("assistant", f"Здравствуйте! Конечно, можно! Могу записать вас к разным мастерам на одно время. {service_key} стоит {p_str} за каждую. Подойдёт в {day_acc}?"))
        turns.append(("user", f"да, в {day_acc} нам обеим удобно"))
        turns.append(("assistant", f"Отлично! В {day_acc} могу записать вас к мастеру {master1} в {time1}, а вашу подругу к {master2} тоже в {time1}. Подскажите ваши имена."))
        turns.append(("user", f"я {name1}, подруга — {name2}"))
        turns.append(("assistant", f"Записала! {name1} к мастеру {master1}, {name2} к мастеру {master2}, обе в {day_acc} в {time1}. Ждём вас!"))
        turns.append(("user", "супер, спасибо!"))
        turns.append(("assistant", f"Пожалуйста! До встречи, {name1}!"))
        return make_dialog(turns)

    elif variant_num == 5:
        # Client asks about products for sale
        name = random.choice(CLIENT_NAMES_F)
        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"Здравствуйте! {filler()}а у вас можно купить профессиональную косметику для волос?"))
        turns.append(("assistant", "Здравствуйте! Да, у нас в салоне продаются профессиональные средства для волос: шампуни, маски, масла, термозащита. Бренды Kerastase, Olaplex, Moroccanoil. Цены от пятисот до пяти тысяч рублей. Что именно вас интересует?"))
        turns.append(("user", f"мне бы что-то от секущихся кончиков{hesitation()} и шампунь для окрашенных волос"))
        turns.append(("assistant", "Рекомендую масло для кончиков Moroccanoil — тысяча двести рублей, и шампунь Kerastase для окрашенных волос — тысяча пятьсот рублей. Можете заехать в любое время, мы работаем с десяти до девяти."))
        turns.append(("user", "отлично, заеду сегодня. А заодно можно на стрижку записаться?"))
        master = random.choice(MASTERS["hair"])
        day_acc, _ = random_day()
        time = random_time()
        p_num, p_str = get_price("Стрижка женская")
        turns.append(("assistant", f"Конечно! Стрижка — {p_str}. Мастер {master} свободна в {day_acc} в {time}. Подходит?"))
        turns.append(("user", "да, запишите"))
        turns.append(("assistant", "Как вас зовут?"))
        turns.append(("user", name))
        turns.append(("assistant", f"{name}, записала на стрижку в {day_acc} в {time}! И ждём вас сегодня за косметикой. До встречи!"))
        return make_dialog(turns)

    elif variant_num == 6:
        # Pedicure booking with details
        name = random.choice(CLIENT_NAMES_F)
        master = random.choice(MASTERS["nails"])
        p_num, p_str = get_price("Педикюр")
        day_acc, _ = random_day()
        time = random_time()

        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"{random.choice(GREETINGS_CLIENT)}! Хочу записаться на педикюр{hesitation()} {filler()}а вы аппаратный делаете?"))
        turns.append(("assistant", f"Здравствуйте! Да, у нас аппаратный педикюр, стоимость {p_str}, длительность {get_duration('Педикюр')}. Мастер {master}. С покрытием гель-лаком будет чуть дороже — плюс пятьсот рублей. Когда вам удобно?"))
        turns.append(("user", f"а с покрытием давайте. В {day_acc} можно?"))
        total = p_num + 500
        turns.append(("assistant", f"Конечно! Педикюр с покрытием — {spell_price(total)}. В {day_acc} {master} свободна в {time}. Подходит?"))
        turns.append(("user", "да"))
        turns.append(("assistant", "Ваше имя?"))
        turns.append(("user", name))
        turns.append(("assistant", f"{name}, записала вас на педикюр с покрытием к {master} в {day_acc} в {time}. Ждём!"))
        return make_dialog(turns)

    elif variant_num == 7:
        # Evening styling booking
        name = random.choice(CLIENT_NAMES_F)
        master = random.choice(MASTERS["hair"])
        p_num, p_str = get_price("Вечерняя причёска")
        day_acc, _ = random_day()
        time = random_time()

        turns = []
        turns.append(("assistant", random.choice(GREETINGS_ADMIN)))
        turns.append(("user", f"Здравствуйте! {filler()}у меня мероприятие в {day_acc}{hesitation()} нужна вечерняя причёска"))
        turns.append(("assistant", f"Здравствуйте! Вечерняя причёска стоит {p_str}, делается за {get_duration('Вечерняя причёска')}. Мастер {master} создаёт потрясающие вечерние образы. Во сколько у вас мероприятие?"))
        turns.append(("user", f"в семь вечера{hesitation()} значит, мне часа в четыре надо бы"))
        turns.append(("assistant", f"Отлично! Записываю вас к {master} в {day_acc} в четыре часа. К семи вечера вы будете полностью готовы. Подскажите ваше имя."))
        turns.append(("user", name))
        turns.append(("assistant", f"{name}, всё записала! В {day_acc} в четыре часа — вечерняя причёска у мастера {master}. Вы будете неотразимы! До встречи!"))
        return make_dialog(turns)

    else:
        # Fallback: random simple booking
        return gen_new_booking_simple()


# ============================================================
# Generate all 400 dialogs according to distribution
# ============================================================

dialogs = []

# 50% new client booking = 200 dialogs
for i in range(100):
    dialogs.append(gen_new_booking_simple())
for i in range(50):
    dialogs.append(gen_new_booking_with_master_choice())
for i in range(20):
    dialogs.append(gen_confused_client())
for i in range(10):
    dialogs.append(gen_mother_booking())
for i in range(10):
    dialogs.append(gen_bride_booking())
for i in range(10):
    dialogs.append(gen_man_grooming())

# 15% regular client rebooking = 60 dialogs
for i in range(60):
    dialogs.append(gen_regular_rebooking())

# 10% rescheduling/cancellation = 40 dialogs
for i in range(40):
    dialogs.append(gen_reschedule())

# 10% price inquiry = 40 dialogs
for i in range(40):
    dialogs.append(gen_price_inquiry())

# 10% multiple services = 40 dialogs
for i in range(20):
    dialogs.append(gen_multiple_services())
for i in range(20):
    dialogs.append(gen_upsell())

# 5% gift certificate / special occasion = 20 dialogs
for i in range(20):
    dialogs.append(gen_gift_certificate())

# Extra variety dialogs to fill specific niches
# We have 200+60+40+40+40+20 = 400, but let me also add specialized ones
# Replace some with specialized dialogs for variety
# Actually we're at exactly 400, but let me add more variety by replacing some
# Let's add more specialized ones and trim

# Additional variety
extra = []
for i in range(20):
    extra.append(gen_elderly_client())
for i in range(20):
    extra.append(gen_cosmetology_booking())
for i in range(15):
    extra.append(gen_keratin_botox())
for i in range(15):
    extra.append(gen_brow_lash_booking())
for i in range(10):
    extra.append(gen_massage_booking())
for i in range(10):
    extra.append(gen_price_objection())
for i in range(8):
    for v in range(8):
        extra.append(gen_specific_variant(v))

# Combine and take exactly 400
all_dialogs = dialogs + extra
random.shuffle(all_dialogs)
all_dialogs = all_dialogs[:400]

# Write output
output_path = "/Users/mihaildurnev/Desktop/voice AI/voicebook/training/dataset/beauty_salon_dialogs.jsonl"
with open(output_path, "w", encoding="utf-8") as f:
    for d in all_dialogs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print(f"Generated {len(all_dialogs)} dialogs to {output_path}")

# Validate
with open(output_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    valid = 0
    for i, line in enumerate(lines):
        try:
            obj = json.loads(line.strip())
            assert "conversations" in obj
            assert len(obj["conversations"]) >= 3  # system + at least 1 pair
            assert obj["conversations"][0]["role"] == "system"
            valid += 1
        except Exception as e:
            print(f"ERROR line {i+1}: {e}")
    print(f"Validated: {valid}/{len(lines)} lines OK")
