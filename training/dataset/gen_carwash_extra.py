#!/usr/bin/env python3
"""Generate 500 diverse car wash SFT training dialogs."""
import json
import random
import os

random.seed(42)

SYSTEM = "Вы — администратор автомойки. Помогаете клиентам записаться на мойку, выбрать тип услуги и удобное время. Говорите вежливо и по делу."

WASH_NAMES = [
    "Мойдодыр", "Аква", "Блеск", "Кристалл", "Премиум Вош", "Чистый кузов",
    "АвтоБлеск", "Аквамарин", "Чистюля", "Мойка Про", "АвтоСпа", "Глянец",
    "Пенный рай", "Водопад", "Сияние", "АкваЛюкс", "МойкаСити", "Идеал",
]

MALE_NAMES = [
    "Александр", "Дмитрий", "Михаил", "Андрей", "Сергей", "Артём", "Николай",
    "Владимир", "Иван", "Павел", "Роман", "Олег", "Максим", "Денис", "Виктор",
    "Алексей", "Евгений", "Кирилл", "Тимур", "Руслан", "Вадим", "Игорь",
    "Антон", "Владислав", "Георгий", "Фёдор", "Борис", "Юрий", "Григорий",
    "Марат", "Ринат", "Эдуард", "Валерий", "Константин", "Станислав",
]

FEMALE_NAMES = [
    "Ирина", "Наталья", "Екатерина", "Мария", "Анна", "Ольга", "Татьяна",
    "Светлана", "Елена", "Юлия", "Дарья", "Алина", "Виктория", "Марина",
    "Кристина", "Полина", "Надежда", "Людмила", "Галина", "Оксана", "Вера",
    "Лариса", "Диана", "Жанна", "Валентина", "Софья", "Алёна", "Регина",
]

# car_model, category: sedan/crossover/suv/minivan/commercial/moto
CARS = [
    ("Тойота Камри", "sedan"), ("Хёндай Солярис", "sedan"), ("Киа Рио", "sedan"),
    ("Шкода Октавия", "sedan"), ("Фольксваген Поло", "sedan"), ("Рено Логан", "sedan"),
    ("Лада Веста", "sedan"), ("Лада Гранта", "sedan"), ("Мазда 3", "sedan"),
    ("Хонда Сивик", "sedan"), ("Тойота Королла", "sedan"), ("Ниссан Альмера", "sedan"),
    ("Форд Фокус", "sedan"), ("Шевроле Круз", "sedan"), ("Пежо 408", "sedan"),
    ("Ситроен С4", "sedan"), ("Опель Астра", "sedan"), ("Ауди А4", "sedan"),
    ("БМВ 3 серии", "sedan"), ("Мерседес С-класс", "sedan"), ("Хёндай Элантра", "sedan"),
    ("Киа Серато", "sedan"), ("Шкода Рапид", "sedan"), ("Фольксваген Джетта", "sedan"),
    ("Тойота Камри", "sedan"), ("Субару Импреза", "sedan"), ("Вольво S60", "sedan"),
    ("Лексус IS", "sedan"), ("Дженезис G70", "sedan"), ("Джили Эмгранд", "sedan"),
    ("Чери Тигго 4", "crossover"), ("Хавейл Джолион", "crossover"),
    ("Киа Спортейдж", "crossover"), ("Хёндай Туссан", "crossover"),
    ("Тойота РАВ4", "crossover"), ("Ниссан Кашкай", "crossover"),
    ("Мазда CX-5", "crossover"), ("Фольксваген Тигуан", "crossover"),
    ("Шкода Кодиак", "crossover"), ("Рено Дастер", "crossover"),
    ("БМВ X3", "crossover"), ("Ауди Q5", "crossover"), ("Вольво XC60", "crossover"),
    ("Субару Форестер", "crossover"), ("Мицубиси Аутлендер", "crossover"),
    ("Хавейл F7", "crossover"), ("Чанган CS75", "crossover"),
    ("Джили Атлас", "crossover"), ("Омода С5", "crossover"),
    ("Тойота Ленд Крузер 300", "suv"), ("Тойота Ленд Крузер Прадо", "suv"),
    ("Лексус LX", "suv"), ("Инфинити QX80", "suv"), ("Ниссан Патрол", "suv"),
    ("Мицубиси Паджеро", "suv"), ("УАЗ Патриот", "suv"), ("Ленд Ровер Дискавери", "suv"),
    ("БМВ X5", "suv"), ("Ауди Q7", "suv"), ("Мерседес GLS", "suv"),
    ("Кадиллак Эскалейд", "suv"), ("Шевроле Тахо", "suv"), ("Джип Гранд Чероки", "suv"),
    ("Вольво XC90", "suv"), ("Хавейл H9", "suv"), ("Танк 500", "suv"),
    ("Киа Карнивал", "minivan"), ("Хёндай Старекс", "minivan"),
    ("Тойота Альфард", "minivan"), ("Фольксваген Мультивэн", "minivan"),
    ("Минивэн Стария", "minivan"),
    ("ГАЗель", "commercial"), ("ГАЗель Некст", "commercial"),
    ("Мерседес Спринтер", "commercial"), ("Форд Транзит", "commercial"),
    ("Фиат Дукато", "commercial"), ("Ситроен Джампер", "commercial"),
]

MOTORCYCLES = [
    "Хонда CBR", "Ямаха MT-07", "Сузуки GSX-R", "Кавасаки Ниндзя", "БМВ R1250",
    "Дукати Монстер", "Харли-Дэвидсон Спортстер", "КТМ Дюк",
]

INFORMAL_CARS = {
    "Тойота Камри": ["камри", "камрюха", "камрюшка"],
    "Тойота Ленд Крузер 300": ["крузак", "ленд крузер", "двухсотка... то есть трёхсотка"],
    "Тойота Ленд Крузер Прадо": ["прадик", "прадо"],
    "Лада Веста": ["веста", "вестуха"],
    "Лада Гранта": ["гранта", "грантуха"],
    "Хёндай Солярис": ["солярис", "солярик"],
    "Киа Рио": ["рио", "киа рио"],
    "Рено Логан": ["логан", "логанчик"],
    "БМВ X5": ["икс пятый", "бэха"],
    "БМВ 3 серии": ["тройка бмв", "бэха"],
    "Мерседес С-класс": ["мерс", "цэшка"],
    "Ауди А4": ["ауди", "а четвёрка"],
    "Фольксваген Поло": ["поло", "полик"],
    "УАЗ Патриот": ["уазик", "патриот"],
    "Мицубиси Паджеро": ["паджерик", "паджеро"],
}

PRICE = {
    "sedan": {"express": (500, 800), "complex": (1000, 1500), "engine": (800, 1200)},
    "crossover": {"express": (700, 1000), "complex": (1300, 1800), "engine": (1000, 1400)},
    "suv": {"express": (900, 1200), "complex": (1500, 2200), "engine": (1200, 1600)},
    "minivan": {"express": (1000, 1400), "complex": (1700, 2200), "engine": (1200, 1500)},
    "commercial": {"express": (1200, 1600), "complex": (2000, 2800), "engine": (1400, 1800)},
}

