#!/usr/bin/env python3
"""Generate 1500 SFT training dialogs for barbershop AI voice receptionist (v2)."""

import json, random, os

random.seed(4004)

SYS = ("Вы — администратор барбершопа. Помогаете клиентам записаться на стрижку или другую услугу, "
       "выбрать мастера и удобное время. Говорите дружелюбно, по делу, в мужском стиле общения.")

# ── Data pools ──
BARBERS = ["Дмитрий","Артём","Кирилл","Алексей","Роман","Сергей","Максим","Виктор","Данил","Егор"]

SERVICES = {
    "Мужская стрижка": ((1200,2000),"сорок минут"),
    "Стрижка машинкой": ((800,1200),"тридцать минут"),
    "Стрижка бороды": ((800,1500),"тридцать минут"),
    "Моделирование бороды": ((1500,2500),"сорок пять минут"),
    "Комплекс стрижка и борода": ((2000,3000),"час пятнадцать"),
    "Королевское бритьё": ((1500,2500),"сорок пять минут"),
    "Камуфляж седины": ((2000,3000),"час"),
    "Укладка": ((500,1000),"пятнадцать минут"),
    "Детская стрижка": ((800,1200),"тридцать минут"),
    "Окрашивание": ((3000,5000),"полтора часа"),
}

SVC_CASUAL = {
    "Мужская стрижка": ["подстричься","стрижку","стрижечку","башку обновить","голову привести в порядок","подравнять"],
    "Стрижка машинкой": ["машинкой снять","под машинку","коротко машинкой","налысо почти"],
    "Стрижка бороды": ["бороду подровнять","бороду поправить","бородку подстричь"],
    "Моделирование бороды": ["бороду смоделировать","бороду оформить","бороду по красоте"],
    "Комплекс стрижка и борода": ["комплекс","стрижку и бороду","полный комплект","голову и бороду"],
    "Королевское бритьё": ["побриться","королевское бритьё","опасной бритвой"],
    "Камуфляж седины": ["камуфляж","седину закрасить","седину убрать"],
    "Укладка": ["уложить","укладку","зачесать"],
    "Детская стрижка": ["сына подстричь","ребёнка подстричь","пацану стрижку"],
    "Окрашивание": ["покраситься","окрашивание","цвет поменять"],
}

COMBOS = [
    ("Мужская стрижка","Стрижка бороды"),
    ("Мужская стрижка","Моделирование бороды"),
    ("Мужская стрижка","Камуфляж седины"),
    ("Мужская стрижка","Укладка"),
    ("Стрижка бороды","Камуфляж седины"),
    ("Комплекс стрижка и борода","Камуфляж седины"),
]

NAMES = ["Александр","Дмитрий","Сергей","Андрей","Михаил","Иван","Максим","Павел","Артём",
         "Николай","Олег","Роман","Евгений","Алексей","Виктор","Денис","Игорь","Тимур",
         "Руслан","Кирилл","Антон","Фёдор","Борис","Вадим","Григорий","Константин","Владислав"]

CHILD_NAMES = ["Ваня","Петя","Миша","Саша","Дима","Матвей","Тимур","Артём","Лёша","Кирилл","Даня","Егор"]

FILLERS = ["ну","эм","так","вот","короче","слушай","значит","это","в общем","ну типа",
           "ну это","блин","ну короче","слушайте","как бы","ну слушай"]

DATES = ["завтра","послезавтра","в субботу","в воскресенье","в пятницу","в понедельник",
         "во вторник","в среду","в четверг","в эту субботу","на следующей неделе",
         "через два дня","в эти выходные","в ближайшую субботу","седня","сегодня вечером"]

TIMES = ["к десяти","в одиннадцать","в двенадцать","к часу","в два","в три","к четырём",
         "в пять","к шести","в семь","часов в шесть","к обеду","после обеда","утром",
         "ближе к вечеру","часиков в пять","в полшестого","часам к трём","к двум"]

