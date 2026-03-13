#!/usr/bin/env python3
"""Generate 2000 'universal operator skills' dialogs across all verticals.
Focus: STT noise handling, unclear speech, pauses, empathy, natural operator behavior."""

import json, random, os

random.seed(5005)

VERTICALS = {
    "barbershop": {
        "sys": "Вы — администратор барбершопа «Бородач». Помогаете клиентам записаться на стрижку или другую услугу, выбрать мастера и удобное время. Говорите дружелюбно, по делу.",
        "greets": ["Барбершоп «Бородач», здарова!","Барбершоп «Бородач», добрый день!","«Бородач», слушаю!"],
        "services": ["мужская стрижка","стрижка бороды","комплекс стрижка и борода","королевское бритьё","камуфляж седины","детская стрижка","окрашивание","укладка"],
        "masters": ["Дмитрий","Артём","Кирилл","Алексей","Роман","Сергей"],
        "prices": {"мужская стрижка":"полторы тысячи","стрижка бороды":"тысяча двести","комплекс стрижка и борода":"две тысячи пятьсот","королевское бритьё":"две тысячи","камуфляж седины":"две тысячи пятьсот","детская стрижка":"тысяча","окрашивание":"четыре тысячи","укладка":"семьсот"},
        "hours": "ежедневно с десяти до двадцати одного",
    },
    "salon": {
        "sys": "Вы — администратор салона красоты «Гармония». Помогаете клиентам записаться на услуги, выбрать мастера и удобное время. Говорите вежливо, профессионально и тепло.",
        "greets": ["Салон «Гармония», здравствуйте!","Салон красоты «Гармония», добрый день!","«Гармония», слушаю вас!"],
        "services": ["стрижка женская","окрашивание","балаяж","маникюр","маникюр с гель-лаком","педикюр","наращивание ресниц","ламинирование бровей","чистка лица","пилинг","массаж","кератиновое выпрямление","укладка"],
        "masters": ["Анна","Светлана","Марина","Юлия","Татьяна","Дарья","Елена","Людмила Сергеевна"],
        "prices": {"стрижка женская":"три тысячи","окрашивание":"пять тысяч","балаяж":"девять тысяч","маникюр":"две тысячи","маникюр с гель-лаком":"три тысячи","педикюр":"три тысячи","наращивание ресниц":"четыре тысячи","ламинирование бровей":"две тысячи пятьсот","чистка лица":"пять тысяч","пилинг":"четыре тысячи","массаж":"четыре тысячи","кератиновое выпрямление":"восемь тысяч","укладка":"две тысячи"},
        "hours": "понедельник-суббота с десяти до двадцати, воскресенье — выходной",
    },
    "restaurant": {
        "sys": "Вы — администратор ресторана «Белый сад». Помогаете гостям забронировать столик, выбрать зал и обсудить детали визита. Говорите вежливо, гостеприимно и профессионально.",
        "greets": ["Ресторан «Белый сад», здравствуйте!","«Белый сад», добрый день!","Ресторан «Белый сад», чем могу помочь?"],
        "services": ["столик на двоих","столик на четверых","банкет","VIP-зал","каминный зал","летняя веранда"],
        "masters": [],
        "prices": {"средний чек":"две тысячи пятьсот рублей","банкетное меню":"от трёх тысяч на персону","VIP-зал":"от пяти тысяч депозит"},
        "hours": "ежедневно с двенадцати до двадцати трёх",
    },
    "carwash": {
        "sys": "Вы — администратор автомойки «АвтоБлеск». Помогаете клиентам записаться на мойку, выбрать тип услуги и удобное время. Говорите вежливо и по делу.",
        "greets": ["Автомойка «АвтоБлеск», здравствуйте!","«АвтоБлеск», добрый день!","Автомойка «АвтоБлеск», слушаю!"],
        "services": ["экспресс-мойка","комплексная мойка","мойка с воском","полная мойка","химчистка салона","полировка кузова","керамическое покрытие","мойка двигателя"],
        "masters": [],
        "prices": {"экспресс-мойка":"шестьсот рублей","комплексная мойка":"тысяча двести","мойка с воском":"тысяча","полная мойка":"тысяча восемьсот","химчистка салона":"четыре тысячи","полировка кузова":"семь тысяч","керамическое покрытие":"двадцать тысяч","мойка двигателя":"тысяча двести"},
        "hours": "ежедневно с восьми до двадцати двух",
    },
}

NAMES = ["Александр","Дмитрий","Сергей","Андрей","Михаил","Иван","Максим","Павел","Артём",
         "Николай","Олег","Роман","Евгений","Алексей","Виктор","Денис","Елена","Анна",
         "Мария","Ольга","Наталья","Татьяна","Екатерина","Ирина","Светлана","Юлия","Дарья","Алина"]