HIMCHISTKA_PRICES = {"partial": (3000, 5000), "full": (5000, 12000)}
POLIROVKA_PRICES = (5000, 15000)
KERAMIKA_PRICES = (15000, 30000)
DETAILING_PRICES = (8000, 25000)
MOTO_WASH = (300, 600)
ANTIKOR_PRICES = (3000, 8000)

DAYS = [
    "завтра", "послезавтра", "в понедельник", "во вторник", "в среду",
    "в четверг", "в пятницу", "в субботу", "в воскресенье",
    "на следующей неделе", "сегодня",
]

TIMES = [
    "девять утра", "десять утра", "одиннадцать утра", "двенадцать дня",
    "час дня", "два часа дня", "три часа дня", "четыре часа дня",
    "пять вечера", "шесть вечера", "половина десятого", "половина одиннадцатого",
    "половина двенадцатого", "половина первого", "половина второго",
    "девять тридцать", "десять тридцать", "одиннадцать тридцать",
    "восемь утра", "семь утра", "семь вечера", "восемь вечера",
]

GREETINGS_USER = [
    "алло", "алё", "да, здравствуйте", "привет", "здрасте", "добрый день",
    "добрый", "ну, здравствуйте", "э... привет", "ну это, алло",
    "алло, это мойка?", "здравствуйте, это автомойка?", "добрый день, алло",
    "ааа, добрый день", "ну вот, добрый день", "слушайте, добрый",
    "да, привет", "здравствуйте", "ну... здрасте",
]

GREETINGS_ADMIN = [
    "Здравствуйте! Автомойка «{name}», чем могу помочь?",
    "Добрый день! Автомойка «{name}», слушаю вас.",
    "Здравствуйте! Это автомойка «{name}», чем могу быть полезен?",
    "Добрый день! Автомойка, слушаю вас.",
    "Здравствуйте! Автомойка «{name}», слушаю вас внимательно.",
    "Добрый день! Это автомойка, рады вашему звонку. Чем могу помочь?",
]

FILLERS = [
    "ну", "эм", "так", "короче", "это...", "ну это...", "как бы",
    "слушайте", "значит", "это самое", "в общем", "вот", "ну вот",
    "подождите...", "секунду...", "дайте подумать...", "так сказать",
]

NOISE = [
    "[неразборчиво]", "[шум двигателя]", "[музыка на фоне]", "[помехи]",
    "[шум улицы]", "[сигнал автомобиля]", "[голоса на фоне]",
    "[шум ветра]", "[звук радио]",
]

def spell_price(p):
    """Spell out a price in Russian words."""
    if p < 1000:
        h = p // 100
        hundreds = ["", "сто", "двести", "триста", "четыреста", "пятьсот",
                     "шестьсот", "семьсот", "восемьсот", "девятьсот"]
        return hundreds[h] + " рублей"

    thousands = {1: "одна тысяча", 2: "две тысячи", 3: "три тысячи",
                 4: "четыре тысячи", 5: "пять тысяч", 6: "шесть тысяч",
                 7: "семь тысяч", 8: "восемь тысяч", 9: "девять тысяч",
                 10: "десять тысяч", 11: "одиннадцать тысяч", 12: "двенадцать тысяч",
                 13: "тринадцать тысяч", 14: "четырнадцать тысяч", 15: "пятнадцать тысяч",
                 16: "шестнадцать тысяч", 17: "семнадцать тысяч", 18: "восемнадцать тысяч",
                 19: "девятнадцать тысяч", 20: "двадцать тысяч",
                 21: "двадцать одна тысяча", 22: "двадцать две тысячи",
                 23: "двадцать три тысячи", 24: "двадцать четыре тысячи",
                 25: "двадцать пять тысяч", 26: "двадцать шесть тысяч",
                 27: "двадцать семь тысяч", 28: "двадцать восемь тысяч",
                 29: "двадцать девять тысяч", 30: "тридцать тысяч",
                 35: "тридцать пять тысяч", 40: "сорок тысяч",
                 45: "сорок пять тысяч", 50: "пятьдесят тысяч",
                 }
    t = p // 1000
    r = p % 1000
    hundreds = ["", "сто", "двести", "триста", "четыреста", "пятьсот",
                 "шестьсот", "семьсот", "восемьсот", "девятьсот"]

    t_str = thousands.get(t, f"{t} тысяч")
    if r == 0:
        return t_str + " рублей"
    else:
        h = r // 100
        return t_str + " " + hundreds[h] + " рублей"


def add_filler(text, prob=0.3):
    if random.random() < prob:
        f = random.choice(FILLERS)
        if random.random() < 0.5:
            return f + ", " + text[0].lower() + text[1:]
        else:
            parts = text.split(" ", 2)
            if len(parts) >= 3:
                return parts[0] + " " + f + ", " + parts[1] + " " + parts[2]
    return text

def add_noise(text, prob=0.15):
    if random.random() < prob:
        n = random.choice(NOISE)
        words = text.split()
        if len(words) > 2:
            pos = random.randint(1, len(words)-1)
            words.insert(pos, n)
            return " ".join(words)
    return text

def make_user_line(text):
    text = add_filler(text)
    text = add_noise(text)
    if random.random() < 0.3:
        text = text[0].lower() + text[1:]
    return text

def get_car_mention(car_name):
    """Sometimes return informal car name."""
    if car_name in INFORMAL_CARS and random.random() < 0.4:
        return random.choice(INFORMAL_CARS[car_name])
    return car_name

def rand_price(lo, hi, step=100):
    return random.randrange(lo, hi+1, step)

def pick_name():
    if random.random() < 0.6:
        return random.choice(MALE_NAMES), "m"
    else:
        return random.choice(FEMALE_NAMES), "f"

def pick_car():
    return random.choice(CARS)

def pick_day_time():
    return random.choice(DAYS), random.choice(TIMES)

# ============================================================
# SCENARIO GENERATORS
# Each returns a list of (role, content) pairs (without system)
# ============================================================

