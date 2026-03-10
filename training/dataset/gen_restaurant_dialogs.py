#!/usr/bin/env python3
"""Generate 400 SFT training dialogs for restaurant AI voice receptionist."""

import json
import random
import os

random.seed(42)

SYSTEM_PROMPT = "Вы — администратор ресторана. Помогаете гостям забронировать столик, выбрать зал и обсудить детали визита. Говорите вежливо, гостеприимно и профессионально."

# ---- Building blocks ----

NAMES_MALE = ["Александр", "Дмитрий", "Сергей", "Андрей", "Михаил", "Иван", "Максим", "Павел", "Артём", "Николай", "Владимир", "Олег", "Роман", "Евгений", "Алексей", "Виктор", "Константин", "Денис", "Игорь", "Тимур", "Руслан", "Борис", "Кирилл", "Антон", "Григорий"]
NAMES_FEMALE = ["Елена", "Анна", "Мария", "Ольга", "Наталья", "Татьяна", "Екатерина", "Ирина", "Светлана", "Юлия", "Дарья", "Алина", "Виктория", "Ксения", "Полина", "Марина", "Людмила", "Валентина", "Надежда", "Оксана", "Лариса", "Диана", "Кристина", "Вера", "Галина"]

FILLERS = ["ну", "эм", "так", "вот", "ааа", "короче", "слушайте", "значит", "это самое", "как бы", "ну вот", "в общем", "ну типа", "а", "ну это", "так сказать"]

DAYS = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"]
DAYS_NA = ["в понедельник", "во вторник", "в среду", "в четверг", "в пятницу", "в субботу", "в воскресенье"]

DATES_SPOKEN = [
    "завтра", "послезавтра", "в эту субботу", "в это воскресенье", "в пятницу",
    "на следующей неделе", "через неделю", "в эти выходные", "в ближайшую субботу",
    "третьего числа", "пятого марта", "десятого", "пятнадцатого", "двадцатого",
    "двадцать третьего", "тридцатого", "в следующую пятницу", "через два дня",
    "седьмого апреля", "первого мая", "двенадцатого июня", "на выходных",
    "в четверг на следующей неделе", "в ближайшее воскресенье"
]