DATES = ["завтра","послезавтра","в субботу","в пятницу","в среду","в четверг",
         "на следующей неделе","в эту субботу","в воскресенье","в понедельник","сегодня"]
TIMES = ["в десять","в одиннадцать","в двенадцать","в час","в два","в три","в четыре",
         "в пять","в шесть","в семь","утром","после обеда","вечером"]

PHONE_PFX = ["восемь девять","плюс семь девять","восемь девятьсот"]
NOISE = ["[неразборчиво]","[шум]","[помехи]","[плохая связь]","[шум на фоне]"]
BG_NOISE = ["[слышен ребёнок на фоне]","[шум улицы]","[музыка на фоне]","[шум ветра]",
            "[гул машин]","[разговоры на фоне]","[звук телевизора]","[лай собаки]"]

rc = random.choice
ri = random.randint

def rphone():
    d = [str(ri(0,9)) for _ in range(7)]
    return rc(PHONE_PFX)+" "+"".join(d[:3])+" "+"".join(d[3:5])+" "+"".join(d[5:])

def S(v): return {"role":"system","content":VERTICALS[v]["sys"]}
def A(t): return {"role":"assistant","content":t}
def U(t): return {"role":"user","content":t}

def pick_v(): return rc(list(VERTICALS.keys()))

# ══════════════════════════════════════════
# Category 1: HEAVY STT NOISE (400 dialogs)
# Model must correctly interpret garbled input
# ══════════════════════════════════════════

def gen_garbled_request():
    """User's first request is mostly unintelligible. Model asks to repeat."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]

    garble_type = rc(["noise","cutoff","mumble","background"])
    if garble_type == "noise":
        c.append(U(f"[шум] {rc(NOISE)} хочу [помехи] {svc[:3]}... [неразборчиво]"))
        c.append(A("Простите, очень плохо слышно. Можете повторить, пожалуйста? Вы хотите записаться?"))
    elif garble_type == "cutoff":
        c.append(U(f"Алло, я хот... {rc(NOISE)} ...на {svc[:4]}..."))
        c.append(A("Извините, связь прерывается. Вы хотели записаться? На какую услугу?"))
    elif garble_type == "mumble":
        # Simulate mumbled/fast speech
        words = svc.split()
        mangled = " ".join(w[:max(2,len(w)//2)]+"..." for w in words)
        c.append(U(f"здрсте мне бы на {mangled} ну вы пнимаете"))
        c.append(A(f"Здравствуйте! Если я правильно поняла, вы хотите записаться на {svc}?"))
    else:
        c.append(U(f"{rc(BG_NOISE)} алло, здравствуйте, мне нужно {rc(NOISE)} записаться"))
        c.append(A("Здравствуйте! Слышу вас, но есть помехи. На какую услугу хотите записаться?"))

    c.append(U(f"Да да, на {svc}, {date}"))
    c.append(A(f"Поняла! {svc.capitalize()}, {date}. На какое время?"))
    c.append(U(f"{time}"))
    price_str = vd["prices"].get(svc, "уточню стоимость")
    c.append(A(f"Записываю: {svc}, {date}, {time}. Стоимость {price_str}. На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Спасибо, {name}! Номер телефона для связи?"))
    ph = rphone()
    c.append(U(ph))
    c.append(A(f"Записала! {name}, {svc}, {date}, {time}. Ждём вас!"))
    c.append(U(rc(["Спасибо","Спасибо, до свидания","Ага, спасибо"])))
    c.append(A("До свидания! Хорошего дня!"))
    return c

def gen_noise_throughout():
    """Noise interrupts multiple times during the conversation."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(f"Здравствуйте, {rc(BG_NOISE)} хочу записаться на {svc}"))
    c.append(A(f"Здравствуйте! Записываю на {svc}. Когда вам удобно?"))
    c.append(U(f"{date}... {rc(NOISE)}... {time}"))
    c.append(A(f"Простите, не расслышала время. Повторите, пожалуйста?"))
    c.append(U(f"Говорю, {time}!"))
    c.append(A(f"Поняла, {time}! На чьё имя записываем?"))
    c.append(U(f"{rc(NOISE)} {name}"))
    c.append(A(f"Простите, имя не расслышала. Повторите?"))
    c.append(U(f"{name}! {name.upper()[0]} как {name[0]}...{name}"))
    c.append(A(f"Спасибо, {name}! Записала: {svc}, {date}, {time}. Ждём вас!"))
    c.append(U("Спасибо!"))
    c.append(A("До свидания!"))
    return c

