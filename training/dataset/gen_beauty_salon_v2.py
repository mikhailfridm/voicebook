#!/usr/bin/env python3
"""Generate 500 SFT beauty salon dialogs (v2) in JSONL format.

Scenario distribution:
  80 - Simple single-service booking (happy path)
  60 - Booking with specific master request
  50 - Multiple services in one visit
  40 - Price inquiry -> leads to booking
  20 - Price inquiry only (no booking)
  35 - Cancellation of existing booking
  35 - Reschedule existing booking
  30 - Master recommendation request
  30 - First-time client with questions
  30 - Time unavailable -> offer alternatives
  25 - User changes mind mid-dialog
  20 - Walk-in availability check
  15 - Aggressive/impatient customer
  15 - Gift certificate / booking for someone else
  15 - Ask about preparation / aftercare
  10 - Transfer to admin
  10 - Complaint about previous visit
 ---
 500 total
"""
import json
import random
import os

random.seed(456)

SYSTEM_PROMPT = (
    "Вы — администратор салона красоты. Помогаете клиентам записаться на услуги, "
    "выбрать мастера и удобное время. Говорите вежливо, профессионально и тепло."
)

# ── Masters by specialty ──────────────────────────────────────────────
MASTERS = {
    "hair": ["Анна", "Светлана", "Марина", "Ольга", "Екатерина", "Ирина"],
    "nails": ["Юлия", "Татьяна", "Наталья", "Алёна", "Кристина"],
    "brows_lashes": ["Дарья", "Елена", "Виктория", "Мария", "Анастасия"],
    "cosmetology": ["Людмила Сергеевна", "Оксана Викторовна", "Ирина Андреевна"],
    "massage": ["Андрей", "Сергей", "Елена"],
    "men": ["Дмитрий", "Артём", "Кирилл"],
}

# ── Services ──────────────────────────────────────────────────────────
SERVICES = {
    "Стрижка женская":          {"price": (2500, 4500),  "duration": "час",                     "masters": "hair"},
    "Стрижка мужская":          {"price": (1200, 2000),  "duration": "сорок минут",             "masters": "men"},
    "Окрашивание":              {"price": (4000, 7000),  "duration": "два часа",                "masters": "hair"},
    "Балаяж":                   {"price": (7000, 12000), "duration": "три часа",                "masters": "hair"},
    "Мелирование":              {"price": (5000, 9000),  "duration": "два с половиной часа",    "masters": "hair"},
    "Маникюр классический":     {"price": (1500, 2500),  "duration": "час",                     "masters": "nails"},
    "Маникюр с гель-лаком":     {"price": (2500, 3500),  "duration": "полтора часа",            "masters": "nails"},
    "Педикюр":                  {"price": (2500, 4000),  "duration": "полтора часа",            "masters": "nails"},
    "Коррекция бровей":         {"price": (800, 1500),   "duration": "двадцать минут",          "masters": "brows_lashes"},
    "Ламинирование бровей":     {"price": (2000, 3500),  "duration": "сорок минут",             "masters": "brows_lashes"},
    "Наращивание ресниц":       {"price": (3000, 5500),  "duration": "два часа",                "masters": "brows_lashes"},
    "Чистка лица":              {"price": (3500, 6000),  "duration": "полтора часа",            "masters": "cosmetology"},
    "Пилинг":                   {"price": (3000, 5000),  "duration": "сорок минут",             "masters": "cosmetology"},
    "Массаж":                   {"price": (3000, 5000),  "duration": "час",                     "masters": "massage"},
    "Укладка":                  {"price": (1500, 3000),  "duration": "сорок минут",             "masters": "hair"},
    "Кератиновое выпрямление":  {"price": (6000, 12000), "duration": "три часа",                "masters": "hair"},
}

# Compatible multi-service combos (same or nearby category)
MULTI_COMBOS = [
    ("Маникюр классический", "Педикюр"),
    ("Маникюр с гель-лаком", "Педикюр"),
    ("Стрижка женская", "Окрашивание"),
    ("Стрижка женская", "Укладка"),
    ("Окрашивание", "Укладка"),
    ("Коррекция бровей", "Ламинирование бровей"),
    ("Коррекция бровей", "Наращивание ресниц"),
    ("Чистка лица", "Пилинг"),
    ("Стрижка женская", "Маникюр с гель-лаком"),
    ("Балаяж", "Укладка"),
    ("Мелирование", "Укладка"),
    ("Маникюр с гель-лаком", "Коррекция бровей"),
    ("Стрижка мужская", "Массаж"),
]

# Master specialization descriptions for recommendations
MASTER_SPECIALTIES = {
    "Анна": "специализируется на сложном окрашивании и работает уже восемь лет",
    "Светлана": "мастер с десятилетним стажем, отлично работает с короткими стрижками",
    "Марина": "специализируется на окрашивании и балаяже, постоянно проходит обучение",
    "Ольга": "прекрасно работает с длинными волосами, делает потрясающие укладки",
    "Екатерина": "молодой, но очень талантливый мастер, особенно хороша в креативных стрижках",
    "Ирина": "очень опытный мастер, специализируется на кератиновом выпрямлении",
    "Юлия": "мастер маникюра с авторской техникой, клиенты в восторге",
    "Татьяна": "опытный мастер, делает идеальное покрытие, которое держится до четырёх недель",
    "Наталья": "специализируется на лечебном маникюре и педикюре",
    "Алёна": "молодой мастер с отличным чувством стиля, прекрасно подбирает дизайн",
    "Кристина": "мастер педикюра высшей категории",
    "Дарья": "лучший бровист в нашем салоне, стаж пять лет",
    "Елена": "универсальный мастер, работает и с бровями, и с ресницами",
    "Виктория": "специализируется на объёмном наращивании ресниц",
    "Мария": "мастер ламинирования и архитектуры бровей",
    "Анастасия": "создаёт невероятно натуральные реснички, очень аккуратная работа",
    "Людмила Сергеевна": "врач-косметолог с медицинским образованием, пятнадцать лет опыта",
    "Оксана Викторовна": "специалист по проблемной коже и anti-age процедурам",
    "Ирина Андреевна": "прекрасно работает с чувствительной кожей",
    "Андрей": "сертифицированный массажист, спортивный и классический массаж",
    "Сергей": "специалист по расслабляющему и лимфодренажному массажу",
    "Дмитрий": "мастер мужских стрижек, работает в стиле барбершоп",
    "Артём": "отлично владеет современными техниками, фейды, андеркат",
    "Кирилл": "универсальный мужской мастер, стрижки и оформление бороды",
}

# ── Reference data ────────────────────────────────────────────────────
DAYS_ACC = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу"]
DAYS_NOM = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
TIMES = [
    "десять утра", "половину одиннадцатого", "одиннадцать",
    "половину двенадцатого", "двенадцать", "час дня", "половину второго",
    "два часа", "половину третьего", "три часа", "четыре часа",
    "пять часов", "шесть часов",
]
TIMES_SHORT = [
    "10:00", "10:30", "11:00", "11:30", "12:00",
    "13:00", "13:30", "14:00", "14:30", "15:00",
    "16:00", "17:00", "18:00",
]

CLIENT_NAMES_F = [
    "Анна", "Мария", "Елена", "Наталья", "Ольга", "Татьяна", "Ирина",
    "Светлана", "Юлия", "Екатерина", "Алина", "Дарья", "Ксения",
    "Полина", "Виктория", "Софья", "Валерия", "Карина", "Диана",
    "Кристина", "Людмила", "Галина", "Нина", "Марина", "Алёна",
    "Вера", "Надежда", "Любовь", "Зинаида", "Тамара",
]
CLIENT_NAMES_M = [
    "Алексей", "Дмитрий", "Сергей", "Андрей", "Максим",
    "Артём", "Иван", "Михаил", "Николай", "Павел",
]
RELATIVE_NAMES_F = [
    "Таня", "Маша", "Лена", "Катя", "Даша", "Света", "Оля",
    "Наташа", "Юля", "Настя", "Алина", "Полина", "Соня", "Вика",
]

PHONES = [f"+7{random.randint(900,999)}{random.randint(1000000,9999999)}" for _ in range(120)]

