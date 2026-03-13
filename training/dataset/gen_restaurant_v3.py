#!/usr/bin/env python3
"""Generate 1500 SFT training dialogs for restaurant AI voice receptionist (v3)."""

import json, random, os

random.seed(42)

SYS = ("Вы — администратор ресторана. Помогаете гостям забронировать столик, "
       "выбрать зал и обсудить детали визита. Говорите вежливо, гостеприимно и профессионально.")

# ── Data pools ──
NAMES = (["Александр","Дмитрий","Сергей","Андрей","Михаил","Иван","Максим","Павел","Артём",
          "Николай","Владимир","Олег","Роман","Евгений","Алексей","Виктор","Денис","Игорь",
          "Тимур","Руслан","Кирилл","Антон","Фёдор","Борис","Станислав","Вадим","Григорий"] +
         ["Елена","Анна","Мария","Ольга","Наталья","Татьяна","Екатерина","Ирина","Светлана",
          "Юлия","Дарья","Алина","Виктория","Ксения","Полина","Марина","Людмила","Надежда",
          "Оксана","Диана","Кристина","Софья","Милана","Вера","Лариса","Галина"])

FILLERS = ["ну","эм","так","вот","ааа","короче","слушайте","значит","это самое","как бы",
           "ну вот","в общем","ну типа","ну это","так сказать","а"]

DATES = ["завтра","послезавтра","в эту субботу","в это воскресенье","в пятницу",
         "на следующей неделе","через неделю","в эти выходные","в ближайшую субботу",
         "третьего числа","пятого марта","десятого","пятнадцатого","двадцатого",
         "двадцать третьего","в следующую пятницу","через два дня","седьмого апреля",
         "в среду","в понедельник","во вторник","в четверг","в ближайшее воскресенье"]

TIMES = ["в шесть","часов в шесть","к семи","в семь","в семь тридцать","в восемь","к восьми",
         "около семи","часам к шести","ну часов в семь","в полседьмого","к шести вечера",
         "в восемь вечера","на семь","в шесть тридцать","примерно в восемь","к двенадцати",
         "в час дня","в два","на час","около двух","часа в три","в пять вечера"]

TIMES_F = ["восемнадцать часов","восемнадцать тридцать","девятнадцать часов",
           "девятнадцать тридцать","двадцать часов","тринадцать часов","семнадцать часов"]

GUEST_S = {2:["на двоих","нас двое","вдвоём"],3:["на троих","нас трое","три человека"],
           4:["на четверых","нас четверо","четыре человека"],5:["на пятерых","нас пятеро"],
           6:["на шестерых","шесть человек"],7:["семь человек"],8:["восемь человек"],
           10:["на десять человек","десять человек"],12:["двенадцать человек"],
           15:["пятнадцать человек"],20:["двадцать человек"],25:["двадцать пять человек"],
           30:["тридцать человек"],40:["сорок человек"],50:["пятьдесят гостей"]}

GUEST_F = {2:"двух",3:"трёх",4:"четырёх",5:"пять",6:"шесть",7:"семь",8:"восемь",
           10:"десять",12:"двенадцать",15:"пятнадцать",20:"двадцать",25:"двадцать пять",
           30:"тридцать",40:"сорок",50:"пятьдесят"}

HALLS = ["основной зал","VIP-зал","банкетный зал","каминный зал","летняя веранда",
         "зал у окна","малый зал","уютный зал"]

OCCASIONS = ["день рождения","юбилей","годовщина свадьбы","помолвка","корпоратив",
             "выпускной","свадьба","новоселье","повышение на работе","встреча одноклассников"]

ALLERGIES = ["орехи","глютен","лактоза","морепродукты","мёд","цитрусовые","яйца","рыба"]
DIETS = ["вегетарианское меню","веганское меню","безглютеновое меню","халяль","детское меню",
         "постное меню","диетическое меню"]