def gen_phone_dictation_hard():
    """User dictates phone number with many corrections, pauses, restarts."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(f"Здравствуйте, запишите меня на {svc}, {date} {time}, на имя {name}"))
    c.append(A(f"Записала! {name}, {svc}, {date}, {time}. Продиктуйте номер телефона."))

    ph = rphone()
    pattern = rc(["restart","correct_mid","slow","confused"])
    if pattern == "restart":
        c.append(U(f"Так, записывайте... восемь... девять... нет, подождите, начну сначала. {ph}"))
        c.append(A(f"Записала. Повторю: {ph}. Верно?"))
        c.append(U("Да, всё правильно"))
    elif pattern == "correct_mid":
        parts = ph.split()
        c.append(U(f"{parts[0]}... {parts[1]}... нет! Не {parts[1][-2:]}, а {ri(10,99)}... ой, нет, всё правильно было. {ph}"))
        c.append(A(f"Хорошо, записала номер. Подтверждаю: {ph}?"))
        c.append(U("Угу, верно"))
    elif pattern == "slow":
        digits = list(ph.replace(" ",""))
        slow = "... ".join(digits[:5]) + "... " + "".join(digits[5:8]) + "... " + "".join(digits[8:])
        c.append(U(f"Так... {slow}"))
        c.append(A(f"Записала! Всё, {name}, ждём вас {date}!"))
    else:
        c.append(U(f"Э... щас... {ph[:10]}... ой, забыл свой номер... {rc(BG_NOISE)}... а, вот: {ph}"))
        c.append(A(f"Бывает! Записала номер. {name}, ждём вас!"))

    c.append(U(rc(["Спасибо!","Спасибо, до свидания","Ага, пока"])))
    c.append(A("До свидания! Хорошего дня!"))
    return c

# ══════════════════════════════════════════
# Category 2: UNCLEAR/VAGUE REQUESTS (300)
# Model must ask smart clarifying questions
# ══════════════════════════════════════════

def gen_vague_service():
    """User describes what they want very vaguely."""
    v = pick_v(); vd = VERTICALS[v]
    name = rc(NAMES); date,time = rc(DATES),rc(TIMES)

    vague_requests = {
        "barbershop": [
            ("ну это... башку в порядок привести","Вам стрижку или комплекс со стрижкой и бородой?","стрижку просто"),
            ("мне бы... ну... вот тут подровнять сверху и по бокам","Понял, мужская стрижка. Записываю?","да, давайте"),
            ("ну чё-то с бородой сделать, не знаю что","Могу предложить стрижку бороды или моделирование — это более детальная работа с формой. Что ближе?","моделирование давайте"),
            ("мне бы чё-нибудь... ну вы знаете... как у Бреда Питта","Понял! Давайте обсудим с мастером — запишу вас на мужскую стрижку, мастер подберёт форму. Хорошо?","ну давай"),
            ("хз что мне надо, борода как-то фигово выглядит","Могу записать на моделирование бороды — мастер оценит и предложит форму. Подойдёт?","ага, давай"),
        ],
        "salon": [
            ("мне бы чё-нибудь с ногтями","Вам маникюр классический или с покрытием гель-лаком?","с гель-лаком"),
            ("хочу что-нибудь с волосами сделать, не знаю что","Могу предложить стрижку, окрашивание или уходовую процедуру. Что вас больше интересует?","наверно покраситься"),
            ("ну мне бы... это... как его... ресницы","Наращивание ресниц или ламинирование? Наращивание — это объём и длина, ламинирование — натуральный изгиб.","наращивание"),
            ("мне нужно привести себя в порядок к свадьбе","Поздравляю! Для свадьбы обычно делают причёску, маникюр и макияж. Хотите записаться на всё?","да, на всё"),
            ("подруга сказала что у вас делают что-то классное с бровями","У нас есть коррекция и ламинирование бровей. Ламинирование сейчас очень популярно — придаёт красивую форму. Хотите записаться?","ну давайте попробую"),
        ],
        "restaurant": [
            ("нам бы куда-нибудь посидеть","С удовольствием поможем! На сколько гостей и когда планируете?","ну нас четверо, в пятницу"),
            ("хочу отметить... ну это... такое событие","Поздравляю! Какое мероприятие планируете — день рождения, юбилей, может быть годовщина?","день рождения жены"),
            ("а у вас можно типа такое... ну чтобы романтично было","Конечно! Могу предложить столик у окна или в каминном зале — там очень уютная атмосфера. На двоих?","да, на двоих"),
            ("мне нужно банкет организовать но я не знаю как","Всё организуем! Для начала скажите: сколько гостей ожидается и какая дата?","человек двадцать, через две недели"),
            ("мы хотим прийти, но у нас аллергия на всё","Не переживайте, наш шеф-повар работает с любыми ограничениями. Расскажите подробнее — какие аллергены нужно исключить?","орехи и молочку"),
        ],
        "carwash": [
            ("мне бы машину это... ну... помыть что ли","Конечно! Вам экспресс-мойку кузова или комплексную с салоном?","а что лучше?"),
            ("тачка грязная капец, надо чё-то делать","Понял! Если просто грязь — подойдёт комплексная мойка. Если хотите глубокую чистку салона — есть химчистка. Что ближе?","комплексную давай"),
            ("мне бы навести красоту на машину перед продажей","Для предпродажной подготовки рекомендую полную мойку плюс полировку кузова. Хотите записаться?","да, давайте"),
            ("не знаю как это называется, чтоб вода скатывалась","Вы имеете в виду обработку антидождём или керамическое покрытие? Антидождь — это на несколько месяцев, керамика — на год и дольше.","антидождь давайте"),
            ("у меня кожа в салоне грязная, можно почистить?","Да, у нас есть химчистка салона — полная или частичная, только сиденья. Что предпочитаете?","ну всё целиком давайте"),
        ],
    }

    options = vague_requests[v]
    user_q, admin_a, user_reply = rc(options)

    svc = rc(vd["services"])
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(user_q))
    c.append(A(admin_a))
    c.append(U(user_reply))
    c.append(A(f"Отлично! Когда вам удобно?"))
    c.append(U(f"{date} {time}"))
    if vd["masters"]:
        master = rc(vd["masters"])
        c.append(A(f"Записываю на {date}, {time}. Мастера предпочитаете?"))
        c.append(U(rc(["Мне без разницы","Любого","На ваш выбор","Кого посоветуете?"])))
        c.append(A(f"Запишу к {master}. На чьё имя?"))
    else:
        c.append(A(f"Записываю на {date}, {time}. На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Спасибо, {name}! Телефон для связи?"))
    c.append(U(rphone()))
    c.append(A(f"Всё записала! Ждём вас, {name}!"))
    c.append(U("Спасибо!"))
    c.append(A("До свидания!"))
    return c

def gen_user_doesnt_know():
    """User genuinely doesn't know what they want, model guides patiently."""
    v = pick_v(); vd = VERTICALS[v]
    name = rc(NAMES); date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(rc(["Здравствуйте, я вообще не знаю что мне нужно",
                    "Алло, мне тут посоветовали к вам обратиться, но я не знаю что выбрать",
                    "Привет, я первый раз звоню, вообще не разбираюсь"])))
    c.append(A(rc(["Ничего страшного, сейчас разберёмся! Расскажите, что вас беспокоит или чего хотелось бы?",
                   "Добро пожаловать! Не переживайте, помогу сориентироваться. Что бы вы хотели?"])))
    if v == "barbershop":
        c.append(U("Ну типа... давно не стригся, борода отросла, выгляжу как бомж"))
        c.append(A("Понял! Тогда лучший вариант — комплекс: стрижка плюс моделирование бороды. Мастер приведёт всё в порядок."))
    elif v == "salon":
        c.append(U("Ну мне бы... типа в целом хорошо выглядеть... у меня мероприятие через неделю"))
        c.append(A("Для мероприятия рекомендую укладку и маникюр. Если хотите, можно добавить уходовую процедуру для лица. Что скажете?"))
    elif v == "restaurant":
        c.append(U("Хочу девушку удивить, но не знаю чем"))
        c.append(A("Могу предложить столик в каминном зале — там очень романтичная атмосфера. Свечи, приглушённый свет. На двоих?"))
    else:
        c.append(U("Ну машина грязная, а я не знаю что делать, я никогда на мойку не ездил"))
        c.append(A("Ничего сложного! Для начала рекомендую комплексную мойку — помоем и кузов, и салон. Какая у вас машина?"))

    c.append(U(rc(["Ну давайте так и сделаем","Ага, звучит хорошо","Окей, давайте","Ну пойдёт"])))
    c.append(A(f"Отлично! Когда удобно?"))
    c.append(U(f"{date} {time}"))
    c.append(A(f"Записываю! На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Готово, {name}! Ждём вас {date}!"))
    c.append(U("Спасибо!"))
    c.append(A("До свидания, хорошего дня!"))
    return c