# ── Fillers / hesitations / noise ─────────────────────────────────────
FILLERS = [
    "ну", "эм", "так", "вот", "ааа", "короче", "слушайте", "значит",
    "это самое", "как бы", "ну вот", "в общем", "типа", "ну типа",
    "как его", "ну как бы", "это",
]

GREETINGS_CLIENT = [
    "Здравствуйте", "Добрый день", "Здрасте", "Алло, здравствуйте",
    "Привет", "Добрый вечер", "Алло", "Да, здравствуйте",
    "Алло, добрый день", "Здрасьте",
]

GREETINGS_ADMIN = [
    "Салон красоты «Гармония», здравствуйте! Чем могу помочь?",
    "Салон красоты «Гармония», добрый день! Слушаю вас.",
    "Добрый день! Салон «Гармония», чем могу быть полезна?",
    "Здравствуйте! Салон красоты «Гармония». Как я могу вам помочь?",
    "Салон «Гармония», добрый день! Рада вас слышать!",
    "Добрый день, салон «Гармония»! Подскажите, чем могу помочь?",
]

CANCEL_REASONS = [
    "планы поменялись", "заболела", "не смогу прийти",
    "уезжаю в командировку", "на работе не отпускают",
    "форс-мажор", "ребёнок заболел", "не получается по времени",
]

PREP_QUESTIONS = {
    "Окрашивание": (
        "Перед окрашиванием рекомендуем не мыть голову один-два дня, "
        "чтобы естественный жир защитил кожу головы. Также лучше прийти "
        "без укладочных средств."
    ),
    "Балаяж": (
        "Перед балаяжем желательно не мыть волосы один-два дня. "
        "Если ранее окрашивали волосы, обязательно скажите мастеру, "
        "чтобы подобрать правильный состав."
    ),
    "Мелирование": (
        "Перед мелированием лучше не мыть голову день-два. "
        "Также рекомендуем за неделю сделать питательную маску для волос."
    ),
    "Кератиновое выпрямление": (
        "Перед кератиновым выпрямлением нужно прийти с чистыми волосами "
        "без укладочных средств. После процедуры нельзя мыть голову "
        "и закалывать волосы три дня."
    ),
    "Чистка лица": (
        "Перед чисткой лица лучше прийти без макияжа. "
        "Если принимаете какие-то лекарства или есть аллергии, "
        "обязательно предупредите косметолога."
    ),
    "Пилинг": (
        "За три дня до пилинга не используйте скрабы и кислотные средства. "
        "После процедуры обязательно наносите солнцезащитный крем, "
        "даже в пасмурную погоду."
    ),
    "Наращивание ресниц": (
        "Перед наращиванием приходите без макияжа на глазах. "
        "Контактные линзы лучше снять. После процедуры "
        "не мочите ресницы сутки и не используйте жирные кремы."
    ),
    "Ламинирование бровей": (
        "Перед ламинированием бровей не нужна специальная подготовка, "
        "просто приходите с чистой кожей. После процедуры сутки "
        "не мочите брови и не наносите косметику на эту зону."
    ),
    "Массаж": (
        "Перед массажем рекомендуем не есть за полтора-два часа. "
        "Наденьте удобную одежду. Если есть проблемы со здоровьем, "
        "обязательно предупредите массажиста."
    ),
    "Маникюр классический": (
        "Перед маникюром не нужна специальная подготовка. "
        "Если хотите покрытие, лучше заранее подумать о цвете. "
        "Снимать старый лак не нужно, мастер сделает это сама."
    ),
    "Маникюр с гель-лаком": (
        "Перед маникюром не наносите крем на руки, "
        "это может повлиять на стойкость покрытия. "
        "Старый гель-лак мастер снимет на месте."
    ),
    "Педикюр": (
        "Перед педикюром не нужно распаривать ноги дома. "
        "Мастер всё сделает сама. Наденьте удобную открытую обувь, "
        "если будет покрытие."
    ),
}


# ── Helpers ───────────────────────────────────────────────────────────

def filler():
    """Optionally prepend a spoken filler."""
    if random.random() < 0.4:
        return random.choice(FILLERS) + ", "
    return ""


def add_filler(text):
    """Add filler to the beginning."""
    if random.random() < 0.5:
        f = random.choice(FILLERS)
        return f"{f}, {text[0].lower()}{text[1:]}"
    return text


def noise():
    """Random STT artefact."""
    if random.random() < 0.08:
        return " [неразборчиво] "
    if random.random() < 0.03:
        return " [шум] "
    return ""


def hesitation():
    return random.choice(["...", "… ", "— ", "", "", ""])


def spell_price(p):
    """Spell price in Russian words."""
    thousands = p // 1000
    hundreds = (p % 1000) // 100

    t_words = {
        1: "тысяча", 2: "две тысячи", 3: "три тысячи", 4: "четыре тысячи",
        5: "пять тысяч", 6: "шесть тысяч", 7: "семь тысяч", 8: "восемь тысяч",
        9: "девять тысяч", 10: "десять тысяч", 11: "одиннадцать тысяч",
        12: "двенадцать тысяч",
    }
    h_words = {
        1: "сто", 2: "двести", 3: "триста", 4: "четыреста", 5: "пятьсот",
        6: "шестьсот", 7: "семьсот", 8: "восемьсот", 9: "девятьсот",
    }

    parts = []
    if thousands:
        parts.append(t_words.get(thousands, f"{thousands} тысяч"))
    if hundreds:
        parts.append(h_words[hundreds])
    if not parts:
        return f"{p} рублей"
    return " ".join(parts) + " рублей"


def price_text(price_range):
    p = random.randrange(price_range[0], price_range[1] + 1, 500)
    return p, spell_price(p)


def get_master(service_key):
    cat = SERVICES[service_key]["masters"]
    return random.choice(MASTERS[cat])


def get_other_master(service_key, exclude):
    cat = SERVICES[service_key]["masters"]
    pool = [m for m in MASTERS[cat] if m != exclude]
    return random.choice(pool) if pool else exclude


def get_price(service_key):
    return price_text(SERVICES[service_key]["price"])


def get_duration(service_key):
    return SERVICES[service_key]["duration"]


def random_day():
    idx = random.randint(0, len(DAYS_ACC) - 1)
    return DAYS_ACC[idx], DAYS_NOM[idx]


def random_time():
    return random.choice(TIMES)


def different_time(exclude):
    t = random_time()
    attempts = 0
    while t == exclude and attempts < 20:
        t = random_time()
        attempts += 1
    return t


def phone_natural(phone):
    """Format phone number with natural spoken pauses."""
    d = phone.replace("+7", "")
    patterns = [
        f"плюс семь {d[:3]} {d[3:6]} {d[6:8]} {d[8:]}",
        f"восемь {d[:3]}{hesitation()} {d[3:6]}{hesitation()} {d[6:8]} {d[8:]}",
        f"плюс семь{hesitation()} {d[:3]} {d[3:6]} {d[6:]}",
    ]
    return random.choice(patterns)


def make_dialog(turns):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for role, content in turns:
        messages.append({"role": role, "content": content})
    return {"conversations": messages}


def vague_service(service_key):
    """Return a vague/informal way to name a service."""
    vague = {
        "Стрижка женская": ["подстричься", "стрижку", "постричь волосы", "стрижечку"],
        "Стрижка мужская": ["подстричься", "мужскую стрижку", "голову постричь"],
        "Окрашивание": ["покраситься", "окрашивание", "покрасить волосы", "цвет поменять"],
        "Балаяж": ["балаяж", "балаяж сделать"],
        "Мелирование": ["мелирование", "мелировку"],
        "Маникюр классический": ["маникюр", "маникюрчик", "что-нибудь с ногтями", "ногти привести в порядок"],
        "Маникюр с гель-лаком": ["маникюр с гелем", "гель-лак", "ногти покрыть гелем", "шеллак"],
        "Педикюр": ["педикюр", "педикюрчик", "ножки привести в порядок"],
        "Коррекция бровей": ["брови подкорректировать", "коррекцию бровей", "бровки поправить"],
        "Ламинирование бровей": ["ламинирование бровей", "брови заламинировать"],
        "Наращивание ресниц": ["ресницы нарастить", "наращивание ресниц", "реснички"],
        "Чистка лица": ["чистку лица", "почистить лицо", "чистку"],
        "Пилинг": ["пилинг", "пилинг лица"],
        "Массаж": ["массаж", "на массажик", "размяться"],
        "Укладка": ["укладку", "уложить волосы", "причёску"],
        "Кератиновое выпрямление": ["кератин", "кератиновое выпрямление", "волосы выпрямить"],
    }
    opts = vague.get(service_key, [service_key.lower()])
    return random.choice(opts)