SPECIAL = ["торт","живая музыка","украшение зала шарами","фотозона","проектор","микрофон",
           "цветы на стол","свечи","детский аниматор"]

RESTS = ["Белый сад","Олива","Террасса","Бриз","Сказка","Панорама","Верона","Каштан",
         "Прага","Романтика","Итальянский дворик","Империя","Центральный","Усадьба",
         "Тёплый дом","Гранд","Европа","Палаццо","Базилик","Парус","Маяк","Причал",
         "Лагуна","Набережная","Встреча","Праздник","Феерия","Джаз","Карамель","Столица",
         "Романс","Огонёк","Патио","Сирень","Фонтан","Ривьера","Акварель"]

CANCEL_REASONS = ["планы изменились","заболел","не получится прийти","срочная командировка",
                  "семейные обстоятельства","перенесли мероприятие"]

NOISE = ["[неразборчиво]","[шум]","[помехи]","[плохая связь]"]
PHONE_PFX = ["восемь девять","плюс семь девять","восемь девятьсот"]

EMOTIONS_POS = ["ой, отлично!","класс!","супер!","замечательно!","вау!","здорово!","круто!"]
EMOTIONS_NEG = ["да блин...","жалко...","фиг знает","ну блин","эх...","обидно","ну ёлки..."]
EMOTIONS_WORRY = ["а точно всё будет?","а вдруг не успеете?","ой, я переживаю","а это надёжно?",
                  "вы уверены?","а если что-то пойдёт не так?"]

INFORMAL_GREETS = ["здрасте","здрасьте","дратути","алё","алло","добрый день","привет",
                   "доброго времени","хай"]
INFORMAL_YES = ["ага","угу","да","ну да","конечно","разумеется","естественно","точно"]
INFORMAL_BYE = ["спасибо большое!","спасибо, до свидания","отлично, спасибо","благодарю!",
                "угу, спасибо","ладно, спасибо, пока","хорошо, спасибо вам","ну спасибо, пока"]

# ── Helpers ──
rc = random.choice
ri = random.randint

def nat(text, filler_prob=0.6):
    """Naturalize user speech: fillers, hesitations, STT noise, emotions, informal."""
    # Filler at start
    if random.random() < filler_prob:
        f = rc(FILLERS)
        text = (f.capitalize() if random.random()<0.3 else f) + ", " + text[0].lower() + text[1:]
    # Hesitation mid-sentence
    if random.random() < 0.25:
        w = text.split()
        if len(w) > 3:
            pos = ri(1, min(len(w)-2, 4))
            w.insert(pos, rc(["э...","эм...","ну...","как его...","это...","м..."]))
            text = " ".join(w)
    # STT noise
    if random.random() < 0.06:
        w = text.split()
        if len(w) > 2:
            w[ri(0, len(w)-1)] = rc(NOISE)
            text = " ".join(w)
    # Drop punctuation sometimes
    if random.random() < 0.25:
        text = text.replace(".", "").replace(",", " ").replace("  ", " ").strip()
    # Trailing filler
    if random.random() < 0.12:
        text += " " + rc(["вот","ну вот так","да","как-то так","типа того","вот так"])
    return text

def rphone():
    d = [str(ri(0,9)) for _ in range(7)]
    return rc(PHONE_PFX)+" "+"".join(d[:3])+" "+"".join(d[3:5])+" "+"".join(d[5:])

def rdate(): return rc(DATES)
def rtime(): return rc(TIMES)
def rtime_f(): return rc(TIMES_F)
def rguest(n): return rc(GUEST_S.get(n,[f"{n} человек"]))
def rguestf(n): return GUEST_F.get(n,str(n))
def rhall(): return rc(HALLS)
def rname(): return rc(NAMES)
def rrest(): return rc(RESTS)