def scenario_dirty_offroad():
    """Car extremely dirty after offroad/long trip."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)

    price_complex = rand_price(*PRICE[cat]["complex"])
    surcharge = random.choice([200, 300, 500])
    total = price_complex + surcharge

    dirt_reasons = [
        "после рыбалки, вся в грязи по самую крышу",
        "по бездорожью ездил, днище и арки забиты глиной",
        "с дачи еду, дорогу размыло, машина вся в грязи",
        "после дальней поездки, тысячу километров проехал, вся в мошках и битуме",
        "на охоту ездил, машина как из болота вылезла",
        "после стройки, вся в цементной пыли",
        "с полевой дороги, грязь везде — арки, пороги, бампер",
    ]

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))

    reason = random.choice(dirt_reasons)
    convs.append(("user", make_user_line(f"мне бы машину помыть, {reason}")))
    convs.append(("assistant", f"Понимаю, бывает! Для сильно загрязнённых автомобилей рекомендую комплексную мойку с предварительным замачиванием — так мы безопасно размягчим всю грязь. Подскажите, какой у вас автомобиль?"))

    convs.append(("user", make_user_line(f"у меня {car_mention}")))
    convs.append(("assistant", f"Комплексная мойка для {car} — {spell_price(price_complex)}. При сильном загрязнении добавляется наценка {spell_price(surcharge)} за дополнительную обработку. Итого — {spell_price(total)}. Время работы — около полутора часов. Когда вам удобно?"))

    convs.append(("user", make_user_line(f"давайте {day} на {time}")))
    convs.append(("assistant", f"Записываю вас на {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Рекомендую не затягивать — засохшая грязь сложнее отмывается. До встречи!"))

    return convs

def scenario_pet_hair():
    """Pet hair in salon needs special cleaning."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)

    price = rand_price(*HIMCHISTKA_PRICES["partial"])
    surcharge = random.choice([500, 800, 1000])
    total = price + surcharge

    pets = [
        ("собака", "собачья шерсть", "пёс"),
        ("кот", "кошачья шерсть", "кот"),
        ("лабрадор", "шерсть лабрадора", "собака"),
        ("хаски", "шерсть хаски", "пёс"),
        ("овчарка", "шерсть овчарки", "собака"),
    ]
    pet, hair_type, pet_word = random.choice(pets)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))

    requests = [
        f"у меня {pet} линяет, весь салон в шерсти. Можете вычистить?",
        f"возил {pet_word}а на дачу, теперь весь задний ряд в шерсти",
        f"нужно салон почистить, {hair_type} повсюду — сиденья, коврики",
    ]
    convs.append(("user", make_user_line(random.choice(requests))))
    convs.append(("assistant", f"Конечно, мы справимся! Для удаления шерсти используем специальные щётки и мощный экстрактор. Это входит в химчистку салона с доплатой за обработку от шерсти. Какой у вас автомобиль?"))

    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Частичная химчистка салона для {car} — {spell_price(price)}, плюс доплата за удаление шерсти — {spell_price(surcharge)}. Итого — {spell_price(total)}. Работа займёт три-четыре часа. Когда привезёте?"))

    convs.append(("user", make_user_line(f"{day} на {time} можно?")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Постараемся убрать каждую шерстинку! До встречи!"))

    return convs

def scenario_spill_urgent():
    """Spilled coffee/food, needs spot cleaning urgently."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    car_mention = get_car_mention(car)
    price = rand_price(1500, 3000, 500)

    spills = [
        ("кофе пролил на сиденье", "кофе"),
        ("ребёнок сок разлил по всему заднему ряду", "сок"),
        ("молоко опрокинулось, запах ужасный", "молоко"),
        ("соус из шаурмы на сиденье капнул", "соус"),
        ("колу пролил на ковролин", "кола"),
        ("еду рассыпал, крошки и пятна везде", "еда"),
        ("мороженое растаяло на сиденье", "мороженое"),
    ]
    spill_desc, substance = random.choice(spills)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"мне срочно нужна чистка, {spill_desc}")))
    convs.append(("assistant", f"Понимаю, с пятнами от {substance} лучше не затягивать! Можем сделать локальную химчистку загрязнённого участка. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Локальная химчистка для {car} — {spell_price(price)}. Если пятно свежее, уберём за полтора-два часа. Можете подъехать сегодня?"))

    if random.random() < 0.5:
        convs.append(("user", make_user_line("да, могу через час приехать")))
        convs.append(("assistant", f"Отлично, ждём вас! Как вас зовут?"))
    else:
        convs.append(("user", make_user_line("а прямо сейчас можно?")))
        convs.append(("assistant", f"Сейчас есть свободный бокс, приезжайте! Как вас зовут?"))

    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Записала, {name}! Приезжайте как можно скорее — чем свежее пятно, тем лучше результат. Ждём!"))

    return convs

def scenario_taxi_quick():
    """Taxi/delivery driver needs quick daily wash."""
    car, cat = pick_car()
    while cat not in ("sedan", "crossover"):
        car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["express"])

    jobs = [
        ("в такси работаю", "таксистов"),
        ("курьером работаю, на своей машине", "курьеров"),
        ("в доставке работаю", "водителей доставки"),
        ("каршеринг веду, машина своя", "водителей"),
    ]
    job_desc, job_word = random.choice(jobs)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"мне бы побыстрее помыть, {job_desc}, времени мало")))
    convs.append(("assistant", f"Понимаю, для вас время — деньги! Экспресс-мойка занимает около двадцати-тридцати минут. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Экспресс-мойка для {car} — {spell_price(price)}. Могу записать вас на {day}, {time}. Подойдёт?"))
    convs.append(("user", make_user_line("да, подходит")))
    convs.append(("assistant", f"Отлично! Как вас зовут?"))
    convs.append(("user", make_user_line(name)))

    if random.random() < 0.5:
        abon_price = price * 10 * 80 // 100  # 20% discount
        convs.append(("assistant", f"Записала, {name}! Кстати, для {job_word} у нас есть абонемент на десять моек со скидкой двадцать процентов — {spell_price(abon_price)}. Могу рассказать подробнее при визите. Ждём вас!"))
    else:
        convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Помоем быстро, не задержим! До встречи!"))

    return convs

def scenario_subscription():
    """Client asking about subscription/абонемент."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["express"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("слышал, у вас абонементы есть. Расскажите?")))
    convs.append(("assistant", f"Да, конечно! У нас есть несколько вариантов абонементов. Абонемент на пять моек — скидка десять процентов, на десять моек — скидка двадцать процентов, на двадцать моек — скидка двадцать пять процентов. Подскажите, какой у вас автомобиль, чтобы я рассчитал стоимость?"))
    convs.append(("user", make_user_line(f"{car_mention}")))

    abon5 = price * 5 * 90 // 100
    abon10 = price * 10 * 80 // 100
    abon20 = price * 20 * 75 // 100

    convs.append(("assistant", f"Для {car} экспресс-мойка стоит {spell_price(price)}. Абонемент на пять моек — {spell_price(abon5)}, на десять — {spell_price(abon10)}, на двадцать — {spell_price(abon20)}. Какой вариант вас интересует?"))

    choice = random.choice(["пять", "десять", "двадцать"])
    abon_chosen = {"пять": abon5, "десять": abon10, "двадцать": abon20}[choice]
    convs.append(("user", make_user_line(f"давайте на {choice} моек")))
    convs.append(("assistant", f"Отличный выбор! Абонемент на {choice} моек — {spell_price(abon_chosen)}. Оплатить можно при первом визите. Срок действия — шесть месяцев. Хотите записаться на первую мойку?"))
    convs.append(("user", make_user_line(f"да, давайте {day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. При визите оформим абонемент. До встречи!"))

    return convs

def scenario_scratch_worry():
    """Client worried about scratches on new car."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))

    worries = [
        "машина новая, боюсь, что поцарапаете",
        "только из салона забрал, хочу помыть, но переживаю за лак",
        "у меня новая тачка, а то слышал, что на мойках царапают",
        "машине месяц, можно аккуратно помыть?",
    ]
    convs.append(("user", make_user_line(random.choice(worries))))
    convs.append(("assistant", f"Понимаю ваше беспокойство! Мы используем только бесконтактную мойку высокого давления и профессиональные микрофибровые материалы. Никаких губок и щёток. Для новых автомобилей рекомендую комплексную мойку с нанесением воска — он создаёт защитный слой. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))

    wax_price = 200
    convs.append(("assistant", f"Комплексная мойка для {car} — {spell_price(price)}, плюс воск — {spell_price(wax_price)}. Итого — {spell_price(price + wax_price)}. Всё максимально бережно. Когда вам удобно?"))
    convs.append(("user", make_user_line(f"давайте {day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Не переживайте, ваш {car} будет в надёжных руках. Ждём вас {day} к {time}!"))

    return convs

def scenario_fleet():
    """Fleet manager booking multiple cars."""
    wash_name = random.choice(WASH_NAMES)
    name, g = pick_name()
    num_cars = random.randint(5, 15)

    companies = [
        "Логистик Плюс", "Доставка Про", "ТрансСервис", "АвтоПарк", "Городские перевозки",
        "Экспресс Доставка", "СпецТранс", "АвтоРент", "МегаТакси",
    ]
    company = random.choice(companies)

    car_types = random.choice([
        ("легковых", "sedan"), ("газелей", "commercial"),
        ("кроссоверов", "crossover"), ("фургонов", "commercial"),
    ])
    car_type_name, cat = car_types
    price = rand_price(*PRICE[cat]["express"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"я из компании «{company}», нужно помыть {num_cars} машин. Работаете с юрлицами?")))
    convs.append(("assistant", f"Здравствуйте! Да, мы работаем с корпоративными клиентами. Для автопарков от пяти машин предлагаем скидку от десяти до двадцати процентов. Подскажите, какие автомобили в вашем автопарке?"))
    convs.append(("user", make_user_line(f"{num_cars} {car_type_name}")))

    discount = 15 if num_cars >= 10 else 10
    total = price * num_cars * (100 - discount) // 100

    convs.append(("assistant", f"Хорошо. Экспресс-мойка одного автомобиля — {spell_price(price)}. При заказе на {num_cars} машин предоставляем скидку {discount} процентов. Итого за весь автопарк — {spell_price(total)}. Можем составить удобный график. Как часто нужна мойка?"))

    freq = random.choice(["раз в неделю", "два раза в неделю", "раз в две недели", "каждый день"])
    convs.append(("user", make_user_line(f"{freq}")))
    convs.append(("assistant", f"Отлично! Предлагаю оформить договор на регулярное обслуживание. Я подготовлю коммерческое предложение. Могу отправить на электронную почту или обсудить при встрече. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Спасибо, {name}! Когда удобно приехать для обсуждения деталей? Мы работаем ежедневно с восьми до двадцати одного."))
    convs.append(("user", make_user_line("завтра подъеду после обеда")))
    convs.append(("assistant", f"Будем ждать вас, {name}! До встречи!"))

    return convs

def scenario_wait_vs_leave():
    """Client wants to wait vs leave car."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"хочу записаться на комплексную мойку. А можно подождать у вас?")))
    convs.append(("assistant", f"Конечно! У нас есть зона ожидания с удобными диванами, Wi-Fi, кофе и чай — бесплатно. Комплексная мойка занимает около часа. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Комплексная мойка для {car} — {spell_price(price)}, примерно один час. На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Располагайтесь в зоне ожидания — через час машина будет готова. До встречи!"))

    return convs

def scenario_products_question():
    """Client asking about products used."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))

    questions = [
        "а какой шампунь вы используете? Не поцарапает?",
        "чем моете? У меня тёмная машина, разводы будут?",
        "какие средства используете? Мне важно, чтобы безопасные",
        "а вы не щётками моете? Я читал, что щётки царапают",
    ]
    convs.append(("user", make_user_line(random.choice(questions))))
    convs.append(("assistant", f"Отличный вопрос! Мы используем только профессиональную автохимию — pH-нейтральные шампуни, не повреждающие лакокрасочное покрытие. Моем бесконтактным методом высокого давления, протираем исключительно микрофиброй. Никаких губок и щёток. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Комплексная мойка для {car} — {spell_price(price)}. После мойки сушим турбосушкой и протираем, чтобы не было разводов. Когда вам удобно?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Уверена, результат вам понравится. Ждём вас {day} к {time}!"))

    return convs

def scenario_seasonal_antikor():
    """Seasonal services - антикор/реагенты."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    antikor_price = rand_price(*ANTIKOR_PRICES)
    wash_price = rand_price(*PRICE[cat]["complex"])

    seasons = [
        ("хочу антикоррозийную обработку перед зимой", "перед зимой", "Антикоррозийная обработка"),
        ("надо реагенты смыть после зимы, днище помыть", "после зимы", "Мойка днища и арок от реагентов"),
        ("весна, хочу смыть соль с машины и обработать днище", "весной", "Комплексная мойка с обработкой днища"),
        ("перед зимой хочу подготовить машину, обработать пороги", "перед зимой", "Антикоррозийная обработка порогов и арок"),
    ]
    request, season_word, service_name = random.choice(seasons)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(request)))
    convs.append(("assistant", f"Правильно, что думаете об этом заранее! {service_name} — важная процедура для защиты кузова. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))

    total = antikor_price + wash_price
    convs.append(("assistant", f"Для {car}: {service_name.lower()} — {spell_price(antikor_price)}, плюс комплексная мойка — {spell_price(wash_price)}. Итого — {spell_price(total)}. Работа займёт два-три часа. Когда вам удобно?"))
    convs.append(("user", make_user_line(f"давайте {day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. {season_word.capitalize()} это особенно актуально. До встречи!"))

    return convs

def scenario_large_vehicle():
    """Client bringing very large vehicle (газель, спринтер)."""
    cars_large = [c for c in CARS if c[1] == "commercial"]
    car, cat = random.choice(cars_large)
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    price = rand_price(*PRICE[cat]["express"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"у меня {car}, берёте такие большие?")))
    convs.append(("assistant", f"Да, конечно! Мы моем коммерческий транспорт, включая {car}. Бокс позволяет принять автомобили любого размера."))
    convs.append(("user", make_user_line("а сколько стоит?")))
    convs.append(("assistant", f"Экспресс-мойка для {car} — {spell_price(price)}. Комплексная с салоном — {spell_price(rand_price(*PRICE[cat]['complex']))}. Что выберете?"))
    convs.append(("user", make_user_line("давайте экспресс")))
    convs.append(("assistant", f"Хорошо, экспресс-мойка за {spell_price(price)}. На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас с {car} {day} к {time}. До встречи!"))

    return convs

def scenario_complaint():
    """Client upset about previous wash quality."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)

    complaints = [
        "в прошлый раз плохо помыли, разводы остались",
        "был у вас вчера, а на заднем бампере грязь осталась",
        "диски не домыли в прошлый раз, заплатил за комплекс",
        "в салоне не пропылесосили, хотя обещали",
        "после мойки нашёл царапину на двери",
    ]
    complaint = random.choice(complaints)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"я хочу пожаловаться — {complaint}")))
    convs.append(("assistant", f"Мне очень жаль, что так произошло! Это не тот уровень качества, который мы хотим предоставлять. Подскажите, пожалуйста, ваше имя и когда вы были у нас?"))
    convs.append(("user", make_user_line(f"{name}, был вчера")))
    convs.append(("assistant", f"Спасибо, {name}. Приношу извинения за неудобства. Мы готовы бесплатно перемыть ваш автомобиль. Когда вам удобно подъехать?"))

    if random.random() < 0.5:
        convs.append(("user", make_user_line("сегодня могу подъехать")))
        convs.append(("assistant", f"Приезжайте, {name}, мы всё исправим. Лично проконтролирую качество. Ждём вас!"))
    else:
        day, time = pick_day_time()
        convs.append(("user", make_user_line(f"давайте {day}")))
        convs.append(("assistant", f"Хорошо, ждём вас {day}. Всё исправим, {name}. Ещё раз приносим извинения!"))

    return convs

def scenario_hand_vs_auto():
    """Client comparing hand wash vs automatic."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("а у вас ручная мойка или автоматическая?")))
    convs.append(("assistant", f"У нас ручная бесконтактная мойка. Это значит, что мастер моет вашу машину вручную, используя аппарат высокого давления и профессиональную микрофибру. В отличие от автоматических моек с щётками, мы не оставляем микроцарапин на кузове."))
    convs.append(("user", make_user_line(f"а по времени сколько? У меня {car_mention}")))
    convs.append(("assistant", f"Комплексная ручная мойка для {car} — около часа, стоимость {spell_price(price)}. Экспресс — тридцать минут, дешевле. Что предпочтёте?"))

    if random.random() < 0.5:
        convs.append(("user", make_user_line("давайте комплексную")))
        chosen_price = price
    else:
        express_price = rand_price(*PRICE[cat]["express"])
        convs.append(("user", make_user_line("экспресс давайте, быстрее")))
        chosen_price = express_price

    convs.append(("assistant", f"Хорошо! На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. До встречи!"))

    return convs

def scenario_motorcycle():
    """Motorcycle wash."""
    moto = random.choice(MOTORCYCLES)
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    price = rand_price(*MOTO_WASH)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"а мотоциклы моете? У меня {moto}")))
    convs.append(("assistant", f"Да, мы моем мотоциклы! Используем деликатную мойку низкого давления, чтобы не повредить электронику и хромированные элементы. Стоимость мойки мотоцикла — {spell_price(price)}, занимает около двадцати минут."))
    convs.append(("user", make_user_line("отлично, запишите меня")))
    convs.append(("assistant", f"С удовольствием! На когда?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}, мойка мотоцикла {moto}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Аккуратно помоем вашу технику! До встречи!"))

    return convs