# ======================================================================
#  SCENARIO GENERATORS
# ======================================================================

def gen_simple_booking():
    """Simple single-service booking — happy path."""
    service_key = random.choice(list(SERVICES.keys()))
    is_male = service_key == "Стрижка мужская"
    name = random.choice(CLIENT_NAMES_M if is_male else CLIENT_NAMES_F)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    duration = get_duration(service_key)
    day_acc, day_nom = random_day()
    time = random_time()
    phone = random.choice(PHONES)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    req_variants = [
        f"{filler()}хотела бы записаться на {vague_service(service_key)}",
        f"{filler()}мне бы на {vague_service(service_key)} записаться",
        f"{filler()}можно записаться на {vague_service(service_key)}?",
        f"хочу на {vague_service(service_key)}{hesitation()} записаться",
        f"запишите меня{hesitation()} на {vague_service(service_key)}, пожалуйста",
        f"{filler()}а можно к вам на {vague_service(service_key)}?",
        f"мне нужна {service_key.lower()}, можно записаться?",
    ]
    if is_male:
        req_variants = [v.replace("хотела", "хотел") for v in req_variants]
    turns.append(("user", f"{random.choice(GREETINGS_CLIENT)}! {noise()}{random.choice(req_variants)}"))

    suggest = [
        f"Конечно! На {service_key.lower()} могу предложить мастера {master}. Процедура занимает {duration}, стоимость — {p_str}. На какой день вас записать?",
        f"С удовольствием! {service_key} у нас делает мастер {master}. По времени это {duration}, стоимость {p_str}. Когда вам удобно?",
        f"Отлично! Могу записать вас к мастеру {master}. {service_key} стоит {p_str}, длительность — {duration}. Какой день вам подходит?",
    ]
    turns.append(("assistant", random.choice(suggest)))

    day_q = [
        f"{filler()}а в {day_acc} есть что-нибудь?",
        f"давайте в {day_acc}",
        f"можно на {day_acc}?",
        f"{filler()}на {day_acc} есть свободное время?",
    ]
    turns.append(("user", random.choice(day_q)))

    t2, t3 = different_time(time), different_time(time)
    slot_variants = [
        f"В {day_acc} у {master} есть окошки в {time}, в {t2} и в {t3}. Какое время удобнее?",
        f"Давайте посмотрю. В {day_acc} свободно в {time} и в {t2}. Что предпочитаете?",
        f"В {day_acc} {master} может принять вас в {time} или в {t3}. Какой вариант подходит?",
    ]
    turns.append(("assistant", random.choice(slot_variants)))

    pick = [
        f"{filler()}давайте в {time}",
        f"в {time} отлично, давайте",
        f"запишите на {time}, пожалуйста",
        f"мне удобно в {time}",
        f"на {time}{hesitation()} подойдёт",
    ]
    turns.append(("user", random.choice(pick)))

    name_q = [
        "Хорошо! Подскажите, пожалуйста, ваше имя.",
        "Отлично! Как вас зовут?",
        "Записываю! Подскажите ваше имя, пожалуйста.",
        "Замечательно! Как я могу вас записать?",
    ]
    turns.append(("assistant", random.choice(name_q)))
    turns.append(("user", f"{name}"))

    # ask phone sometimes
    if random.random() < 0.35:
        turns.append(("assistant", f"Спасибо, {name}! Подскажите, пожалуйста, номер телефона для подтверждения записи."))
        turns.append(("user", f"{filler()}{phone_natural(phone)}"))

    confirm = [
        f"Записала вас на {service_key.lower()} к мастеру {master} в {day_acc} в {time}. Стоимость — {p_str}. Всё верно?",
        f"Итак, {name}, {service_key.lower()}, мастер {master}, {day_nom}, {time}. Стоимость — {p_str}. Подтверждаете?",
        f"{name}, подтверждаю: {service_key.lower()} у мастера {master}, {day_nom} в {time}, {p_str}. Верно?",
    ]
    turns.append(("assistant", random.choice(confirm)))

    yes = ["да, всё верно", "да, спасибо", "ага, правильно", "всё так, спасибо",
           "да, записывайте", "да-да, всё ок", "угу, всё правильно"]
    turns.append(("user", random.choice(yes)))

    bye = [
        f"Отлично, {name}! Ждём вас в {day_acc} в {time}. Хорошего дня!",
        f"Замечательно! Запись подтверждена. Ждём вас, {name}! До свидания!",
        f"Готово! {name}, ждём вас в {day_acc}. Если что-то изменится — звоните. До встречи!",
        f"Записала вас на {service_key.lower()} к мастеру {master}, {day_nom} в {time}. Стоимость {p_str}. Ждём вас!",
    ]
    turns.append(("assistant", random.choice(bye)))

    return make_dialog(turns)


def gen_specific_master():
    """Booking with specific master request — master busy, offer alternatives."""
    service_key = random.choice(list(SERVICES.keys()))
    cat = SERVICES[service_key]["masters"]
    masters_pool = MASTERS[cat]
    wanted = random.choice(masters_pool)
    alt = random.choice([m for m in masters_pool if m != wanted]) if len(masters_pool) > 1 else wanted
    is_male = service_key == "Стрижка мужская"
    name = random.choice(CLIENT_NAMES_M if is_male else CLIENT_NAMES_F)
    p_num, p_str = get_price(service_key)
    day_acc, day_nom = random_day()
    alt_day_acc, alt_day_nom = random_day()
    time = random_time()
    alt_time = different_time(time)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    req = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу записаться к {wanted} на {vague_service(service_key)}",
        f"Добрый день! Мне бы к {wanted}{hesitation()} на {service_key.lower()}",
        f"Здрасте! А {wanted} работает? Хочу к ней на {vague_service(service_key)}",
        f"Алло! {filler()}запишите меня к мастеру {wanted}, пожалуйста",
    ]
    if is_male:
        req = [v.replace("к ней", "к нему") for v in req]
    turns.append(("user", random.choice(req)))

    # 50% master busy, 50% available
    if random.random() < 0.5:
        turns.append(("assistant",
            f"К сожалению, {wanted} в ближайшие дни полностью занят{'а' if wanted not in CLIENT_NAMES_M else ''}. "
            f"Ближайшее свободное время у неё в {alt_day_acc} в {alt_time}. "
            f"Или могу предложить мастера {alt} — {'она' if alt not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else 'он'} свободн{'а' if alt not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} уже в {day_acc}. Как вам удобнее?"))

        choice_variants = [
            f"{filler()}ладно, давайте к {alt} в {day_acc}",
            f"тогда подожду {wanted}{hesitation()} запишите в {alt_day_acc}",
            f"а давайте к {alt}, не хочу ждать",
            f"нет, я хочу именно к {wanted}, запишите в {alt_day_acc}",
        ]
        choice = random.choice(choice_variants)
        turns.append(("user", choice))

        if alt in choice:
            chosen, chosen_day, chosen_time = alt, day_acc, time
        else:
            chosen, chosen_day, chosen_time = wanted, alt_day_acc, alt_time

        turns.append(("assistant",
            f"Хорошо! Записываю вас к мастеру {chosen} на {service_key.lower()} в {chosen_day} в {chosen_time}. "
            f"Стоимость — {p_str}. Подскажите ваше имя."))
    else:
        turns.append(("assistant",
            f"Конечно! {wanted} свободн{'а' if wanted not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} в {day_acc}. "
            f"Есть время в {time} и в {alt_time}. {service_key} — {p_str}. Какое время удобнее?"))
        turns.append(("user", f"в {time}, пожалуйста"))
        chosen, chosen_day, chosen_time = wanted, day_acc, time
        turns.append(("assistant", "Отлично! Подскажите ваше имя."))

    turns.append(("user", name))
    turns.append(("assistant",
        f"Записала вас на {service_key.lower()} к мастеру {chosen}, {chosen_day} в {chosen_time}. "
        f"Стоимость — {p_str}. Ждём вас!"))
    turns.append(("user", random.choice(["спасибо!", "спасибо большое!", "благодарю, до свидания!"])))
    turns.append(("assistant", f"Пожалуйста, {name}! До встречи!"))

    return make_dialog(turns)