def greet():
    r = rrest()
    return rc([f"Добрый день! Ресторан «{r}», администратор слушает. Чем могу помочь?",
               f"Здравствуйте! Ресторан «{r}», рады вашему звонку. Чем могу быть полезна?",
               f"Добрый вечер! Ресторан «{r}», слушаю вас.",
               f"Здравствуйте! Ресторан «{r}», администратор на связи.",
               f"Алло, добрый день! Ресторан «{r}». Чем могу помочь?"])

def bye_u(): return nat(rc(INFORMAL_BYE))
def bye_a():
    return rc(["Благодарим за звонок! Хорошего вам дня!","Спасибо за звонок! Ждём вас, до свидания!",
               "Всего доброго! Будем рады вас видеть!","До свидания! Хорошего дня!",
               "Спасибо! Ждём вас, до встречи!"])

def phone_ex(name, c):
    """Phone number exchange turns."""
    c.append(A(rc([f"Спасибо, {name}! Подскажите контактный номер телефона.",
                   f"Записала, {name}. Оставьте номер телефона на случай изменений.",
                   f"Отлично, {name}! Ваш номер телефона для связи?",
                   f"{name}, продиктуйте номер телефона, пожалуйста."])))
    ph = rphone()
    v = random.random()
    if v < 0.3: c.append(U(nat(ph)))
    elif v < 0.55: c.append(U(nat(f"Да, записывайте: {ph}")))
    elif v < 0.75: c.append(U(nat(f"{ph[:15]}... нет, подождите... {ph}")))
    else: c.append(U(nat(f"Номер {ph}")))

def confirm_booking(name, n, date, time_f, hall, c):
    """Standard confirmation block."""
    c.append(A(rc([
        f"Записала: {name}, {hall}, {date}, {time_f}, на {rguestf(n)} гостей. Всё верно?",
        f"Итак, бронирую: {name}, {date}, {time_f}, {hall}, {rguestf(n)} персон. Подтверждаете?",
        f"Подтверждаю: столик на {rguestf(n)} гостей, {date}, {time_f}, {hall}. Верно?"])))
    c.append(U(nat(rc(["Да, всё верно","Угу, подтверждаю","Ага, всё так","Да, записывайте"]))))
    c.append(A(rc([f"Отлично, бронь оформлена! {name}, ждём вас {date}.",
                   f"Замечательно! Бронь подтверждена. Ждём вас!",
                   f"Готово! Столик забронирован. До встречи!"])))

# Shorthand constructors
def S(): return {"role":"system","content":SYS}
def A(t): return {"role":"assistant","content":t}
def U(t): return {"role":"user","content":t}

# ══════════ Scenario generators ══════════