# ══════════════════════════════════════════
# Category 3: PAUSES & SILENCE (200)
# ══════════════════════════════════════════

def gen_long_pause():
    """User goes silent mid-conversation, model handles it patiently."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(f"Здравствуйте, хочу записаться на {svc}"))
    c.append(A(f"Здравствуйте! Когда вам удобно?"))
    # Silence / thinking
    pause_type = rc(["thinking","distracted","checking","dropped"])
    if pause_type == "thinking":
        c.append(U("Эммм... секунду... [пауза] ...дайте подумать..."))
        c.append(A("Конечно, не торопитесь!"))
        c.append(U(f"Ну давайте {date} {time}"))
    elif pause_type == "distracted":
        c.append(U(f"Так, {date}... ой, подождите секунду... {rc(BG_NOISE)}... [пауза]... простите, отвлеклась"))
        c.append(A("Ничего страшного! Итак, {date}. На какое время?"))
        c.append(U(time))
    elif pause_type == "checking":
        c.append(U("Подождите, мне нужно посмотреть расписание... [пауза]... так..."))
        c.append(A("Да, конечно, жду."))
        c.append(U(f"Вот, {date} {time} подойдёт"))
    else:
        c.append(U("Ал... [тишина]"))
        c.append(A("Алло? Вы на связи?"))
        c.append(U(f"Да-да, простите, связь пропала. {date} {time}"))
    c.append(A(f"Отлично, {date}, {time}! На чьё имя записать?"))
    c.append(U(name))
    c.append(A(f"Записала, {name}! Ждём вас!"))
    c.append(U("Спасибо!"))
    c.append(A("До свидания!"))
    return c

def gen_user_talks_to_someone_else():
    """User is talking to someone else during the call."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(f"Да, здравствуйте, мне нужно на {svc}... [в сторону: подожди, я по телефону!]... извините"))
    c.append(A("Ничего страшного! Записываю на {svc}. Когда удобно?"))
    c.append(U(f"Так... {date}... [в сторону: да, я скоро!]... {time}, если можно"))
    c.append(A(f"Конечно! {date}, {time}. На чьё имя?"))
    c.append(U(f"[в сторону: щас, минуту!]... на {name}"))
    c.append(A(f"Записала, {name}! Ждём вас {date}!"))
    c.append(U("Спасибо, извините за шум"))
    c.append(A("Ничего! До свидания, хорошего дня!"))
    return c