TIMES = ["18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "12:00", "12:30", "13:00", "13:30", "14:00", "17:00", "17:30", "21:00", "15:00"]
TIMES_SPOKEN = [
    "в шесть", "часов в шесть", "к семи", "в семь", "в семь тридцать", "в восемь",
    "к восьми", "около семи", "часам к шести", "ну часов в семь", "в полседьмого",
    "к шести вечера", "в восемь вечера", "на семь", "в шесть тридцать",
    "ну где-то в семь", "часиков в шесть", "примерно в восемь", "к двенадцати",
    "в час дня", "в два", "на час", "около двух", "в полвторого", "к трём",
    "часа в три", "в пять вечера"
]

GUEST_COUNTS = [2, 2, 2, 3, 4, 4, 4, 5, 6, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 50]

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

HALLS = ["основной зал", "VIP-зал", "банкетный зал", "каминный зал", "зал у окна", "малый зал", "верхний зал", "уютный зал"]

CUISINES = ["европейская", "русская", "итальянская", "японская", "грузинская", "авторская", "средиземноморская", "паназиатская"]

ALLERGIES = ["орехи", "глютен", "лактоза", "морепродукты", "яйца", "мёд", "цитрусовые", "рыба"]

DIET_TYPES = ["вегетарианское меню", "веганское меню", "безглютеновое меню", "халяль", "кошерное меню", "детское меню", "постное меню", "диетическое меню"]

OCCASIONS = ["день рождения", "юбилей", "годовщина свадьбы", "помолвка", "выпускной", "повышение на работе", "встреча одноклассников", "новоселье"]

SPECIAL_REQUESTS = ["торт", "живая музыка", "украшение зала шарами", "фотозона", "проектор", "микрофон", "цветы на стол", "свечи", "именная табличка", "детский аниматор"]

NOISE_MARKERS = ["[неразборчиво]", "[шум]", "[помехи]", "[плохая связь]"]

PHONE_PREFIXES = ["восемь девять", "плюс семь девять", "восемь девятьсот"]


def add_filler(text, prob=0.4):
    """Add a filler word at the beginning with given probability."""
    if random.random() < prob:
        f = random.choice(FILLERS)
        # Sometimes capitalize filler, sometimes not
        if random.random() < 0.5:
            return f.capitalize() + ", " + text[0].lower() + text[1:]
        else:
            return f + ", " + text[0].lower() + text[1:]
    return text


def add_hesitation(text, prob=0.2):
    """Add hesitation mid-sentence."""
    if random.random() < prob:
        words = text.split()
        if len(words) > 3:
            pos = random.randint(1, min(len(words) - 2, 4))
            h = random.choice(["э...", "эм...", "ну...", "как его...", "это..."])
            words.insert(pos, h)
            return " ".join(words)
    return text


def add_noise(text, prob=0.05):
    """Add noise marker."""
    if random.random() < prob:
        marker = random.choice(NOISE_MARKERS)
        words = text.split()
        if len(words) > 2:
            pos = random.randint(0, len(words) - 1)
            words[pos] = marker
            return " ".join(words)
    return text


def naturalize(text):
    """Make user text more natural."""
    text = add_filler(text)
    text = add_hesitation(text)
    text = add_noise(text)
    # Randomly drop punctuation
    if random.random() < 0.3:
        text = text.replace(".", "").replace(",", " ").replace("  ", " ").strip()
    # Sometimes add trailing filler
    if random.random() < 0.15:
        text = text + " " + random.choice(["вот", "ну вот так", "да", "вот так", "типа того", "как-то так"])
    return text


def spell_number(n):
    """Spell out a number in Russian for assistant responses."""
    nums = {
        1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
        6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять",
        11: "одиннадцать", 12: "двенадцать", 13: "тринадцать", 14: "четырнадцать",
        15: "пятнадцать", 16: "шестнадцать", 17: "семнадцать", 18: "восемнадцать",
        19: "девятнадцать", 20: "двадцать", 25: "двадцать пять", 30: "тридцать",
        40: "сорок", 50: "пятьдесят", 60: "шестьдесят", 100: "сто",
    }
    return nums.get(n, str(n))


def spell_thousands(n):
    """Spell N thousand rubles with correct Russian grammar: 'две тысячи', 'пять тысяч' etc."""
    m = {
        1: "одну тысячу", 2: "две тысячи", 3: "три тысячи", 4: "четыре тысячи",
        5: "пять тысяч", 6: "шесть тысяч", 7: "семь тысяч", 8: "восемь тысяч",
        10: "десять тысяч", 12: "двенадцать тысяч", 15: "пятнадцать тысяч",
        20: "двадцать тысяч", 25: "двадцать пять тысяч", 30: "тридцать тысяч",
        40: "сорок тысяч", 50: "пятьдесят тысяч",
    }
    return m.get(n, f"{n} тысяч")


def guest_count_spelled(n):
    """Guest count for assistant in genitive/accusative context: 'двух', 'четырёх' etc.
    Works for both 'на X гостей' (accusative) and 'для X гостей' (genitive) since
    for numbers >= 5 the forms coincide, and for 2-4 we use the shared animate accusative=genitive form."""
    m = {
        2: "двух", 3: "трёх", 4: "четырёх", 5: "пять", 6: "шесть",
        7: "семь", 8: "восемь", 10: "десять", 12: "двенадцать",
        15: "пятнадцать", 20: "двадцать", 25: "двадцать пять",
        30: "тридцать", 40: "сорок", 50: "пятьдесят"
    }
    return m.get(n, str(n))


def random_phone():
    """Generate a spoken phone number."""
    digits = [str(random.randint(0, 9)) for _ in range(7)]
    return random.choice(PHONE_PREFIXES) + " " + "".join(digits[:3]) + " " + "".join(digits[3:5]) + " " + "".join(digits[5:])


def pick_time_spoken():
    return random.choice(TIMES_SPOKEN)

def pick_date_spoken():
    return random.choice(DATES_SPOKEN)

def pick_guest_spoken(n):
    return random.choice(GUEST_SPOKEN.get(n, [f"{n} человек"]))

def pick_hall():
    return random.choice(HALLS)

# ========== Dialog generators ==========

def gen_simple_booking():
    """Simple table booking (40%)."""
    n = random.choice([2, 2, 2, 3, 4, 4, 5, 6])
    date = pick_date_spoken()
    time = pick_time_spoken()
    name = random.choice(NAMES_MALE + NAMES_FEMALE)
    hall = pick_hall()

    templates = []

    # Template 1: straightforward booking
    def t1():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Greeting from assistant
        greetings = [
            "Добрый день! Ресторан «Белый сад», администратор слушает. Чем могу помочь?",
            "Здравствуйте! Ресторан «Олива», рады вашему звонку. Чем могу быть полезна?",
            "Добрый вечер! Ресторан «Террасса», слушаю вас.",
            "Здравствуйте! Ресторан «Бриз», администратор на связи. Чем могу помочь?",
            "Добрый день! Ресторан «Сказка», вас приветствует администратор. Слушаю вас.",
            "Алло, добрый день! Ресторан «Панорама». Чем могу помочь?",
        ]
        convs.append({"role": "assistant", "content": random.choice(greetings)})

        # User wants to book
        user_msgs = [
            f"Хотел бы забронировать столик {date} {time}, {pick_guest_spoken(n)}",
            f"Можно столик забронировать? {date}, {pick_guest_spoken(n)}, {time}",
            f"Бронь хочу сделать, {pick_guest_spoken(n)}, {date}",
            f"Здравствуйте, нужен столик {date} на вечер, {pick_guest_spoken(n)}",
            f"Добрый день, хотели бы зарезервировать столик {date} {time}",
            f"Привет, а можно столик {date}? {pick_guest_spoken(n)}",
        ]
        convs.append({"role": "user", "content": naturalize(random.choice(user_msgs))})

        # Assistant confirms and asks about hall
        hall_q = [
            f"Конечно! Столик на {guest_count_spelled(n)} гостей, {date}. Подскажите, есть ли предпочтения по залу? У нас есть {random.choice(HALLS)}, {random.choice(HALLS)} и {random.choice(HALLS)}.",
            f"С удовольствием помогу! Бронируем на {guest_count_spelled(n)} персон. Какой зал вы предпочитаете — {random.choice(HALLS)} или {random.choice(HALLS)}?",
            f"Отлично, записываю. На {guest_count_spelled(n)} гостей, {date}. Вам удобнее в {random.choice(HALLS)} или {random.choice(HALLS)}?",
        ]
        convs.append({"role": "assistant", "content": random.choice(hall_q)})

        # User picks hall
        user_hall = [
            f"Давайте в {hall}",
            f"В {hall}, пожалуйста",
            f"А что такое {hall}? Ну ладно, давайте туда",
            f"Нам бы {hall} подошёл",
            f"Лучше {hall}",
        ]
        convs.append({"role": "user", "content": naturalize(random.choice(user_hall))})

        # Assistant asks for name
        convs.append({"role": "assistant", "content": random.choice([
            f"Прекрасный выбор! {hall.capitalize()} — отличное место. На чьё имя оформить бронирование?",
            f"Замечательно, {hall} свободен в это время. Подскажите, пожалуйста, ваше имя для брони.",
            f"Хорошо, бронирую {hall}. Как я могу записать вас?",
        ])})

        # User gives name
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"На {name}", f"{name}", f"Запишите на {name}", f"Имя — {name}", f"На имя {name}, пожалуйста"
        ]))})

        # Assistant asks for phone
        convs.append({"role": "assistant", "content": random.choice([
            f"Спасибо, {name}! Подскажите, пожалуйста, контактный номер телефона для подтверждения бронирования.",
            f"Записала, {name}. Оставьте, пожалуйста, номер телефона на случай изменений.",
            f"Отлично, {name}! И последнее — ваш номер телефона для связи?",
        ])})

        phone = random_phone()
        convs.append({"role": "user", "content": naturalize(random.choice([
            phone, f"Да, {phone}", f"Номер {phone}", f"Запишите {phone}"
        ]))})

        # Confirmation
        convs.append({"role": "assistant", "content": random.choice([
            f"Прекрасно! Итак, подтверждаю бронирование: столик на {guest_count_spelled(n)} гостей, {date}, {hall}. Бронь на имя {name}. Ждём вас, хорошего дня!",
            f"Бронирование подтверждено! {hall.capitalize()}, на {guest_count_spelled(n)} персон, {date}. {name}, будем рады вас видеть!",
            f"Отлично, всё записала! Столик на {guest_count_spelled(n)} в {hall}, {date}. Бронь на имя {name}. Если что-то изменится, пожалуйста, позвоните нам заранее. Ждём вас!",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Спасибо большое!", "Спасибо, до свидания", "Отлично, спасибо", "Благодарю, ждите", "Спасибо, всего доброго"
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Благодарим за бронирование! Хорошего вам дня, до встречи!",
            "Спасибо за звонок! Ждём вас с нетерпением. До свидания!",
            "Всего доброго! Будем рады вас видеть!",
        ])})

        return convs

    # Template 2: user unsure about time
    def t2():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        greetings = [
            "Добрый день! Ресторан «Верона», администратор слушает.",
            "Здравствуйте! Ресторан «Каштан», чем могу помочь?",
            "Добрый вечер! Ресторан «Прага» на связи.",
        ]
        convs.append({"role": "assistant", "content": random.choice(greetings)})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здрасте, хотел бы столик забронировать, но не знаю точно во сколько",
            f"Добрый день, мне нужен столик {date}, но я пока не определился со временем",
            f"Привет, можно бронь? Нас будет {pick_guest_spoken(n)}, {date}, но время пока не точно",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Конечно, помогу определиться! На какое примерно время вы ориентируетесь — обед или ужин? У нас обеденное время с двенадцати до пятнадцати, а ужин — с восемнадцати до двадцати двух.",
            f"Без проблем! Давайте подберём удобное время. Вы планируете обед или ужин?",
            f"Хорошо, не проблема. Подскажите, вам удобнее в обеденное время или вечером?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Вечером, наверное, часов в семь-восемь",
            "Лучше вечер, ближе к семи",
            "На ужин, где-то в районе восьми",
            "Вечером хотим, но не знаю точно... может часов в семь?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Отлично! На {date} в девятнадцать часов у нас свободен столик в {hall}. Вас устроит?",
            f"Хорошо, {date} в девятнадцать тридцать есть свободный столик на {guest_count_spelled(n)} гостей. Подойдёт?",
            f"Прекрасно! Могу предложить {date} в двадцать часов, {hall}. Как вам?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, отлично, давайте", "Подходит, бронируйте", "Годится, записывайте",
        ]))})

        convs.append({"role": "assistant", "content": f"Замечательно! На чьё имя бронируем?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content": f"Спасибо, {name}! Бронирование подтверждено: столик на {guest_count_spelled(n)} гостей, {date}. Будем вас ждать!"})

        convs.append({"role": "user", "content": naturalize("Спасибо!")})
        convs.append({"role": "assistant", "content": "Благодарим за звонок! До встречи!"})

        return convs

    # Template 3: couple on a date
    def t3():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый вечер! Ресторан «Романтика», слушаю вас.",
            "Здравствуйте! Ресторан «Лунный свет», чем могу помочь?",
            "Добрый день! Ресторан «Итальянский дворик», администратор на связи.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, хочу забронировать столик на двоих на {date}, что-нибудь уютное",
            f"Добрый вечер, мне нужен романтический столик на двоих {date}",
            f"Привет, хотел бы столик на двоих забронировать, {date}, желательно у окна",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Как приятно! С удовольствием помогу подобрать уютный столик на двоих. На какое время вы планируете визит?",
            f"Замечательно! У нас есть прекрасные столики для двоих — у окна с видом на город и в каминном зале. Какое время вам удобно?",
            f"С радостью помогу! Для романтического ужина могу предложить столик у окна или в VIP-зале со свечами. Во сколько вы хотели бы прийти?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"Часов в восемь вечера, можно у окна?")})

        convs.append({"role": "assistant", "content": random.choice([
            f"Конечно! Столик у панорамного окна на двоих в двадцать часов — прекрасный выбор. Хотите, мы подготовим свечи и лёгкое оформление?",
            f"Отличный выбор! Столик у окна свободен в двадцать часов. Если хотите, мы можем поставить свечи и цветы — это бесплатно.",
        ])})

        if random.random() < 0.6:
            convs.append({"role": "user", "content": naturalize("О, было бы здорово, да! Свечи — это супер")})
            convs.append({"role": "assistant", "content": f"Замечательно, обязательно подготовим! На чьё имя бронируем?"})
        else:
            convs.append({"role": "user", "content": naturalize("Нет, спасибо, просто столик")})
            convs.append({"role": "assistant", "content": "Хорошо, без проблем. На чьё имя оформить бронь?"})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})

        convs.append({"role": "assistant", "content": f"Готово! Столик на двоих у окна, {date}, двадцать часов. Бронь на имя {name}. Приятного вечера, ждём вас!"})

        convs.append({"role": "user", "content": naturalize("Спасибо большое!")})
        convs.append({"role": "assistant", "content": "Благодарим! Желаем прекрасного вечера. До встречи!"})

        return convs

    # Template 4: quick no-nonsense booking
    def t4():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Империя», слушаю вас.",
            "Здравствуйте! Ресторан «Центральный», чем помочь?",
            "Алло! Ресторан «Домино», администратор слушает.",
        ])})

        convs.append({"role": "user", "content": naturalize(
            f"Столик {date}, {time}, {pick_guest_spoken(n)}, на имя {name}"
        )})

        convs.append({"role": "assistant", "content": random.choice([
            f"Принято! Столик на {guest_count_spelled(n)} гостей, {date}. Бронь на имя {name}. Оставьте, пожалуйста, контактный телефон.",
            f"Отлично, записываю: {date}, на {guest_count_spelled(n)} персон, {name}. Ваш номер телефона для связи?",
        ])})

        phone = random_phone()
        convs.append({"role": "user", "content": naturalize(phone)})

        convs.append({"role": "assistant", "content": f"Спасибо! Бронирование подтверждено. Ждём вас, {name}!"})
        convs.append({"role": "user", "content": naturalize("Угу, спасибо")})
        convs.append({"role": "assistant", "content": "Всего доброго, до свидания!"})

        return convs

    # Template 5: family dinner
    def t5():
        n_fam = random.choice([4, 5, 6, 7])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Семейный очаг», администратор на связи.",
            "Здравствуйте! Ресторан «Усадьба», чем могу помочь?",
            "Добрый день! Ресторан «Тёплый дом», слушаю вас.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, хотим прийти всей семьёй, {pick_guest_spoken(n_fam)}, {date}. С нами будут дети",
            f"Добрый день, нужен столик для семьи, {pick_guest_spoken(n_fam)}, двое из них дети",
            f"Привет, бронь нужна {date}, нас {pick_guest_spoken(n_fam)} с детьми",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Замечательно, будем рады видеть всю семью! У нас есть уютные столики для семейных ужинов. Сколько деток будет с вами и какого возраста? Мы можем предложить детское меню и высокие стульчики.",
            f"С удовольствием! Для семей с детьми у нас есть специальные зоны. Подскажите возраст детей — мы подготовим детские стульчики и раскраски.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Двое деток, пять и восемь лет",
            "Один ребёнок, три года",
            "С нами малыш, два годика, и старший — десять",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Отлично, подготовим всё необходимое! Детское меню у нас включает пасту, котлетки, пюре и соки. Во сколько вы планируете прийти?",
            f"Замечательно! У нас есть детское меню от четырёхсот рублей и специальные стульчики. Какое время вам удобно?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"Ну давайте часов в шесть")})

        convs.append({"role": "assistant", "content": f"Хорошо, бронирую столик на {guest_count_spelled(n_fam)} гостей, {date}, восемнадцать часов. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content": f"Готово, {name}! Столик забронирован, детские стульчики и раскраски будут на месте. Ждём вашу семью!"})

        return convs

    return random.choice([t1, t2, t3, t4, t5])()


