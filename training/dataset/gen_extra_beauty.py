#!/usr/bin/env python3
"""Generate 500 extra SFT dialogs for beauty salon voice receptionist."""
import json
import random
import os

random.seed(42)

SYSTEM = "Вы — администратор салона красоты. Помогаете клиентам записаться на услуги, выбрать мастера и удобное время. Говорите вежливо, профессионально и тепло."

SALON_NAMES = ["Гармония", "Жемчужина", "Аврора", "Эстетика", "Шарм", "Бархат", "Лотос", "Орхидея", "Элегия", "Каприз"]

MASTERS_F = ["Анна", "Светлана", "Ольга", "Марина", "Екатерина", "Наталья", "Ирина", "Людмила", "Валентина", "Татьяна", "Елена", "Юлия", "Оксана", "Дарья", "Виктория", "Алёна", "Галина", "Кристина", "Полина", "Надежда"]
MASTERS_M = ["Алексей", "Дмитрий", "Сергей", "Андрей", "Михаил", "Артём", "Роман", "Владислав", "Игорь", "Павел"]
MASTERS_ALL = MASTERS_F + MASTERS_M

PATRONYMICS_F = ["Андреевна", "Сергеевна", "Викторовна", "Александровна", "Дмитриевна", "Игоревна", "Николаевна", "Олеговна"]
PATRONYMICS_M = ["Андреевич", "Сергеевич", "Викторович", "Александрович", "Дмитриевич", "Игоревич"]

CLIENT_NAMES_F = ["Алина", "Вера", "Диана", "Жанна", "Зоя", "Карина", "Лариса", "Маргарита", "Нина", "Регина", "Софья", "Тамара", "Ульяна", "Фаина", "Эльвира", "Яна", "Лилия", "Роза", "Камила", "Амина", "Снежана", "Влада", "Арина", "Милана", "Злата", "Варвара", "Аделина", "Евгения", "Ангелина", "Стефания", "Василиса", "Мирослава", "Есения", "Агата", "Таисия", "Рената", "Инга", "Альбина", "Римма", "Клара"]
CLIENT_NAMES_M = ["Антон", "Борис", "Виктор", "Геннадий", "Евгений", "Захар", "Константин", "Леонид", "Максим", "Николай", "Олег", "Руслан", "Тимур", "Филипп", "Эдуард", "Ярослав", "Кирилл", "Данил", "Артур", "Марк", "Илья", "Матвей", "Глеб", "Тимофей", "Лев"]

DAYS = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"]
DAYS_NA = ["в понедельник", "во вторник", "в среду", "в четверг", "в пятницу", "в субботу", "в воскресенье"]
DAYS_RAW = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]

TIMES_SPOKEN = [
    ("десять утра", "десять"), ("в десять тридцать", "десять тридцать"), ("в одиннадцать", "одиннадцать"),
    ("в полдвенадцатого", "одиннадцать тридцать"), ("в двенадцать", "двенадцать"), ("в час дня", "час"),
    ("в половину второго", "полвторого"), ("в два часа", "два"), ("в два тридцать", "два тридцать"),
    ("в три", "три"), ("в половину четвёртого", "полчетвёртого"), ("в четыре", "четыре"),
    ("в четыре тридцать", "четыре тридцать"), ("в пять", "пять"), ("в половину шестого", "полшестого"),
    ("в шесть вечера", "шесть"), ("в шесть тридцать", "шесть тридцать"), ("в семь вечера", "семь"),
]

GREETINGS_ADMIN = [
    "Салон красоты «{s}», здравствуйте! Чем могу помочь?",
    "Добрый день, салон «{s}»! Слушаю вас.",
    "Салон «{s}», добрый день! Подскажите, чем могу помочь?",
    "Здравствуйте, салон красоты «{s}»! Рада вас слышать.",
    "Салон «{s}», здравствуйте! Как я могу вам помочь?",
    "Добрый день! Салон красоты «{s}» на связи.",
    "Салон «{s}», добрый вечер! Слушаю вас внимательно.",
]

GREETINGS_CLIENT = [
    "Здравствуйте!", "Добрый день!", "Алло, здрасте!", "Да, здравствуйте!",
    "Добрый день, это салон?", "Алё, это салон красоты?", "Здрасьте!",
    "Добрый день! Вы работаете?", "Привет!", "Ой, здравствуйте!",
    "Алло! Добрый день!", "Ну здравствуйте!", "Здрасте, это салон?",
]

FILLERS = ["ну", "эм", "так", "вот", "ааа", "короче", "слушайте", "типа", "как бы", "ой", "ну как бы", "в общем", "это самое", "ну вот", "значит"]

def filler():
    return random.choice(FILLERS) if random.random() < 0.4 else ""

def add_filler(text):
    f = filler()
    if f:
        if random.random() < 0.5:
            return f"{f}, {text}"
        else:
            return f"{text}... {f}"
    return text