# ══════════════════════════════════════════
# Category 4: OFF-TOPIC & SMALL TALK (200)
# Model stays friendly but steers back
# ══════════════════════════════════════════

def gen_off_topic():
    """User goes off-topic, model steers back to booking."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)

    off_topics = [
        ("А у вас кофе наливают пока ждёшь?","Да, у нас есть чай и кофе для гостей! Так, записываю вас — когда удобно?"),
        ("А вы давно работаете?","Мы работаем уже несколько лет, клиенты довольны! Давайте продолжим запись — на когда?"),
        ("А вот я слышал у вас ремонт был","Да, мы обновили интерьер, стало ещё уютнее! Так, возвращаемся к записи — время удобное скажете?"),
        ("А скажите, а парковка у вас есть?","Да, бесплатная парковка есть! Удобно. Итак, на какое время записать?"),
        ("Ох, а погода сегодня ужасная","Да, погода не радует! Но у нас тепло и уютно. Давайте запишем вас — когда хотите прийти?"),
        ("А у вас Wi-Fi есть?","Да, бесплатный Wi-Fi есть. Так, продолжаем — на когда записываем?"),
        ("А можно собаку с собой привести?","К сожалению, с животными нельзя. Но давайте запишем вас — когда удобно?"),
    ]

    topic_q, topic_a = rc(off_topics)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(f"Здравствуйте, хочу записаться на {svc}"))
    c.append(A(f"Здравствуйте! Отлично, {svc}. Когда вам удобно?"))
    c.append(U(topic_q))
    c.append(A(topic_a))
    c.append(U(f"{date} {time}"))
    c.append(A(f"Записываю: {svc}, {date}, {time}. На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Готово, {name}! Ждём вас!"))
    c.append(U("Спасибо!"))
    c.append(A("До свидания!"))
    return c

def gen_small_talk_start():
    """User starts with small talk before getting to the point."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)

    openers = [
        ("Ой, здравствуйте! Как у вас дела? Всё хорошо?","Здравствуйте! Всё отлично, спасибо! Чем могу помочь?"),
        ("Привет! Вы меня помните? Я к вам ходила в прошлом месяце","Здравствуйте! Рады снова слышать! Чем могу помочь?"),
        ("Добрый день! Ой, у вас такой приятный голос!","Спасибо большое! Чем могу быть полезна?"),
        ("Здрасте! Мне тут подруга ваш номер дала, говорит у вас классно","Здравствуйте! Спасибо за рекомендацию! Чем могу помочь?"),
        ("Алло! Я тут первый раз звоню, немножко волнуюсь","Здравствуйте! Не переживайте, я вам всё подскажу. Чем могу помочь?"),
    ]

    opener_u, opener_a = rc(openers)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(opener_u))
    c.append(A(opener_a))
    c.append(U(f"Ну вот, хочу записаться на {svc}, можно?"))
    c.append(A(f"Конечно! На когда?"))
    c.append(U(f"{date} {time}"))
    c.append(A(f"Записываю: {svc}, {date}, {time}. На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Записала, {name}! Ждём вас!"))
    c.append(U("Спасибо, вы прелесть!"))
    c.append(A("Спасибо! До свидания, хорошего дня!"))
    return c