def gen_event_banquet():
    """Event/banquet booking (20%)."""
    n = random.choice([10, 12, 15, 20, 25, 30, 40, 50])
    date = pick_date_spoken()
    name = random.choice(NAMES_MALE + NAMES_FEMALE)
    occasion = random.choice(OCCASIONS)
    budget_per_person = random.choice([2000, 2500, 3000, 3500, 4000, 5000])

    templates = []

    def t1():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Гранд», администратор банкетного отдела слушает.",
            "Здравствуйте! Ресторан «Европа», отдел мероприятий. Чем могу помочь?",
            "Добрый день! Ресторан «Палаццо», администратор на связи.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, хотим организовать {occasion}, {pick_guest_spoken(n)}, {date}",
            f"Добрый день, нужен банкетный зал на {occasion}, нас будет {pick_guest_spoken(n)}",
            f"Привет, мы планируем {occasion} {date}, нужно место на {pick_guest_spoken(n)}",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Как замечательно! Поздравляю! С удовольствием поможем организовать {occasion}. Наш банкетный зал вмещает до шестидесяти гостей. Расскажите, пожалуйста, о ваших пожеланиях — какой формат вы хотите?",
            f"Прекрасный повод! Для {occasion} на {guest_count_spelled(n)} гостей идеально подойдёт наш банкетный зал. У нас есть несколько вариантов банкетного меню. Какой бюджет вы рассматриваете?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Ну бюджет где-то... {budget_per_person} рублей на человека, может чуть больше",
            f"Хотели бы уложиться в {budget_per_person} на персону",
            f"Рассчитываем примерно {budget_per_person} рублей с человека, это реально?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Да, конечно! При бюджете {spell_thousands(budget_per_person // 1000)} рублей на персону мы можем предложить отличное банкетное меню, которое включает холодные и горячие закуски, основное блюдо на выбор, десерт и напитки. Алкоголь можно принести свой — пробковый сбор составит триста рублей с бутылки. Хотите, чтобы я отправила подробное меню?",
            f"Отличный бюджет! За {spell_thousands(budget_per_person // 1000)} рублей с персоны мы подготовим полноценный банкет: салаты, горячие закуски, основное блюдо, гарнир и десерт. Дополнительно можем оформить зал. Нужны ли какие-то особые пожелания по меню?",
        ])})

        # Ask about special requests
        if random.random() < 0.6:
            req = random.choice(SPECIAL_REQUESTS)
            convs.append({"role": "user", "content": naturalize(random.choice([
                f"Да, и ещё нужен {req}, это возможно?",
                f"А {req} у вас можно организовать?",
                f"Подскажите, {req} — это отдельно оплачивается?",
            ]))})

            convs.append({"role": "assistant", "content": random.choice([
                f"Конечно! {req.capitalize()} мы можем организовать. Стоимость уточню и перезвоню вам с деталями. Это не входит в банкетное меню, но мы часто делаем это для наших гостей.",
                f"Да, безусловно! {req.capitalize()} — это мы делаем регулярно. Я включу это в расчёт и отправлю вам полную смету.",
            ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Отлично, давайте бронируйте", "Хорошо, нас всё устраивает",
            "Супер, давайте оформлять", "Замечательно, бронируем",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Прекрасно! Для подтверждения банкета нам потребуется предоплата в размере тридцати процентов от общей суммы. На чьё имя оформляем бронирование?",
            f"Отлично! Для бронирования банкетного зала необходим депозит — двадцать тысяч рублей. Это засчитывается в общую сумму. Ваше имя, пожалуйста?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        phone = random_phone()
        convs.append({"role": "assistant", "content": f"Спасибо, {name}! Номер телефона для связи?"})
        convs.append({"role": "user", "content": naturalize(phone)})

        convs.append({"role": "assistant", "content": f"Замечательно! Бронирование банкетного зала подтверждено: {occasion}, {date}, {guest_count_spelled(n)} гостей, бронь на имя {name}. Наш менеджер свяжется с вами для обсуждения деталей меню и внесения предоплаты. Спасибо за выбор нашего ресторана!"})

        return convs

    # Template 2: corporate event
    def t2():
        n_corp = random.choice([15, 20, 25, 30])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Бизнес-холл», администратор слушает."})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, нам нужно провести корпоратив, {pick_guest_spoken(n_corp)}, нужен проектор и микрофон",
            f"Добрый день, планируем корпоративное мероприятие на {pick_guest_spoken(n_corp)}, {date}",
            f"Привет, ищем площадку для корпоратива, человек {n_corp}",
        ]))})

        convs.append({"role": "assistant", "content": f"Здравствуйте! С удовольствием поможем организовать корпоративное мероприятие. Наш банкетный зал прекрасно подходит для таких событий — он вмещает до шестидесяти гостей и оборудован проектором, экраном и аудиосистемой. Какой формат вы рассматриваете — фуршет или банкет?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Банкет, конечно, чтобы все сидели нормально",
            "Лучше банкет, и нужно чтобы проектор был",
            "Фуршет, наверное, так удобнее для общения",
        ]))})

        budget_corp = random.choice([3000, 3500, 4000, 5000])
        convs.append({"role": "assistant", "content": f"Отлично! Наше корпоративное меню начинается от двух тысяч пятисот рублей на персону. Есть также премиум-вариант за четыре тысячи рублей с расширенным выбором блюд и напитков. Какой бюджет вы рассматриваете?"})

        convs.append({"role": "user", "content": naturalize(f"Давайте за {budget_corp} на человека, нормально будет")})

        convs.append({"role": "assistant", "content": f"Прекрасный выбор! За {spell_thousands(budget_corp // 1000)} рублей на персону мы подготовим отличный банкет. Аренда зала и оборудования при заказе банкета — бесплатно. Нужна ли будет музыкальная программа или ведущий?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Нет, ведущий свой будет, нам только зал и еда",
            "Да, порекомендуйте ведущего, пожалуйста",
            "Нет, спасибо, всё организуем сами",
        ]))})

        convs.append({"role": "assistant", "content": f"Хорошо, понятно! На чьё имя и компанию оформляем бронирование? Также потребуется контактный номер для согласования деталей."})

        convs.append({"role": "user", "content": naturalize(f"{name}, компания «{random.choice(['Технолоджи', 'ИнноСофт', 'АльфаГруп', 'МедиаПлюс', 'СтройИнвест'])}»")})

        convs.append({"role": "assistant", "content": f"Спасибо, {name}! Бронирование зафиксировано. Наш менеджер по мероприятиям свяжется с вами в течение рабочего дня для обсуждения всех деталей и отправки коммерческого предложения. Всего доброго!"})

        return convs

    return random.choice([t1, t2])()