def scenario_child_seat():
    """Client with child seat that needs cleaning."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    seat_price = random.choice([500, 800, 1000])
    wash_price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("можно детское кресло почистить? Ребёнок всё залил соком")))
    convs.append(("assistant", f"Конечно! Мы чистим детские автокресла — используем безопасные гипоаллергенные средства. Стоимость чистки детского кресла — {spell_price(seat_price)}. Хотите заодно помыть машину?"))
    convs.append(("user", make_user_line(f"да, давайте и машину тоже. У меня {car_mention}")))

    total = wash_price + seat_price
    convs.append(("assistant", f"Комплексная мойка {car} — {spell_price(wash_price)}, плюс чистка детского кресла — {spell_price(seat_price)}. Итого — {spell_price(total)}. Когда удобно?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Кресло будет чистым и безопасным для малыша! До встречи!"))

    return convs

def scenario_pre_inspection():
    """Pre-inspection car prep."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["complex"])
    engine_price = rand_price(*PRICE[cat]["engine"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("мне на техосмотр скоро, хочу машину привести в порядок")))
    convs.append(("assistant", f"Понимаю! Для техосмотра рекомендую комплексную мойку кузова и салона, а также мойку двигателя — чтобы всё выглядело аккуратно. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))

    total = price + engine_price
    convs.append(("assistant", f"Для {car}: комплексная мойка — {spell_price(price)}, мойка двигателя — {spell_price(engine_price)}. Итого — {spell_price(total)}. Когда техосмотр?"))
    convs.append(("user", make_user_line(f"через неделю, хочу {day} помыть")))
    convs.append(("assistant", f"Отлично, записываю на {day}, {time} подойдёт?"))
    convs.append(("user", make_user_line("да, нормально")))
    convs.append(("assistant", f"Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Записала, {name}! Ждём вас {day} к {time}. Подготовим машину к техосмотру на отлично! До встречи!"))

    return convs

def scenario_late_hours():
    """Client asking about operating hours late evening / early morning."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["express"])

    hours_variants = [
        ("а вы до скольки работаете? Мне бы вечером, часов в девять", "девять вечера", "Мы работаем до десяти вечера, так что в девять — без проблем!"),
        ("можно рано утром? Часов в семь?", "семь утра", "Мы открываемся в восемь утра. Можем записать вас на восемь — самое раннее время."),
        ("работаете в воскресенье?", "воскресенье", "Да, мы работаем без выходных, с восьми до двадцати двух!"),
        ("а ночью работаете?", "ночь", "К сожалению, ночью мы не работаем. Часы работы — с восьми утра до десяти вечера ежедневно. Могу записать на раннее утро или поздний вечер."),
        ("в праздники работаете?", "праздники", "Да, мы работаем в праздничные дни по обычному графику — с восьми до двадцати двух."),
    ]
    question, topic, answer = random.choice(hours_variants)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(question)))
    convs.append(("assistant", answer))
    convs.append(("user", make_user_line(f"хорошо, у меня {car_mention}, запишите на вечер")))
    convs.append(("assistant", f"Экспресс-мойка для {car} — {spell_price(price)}. Записываю на сегодня, восемь вечера. Подойдёт?"))
    convs.append(("user", make_user_line("да, отлично")))
    convs.append(("assistant", f"Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас сегодня вечером. До встречи!"))

    return convs

def scenario_express_rush():
    """Client in a rush, asking about express options."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["express"])

    rush_phrases = [
        "мне очень быстро надо, минут за пятнадцать можно?",
        "я тороплюсь, есть что-то быстрое?",
        "через полчаса встреча, можно молнией помыть?",
        "быстро-быстро, только кузов окатить",
        "у меня мало времени, что самое быстрое?",
    ]

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(random.choice(rush_phrases))))
    convs.append(("assistant", f"Самый быстрый вариант — экспресс-мойка кузова, занимает двадцать-тридцать минут. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Экспресс-мойка для {car} — {spell_price(price)}. Сейчас есть свободный бокс, можете подъехать прямо сейчас!"))
    convs.append(("user", make_user_line("отлично, еду к вам")))
    convs.append(("assistant", f"Как вас зовут, чтобы мастер был готов?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Ждём вас, {name}! Помоем максимально быстро!"))

    return convs