# ══════════════════════════════════════════
# Category 5: EMPATHY & EMOTIONAL SUPPORT (200)
# ══════════════════════════════════════════

def gen_emotional_user():
    """User is emotional (upset, excited, anxious), model responds with empathy."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)

    emotions = [
        # (user, empathetic response)
        ("Я сегодня рассталась с парнем и хочу кардинально поменять внешность",
         "Мне очень жаль это слышать. Иногда перемены — это именно то, что нужно! Давайте подберём что-нибудь для вас."),
        ("У меня завтра собеседование, я очень нервничаю, хочу выглядеть идеально",
         "Всё будет отлично! Поможем вам подготовиться. Что бы хотели сделать?"),
        ("Ой, у меня через два часа свидание, а я выгляжу ужасно!",
         "Не переживайте, мы быстро всё исправим! Что вам нужно?"),
        ("Мне так грустно, хочу себя порадовать чем-нибудь",
         "Иногда нужно себя побаловать! У нас как раз есть отличные процедуры для настроения."),
        ("У дочки выпускной, я хочу чтобы она была самая красивая!",
         "Какой замечательный повод! Обязательно поможем, чтобы всё было идеально."),
        ("Ой, я так рада! Мне сделали предложение! Нужно готовиться к свадьбе!",
         "Ой, поздравляю! Это прекрасная новость! Конечно, поможем подготовиться."),
        ("Мне завтра презентация на 500 человек, я просто в панике",
         "Понимаю волнение! Но вы справитесь. А мы поможем, чтобы вы выглядели на все сто."),
        ("Я недавно болел и выгляжу плохо, хочу привести себя в порядок",
         "Рады, что вы поправились! Поможем вернуть свежий вид. Что бы хотели?"),
    ]

    user_emo, admin_resp = rc(emotions)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(user_emo))
    c.append(A(admin_resp))
    c.append(U(f"Давайте {svc}"))
    c.append(A(f"Отличный выбор! Когда удобно?"))
    c.append(U(f"{date} {time}"))
    c.append(A(f"Записала: {svc}, {date}, {time}. На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Готово, {name}! Всё будет замечательно, не переживайте! Ждём вас!"))
    c.append(U(rc(["Спасибо вам большое!","Спасибо, вы очень добры!","Ой спасибо!"])))
    c.append(A("Пожалуйста! До встречи, хорошего дня!"))
    return c

# ══════════════════════════════════════════
# Category 6: MULTI-STEP CLARIFICATION (200)
# Model extracts info step by step patiently
# ══════════════════════════════════════════

def gen_info_extraction():
    """User gives minimal info, model patiently extracts everything needed."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]

    # User gives almost nothing
    c.append(U(rc(["Запишите меня","Хочу записаться","Мне нужно к вам","Можно записаться?"])))
    c.append(A("Конечно! На какую услугу?"))
    c.append(U(rc([f"На {svc}",f"Ну, {svc}",f"Это... {svc}"])))
    c.append(A(f"Хорошо, {svc}. На какой день?"))
    c.append(U(rc([date,f"Ну {date}",f"Наверно {date}"])))
    c.append(A(f"На какое время?"))
    c.append(U(rc([time,f"Ну {time}",f"Где-то {time}"])))
    if vd["masters"]:
        master = rc(vd["masters"])
        c.append(A(f"К кому хотите? Есть {rc(vd['masters'])}, {rc(vd['masters'])}."))
        c.append(U(rc(["Без разницы","Любого","Мне всё равно","Кого угодно"])))
        c.append(A(f"Хорошо, запишу к {master}. Ваше имя?"))
    else:
        c.append(A("Как вас зовут?"))
    c.append(U(name))
    c.append(A(f"И номер телефона, пожалуйста."))
    c.append(U(rphone()))
    c.append(A(f"Всё записала! {name}, {svc}, {date}, {time}. Ждём!"))
    c.append(U("Спасибо"))
    c.append(A("До свидания!"))
    return c

# ══════════════════════════════════════════
# Category 7: MISUNDERSTANDING & REPAIR (200)
# Model misinterprets, user corrects, model recovers gracefully
# ══════════════════════════════════════════