def gen_multiple_services():
    """Multiple services in one visit."""
    combo = random.choice(MULTI_COMBOS)
    s1_key, s2_key = combo
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M[:3])
    day_acc, day_nom = random_day()
    time = random_time()

    p1, p1s = get_price(s1_key)
    p2, p2s = get_price(s2_key)
    total = p1 + p2
    total_str = spell_price(total)
    m1 = get_master(s1_key)
    m2 = get_master(s2_key)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    req = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу записаться на {vague_service(s1_key)} и {vague_service(s2_key)}",
        f"Добрый день! Можно в один день сделать {vague_service(s1_key)} и {vague_service(s2_key)}?",
        f"Здравствуйте! {filler()}мне бы на несколько процедур{hesitation()} {vague_service(s1_key)} и ещё {vague_service(s2_key)}",
    ]
    turns.append(("user", random.choice(req)))

    if SERVICES[s1_key]["masters"] == SERVICES[s2_key]["masters"]:
        # same master for both
        turns.append(("assistant",
            f"Конечно, можно в один визит! {s1_key} — {p1s}, {s2_key} — {p2s}. "
            f"Мастер {m1} может сделать обе процедуры. Общая стоимость — {total_str}. Когда вам удобно?"))
    else:
        turns.append(("assistant",
            f"Отлично, обе процедуры можно сделать в один день! {s1_key} — {p1s} у мастера {m1}, "
            f"{s2_key} — {p2s} у мастера {m2}. Итого — {total_str}. На какой день вас записать?"))

    turns.append(("user", f"{filler()}а в {day_acc} можно?"))
    turns.append(("assistant", f"В {day_acc} можем начать в {time}. Подходит?"))
    turns.append(("user", f"да{hesitation()} записывайте"))
    turns.append(("assistant", "Подскажите ваше имя, пожалуйста."))
    turns.append(("user", name))

    turns.append(("assistant",
        f"Записала вас на {s1_key.lower()} и {s2_key.lower()}, {day_nom} в {time}. "
        f"Общая стоимость — {total_str}. Ждём вас, {name}!"))
    turns.append(("user", "спасибо огромное!"))
    turns.append(("assistant", f"Вам спасибо! До встречи, {name}!"))

    return make_dialog(turns)


def gen_price_inquiry_booking():
    """Price inquiry that leads to booking."""
    services_ask = random.sample(list(SERVICES.keys()), random.randint(1, 3))
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    pq = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хотела узнать, сколько стоит {vague_service(services_ask[0])}?",
        f"Здравствуйте! Подскажите цены{hesitation()} на {services_ask[0].lower()}",
        f"Алло, здравствуйте! А сколько у вас {vague_service(services_ask[0])} стоит?{noise()}",
        f"Добрый день! {filler()}интересуют цены на {services_ask[0].lower()}",
    ]
    turns.append(("user", random.choice(pq)))

    p1, p1s = get_price(services_ask[0])
    d1 = get_duration(services_ask[0])
    turns.append(("assistant",
        f"{services_ask[0]} у нас стоит {p1s}, процедура занимает {d1}. "
        f"Могу я ещё чем-то помочь?"))

    if len(services_ask) > 1:
        turns.append(("user", f"а ещё{hesitation()} сколько стоит {services_ask[1].lower()}?"))
        p2, p2s = get_price(services_ask[1])
        d2 = get_duration(services_ask[1])
        turns.append(("assistant", f"{services_ask[1]} — {p2s}, длительность {d2}. Желаете записаться?"))

    if len(services_ask) > 2:
        turns.append(("user", f"и {services_ask[2].lower()}?"))
        p3, p3s = get_price(services_ask[2])
        turns.append(("assistant", f"{services_ask[2]} — {p3s}. Записать вас на какую-нибудь из этих услуг?"))

    # leads to booking
    chosen = random.choice(services_ask)
    turns.append(("user", f"{filler()}да, запишите на {vague_service(chosen)}, пожалуйста"))
    master = get_master(chosen)
    day_acc, day_nom = random_day()
    time = random_time()
    pc, pcs = get_price(chosen)
    turns.append(("assistant", f"С удовольствием! Мастер {master} может принять вас в {day_acc} в {time}. {chosen} — {pcs}. Подходит?"))
    turns.append(("user", "да, отлично"))
    turns.append(("assistant", "Подскажите ваше имя, пожалуйста."))
    turns.append(("user", name))
    turns.append(("assistant",
        f"Записала вас на {chosen.lower()} к мастеру {master}, {day_nom} в {time}. "
        f"Стоимость — {pcs}. Ждём вас, {name}!"))

    return make_dialog(turns)


def gen_price_inquiry_only():
    """Price inquiry without booking — model gives info gracefully."""
    services_ask = random.sample(list(SERVICES.keys()), random.randint(1, 3))

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    pq = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}скажите, сколько у вас стоит {vague_service(services_ask[0])}?",
        f"Здравствуйте! Мне просто цены узнать{hesitation()} на {services_ask[0].lower()}",
        f"Алло! А можно прайс узнать? Интересует {services_ask[0].lower()}{noise()}",
    ]
    turns.append(("user", random.choice(pq)))

    p1, p1s = get_price(services_ask[0])
    turns.append(("assistant",
        f"Здравствуйте! {services_ask[0]} у нас стоит {p1s}, "
        f"длительность — {get_duration(services_ask[0])}. Что-нибудь ещё подсказать?"))

    if len(services_ask) > 1:
        turns.append(("user", f"а {services_ask[1].lower()}?"))
        p2, p2s = get_price(services_ask[1])
        turns.append(("assistant", f"{services_ask[1]} — {p2s}. Желаете записаться на что-нибудь?"))

    if len(services_ask) > 2:
        turns.append(("user", f"и ещё {services_ask[2].lower()}, пожалуйста"))
        p3, p3s = get_price(services_ask[2])
        turns.append(("assistant", f"{services_ask[2]} — {p3s}. Записать вас?"))

    no = [
        "нет, спасибо, я подумаю",
        f"{filler()}пока нет, позвоню попозже",
        "не сейчас, спасибо за информацию",
        "я подумаю и перезвоню",
        "нет, мне просто узнать надо было, спасибо",
        "ладно, спасибо, я пока просто прицениваюсь",
    ]
    turns.append(("user", random.choice(no)))
    turns.append(("assistant",
        "Конечно! Будем рады видеть вас в любое время. Звоните, если появятся вопросы. Хорошего дня!"))

    return make_dialog(turns)