TIMES_F = ["десять часов","одиннадцать часов","двенадцать часов","тринадцать часов",
           "четырнадцать часов","пятнадцать часов","шестнадцать часов","семнадцать часов",
           "восемнадцать часов","девятнадцать часов","двадцать часов"]

GREETINGS_A = [
    "Барбершоп «Бородач», здарова! Чем могу помочь?",
    "Барбершоп «Бородач», добрый день! Слушаю.",
    "Добрый день! Барбершоп «Бородач». Чем помочь?",
    "Здравствуйте! Барбершоп «Бородач», на связи.",
    "Барбершоп «Бородач», привет! Что подсказать?",
    "Алло! «Бородач», слушаю вас.",
]

GREETINGS_C = ["Здорово","Привет","Здрасте","Добрый день","Алло","Йо","Привет, слушай",
               "Здрасьте","Алё","Доброго"]

CANCEL_REASONS = ["планы поменялись","не получится прийти","заболел","командировка",
                  "работа навалилась","забыл что занят"]

NOISE = ["[неразборчиво]","[шум]","[помехи]","[плохая связь]","[шум улицы]"]
PHONE_PFX = ["восемь девять","плюс семь девять","восемь девятьсот"]

POS = ["збс!","отлично!","класс!","круто!","супер!","го!","огонь!","ну збс"]
NEG = ["блин...","ну блин","ёлки...","фигово","обидно","ну капец","чёрт"]
RUSH = ["слушай мне некогда давай быстро","короче быстро","мне срочно","времени нет давай по-быстрому"]

YES = ["ага","угу","да","ну да","точно","ладно","окей","збс","го","давай","пойдёт"]
BYE_U = ["спасибо, бро","спасибо, давай","ну всё, спасибо","збс, спасибо","ладно, давай, пока",
         "окей, спасибо, до связи","благодарю","спасибо большое","ну давай, пока"]
BYE_A = ["Ждём! До встречи!","Отлично, до встречи!","Ждём тебя! Хорошего дня!",
         "Записали! До встречи, бро!","Круто, ждём! Пока!","Всё готово! До связи!"]

rc = random.choice
ri = random.randint

# ── Helpers ──

def nat(text, fp=0.6):
    if random.random() < fp:
        f = rc(FILLERS)
        text = (f.capitalize() if random.random()<0.25 else f) + ", " + text[0].lower() + text[1:]
    if random.random() < 0.25:
        w = text.split()
        if len(w) > 3:
            w.insert(ri(1,min(len(w)-2,4)), rc(["э...","эм...","ну...","типа...","это...","м..."]))
            text = " ".join(w)
    if random.random() < 0.06:
        w = text.split()
        if len(w) > 2:
            w[ri(0,len(w)-1)] = rc(NOISE)
            text = " ".join(w)
    if random.random() < 0.25:
        text = text.replace(".","").replace(",","").strip()
    if random.random() < 0.12:
        text += " " + rc(["вот","короче","да","ну вот","как-то так","в общем"])
    return text

def spell_price(p):
    t=p//1000; h=(p%1000)//100; parts=[]
    tw={1:"тысяча",2:"две тысячи",3:"три тысячи",4:"четыре тысячи",5:"пять тысяч"}
    if t: parts.append(tw.get(t,f"{t} тысяч"))
    hw={1:"сто",2:"двести",3:"триста",4:"четыреста",5:"пятьсот",6:"шестьсот",7:"семьсот",8:"восемьсот",9:"девятьсот"}
    if h: parts.append(hw[h])
    return " ".join(parts)+" рублей" if parts else f"{p} рублей"

def get_price(svc):
    lo,hi = SERVICES[svc][0]
    return random.randrange(lo,hi+1,100)

def get_dur(svc): return SERVICES[svc][1]

