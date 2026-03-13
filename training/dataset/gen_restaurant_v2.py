#!/usr/bin/env python3
"""Generate 500 high-quality SFT training dialogs for restaurant AI voice receptionist (v2).

Scenario distribution:
  - Simple table booking (100)
  - Booking with occasion (60)
  - Large group / banquet / corporate (60)
  - Cancellation (40)
  - Reschedule (40)
  - Time unavailable → alternatives (40)
  - Menu / allergy / diet + booking (40)
  - Unclear/vague request → clarification (30)
  - User changes mind mid-dialog (30)
  - VIP/private room (20)
  - Price inquiry only (20)
  - Delivery/takeout redirect (10)
  - Aggressive/impatient customer (10)
"""

import json
import random
import os

random.seed(123)

SYSTEM_PROMPT = (
    "Вы — администратор ресторана. Помогаете гостям забронировать столик, "
    "выбрать зал и обсудить детали визита. Говорите вежливо, гостеприимно и профессионально."
)

# ──────────────── Building blocks ────────────────

NAMES_MALE = [
    "Александр", "Дмитрий", "Сергей", "Андрей", "Михаил", "Иван", "Максим",
    "Павел", "Артём", "Николай", "Владимир", "Олег", "Роман", "Евгений",
    "Алексей", "Виктор", "Константин", "Денис", "Игорь", "Тимур", "Руслан",
    "Борис", "Кирилл", "Антон", "Григорий", "Станислав", "Вадим", "Фёдор",
]
NAMES_FEMALE = [
    "Елена", "Анна", "Мария", "Ольга", "Наталья", "Татьяна", "Екатерина",
    "Ирина", "Светлана", "Юлия", "Дарья", "Алина", "Виктория", "Ксения",
    "Полина", "Марина", "Людмила", "Валентина", "Надежда", "Оксана",
    "Лариса", "Диана", "Кристина", "Вера", "Галина", "Софья", "Милана",
]

FILLERS = [
    "ну", "эм", "так", "вот", "ааа", "короче", "слушайте", "значит",
    "это самое", "как бы", "ну вот", "в общем", "ну типа", "а",
    "ну это", "так сказать",
]

DATES_SPOKEN = [
    "завтра", "послезавтра", "в эту субботу", "в это воскресенье", "в пятницу",
    "на следующей неделе", "через неделю", "в эти выходные",
    "в ближайшую субботу", "третьего числа", "пятого марта", "десятого",
    "пятнадцатого", "двадцатого", "двадцать третьего", "тридцатого",
    "в следующую пятницу", "через два дня", "седьмого апреля",
    "первого мая", "двенадцатого июня", "на выходных",
    "в четверг на следующей неделе", "в ближайшее воскресенье",
    "в среду", "в понедельник", "во вторник", "в четверг",
]

TIMES_SPOKEN = [
    "в шесть", "часов в шесть", "к семи", "в семь", "в семь тридцать",
    "в восемь", "к восьми", "около семи", "часам к шести",
    "ну часов в семь", "в полседьмого", "к шести вечера",
    "в восемь вечера", "на семь", "в шесть тридцать",
    "ну где-то в семь", "часиков в шесть", "примерно в восемь",
    "к двенадцати", "в час дня", "в два", "на час", "около двух",
    "в полвторого", "к трём", "часа в три", "в пять вечера",
]

TIMES_FORMAL = [
    "восемнадцать часов", "восемнадцать тридцать", "девятнадцать часов",
    "девятнадцать тридцать", "двадцать часов", "двенадцать часов",
    "тринадцать часов", "четырнадцать часов", "семнадцать часов",
]

GUEST_SPOKEN = {
    2: ["на двоих", "нас двое", "вдвоём", "два человека", "для двоих", "нас будет двое"],
    3: ["на троих", "нас трое", "три человека", "нас будет трое"],
    4: ["на четверых", "нас четверо", "четыре человека", "на четыре персоны", "нас будет четверо"],
    5: ["на пятерых", "нас пятеро", "пять человек", "нас будет пять"],
    6: ["на шестерых", "нас шестеро", "шесть человек", "человек шесть"],
    7: ["на семерых", "семь человек", "нас будет семеро"],
    8: ["на восьмерых", "восемь человек", "человек восемь", "нас восемь будет"],
    10: ["на десять человек", "человек десять", "нас десять будет", "десять человек"],
    12: ["на двенадцать человек", "человек двенадцать", "двенадцать нас будет"],
    15: ["на пятнадцать человек", "человек пятнадцать", "нас пятнадцать"],
    20: ["на двадцать человек", "человек двадцать", "двадцать гостей"],
    25: ["на двадцать пять человек", "человек двадцать пять", "двадцать пять гостей"],
    30: ["на тридцать человек", "человек тридцать", "тридцать гостей"],
    40: ["на сорок человек", "человек сорок", "сорок гостей"],
    50: ["на пятьдесят человек", "человек пятьдесят", "пятьдесят гостей"],
}

HALLS = [
    "основной зал", "VIP-зал", "банкетный зал", "каминный зал",
    "летняя веранда", "зал у окна", "малый зал", "уютный зал",
]

CUISINES = [
    "европейская", "русская", "итальянская", "японская",
    "грузинская", "авторская", "средиземноморская", "паназиатская",
]

ALLERGIES = ["орехи", "глютен", "лактоза", "морепродукты", "мёд", "цитрусовые", "яйца", "рыба"]

DIET_TYPES = [
    "вегетарианское меню", "веганское меню", "безглютеновое меню",
    "халяль", "детское меню", "постное меню", "диетическое меню",
]

OCCASIONS = [
    "день рождения", "юбилей", "годовщина свадьбы", "помолвка",
    "корпоратив", "выпускной", "свадьба", "новоселье",
    "повышение на работе", "встреча одноклассников",
]

SPECIAL_REQUESTS = [
    "торт", "живая музыка", "украшение зала шарами", "фотозона",
    "проектор", "микрофон", "цветы на стол", "свечи",
    "именная табличка", "детский аниматор",
]

NOISE_MARKERS = ["[неразборчиво]", "[шум]", "[помехи]", "[плохая связь]"]

PHONE_PREFIXES = ["восемь девять", "плюс семь девять", "восемь девятьсот"]

RESTAURANT_NAMES = [
    "Белый сад", "Олива", "Террасса", "Бриз", "Сказка", "Панорама",
    "Верона", "Каштан", "Прага", "Романтика", "Лунный свет",
    "Итальянский дворик", "Империя", "Центральный", "Домино",
    "Семейный очаг", "Усадьба", "Тёплый дом", "Гранд", "Европа",
    "Палаццо", "Зелёный сад", "Свежесть", "Базилик", "Вкус",
    "Парус", "Маяк", "Причал", "Лагуна", "Большой", "Площадь",
    "Набережная", "Встреча", "Праздник", "Торжество", "Феерия",
    "Белая роза", "Джаз", "Карамель", "Деловой квартал", "Столица",
    "Романс", "Бистро", "Огонёк", "Аромат", "Патио", "Сирень",
    "Фонтан", "Ривьера", "Акварель",
]

CANCEL_REASONS = [
    "планы изменились", "заболел", "не получится прийти",
    "перенесли мероприятие", "срочная командировка",
    "семейные обстоятельства", "улетаю",
]


# ──────────────── Helpers ────────────────

def add_filler(text, prob=0.4):
    if random.random() < prob:
        f = random.choice(FILLERS)
        if random.random() < 0.5:
            return f.capitalize() + ", " + text[0].lower() + text[1:]
        else:
            return f + ", " + text[0].lower() + text[1:]
    return text


def add_hesitation(text, prob=0.2):
    if random.random() < prob:
        words = text.split()
        if len(words) > 3:
            pos = random.randint(1, min(len(words) - 2, 4))
            h = random.choice(["э...", "эм...", "ну...", "как его...", "это..."])
            words.insert(pos, h)
            return " ".join(words)
    return text