def gen_simple_booking():
    n = rc([2,2,2,3,3,4,4,4,5,6,7,8])
    date,time_u,time_f,name = rdate(),rtime(),rtime_f(),rname()
    h1,h2 = rhall(),rhall()
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Хотел бы забронировать столик {date} {time_u}, {rguest(n)}",
        f"Можно столик? {date}, {rguest(n)}, {time_u}",
        f"{rc(INFORMAL_GREETS)}, нужен столик {date} на вечер, {rguest(n)}",
        f"Добрый день, хотели бы зарезервировать столик {date} {time_u}"]))))
    c.append(A(f"Конечно! Столик на {rguestf(n)} гостей, {date}. Предпочтения по залу? У нас {h1} и {h2}."))
    c.append(U(nat(rc([f"Давайте {h1}",f"В {h1}, пожалуйста",f"Мне без разницы, на ваше усмотрение",
                       f"{h2} будет лучше"]))))
    hall = h1
    c.append(A(f"Хорошо, {hall}. На чьё имя бронируем?"))
    c.append(U(nat(rc([name, f"На {name}", f"Имя — {name}", f"Запишите на {name}"]))))
    phone_ex(name, c)
    confirm_booking(name, n, date, time_f, hall, c)
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_occasion():
    n = rc([4,5,6,6,8,8,10,12,15])
    occ = rc(OCCASIONS[:4])  # birthday, anniversary, proposal
    date,time_u,time_f,name = rdate(),rtime(),rtime_f(),rname()
    spec = rc(SPECIAL)
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Хочу забронировать столик на {occ}, {rguest(n)}, {date}",
        f"У нас {occ}! Нужен столик {date}, {rguest(n)}",
        f"{rc(INFORMAL_GREETS)}, мы {occ} хотим отметить, {rguest(n)}, {date}"]))))
    c.append(A(f"Поздравляем! С удовольствием поможем. На {rguestf(n)} гостей, {date}. Рекомендую банкетный зал или VIP-зал. Есть пожелания по оформлению?"))
    c.append(U(nat(rc([f"Да, хотелось бы {spec}",f"Можно {spec} организовать?",
                       f"А {spec} у вас есть?",f"Нет, ничего особенного не нужно"]))))
    c.append(A(f"Конечно, организуем! Во сколько планируете прийти?"))
    c.append(U(nat(time_u)))
    c.append(A(f"Отлично. На чьё имя бронь?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Всё записала! {name}, {date}, {time_f}, {rguestf(n)} гостей, {occ}. Ждём вас!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_banquet():
    n = rc([15,20,20,25,30,40,50])
    date,time_u,time_f,name = rdate(),rtime(),rtime_f(),rname()
    budget = rc([2,3,4,5]) * 1000
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Нужен банкетный зал на {rguest(n)}, {date}",
        f"Хотим корпоратив провести, {rguest(n)}, {date}",
        f"Планируем банкет {date}, {rguest(n)}. Есть свободный зал?"]))))
    c.append(A(f"Конечно! На {rguestf(n)} гостей у нас подойдёт банкетный зал. {date} свободен. Бюджет на человека какой планируете?"))
    c.append(U(nat(rc([f"Ну где-то {budget} на человека",f"Примерно {budget} рублей",
                       f"Тысячи {budget//1000} на человека",f"Бюджет пока не определён"]))))
    c.append(A(f"Хорошо, подберём меню. Во сколько начало?"))
    c.append(U(nat(time_u)))
    c.append(A(f"Отлично. На чьё имя оформить?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Записала: банкет на {rguestf(n)} гостей, {date}, {time_f}. Менеджер свяжется с вами для обсуждения меню."))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_cancel():
    name = rname()
    reason = rc(CANCEL_REASONS)
    date = rdate()
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Хочу отменить бронь на {date}",f"Мне нужно отменить бронирование, {reason}",
        f"Отмените, пожалуйста, столик на {date}. {reason.capitalize()}",
        f"{rc(INFORMAL_GREETS)}, я бронировал столик на {date}, нужно отменить"]))))
    c.append(A(f"Конечно, подскажите на чьё имя была бронь?"))
    c.append(U(nat(rc([name, f"На {name}", f"Бронь на имя {name}"]))))
    c.append(A(f"Нашла бронь, {name}. Отменяю. Если планы изменятся — звоните, всегда будем рады!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_reschedule():
    name = rname()
    old_date, new_date = rdate(), rdate()
    new_time = rtime()
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Хочу перенести бронь с {old_date} на {new_date}",
        f"Можно перенести столик? Бронировали на {old_date}, а теперь нужно на {new_date}",
        f"Нам нужно изменить дату бронирования"]))))
    c.append(A(f"Конечно! На чьё имя бронь?"))
    c.append(U(nat(name)))
    c.append(A(f"Нашла. Переносим на {new_date}. Время остаётся прежним или меняем?"))
    c.append(U(nat(rc([f"Время поменяйте тоже, {new_time}",f"Время то же",
                       f"Давайте {new_time}",f"Нет, время оставьте"]))))
    c.append(A(f"Готово, {name}! Бронь перенесена на {new_date}. Ждём вас!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_time_unavailable():
    n = rc([2,3,4,4,5,6])
    date,time_u,name = rdate(),rtime(),rname()
    alt_time = rtime()
    c = [S(), A(greet())]
    c.append(U(nat(f"Хотел бы столик {date} {time_u}, {rguest(n)}")))
    c.append(A(f"К сожалению, {time_u} {date} всё занято. Могу предложить {alt_time} или другую дату. Как вам?"))
    v = random.random()
    if v < 0.6:
        c.append(U(nat(rc([f"Ладно, давайте {alt_time}",f"Ну {alt_time} пойдёт",
                           f"Хорошо, {alt_time} подойдёт"]))))
        c.append(A(f"Отлично! На чьё имя?"))
        c.append(U(nat(name)))
        phone_ex(name, c)
        c.append(A(f"Бронь оформлена! {name}, {date}, {alt_time}. Ждём вас!"))
    else:
        c.append(U(nat(rc(["Нет, тогда не получится","Жалко... тогда не надо",
                           "Нет, мне только это время подходит"]))))
        c.append(A("Понимаю. Если планы изменятся — звоните, будем рады помочь!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_allergy():
    n = rc([2,3,4,4,5,6])
    date,time_u,time_f,name = rdate(),rtime(),rtime_f(),rname()
    issue = rc(ALLERGIES + DIETS)
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Хотим столик {date}, {rguest(n)}. И у нас вопрос — есть {issue}?",
        f"Забронировать столик, {date}. У одного из гостей аллергия на {rc(ALLERGIES)}",
        f"Нужен столик {date}, {rguest(n)}. Есть ли у вас {rc(DIETS)}?"]))))
    c.append(A(f"Да, конечно! Мы учтём все пожелания. У нас есть специальные позиции в меню. Бронируем на {rguestf(n)} гостей, {date}?"))
    c.append(U(nat(rc(["Да, давайте","Отлично, бронируйте",rc(INFORMAL_YES)]))))
    c.append(A("Во сколько планируете?"))
    c.append(U(nat(time_u)))
    c.append(A(f"На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Готово! {name}, {date}, {time_f}, {rguestf(n)} гостей. Пожелания по меню передам шеф-повару."))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_self_correction():
    n = rc([2,3,4,5,6])
    date1, date2 = rdate(), rdate()
    time1, time2 = rtime(), rtime()
    name = rname()
    c = [S(), A(greet())]
    c.append(U(nat(f"Столик {date1} {time1}, {rguest(n)}")))
    c.append(A(f"Конечно! Столик на {rguestf(n)} гостей, {date1}, {time1}. На чьё имя?"))
    # Self-correction
    c.append(U(nat(rc([
        f"Ой, стоп, не {date1}, а {date2}!",f"Нет, подождите, я перепутал — {date2}, не {date1}",
        f"Ой, я ошиблась! Не {time1}, а {time2}",f"Стоп стоп, давайте {date2} {time2} лучше"]))))
    c.append(A(rc([f"Поняла, исправляю. {date2}. На чьё имя бронь?",
                   f"Без проблем, записываю {date2}. Имя для брони?"])))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Готово! {name}, ждём вас {date2}!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_unclear():
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        "Ну это... столик бы... ну вы понимаете",
        "Можно... э... ну это... как бы забронировать...",
        "Здрасте, мне бы это... ну как его... посидеть у вас",
        "Алё, а можно к вам прийти? Ну типа за столик",
        "Ну мне бы... это самое... ну вы понимаете наверное"]))))
    c.append(A("Конечно! Вы хотите забронировать столик? Подскажите, на какую дату, время и сколько гостей будет?"))
    n = rc([2,3,4])
    date, time_u = rdate(), rtime()
    c.append(U(nat(rc([f"Ну да, {date}, {rguest(n)}, {time_u}",
                       f"Ага, {date} бы, {rguest(n)}... {time_u} где-то"]))))
    name = rname()
    c.append(A(f"Поняла! {date}, {rguestf(n)} гостей. На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Бронь оформлена! Ждём вас, {name}!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_changes_mind():
    n1, n2 = rc([2,3,4]), rc([5,6,8])
    date, time_u, name = rdate(), rtime(), rname()
    h1, h2 = rhall(), rhall()
    c = [S(), A(greet())]
    c.append(U(nat(f"Столик {date} {time_u}, {rguest(n1)}")))
    c.append(A(f"Отлично, {rguestf(n1)} гостей, {date}. Зал — {h1} или {h2}?"))
    c.append(U(nat(f"Давайте {h1}")))
    c.append(A(f"Хорошо, {h1}. На чьё имя?"))
    # Changes mind
    c.append(U(nat(rc([
        f"Стоп, а знаете что, нас будет не {rguestf(n1)}, а {rguest(n2)}. Можно {h2} тогда?",
        f"Ой, подождите, я передумал. Лучше {h2} и {rguest(n2)}",
        f"Секунду... а давайте лучше {h2}? И нас будет {rguest(n2)}"]))))
    c.append(A(f"Конечно, меняю. {h2}, на {rguestf(n2)} гостей. На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Готово! {name}, {date}, {h2}. Ждём!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_vip():
    n = rc([2,2,4,4,6])
    date, time_u, time_f, name = rdate(), rtime(), rtime_f(), rname()
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Хотелось бы VIP-зал, {date}, {rguest(n)}",
        f"Есть ли у вас отдельный кабинет? Нужен {date}",
        f"Нам нужен приватный зал {date}, {rguest(n)}"]))))
    c.append(A(f"Да, VIP-зал на {rguestf(n)} гостей доступен {date}. Стоимость аренды — от 5000 рублей. Бронируем?"))
    c.append(U(nat(rc(["Да, бронируйте","Подходит, давайте","Ага, хорошо"]))))
    c.append(A("Во сколько ждать вас?"))
    c.append(U(nat(time_u)))
    c.append(A("На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"VIP-зал забронирован! {name}, {date}, {time_f}. Ждём вас!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_price():
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        "Скажите, а сколько стоит банкет у вас?","Какие цены на банкетный зал?",
        "Сколько стоит забронировать VIP-зал?","А прайс на банкеты есть?",
        "Интересуют цены на проведение мероприятия"]))))
    price = rc([2000,2500,3000,3500,4000,5000])
    c.append(A(f"Средний чек — от {price} рублей на человека. Банкетный зал — от 5000 рублей аренда. VIP-зал — от 8000. Хотите забронировать?"))
    if random.random() < 0.5:
        c.append(U(nat(rc(["Спасибо, я подумаю","Понял, перезвоню","Надо обсудить, спасибо"]))))
        c.append(A("Конечно! Будем рады, звоните в любое время."))
    else:
        n = rc([4,6,8,10])
        date = rdate()
        c.append(U(nat(f"Давайте забронируем, {rguest(n)}, {date}")))
        name = rname()
        c.append(A(f"С удовольствием! На чьё имя?"))
        c.append(U(nat(name)))
        phone_ex(name, c)
        c.append(A(f"Бронь оформлена! {name}, {date}, {rguestf(n)} гостей."))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_emotional(mood):
    """mood: 'excited', 'frustrated', 'worried'"""
    n = rc([2,3,4,5,6])
    date, time_u, name = rdate(), rtime(), rname()
    c = [S(), A(greet())]
    if mood == "excited":
        c.append(U(nat(f"{rc(EMOTIONS_POS)} Хотим столик {date}, {rguest(n)}! {rc(EMOTIONS_POS)}")))
        c.append(A(f"Как здорово! Бронируем на {rguestf(n)} гостей, {date}. Время?"))
        c.append(U(nat(f"{time_u}! {rc(EMOTIONS_POS)}")))
    elif mood == "frustrated":
        c.append(U(nat(f"{rc(EMOTIONS_NEG)} Мне бы столик {date}, {rguest(n)}")))
        c.append(A(f"Конечно, поможем! На {rguestf(n)} гостей, {date}. Во сколько?"))
        c.append(U(nat(f"{time_u}... {rc(EMOTIONS_NEG)}")))
    else:  # worried
        c.append(U(nat(f"Здравствуйте... {rc(EMOTIONS_WORRY)} Нужен столик {date}, {rguest(n)}")))
        c.append(A(f"Не переживайте, всё организуем! Столик на {rguestf(n)}, {date}. Время?"))
        c.append(U(nat(f"{time_u}... {rc(EMOTIONS_WORRY)}")))
    c.append(A("Записываю. На чьё имя?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Бронь готова! {name}, ждём вас {date}. Всё будет прекрасно!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_delivery_redirect():
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        "А у вас есть доставка?","Можно еду заказать на дом?",
        "Вы доставляете?","Хочу заказать доставку",
        "А навынос можно?"]))))
    c.append(A(rc([
        "К сожалению, мы не осуществляем доставку. Но вы можете забронировать столик! Или попробуйте заказать через агрегатор доставки.",
        "Доставки у нас нет, но можем оформить навынос если приедете. Или забронировать столик — будем рады видеть!",
        "Мы работаем только на месте. Но могу забронировать для вас столик!"])))
    if random.random() < 0.4:
        c.append(U(nat("Ладно, тогда давайте столик забронируем")))
        n = rc([2,3,4])
        date = rdate()
        c.append(A(f"С удовольствием! На какую дату и сколько гостей?"))
        c.append(U(nat(f"{date}, {rguest(n)}")))
        name = rname()
        c.append(A(f"На чьё имя?"))
        c.append(U(nat(name)))
        c.append(A(f"Готово! {name}, ждём вас {date}!"))
    else:
        c.append(U(nat(rc(["Ладно, понял, спасибо","Жалко, ну ладно","Окей, спасибо"]))))
        c.append(A("Будем рады, если решите заглянуть к нам! До свидания!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_aggressive():
    n = rc([2,4,6])
    date, time_u, name = rdate(), rtime(), rname()
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        f"Слушайте, мне нужен столик {date} и побыстрее!",
        f"Чё так долго трубку берёте? Столик нужен {date}!",
        f"Алё! Столик давайте, {date}, {rguest(n)}, побыстрее!",
        f"Так, мне срочно нужен столик {date}, чё тут сложного?"]))))
    c.append(A(f"Конечно, сейчас всё оформим! На {rguestf(n)} гостей, {date}. Время?"))
    c.append(U(nat(f"{time_u}, давайте быстрее")))
    c.append(A(f"Записываю. На чьё имя бронь?"))
    c.append(U(nat(name)))
    phone_ex(name, c)
    c.append(A(f"Всё готово, {name}! Бронь на {date}. Ждём вас, хорошего дня!"))
    c.append(U(nat(rc(["Ладно","Угу","Ну давайте","Ага, пока"]))))
    c.append(A(bye_a()))
    return c