def rphone():
    d = [str(ri(0,9)) for _ in range(7)]
    return rc(PHONE_PFX)+" "+"".join(d[:3])+" "+"".join(d[3:5])+" "+"".join(d[5:])

def casual(svc):
    return rc(SVC_CASUAL.get(svc, [svc.lower()]))

def S(): return {"role":"system","content":SYS}
def A(t): return {"role":"assistant","content":t}
def U(t): return {"role":"user","content":t}

def phone_ex(name, c):
    c.append(A(rc([f"Записал, {name}! Номер телефона оставишь?",
                   f"{name}, продиктуй номер для связи.",
                   f"Отлично, {name}! Телефон скажешь?",
                   f"Супер! {name}, номерок телефона?"])))
    ph = rphone()
    v = random.random()
    if v < 0.3: c.append(U(nat(ph)))
    elif v < 0.55: c.append(U(nat(f"Да, записывай: {ph}")))
    elif v < 0.75: c.append(U(nat(f"{ph[:15]}... нет, подождите... {ph}")))
    else: c.append(U(nat(f"Номер {ph}")))

def summary(name, svc, barber, date, time_f, price, c):
    c.append(A(rc([
        f"Записал: {name}, {svc.lower()}, мастер {barber}, {date}, {time_f}. Стоимость {spell_price(price)}. Всё верно?",
        f"Итого: {svc.lower()} у {barber}, {date} в {time_f}. Цена {spell_price(price)}. Подтверждаешь?",
        f"Подтверждаю: {name}, {date}, {time_f}, {svc.lower()}, мастер {barber}, {spell_price(price)}. Окей?"])))
    c.append(U(nat(rc(["Да, всё верно","Ага, подтверждаю","Угу, всё так","Окей, давай","Збс, подтверждаю"]))))
    c.append(A(rc([f"Отлично! Ждём тебя, {name}!",f"Записали! До встречи!",
                   f"Круто! {name}, ждём! Хорошего дня!",f"Всё, записал! До встречи, бро!"])))

# ══════════ Scenario generators ══════════