def add_noise(text, prob=0.05):
    if random.random() < prob:
        marker = random.choice(NOISE_MARKERS)
        words = text.split()
        if len(words) > 2:
            pos = random.randint(0, len(words) - 1)
            words[pos] = marker
            return " ".join(words)
    return text


def naturalize(text):
    text = add_filler(text)
    text = add_hesitation(text)
    text = add_noise(text)
    if random.random() < 0.3:
        text = text.replace(".", "").replace(",", " ").replace("  ", " ").strip()
    if random.random() < 0.15:
        text = text + " " + random.choice(["вот", "ну вот так", "да", "вот так", "типа того", "как-то так"])
    return text


def spell_number(n):
    nums = {
        1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
        6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять",
        11: "одиннадцать", 12: "двенадцать", 13: "тринадцать",
        14: "четырнадцать", 15: "пятнадцать", 20: "двадцать",
        25: "двадцать пять", 30: "тридцать", 40: "сорок", 50: "пятьдесят",
    }
    return nums.get(n, str(n))


def spell_thousands(n):
    m = {
        1: "одну тысячу", 2: "две тысячи", 3: "три тысячи",
        4: "четыре тысячи", 5: "пять тысяч", 6: "шесть тысяч",
        7: "семь тысяч", 8: "восемь тысяч", 10: "десять тысяч",
        12: "двенадцать тысяч", 15: "пятнадцать тысяч",
        20: "двадцать тысяч", 25: "двадцать пять тысяч",
        30: "тридцать тысяч", 40: "сорок тысяч", 50: "пятьдесят тысяч",
    }
    return m.get(n, f"{n} тысяч")


def guest_count_spelled(n):
    m = {
        2: "двух", 3: "трёх", 4: "четырёх", 5: "пять", 6: "шесть",
        7: "семь", 8: "восемь", 10: "десять", 12: "двенадцать",
        15: "пятнадцать", 20: "двадцать", 25: "двадцать пять",
        30: "тридцать", 40: "сорок", 50: "пятьдесят",
    }
    return m.get(n, str(n))


def random_phone():
    digits = [str(random.randint(0, 9)) for _ in range(7)]
    return (random.choice(PHONE_PREFIXES) + " "
            + "".join(digits[:3]) + " " + "".join(digits[3:5]) + " " + "".join(digits[5:]))


def pick_time():
    return random.choice(TIMES_SPOKEN)


def pick_time_formal():
    return random.choice(TIMES_FORMAL)


def pick_date():
    return random.choice(DATES_SPOKEN)


def pick_guest(n):
    return random.choice(GUEST_SPOKEN.get(n, [f"{n} человек"]))


def pick_hall():
    return random.choice(HALLS)


def pick_name():
    return random.choice(NAMES_MALE + NAMES_FEMALE)


def pick_restaurant():
    return random.choice(RESTAURANT_NAMES)


def greeting():
    r = pick_restaurant()
    return random.choice([
        f"Добрый день! Ресторан «{r}», администратор слушает. Чем могу помочь?",
        f"Здравствуйте! Ресторан «{r}», рады вашему звонку. Чем могу быть полезна?",
        f"Добрый вечер! Ресторан «{r}», слушаю вас.",
        f"Здравствуйте! Ресторан «{r}», администратор на связи. Чем могу помочь?",
        f"Добрый день! Ресторан «{r}», вас приветствует администратор.",
        f"Алло, добрый день! Ресторан «{r}». Чем могу помочь?",
    ])


def farewell_user():
    return naturalize(random.choice([
        "Спасибо большое!", "Спасибо, до свидания", "Отлично, спасибо",
        "Благодарю!", "Спасибо, всего доброго", "Угу, спасибо",
        "Ладно, спасибо, пока", "Хорошо, спасибо вам",
    ]))


def farewell_assistant():
    return random.choice([
        "Благодарим за звонок! Хорошего вам дня, до встречи!",
        "Спасибо за звонок! Ждём вас с нетерпением. До свидания!",
        "Всего доброго! Будем рады вас видеть!",
        "До свидания! Хорошего дня!",
        "Спасибо! Ждём вас, до встречи!",
    ])


def phone_exchange(name, convs):
    """Add phone-number collection turns."""
    convs.append({"role": "assistant", "content": random.choice([
        f"Спасибо, {name}! Подскажите контактный номер телефона для подтверждения.",
        f"Записала, {name}. Оставьте, пожалуйста, номер телефона на случай изменений.",
        f"Отлично, {name}! Ваш номер телефона для связи?",
        f"{name}, продиктуйте, пожалуйста, номер телефона.",
    ])})
    phone = random_phone()
    # Variations on how users dictate phones
    variant = random.random()
    if variant < 0.3:
        convs.append({"role": "user", "content": naturalize(phone)})
    elif variant < 0.5:
        convs.append({"role": "user", "content": naturalize(f"Да, записывайте: {phone}")})
    elif variant < 0.7:
        # User corrects themselves mid-number
        wrong_digit = str(random.randint(0, 9))
        convs.append({"role": "user", "content": naturalize(
            f"{phone[:15]}... нет, подождите... {phone}"
        )})
    else:
        convs.append({"role": "user", "content": naturalize(f"Номер {phone}")})


# ══════════════ Scenario generators ══════════════

# ─── 1. Simple table booking (100) ───