def gen_background_noise():
    n = rc([2,3,4,5])
    date, time_u, name = rdate(), rtime(), rname()
    c = [S(), A(greet())]
    c.append(U(f"[шум] {nat(f'столик {date} {rguest(n)}')} [неразборчиво]"))
    c.append(A("Извините, плохо слышно. Вы хотите забронировать столик? На какую дату и сколько гостей?"))
    c.append(U(f"{nat(f'{date}, {rguest(n)}, {time_u}')} [помехи]"))
    c.append(A(f"Поняла, {date}, на {rguestf(n)} гостей. На чьё имя?"))
    c.append(U(f"[шум] {nat(name)}"))
    c.append(A(f"Записала — {name}. Номер телефона?"))
    ph = rphone()
    c.append(U(f"{nat(ph)} [неразборчиво]"))
    c.append(A(f"Повторите, пожалуйста, номер. Плохо слышно."))
    c.append(U(nat(ph)))
    c.append(A(f"Спасибо! Бронь оформлена, {name}. Ждём вас {date}!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_callback():
    name = rname()
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        "Мне сейчас неудобно говорить, можете перезвонить?",
        "Я за рулём, перезвоните через полчаса",
        "Слушайте, мне надо уточнить у жены, можно я перезвоню?"]))))
    c.append(A(rc([
        "Конечно! Когда вам удобно будет — звоните, мы на связи.",
        "Без проблем! Перезвоните в любое удобное время, мы работаем до 23:00.",
        f"Хорошо! Если хотите, оставьте имя и номер — мы сами вам перезвоним."])))
    if random.random() < 0.4:
        c.append(U(nat(f"Давайте, я {name}, номер {rphone()}")))
        c.append(A(f"Записала, {name}! Перезвоним вам. До связи!"))
    else:
        c.append(U(nat("Нет, я сам перезвоню, спасибо")))
        c.append(A("Хорошо, ждём вашего звонка!"))
    c.append(U(bye_u())); c.append(A(bye_a()))
    return c