def gen_cancellation():
    """Cancellation of existing booking — polite, ask reason, offer reschedule."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    service_key = random.choice(list(SERVICES.keys()))
    master = get_master(service_key)
    old_day_acc, old_day_nom = random_day()
    new_day_acc, new_day_nom = random_day()
    while new_day_acc == old_day_acc:
        new_day_acc, new_day_nom = random_day()
    new_time = random_time()
    reason = random.choice(CANCEL_REASONS)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    cancel_req = [
        f"Здравствуйте! Это {name}. {filler()}мне нужно отменить запись на {old_day_acc}",
        f"Добрый день, {name} говорит. К сожалению, не смогу прийти в {old_day_acc}{hesitation()} можно отменить?",
        f"Алло, здравствуйте. Это {name}, {filler()}у меня запись на {service_key.lower()} в {old_day_acc}, но {reason}{noise()}",
        f"Здрасте! Это {name}{hesitation()} {filler()}надо отменить запись к {master} в {old_day_acc}",
    ]
    turns.append(("user", random.choice(cancel_req)))

    turns.append(("assistant",
        f"Здравствуйте, {name}! Конечно, я отменю вашу запись на {old_day_acc}. "
        f"Может быть, перенесём на другой день?"))

    if random.random() < 0.45:
        # refuses reschedule
        decline = [
            f"{filler()}нет, пока не надо, я позвоню позже",
            "нет, спасибо, пока не знаю, когда смогу",
            f"не надо{hesitation()} я перезвоню, когда определюсь с расписанием",
        ]
        turns.append(("user", random.choice(decline)))
        turns.append(("assistant",
            f"Хорошо, {name}! Запись отменена. Будем ждать вашего звонка. Хорошего дня!"))
    else:
        # agrees to reschedule
        turns.append(("user", f"а можно перенести на {new_day_acc}?"))
        turns.append(("assistant",
            f"Конечно! В {new_day_acc} у мастера {master} свободно в {new_time}. Устроит?"))
        turns.append(("user", "да, отлично"))
        turns.append(("assistant",
            f"Перенесла вашу запись на {new_day_acc} в {new_time}. {name}, ждём вас! До свидания!"))

    return make_dialog(turns)


def gen_reschedule():
    """Reschedule existing booking — change date/time/master."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    service_key = random.choice(list(SERVICES.keys()))
    master = get_master(service_key)
    old_day_acc, old_day_nom = random_day()
    new_day_acc, new_day_nom = random_day()
    while new_day_acc == old_day_acc:
        new_day_acc, new_day_nom = random_day()
    old_time = random_time()
    new_time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    req = [
        f"Здравствуйте! Это {name}. {filler()}у меня запись на {old_day_acc}, хотела бы перенести",
        f"Добрый день, {name}. Можно мне перенести запись с {old_day_nom} на другой день?",
        f"Алло! Я {name}, записана на {service_key.lower()} в {old_day_acc}{hesitation()} но не получается прийти. Можно перенести?",
        f"Здрасте! {filler()}это {name}, у меня запись на {old_day_acc} в {old_time}{hesitation()} нужно переписать на другое время",
    ]
    turns.append(("user", random.choice(req)))

    turns.append(("assistant",
        f"Здравствуйте, {name}! Конечно, давайте перенесём. На какой день вам удобно?"))

    turns.append(("user", f"{filler()}а в {new_day_acc} есть свободное время?"))

    t2 = different_time(new_time)
    turns.append(("assistant",
        f"В {new_day_acc} у мастера {master} есть время в {new_time} и в {t2}. Что удобнее?"))
    turns.append(("user", f"давайте в {new_time}"))

    # sometimes change master too
    if random.random() < 0.25:
        other = get_other_master(service_key, master)
        turns.append(("assistant",
            f"Хорошо! А к мастеру {master} или можно к {other}?"))
        turns.append(("user", f"{filler()}к {other} давайте, без разницы"))
        final_master = other
    else:
        final_master = master

    turns.append(("assistant",
        f"Готово! Перенесла вашу запись на {new_day_acc} в {new_time} к мастеру {final_master}. {name}, ждём вас!"))
    turns.append(("user", "спасибо!"))
    turns.append(("assistant", "Пожалуйста! Хорошего дня!"))

    return make_dialog(turns)


def gen_master_recommendation():
    """User doesn't know which master to choose — admin recommends."""
    service_key = random.choice(list(SERVICES.keys()))
    cat = SERVICES[service_key]["masters"]
    pool = MASTERS[cat]
    m1, m2 = random.sample(pool, min(2, len(pool)))
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    p_num, p_str = get_price(service_key)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    req = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу на {vague_service(service_key)}{hesitation()} а кого посоветуете из мастеров?",
        f"Добрый день! Мне бы на {service_key.lower()}, но я не знаю, к кому лучше записаться{hesitation()} что посоветуете?",
        f"Здравствуйте! {filler()}хочу записаться на {vague_service(service_key)}, но я у вас первый раз{hesitation()} к кому лучше?",
    ]
    turns.append(("user", random.choice(req)))

    spec1 = MASTER_SPECIALTIES.get(m1, "отличный мастер")
    spec2 = MASTER_SPECIALTIES.get(m2, "прекрасный специалист")
    turns.append(("assistant",
        f"У нас прекрасные мастера! Могу порекомендовать {m1} — {spec1}. "
        f"Также есть {m2} — {spec2}. К кому бы вы хотели?"))

    pick = [
        f"{filler()}давайте к {m1}",
        f"к {m2}, пожалуйста",
        f"ну{hesitation()} к {m1}, наверное",
        f"а мне любого{hesitation()} кто раньше свободен?",
    ]
    choice = random.choice(pick)
    turns.append(("user", choice))

    if "любого" in choice or "раньше" in choice:
        chosen = random.choice([m1, m2])
        turns.append(("assistant",
            f"Тогда записываю вас к {chosen} — {'она' if chosen not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else 'он'} "
            f"свободн{'а' if chosen not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} уже в {day_acc} в {time}. {service_key} — {p_str}. Устроит?"))
    else:
        chosen = m1 if m1 in choice else m2
        turns.append(("assistant",
            f"Отличный выбор! {chosen} свободн{'а' if chosen not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} "
            f"в {day_acc} в {time}. {service_key} стоит {p_str}. Записать вас?"))

    turns.append(("user", "да, записывайте"))
    turns.append(("assistant", "Как вас зовут?"))
    turns.append(("user", name))
    turns.append(("assistant",
        f"{name}, записала вас на {service_key.lower()} к мастеру {chosen}, "
        f"{day_nom} в {time}. Стоимость — {p_str}. Ждём вас!"))
    turns.append(("user", "спасибо!"))
    turns.append(("assistant", f"Пожалуйста! До встречи, {name}!"))

    return make_dialog(turns)