def gen_menu_dietary():
    """Menu/dietary questions (10%)."""
    name = random.choice(NAMES_MALE + NAMES_FEMALE)
    allergy = random.choice(ALLERGIES)
    diet = random.choice(DIET_TYPES)

    templates = []

    def t1():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Зелёный сад», администратор слушает.",
            "Здравствуйте! Ресторан «Свежесть», чем могу помочь?",
            "Добрый день! Ресторан «Базилик», на связи.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, скажите, у вас есть {diet}?",
            f"Добрый день, а у вас можно заказать что-то без {allergy}? У меня аллергия",
            f"Привет, мне нужно узнать, есть ли у вас {diet}, потому что у меня ограничения по питанию",
            f"Скажите, а в вашем меню есть блюда без {allergy}? Мне это важно",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Конечно! Мы серьёзно относимся к вопросам питания наших гостей. У нас есть отдельный раздел меню для гостей с особыми предпочтениями. Наш шеф-повар готовит блюда без {allergy} — это несколько салатов, горячие блюда и десерты. Хотите, я расскажу подробнее?",
            f"Да, безусловно! У нас в меню отмечены все аллергены, и мы всегда можем адаптировать блюда под ваши пожелания. Блюда без {allergy} — это около десяти позиций. Вы планируете нас посетить?",
            f"Здравствуйте! Да, у нас есть {diet}. Наш шеф-повар уделяет этому большое внимание. Могу перечислить доступные позиции, если хотите.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, расскажите, что есть",
            "Было бы здорово, перечислите пожалуйста",
            "Ага, интересно, что можете предложить",
        ]))})

        menu_items = random.choice([
            "салат «Цезарь» в адаптированном варианте, крем-суп из тыквы, стейк из лосося с овощами гриль и ягодный чизкейк",
            "овощной салат с авокадо, грибной крем-суп, филе курицы на гриле с рисом и фруктовый сорбет",
            "капрезе с моцареллой, минестроне, паста с овощами и панна-котта на кокосовом молоке",
            "салат с рукколой и грушей, тыквенный суп-пюре, дорадо на гриле и домашнее мороженое",
        ])

        convs.append({"role": "assistant", "content": f"С удовольствием! Из подходящих блюд могу порекомендовать: {menu_items}. Средний чек на одного гостя составляет от одной тысячи двухсот до двух тысяч рублей. Хотите забронировать столик?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Да, давайте, на двоих, {pick_date_spoken()}",
            "Звучит хорошо, да, хочу бронь",
            "Пока нет, просто узнавал, спасибо",
            "Да, забронируйте, пожалуйста",
        ]))})

        if "нет" in convs[-1]["content"].lower() or "просто" in convs[-1]["content"].lower():
            convs.append({"role": "assistant", "content": "Конечно, будем рады видеть вас в любое время! Если надумаете, звоните — мы всегда на связи. Хорошего дня!"})
        else:
            convs.append({"role": "assistant", "content": f"Отлично! На какое время и сколько гостей?"})
            n = random.choice([2, 2, 3, 4])
            convs.append({"role": "user", "content": naturalize(f"{pick_guest_spoken(n)}, {pick_time_spoken()}")})
            convs.append({"role": "assistant", "content": f"Записала! Столик на {guest_count_spelled(n)} гостей. Отмечу в бронировании информацию об аллергии, чтобы кухня была в курсе. На чьё имя?"})
            convs.append({"role": "user", "content": naturalize(f"{name}")})
            convs.append({"role": "assistant", "content": f"Спасибо, {name}! Бронирование подтверждено. Мы предупредим кухню о ваших пожеланиях по питанию. Ждём вас!"})

        return convs

    # Template 2: asking about cuisine type
    def t2():
        cuisine = random.choice(CUISINES)
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Вкус», администратор слушает."})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, подскажите, у вас {cuisine} кухня?",
            f"Добрый день, а что у вас за кухня? Хочется чего-то {cuisine}ого",
            f"Привет, а у вас есть блюда {cuisine}й кухни?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Здравствуйте! Да, наш ресторан специализируется на {cuisine}й кухне. Наш шеф-повар имеет более пятнадцати лет опыта и регулярно обновляет меню. Самые популярные блюда у нас — это авторские интерпретации классических рецептов. Хотите узнать подробнее о меню или забронировать столик?",
            f"Добрый день! У нас {cuisine} кухня с авторским подходом. Шеф-повар использует только свежие продукты от локальных фермеров. Могу рассказать о наших фирменных блюдах!",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, расскажите про фирменные блюда",
            "А какой средний чек у вас?",
            "Интересно, а шеф-повар кто у вас?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Наши фирменные блюда: карпаччо из телятины с трюфельным маслом, ризотто с белыми грибами и томлёная баранья нога. Средний чек — от полутора до трёх тысяч рублей на гостя без алкоголя. Хотели бы забронировать столик?",
            "Средний чек у нас составляет от двух до трёх тысяч рублей на персону. Из фирменного рекомендую попробовать наш стейк рибай сухой выдержки и домашнюю пасту с морепродуктами. Будете бронировать?",
        ])})

        convs.append({"role": "user", "content": naturalize("Пока подумаю, спасибо за информацию")})
        convs.append({"role": "assistant", "content": "Конечно, будем рады видеть вас! Если решите прийти, бронируйте заранее — в выходные у нас бывает много гостей. Хорошего дня!"})

        return convs

    return random.choice([t1, t2])()