def gen_simple_booking():
    n = random.choice([2, 2, 2, 3, 3, 4, 4, 4, 5, 6, 6, 7, 8])
    date = pick_date()
    time_u = pick_time()
    time_f = pick_time_formal()
    name = pick_name()
    hall = pick_hall()
    hall2 = pick_hall()
    while hall2 == hall:
        hall2 = pick_hall()

    variant = random.randint(1, 5)

    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Straightforward: user gives everything
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Хотел бы забронировать столик {date} {time_u}, {pick_guest(n)}",
            f"Можно столик забронировать? {date}, {pick_guest(n)}, {time_u}",
            f"Здравствуйте, нужен столик {date} на вечер, {pick_guest(n)}",
            f"Добрый день, хотели бы зарезервировать столик {date} {time_u}",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Конечно! Столик на {guest_count_spelled(n)} гостей, {date}. Есть ли предпочтения по залу? У нас есть {hall} и {hall2}.",
            f"С удовольствием! Бронируем на {guest_count_spelled(n)} персон, {date}. Какой зал предпочитаете — {hall} или {hall2}?",
            f"Отлично, записываю. На {guest_count_spelled(n)} гостей, {date}. Вам удобнее в {hall} или в {hall2}?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Давайте в {hall}", f"В {hall}, пожалуйста",
            f"Нам бы {hall} подошёл", f"Лучше {hall}",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Прекрасный выбор! На чьё имя оформить бронирование?",
            f"Замечательно, {hall} свободен. Подскажите ваше имя для брони.",
            f"Хорошо, бронирую {hall}. Как записать вас?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"На {name}", f"{name}", f"Запишите на {name}",
        ]))})

        phone_exchange(name, convs)

        convs.append({"role": "assistant", "content": random.choice([
            f"Прекрасно! Итак, бронирование подтверждено: столик на {guest_count_spelled(n)} гостей, {date}, {hall}. Бронь на имя {name}. Ждём вас!",
            f"Всё записала! Столик на {guest_count_spelled(n)} в {hall}, {date}. Бронь на имя {name}. Если что-то изменится, позвоните заранее. Ждём вас!",
        ])})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    elif variant == 2:
        # User unsure about time
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здрасте, хотел столик забронировать, но время не знаю точно",
            f"Добрый день, мне нужен столик {date}, но со временем пока не определился",
            f"Привет, можно бронь? {pick_guest(n)}, {date}, но время точно не скажу",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Конечно, помогу! Вы планируете обед или ужин?",
            "Без проблем! Вам удобнее в обеденное время или вечером?",
            "Хорошо! Подскажите, примерно на какое время ориентируетесь — обед или ужин?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Вечером, наверное, часов в семь-восемь",
            "Лучше вечер, ближе к семи",
            "На ужин, где-то в районе восьми",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Отлично! На {date} в {time_f} свободен столик в {hall}. Устроит?",
            f"Хорошо! На {date} в {time_f} есть столик на {guest_count_spelled(n)} гостей. Подойдёт?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, отлично, давайте", "Подходит, бронируйте", "Годится",
        ]))})

        convs.append({"role": "assistant", "content": "Замечательно! На чьё имя бронируем?"})
        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Спасибо, {name}! Бронирование подтверждено: столик на {guest_count_spelled(n)} гостей, {date}, {time_f}. Ждём вас!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    elif variant == 3:
        # Quick no-nonsense booking — user dumps everything at once
        convs.append({"role": "user", "content": naturalize(
            f"Столик {date}, {time_u}, {pick_guest(n)}, на имя {name}"
        )})

        convs.append({"role": "assistant", "content": random.choice([
            f"Принято! Столик на {guest_count_spelled(n)} гостей, {date}. Бронь на имя {name}. Оставьте контактный телефон.",
            f"Записываю: {date}, на {guest_count_spelled(n)} персон, {name}. Ваш номер телефона?",
        ])})

        phone = random_phone()
        convs.append({"role": "user", "content": naturalize(phone)})

        convs.append({"role": "assistant", "content":
            f"Спасибо! Бронирование подтверждено. Ждём вас, {name}!"})

        convs.append({"role": "user", "content": naturalize("Угу, спасибо")})
        convs.append({"role": "assistant", "content": "Всего доброго, до свидания!"})

    elif variant == 4:
        # Couple / romantic date
        n = 2
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, хочу забронировать столик на двоих на {date}, что-нибудь уютное",
            f"Добрый вечер, нужен романтический столик на двоих {date}",
            f"Привет, столик на двоих {date}, желательно у окна",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Замечательно! У нас есть прекрасные столики для двоих — у окна и в каминном зале. На какое время?",
            "С радостью! Для романтического ужина могу предложить столик у окна со свечами. Во сколько?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"Часов в восемь вечера")})

        convs.append({"role": "assistant", "content": random.choice([
            "Столик у окна на двоих в двадцать часов свободен. Хотите, подготовим свечи?",
            "Отличный выбор! В двадцать часов есть столик у панорамного окна. Оформление свечами — бесплатно.",
        ])})

        if random.random() < 0.6:
            convs.append({"role": "user", "content": naturalize("Да, было бы здорово, свечи — это супер")})
            convs.append({"role": "assistant", "content": "Обязательно подготовим! На чьё имя бронируем?"})
        else:
            convs.append({"role": "user", "content": naturalize("Нет спасибо, просто столик")})
            convs.append({"role": "assistant", "content": "Хорошо. На чьё имя оформить бронь?"})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})
        convs.append({"role": "assistant", "content":
            f"Готово! Столик на двоих у окна, {date}, двадцать часов. Бронь на имя {name}. Приятного вечера!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    else:
        # Family dinner with kids
        n = random.choice([4, 5, 6, 7])
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Хотим прийти всей семьёй, {pick_guest(n)}, {date}. С нами будут дети",
            f"Нужен столик для семьи, {pick_guest(n)}, двое из них дети",
            f"Бронь нужна {date}, нас {pick_guest(n)} с детьми",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Будем рады видеть всю семью! Подскажите возраст детей — подготовим стульчики и детское меню.",
            "С удовольствием! Сколько деток и какого возраста? Мы можем предложить детское меню и раскраски.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Двое, пять и восемь лет", "Один ребёнок, три года",
            "Малыш два годика и старший десять",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Отлично, подготовим всё! Детское меню от четырёхсот рублей. Во сколько вас ждать?"})

        convs.append({"role": "user", "content": naturalize(f"Давайте часов в шесть")})

        convs.append({"role": "assistant", "content":
            f"Бронирую столик на {guest_count_spelled(n)} гостей, {date}, восемнадцать часов. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! Столик забронирован, детские стульчики и раскраски будут на месте. Ждём!"})

    return convs


# ─── 2. Booking with occasion (60) ───

def gen_occasion_booking():
    n = random.choice([4, 5, 6, 8, 10, 12, 15])
    date = pick_date()
    name = pick_name()
    occasion = random.choice(OCCASIONS[:8])  # main occasions
    req1 = random.choice(SPECIAL_REQUESTS)
    req2 = random.choice([r for r in SPECIAL_REQUESTS if r != req1])

    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Birthday / anniversary with cake and decorations
        bday_name = pick_name()
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Хочу организовать {occasion} для {bday_name}, {date}, нас будет {pick_guest(n)}",
            f"У {'мужа' if bday_name in NAMES_MALE else 'подруги'} {occasion} {date}, хочу сделать сюрприз, {pick_guest(n)}",
            f"Планирую отметить {occasion}, {date}, {pick_guest(n)}, нужен торт и украшения",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Как замечательно! С удовольствием поможем! Для {guest_count_spelled(n)} гостей предлагаю {pick_hall()}. Нужен ли торт и оформление зала?",
            f"Прекрасный повод! Мы обожаем организовывать праздники. Торт от нашего кондитера — от двух тысяч пятисот рублей за килограмм. Какие пожелания по оформлению?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Да, {req1} и {req2}, пожалуйста",
            f"Торт килограмма на два и {req1}",
            f"Нужен торт шоколадный и {req1}, больше ничего",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Записываю! {req1.capitalize()} и торт подготовим. Стоимость оформления — от пяти тысяч рублей. Во сколько планируете прийти?",
            f"Прекрасно! Всё организуем. Наш декоратор подготовит зал за час до прихода. На какое время бронируем?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"{pick_time()}")})

        convs.append({"role": "assistant", "content":
            f"Отлично! На чьё имя оформить бронирование?"})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})

        phone_exchange(name, convs)

        convs.append({"role": "assistant", "content":
            f"Бронирование подтверждено: {occasion}, {date}, {guest_count_spelled(n)} гостей, на имя {name}. Торт и оформление подготовим. Будет незабываемый праздник!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    elif variant == 2:
        # Occasion + asking about cake options
        convs.append({"role": "user", "content": naturalize(
            f"Здравствуйте, у нас {occasion} {date}, нас {pick_guest(n)}, а торт у вас можно заказать?"
        )})

        convs.append({"role": "assistant", "content": random.choice([
            "Конечно! Наш кондитер готовит на заказ — шоколадный, ягодный, чизкейк, медовик. Стоимость от двух тысяч рублей за килограмм. Какой торт вам ближе?",
            "Да, безусловно! Торты у нас от собственного кондитера. Есть классические и авторские варианты. Стоимость от двух тысяч пятисот рублей за килограмм. Что предпочитаете?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Давайте шоколадный, килограмма на три",
            "Ягодный, два кило наверное",
            "А что посоветуете? На ваш выбор",
        ]))})

        if "на ваш выбор" in convs[-1]["content"].lower() or "посоветуете" in convs[-1]["content"].lower():
            convs.append({"role": "assistant", "content":
                "Рекомендую наш фирменный ягодный торт — он пользуется большой популярностью. На сколько гостей нужен?"})
            convs.append({"role": "user", "content": naturalize(f"Нас {pick_guest(n)}, значит побольше")})
            convs.append({"role": "assistant", "content":
                f"Поняла, для {guest_count_spelled(n)} гостей закажу торт на три килограмма. На чьё имя бронь?"})
        else:
            convs.append({"role": "assistant", "content":
                f"Отличный выбор! Записываю торт. На чьё имя бронируем, {date}, {guest_count_spelled(n)} гостей?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! Бронирование и торт подтверждены на {date}. Хорошего праздника!"})

    else:
        # Occasion + asking about flowers and special decor
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, хочу отметить {occasion} {date}, можно ли у вас заказать цветы на стол и украшения?",
            f"Добрый день, мы планируем {occasion}, {pick_guest(n)}, {date}. Хочется чтобы было красиво оформлено",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Конечно! У нас есть несколько пакетов оформления. Базовый — свечи и цветы на стол за три тысячи рублей. Премиум — шары, фотозона и именная табличка за восемь тысяч. Какой вам ближе?",
            f"С удовольствием оформим! Расскажите, что представляете — свечи, цветы, шары? Можем подготовить любой вариант.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Базовый подойдёт, свечи и цветы — то что надо",
            "Давайте премиум, хочется чтобы всё было идеально",
            "А можно свечи и шары, без фотозоны?",
        ]))})

        convs.append({"role": "assistant", "content":
            "Конечно, подберём под ваши пожелания! На какое время и на чьё имя бронируем?"})

        convs.append({"role": "user", "content": naturalize(f"{pick_time()}, на {name}")})

        convs.append({"role": "assistant", "content":
            f"Записала! {occasion.capitalize()}, {date}, {guest_count_spelled(n)} гостей, бронь на имя {name}. Оформление подготовим. Ждём вас!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    return convs


# ─── 3. Large group / banquet / corporate (60) ───

def gen_large_group():
    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Big banquet with menu selection
        n = random.choice([15, 20, 25, 30, 40, 50])
        date = pick_date()
        name = pick_name()
        occasion = random.choice(OCCASIONS)
        budget = random.choice([2500, 3000, 3500, 4000, 5000, 7000])

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Хотим организовать {occasion}, {pick_guest(n)}, {date}",
            f"Нужен банкетный зал на {occasion}, нас {pick_guest(n)}",
            f"Планируем {occasion} {date}, нужно место на {pick_guest(n)}",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"С удовольствием поможем организовать {occasion}! Наш банкетный зал вмещает до шестидесяти гостей. Какой бюджет на персону вы рассматриваете?",
            f"Прекрасный повод! Для {guest_count_spelled(n)} гостей идеально подойдёт банкетный зал. У нас несколько вариантов меню. Какой бюджет рассматриваете?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Где-то {budget} рублей на человека",
            f"Хотели бы уложиться в {budget} на персону",
            f"Рассчитываем примерно {budget} рублей с человека",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Отлично! За {spell_thousands(budget // 1000)} рублей на персону подготовим банкетное меню: холодные и горячие закуски, основное блюдо, десерт и напитки. Нужны ли дополнительные услуги — проектор, микрофон, оформление?"})

        if random.random() < 0.6:
            req = random.choice(SPECIAL_REQUESTS)
            convs.append({"role": "user", "content": naturalize(f"Да, нужен {req}")})
            convs.append({"role": "assistant", "content":
                f"Конечно! {req.capitalize()} организуем. Включу в расчёт. На чьё имя оформляем?"})
        else:
            convs.append({"role": "user", "content": naturalize("Нет, пока ничего дополнительного")})
            convs.append({"role": "assistant", "content": "Хорошо! На чьё имя оформляем бронирование?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        phone_exchange(name, convs)

        convs.append({"role": "assistant", "content":
            f"Бронирование подтверждено: банкетный зал, {date}, {guest_count_spelled(n)} гостей, на имя {name}. Наш менеджер свяжется для обсуждения деталей меню и предоплаты."})

    elif variant == 2:
        # Corporate event with equipment
        n = random.choice([15, 20, 25, 30])
        date = pick_date()
        name = pick_name()
        company = random.choice(["Технолоджи", "ИнноСофт", "АльфаГруп", "МедиаПлюс", "СтройИнвест", "ВебТек", "ФинансПро"])

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Нам нужно провести корпоратив, {pick_guest(n)}, нужен проектор и микрофон",
            f"Планируем корпоративное мероприятие на {pick_guest(n)}, {date}",
            f"Ищем площадку для корпоратива, человек {n}",
        ]))})

        convs.append({"role": "assistant", "content":
            f"С удовольствием! Наш банкетный зал оборудован проектором, экраном и аудиосистемой. Какой формат — фуршет или банкет?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Банкет, чтобы все сидели", "Лучше фуршет, удобнее для общения",
            "Банкет, и нужно чтобы проектор работал",
        ]))})

        budget_corp = random.choice([3000, 3500, 4000, 5000])
        convs.append({"role": "assistant", "content":
            f"Отлично! Корпоративное меню от двух тысяч пятисот рублей на персону. Есть премиум-вариант за четыре тысячи. Какой бюджет?"})

        convs.append({"role": "user", "content": naturalize(f"Давайте за {budget_corp} на человека")})

        convs.append({"role": "assistant", "content":
            f"Прекрасно! Аренда зала и оборудования при заказе банкета — бесплатно. На чьё имя и компанию оформляем?"})

        convs.append({"role": "user", "content": naturalize(f"{name}, компания «{company}»")})

        convs.append({"role": "assistant", "content":
            f"Спасибо, {name}! Бронирование зафиксировано. Менеджер свяжется в течение рабочего дня для обсуждения деталей. Всего доброго!"})

    else:
        # Large friend group
        n = random.choice([8, 10, 12, 15, 20])
        date = pick_date()
        name = pick_name()

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Нас большая компания, {pick_guest(n)}, хотим {date} посидеть",
            f"Можно забронировать на большую компанию? Человек {n}, {date}",
            f"Нужен стол на {pick_guest(n)}, {date}, встреча друзей",
        ]))})

        hall_rec = random.choice(["банкетный зал", "второй этаж", "VIP-зал"])
        convs.append({"role": "assistant", "content":
            f"Замечательно! Для {guest_count_spelled(n)} гостей рекомендую {hall_rec}. На какое время?"})

        convs.append({"role": "user", "content": naturalize(f"{pick_time()}")})

        if n >= 10:
            convs.append({"role": "assistant", "content":
                "Для компании от десяти человек у нас есть сет-меню от двух тысяч рублей на персону. Или можно заказать по основному меню. Как удобнее?"})

            convs.append({"role": "user", "content": naturalize(random.choice([
                "По основному меню, каждый сам выберет",
                "Лучше сет-меню, так проще",
                "Можно часть общие закуски, а горячее — каждый сам?",
            ]))})

            convs.append({"role": "assistant", "content":
                "Конечно! Мы гибко подходим к заказам для больших компаний. На чьё имя бронируем?"})
        else:
            convs.append({"role": "assistant", "content":
                "Отлично! Столик подберём просторный. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})

        phone_exchange(name, convs)

        convs.append({"role": "assistant", "content":
            f"Бронирование подтверждено: {date}, {guest_count_spelled(n)} гостей, на имя {name}. Если количество изменится, дайте знать заранее. Ждём!"})

    return convs


# ─── 4. Cancellation (40) ───

def gen_cancellation():
    name = pick_name()
    date_old = random.choice(["на завтра", "на пятницу", "на субботу", "на воскресенье", "на сегодня вечером"])
    reason = random.choice(CANCEL_REASONS)

    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Simple cancel, offer reschedule, user declines
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Мне нужно отменить бронирование {date_old}, на имя {name}",
            f"У меня бронь {date_old}, хочу отменить. {name}",
            f"Я бронировал столик {date_old}, но не получится прийти",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Здравствуйте! Вижу бронирование на имя {name}. Жаль, что не получается. Могу отменить. Может, перенесём на другой день?",
            f"Добрый день, {name}! Нашла вашу бронь. Могу я узнать причину? Возможно, получится перенести?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Нет, просто отмените, {reason}",
            "Нет, к сожалению, отменяйте",
            f"Пока нет, у нас {reason}, отменяйте",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Понимаю, бывает. Бронирование отменено. Будем рады видеть вас в другой раз, {name}!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": "Пожалуйста! Всего доброго, до свидания!"})

    elif variant == 2:
        # Cancel, then agree to reschedule
        date_new = pick_date()
        convs.append({"role": "user", "content": naturalize(
            f"Добрый день, у меня бронь {date_old}, {name}. Нужно отменить, {reason}"
        )})

        convs.append({"role": "assistant", "content":
            f"Здравствуйте, {name}! Вижу бронь. Жаль это слышать. Хотите, перенесём на другую дату? Бронь сохранится."})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"А можно на {date_new}?",
            f"Давайте {date_new}, в то же время",
            f"Хорошая идея, перенесите на {date_new}",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Конечно! Переношу на {date_new}, все условия сохраняются. Подтверждаю перенос, {name}. Ждём вас!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    else:
        # Banquet cancel with deposit discussion
        convs.append({"role": "user", "content": naturalize(
            f"Мне очень неудобно, но нужно отменить банкет {date_old}. На имя {name}"
        )})

        convs.append({"role": "assistant", "content":
            f"Здравствуйте, {name}. Вижу бронирование банкетного зала. При отмене менее чем за трое суток мы не можем вернуть депозит полностью. Возвращаем пятьдесят процентов, или можно перенести с сохранением всей суммы. Что предпочитаете?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Давайте перенесём лучше", "А на когда свободные даты?",
            "Пятьдесят процентов... ну ладно, перенесём тогда",
        ]))})

        date_new = pick_date()
        convs.append({"role": "assistant", "content":
            f"Ближайшие свободные даты — {pick_date()} и {pick_date()}. Какая удобнее?"})

        convs.append({"role": "user", "content": naturalize(f"Давайте {date_new}")})

        convs.append({"role": "assistant", "content":
            f"Готово! Банкет перенесён на {date_new}. Депозит сохраняется. {name}, если будут изменения по меню, позвоните за неделю."})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    return convs