def gen_simple():
    svc = rc(list(SERVICES.keys()))
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u,time_f = rc(DATES),rc(TIMES),rc(TIMES_F)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([
        f"{rc(GREETINGS_C)}, хочу {casual(svc)}",
        f"{rc(GREETINGS_C)}! Можно записаться {casual(svc)}?",
        f"{rc(GREETINGS_C)}, мне бы {casual(svc)}, {date}",
        f"Запишите меня {casual(svc)}, пожалуйста",
        f"{rc(GREETINGS_C)}, нужно {casual(svc)} {date} {time_u}"]))))
    c.append(A(rc([
        f"Привет! {svc} — отличный выбор. К кому хочешь? Есть {rc(BARBERS)}, {rc(BARBERS)}, {barber}.",
        f"Здарова! На {svc.lower()} записываю. Мастера предпочитаешь какого?",
        f"Привет! {svc}, понял. Когда удобно и к кому?"])))
    c.append(U(nat(rc([f"Давай к {barber}",f"К {barber}, если можно",f"Мне без разницы, любого",
                       f"К {barber} хочу",f"Ну к {barber} наверное"]))))
    if "когда" not in c[-2]["content"].lower():
        c.append(A(f"К {barber}, записал. Когда удобно?"))
        c.append(U(nat(rc([f"{date} {time_u}",f"Давай {date}",f"{date}, {time_u}"]))))
    c.append(A(f"{svc}, мастер {barber}, {date}, {time_f}. Стоимость {spell_price(price)}, длительность {get_dur(svc)}. На чьё имя?"))
    c.append(U(nat(rc([name, f"На {name}", f"Запиши на {name}"]))))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_specific_master():
    svc = rc(list(SERVICES.keys()))
    wanted = rc(BARBERS); alt = rc([b for b in BARBERS if b != wanted])
    name = rc(NAMES); date,time_u,time_f = rc(DATES),rc(TIMES),rc(TIMES_F)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(f"{rc(GREETINGS_C)}, хочу к {wanted} на {casual(svc)}")))
    busy = random.random() < 0.5
    if busy:
        c.append(A(f"Привет! К сожалению, {wanted} {date} полностью занят. Могу предложить {alt} — отличный мастер. Или другой день к {wanted}?"))
        if random.random() < 0.6:
            c.append(U(nat(rc([f"Ладно, давай к {alt}",f"Окей, пусть {alt}",f"Ну давайте к {alt} тогда"]))))
            barber = alt
        else:
            c.append(U(nat(rc(["А когда {wanted} свободен?",f"Лучше подожду {wanted}","Нет, хочу именно к {wanted}"]))))
            c.append(A(f"{wanted} свободен послезавтра. Могу записать?"))
            c.append(U(nat("Да, давай послезавтра")))
            barber = wanted; date = "послезавтра"
    else:
        c.append(A(f"Привет! {wanted} свободен. Когда удобно?"))
        c.append(U(nat(f"{date} {time_u}")))
        barber = wanted
    c.append(A(f"Отлично! {svc}, {barber}, {date}, {time_f}. {spell_price(price).capitalize()}. Имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_combo():
    s1,s2 = rc(COMBOS)
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u,time_f = rc(DATES),rc(TIMES),rc(TIMES_F)
    p1,p2 = get_price(s1),get_price(s2)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([
        f"{rc(GREETINGS_C)}, мне бы {casual(s1)} и {casual(s2)}",
        f"{rc(GREETINGS_C)}, хочу {casual(s1)} плюс {casual(s2)}",
        f"Можно записаться на {casual(s1)} и ещё {casual(s2)}?"]))))
    c.append(A(f"Привет! {s1} и {s2} — отличная комбинация. К кому хочешь?"))
    c.append(U(nat(rc([f"К {barber}",f"Давай к {barber}",f"Без разницы, любого"]))))
    c.append(A(f"Когда удобно? Учти, на оба — примерно {get_dur(s1)} плюс {get_dur(s2)}."))
    c.append(U(nat(f"{date} {time_u}")))
    total = p1+p2
    c.append(A(f"Записал: {s1.lower()} и {s2.lower()}, мастер {barber}, {date}, {time_f}. Всего {spell_price(total)}. Имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_self_correct():
    svc = rc(list(SERVICES.keys())); svc2 = rc([s for s in SERVICES if s != svc])
    barber = rc(BARBERS); name = rc(NAMES)
    date,date2 = rc(DATES),rc(DATES)
    time_u,time_u2,time_f = rc(TIMES),rc(TIMES),rc(TIMES_F)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(f"{rc(GREETINGS_C)}, хочу {casual(svc)} {date} {time_u}")))
    c.append(A(f"Записываю: {svc.lower()}, {date}, {time_u}. К кому?"))
    c.append(U(nat(f"К {barber}")))
    # Self-correction
    corr_type = rc(["date","time","service","barber"])
    if corr_type == "date":
        c.append(U(nat(rc([f"Ой, стоп, не {date}, а {date2}",f"Нет, подождите, я перепутал — {date2}",
                           f"А нет, вру — давайте {date2}"]))))
        c.append(A(f"Понял, значит {date2}. Записал!"))
        date = date2
    elif corr_type == "time":
        c.append(U(nat(rc([f"Стоп, не {time_u}, а {time_u2}",f"Ой нет, лучше {time_u2}",
                           f"Хотя нет, давай {time_u2}"]))))
        c.append(A(f"Окей, меняю на {time_u2}. Без проблем!"))
    elif corr_type == "service":
        price = get_price(svc2)
        c.append(U(nat(rc([f"Стоп, мне не {casual(svc)}, а {casual(svc2)}",
                           f"Ой, я не то сказал — мне {casual(svc2)}",
                           f"Нет подождите, давайте лучше {casual(svc2)}"]))))
        c.append(A(f"Понял, меняю на {svc2.lower()}. Стоимость {spell_price(price)}."))
        svc = svc2
    else:
        b2 = rc([b for b in BARBERS if b != barber])
        c.append(U(nat(rc([f"Нет стоп, не к {barber}, к {b2}",f"Ой, давай лучше к {b2}"]))))
        c.append(A(f"Окей, переписал на {b2}!"))
        barber = b2
    c.append(A(f"Итого: {svc.lower()}, {barber}, {date}. {spell_price(price)}. На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_price_book():
    svc = rc(list(SERVICES.keys()))
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u,time_f = rc(DATES),rc(TIMES),rc(TIMES_F)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, скажите сколько стоит {casual(svc)}?",
                       f"Алё, а скока у вас {casual(svc)}?",
                       f"{rc(GREETINGS_C)}, хотел узнать цену на {casual(svc)}"]))))
    c.append(A(f"{svc} у нас стоит {spell_price(price)}, занимает {get_dur(svc)}. Хочешь записаться?"))
    c.append(U(nat(rc(["Да, давай запишите","Ага, записывай","Ну давайте, пойдёт","Окей, го"]))))
    c.append(A("Отлично! Когда удобно и к кому?"))
    c.append(U(nat(f"{date} {time_u}, к {barber}")))
    c.append(A(f"Записал: {svc.lower()}, {barber}, {date}, {time_f}. Имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_cancel():
    name = rc(NAMES); svc = rc(list(SERVICES.keys()))
    reason = rc(CANCEL_REASONS)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, хочу отменить запись",
                       f"Алё, мне нужно отменить бронь",
                       f"{rc(GREETINGS_C)}, не смогу прийти, хочу отменить"]))))
    c.append(A("Конечно. На чьё имя была запись?"))
    c.append(U(nat(name)))
    c.append(A(f"Нашёл запись, {name}. {svc.lower()}. Могу отменить или перенести. Что предпочитаешь?"))
    if random.random() < 0.5:
        c.append(U(nat(rc([f"Отменяйте, {reason}",f"Просто отмените, {reason}"]))))
        c.append(A(f"Понял, запись отменена. Будем рады видеть в другой раз!"))
    else:
        c.append(U(nat("Лучше перенести, можно?")))
        date,time_u = rc(DATES),rc(TIMES)
        c.append(A("Конечно! Когда удобно?"))
        c.append(U(nat(f"{date} {time_u}")))
        c.append(A(f"Готово, перенёс на {date}. Ждём!"))
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_reschedule():
    name = rc(NAMES); svc = rc(list(SERVICES.keys()))
    date,time_u = rc(DATES),rc(TIMES)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, хочу перенести запись",
                       f"Слушай, мне нужно перенести время",
                       f"Алё, можно перезаписаться на другое время?"]))))
    c.append(A("Без проблем! На чьё имя запись?"))
    c.append(U(nat(name)))
    c.append(A(f"Нашёл: {name}, {svc.lower()}. На когда переносим?"))
    c.append(U(nat(f"{date} {time_u}")))
    if random.random() < 0.3:
        c.append(A(f"К сожалению, {time_u} уже занято. Могу предложить {rc(TIMES)} или {rc(TIMES)}."))
        c.append(U(nat(rc(["Давай первый вариант","Второй подойдёт","Ну ладно, первый"]))))
    c.append(A(f"Перенёс запись на {date}. Всё остальное без изменений. Ждём!"))
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_time_unavail():
    svc = rc(list(SERVICES.keys()))
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u = rc(DATES),rc(TIMES)
    alt1,alt2 = rc(TIMES),rc(TIMES)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(f"{rc(GREETINGS_C)}, запишите на {casual(svc)} к {barber}, {date} {time_u}")))
    c.append(A(f"Привет! К сожалению, {barber} {date} {time_u} занят. Могу предложить {alt1} или {alt2}. Подойдёт?"))
    c.append(U(nat(rc([f"Давай {alt1}",f"{alt2} лучше",f"Ну ладно, {alt1}"]))))
    c.append(A(f"Отлично! {svc}, {barber}, {date}. {spell_price(price)}. Имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_master_recommend():
    svc = rc(list(SERVICES.keys()))
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u,time_f = rc(DATES),rc(TIMES),rc(TIMES_F)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, хочу {casual(svc)}, но не знаю к кому",
                       f"Мне бы {casual(svc)}, кого посоветуете?",
                       f"Хочу {casual(svc)}, мне любого мастера"]))))
    c.append(A(rc([f"Рекомендую {barber} — у него большой опыт и отличные отзывы. Когда удобно?",
                   f"Могу записать к {barber}, он один из лучших. Когда хочешь?",
                   f"Советую {barber}, клиенты всегда довольны. На когда?"])))
    c.append(U(nat(f"{date} {time_u}")))
    c.append(A(f"Записал: {svc.lower()}, {barber}, {date}, {time_f}. {spell_price(price)}. Имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_first_time():
    name = rc(NAMES); barber = rc(BARBERS)
    date,time_u = rc(DATES),rc(TIMES)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, я первый раз у вас, не знаю чё выбрать",
                       f"Привет, я ни разу не был, что посоветуете?",
                       f"Здрасте, хочу прийти но не знаю что мне нужно"]))))
    c.append(A(rc(["Привет! Добро пожаловать! Расскажи, что хочешь: просто подстричься, бороду оформить, или полный комплекс?",
                   "Здарова! Рады новым клиентам. Что хочешь — стрижку, бороду, или и то и другое?"])))
    svc = rc(["Мужская стрижка","Комплекс стрижка и борода","Стрижка бороды"])
    c.append(U(nat(rc([f"Ну давайте {casual(svc)}",f"Наверно {casual(svc)}",
                       f"Хз, наверно {casual(svc)}"]))))
    price = get_price(svc)
    c.append(A(f"Отличный выбор! {svc} — {spell_price(price)}, {get_dur(svc)}. Записать к {barber}?"))
    c.append(U(nat(rc(YES))))
    c.append(A(f"Когда удобно?"))
    c.append(U(nat(f"{date} {time_u}")))
    c.append(A(f"Записал! {svc}, {barber}, {date}. На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_changes_mind():
    svc = rc(list(SERVICES.keys())); barber = rc(BARBERS)
    date,time_u = rc(DATES),rc(TIMES)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(f"{rc(GREETINGS_C)}, хочу записаться на {casual(svc)}")))
    c.append(A(f"Привет! {svc}, когда удобно?"))
    c.append(U(nat(f"{date} {time_u}")))
    c.append(A(f"К {barber} запишу?"))
    c.append(U(nat(rc([f"Ой, знаете, я передумал","Нет, простите, не получится","Блин, давайте в другой раз",
                       f"Стоп, я не смогу, извините"]))))
    c.append(A(rc(["Без проблем! Звони, когда решишься.",
                   "Окей, ничего страшного! Будем рады, когда будешь готов.",
                   "Понял! Если что — мы на связи."])))
    c.append(U(nat(rc(["Спасибо, давай","Ладно, пока","Окей, спасибо"]))))
    c.append(A(rc(BYE_A)))
    return c