def gen_reschedule_cancel():
    """Rescheduling/cancellation (10%)."""
    name = random.choice(NAMES_MALE + NAMES_FEMALE)
    date_old = random.choice(["на завтра", "на пятницу", "на субботу", "на воскресенье", "на сегодня"])
    date_new = pick_date_spoken()

    templates = []

    def t1():
        """Cancel booking."""
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Парус», администратор слушает.",
            "Здравствуйте! Ресторан «Маяк», чем могу помочь?",
            "Добрый день! Ресторан «Причал», на связи.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, мне нужно отменить бронирование {date_old}, на имя {name}",
            f"Добрый день, у меня бронь {date_old}, хочу отменить. {name}",
            f"Привет, я бронировал столик {date_old}, но не получится прийти",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Здравствуйте! Да, вижу бронирование на имя {name}. Очень жаль, что не получается прийти. Могу отменить бронь. Скажите, может быть, хотите перенести на другую дату?",
            f"Добрый день, {name}! Нашла вашу бронь. Конечно, могу отменить. Может, перенесём на другой день?",
        ])})

        if random.random() < 0.5:
            convs.append({"role": "user", "content": naturalize(random.choice([
                "Нет, просто отмените, пожалуйста",
                "Нет, к сожалению, не могу, отменяйте",
                "Пока нет, отменяйте",
            ]))})
            convs.append({"role": "assistant", "content": f"Хорошо, бронирование отменено. Будем рады видеть вас в другой раз, {name}! Хорошего дня."})
        else:
            convs.append({"role": "user", "content": naturalize(random.choice([
                f"А можно перенести на {date_new}?",
                f"Да, давайте {date_new}, в то же время",
                f"Хорошая идея, перенесите на {date_new}",
            ]))})
            convs.append({"role": "assistant", "content": f"Конечно! Переношу бронирование на {date_new}, все остальные условия сохраняются. Подтверждаю перенос, {name}. Ждём вас!"})

        convs.append({"role": "user", "content": naturalize("Спасибо")})
        convs.append({"role": "assistant", "content": "Пожалуйста! Будем рады видеть вас. До свидания!"})

        return convs

    # Template 2: reschedule with changes
    def t2():
        n_old = random.choice([2, 4, 6])
        n_new = n_old + random.choice([1, 2, 3])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Лагуна», администратор на связи."})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Добрый день, у меня бронь {date_old} на {guest_count_spelled(n_old)}, {name}. Нужно изменить — нас теперь будет больше",
            f"Здравствуйте, бронировал {date_old} столик, но у нас изменилось количество гостей",
        ]))})

        convs.append({"role": "assistant", "content": f"Здравствуйте! Да, вижу вашу бронь. Конечно, без проблем, сколько гостей теперь будет?"})

        convs.append({"role": "user", "content": naturalize(f"Теперь нас {pick_guest_spoken(n_new)}")})

        convs.append({"role": "assistant", "content": random.choice([
            f"Хорошо, увеличиваю бронирование до {guest_count_spelled(n_new)} гостей. Возможно, потребуется пересадить вас за более просторный стол, но это не проблема. Время остаётся прежним?",
            f"Принято! Для {guest_count_spelled(n_new)} гостей подберём стол побольше. Дата и время без изменений?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, время то же", "Всё остальное без изменений",
            f"Время то же, но может лучше {date_new}?",
        ]))})

        convs.append({"role": "assistant", "content": f"Отлично, бронирование обновлено! {name}, ждём вас в обновлённом составе!"})

        return convs

    # Template 3: late cancel with deposit
    def t3():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Империал», администратор банкетного отдела."})

        convs.append({"role": "user", "content": naturalize(f"Здравствуйте, мне очень неудобно, но нужно отменить банкет {date_old}. На имя {name}")})

        convs.append({"role": "assistant", "content": f"Здравствуйте, {name}. Вижу ваше бронирование банкетного зала. К сожалению, при отмене менее чем за трое суток мы не можем вернуть депозит в полном объёме. Мы можем вернуть пятьдесят процентов или перенести мероприятие на другую дату с сохранением полной суммы. Что бы вы предпочли?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "А можно перенести? На когда есть свободные даты?",
            "Ой, а сколько депозит был? Ну давайте перенесём лучше",
            "Пятьдесят процентов... ну ладно, давайте перенесём тогда",
        ]))})

        convs.append({"role": "assistant", "content": f"Конечно, перенесём! Ближайшие свободные даты для банкетного зала — {random.choice(DATES_SPOKEN)} и {random.choice(DATES_SPOKEN)}. Какая дата вам удобнее?"})

        convs.append({"role": "user", "content": naturalize(f"Давайте {date_new}")})

        convs.append({"role": "assistant", "content": f"Замечательно! Переношу банкет на {date_new}. Депозит сохраняется полностью. Все остальные условия те же. {name}, если будут изменения по количеству гостей или меню, позвоните нам за неделю. Хорошего дня!"})

        return convs

    return random.choice([t1, t2, t3])()