# ─── 5. Reschedule (40) ───

def gen_reschedule():
    name = pick_name()
    date_old = random.choice(["на завтра", "на пятницу", "на субботу", "на воскресенье"])
    date_new = pick_date()

    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Change date only
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, у меня бронь {date_old}, {name}. Хочу перенести на {date_new}",
            f"Добрый день, бронировал {date_old}, нужно перенести. Можно на {date_new}?",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Здравствуйте, {name}! Нашла вашу бронь. {date_new.capitalize()} свободно. Время и количество гостей без изменений?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, всё остальное то же", "Всё без изменений, только дата",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Готово! Бронирование перенесено на {date_new}. Все остальные условия сохранены. Ждём вас, {name}!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    elif variant == 2:
        # Change guest count
        n_old = random.choice([2, 4, 6])
        n_new = n_old + random.choice([1, 2, 3])
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"У меня бронь {date_old} на {guest_count_spelled(n_old)}, {name}. Нас теперь будет больше",
            f"Бронировал {date_old} столик, количество гостей изменилось",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Здравствуйте! Вижу вашу бронь. Сколько гостей теперь будет?"})

        convs.append({"role": "user", "content": naturalize(f"Теперь нас {pick_guest(n_new)}")})

        convs.append({"role": "assistant", "content": random.choice([
            f"Хорошо, для {guest_count_spelled(n_new)} гостей подберём стол побольше. Дата и время без изменений?",
            f"Принято! Увеличиваю до {guest_count_spelled(n_new)} гостей. Время прежнее?",
        ])})

        convs.append({"role": "user", "content": naturalize("Да, время то же")})

        convs.append({"role": "assistant", "content":
            f"Отлично, бронирование обновлено! {name}, ждём вас!"})

    else:
        # Change both date and time
        convs.append({"role": "user", "content": naturalize(
            f"Здравствуйте, бронь {date_old} на {name}. Нужно поменять и дату, и время"
        )})

        convs.append({"role": "assistant", "content":
            f"Конечно, {name}! На какую дату и время хотите перенести?"})

        time_new = pick_time()
        convs.append({"role": "user", "content": naturalize(f"На {date_new}, {time_new}")})

        convs.append({"role": "assistant", "content":
            f"Проверяю... {date_new} свободно! Переношу бронирование. Количество гостей прежнее?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, всё то же", "Количество не меняется",
            f"Нет, добавится ещё пара человек, нас теперь {pick_guest(random.choice([4, 5, 6]))}",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Записала! Бронь обновлена: {date_new}. {name}, ждём вас!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    return convs


# ─── 6. Time unavailable → alternatives (40) ───

def gen_time_unavailable():
    n = random.choice([2, 2, 3, 4, 4, 6])
    date = pick_date()
    name = pick_name()
    time_wanted = pick_time()
    alt1 = random.choice(TIMES_FORMAL)
    alt2 = random.choice([t for t in TIMES_FORMAL if t != alt1])

    variant = random.randint(1, 2)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # User picks from alternatives
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Хочу столик {date} {time_wanted}, {pick_guest(n)}",
            f"Бронь нужна {date} {time_wanted} на {pick_guest(n)}",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"К сожалению, на {time_wanted} все столики заняты. Могу предложить {alt1} или {alt2}. Какое время удобнее?",
            f"Увы, это время уже занято. Есть свободные столики на {alt1} и {alt2}. Подойдёт?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Давайте {alt1}", f"На {alt2} подойдёт",
            f"Ну ладно, тогда {alt1}",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Отлично! Бронирую на {guest_count_spelled(n)} гостей, {date}. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! Столик забронирован. Ждём вас!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    else:
        # User doesn't like alternatives, picks another day
        date2 = pick_date()
        while date2 == date:
            date2 = pick_date()

        convs.append({"role": "user", "content": naturalize(
            f"Нужен столик {date} {time_wanted}, {pick_guest(n)}"
        )})

        convs.append({"role": "assistant", "content":
            f"К сожалению, {date} на это время все столики заняты. Ближайшее свободное — {alt1}. Или можем посмотреть другую дату. Что удобнее?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Нет, {alt1} не подходит. А на {date2} есть?",
            f"Хм, тогда лучше {date2}, в то же время",
            f"Давайте на другой день, {date2}",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Проверяю... Да, {date2} свободно! Бронирую на {guest_count_spelled(n)} гостей. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})

        convs.append({"role": "assistant", "content":
            f"Замечательно! Столик забронирован: {date2}, {guest_count_spelled(n)} гостей, на имя {name}. Ждём вас!"})

        convs.append({"role": "user", "content": farewell_user()})
        convs.append({"role": "assistant", "content": farewell_assistant()})

    return convs


# ─── 7. Menu / allergy / diet + booking (40) ───

def gen_menu_allergy():
    name = pick_name()
    allergy = random.choice(ALLERGIES)
    diet = random.choice(DIET_TYPES)
    n = random.choice([2, 2, 3, 4])
    date = pick_date()

    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Allergy question → booking
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Скажите, у вас есть блюда без {allergy}? У меня аллергия",
            f"А в вашем меню есть что-то без {allergy}? Мне это важно",
            f"У меня аллергия на {allergy}, можно ли у вас поесть?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Конечно! Мы серьёзно относимся к аллергиям. У нас отмечены все аллергены, и повар готовит блюда без {allergy}. Около десяти позиций доступно. Хотите забронировать столик?",
            f"Да, безусловно! Наш шеф-повар адаптирует блюда под ваши пожелания. Без {allergy} доступны салаты, горячие и десерты. Планируете нас посетить?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Да, давайте, на {pick_guest(n)}, {date}",
            "Да, забронируйте, пожалуйста",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Отлично! На какое время?"})

        convs.append({"role": "user", "content": naturalize(f"{pick_time()}")})

        convs.append({"role": "assistant", "content":
            f"Записала! Столик на {guest_count_spelled(n)} гостей. Отмечу аллергию на {allergy}, кухня будет в курсе. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Спасибо, {name}! Бронирование подтверждено. Предупредим кухню. Ждём вас!"})

    elif variant == 2:
        # Diet question + booking
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, у вас есть {diet}?",
            f"Мне нужно узнать, есть ли {diet}, у меня ограничения по питанию",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Здравствуйте! Да, у нас есть {diet}. Наш шеф-повар уделяет этому внимание. Могу перечислить подходящие позиции.",
            f"Конечно! {diet.capitalize()} — это отдельный раздел нашего меню. Есть салаты, горячие блюда и десерты. Рассказать подробнее?",
        ])})

        convs.append({"role": "user", "content": naturalize("Да, расскажите, что есть")})

        menu_items = random.choice([
            "салат с рукколой и авокадо, крем-суп из тыквы, стейк из лосося с овощами и ягодный сорбет",
            "овощной салат, грибной крем-суп, паста с овощами и панна-котта на кокосовом молоке",
            "капрезе с моцареллой, минестроне, дорадо на гриле и фруктовый десерт",
        ])

        convs.append({"role": "assistant", "content":
            f"Рекомендую: {menu_items}. Средний чек — от полутора тысяч рублей. Хотите забронировать столик?"})

        convs.append({"role": "user", "content": naturalize(f"Да, на {pick_guest(n)}, {date}")})

        convs.append({"role": "assistant", "content": f"На какое время?"})

        convs.append({"role": "user", "content": naturalize(f"{pick_time()}")})

        convs.append({"role": "assistant", "content":
            f"Записала! На чьё имя бронь?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Спасибо, {name}! Бронирование подтверждено, кухня будет предупреждена о ваших пожеланиях. Ждём!"})

    else:
        # Kids menu question + booking
        convs.append({"role": "user", "content": naturalize(random.choice([
            "А у вас есть детское меню? Мы с ребёнком хотим прийти",
            "Подскажите, для детей что-то есть у вас?",
        ]))})

        convs.append({"role": "assistant", "content":
            "Конечно! Детское меню включает пасту, куриные котлетки, пюре, блинчики и соки. Стоимость от четырёхсот рублей. Сколько лет ребёнку?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Пять лет", "Семь, уже всё ест", "Три годика",
        ]))})

        convs.append({"role": "assistant", "content":
            "Замечательно! У нас есть детские стульчики и раскраски. Хотите забронировать столик?"})

        convs.append({"role": "user", "content": naturalize(f"Да, {date}, {pick_time()}, на {pick_guest(n)}")})

        convs.append({"role": "assistant", "content":
            f"Записала! На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! Столик на {guest_count_spelled(n)} гостей, детское меню подготовим. Ждём вашу семью!"})

    return convs