def gen_misunderstanding():
    """Model misunderstands, user corrects, model recovers."""
    v = pick_v(); vd = VERTICALS[v]
    name = rc(NAMES); date,time = rc(DATES),rc(TIMES)
    svcs = vd["services"]
    svc1,svc2 = rc(svcs),rc(svcs)
    while svc2 == svc1 and len(svcs) > 1: svc2 = rc(svcs)

    c = [S(v), A(rc(vd["greets"]))]

    mis_type = rc(["service","time","name","date"])
    if mis_type == "service":
        c.append(U(f"Мне нужно на {svc1}"))
        c.append(A(f"Записываю на {svc2}?"))
        c.append(U(f"Нет-нет, не {svc2}, а {svc1}!"))
        c.append(A(f"Прошу прощения! Конечно, {svc1}. Когда удобно?"))
        c.append(U(f"{date} {time}"))
    elif mis_type == "time":
        c.append(U(f"На {svc1}, {date}, {time}"))
        wrong_time = rc([t for t in TIMES if t != time])
        c.append(A(f"Записываю на {svc1}, {date}, {wrong_time}?"))
        c.append(U(f"Нет, я сказал {time}, не {wrong_time}"))
        c.append(A(f"Извините! {time}, записала."))
    elif mis_type == "name":
        similar_names = {"Александр":"Алексей","Елена":"Алёна","Мария":"Марина","Дмитрий":"Данил",
                        "Наталья":"Наталия","Андрей":"Артём","Сергей":"Евгений"}
        wrong = similar_names.get(name, name+"а")
        c.append(U(f"Хочу на {svc1}, {date}"))
        c.append(A(f"Записываю! На чьё имя?"))
        c.append(U(name))
        c.append(A(f"Записала, {wrong}?"))
        c.append(U(f"Нет, не {wrong}, а {name}. {name[0]} — {name}"))
        c.append(A(f"Простите, {name}! Исправила."))
    else:
        wrong_date = rc([d for d in DATES if d != date])
        c.append(U(f"На {svc1}, {date}"))
        c.append(A(f"На {svc1}, {wrong_date}?"))
        c.append(U(f"Нет! {date}, а не {wrong_date}"))
        c.append(A(f"Извините! {date}, записала. На какое время?"))
        c.append(U(time))

    c.append(A(f"Итак: {svc1}, {date}, {time}, {name}. Всё верно?"))
    c.append(U("Да, теперь всё правильно"))
    c.append(A(f"Отлично! Ждём вас, {name}!"))
    c.append(U("Спасибо"))
    c.append(A("До свидания!"))
    return c

# ══════════════════════════════════════════
# Category 8: COMPLEX MULTI-TURN (200)
# Long conversations with many twists
# ══════════════════════════════════════════

def gen_complex_conversation():
    """Long dialog with multiple topics, changes, and questions."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); svc2 = rc(vd["services"])
    name = rc(NAMES)
    date,date2 = rc(DATES),rc(DATES)
    time,time2 = rc(TIMES),rc(TIMES)

    c = [S(v), A(rc(vd["greets"]))]
    # Start with booking
    c.append(U(f"Здравствуйте! Хочу записаться на {svc}"))
    c.append(A(f"Здравствуйте! Когда удобно?"))
    c.append(U(f"{date} {time}"))
    # Ask about price
    price_str = vd["prices"].get(svc, "уточню")
    c.append(A(f"Записываю: {svc}, {date}, {time}. Стоимость {price_str}."))
    c.append(U(rc(["А сколько по времени займёт?","А долго это?","Это надолго?"])))
    c.append(A(rc(["Примерно час.","Около сорока минут.","Полтора-два часа, зависит от объёма работы."])))
    # Change something
    c.append(U(f"Хм... а знаете, давайте лучше {date2}"))
    c.append(A(f"Без проблем, переношу на {date2}. Время то же?"))
    v2 = random.random()
    if v2 < 0.4:
        c.append(U(f"Нет, давайте лучше {time2}"))
        c.append(A(f"Хорошо, {date2}, {time2}."))
    else:
        c.append(U("Да, время то же"))
    # Add another service maybe
    if random.random() < 0.5:
        c.append(U(f"А можно ещё добавить {svc2}?"))
        c.append(A(f"Конечно! Добавляю {svc2}. На чьё имя?"))
    else:
        c.append(A("На чьё имя записать?"))
    c.append(U(name))
    c.append(A(f"Телефон для связи?"))
    c.append(U(rphone()))
    c.append(A(f"Всё готово, {name}! Ждём вас!"))
    c.append(U("Спасибо большое!"))
    c.append(A("Пожалуйста! До свидания!"))
    return c

# ══════════════════════════════════════════
# Category 9: OPERATOR PROACTIVITY (100)
# Model anticipates needs, suggests, upsells naturally
# ══════════════════════════════════════════

def gen_proactive_operator():
    """Model proactively suggests relevant things a good operator would."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)

    proactive_pairs = {
        "barbershop": [
            (f"На {svc}",
             f"Записываю! Кстати, если давно не делали камуфляж седины — сейчас можно совместить, сэкономите время."),
            (f"Стрижку мне",
             "Отлично! Обратите внимание — сейчас при заказе комплекса стрижка плюс борода скидка десять процентов."),
        ],
        "salon": [
            (f"На {svc}",
             f"Записываю! Кстати, многие клиентки совмещают {svc} с укладкой — получается полный образ."),
            (f"Маникюр",
             "Хорошо! Обратите внимание, сейчас есть акция — маникюр плюс педикюр со скидкой пятнадцать процентов."),
        ],
        "restaurant": [
            ("Столик на двоих",
             "Конечно! Кстати, если это особый повод, могу организовать свечи и цветы на столе — бесплатно при заказе ужина."),
            ("Банкет на десять человек",
             "Отлично! При бронировании банкета на десять и более гостей аренда зала бесплатна. Удобно?"),
        ],
        "carwash": [
            (f"На {svc}",
             f"Записываю! Кстати, после мойки рекомендую обработку антидождём — кузов будет чистый гораздо дольше."),
            ("Комплексную мойку",
             "Хорошо! Обратите внимание — сейчас абонемент на пять моек со скидкой пятнадцать процентов."),
        ],
    }

    user_q, admin_proactive = rc(proactive_pairs[v])
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(user_q))
    c.append(A(admin_proactive))
    c.append(U(rc(["Ну давайте","Нет, спасибо, только основное","О, интересно, давайте!","Не, в другой раз"])))
    c.append(A(f"Хорошо! На когда записать?"))
    c.append(U(f"{date} {time}"))
    c.append(A(f"Записала: {date}, {time}. На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Готово, {name}! Ждём вас!"))
    c.append(U("Спасибо!"))
    c.append(A("До свидания!"))
    return c