def gen_walkin():
    svc = rc(["Мужская стрижка","Стрижка машинкой","Стрижка бороды","Укладка"])
    barber = rc(BARBERS); name = rc(NAMES)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, можно щас подъехать {casual(svc)}?",
                       f"Алё, а есть окно прям сейчас?",
                       f"Можно без записи подойти?"]))))
    free = random.random() < 0.6
    if free:
        c.append(A(f"Привет! Да, {barber} свободен через пятнадцать минут. {svc} — {spell_price(price)}. Подъезжай!"))
        c.append(U(nat(rc([f"{rc(POS)} еду!","Окей, буду через десять","Збс, выезжаю"]))))
        c.append(A(f"Ждём! Имя скажи, запишу."))
        c.append(U(nat(name)))
        c.append(A(f"Записал, {name}! До встречи!"))
    else:
        c.append(A(f"Привет! К сожалению, сейчас все мастера заняты. Ближайшее окно — через два часа. Записать?"))
        if random.random() < 0.5:
            c.append(U(nat("Ладно, записывай")))
            c.append(A(f"Записал! Через два часа, {svc.lower()}, {barber}. Имя?"))
            c.append(U(nat(name)))
            phone_ex(name, c)
        else:
            c.append(U(nat("Нет, долго, в другой раз")))
            c.append(A("Понял! Звони, когда будет удобно."))
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_father_son():
    name = rc(NAMES); child = rc(CHILD_NAMES); barber = rc(BARBERS)
    date,time_u = rc(DATES),rc(TIMES)
    p1,p2 = get_price("Мужская стрижка"),get_price("Детская стрижка")
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, хочу записать себя и сына на стрижку",
                       f"Привет, нужно подстричься мне и ребёнку",
                       f"Здрасте, можно записать двоих — меня и пацана?"]))))
    c.append(A("Привет! Конечно, мужская стрижка и детская. Когда удобно?"))
    c.append(U(nat(f"{date} {time_u}")))
    c.append(A(f"Отлично! Можем записать подряд к одному мастеру. {barber} подойдёт?"))
    c.append(U(nat(rc(YES))))
    total = p1+p2
    c.append(A(f"Записал: мужская стрижка {spell_price(p1)} и детская {spell_price(p2)}, итого {spell_price(total)}. Мастер {barber}, {date}. Имя?"))
    c.append(U(nat(f"{name}, ребёнка зовут {child}")))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_rushed():
    svc = rc(["Мужская стрижка","Стрижка машинкой","Стрижка бороды"])
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u = rc(DATES),rc(TIMES)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc(RUSH) + f", мне нужно {casual(svc)}")))
    c.append(A(f"Понял! {svc}, к {barber}, когда?"))
    c.append(U(nat(f"{date} {time_u}")))
    c.append(A(f"Записал: {barber}, {date}. {spell_price(price)}. Имя?"))
    c.append(U(nat(name)))
    c.append(A(f"Готово, {name}! Ждём! Хорошего дня!"))
    c.append(U(nat("Спасибо, давай")))
    return c