def gen_transfer():
    c = [S(), A(greet())]
    c.append(U(nat(rc([
        "Мне нужно поговорить с менеджером",
        "Можно управляющего?","Переключите на администратора, пожалуйста",
        "Мне надо обсудить кое-что с вашим руководством",
        "Соедините с менеджером по банкетам"]))))
    c.append(A(rc([
        "Конечно, сейчас соединю вас. Одну минуту, пожалуйста.",
        "Секунду, переключаю на менеджера. Оставайтесь на линии.",
        "Хорошо, перевожу звонок. Подождите, пожалуйста."])))
    c.append(U(nat(rc(["Хорошо, спасибо","Ага, жду","Угу"]))))
    return c

# ══════════ Main ══════════

DISTRIBUTION = {
    "simple_booking": (295, gen_simple_booking),
    "occasion_booking": (175, gen_occasion),
    "banquet_corporate": (135, gen_banquet),
    "cancellation": (110, gen_cancel),
    "reschedule": (110, gen_reschedule),
    "time_unavailable": (90, gen_time_unavailable),
    "allergy_diet": (85, gen_allergy),
    "self_correction": (85, gen_self_correction),
    "unclear_vague": (65, gen_unclear),
    "changes_mind": (55, gen_changes_mind),
    "vip_room": (55, gen_vip),
    "price_inquiry": (45, gen_price),
    "emotional_excited": (40, lambda: gen_emotional("excited")),
    "emotional_frustrated": (40, lambda: gen_emotional("frustrated")),
    "emotional_worried": (35, lambda: gen_emotional("worried")),
    "delivery_redirect": (20, gen_delivery_redirect),
    "aggressive": (20, gen_aggressive),
    "background_noise": (20, gen_background_noise),
    "call_back": (10, gen_callback),
    "transfer_admin": (10, gen_transfer),
}

def generate_all(total=1500):
    dialogs = []
    for name, (count, gen) in DISTRIBUTION.items():
        for _ in range(count):
            dialogs.append({"conversations": gen()})
    random.shuffle(dialogs)
    return dialogs

if __name__ == "__main__":
    dialogs = generate_all(1500)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restaurant_dialogs_v3.jsonl")

    with open(out, "w", encoding="utf-8") as f:
        for d in dialogs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"Generated {len(dialogs)} dialogs -> {out}")

    # Validate
    with open(out, "r", encoding="utf-8") as f:
        lines = f.readlines()
    valid = sum(1 for l in lines if "conversations" in json.loads(l.strip()) and
                len(json.loads(l.strip())["conversations"]) >= 3 and
                json.loads(l.strip())["conversations"][0]["role"] == "system")
    print(f"Validation: {valid}/{len(lines)} valid")

    first = json.loads(lines[0])
    for t in first["conversations"]:
        print(f"  [{t['role']}]: {t['content'][:120]}{'...' if len(t['content'])>120 else ''}")
    print(f"\nTotal: {len(lines)} dialogs")