# ══════════════════════════════════════════
# Category 10: NATURAL OPERATOR PHRASES (100)
# Short dialogs teaching specific operator micro-skills
# ══════════════════════════════════════════

def gen_confirm_repeat():
    """Model confirms by repeating back info naturally."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    date,time = rc(DATES),rc(TIMES)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(f"Запишите на {svc}, {date}, {time}, имя {name}"))
    c.append(A(f"Повторю, чтобы убедиться: {svc}, {date}, {time}, на имя {name}. Всё верно?"))
    c.append(U("Да, всё так"))
    c.append(A(f"Отлично, записала! Ждём вас, {name}!"))
    c.append(U("Спасибо!"))
    c.append(A("До свидания!"))
    return c

def gen_apologize_recover():
    """Model makes a mistake, apologizes, and recovers gracefully."""
    v = pick_v(); vd = VERTICALS[v]
    svc = rc(vd["services"]); name = rc(NAMES)
    c = [S(v), A(rc(vd["greets"]))]
    c.append(U(f"Хочу записаться на {svc}"))
    c.append(A(f"Конечно! Стоимость... простите, секунду, уточняю... {vd['prices'].get(svc, 'уточню стоимость')} рублей. Когда удобно?"))
    c.append(U(rc(DATES) + " " + rc(TIMES)))
    c.append(A(f"Записала! На чьё имя?"))
    c.append(U(name))
    c.append(A(f"Спасибо, {name}! Ждём вас!"))
    c.append(U("Пока"))
    c.append(A("До свидания!"))
    return c

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

SCENARIOS = [
    (gen_garbled_request, 200),
    (gen_noise_throughout, 100),
    (gen_phone_dictation_hard, 100),
    (gen_vague_service, 200),
    (gen_user_doesnt_know, 100),
    (gen_long_pause, 100),
    (gen_user_talks_to_someone_else, 100),
    (gen_off_topic, 100),
    (gen_small_talk_start, 100),
    (gen_emotional_user, 200),
    (gen_info_extraction, 100),
    (gen_misunderstanding, 200),
    (gen_complex_conversation, 200),
    (gen_proactive_operator, 100),
    (gen_confirm_repeat, 50),
    (gen_apologize_recover, 50),
]

def main():
    total_planned = sum(w for _, w in SCENARIOS)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "universal_skills_dialogs.jsonl")
    dialogs = []
    for gen_fn, count in SCENARIOS:
        for _ in range(count):
            try:
                convs = gen_fn()
                dialogs.append({"conversations": convs})
            except Exception as e:
                print(f"Error in {gen_fn.__name__}: {e}")
    # Pad to 2000 if needed
    while len(dialogs) < 2000:
        gen_fn = rc([fn for fn, _ in SCENARIOS])
        try:
            dialogs.append({"conversations": gen_fn()})
        except:
            pass
    random.shuffle(dialogs)
    with open(out, "w", encoding="utf-8") as f:
        for d in dialogs[:2000]:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"Generated {min(len(dialogs),2000)} dialogs -> {out}")
    ok = 0
    with open(out, encoding="utf-8") as f:
        for line in f:
            json.loads(line)
            ok += 1
    print(f"Validated: {ok}/2000 lines OK")

if __name__ == "__main__":
    main()