def gen_large_group():
    """Large group booking (10%)."""
    n = random.choice([8, 10, 12, 15, 20])
    date = pick_date_spoken()
    name = random.choice(NAMES_MALE + NAMES_FEMALE)

    templates = []

    def t1():
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Большой», администратор слушает.",
            "Здравствуйте! Ресторан «Площадь», чем могу помочь?",
            "Добрый день! Ресторан «Набережная», на связи.",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, нас большая компания, {pick_guest_spoken(n)}, хотим {date} посидеть",
            f"Добрый день, можно забронировать на большую компанию? Человек {n}, {date}",
            f"Привет, нужен стол на {pick_guest_spoken(n)}, {date}, встреча друзей",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Здравствуйте! Большая компания — это замечательно! Для {guest_count_spelled(n)} гостей я бы рекомендовала наш {random.choice(['банкетный зал', 'второй этаж', 'VIP-зал'])} — там просторно и уютно. На какое время планируете?",
            f"С удовольствием! Для компании из {guest_count_spelled(n)} человек лучше всего подойдёт отдельный зал. У нас есть {random.choice(HALLS)} — идеально для больших компаний. Во сколько вы хотели бы прийти?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"{pick_time_spoken()}")})

        if n >= 10:
            convs.append({"role": "assistant", "content": random.choice([
                f"Хорошо! Для компании от {spell_number(10)} человек у нас действует специальное предложение — банкетное меню от двух тысяч рублей на персону, которое включает набор закусок, горячее и десерт. Или вы предпочитаете заказывать по основному меню?",
                f"Отлично! Для больших компаний мы рекомендуем сет-меню — это удобнее и выгоднее. Стоимость от двух тысяч пятисот рублей на человека. Или можно заказать по основному меню, как удобнее.",
            ])})
        else:
            convs.append({"role": "assistant", "content": "Отлично! Столик подберём просторный. Будете заказывать по основному меню?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Давайте по основному меню, каждый сам выберет",
            "Лучше сет-меню, так проще",
            "А можно часть по меню, а часть общие закуски?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Конечно, как вам удобнее! Мы можем комбинировать — общие закуски на стол и индивидуальные горячие блюда. На чьё имя бронируем?",
            "Без проблем! Мы гибко подходим к заказам для больших компаний. Подскажите ваше имя для бронирования.",
        ])})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})

        phone = random_phone()
        convs.append({"role": "assistant", "content": f"Спасибо, {name}! Номер телефона?"})
        convs.append({"role": "user", "content": naturalize(phone)})

        convs.append({"role": "assistant", "content": f"Прекрасно! Бронирование подтверждено: {date}, {guest_count_spelled(n)} гостей, бронь на имя {name}. Просьба — если количество гостей изменится, дайте знать заранее, чтобы мы подготовили нужное количество мест. Ждём вас!"})

        return convs

    # Template 2: classmates reunion
    def t2():
        n2 = random.choice([12, 15, 20, 25])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Встреча», администратор слушает."})

        convs.append({"role": "user", "content": naturalize(f"Здравствуйте, мы с одноклассниками хотим собраться, нас будет примерно {pick_guest_spoken(n2)}, но может кто-то ещё присоединится")})

        convs.append({"role": "assistant", "content": f"Какая приятная встреча намечается! Для встречи одноклассников рекомендую наш просторный {random.choice(['банкетный зал', 'VIP-зал'])} — там будет комфортно и приватно. Когда планируете?"})

        convs.append({"role": "user", "content": naturalize(f"{date}, вечером")})

        convs.append({"role": "assistant", "content": f"Отлично! Забронирую на {guest_count_spelled(n2)} гостей с возможностью расширения до {spell_number(n2 + 5)}. Для таких встреч многие заказывают наше «Дружеское меню» — набор закусок, два горячих на выбор и десерт за две тысячи восемьсот рублей с человека. Как вам?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Звучит хорошо, давайте", "А можно меню посмотреть заранее?",
            "Нормально, бронируйте",
        ]))})

        convs.append({"role": "assistant", "content": f"Замечательно! Могу отправить меню на почту или в мессенджер. На чьё имя бронирование?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content": f"Записала! {name}, бронь на {date}, {guest_count_spelled(n2)} гостей. Для подтверждения прошу внести депозит — пять тысяч рублей, он засчитается в общий счёт. Удобнее перевести или оплатить на месте?"})

        convs.append({"role": "user", "content": naturalize("Переведу, скиньте реквизиты")})

        convs.append({"role": "assistant", "content": f"Сейчас отправлю реквизиты в СМС на ваш номер. После поступления оплаты бронь будет окончательно подтверждена. {name}, ждём вас и ваших друзей!"})

        return convs

    return random.choice([t1, t2])()