# ─── 8. Unclear/vague request → clarification (30) ───

def gen_unclear_request():
    name = pick_name()

    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # User doesn't know what they want
        convs.append({"role": "user", "content": naturalize(random.choice([
            "Здрасте, эм, мы хотели бы к вам прийти, но пока не знаю точно когда и сколько нас",
            "Привет, слушайте, я хотел бы бронь, но ещё не определился с деталями",
            "Добрый день, нам нужен столик... но я пока не знаю на сколько человек",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Здравствуйте! Без проблем, давайте разберёмся вместе. Вы планируете прийти вдвоём или компанией?",
            "Добрый день! Ничего страшного, помогу определиться. Примерно сколько вас может быть — двое, трое, больше?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Ну наверное человека четыре-пять, может шесть",
            "Нас трое точно, может ещё кто присоединится",
            "Пока не знаю, может двое, может четверо",
        ]))})

        n = random.choice([4, 5, 6])
        convs.append({"role": "assistant", "content":
            f"Хорошо, забронирую на {guest_count_spelled(n)} гостей с возможностью расширения. На какую дату рассматриваете?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Ну на выходные наверное... суббота или воскресенье",
            "Где-то на этой неделе, не знаю точно",
            "Либо в пятницу, либо в субботу",
        ]))})

        date = pick_date()
        convs.append({"role": "assistant", "content":
            f"Рекомендую {date} — есть хорошие столики. Обед или ужин?"})

        convs.append({"role": "user", "content": naturalize("Ужин, часов в семь наверное")})

        convs.append({"role": "assistant", "content":
            f"Отлично! Бронирую столик на {guest_count_spelled(n)} гостей, {date}, девятнадцать часов. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Записала, {name}! Если количество гостей уточнится, просто позвоните. Ждём вас!"})

    elif variant == 2:
        # User just says "нужен столик" with no details
        convs.append({"role": "user", "content": naturalize(random.choice([
            "Столик нужен", "Мне бы бронь", "Хочу забронировать",
        ]))})

        convs.append({"role": "assistant", "content":
            "Конечно! Подскажите, на какую дату и сколько гостей будет?"})

        n = random.choice([2, 3, 4])
        date = pick_date()
        convs.append({"role": "user", "content": naturalize(f"Ну {date}, {pick_guest(n)}")})

        convs.append({"role": "assistant", "content": "Отлично! На какое время?"})

        convs.append({"role": "user", "content": naturalize(f"{pick_time()}")})

        convs.append({"role": "assistant", "content":
            f"Замечательно! Столик на {guest_count_spelled(n)} гостей, {date}. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Бронь подтверждена, {name}! Ждём вас."})

    else:
        # User asks "а что у вас есть?" — needs guidance
        convs.append({"role": "user", "content": naturalize(random.choice([
            "Здрасте, а что у вас вообще есть? Мы хотим куда-нибудь сходить",
            "Привет, расскажите вообще про ваш ресторан, что у вас интересного",
            "Добрый день, а чё у вас?",
        ]))})

        cuisine = random.choice(CUISINES)
        convs.append({"role": "assistant", "content":
            f"Здравствуйте! У нас ресторан {cuisine}й кухни. Уютная атмосфера, несколько залов — основной, каминный и VIP. Средний чек — от двух до трёх тысяч рублей. Вы планируете ужин или обед?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Ну ужин наверное, вдвоём хотим", "Обед, нас трое будет",
            "Вечером, компанией",
        ]))})

        n = random.choice([2, 3, 4])
        convs.append({"role": "assistant", "content":
            f"Отлично! На какую дату забронировать?"})

        date = pick_date()
        convs.append({"role": "user", "content": naturalize(f"На {date}")})

        convs.append({"role": "assistant", "content":
            f"Замечательно! Столик на {guest_count_spelled(n)} гостей, {date}. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! Ждём вас, будем рады!"})

    return convs