def gen_first_time_client():
    """First-time client with questions — doesn't know what they need."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    is_male = name in CLIENT_NAMES_M

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    intros = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}я у вас первый раз{hesitation()} не знаю, что мне нужно, может подскажете?",
        f"Добрый день! Мне подруга посоветовала ваш салон{hesitation()} {filler()}хочу что-нибудь сделать, но не знаю, с чего начать",
        f"Здравствуйте! {filler()}я давно хотела к вам прийти{hesitation()} расскажите, какие у вас услуги?",
        f"Алло! {filler()}это салон Гармония? Хочу записаться, но не знаю{hesitation()} что именно мне нужно",
    ]
    if is_male:
        intros = [
            f"{random.choice(GREETINGS_CLIENT)}! {filler()}я у вас первый раз{hesitation()} мне бы подстричься, и может ещё что-нибудь",
            f"Добрый день! Жена посоветовала ваш салон{hesitation()} {filler()}хочу нормально подстричься",
        ]
    turns.append(("user", random.choice(intros)))

    if is_male:
        service_key = "Стрижка мужская"
        master = get_master(service_key)
        p_num, p_str = get_price(service_key)
        turns.append(("assistant",
            f"Здравствуйте! Рады, что выбрали нас! Для начала могу предложить мужскую стрижку — "
            f"{p_str}, это займёт {get_duration(service_key)}. "
            f"Мастер {master} отлично работает с мужскими стрижками. Хотите записаться?"))
    else:
        turns.append(("assistant",
            "Здравствуйте! Как приятно! Давайте разберёмся вместе. "
            "Расскажите, что бы вы хотели изменить или улучшить? "
            "Может, стрижка, окрашивание, уход за волосами, маникюр, уход за кожей?"))

        concern = random.choice([
            f"{filler()}ну{hesitation()} волосы секутся и тусклые какие-то{hesitation()} может, подстричь и покрасить?",
            f"хочу{hesitation()} {filler()}маникюр нормальный и может что-нибудь для лица",
            f"{filler()}мне бы ногти сделать и брови{hesitation()} давно руки не доходили",
            f"да мне бы просто подстричься и укладку{hesitation()} на мероприятие иду",
        ])
        turns.append(("user", concern))

        if "волос" in concern or "подстричь" in concern or "укладку" in concern:
            service_key = random.choice(["Стрижка женская", "Окрашивание", "Укладка"])
        elif "маникюр" in concern or "ногти" in concern:
            service_key = random.choice(["Маникюр с гель-лаком", "Маникюр классический"])
        elif "брови" in concern:
            service_key = "Коррекция бровей"
        elif "лица" in concern or "кожи" in concern:
            service_key = "Чистка лица"
        else:
            service_key = random.choice(list(SERVICES.keys()))

        master = get_master(service_key)
        p_num, p_str = get_price(service_key)
        spec = MASTER_SPECIALTIES.get(master, "прекрасный специалист")
        turns.append(("assistant",
            f"Тогда рекомендую начать с {service_key.lower()} — {p_str}, "
            f"займёт {get_duration(service_key)}. "
            f"Мастер {master} — {spec}. Хотите записаться?"))

    turns.append(("user", f"да{hesitation()} {filler()}давайте попробую"))

    day_acc, day_nom = random_day()
    time = random_time()
    turns.append(("assistant", f"Отлично! В {day_acc} в {time} подойдёт?"))
    turns.append(("user", f"да, хорошо"))
    turns.append(("assistant", "Как вас зовут?"))
    turns.append(("user", name))
    turns.append(("assistant",
        f"{name}, записала вас на {service_key.lower()} к мастеру {master}, "
        f"{day_nom} в {time}. Стоимость — {p_str}. "
        f"Будем рады видеть вас в салоне «Гармония»!"))
    turns.append(("user", "спасибо! до встречи"))
    turns.append(("assistant", f"До встречи, {name}! Уверена, вам понравится!"))

    return make_dialog(turns)


def gen_time_unavailable():
    """Specific slot taken — suggest 2-3 nearby times."""
    service_key = random.choice(list(SERVICES.keys()))
    is_male = service_key == "Стрижка мужская"
    name = random.choice(CLIENT_NAMES_M if is_male else CLIENT_NAMES_F)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, day_nom = random_day()
    wanted_time = random_time()
    alt1, alt2, alt3 = different_time(wanted_time), different_time(wanted_time), different_time(wanted_time)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    turns.append(("user",
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу записаться на {vague_service(service_key)} "
        f"в {day_acc} в {wanted_time}"))

    turns.append(("assistant",
        f"Здравствуйте! К сожалению, в {day_acc} в {wanted_time} у мастера {master} уже занято. "
        f"Но есть свободное время в {alt1}, в {alt2} и в {alt3}. Какой вариант вам подходит?"))

    pick_var = [
        f"{filler()}давайте в {alt1}",
        f"тогда в {alt2}{hesitation()} подойдёт",
        f"ладно, в {alt3}",
        f"а{hesitation()} в {alt1} давайте, ближе к моему времени",
    ]
    chosen_time = random.choice([alt1, alt2, alt3])
    turns.append(("user", f"{filler()}давайте в {chosen_time}"))

    turns.append(("assistant",
        f"Отлично! Записываю на {service_key.lower()} в {day_acc} в {chosen_time} "
        f"к мастеру {master}. Стоимость — {p_str}. Как вас зовут?"))
    turns.append(("user", name))
    turns.append(("assistant",
        f"Записала вас, {name}! {service_key}, мастер {master}, {day_nom} в {chosen_time}. "
        f"Стоимость — {p_str}. Ждём вас!"))
    turns.append(("user", "спасибо"))
    turns.append(("assistant", f"Пожалуйста! До встречи, {name}!"))

    return make_dialog(turns)


def gen_change_mind():
    """User changes mind mid-dialog — switches service or master or time."""
    s1 = random.choice(list(SERVICES.keys()))
    # pick a different service to switch to
    s2 = random.choice([k for k in SERVICES.keys() if k != s1])
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    m1 = get_master(s1)
    m2 = get_master(s2)
    p1, p1s = get_price(s1)
    p2, p2s = get_price(s2)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    turns.append(("user",
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу записаться на {vague_service(s1)}"))

    turns.append(("assistant",
        f"Здравствуйте! {s1} — {p1s}, длительность — {get_duration(s1)}. "
        f"Мастер {m1} может принять вас в {day_acc} в {time}. Записать?"))

    # user changes mind
    change_variants = [
        f"ой{hesitation()} {filler()}подождите, я передумала. Лучше {vague_service(s2)}",
        f"стоп{hesitation()} а знаете, давайте лучше {vague_service(s2)} вместо этого",
        f"{filler()}нет, я передумала{hesitation()} можно вместо {s1.lower()} на {vague_service(s2)}?",
        f"секунду{hesitation()} а давайте лучше на {vague_service(s2)}, я переменила решение",
    ]
    turns.append(("user", random.choice(change_variants)))

    turns.append(("assistant",
        f"Конечно, без проблем! {s2} — {p2s}, длительность — {get_duration(s2)}. "
        f"Мастер {m2} свободн{'а' if m2 not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} "
        f"в {day_acc} в {time}. Подходит?"))

    turns.append(("user", f"да{hesitation()} вот так, давайте"))
    turns.append(("assistant", "Подскажите, пожалуйста, ваше имя."))
    turns.append(("user", name))
    turns.append(("assistant",
        f"Записала вас на {s2.lower()} к мастеру {m2}, {day_nom} в {time}. "
        f"Стоимость — {p2s}. Ждём вас, {name}!"))
    turns.append(("user", "спасибо, извините за суматоху!"))
    turns.append(("assistant", f"Ничего страшного, {name}! Главное, что нашли подходящую услугу. До встречи!"))

    return make_dialog(turns)


def gen_walkin_check():
    """Walk-in availability check — 'можно прямо сейчас?'"""
    service_key = random.choice(list(SERVICES.keys()))
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    walkin = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}а можно прямо сейчас прийти на {vague_service(service_key)}?",
        f"Алло! Я тут рядом с вашим салоном{hesitation()} можно без записи на {vague_service(service_key)}?",
        f"Здрасте! {filler()}а у вас сейчас свободно? Хочу на {vague_service(service_key)}",
        f"Добрый день! Можно к вам прямо сейчас{hesitation()} без записи?",
    ]
    turns.append(("user", random.choice(walkin)))

    if random.random() < 0.4:
        # available now
        turns.append(("assistant",
            f"Здравствуйте! Да, вам повезло — мастер {master} сейчас свободн{'а' if master not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''}! "
            f"{service_key} — {p_str}, займёт {get_duration(service_key)}. Приходите, ждём!"))
        turns.append(("user", "ой, отлично! бегу к вам!"))
        turns.append(("assistant", "Как вас зовут? Запишу, чтобы мастер был готов."))
        turns.append(("user", name))
        turns.append(("assistant", f"Ждём вас, {name}! Мастер {master} вас примет."))
    else:
        # not available now, offer nearest slot
        turns.append(("assistant",
            f"Здравствуйте! К сожалению, сейчас все мастера заняты. "
            f"Ближайшее свободное время — через час, в {time}, у мастера {master}. "
            f"{service_key} — {p_str}. Подождёте или записать на другое время?"))

        if random.random() < 0.5:
            turns.append(("user", f"{filler()}ладно, подожду. Запишите через час"))
            turns.append(("assistant", "Подскажите ваше имя, пожалуйста."))
            turns.append(("user", name))
            turns.append(("assistant",
                f"{name}, записала вас на {service_key.lower()} к мастеру {master} на {time}. "
                f"Стоимость — {p_str}. Ждём вас!"))
        else:
            turns.append(("user", f"нет, лучше на другой день{hesitation()} а в {day_acc} есть?"))
            alt_time = random_time()
            turns.append(("assistant",
                f"В {day_acc} {master} свободн{'а' if master not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} в {alt_time}. Подходит?"))
            turns.append(("user", "да, давайте"))
            turns.append(("assistant", "Как вас зовут?"))
            turns.append(("user", name))
            turns.append(("assistant",
                f"{name}, записала вас на {service_key.lower()} к мастеру {master}, "
                f"{day_nom} в {alt_time}. Стоимость — {p_str}. До встречи!"))

    return make_dialog(turns)


def gen_aggressive_client():
    """Aggressive/impatient customer — model stays calm and professional."""
    service_key = random.choice(list(SERVICES.keys()))
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    angry_starts = [
        f"Алло! Я уже третий раз звоню! Мне никто не перезвонил! Мне нужно записаться на {vague_service(service_key)}!",
        f"Здрасте. Короче, мне срочно надо на {vague_service(service_key)}, у вас вообще можно записаться или как?",
        f"Алло! Чё так долго трубку берёте? Мне на {vague_service(service_key)} надо, и побыстрее!",
        f"Добрый день! Вот скажите, почему у вас вечно всё занято? Мне нужно на {service_key.lower()}, но в прошлый раз мест не было!",
    ]
    turns.append(("user", random.choice(angry_starts)))

    turns.append(("assistant",
        f"Здравствуйте! Приношу извинения за неудобства. Давайте я прямо сейчас подберу для вас удобное время. "
        f"{service_key} — {p_str}. Мастер {master} свободн{'а' if master not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} в {day_acc}. Когда вам удобно?"))

    impatient_2 = [
        f"в {day_acc} давайте, только побыстрее всё оформите",
        f"ну давайте в {day_acc}{hesitation()} и чтоб точно место было, а то в прошлый раз я пришла, а мастер занят",
        f"ладно, в {day_acc}. Только не подведите опять",
    ]
    turns.append(("user", random.choice(impatient_2)))

    t2 = different_time(time)
    turns.append(("assistant",
        f"Записываю! В {day_acc} есть время в {time} и в {t2}. "
        f"Какое удобнее? Я гарантирую, что мастер вас будет ждать."))

    turns.append(("user", f"в {time}. И чтоб без задержек"))

    turns.append(("assistant",
        "Обещаю, всё будет точно по времени! Подскажите, пожалуйста, ваше имя."))

    turns.append(("user", name))

    turns.append(("assistant",
        f"{name}, записала вас на {service_key.lower()} к мастеру {master}, "
        f"{day_nom} в {time}. Стоимость — {p_str}. "
        f"Мы будем ждать вас и всё пройдёт отлично!"))

    softened = [
        "ладно, спасибо. Извините, что нагрубила",
        "хорошо, спасибо",
        "ну ладно, посмотрим. До свидания",
        "окей, спасибо. Приду",
    ]
    turns.append(("user", random.choice(softened)))
    turns.append(("assistant",
        f"Ничего страшного, {name}! Мы всегда рады помочь. До встречи!"))

    return make_dialog(turns)


def gen_gift_booking():
    """Gift certificate or booking for someone else."""
    buyer = random.choice(CLIENT_NAMES_F)
    recipient_name = random.choice(RELATIVE_NAMES_F)
    relationship = random.choice(["маму", "подругу", "сестру", "дочку", "свекровь", "коллегу"])
    service_key = random.choice(list(SERVICES.keys()))
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, day_nom = random_day()
    time = random_time()

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    req = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}хочу записать {relationship} на {vague_service(service_key)}",
        f"Добрый день! Хочу подарить {relationship} {service_key.lower()}{hesitation()} можно записать?",
        f"Здравствуйте! {filler()}а можно записать не себя, а {relationship}? На {vague_service(service_key)}",
        f"Алло! У {relationship.replace('у','ы').replace('маму','мамы').replace('подругу','подруги')} день рождения{hesitation()} "
        f"хочу подарить ей поход к вам на {vague_service(service_key)}",
    ]
    turns.append(("user", random.choice(req)))

    turns.append(("assistant",
        f"Здравствуйте! Какой замечательный подарок! Конечно, можем записать. "
        f"{service_key} — {p_str}, длительность — {get_duration(service_key)}. "
        f"Подскажите имя человека, которого записываем, и удобный день."))

    turns.append(("user", f"её зовут {recipient_name}{hesitation()} {filler()}а в {day_acc} можно?"))

    turns.append(("assistant",
        f"В {day_acc} мастер {master} свободн{'а' if master not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} "
        f"в {time}. Записываю {recipient_name} на {service_key.lower()}?"))

    turns.append(("user", "да, пожалуйста!"))

    turns.append(("assistant",
        f"Записала {recipient_name} на {service_key.lower()} к мастеру {master}, "
        f"{day_nom} в {time}. Стоимость — {p_str}. "
        f"Можем также оформить подарочный сертификат с красивым оформлением. Хотите?"))

    if random.random() < 0.5:
        turns.append(("user", f"ой, да, сертификат — это здорово! А сколько он стоит?"))
        turns.append(("assistant",
            "Сам сертификат бесплатный, вы оплачиваете только стоимость услуги. "
            "Можете забрать его в салоне или мы отправим электронный вариант на почту."))
        turns.append(("user", "отлично, заберу в салоне. Спасибо!"))
        turns.append(("assistant",
            f"Замечательно! Сертификат и запись для {recipient_name} готовы. "
            f"Заходите за сертификатом в любое время. До свидания!"))
    else:
        turns.append(("user", "нет, сертификат не нужен, я ей сама скажу. Спасибо!"))
        turns.append(("assistant",
            f"Хорошо! {recipient_name} записана, ждём её в {day_acc} в {time}. "
            f"Спасибо за звонок! До свидания!"))

    return make_dialog(turns)


def gen_prep_aftercare():
    """Ask about preparation or aftercare for a procedure."""
    service_key = random.choice(list(PREP_QUESTIONS.keys()))
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    master = get_master(service_key)
    p_num, p_str = get_price(service_key)
    day_acc, day_nom = random_day()
    time = random_time()
    prep_info = PREP_QUESTIONS[service_key]

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    # Sometimes ask before booking, sometimes during/after
    if random.random() < 0.6:
        # ask before / as the reason for the call
        req = [
            f"{random.choice(GREETINGS_CLIENT)}! {filler()}я записана на {service_key.lower()}{hesitation()} "
            f"хотела узнать, нужно ли что-то делать перед процедурой?",
            f"Добрый день! Собираюсь к вам на {vague_service(service_key)}{hesitation()} "
            f"как мне подготовиться?",
            f"Здравствуйте! {filler()}а скажите, перед {service_key.lower()} "
            f"нужна какая-то подготовка?{noise()}",
        ]
        turns.append(("user", random.choice(req)))
        turns.append(("assistant", prep_info + " Могу я ещё чем-то помочь?"))

        if random.random() < 0.6:
            turns.append(("user", f"да, хотела бы ещё записаться{hesitation()} на {day_acc} можно?"))
            turns.append(("assistant",
                f"Конечно! В {day_acc} мастер {master} свободн{'а' if master not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} "
                f"в {time}. {service_key} — {p_str}. Подходит?"))
            turns.append(("user", "да"))
            turns.append(("assistant", "Как вас зовут?"))
            turns.append(("user", name))
            turns.append(("assistant",
                f"Записала вас, {name}! {service_key}, мастер {master}, {day_nom} в {time}. "
                f"Стоимость — {p_str}. Ждём вас!"))
        else:
            turns.append(("user", "нет, спасибо, это всё"))
            turns.append(("assistant", "Пожалуйста! Если будут ещё вопросы — звоните. Хорошего дня!"))
    else:
        # ask during booking process
        turns.append(("user",
            f"{random.choice(GREETINGS_CLIENT)}! Запишите меня на {vague_service(service_key)}, пожалуйста"))
        turns.append(("assistant",
            f"Здравствуйте! {service_key} — {p_str}, длительность — {get_duration(service_key)}. "
            f"Мастер {master}. Когда вам удобно?"))
        turns.append(("user", f"в {day_acc}{hesitation()} а кстати, мне что-то нужно делать перед процедурой?"))
        turns.append(("assistant",
            f"Хороший вопрос! {prep_info} "
            f"В {day_acc} {master} свободн{'а' if master not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} "
            f"в {time}. Подходит?"))
        turns.append(("user", "да, записывайте"))
        turns.append(("assistant", "Как вас зовут?"))
        turns.append(("user", name))
        turns.append(("assistant",
            f"{name}, записала вас на {service_key.lower()} к мастеру {master}, "
            f"{day_nom} в {time}. Стоимость — {p_str}. Ждём вас!"))

    return make_dialog(turns)


def gen_transfer_to_admin():
    """Complex request model can't handle — transfer to human admin."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    complex_requests = [
        f"{random.choice(GREETINGS_CLIENT)}! {filler()}я хочу обсудить аренду кресла в вашем салоне",
        f"Добрый день! Мне нужно поговорить с директором{hesitation()} по поводу сотрудничества",
        f"Здравствуйте! {filler()}у меня сложная ситуация с аллергией{hesitation()} "
        f"мне нужна консультация именно с вашим косметологом по телефону",
        f"Алло! Я хочу вернуть деньги за процедуру{hesitation()} мне сделали плохо",
        f"Здрасте! {filler()}у вас можно провести мероприятие? Девичник на десять человек{hesitation()} "
        f"с фуршетом и несколькими мастерами?",
        f"Добрый день! Хочу заключить договор на корпоративное обслуживание{hesitation()} "
        f"для сотрудников нашей компании",
    ]
    turns.append(("user", random.choice(complex_requests)))

    turns.append(("assistant",
        "Я вас понимаю! К сожалению, этот вопрос выходит за рамки моих возможностей. "
        "Давайте я соединю вас со старшим администратором, она сможет вам помочь. "
        "Подскажите ваше имя и удобный номер для связи?"))

    turns.append(("user", f"это {name}{hesitation()} {phone_natural(random.choice(PHONES))}"))

    turns.append(("assistant",
        f"Спасибо, {name}! Передам вашу информацию администратору. "
        f"Вам перезвонят в ближайшее время. Могу ещё чем-то помочь?"))

    end = [
        "нет, спасибо, жду звонка",
        f"нет, это всё{hesitation()} спасибо",
        "а когда примерно перезвонят?",
    ]
    choice = random.choice(end)
    turns.append(("user", choice))

    if "когда" in choice:
        turns.append(("assistant",
            "Обычно перезванивают в течение часа. Если не перезвонят — позвоните нам ещё раз, пожалуйста. Хорошего дня!"))
    else:
        turns.append(("assistant",
            f"Хорошо, {name}! Хорошего дня, до свидания!"))

    return make_dialog(turns)