def gen_special_requests():
    """Special requests (10%)."""
    name = random.choice(NAMES_MALE + NAMES_FEMALE)
    date = pick_date_spoken()

    templates = []

    # Template 1: birthday with cake
    def t1():
        age = random.choice([25, 30, 35, 40, 45, 50, 55, 60])
        n = random.choice([6, 8, 10, 12, 15])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Праздник», администратор слушает.",
            "Здравствуйте! Ресторан «Торжество», чем могу помочь?",
            "Добрый день! Ресторан «Феерия», на связи.",
        ])})

        bday_name = random.choice(NAMES_MALE + NAMES_FEMALE)
        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, хочу организовать день рождения для {bday_name}, {date}, нас будет {pick_guest_spoken(n)}. Нужен торт и украшения",
            f"Добрый день, у {'мужа' if bday_name in NAMES_MALE else 'подруги'} день рождения {date}, хочу сделать сюрприз. Нас {pick_guest_spoken(n)}",
            f"Привет, планирую отметить юбилей — {age} лет, {date}, {pick_guest_spoken(n)}, нужен торт и может шарики",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Как здорово! С удовольствием поможем сделать этот день незабываемым! Для {guest_count_spelled(n)} гостей предлагаю наш {random.choice(['банкетный зал', 'VIP-зал'])}. По торту — у нас есть свой кондитер, который готовит на заказ. Торт обойдётся от трёх тысяч рублей за килограмм. Какой размер вам нужен?",
            f"Замечательный повод! Обожаем организовывать дни рождения. Могу предложить полный пакет: украшение зала шарами, именной торт от нашего кондитера и фотозону. Стоимость оформления — от пяти тысяч рублей. Торт — от двух тысяч пятисот рублей за килограмм. Расскажите подробнее о ваших пожеланиях!",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Торт на два килограмма, шоколадный. И шарики хотелось бы",
            "Давайте торт килограмма на три, и украшения простые, не слишком пёстрые",
            "Мне бы торт и может цветы на стол, шарики — перебор",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Прекрасный выбор! Записываю: торт и оформление. Наш декоратор подготовит всё за час до вашего прихода. Также рекомендую обсудить меню — у нас есть специальное праздничное предложение от двух тысяч пятисот рублей на гостя. Хотите посмотреть варианты?",
            "Отлично, всё сделаем! По меню — рекомендую наш праздничный сет: красивая подача, несколько смен блюд. Стоимость — три тысячи рублей на персону. Подойдёт?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Да, давайте праздничный сет, звучит хорошо",
            "А можно по обычному меню заказать? Не все много едят",
            "Подойдёт, записывайте",
        ]))})

        convs.append({"role": "assistant", "content": f"Конечно! Бронирую: {date}, {guest_count_spelled(n)} гостей, торт и оформление зала. На чьё имя?"})

        convs.append({"role": "user", "content": naturalize(f"На {name}")})

        convs.append({"role": "assistant", "content": f"Спасибо, {name}! Для подтверждения праздничного бронирования нужна предоплата — десять тысяч рублей. Это пойдёт в счёт общей суммы. Реквизиты отправлю в СМС. Будет незабываемый праздник!"})

        convs.append({"role": "user", "content": naturalize("Отлично, жду, спасибо!")})
        convs.append({"role": "assistant", "content": f"Спасибо за доверие, {name}! Будем рады сделать этот день особенным. До встречи!"})

        return convs

    # Template 2: wedding banquet
    def t2():
        n_wedding = random.choice([30, 40, 50, 60])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Белая роза», свадебный отдел слушает."})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, мы планируем свадьбу {date}, нужен зал на {pick_guest_spoken(n_wedding)}",
            f"Добрый день, ищем ресторан для свадебного банкета, {pick_guest_spoken(n_wedding)} гостей",
            f"Привет, хотим отпраздновать свадьбу у вас, нас будет примерно {pick_guest_spoken(n_wedding)}",
        ]))})

        convs.append({"role": "assistant", "content": f"Поздравляю! Свадьба — это прекрасно! Наш банкетный зал вмещает до восьмидесяти гостей и идеально подходит для свадебных торжеств. Мы предлагаем несколько пакетов: «Классический» от четырёх тысяч рублей на персону, «Премиум» от шести тысяч и «Люкс» от восьми тысяч. Каждый включает банкетное меню, оформление зала и услуги координатора. Какой бюджет вы рассматриваете?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Нам бы средний вариант, премиум наверное",
            "А что входит в классический?",
            "Давайте посмотрим люкс, хочется чтобы всё было идеально",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Пакет «Премиум» включает: приветственный фуршет с шампанским, банкетное меню из семи блюд, свадебный торт весом пять килограммов, оформление зала живыми цветами и тканями, координатор мероприятия на весь вечер. Алкогольные напитки — на ваш выбор: можете принести свои или заказать у нас.",
            "«Классический» пакет: банкетное меню из пяти блюд, базовое оформление зала (шары, ленты, свечи), свадебный торт три килограмма. Это хороший вариант для уютной свадьбы. Хотите, отправлю подробное описание всех пакетов на электронную почту?",
        ])})

        convs.append({"role": "user", "content": naturalize("Да, отправьте, мы с женихом посмотрим и перезвоним")})

        convs.append({"role": "assistant", "content": "Конечно! Подскажите вашу электронную почту и удобное время для повторного звонка. Также рекомендую приехать к нам на просмотр зала — так вы сможете лучше представить ваше торжество."})

        convs.append({"role": "user", "content": naturalize(f"Почта — {name.lower()}@mail.ru, позвоните послезавтра")})

        convs.append({"role": "assistant", "content": f"Записала! Отправлю подробную презентацию на {name.lower()}@mail.ru и перезвоню послезавтра. А пока, если хотите, можем предварительно зарезервировать дату, чтобы зал не заняли. Это ни к чему не обязывает."})

        convs.append({"role": "user", "content": naturalize("Да, зарезервируйте пока, на всякий случай")})
        convs.append({"role": "assistant", "content": f"Готово! Дата {date} предварительно зарезервирована. Ждём вашего решения. Ещё раз поздравляю и желаю вам счастья! До свидания!"})

        return convs

    # Template 3: live music request
    def t3():
        n3 = random.choice([4, 6, 8, 10])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый вечер! Ресторан «Джаз», администратор на связи."})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Добрый вечер, хотел узнать — у вас есть живая музыка?",
            f"Привет, а по каким дням у вас играет живая музыка?",
            f"Здравствуйте, подскажите, в {random.choice(['пятницу', 'субботу'])} у вас будет музыка?",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            "Добрый вечер! Да, у нас живая музыка по пятницам и субботам с двадцати часов. В пятницу играет джазовый квартет, а в субботу — акустический дуэт. Хотели бы забронировать столик?",
            "Здравствуйте! Живая музыка у нас по выходным: в пятницу — джаз, в субботу — лаунж. Начало в двадцать часов. Бронируете?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"О, джаз — это круто! Да, {pick_guest_spoken(n3)}, в пятницу")})

        convs.append({"role": "assistant", "content": f"Прекрасный выбор! Для лучшего звука рекомендую столик ближе к сцене. На {guest_count_spelled(n3)} гостей есть отличный столик с прямым видом на музыкантов. Бронируем?"})

        convs.append({"role": "user", "content": naturalize("Да, конечно, бронируйте!")})

        convs.append({"role": "assistant", "content": f"Отлично! На чьё имя?"})
        convs.append({"role": "user", "content": naturalize(f"{name}")})
        convs.append({"role": "assistant", "content": f"Готово, {name}! Столик на {guest_count_spelled(n3)} гостей в пятницу вечером, ближе к сцене. Джаз начнётся в двадцать часов, рекомендую прийти к девятнадцати тридцати. Хорошего вечера!"})

        return convs

    # Template 4: children's party
    def t4():
        n_kids = random.choice([8, 10, 12, 15])
        child_age = random.choice([5, 6, 7, 8, 9, 10])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Карамель», администратор слушает."})

        convs.append({"role": "user", "content": naturalize(f"Здравствуйте, хочу организовать детский день рождения, ребёнку {child_age} лет, {pick_guest_spoken(n_kids)} с родителями")})

        convs.append({"role": "assistant", "content": f"Как замечательно! Детские праздники — наша специальность! У нас есть детская комната с аниматором и отдельное меню для маленьких гостей. Пакет «Детский праздник» включает: аниматора на два часа, детское меню, торт и воздушные шары. Стоимость — от одной тысячи пятисот рублей на ребёнка. Взрослые могут заказать по основному меню. Когда планируете?"})

        convs.append({"role": "user", "content": naturalize(f"{date}, днём, часа в два")})

        convs.append({"role": "assistant", "content": "Отлично! В четырнадцать часов — прекрасное время для детского праздника. Какую тематику хотите? У нас есть пираты, принцессы, супергерои и научное шоу."})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "Пираты! Сын обожает пиратов",
            "Принцессы, конечно, у нас девочка",
            "Научное шоу звучит интересно",
            "Супергерои, мальчишки будут в восторге",
        ]))})

        convs.append({"role": "assistant", "content": f"Отличный выбор! Записываю: детский праздник {date} в четырнадцать часов, {guest_count_spelled(n_kids)} гостей. Торт заказываете у нас или принесёте свой?"})

        convs.append({"role": "user", "content": naturalize(random.choice([
            "У вас закажем, шоколадный", "Свой принесём", "А какие торты у вас есть?",
        ]))})

        convs.append({"role": "assistant", "content": f"Хорошо, записала! На чьё имя бронирование?"})
        convs.append({"role": "user", "content": naturalize(f"{name}")})
        convs.append({"role": "assistant", "content": f"Спасибо, {name}! Праздник будет чудесным! Предоплата — три тысячи рублей. Наш менеджер позвонит вам для согласования деталей. До встречи!"})

        return convs

    # Template 5: business lunch
    def t5():
        n5 = random.choice([2, 3, 4, 5, 6])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": random.choice([
            "Добрый день! Ресторан «Деловой квартал», администратор слушает.",
            "Здравствуйте! Ресторан «Столица», чем могу помочь?",
        ])})

        convs.append({"role": "user", "content": naturalize(random.choice([
            f"Здравствуйте, нужен столик для деловой встречи, {pick_guest_spoken(n5)}, {date}, в обед",
            f"Добрый день, хочу забронировать для бизнес-ланча, нас {pick_guest_spoken(n5)}, нужно тихое место",
            f"Привет, нужна бронь для переговоров за обедом, {pick_guest_spoken(n5)}, желательно отдельный кабинет",
        ]))})

        convs.append({"role": "assistant", "content": random.choice([
            f"Здравствуйте! Для деловой встречи рекомендую наш VIP-кабинет — тихо, приватно, есть розетки для ноутбуков и Wi-Fi. Бизнес-ланч у нас с двенадцати до пятнадцати часов, стоимость — от пятисот девяноста рублей: салат, суп, горячее и напиток. На какое время?",
            f"С удовольствием! Для переговоров идеально подойдёт наш отдельный кабинет на {guest_count_spelled(n5)} персон. Тишина, приватность, быстрое обслуживание. Бизнес-ланч — шестьсот пятьдесят рублей. Во сколько вас ждать?",
        ])})

        convs.append({"role": "user", "content": naturalize(f"К часу дня, и чтобы побыстрее обслужили, у нас мало времени")})

        convs.append({"role": "assistant", "content": f"Понимаю! Предупрежу кухню, чтобы подготовили всё оперативно. Если хотите, можем заранее сформировать заказ — тогда блюда будут готовы к вашему приходу. Это сэкономит время."})

        convs.append({"role": "user", "content": naturalize("О, отличная идея, давайте так")})

        convs.append({"role": "assistant", "content": "Замечательно! Тогда выберите, пожалуйста, из бизнес-ланча: салат «Цезарь» или «Греческий», суп — грибной крем-суп или борщ, горячее — стейк из курицы или рыба на гриле."})

        convs.append({"role": "user", "content": naturalize("Всем «Цезарь», грибной суп и курицу, пожалуй")})

        convs.append({"role": "assistant", "content": f"Записала: {spell_number(n5)} «Цезаря», {spell_number(n5)} грибных крем-супа и {spell_number(n5)} стейков из курицы. На чьё имя бронь?"})

        convs.append({"role": "user", "content": naturalize(f"{name}")})

        convs.append({"role": "assistant", "content": f"Готово, {name}! VIP-кабинет, {date}, тринадцать часов, на {guest_count_spelled(n5)} гостей. Заказ будет готов к вашему приходу. Продуктивной встречи!"})

        return convs

    # Template 6: special decoration request
    def t6():
        n6 = random.choice([2, 4, 6])
        occasion6 = random.choice(["годовщину свадьбы", "помолвку", "предложение руки и сердца"])
        convs = [{"role": "system", "content": SYSTEM_PROMPT}]
        convs.append({"role": "assistant", "content": "Добрый день! Ресторан «Романс», администратор слушает."})

        convs.append({"role": "user", "content": naturalize(f"Здравствуйте, хочу отметить {occasion6} {date}, нужно чтобы было особенно красиво")})

        convs.append({"role": "assistant", "content": f"Какой прекрасный повод! Мы обожаем создавать атмосферу для таких моментов. Расскажите, что вы представляете — свечи, лепестки роз, особое оформление стола? Сколько гостей будет?"})

        convs.append({"role": "user", "content": naturalize(f"Нас {pick_guest_spoken(n6)}, хочется свечи, цветы и может что-то необычное")})

        convs.append({"role": "assistant", "content": random.choice([
            f"Могу предложить наш романтический пакет: столик у окна с панорамным видом, свечи, живые цветы, бутылка шампанского в подарок и именной десерт. Стоимость оформления — три тысячи рублей. Как вам?",
            f"У нас есть пакет «Романтический вечер»: отдельная зона со свечами, лепестки роз, бутылка просекко и комплимент от шеф-повара. Стоимость — четыре тысячи рублей за оформление. Хотите?",
        ])})

        convs.append({"role": "user", "content": naturalize("Да, идеально! Бронируйте!")})

        convs.append({"role": "assistant", "content": f"Замечательно! На чьё имя и на какое время?"})
        convs.append({"role": "user", "content": naturalize(f"{name}, к семи вечера")})
        convs.append({"role": "assistant", "content": f"Всё записала, {name}! {date}, девятнадцать часов, романтический пакет. Мы создадим незабываемую атмосферу. Будем ждать вас!"})

        return convs

    return random.choice([t1, t2, t3, t4, t5, t6])()