# ─── 9. User changes mind mid-dialog (30) ───

def gen_changes_mind():
    name = pick_name()
    date = pick_date()

    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Changes time
        time1 = pick_time()
        time2 = pick_time()
        while time2 == time1:
            time2 = pick_time()
        n = random.choice([2, 3, 4, 5])

        convs.append({"role": "user", "content": naturalize(
            f"Столик {date} {time1}, {pick_guest(n)}"
        )})

        convs.append({"role": "assistant", "content":
            f"Конечно! Бронирую столик на {guest_count_spelled(n)} гостей, {date}. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Подождите, нет, давайте лучше {time2}",
            f"Ой, я передумал, лучше {time2}",
            f"Стоп, {time2} будет удобнее",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Без проблем! Меняю время. {date}, столик на {guest_count_spelled(n)} гостей. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Записала, {name}! Бронирование подтверждено. Ждём вас!"})

    elif variant == 2:
        # Changes guest count
        n1 = random.choice([2, 3, 4])
        n2 = n1 + random.choice([2, 3, 4])

        convs.append({"role": "user", "content": naturalize(
            f"Бронь {date}, {pick_guest(n1)}, {pick_time()}"
        )})

        convs.append({"role": "assistant", "content":
            f"Записываю! Столик на {guest_count_spelled(n1)} гостей, {date}. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Ой, подождите, нас не {spell_number(n1)}, нас {pick_guest(n2)}",
            f"Секунду, жена написала — нас теперь {pick_guest(n2)}",
            f"Стоп, поменялось, нас {pick_guest(n2)} будет",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Поняла, меняю на {guest_count_spelled(n2)} гостей. Подберу стол побольше. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! Столик на {guest_count_spelled(n2)}, {date}. Ждём!"})

    else:
        # Completely changes mind — cancels mid-booking
        n = random.choice([2, 4, 6])

        convs.append({"role": "user", "content": naturalize(
            f"Нужен столик {date}, {pick_guest(n)}, {pick_time()}"
        )})

        convs.append({"role": "assistant", "content":
            f"Конечно! На {guest_count_spelled(n)} гостей, {date}. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Нет, я передумал, извините, не нужно",
            "Ой, подождите, мне перезвонили, пока не надо",
            "Знаете, давайте отложим, я перезвоню позже",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Конечно, не проблема! Будем рады, когда определитесь. Звоните в любое время.",
            "Ничего страшного! Когда будете готовы — звоните, мы всегда на связи. Хорошего дня!",
        ])})

        convs.append({"role": "user", "content": naturalize("Спасибо, до свидания")})
        convs.append({"role": "assistant", "content": "До свидания! Хорошего дня!"})

    return convs


# ─── 10. VIP/private room (20) ───

def gen_vip_request():
    n = random.choice([2, 4, 6, 8])
    date = pick_date()
    name = pick_name()

    variant = random.randint(1, 2)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # VIP room request with premium pricing
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Нужен VIP-зал, {date}, {pick_guest(n)}, чтобы было приватно",
            f"Хочу арендовать отдельный кабинет, {pick_guest(n)}, {date}",
            f"Нам бы приватную комнату {date}, важная встреча",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Конечно! Наш VIP-зал рассчитан на восемь-двенадцать гостей. Полная приватность, отдельный вход, персональный официант. Минимальный депозит — пятнадцать тысяч рублей, который засчитывается в счёт. На какое время?",
            f"С удовольствием! VIP-кабинет — уютная обстановка, звукоизоляция, отдельное обслуживание. Аренда — десять тысяч рублей, входит в общий счёт при заказе от этой суммы. Во сколько вас ждать?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"{pick_time()}")})

        # User asks about price mid-flow
        if random.random() < 0.5:
            convs.append({"role": "user", "content": naturalize("А сколько примерно выйдет на всех?")})
            total = n * random.choice([3000, 4000, 5000])
            convs.append({"role": "assistant", "content":
                f"При среднем чеке три-пять тысяч рублей на гостя, для {guest_count_spelled(n)} персон выйдет примерно {spell_thousands(total // 1000)} рублей. Депозит засчитается."})
            convs.append({"role": "user", "content": naturalize("Нормально, бронируйте")})

        convs.append({"role": "assistant", "content": "На чьё имя оформить бронирование?"})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})

        phone_exchange(name, convs)

        convs.append({"role": "assistant", "content":
            f"VIP-зал забронирован: {date}, {guest_count_spelled(n)} гостей, на имя {name}. Персональный официант будет к вашим услугам. Ждём вас!"})

    else:
        # Private room for business negotiation
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Нужен отдельный кабинет для деловых переговоров, {pick_guest(n)}, {date}",
            f"Есть у вас приватная комната? Деловая встреча, {pick_guest(n)}",
        ]))})

        convs.append({"role": "assistant", "content":
            f"Да, у нас есть VIP-кабинет — тишина, приватность, Wi-Fi, розетки для ноутбуков. Обслуживание ускоренное. Депозит — десять тысяч рублей. На какое время?"})

        convs.append({"role": "user", "content": naturalize(f"{date}, к часу дня, быстрое обслуживание важно")})

        convs.append({"role": "assistant", "content":
            "Понимаю! Можем заранее подготовить заказ, чтобы блюда были готовы к вашему приходу. Хотите воспользоваться?"})

        convs.append({"role": "user", "content": naturalize("Да, отличная идея")})

        convs.append({"role": "assistant", "content":
            "Замечательно! Наш бизнес-ланч: салат, суп и горячее — шестьсот пятьдесят рублей. Или можно по основному меню. Что предпочитаете?"})

        convs.append({"role": "user", "content": naturalize("Бизнес-ланч всем, быстрее будет")})

        convs.append({"role": "assistant", "content": f"Принято! На чьё имя?"})
        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! VIP-кабинет, {date}, тринадцать часов. Заказ будет готов к приходу. Продуктивной встречи!"})

    return convs