def gen_complaint():
    """Complaint about previous visit — model empathizes, offers to connect with manager."""
    name = random.choice(CLIENT_NAMES_F + CLIENT_NAMES_M)
    service_key = random.choice(list(SERVICES.keys()))
    master = get_master(service_key)
    other_master = get_other_master(service_key, master)

    turns = []
    turns.append(("assistant", random.choice(GREETINGS_ADMIN)))

    complaints = [
        f"Здравствуйте{hesitation()} {filler()}я была у вас на прошлой неделе на {service_key.lower()}, и мне не понравился результат",
        f"Добрый день! Я {name}. У меня претензия{hesitation()} была на {service_key.lower()} у {master}, "
        f"и результат совсем не тот, что я просила",
        f"Алло! {filler()}я хочу пожаловаться. Была у {master} на {service_key.lower()}, "
        f"и мне всё испортили{hesitation()} я в шоке{noise()}",
        f"Здрасте. Короче, ходила к вам на {vague_service(service_key)}{hesitation()} "
        f"и результат ужасный. Что делать?",
    ]
    turns.append(("user", random.choice(complaints)))

    turns.append(("assistant",
        f"Мне очень жаль, что вы столкнулись с такой ситуацией! Это совершенно не тот уровень, "
        f"который мы стремимся обеспечить. Подскажите, пожалуйста, ваше имя и когда именно вы были у нас, "
        f"чтобы я могла разобраться."))

    turns.append(("user",
        f"это {name}{hesitation()} была в прошлую {random.choice(DAYS_ACC[:5])}"))

    turns.append(("assistant",
        f"{name}, я понимаю ваше разочарование и приношу искренние извинения. "
        f"Могу предложить два варианта: бесплатную коррекцию у другого мастера "
        f"или соединить вас с управляющей салона для решения вопроса. Что вам удобнее?"))

    if random.random() < 0.5:
        turns.append(("user", f"{filler()}давайте коррекцию{hesitation()} но к другому мастеру"))
        day_acc, day_nom = random_day()
        time = random_time()
        turns.append(("assistant",
            f"Конечно! Мастер {other_master} свободн{'а' if other_master not in ['Андрей','Сергей','Дмитрий','Артём','Кирилл'] else ''} "
            f"в {day_acc} в {time}. Записать вас на бесплатную коррекцию?"))
        turns.append(("user", "да"))
        turns.append(("assistant",
            f"{name}, записала вас на бесплатную коррекцию к мастеру {other_master}, "
            f"{day_nom} в {time}. Ещё раз приносим извинения. Мы обязательно всё исправим!"))
    else:
        turns.append(("user", "соедините с управляющей, пожалуйста"))
        turns.append(("assistant",
            f"Конечно, {name}! Сейчас передам информацию управляющей, и она свяжется с вами "
            f"в ближайшее время. Подскажите номер телефона для обратной связи."))
        turns.append(("user", phone_natural(random.choice(PHONES))))
        turns.append(("assistant",
            f"Записала! {name}, управляющая перезвонит вам сегодня. "
            f"Ещё раз приносим искренние извинения за доставленные неудобства."))

    turns.append(("user", random.choice(["ладно, спасибо", "хорошо, жду", "ок, до свидания"])))
    turns.append(("assistant", f"До свидания, {name}! Мы обязательно решим этот вопрос."))

    return make_dialog(turns)