# ============ GENERATION ============

def generate_all_dialogs(count=400):
    """Generate dialogs according to distribution."""
    dialogs = []

    # Distribution: simple 40%, event 20%, menu 10%, reschedule 10%, large 10%, special 10%
    counts = {
        'simple': int(count * 0.40),      # 160
        'event': int(count * 0.20),        # 80
        'menu': int(count * 0.10),         # 40
        'reschedule': int(count * 0.10),   # 40
        'large': int(count * 0.10),        # 40
        'special': int(count * 0.10),      # 40
    }

    # Adjust to reach exact count
    total = sum(counts.values())
    if total < count:
        counts['simple'] += count - total

    generators = {
        'simple': gen_simple_booking,
        'event': gen_event_banquet,
        'menu': gen_menu_dietary,
        'reschedule': gen_reschedule_cancel,
        'large': gen_large_group,
        'special': gen_special_requests,
    }

    for category, num in counts.items():
        gen = generators[category]
        for _ in range(num):
            convs = gen()
            dialogs.append({"conversations": convs})

    random.shuffle(dialogs)
    return dialogs


if __name__ == "__main__":
    dialogs = generate_all_dialogs(400)

    output_path = os.path.join(os.path.dirname(__file__), "restaurant_dialogs.jsonl")

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
                assert len(obj["conversations"]) >= 4  # system + at least 3 turns
                assert obj["conversations"][0]["role"] == "system"
                valid += 1
            except Exception as e:
                print(f"Invalid line {i+1}: {e}")
        print(f"Validation: {valid}/{len(lines)} valid lines")