def gen_price_only():
    svc = rc(list(SERVICES.keys()))
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc([f"{rc(GREETINGS_C)}, скока стоит {casual(svc)}?",
                       f"Цена на {casual(svc)}?",
                       f"Хотел узнать прайс на {casual(svc)}"]))))
    c.append(A(f"{svc} — {spell_price(price)}, занимает {get_dur(svc)}. Хочешь записаться?"))
    c.append(U(nat(rc(["Нет, спасибо, я подумаю","Не, пока просто узнавал","Я ещё подумаю, спасибо"]))))
    c.append(A(rc(["Хорошо! Звони, когда решишься.","Без проблем! Мы на связи.","Ок, ждём звонка!"])))
    c.append(U(nat(rc(["Давай, пока","Спасибо, до свидания"]))))
    return c

def gen_aggressive():
    svc = rc(list(SERVICES.keys()))
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u = rc(DATES),rc(TIMES)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc(["Чё так долго трубку берёте?","Алё, вы там спите что ли?",
                       "Сколько можно ждать?","Наконец-то, я уже пять раз звонил"]))))
    c.append(A("Прошу прощения за ожидание! Слушаю вас, чем могу помочь?"))
    c.append(U(nat(f"Мне {casual(svc)} надо, {date}")))
    c.append(A(f"Конечно! {svc}, {date}. К {barber} могу записать. Устроит?"))
    c.append(U(nat(rc(["Ну давайте","Ладно, пойдёт","Угу"]))))
    c.append(A(f"Записал: {date}, {svc.lower()}, {barber}. {spell_price(price)}. Имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_noise_dialog():
    svc = rc(list(SERVICES.keys()))
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u = rc(DATES),rc(TIMES)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(f"{rc(GREETINGS_C)}, [шум] хочу {rc(NOISE)} {casual(svc)}"))
    c.append(A("Простите, плохо слышно. Вы хотите записаться? На какую услугу?"))
    c.append(U(nat(f"Да, {casual(svc)}, {date}")))
    c.append(A(f"Понял! {svc}, {date}. К {barber} запишу. Время?"))
    c.append(U(nat(time_u)))
    c.append(A(f"Записал: {svc.lower()}, {barber}, {date}. {spell_price(price)}. Имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

def gen_transfer():
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(rc(["Можно с управляющим поговорить?","Мне нужен администратор",
                       "Соедините с менеджером","У меня вопрос, нужен главный"]))))
    c.append(A(rc(["Конечно, сейчас переключу. Одну секунду.",
                   "Да, переключаю на управляющего. Оставайтесь на линии.",
                   "Секунду, соединяю с менеджером."])))
    c.append(U(nat("Спасибо")))
    return c

def gen_callback():
    svc = rc(list(SERVICES.keys()))
    barber = rc(BARBERS); name = rc(NAMES)
    date,time_u = rc(DATES),rc(TIMES)
    price = get_price(svc)
    c = [S(), A(rc(GREETINGS_A))]
    c.append(U(nat(f"{rc(GREETINGS_C)}, я только что звонил, связь оборвалась. Мы записывались на {casual(svc)}")))
    c.append(A("Привет! Да, вижу незавершённую запись. Давай продолжим! На когда записываем?"))
    c.append(U(nat(f"{date} {time_u}")))
    c.append(A(f"Записал: {svc.lower()}, {barber}, {date}. {spell_price(price)}. На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(U(rc(BYE_U))); c.append(A(rc(BYE_A)))
    return c

# ══════════ Main ══════════

SCENARIOS = [
    (gen_simple, 300),
    (gen_specific_master, 150),
    (gen_combo, 120),
    (gen_self_correct, 120),
    (gen_price_book, 80),
    (gen_cancel, 80),
    (gen_reschedule, 80),
    (gen_time_unavail, 70),
    (gen_master_recommend, 60),
    (gen_first_time, 50),
    (gen_changes_mind, 40),
    (gen_walkin, 40),
    (gen_father_son, 30),
    (gen_rushed, 30),
    (gen_price_only, 30),
    (gen_aggressive, 20),
    (gen_noise_dialog, 20),
    (gen_transfer, 10),
    (gen_callback, 10),
]

# Verify total
assert sum(w for _, w in SCENARIOS) == 1340, f"Total is {sum(w for _, w in SCENARIOS)}"

def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "barbershop_dialogs_v2.jsonl")
    dialogs = []
    for gen_fn, count in SCENARIOS:
        for _ in range(count):
            convs = gen_fn()
            dialogs.append({"conversations": convs})
    # Pad to 1500 with random scenarios
    while len(dialogs) < 1500:
        gen_fn = rc([fn for fn, _ in SCENARIOS[:5]])
        dialogs.append({"conversations": gen_fn()})
    random.shuffle(dialogs)
    with open(out, "w", encoding="utf-8") as f:
        for d in dialogs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"Generated {len(dialogs)} dialogs -> {out}")
    # Validate
    ok = 0
    with open(out, encoding="utf-8") as f:
        for line in f:
            json.loads(line)
            ok += 1
    print(f"Validated: {ok}/{len(dialogs)} lines OK")

if __name__ == "__main__":
    main()