# ======================================================================
#  GENERATION
# ======================================================================

dialogs = []

# 1. Simple single-service booking (80)
for _ in range(80):
    dialogs.append(gen_simple_booking())

# 2. Booking with specific master request (55)
for _ in range(55):
    dialogs.append(gen_specific_master())

# 3. Multiple services in one visit (45)
for _ in range(45):
    dialogs.append(gen_multiple_services())

# 4. Price inquiry -> leads to booking (40)
for _ in range(40):
    dialogs.append(gen_price_inquiry_booking())

# 5. Price inquiry only (20)
for _ in range(20):
    dialogs.append(gen_price_inquiry_only())

# 6. Cancellation of existing booking (35)
for _ in range(35):
    dialogs.append(gen_cancellation())

# 7. Reschedule existing booking (35)
for _ in range(35):
    dialogs.append(gen_reschedule())

# 8. Master recommendation request (25)
for _ in range(25):
    dialogs.append(gen_master_recommendation())

# 9. First-time client with questions (25)
for _ in range(25):
    dialogs.append(gen_first_time_client())

# 10. Time unavailable -> offer alternatives (25)
for _ in range(25):
    dialogs.append(gen_time_unavailable())

# 11. User changes mind mid-dialog (25)
for _ in range(25):
    dialogs.append(gen_change_mind())

# 12. Walk-in availability check (20)
for _ in range(20):
    dialogs.append(gen_walkin_check())

# 13. Aggressive/impatient customer (15)
for _ in range(15):
    dialogs.append(gen_aggressive_client())

# 14. Gift certificate / booking for someone else (15)
for _ in range(15):
    dialogs.append(gen_gift_booking())

# 15. Ask about preparation / aftercare (15)
for _ in range(15):
    dialogs.append(gen_prep_aftercare())

# 16. Transfer to admin (10)
for _ in range(10):
    dialogs.append(gen_transfer_to_admin())

# 17. Complaint about previous visit (15)
for _ in range(15):
    dialogs.append(gen_complaint())

assert len(dialogs) == 500, f"Expected 500 dialogs, got {len(dialogs)}"

random.shuffle(dialogs)

# ── Write output ──────────────────────────────────────────────────────
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "beauty_salon_dialogs_v2.jsonl")

with open(output_path, "w", encoding="utf-8") as f:
    for d in dialogs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print(f"Generated {len(dialogs)} dialogs to {output_path}")

# ── Validate ──────────────────────────────────────────────────────────
with open(output_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    valid = 0
    for i, line in enumerate(lines):
        try:
            obj = json.loads(line.strip())
            assert "conversations" in obj, "missing 'conversations'"
            assert len(obj["conversations"]) >= 3, "too few messages"
            assert obj["conversations"][0]["role"] == "system", "first must be system"
            assert obj["conversations"][1]["role"] == "assistant", "second must be assistant"
            valid += 1
        except Exception as e:
            print(f"ERROR line {i+1}: {e}")
    print(f"Validated: {valid}/{len(lines)} lines OK")