def scenario_loyalty_discount():
    """Regular client asking about loyalty discount."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"я у вас постоянно моюсь, есть скидка для постоянных клиентов?")))
    convs.append(("assistant", f"Конечно! Для постоянных клиентов у нас действует программа лояльности. После пятой мойки — скидка десять процентов, после десятой — пятнадцать процентов. Также есть накопительная карта. Подскажите ваше имя, я проверю вашу историю."))
    convs.append(("user", make_user_line(f"{name}")))

    visits = random.randint(6, 20)
    discount = 10 if visits < 10 else 15
    discounted = price * (100 - discount) // 100

    convs.append(("assistant", f"Нашла вас, {name}! У вас уже {visits} посещений, вам полагается скидка {discount} процентов. Комплексная мойка для вашего автомобиля — {spell_price(discounted)} вместо {spell_price(price)}. Хотите записаться?"))
    convs.append(("user", make_user_line(f"да, давайте {day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Ждём вас, {name}! Спасибо за верность нашей мойке!"))

    return convs

def scenario_full_restoration():
    """Client wanting full restoration (полировка + керамика + салон)."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)

    polish_price = rand_price(*POLIROVKA_PRICES)
    ceramic_price = rand_price(*KERAMIKA_PRICES)
    himchistka_price = rand_price(*HIMCHISTKA_PRICES["full"])
    total = polish_price + ceramic_price + himchistka_price

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"хочу полностью обновить машину — полировка, керамика, салон. Сколько выйдет?")))
    convs.append(("assistant", f"Отличный выбор — комплексное восстановление! Подскажите, какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Для {car}: полировка кузова — {spell_price(polish_price)}, керамическое покрытие — {spell_price(ceramic_price)}, полная химчистка салона — {spell_price(himchistka_price)}. Итого — {spell_price(total)}. Работа займёт два-три дня, автомобиль нужно будет оставить."))
    convs.append(("user", make_user_line("ого, серьёзная сумма... но давайте, машина того стоит")))
    convs.append(("assistant", f"Машина будет как новая, не пожалеете! Когда удобно привезти?"))
    convs.append(("user", make_user_line(f"давайте {day} с утра")))
    convs.append(("assistant", f"Записываю: {day}, к девяти утра. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Спасибо, {name}! Ваш {car} будет в идеальном состоянии. Ждём вас {day} утром. До встречи!"))

    return convs