def pick_master(gender=None):
    if gender == "f":
        name = random.choice(MASTERS_F)
        patr = random.choice(PATRONYMICS_F)
    elif gender == "m":
        name = random.choice(MASTERS_M)
        patr = random.choice(PATRONYMICS_M)
    else:
        if random.random() < 0.7:
            name = random.choice(MASTERS_F)
            patr = random.choice(PATRONYMICS_F)
        else:
            name = random.choice(MASTERS_M)
            patr = random.choice(PATRONYMICS_M)
    if random.random() < 0.4:
        return f"{name} {patr}"
    return name

def pick_client(gender=None):
    if gender == "m":
        return random.choice(CLIENT_NAMES_M)
    return random.choice(CLIENT_NAMES_F)

def pick_time():
    return random.choice(TIMES_SPOKEN)

def pick_day():
    return random.choice(DAYS_NA)

def pick_day_raw():
    return random.choice(DAYS_RAW)

def price_str(val):
    """Convert number to spoken Russian price."""
    thousands = val // 1000
    hundreds = val % 1000
    parts = []
    if thousands == 1:
        parts.append("тысяча")
    elif thousands in (2, 3, 4):
        w = {2: "две", 3: "три", 4: "четыре"}
        parts.append(f"{w[thousands]} тысячи")
    elif thousands >= 5:
        w = {5: "пять", 6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять"}
        parts.append(f"{w.get(thousands, str(thousands))} тысяч")
    if hundreds == 500:
        parts.append("пятьсот")
    elif hundreds > 0:
        parts.append(str(hundreds))
    return " ".join(parts) + " рублей"

def make_dialog(conv_turns):
    return {"conversations": [{"role": "system", "content": SYSTEM}] + conv_turns}

salon = lambda: random.choice(SALON_NAMES)
greeting_a = lambda s: random.choice(GREETINGS_ADMIN).format(s=s)
greeting_c = lambda: random.choice(GREETINGS_CLIENT)

dialogs = []

# ============================================================
# SCENARIO 1: Client forgot what service they had last time (0-34 = 35 dialogs)
# ============================================================
for i in range(35):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()
    services_forgot = [
        ("балаяж", "балаяж", random.choice([5000, 5500, 6000, 6500])),
        ("мелирование", "мелирование", random.choice([4000, 4500, 5000])),
        ("окрашивание в один тон", "окрашивание в один тон", random.choice([3000, 3500, 4000])),
        ("ботокс для волос", "ботокс для волос", random.choice([4000, 5000, 6000])),
        ("кератиновое выпрямление", "кератиновое выпрямление", random.choice([5000, 6000, 7000])),
        ("стрижку и укладку", "стрижка и укладка", random.choice([2000, 2500, 3000])),
    ]
    svc_spoken, svc_name, price = random.choice(services_forgot)
    p = price_str(price)

    forgot_phrases = [
        f"{add_filler('я у вас была недавно')}, мне делали что-то с волосами... не помню точно что",
        f"слушайте, я хотела бы повторить то, что мне делали в прошлый раз... {random.choice(FILLERS)}, только я забыла название",
        f"здрасьте, {random.choice(FILLERS)}, мне бы то же самое что и в прошлый раз, но я не помню как это называется",
        f"ой, я была у вас месяц назад, мне {random.choice(FILLERS)} что-то с волосами делали, красили вроде",
        f"я записывалась к вам, {random.choice(FILLERS)}, там такая процедура была... для волос... забыла как называется",
    ]

    clarify_phrases = [
        f"Подскажите, пожалуйста, как вас зовут? Я посмотрю вашу историю посещений.",
        f"Конечно, давайте посмотрим. Подскажите ваше имя, чтобы я нашла вашу запись.",
        f"Без проблем! Как вас зовут? Я найду вашу последнюю запись.",
    ]

    found_phrases = [
        f"Нашла! В прошлый раз вам делали {svc_spoken} у мастера {master}. Хотите повторить?",
        f"Да, вижу вашу запись. Это был {svc_spoken}, мастер {master}. Записать вас снова?",
        f"Вот, нашла. Вам делали {svc_spoken} у {master}. Стоимость — {p}. Хотите записаться?",
    ]

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": random.choice(forgot_phrases)},
        {"role": "assistant", "content": random.choice(clarify_phrases)},
        {"role": "user", "content": client},
        {"role": "assistant", "content": random.choice(found_phrases)},
        {"role": "user", "content": random.choice(["да, давайте!", "ой, точно! да, запишите меня", f"{random.choice(FILLERS)}, да, хочу повторить"])},
        {"role": "assistant", "content": f"Когда вам удобно? {master} работает {day}."},
        {"role": "user", "content": random.choice([f"давайте {day}", f"а {t1} можно?", f"{random.choice(FILLERS)}, {day} подойдёт"])},
        {"role": "assistant", "content": f"Записала вас, {client}! {master}, {svc_spoken}, {day} {t1}. Стоимость — {p}. Ждём вас!"},
        {"role": "user", "content": random.choice(["спасибо большое!", "отлично, спасибо!", "ой, спасибо, до свидания!"])},
        {"role": "assistant", "content": f"Пожалуйста, {client}! До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 2: Comparing with competitor (35-69 = 35)
# ============================================================
competitors = ["Золотые ножницы", "Бьюти Лаб", "Студия Красоты", "Мон Плезир", "Афродита"]
for i in range(35):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    comp = random.choice(competitors)
    t1, t1s = pick_time()
    day = pick_day()
    svc_options = [
        ("окрашивание", random.choice([3500, 4000, 4500, 5000])),
        ("стрижку", random.choice([1500, 1800, 2000, 2500])),
        ("маникюр", random.choice([1200, 1500, 1800, 2000])),
        ("кератиновое выпрямление", random.choice([5000, 6000, 7000])),
    ]
    svc, price = random.choice(svc_options)
    p = price_str(price)

    compare_phrases = [
        f"а скажите, у вас {svc} сколько стоит? а то в «{comp}» мне {price_str(price + random.choice([500, 1000, 1500]))} назвали",
        f"я обзваниваю салоны... {random.choice(FILLERS)}, сколько у вас {svc}? в «{comp}» дорого показалось",
        f"слушайте, а чем вы лучше «{comp}»? мне подруга сказала к вам идти, но я пока думаю",
        f"мне в «{comp}» не понравилось, {random.choice(FILLERS)}, ищу новый салон. Что у вас по ценам на {svc}?",
    ]

    advantage_phrases = [
        f"У нас {svc} стоит {p}. Мы используем профессиональную косметику, а мастер {master} — специалист с опытом более десяти лет.",
        f"Стоимость — {p}. Наши мастера работают на профессиональных средствах. {master} — один из лучших специалистов в городе.",
        f"{svc.capitalize()} у нас — {p}. Мы также предоставляем гарантию на результат и используем только премиальную косметику.",
    ]

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": random.choice(compare_phrases)},
        {"role": "assistant", "content": random.choice(advantage_phrases)},
        {"role": "user", "content": random.choice([
            f"ну ладно, {random.choice(FILLERS)}, давайте попробую к вам",
            "звучит неплохо, а можно записаться?",
            f"хм, {random.choice(FILLERS)}, окей, давайте попробуем",
            "ну цена нормальная, запишите меня",
        ])},
        {"role": "assistant", "content": f"С удовольствием! Когда вам удобно? {master} свободна {day} {t1}."},
        {"role": "user", "content": random.choice([f"давайте {day}", f"{t1} подойдёт", f"ну {day} {t1} ок"])},
        {"role": "assistant", "content": "Отлично! Как вас зовут?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {master} {day} {t1}. Стоимость — {p}. Уверена, вам понравится! До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 3: Trendy services — аэртач, шатуш, etc. (70-104 = 35)
# ============================================================
for i in range(35):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    trendy = [
        ("аэртач", "аэртач", ["эртач", "аэртач... или как оно правильно", "аэр тач"], random.choice([6000, 7000, 8000]), "четыре часа"),
        ("шатуш", "шатуш", ["шатуш... или шатуж?", "шатушь", "шатуш как-то так"], random.choice([5000, 6000, 7000]), "три с половиной часа"),
        ("омбре", "омбре", ["омбрэ", "амбре... нет, омбре", "омбре или как там"], random.choice([4500, 5500, 6500]), "три часа"),
        ("нанопластика волос", "нанопластику волос", ["нанопластика", "нано пластику... для волос", "нанопластика вроде"], random.choice([5000, 6000, 7000]), "два с половиной часа"),
        ("голливудское наращивание", "голливудское наращивание", ["голливудские пряди", "наращивание голливудское... или как", "голливуд наращивание"], random.choice([7000, 8000, 9000]), "три часа"),
    ]
    svc_name, svc_acc, misp, price, duration = random.choice(trendy)
    p = price_str(price)
    client_ask = random.choice(misp)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} {random.choice(FILLERS)}, я хотела бы записаться на {client_ask}"},
        {"role": "assistant", "content": f"Вы имеете в виду {svc_name}? Да, конечно, у нас есть эта услуга! Стоимость — {p}, длительность — примерно {duration}. Мастер {master} — отличный специалист по этой технике."},
        {"role": "user", "content": random.choice([
            f"да, точно, {svc_name}! а когда можно?",
            f"ой, ну да, {random.choice(FILLERS)}, это оно. Когда свободно?",
            "да-да, именно это. Когда можно записаться?",
        ])},
        {"role": "assistant", "content": f"Ближайшее свободное время у {master} — {day} {t1}. Подходит?"},
        {"role": "user", "content": random.choice(["да, отлично!", f"{random.choice(FILLERS)}, давайте", "подходит, записывайте"])},
        {"role": "assistant", "content": "Как вас зовут?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc_acc} к мастеру {master} {day} {t1}. Стоимость — {p}. Пожалуйста, приходите с чистыми сухими волосами. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 4: Mother booking daughter's first haircut (105-134 = 30)
# ============================================================
daughter_names = ["Машенька", "Анечка", "Сонечка", "Дашенька", "Полечка", "Варенька", "Настенька", "Катюша", "Алиночка", "Милочка"]
for i in range(30):
    s = salon()
    master = pick_master("f")
    mom = pick_client()
    daughter = random.choice(daughter_names)
    t1, t1s = pick_time()
    day = pick_day()
    age = random.choice([14, 15, 16, 17])
    price = random.choice([1500, 1800, 2000])
    p = price_str(price)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": add_filler(f"здравствуйте, я хотела бы дочку записать на стрижку. Ей {age} лет, она первый раз идёт в нормальный салон")},
        {"role": "assistant", "content": f"Здравствуйте! Как замечательно! Мастер {master} отлично работает с молодыми клиентами. Женская стрижка — {p}. Мастер сначала обсудит с дочкой, что она хочет, и подберёт подходящий вариант."},
        {"role": "user", "content": random.choice([
            f"ой, она хочет что-то модное, {random.choice(FILLERS)}, каре вроде",
            f"она ещё не определилась, {random.choice(FILLERS)}, можно на месте решить?",
            f"она хочет немного подстричь кончики и чёлку",
            f"ну она насмотрелась в интернете, {random.choice(FILLERS)}, хочет как у блогеров",
        ])},
        {"role": "assistant", "content": f"Конечно, мастер {master} всё обсудит на месте и подберёт стрижку по типу лица. Когда вам удобно прийти?"},
        {"role": "user", "content": f"а {day} можно?"},
        {"role": "assistant", "content": f"Да, {day} {master} свободна {t1}. Записать?"},
        {"role": "user", "content": "да, пожалуйста!"},
        {"role": "assistant", "content": f"Как зовут дочку?"},
        {"role": "user", "content": daughter},
        {"role": "assistant", "content": f"Записала {daughter} на женскую стрижку к мастеру {master} {day} {t1}. Стоимость — {p}. Ждём вас!"},
        {"role": "user", "content": "спасибо большое!"},
        {"role": "assistant", "content": f"Пожалуйста! {daughter} будет довольна, {master} — замечательный мастер. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 5: Fix bad haircut from elsewhere (135-169 = 35)
# ============================================================
for i in range(35):
    s = salon()
    master = pick_master()
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()
    price = random.choice([2000, 2500, 3000])
    p = price_str(price)

    problems = [
        "мне в другом салоне ужасно покрасили, цвет вообще не тот",
        "мне так криво подстригли, что я плакала",
        f"я была в другом месте, {random.choice(FILLERS)}, и мне испортили волосы",
        "мне сделали мелирование, а оно жёлтое какое-то",
        f"ой, {random.choice(FILLERS)}, мне так чёлку обрезали, что я в шоке",
        "мне брови выщипали криво, теперь одна выше другой",
    ]

    fixes = [
        f"Ой, как неприятно! Не переживайте, наш мастер {master} обязательно всё исправит. Давайте запишу вас на консультацию, мастер оценит ситуацию и предложит решение.",
        f"Понимаю ваше расстройство! {master} — очень опытный специалист, работает с такими случаями. Давайте сначала запишу вас на осмотр.",
        f"Не волнуйтесь, это поправимо! Мастер {master} посмотрит и подберёт лучший вариант исправления. Когда сможете прийти?",
    ]

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": random.choice(problems)},
        {"role": "assistant", "content": random.choice(fixes)},
        {"role": "user", "content": random.choice([
            f"да, пожалуйста, {random.choice(FILLERS)}, мне срочно надо это исправить",
            "а сколько это будет стоить?",
            f"ой, спасибо, {random.choice(FILLERS)}, а когда можно прийти?",
        ])},
        {"role": "assistant", "content": f"Консультация бесплатная, а стоимость коррекции зависит от объёма работы, примерно от {p}. {master} свободна {day} {t1}. Подходит?"},
        {"role": "user", "content": random.choice(["да, записывайте!", f"{random.choice(FILLERS)}, давайте", "подходит, конечно"])},
        {"role": "assistant", "content": "Как вас зовут?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас к мастеру {master} {day} {t1} на консультацию и коррекцию. Не переживайте, всё поправим! До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 6: Consultation before committing (170-199 = 30)
# ============================================================
for i in range(30):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    consult_topics = [
        ("хочу поменять цвет волос, но не знаю какой подойдёт", "окрашивание", "подбор цвета и типа окрашивания", random.choice([3000, 4000, 5000, 6000])),
        ("думаю сделать короткую стрижку, но боюсь", "стрижку", "подбор стрижки по форме лица", random.choice([1500, 2000, 2500])),
        (f"{random.choice(FILLERS)}, хочу нарастить ресницы, но не знаю какие", "наращивание ресниц", "подбор формы и длины ресниц", random.choice([2500, 3000, 3500])),
        ("хочу сделать что-то с бровями, но не понимаю что мне нужно", "оформление бровей", "подбор формы бровей", random.choice([800, 1000, 1200])),
    ]
    topic, svc, consult_desc, price = random.choice(consult_topics)
    p = price_str(price)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} {add_filler(topic)}"},
        {"role": "assistant", "content": f"Отлично, что вы хотите подойти к этому осознанно! Могу записать вас на бесплатную консультацию к мастеру {master}. Она специализируется на {consult_desc} и поможет определиться."},
        {"role": "user", "content": random.choice([
            "а это точно бесплатно?",
            "о, круто! а если я сразу захочу сделать, можно?",
            f"{random.choice(FILLERS)}, хорошо, а когда можно прийти?",
        ])},
        {"role": "assistant", "content": f"Консультация абсолютно бесплатная. Если решите сделать {svc} в тот же день — сможем сразу приступить. Стоимость — от {p}. {master} свободна {day} {t1}."},
        {"role": "user", "content": random.choice(["отлично, записывайте!", f"давайте {day}", "ой, прекрасно, запишите меня"])},
        {"role": "assistant", "content": "Ваше имя, пожалуйста?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на консультацию к мастеру {master} {day} {t1}. Если решите сделать процедуру — сразу приступим. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 7: Group booking — девичник, подруги (200-234 = 35)
# ============================================================
for i in range(35):
    s = salon()
    master1 = pick_master("f")
    master2 = pick_master("f")
    while master2 == master1:
        master2 = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()
    count = random.choice([2, 3, 4, 5])
    count_word = {2: "двоих", 3: "троих", 4: "четверых", 5: "пятерых"}[count]
    events = ["девичник", "девочкам собираемся компанией", "подружки решили вместе сходить", "день рождения у подруги отмечаем"]

    svc_options = [
        ("маникюр", random.choice([1500, 1800, 2000])),
        ("укладку", random.choice([1500, 2000, 2500])),
        ("маникюр и укладку", random.choice([3000, 3500, 4000])),
    ]
    svc, price = random.choice(svc_options)
    p = price_str(price)
    total = price_str(price * count)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} {random.choice(FILLERS)}, у нас {random.choice(events)}, и нам нужно записать {count_word} человек на {svc}"},
        {"role": "assistant", "content": f"Как здорово! С удовольствием запишу вашу компанию. {svc.capitalize()} стоит {p} за одного человека. Для {count_word} человек итого получится {total}. На какой день?"},
        {"role": "user", "content": f"а {day} можно всех сразу?"},
        {"role": "assistant", "content": f"Сейчас посмотрю... Да, {day} {t1} у нас свободны мастера {master1} и {master2}, сможем принять всех. Может занять чуть больше времени, но уложимся."},
        {"role": "user", "content": random.choice([
            "отлично, записывайте!",
            f"ой, класс, {random.choice(FILLERS)}, давайте!",
            "супер, нам это подходит!",
        ])},
        {"role": "assistant", "content": "На чьё имя записать?"},
        {"role": "user", "content": f"{client}. Ну и ещё {count - 1} девочки со мной"},
        {"role": "assistant", "content": f"{client}, записала вашу группу — {count_word} человек на {svc} {day} {t1}. Мастера {master1} и {master2}. Итого — {total}. Ждём вас!"},
        {"role": "user", "content": random.choice(["спасибо, будем!", "круто, спасибо!", "ждите нас!"])},
        {"role": "assistant", "content": f"Будет отличный {random.choice(events).split()[0]}! До встречи, {client}!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 8: Client running late (235-264 = 30)
# ============================================================
for i in range(30):
    s = salon()
    master = pick_master()
    client = pick_client()
    t1, t1s = pick_time()
    t2, t2s = pick_time()
    day_r = pick_day_raw()
    late_min = random.choice([15, 20, 30])
    late_word = {15: "пятнадцать", 20: "двадцать", 30: "тридцать"}[late_min]

    svc = random.choice(["стрижку", "маникюр", "окрашивание", "укладку"])

    can_wait = random.random() < 0.6

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": random.choice([
            f"здрасте, {random.choice(FILLERS)}, я записана на {t1s} на {svc}, но я опаздываю минут на {late_word}!",
            f"алло, извините, я {client}, у меня запись на {t1s}, но я застряла в пробке, буду минут через {late_word}",
            f"ой, это {client}, я сегодня к вам на {t1s}... {random.choice(FILLERS)}, опаздываю, можно попозже прийти?",
        ])},
    ]

    if can_wait:
        conv += [
            {"role": "assistant", "content": f"Не переживайте, {client}! Мастер {master} сможет вас подождать. Приходите, как будете готовы, но, пожалуйста, не позже чем через {late_word} минут, хорошо?"},
            {"role": "user", "content": random.choice(["ой, спасибо огромное! бегу!", "спасибо-спасибо, уже еду!", f"{random.choice(FILLERS)}, вы лучшие, уже выезжаю!"])},
            {"role": "assistant", "content": f"Ждём вас, {client}! Не торопитесь, доберитесь безопасно."},
        ]
    else:
        conv += [
            {"role": "assistant", "content": f"К сожалению, мастер {master} после вас принимает следующего клиента и не сможет ждать. Могу перенести вашу запись на {t2}. Подойдёт?"},
            {"role": "user", "content": random.choice([
                f"ну ладно, {random.choice(FILLERS)}, давайте на {t2s}",
                f"эх... хорошо, перенесите на {t2s}",
                "а другого варианта нет? ну ладно, давайте",
            ])},
            {"role": "assistant", "content": f"Перенесла вашу запись на {t2}. {client}, ждём вас!"},
            {"role": "user", "content": "спасибо, извините за беспокойство"},
            {"role": "assistant", "content": "Ничего страшного! До встречи!"},
        ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 9: Price negotiation / discount (265-299 = 35)
# ============================================================
for i in range(35):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    svc_options = [
        ("окрашивание", random.choice([4000, 5000, 6000])),
        ("маникюр с покрытием", random.choice([1800, 2000, 2500])),
        ("кератиновое выпрямление", random.choice([5000, 6000, 7000])),
        ("стрижку и укладку", random.choice([2000, 2500, 3000])),
    ]
    svc, price = random.choice(svc_options)
    p = price_str(price)

    discount_type = random.choice(["none", "first_visit", "combo"])

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} {add_filler(f'а сколько у вас {svc} стоит?')}"},
        {"role": "assistant", "content": f"{svc.capitalize()} у мастера {master} — {p}."},
        {"role": "user", "content": random.choice([
            f"ой, а скидочку никак нельзя?",
            f"а подешевле нет варианта? {random.choice(FILLERS)}, дороговато как-то",
            f"хм, а акции какие-нибудь есть?",
            f"{random.choice(FILLERS)}, а если я подругу приведу, скидка будет?",
        ])},
    ]

    if discount_type == "first_visit":
        disc_price = price - 500
        dp = price_str(disc_price)
        conv += [
            {"role": "assistant", "content": f"Для первого посещения у нас действует скидка — {dp} вместо {p}. Хотите записаться?"},
            {"role": "user", "content": f"о, {random.choice(FILLERS)}, тогда давайте!"},
        ]
    elif discount_type == "combo":
        conv += [
            {"role": "assistant", "content": f"Скидка на отдельные услуги, к сожалению, не предусмотрена. Но если возьмёте комплекс, например {svc} плюс укладку — выйдет выгоднее. Хотите посмотреть варианты?"},
            {"role": "user", "content": random.choice(["ну давайте комплекс тогда", f"{random.choice(FILLERS)}, а сколько комплекс?", "ладно, запишите просто на {svc}".format(svc=svc)])},
        ]
    else:
        conv += [
            {"role": "assistant", "content": f"Понимаю! К сожалению, на эту услугу скидки сейчас нет. Но качество работы {master} того стоит — наши клиенты всегда довольны. Хотите записаться?"},
            {"role": "user", "content": random.choice([f"ну ладно, {random.choice(FILLERS)}, давайте", "хорошо, записывайте", f"эх, {random.choice(FILLERS)}, ну давайте тогда"])},
        ]

    conv += [
        {"role": "assistant", "content": f"Когда вам удобно? {master} свободна {day} {t1}."},
        {"role": "user", "content": random.choice([f"давайте {day}", f"{t1} подойдёт"])},
        {"role": "assistant", "content": "Ваше имя?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {master} {day} {t1}. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 10: Allergies / sensitivities (300-329 = 30)
# ============================================================
for i in range(30):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    allergy_cases = [
        ("окрашивание", "аллергия на аммиачную краску", "безаммиачные красители", random.choice([4000, 5000, 5500])),
        ("наращивание ресниц", "чувствительные глаза, от клея раздражение", "гипоаллергенный клей", random.choice([2500, 3000, 3500])),
        ("маникюр с покрытием", "аллергия на гель-лак", "гипоаллергенное покрытие", random.choice([1800, 2000, 2500])),
        ("химическую завивку", "чувствительная кожа головы", "щадящий состав для чувствительной кожи", random.choice([3000, 4000, 4500])),
        ("окрашивание бровей", "аллергия на хну", "синтетический краситель без хны", random.choice([800, 1000, 1200])),
    ]
    svc, problem, solution, price = random.choice(allergy_cases)
    p = price_str(price)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} {random.choice(FILLERS)}, я хотела бы на {svc}, но у меня {problem}. Это проблема?"},
        {"role": "assistant", "content": f"Спасибо, что предупредили! Это очень важно. У нас есть {solution}, которые подходят для чувствительных клиентов. Мастер {master} работает с такими случаями и подберёт безопасный вариант."},
        {"role": "user", "content": random.choice([
            "ой, правда? а я боялась, что откажете",
            f"{random.choice(FILLERS)}, отлично, а сколько стоит?",
            "это замечательно! а можно записаться?",
        ])},
        {"role": "assistant", "content": f"Конечно не откажем! Стоимость — {p}. Рекомендуем также сделать тест на аллергию за сорок восемь часов до процедуры. {master} свободна {day} {t1}. Записать?"},
        {"role": "user", "content": "да, пожалуйста!"},
        {"role": "assistant", "content": "Ваше имя?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {master} {day} {t1}. Стоимость — {p}. Не забудьте прийти на тест за два дня до процедуры. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 11: Unclear speech, admin clarifying (330-364 = 35)
# ============================================================
for i in range(35):
    s = salon()
    master = pick_master()
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    unclear_cases = [
        (
            "[неразборчиво]... мне бы на... [шум на фоне]... стрижку",
            "Извините, плохо слышно! Вы сказали — на стрижку? Подскажите, женская или мужская?",
            "женскую!",
            "женскую стрижку", random.choice([1500, 2000, 2500])
        ),
        (
            "алё... [неразборчиво]... ногти... [шум на фоне]",
            "Простите, связь прерывается. Вы хотите записаться на маникюр?",
            "да! маникюр! простите, на улице шумно",
            "маникюр", random.choice([1200, 1500, 1800])
        ),
        (
            "мне бы это... как его... [неразборчиво]... ну для волос... чтобы блестели",
            "Может быть, вы имеете в виду ламинирование волос? Или ботокс для волос?",
            f"{random.choice(FILLERS)}, ламинирование! точно!",
            "ламинирование волос", random.choice([3000, 4000, 5000])
        ),
        (
            "[шум на фоне] здрасте... мне... [неразборчиво]... брови...",
            "Здравствуйте! Плохо вас слышу. Вы хотите записаться на оформление бровей?",
            "да-да, на брови! извините, в метро еду",
            "оформление бровей", random.choice([800, 1000, 1200])
        ),
        (
            "алё, слышите? мне нужно [неразборчиво]... покраситься... [шум на фоне]",
            "Слышу вас! На окрашивание хотите записаться? В какой цвет планируете?",
            "да, в блонд! простите за шум",
            "окрашивание", random.choice([4000, 5000, 6000])
        ),
    ]
    msg1, resp1, msg2, svc, price = random.choice(unclear_cases)
    p = price_str(price)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": msg1},
        {"role": "assistant", "content": resp1},
        {"role": "user", "content": msg2},
        {"role": "assistant", "content": f"Поняла! {svc.capitalize()} — {p}. Мастер {master} свободна {day} {t1}. Записать вас?"},
        {"role": "user", "content": random.choice(["да!", "давайте!", "записывайте"])},
        {"role": "assistant", "content": "Как вас зовут?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {master} {day} {t1}. Стоимость — {p}. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 12: Talkative client, admin steering back (365-394 = 30)
# ============================================================
for i in range(30):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()
    svc = random.choice(["стрижку", "укладку", "маникюр", "окрашивание"])
    price = random.choice([1500, 2000, 2500, 3000, 4000])
    p = price_str(price)

    offtopic = [
        f"а вы знаете, я вчера такой фильм посмотрела! {random.choice(FILLERS)}, просто невероятный, три часа не могла оторваться, и там ещё актёр такой красивый...",
        f"ой, а у меня кошка вчера такое устроила! {random.choice(FILLERS)}, вы не поверите, залезла на шкаф и скинула все цветы...",
        f"а я вот думаю, может мне ещё и причёску сменить кардинально? хотя нет, муж будет ругаться, он у меня вообще консервативный, {random.choice(FILLERS)}, мы вчера поссорились из-за...",
        f"знаете, а я читала что сейчас модно {random.choice(FILLERS)} натуральные оттенки, и ещё эти, как их, корейские тренды, и вообще я подписалась на блогершу одну...",
        f"ой, а погода сегодня! вы видели? я пока шла, чуть зонт не сломала, {random.choice(FILLERS)}, и ещё очередь в магазине была такая...",
    ]

    steer_back = [
        f"Очень интересно! Но давайте вернёмся к записи, чтобы вы не забыли. Так когда вам удобно прийти на {svc}?",
        f"Ого, как интересно! Но мне бы хотелось вас записать, пока есть свободные места. На какой день?",
        f"Замечательная история! Давайте зафиксируем вашу запись, чтобы точно забронировать время. Какой день удобен?",
    ]

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} мне бы на {svc} записаться"},
        {"role": "assistant", "content": f"Конечно! {svc.capitalize()} у мастера {master} — {p}. Когда вам удобно?"},
        {"role": "user", "content": random.choice(offtopic)},
        {"role": "assistant", "content": random.choice(steer_back)},
        {"role": "user", "content": f"ой, да, извините! {random.choice(FILLERS)}, давайте {day}"},
        {"role": "assistant", "content": f"{master} свободна {day} {t1}. Подходит?"},
        {"role": "user", "content": "да, отлично!"},
        {"role": "assistant", "content": "Ваше имя?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {master} {day} {t1}. Стоимость — {p}. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 13: Special event — выпускной, юбилей, фотосессия (395-429 = 35)
# ============================================================
for i in range(35):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    events = [
        ("выпускной", "выпускной вечер", ["праздничную укладку", "вечерний макияж и укладку"], random.choice([3000, 3500, 4000, 5000])),
        ("юбилей", "юбилей", ["праздничную укладку", "укладку и макияж"], random.choice([3000, 4000, 4500])),
        ("свадьбу подруги", "свадьбу", ["вечернюю укладку", "укладку и маникюр"], random.choice([3500, 4000, 5000])),
        ("фотосессию", "фотосессию", ["укладку для фотосессии", "макияж и укладку"], random.choice([3000, 4000, 5000])),
        ("корпоратив", "корпоратив", ["экспресс-укладку", "укладку и маникюр"], random.choice([2000, 2500, 3000])),
        ("день рождения", "день рождения", ["праздничную причёску", "укладку и макияж"], random.choice([2500, 3000, 4000])),
    ]
    event_short, event_full, svc_list, price = random.choice(events)
    svc = random.choice(svc_list)
    p = price_str(price)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} {random.choice(FILLERS)}, у меня скоро {event_short}, мне нужно {svc}"},
        {"role": "assistant", "content": f"Как здорово! Поздравляю с {event_full if event_short != 'фотосессию' else 'предстоящей фотосессией'}! {svc.capitalize()} — {p}. Мастер {master} делает потрясающие праздничные образы. Когда у вас мероприятие?"},
        {"role": "user", "content": f"через неделю, {day}"},
        {"role": "assistant", "content": f"Рекомендую прийти утром, чтобы было время на всё. {master} свободна {day} {t1}. Записать?"},
        {"role": "user", "content": random.choice(["да, пожалуйста!", "конечно!", f"{random.choice(FILLERS)}, записывайте!"])},
        {"role": "assistant", "content": "Ваше имя?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {master} {day} {t1}. Стоимость — {p}. Вы будете выглядеть великолепно! До встречи!"},
        {"role": "user", "content": random.choice(["спасибо огромное!", "ой, спасибо! жду не дождусь!", "спасибо, до свидания!"])},
        {"role": "assistant", "content": f"Пожалуйста, {client}! До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 14: Unhappy with previous visit, rebooking (430-464 = 35)
# ============================================================
for i in range(35):
    s = salon()
    old_master = pick_master()
    new_master = pick_master()
    while new_master == old_master:
        new_master = pick_master()
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    complaints = [
        f"я была у {old_master} на стрижке и мне не понравилось, слишком коротко",
        f"{random.choice(FILLERS)}, в прошлый раз {old_master} мне окрашивание делала, и цвет совсем не тот получился",
        f"мне {old_master} маникюр делала, и он облез через два дня",
        f"я ходила к {old_master}, но {random.choice(FILLERS)}, мне не подошёл её стиль работы",
    ]

    svc = random.choice(["стрижку", "окрашивание", "маникюр", "укладку"])
    price = random.choice([1500, 2000, 2500, 3000, 4000])
    p = price_str(price)

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} {random.choice(complaints)}. Можно к другому мастеру?"},
        {"role": "assistant", "content": f"Мне очень жаль, что вам не понравилось! Конечно, могу записать вас к другому мастеру. Рекомендую {new_master} — очень аккуратный и внимательный специалист. На {svc} хотите записаться?"},
        {"role": "user", "content": random.choice([
            f"да, давайте к {new_master}",
            f"{random.choice(FILLERS)}, хорошо, попробую",
            "да, именно на это",
        ])},
        {"role": "assistant", "content": f"{new_master} свободна {day} {t1}. Стоимость — {p}. Записать?"},
        {"role": "user", "content": "да, записывайте"},
        {"role": "assistant", "content": f"Как вас зовут?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {new_master} {day} {t1}. Стоимость — {p}. Уверена, в этот раз всё будет отлично! До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# SCENARIO 15: Loyalty program / скидочная карта (465-499 = 35)
# ============================================================
for i in range(35):
    s = salon()
    master = pick_master("f")
    client = pick_client()
    t1, t1s = pick_time()
    day = pick_day()

    svc = random.choice(["стрижку", "маникюр", "окрашивание", "укладку", "педикюр"])
    price = random.choice([1500, 2000, 2500, 3000, 4000])
    p = price_str(price)

    loyalty_q = random.choice([
        "а у вас есть скидочная карта?",
        f"{random.choice(FILLERS)}, а программа лояльности какая-нибудь есть?",
        "а бонусы какие-нибудь копятся?",
        "подруга говорила, у вас карта постоянного клиента есть?",
        f"а если я постоянно хожу, {random.choice(FILLERS)}, скидка будет?",
    ])

    has_program = random.random() < 0.7

    conv = [
        {"role": "assistant", "content": greeting_a(s)},
        {"role": "user", "content": f"{greeting_c()} хочу на {svc} записаться. И ещё вопрос — {loyalty_q}"},
    ]

    if has_program:
        conv += [
            {"role": "assistant", "content": f"Да, конечно! У нас действует накопительная система: после пятого посещения вы получаете скидку десять процентов на все услуги. А пока — {svc} у мастера {master} стоит {p}. Записать вас?"},
        ]
    else:
        conv += [
            {"role": "assistant", "content": f"Мы сейчас как раз запускаем программу лояльности! Пока могу предложить {svc} у мастера {master} за {p}. Оставлю вашу заявку на карту, и как только программа заработает, мы вам сообщим. Записать на {svc}?"},
        ]

    conv += [
        {"role": "user", "content": random.choice([
            "да, давайте!",
            f"хорошо, {random.choice(FILLERS)}, записывайте",
            "отлично, запишите меня",
        ])},
        {"role": "assistant", "content": f"Когда вам удобно? {master} свободна {day} {t1}."},
        {"role": "user", "content": random.choice([f"давайте {day}", f"{t1} подойдёт", f"{random.choice(FILLERS)}, {day} хорошо"])},
        {"role": "assistant", "content": "Ваше имя, пожалуйста?"},
        {"role": "user", "content": client},
        {"role": "assistant", "content": f"{client}, записала вас на {svc} к мастеру {master} {day} {t1}. Стоимость — {p}. До встречи!"},
    ]
    dialogs.append(make_dialog(conv))

# ============================================================
# Write output
# ============================================================
random.shuffle(dialogs)

out_path = "/Users/mihaildurnev/Desktop/voice AI/voicebook/training/dataset/beauty_salon_dialogs_extra.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for d in dialogs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print(f"Generated {len(dialogs)} dialogs -> {out_path}")