# ─── 11. Price inquiry only (20) ───

def gen_price_inquiry():
    variant = random.randint(1, 3)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Average check
        convs.append({"role": "user", "content": naturalize(random.choice([
            "Подскажите, какой у вас средний чек?",
            "Здрасте, а сколько стоит у вас поужинать?",
            "Добрый день, хотел узнать цены",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Здравствуйте! Средний чек — от двух до трёх тысяч рублей на гостя без алкоголя. Бизнес-ланч с двенадцати до пятнадцати — шестьсот пятьдесят рублей. Хотите забронировать столик?",
            "Добрый день! Средний чек у нас — от полутора до четырёх тысяч рублей, зависит от выбора блюд. Обеденное меню выгоднее. Хотите узнать подробнее?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Нет, спасибо, просто узнавал", "Понял, спасибо, подумаю",
            "А банкетное меню сколько?",
        ]))})

        if "банкетное" in convs[-1]["content"].lower():
            convs.append({"role": "assistant", "content":
                "Банкетное меню — от двух тысяч пятисот до семи тысяч рублей на персону, в зависимости от пакета. Включает закуски, горячее и десерт. Хотите, отправлю подробное меню?"})
            convs.append({"role": "user", "content": naturalize("Нет, пока достаточно, спасибо")})

        convs.append({"role": "assistant", "content":
            "Будем рады видеть вас! Если решите прийти, бронируйте заранее. Хорошего дня!"})

    elif variant == 2:
        # Deposit / corkage fee
        convs.append({"role": "user", "content": naturalize(random.choice([
            "Скажите, у вас есть депозит на столик?",
            "А можно своё вино принести? Пробковый сбор?",
            "Здрасте, сколько депозит на банкетный зал?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Здравствуйте! По будням депозита нет. В пятницу и субботу вечером депозит — две тысячи рублей на гостя, он засчитывается в счёт. Своё вино можно, пробковый сбор — триста рублей за бутылку.",
            "Добрый день! Депозит по выходным — от двух тысяч рублей на персону, входит в общий счёт. Банкетный зал — от двадцати тысяч. Пробковый сбор за свой алкоголь — триста рублей.",
        ])})

        convs.append({"role": "user", "content": naturalize("Понял, спасибо за информацию")})

        convs.append({"role": "assistant", "content":
            "Пожалуйста! Если будут вопросы, звоните. Хорошего дня!"})

    else:
        # Banquet pricing per person
        n = random.choice([15, 20, 30])
        convs.append({"role": "user", "content": naturalize(
            f"Подскажите, сколько выйдет банкет на {pick_guest(n)}?"
        )})

        budget_options = random.choice([
            ("два тысячи пятьсот", "четыре тысячи"),
            ("три тысячи", "пять тысяч"),
            ("две тысячи", "семь тысяч"),
        ])
        convs.append({"role": "assistant", "content":
            f"Здравствуйте! Банкетное меню от {budget_options[0]} до {budget_options[1]} рублей на персону. Для {guest_count_spelled(n)} гостей аренда зала бесплатна при заказе банкета. Хотите, расскажу подробнее о меню?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Пока нет, мы ещё думаем", "Да, расскажите",
        ]))})

        if "нет" in convs[-1]["content"].lower() or "думаем" in convs[-1]["content"].lower():
            convs.append({"role": "assistant", "content":
                "Конечно! Когда определитесь, звоните. Могу отправить подробное предложение на электронную почту."})
        else:
            convs.append({"role": "assistant", "content":
                "В базовый пакет входят холодные закуски, горячие закуски, основное блюдо и десерт. Премиум включает приветственный фуршет и расширенный выбор. Хотите забронировать дату?"})
            convs.append({"role": "user", "content": naturalize("Пока нет, перезвоним")})
            convs.append({"role": "assistant", "content":
                "Хорошо! Рекомендую не затягивать — популярные даты быстро занимают. Всего доброго!"})

    return convs