def scenario_simple_booking():
    """Simple straightforward booking."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)

    service_type = random.choice(["express", "complex"])
    if service_type == "express":
        price = rand_price(*PRICE[cat]["express"])
        service_name = "Экспресс-мойка"
        duration = "около тридцати минут"
    else:
        price = rand_price(*PRICE[cat]["complex"])
        service_name = "Комплексная мойка кузова и салона"
        duration = "примерно один час"

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))

    requests = [
        "хочу помыть машину", "запишите на мойку", "мне бы машину помыть",
        "нужна мойка", "можно записаться?", "машину помыть хочу",
    ]
    convs.append(("user", make_user_line(random.choice(requests))))
    convs.append(("assistant", f"Конечно! Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"{service_name} для {car} — {spell_price(price)}, {duration}. На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Хорошего дня!"))

    return convs

def scenario_price_inquiry():
    """Client asking about prices for different services."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)

    express_price = rand_price(*PRICE[cat]["express"])
    complex_price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))

    price_questions = [
        "чё по ценам?", "сколько стоит мойка?", "прайс какой?",
        "расскажите по ценам", "какие расценки?",
    ]
    convs.append(("user", make_user_line(random.choice(price_questions))))
    convs.append(("assistant", f"Стоимость зависит от автомобиля и вида мойки. Подскажите, какая у вас машина?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Для {car}: экспресс-мойка кузова — {spell_price(express_price)}, комплексная мойка с салоном — {spell_price(complex_price)}. Что вас интересует?"))

    if random.random() < 0.5:
        convs.append(("user", make_user_line("давайте комплексную")))
        convs.append(("assistant", f"Отлично! На когда записать?"))
    else:
        convs.append(("user", make_user_line("экспресс хватит")))
        convs.append(("assistant", f"Хорошо! На когда записать?"))

    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. До встречи!"))

    return convs

def scenario_reschedule():
    """Client rescheduling an appointment."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    old_day, old_time = pick_day_time()
    new_day, new_time = pick_day_time()
    while new_day == old_day:
        new_day, new_time = pick_day_time()

    services = ["комплексная мойка", "экспресс-мойка", "химчистка салона", "полировка"]
    service = random.choice(services)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"я записан на {old_day}, хочу перенести")))
    convs.append(("assistant", f"Конечно! Подскажите ваше имя, чтобы я нашла запись."))
    convs.append(("user", make_user_line(f"{name}")))
    convs.append(("assistant", f"Нашла, {name}! {service.capitalize()}, {old_day}, {old_time}. На какое время перенести?"))
    convs.append(("user", make_user_line(f"можно {new_day} на {new_time}?")))
    convs.append(("assistant", f"{new_day.capitalize()}, {new_time} — свободно! Переношу запись. Ждём вас!"))
    convs.append(("user", make_user_line("спасибо!")))
    convs.append(("assistant", f"Пожалуйста, {name}! Всего доброго!"))

    return convs

def scenario_cancel():
    """Client cancelling an appointment."""
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"хочу отменить запись на {day}")))
    convs.append(("assistant", f"Подскажите ваше имя, пожалуйста."))
    convs.append(("user", make_user_line(f"{name}")))
    convs.append(("assistant", f"Нашла, {name}. Запись на {day}, {time} отменена. Будем рады видеть вас в другой раз!"))
    convs.append(("user", make_user_line("спасибо, до свидания")))
    convs.append(("assistant", f"До свидания, {name}! Хорошего дня!"))

    return convs

def scenario_wax_coating():
    """Client asking about wax/protective coating after wash."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    wash_price = rand_price(*PRICE[cat]["complex"])
    wax_price = random.choice([200, 300, 500])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("а воском можете покрыть после мойки? Чтобы блестела")))
    convs.append(("assistant", f"Конечно! После комплексной мойки можем нанести жидкий воск — он придаёт блеск и защищает кузов от грязи на одну-две недели. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    total = wash_price + wax_price
    convs.append(("assistant", f"Комплексная мойка {car} — {spell_price(wash_price)}, плюс обработка воском — {spell_price(wax_price)}. Итого — {spell_price(total)}. На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ваш {car} будет блестеть! Ждём {day} к {time}. До встречи!"))

    return convs

def scenario_engine_wash():
    """Client wants engine wash."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    engine_price = rand_price(*PRICE[cat]["engine"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("движок помыть можете?")))
    convs.append(("assistant", f"Да, мы делаем мойку двигателя! Используем специальные средства и пар, чтобы не повредить электрику. Подскажите, какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Мойка двигателя для {car} — {spell_price(engine_price)}, занимает около сорока минут. Хотите заодно помыть кузов?"))

    if random.random() < 0.5:
        wash_price = rand_price(*PRICE[cat]["express"])
        total = engine_price + wash_price
        convs.append(("user", make_user_line("да, давайте и кузов тоже")))
        convs.append(("assistant", f"Мойка двигателя плюс экспресс-мойка кузова — итого {spell_price(total)}. На когда записать?"))
    else:
        convs.append(("user", make_user_line("нет, только движок")))
        convs.append(("assistant", f"Хорошо, только мойка двигателя — {spell_price(engine_price)}. На когда записать?"))

    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. До встречи!"))

    return convs

def scenario_detailing():
    """Client asking about detailing."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    detail_price = rand_price(*DETAILING_PRICES)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("интересует детейлинг, что входит и сколько стоит?")))
    convs.append(("assistant", f"Детейлинг — это комплексный уход: глубокая мойка кузова и колёс, удаление битума и металлических вкраплений, полировка лакокрасочного покрытия, нанесение защитного состава, полная химчистка салона, обработка кожи и пластика. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Для {car} стоимость детейлинга — от {spell_price(detail_price)}. Работа занимает шесть-десять часов, автомобиль нужно оставить. Хотите записаться?"))
    convs.append(("user", make_user_line("да, хочу")))
    convs.append(("assistant", f"На когда вас записать?"))
    convs.append(("user", make_user_line(f"{day} с утра")))
    convs.append(("assistant", f"Записываю: {day}, к девяти утра. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Спасибо, {name}! Ваш {car} будет как новый. Ждём вас {day} утром!"))

    return convs

def scenario_presale():
    """Pre-sale preparation."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = random.choice([7000, 8000, 9000, 10000])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("продаю машину, хочу подготовить к продаже")))
    convs.append(("assistant", f"Предпродажная подготовка — отличное вложение! Включает полную мойку, химчистку салона, полировку кузова, обработку пластика и чернение шин. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Предпродажная подготовка для {car} — {spell_price(price)}. Работа занимает пять-семь часов. Машину нужно будет оставить. Когда удобно?"))
    convs.append(("user", make_user_line(f"{day} с утра")))
    convs.append(("assistant", f"Записываю: {day}, к девяти утра. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Отлично, {name}! После наших процедур {car} будет выглядеть максимально привлекательно для покупателей. Ждём вас {day}!"))

    return convs

def scenario_ceramic():
    """Client asking about ceramic coating."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    ceramic_price = rand_price(*KERAMIKA_PRICES)
    polish_price = rand_price(*POLIROVKA_PRICES)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("хочу керамику нанести, сколько стоит?")))
    convs.append(("assistant", f"Керамическое покрытие — это долговременная защита кузова на один-три года. Перед нанесением обязательна полировка. Подскажите, какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    total = ceramic_price + polish_price
    convs.append(("assistant", f"Для {car}: полировка — {spell_price(polish_price)}, керамическое покрытие — {spell_price(ceramic_price)}. Итого — {spell_price(total)}. Работа займёт полтора-два дня. Когда привезёте?"))
    convs.append(("user", make_user_line(f"давайте {day}")))
    convs.append(("assistant", f"Записываю: {day}, привозите к девяти утра. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Спасибо, {name}! Ваш {car} получит надёжную защиту. Ждём {day} утром!"))

    return convs

def scenario_himchistka():
    """Full or partial interior cleaning."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)

    if random.random() < 0.5:
        price = rand_price(*HIMCHISTKA_PRICES["full"])
        service = "полная химчистка салона"
        duration = "четыре-шесть часов"
    else:
        price = rand_price(*HIMCHISTKA_PRICES["partial"])
        service = "частичная химчистка салона"
        duration = "два-три часа"

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("хочу салон почистить")))
    convs.append(("assistant", f"Конечно! У нас есть полная и частичная химчистка салона. Подскажите, какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"{service.capitalize()} для {car} — {spell_price(price)}, займёт {duration}. Хотите записаться?"))
    convs.append(("user", make_user_line("да, запишите")))
    convs.append(("assistant", f"На когда?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. До встречи!"))

    return convs

def scenario_smoke_smell():
    """Car smells like smoke, needs odor removal."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(3000, 6000, 500)

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("машина воняет сигаретами, можете убрать запах?")))
    convs.append(("assistant", f"Да, мы делаем озонирование салона — это процедура, которая полностью устраняет запах табака. Обычно совмещаем с химчисткой для лучшего результата. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Химчистка салона с озонированием для {car} — {spell_price(price)}. Занимает пять-шесть часов. Запах уйдёт полностью. Когда привезёте?"))
    convs.append(("user", make_user_line(f"давайте {day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! После озонирования салон будет пахнуть свежестью. Ждём вас {day} к {time}!"))

    return convs

def scenario_gift_certificate():
    """Client asking about gift certificate."""
    wash_name = random.choice(WASH_NAMES)
    name, g = pick_name()

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("хочу подарить другу сертификат на мойку, есть такое?")))
    convs.append(("assistant", f"Да, у нас есть подарочные сертификаты! Можно выбрать на фиксированную сумму — одна тысяча, две тысячи, три тысячи или пять тысяч рублей. Также можно оформить на конкретную услугу. Какой вариант вас интересует?"))

    amounts = [("одна тысяча", 1000), ("две тысячи", 2000), ("три тысячи", 3000), ("пять тысяч", 5000)]
    chosen_text, chosen_val = random.choice(amounts)
    convs.append(("user", make_user_line(f"давайте на {chosen_text} рублей")))
    convs.append(("assistant", f"Отлично! Сертификат на {chosen_text} рублей. Срок действия — шесть месяцев. Можете приобрести у нас на мойке или я могу оформить заказ прямо сейчас. Как вам удобнее?"))
    convs.append(("user", make_user_line("заеду к вам за ним")))
    convs.append(("assistant", f"Хорошо! Мы работаем ежедневно с восьми до двадцати двух. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Спасибо, {name}! Ждём вас за сертификатом. Отличный подарок, кстати! До встречи!"))

    return convs