# ─── 12. Delivery/takeout redirect (10) ───

def gen_delivery_redirect():
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    convs.append({"role": "user", "content": naturalize(random.choice([
        "Здрасте, а у вас есть доставка?",
        "Можно заказать на дом?",
        "А вы делаете навынос?",
        "Добрый день, хочу заказать доставку еды",
        "Привет, а еду с собой можно взять?",
    ]))})

    convs.append({"role": "assistant", "content": random.choice([
        "Здравствуйте! К сожалению, мы принимаем только бронирования столиков. Для заказа доставки рекомендую обратиться через приложение или позвонить по номеру доставки: восемь восемьсот пятьсот двадцать тридцать. Могу ли помочь с бронированием?",
        "Добрый день! Наш ресторан работает только на обслуживание гостей в зале. Доставку можно оформить через наш сайт или приложение. Если хотите, могу забронировать столик для вас.",
    ])})

    convs.append({"role": "user", "content": naturalize(random.choice([
        "А, понял, нет, мне доставку надо, спасибо",
        "Жаль, ну ладно, спасибо",
        "Хм, а может тогда столик забронирую, давно хотел зайти",
    ]))})

    if "столик" in convs[-1]["content"].lower() or "зайти" in convs[-1]["content"].lower():
        n = random.choice([2, 3, 4])
        date = pick_date()
        name = pick_name()
        convs.append({"role": "assistant", "content":
            "Отлично! Будем рады! На какую дату и сколько гостей?"})
        convs.append({"role": "user", "content": naturalize(f"{date}, {pick_guest(n)}")})
        convs.append({"role": "assistant", "content": f"На какое время?"})
        convs.append({"role": "user", "content": naturalize(f"{pick_time()}")})
        convs.append({"role": "assistant", "content": f"Замечательно! На чьё имя?"})
        convs.append({"role": "user", "content": naturalize(f"{name}")})
        convs.append({"role": "assistant", "content":
            f"Бронь подтверждена, {name}! Ждём вас!"})
    else:
        convs.append({"role": "assistant", "content":
            "Пожалуйста! Будем рады видеть вас лично. Хорошего дня!"})

    return convs


# ─── 13. Aggressive/impatient customer (10) ───

def gen_aggressive_customer():
    name = pick_name()
    n = random.choice([2, 4, 6])
    date = pick_date()

    variant = random.randint(1, 2)
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    if variant == 1:
        # Impatient, wants fast service
        convs.append({"role": "user", "content": naturalize(random.choice([
            "Слушайте, мне быстро надо столик, нет времени на разговоры",
            "Короче, столик нужен, побыстрее можно?",
            "Ну сколько можно ждать, бронь нужна срочно",
        ]))})

        convs.append({"role": "assistant", "content":
            "Конечно, сейчас всё быстро оформим! На какую дату, время и сколько гостей?"})

        convs.append({"role": "user", "content": naturalize(
            f"{date}, {pick_time()}, {pick_guest(n)}, на имя {name}"
        )})

        convs.append({"role": "assistant", "content":
            f"Готово! Бронь подтверждена: {date}, на {guest_count_spelled(n)} гостей, {name}. Ждём вас!"})

        convs.append({"role": "user", "content": naturalize("Ну наконец-то, спасибо")})
        convs.append({"role": "assistant", "content": "Пожалуйста! Хорошего дня, до встречи!"})

    else:
        # Unhappy about something, model stays calm
        convs.append({"role": "user", "content": naturalize(random.choice([
            "Вы что, серьёзно? Почему в субботу нет мест? У вас всегда так?",
            "Это безобразие, я звоню третий раз и каждый раз занято",
            "Ну и порядки у вас, невозможно дозвониться и столик забронировать",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Понимаю ваше разочарование, приношу извинения за неудобства. Давайте я помогу найти удобное время. Какая дата и время вам подойдут?",
            "Мне очень жаль, что так получилось. Давайте подберём для вас лучший вариант прямо сейчас. На какую дату рассматриваете?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"Ну давайте {date}, {pick_time()}, {pick_guest(n)}")})

        convs.append({"role": "assistant", "content":
            f"Отлично, {date} есть свободный столик на {guest_count_spelled(n)} гостей! Бронирую. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content":
            f"Готово, {name}! Столик забронирован. Постараемся, чтобы ваш визит прошёл идеально. Ждём вас!"})

        convs.append({"role": "user", "content": naturalize("Ладно, спасибо")})
        convs.append({"role": "assistant", "content":
            "Спасибо за терпение! Хорошего дня, до встречи!"})

    return convs


# ─── Extra patterns: transfer to admin, "мне всё равно", price mid-booking ───

def gen_transfer_to_admin():
    """User asks to be connected to a human admin."""
    convs = [{"role": "system", "content": SYSTEM_PROMPT}]
    convs.append({"role": "assistant", "content": greeting()})

    convs.append({"role": "user", "content": naturalize(random.choice([
        "Соедините с администратором, пожалуйста",
        "Мне нужен живой человек, соедините",
        "Можно с менеджером поговорить?",
    ]))})

    convs.append({"role": "assistant", "content": random.choice([
        "Конечно! Сейчас переведу вас на администратора. Одну секунду, пожалуйста.",
        "Хорошо, соединяю с администратором. Пожалуйста, оставайтесь на линии.",
    ])})

    return convs


# ══════════════ Main generation ══════════════

def generate_all_dialogs(count=500):
    dialogs = []

    distribution = {
        'simple': 100,
        'occasion': 60,
        'large': 60,
        'cancel': 40,
        'reschedule': 40,
        'time_unavail': 40,
        'menu_allergy': 40,
        'unclear': 30,
        'changes_mind': 30,
        'vip': 20,
        'price': 20,
        'delivery': 10,
        'aggressive': 10,
    }

    total = sum(distribution.values())
    assert total == count, f"Distribution sums to {total}, expected {count}"

    generators = {
        'simple': gen_simple_booking,
        'occasion': gen_occasion_booking,
        'large': gen_large_group,
        'cancel': gen_cancellation,
        'reschedule': gen_reschedule,
        'time_unavail': gen_time_unavailable,
        'menu_allergy': gen_menu_allergy,
        'unclear': gen_unclear_request,
        'changes_mind': gen_changes_mind,
        'vip': gen_vip_request,
        'price': gen_price_inquiry,
        'delivery': gen_delivery_redirect,
        'aggressive': gen_aggressive_customer,
    }

    for category, num in distribution.items():
        gen = generators[category]
        for _ in range(num):
            convs = gen()
            dialogs.append({"conversations": convs})

    random.shuffle(dialogs)
    return dialogs


if __name__ == "__main__":
    dialogs = generate_all_dialogs(500)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restaurant_dialogs_v2.jsonl")

    with open(output_path, "w", encoding="utf-8") as f:
        for dialog in dialogs:
            line = json.dumps(dialog, ensure_ascii=False)
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
                assert len(obj["conversations"]) >= 4
                assert obj["conversations"][0]["role"] == "system"
                valid += 1
            except Exception as e:
                print(f"Invalid line {i+1}: {e}")
        print(f"Validation: {valid}/{len(lines)} valid lines")

    # Print first and last dialog
    print("\n=== FIRST DIALOG ===")
    first = json.loads(lines[0].strip())
    for turn in first["conversations"]:
        print(f"  [{turn['role']}]: {turn['content'][:120]}{'...' if len(turn['content']) > 120 else ''}")

    print("\n=== LAST DIALOG ===")
    last = json.loads(lines[-1].strip())
    for turn in last["conversations"]:
        print(f"  [{turn['role']}]: {turn['content'][:120]}{'...' if len(turn['content']) > 120 else ''}")

    print(f"\nTotal lines: {len(lines)}")