def scenario_tires_blackening():
    """Client wants tire blackening / wheel cleaning."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    wash_price = rand_price(*PRICE[cat]["complex"])
    tire_price = random.choice([200, 300, 500])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("а чернение шин делаете?")))
    convs.append(("assistant", f"Да, конечно! Чернение шин придаёт колёсам ухоженный вид. Стоимость — {spell_price(tire_price)}. Обычно делаем вместе с мойкой. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    total = wash_price + tire_price
    convs.append(("assistant", f"Комплексная мойка для {car} — {spell_price(wash_price)}, плюс чернение шин — {spell_price(tire_price)}. Итого — {spell_price(total)}. На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. До встречи!"))

    return convs

def scenario_bitum_removal():
    """Client needs bitumen/tar spot removal."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    wash_price = rand_price(*PRICE[cat]["complex"])
    bitum_price = random.choice([500, 800, 1000])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("по новому асфальту проехал, весь порог и двери в битуме. Можете убрать?")))
    convs.append(("assistant", f"Да, мы удаляем битумные пятна специальным составом, безопасным для лака. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    total = wash_price + bitum_price
    convs.append(("assistant", f"Удаление битума — {spell_price(bitum_price)}, плюс комплексная мойка — {spell_price(wash_price)}. Итого — {spell_price(total)}. Когда удобно?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Уберём весь битум без следа. Ждём вас {day} к {time}!"))

    return convs

def scenario_multiple_services_question():
    """Client asking about multiple services, choosing one."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)

    express_price = rand_price(*PRICE[cat]["express"])
    complex_price = rand_price(*PRICE[cat]["complex"])
    engine_price = rand_price(*PRICE[cat]["engine"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"у меня {car_mention}, расскажите все услуги и цены")))
    convs.append(("assistant", f"Для {car} доступны: экспресс-мойка кузова — {spell_price(express_price)}, около тридцати минут; комплексная мойка кузова и салона — {spell_price(complex_price)}, примерно один час; мойка двигателя — {spell_price(engine_price)}, сорок минут. Также есть химчистка, полировка, керамика и детейлинг. Что вас интересует?"))
    convs.append(("user", make_user_line("давайте комплекс и движок заодно")))
    total = complex_price + engine_price
    convs.append(("assistant", f"Отлично! Комплексная мойка плюс мойка двигателя — итого {spell_price(total)}. На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. До встречи!"))

    return convs

def scenario_leather_care():
    """Client with leather seats wanting special care."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = random.choice([2000, 2500, 3000, 3500])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("у меня кожаный салон, нужна обработка кожи. Делаете?")))
    convs.append(("assistant", f"Да, конечно! Обработка кожаного салона включает чистку, увлажнение и нанесение защитного крема. Кожа становится мягкой и защищённой от трещин. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Обработка кожаного салона для {car} — {spell_price(price)}. Работа занимает два-три часа. Когда удобно?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Позаботимся о вашей коже как следует. Ждём {day} к {time}!"))

    return convs

def scenario_headlight_polish():
    """Client wants headlight polishing."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = random.choice([1500, 2000, 2500, 3000])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("фары помутнели, можете отполировать?")))
    convs.append(("assistant", f"Да, мы делаем полировку фар! После обработки они становятся прозрачными, как новые, и свет значительно улучшается. Стоимость — {spell_price(price)} за пару. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Полировка фар для {car} — {spell_price(price)}, занимает около часа. Хотите записаться?"))
    convs.append(("user", make_user_line("да, давайте")))
    convs.append(("assistant", f"На когда?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Ждём вас {day} к {time}. Фары будут как новые!"))

    return convs

def scenario_rain_protection():
    """Client asking about rain/hydrophobic coating for windshield."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = random.choice([1000, 1500, 2000])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("а антидождь на лобовое делаете?")))
    convs.append(("assistant", f"Да! Гидрофобное покрытие «антидождь» отталкивает воду — капли скатываются на скорости, видимость значительно улучшается. Стоимость — {spell_price(price)} за лобовое стекло. Можно обработать все стёкла — будет дороже. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}, давайте только лобовое")))
    convs.append(("assistant", f"Хорошо, антидождь на лобовое стекло {car} — {spell_price(price)}. На когда записать?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! В дождь будете видеть дорогу гораздо лучше. Ждём {day} к {time}!"))

    return convs

def scenario_trunk_cleaning():
    """Client needs trunk cleaned specifically."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = random.choice([1000, 1500, 2000])

    reasons = [
        "в багажнике масло разлилось", "рыбу возил, запах не выветривается",
        "стройматериалы возил, весь в пыли", "продукты протекли в багажник",
    ]

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line(f"мне нужно багажник почистить, {random.choice(reasons)}")))
    convs.append(("assistant", f"Понимаю! Сделаем химчистку багажного отделения с удалением запаха. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Химчистка багажника {car} — {spell_price(price)}, займёт полтора-два часа. Когда удобно?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Готово, {name}! Вычистим багажник до идеала. Ждём {day} к {time}!"))

    return convs

def scenario_first_visit_question():
    """First-time client asking how everything works."""
    car, cat = pick_car()
    name, g = pick_name()
    wash_name = random.choice(WASH_NAMES)
    day, time = pick_day_time()
    car_mention = get_car_mention(car)
    price = rand_price(*PRICE[cat]["complex"])

    convs = []
    convs.append(("user", make_user_line(random.choice(GREETINGS_USER))))
    convs.append(("assistant", random.choice(GREETINGS_ADMIN).format(name=wash_name)))
    convs.append(("user", make_user_line("я первый раз к вам, как всё устроено? Нужно записываться или можно так приехать?")))
    convs.append(("assistant", f"Рады новому клиенту! Лучше записаться заранее, чтобы не ждать. Вы приезжаете к назначенному времени, оставляете ключи, и мы начинаем работу. Есть зона ожидания с Wi-Fi и кофе. Или можете оставить машину и забрать позже — как удобнее. Какой у вас автомобиль?"))
    convs.append(("user", make_user_line(f"{car_mention}")))
    convs.append(("assistant", f"Комплексная мойка для {car} — {spell_price(price)}, около часа. Хотите записаться?"))
    convs.append(("user", make_user_line("да, давайте попробую")))
    convs.append(("assistant", f"Отлично! На когда?"))
    convs.append(("user", make_user_line(f"{day} на {time}")))
    convs.append(("assistant", f"Записываю: {day}, {time}. Как вас зовут?"))
    convs.append(("user", make_user_line(name)))
    convs.append(("assistant", f"Добро пожаловать, {name}! Ждём вас {day} к {time}. Уверены, вам понравится! До встречи!"))

    return convs

# All scenario functions
SCENARIOS = [
    (scenario_dirty_offroad, 25),
    (scenario_pet_hair, 20),
    (scenario_spill_urgent, 20),
    (scenario_taxi_quick, 20),
    (scenario_subscription, 20),
    (scenario_scratch_worry, 20),
    (scenario_fleet, 15),
    (scenario_wait_vs_leave, 15),
    (scenario_products_question, 20),
    (scenario_seasonal_antikor, 20),
    (scenario_large_vehicle, 15),
    (scenario_complaint, 15),
    (scenario_hand_vs_auto, 15),
    (scenario_motorcycle, 15),
    (scenario_child_seat, 15),
    (scenario_pre_inspection, 15),
    (scenario_late_hours, 15),
    (scenario_express_rush, 20),
    (scenario_loyalty_discount, 15),
    (scenario_full_restoration, 15),
    (scenario_simple_booking, 30),
    (scenario_price_inquiry, 25),
    (scenario_reschedule, 15),
    (scenario_cancel, 10),
    (scenario_wax_coating, 15),
    (scenario_engine_wash, 15),
    (scenario_detailing, 10),
    (scenario_presale, 10),
    (scenario_ceramic, 10),
    (scenario_himchistka, 15),
    (scenario_smoke_smell, 10),
    (scenario_gift_certificate, 5),
    (scenario_tires_blackening, 10),
    (scenario_bitum_removal, 10),
    (scenario_multiple_services_question, 10),
    (scenario_leather_care, 8),
    (scenario_headlight_polish, 8),
    (scenario_rain_protection, 8),
    (scenario_trunk_cleaning, 8),
    (scenario_first_visit_question, 8),
]

def main():
    dialogs = []

    # Generate according to weights
    for scenario_fn, count in SCENARIOS:
        for _ in range(count):
            convs = scenario_fn()
            messages = [{"role": "system", "content": SYSTEM}]
            for role, content in convs:
                messages.append({"role": role, "content": content})
            dialogs.append({"conversations": messages})

    # Shuffle
    random.shuffle(dialogs)

    # Take exactly 500
    dialogs = dialogs[:500]

    # Verify we have 500
    if len(dialogs) < 500:
        # Fill remaining with simple bookings
        while len(dialogs) < 500:
            convs = scenario_simple_booking()
            messages = [{"role": "system", "content": SYSTEM}]
            for role, content in convs:
                messages.append({"role": role, "content": content})
            dialogs.append({"conversations": messages})

    random.shuffle(dialogs)

    outpath = os.path.join(os.path.dirname(__file__), "carwash_dialogs_extra.jsonl")
    with open(outpath, "w", encoding="utf-8") as f:
        for d in dialogs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Generated {len(dialogs)} dialogs to {outpath}")

if __name__ == "__main__":
    main()
