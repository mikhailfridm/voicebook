#!/usr/bin/env python3
"""Generate 500 realistic restaurant SFT dialogs in Russian."""
import json
import random
import os

random.seed(42)

SYSTEM = "Вы — администратор ресторана. Помогаете гостям забронировать столик, выбрать зал и обсудить детали визита. Говорите вежливо, гостеприимно и профессионально."

RESTAURANTS = [
    "Олива", "Шато", "Тоскана", "Прованс", "Империя вкуса",
    "Белая акация", "Камелот", "Ривьера", "Золотой лев", "Барская усадьба",
    "Трюфель", "Огонёк", "Сказка", "Палаццо", "Лаванда",
    "Терраса", "Бархат", "Мельница", "Старый город", "Атриум",
    "Причал", "Усадьба", "Дворянское гнездо", "Маяк", "Базилик",
    "Серебряный век", "Вишнёвый сад", "Пряности", "Бриз", "Каравелла"
]

ADMIN_GREETINGS = [
    "Добрый день! Ресторан «{r}», администратор слушает.",
    "Здравствуйте! Ресторан «{r}», чем могу помочь?",
    "Добрый день! Ресторан «{r}», администратор на связи. Слушаю вас.",
    "Ресторан «{r}», добрый день! Чем могу быть полезна?",
    "Добрый вечер! Ресторан «{r}», администратор. Слушаю вас.",
    "Здравствуйте! «{r}», администратор ресторана. Чем могу помочь?",
    "Добрый день! Вы позвонили в ресторан «{r}». Слушаю вас.",
    "Ресторан «{r}», здравствуйте! Администратор слушает.",
]

NAMES_M = ["Алексей","Дмитрий","Сергей","Андрей","Михаил","Иван","Максим","Павел","Артём","Николай","Олег","Роман","Виктор","Егор","Тимур","Руслан","Денис","Владимир","Константин","Антон"]
NAMES_F = ["Елена","Мария","Ольга","Анна","Татьяна","Наталья","Екатерина","Ирина","Светлана","Юлия","Алина","Дарья","Виктория","Марина","Ксения","Полина","Надежда","Валерия","Людмила","Галина"]

DAYS = ["в понедельник","во вторник","в среду","в четверг","в пятницу","в субботу","в воскресенье"]
DATES = ["завтра","послезавтра","в эту субботу","в следующую пятницу","через неделю","на выходных","в эту пятницу","в следующую субботу","двадцатого","пятнадцатого числа","в следующее воскресенье","тридцать первого декабря","восьмого марта","двадцать третьего февраля","четырнадцатого февраля"]
TIMES = ["в восемнадцать часов","в девятнадцать часов","в двадцать часов","в семь вечера","в восемь вечера","к шести","часам к семи","в полседьмого","в девятнадцать тридцать","к обеду, часам к двенадцати","в час дня","в два часа дня","в половине восьмого"]
TIMES_INFORMAL = ["часов в шесть","ну где-то в семь","к восьми наверное","часиков в семь","ну... в шесть примерно","в районе семи","ближе к восьми","к семи где-то"]

GUEST_COUNTS_FORMAL = ["двоих","троих","четверых","пятерых","шестерых","семерых","восьмерых","десятерых","двенадцать человек","пятнадцать человек","двадцать человек","двадцать пять гостей","тридцать человек"]
GUEST_COUNTS_INFORMAL = ["двоих","нас будет трое","четверо нас","пятеро","нас шестеро","семь человек","восемь","нас десять будет","человек двенадцать","пятнашка примерно"]

FILLERS = ["ну","эм","так","вот","ааа","короче","слушайте","типа","как бы","в общем","значит","это","ну вот","ну такое","ну короче"]
NOISE = ["[неразборчиво]","[голоса на фоне]","[шум машин]","[шум на фоне]","[помехи]","[пауза]","[смех]"]

HALLS = ["основной зал","VIP-зал","банкетный зал","летняя веранда","зал у камина","лаунж-зона","зал на втором этаже","терраса","малый зал","каминный зал"]
TABLES = ["у окна","в углу","на веранде","у камина","в центре зала","в тихом месте","подальше от входа","с видом на город","на балконе","у аквариума"]

COMPANIES = ["ТехноГруп","АльфаСервис","МегаСтрой","Глобал Трейд","СитиЛайн","ПромИнвест","Бизнес Партнёр","Медиа Плюс","ЭкоСтандарт","ИнфоТех"]

ALLERGIES = ["глютен","лактоза","орехи","морепродукты","мёд","яйца","соя","цитрусовые","грибы","рыба"]
DIETS = ["вегетарианское меню","веганское меню","безглютеновое меню","постное меню","халяльное меню","кошерное меню","низкокалорийное меню","детское меню"]

def filler():
    return random.choice(FILLERS)

def maybe_filler(p=0.4):
    return f"{filler()} " if random.random() < p else ""

def maybe_noise(p=0.1):
    return f" {random.choice(NOISE)}" if random.random() < p else ""

def rand_name():
    if random.random() < 0.5:
        return random.choice(NAMES_M), "m"
    return random.choice(NAMES_F), "f"

def rand_phone():
    return f"+7 {random.randint(900,999)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"

def rand_restaurant():
    return random.choice(RESTAURANTS)

def greeting(r):
    return random.choice(ADMIN_GREETINGS).format(r=r)

dialogs = []

# ============================================================
# SCENARIO GENERATORS (each produces a list of conversations)
# ============================================================

def scenario_regular_table():
    """Regular calling about their usual table."""
    r = rand_restaurant()
    name, g = rand_name()
    day = random.choice(DATES[:8])
    time = random.choice(TIMES_INFORMAL)
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"{maybe_filler()}Здравствуйте, это {name}, я у вас постоянный гость. {maybe_filler()}Мой столик свободен {day}?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте, {name}! Рады вас слышать. Позвольте уточнить — ваш любимый столик {random.choice(TABLES)}? На какое время вас ожидать?"},
        {"role": "user", "content": f"{maybe_filler()}{time}, как обычно{maybe_noise()}"},
        {"role": "assistant", "content": f"Прекрасно! Столик забронирован на ваше имя, {day}, {random.choice(TIMES[:5])}. Вас будет {'двое, как всегда' if random.random()<0.5 else 'только вы'}?"},
        {"role": "user", "content": f"Да, {filler()}, как обычно. Спасибо!"},
        {"role": "assistant", "content": f"Отлично, {name}! Всё записано. Будем рады вас видеть. Хорошего дня!"},
    ]
    return convs

def scenario_surprise_party():
    """Surprise party planning."""
    r = rand_restaurant()
    name, g = rand_name()
    bday_name, _ = rand_name()
    count = random.choice(["десять","двенадцать","пятнадцать","восемь","двадцать"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Мне нужна помощь — хочу устроить сюрприз на день рождения {('подруге' if random.random()<0.5 else 'другу')}. Только {('она' if random.random()<0.5 else 'он')} ничего не должен{'а' if random.random()<0.5 else ''} знать!{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Какая замечательная идея! Мы с удовольствием поможем организовать сюрприз. Сколько гостей планируется и на какую дату?"},
        {"role": "user", "content": f"{maybe_filler()}Нас будет {count} человек, {random.choice(DATES[:8])}. Можно отдельный зал, чтоб {bday_name} не видел{'а' if random.random()<0.3 else ''} нас, когда войдёт?"},
        {"role": "assistant", "content": f"Конечно! У нас есть {random.choice(['банкетный зал','VIP-зал','малый зал'])}, который идеально подходит для таких мероприятий. Мы можем провести именинника через основной зал, а гости уже будут ждать внутри. Хотите заказать торт и украшение зала?"},
        {"role": "user", "content": f"Торт у нас свой будет, а вот шарики и украшения — это было бы здорово! {maybe_filler()}И чтобы музыку включили в нужный момент{maybe_noise()}"},
        {"role": "assistant", "content": f"Замечательно! Свой торт — без проблем, мы только попросим предупредить заранее. Украшение зала шарами — две тысячи пятьсот рублей. Музыкальное оформление входит в стоимость аренды. Какой бюджет на банкет вы рассматриваете?"},
        {"role": "user", "content": f"{filler()} ну давайте {random.choice(['три','три с половиной','четыре'])} тысячи на человека"},
        {"role": "assistant", "content": f"Отличный выбор! На чьё имя оформляем бронирование и контактный телефон для связи?"},
        {"role": "user", "content": f"{name}, {rand_phone()}"},
        {"role": "assistant", "content": f"Записала! {name}, бронь оформлена. Мы всё подготовим к сюрпризу. За день до мероприятия свяжемся с вами для подтверждения деталей. Хорошего дня!"},
    ]
    return convs

def scenario_own_cake_wine():
    """Client asking about bringing own cake/wine."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}У нас день рождения, хотим отметить у вас. А можно свой торт принести?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Конечно, вы можете принести свой торт. Мы берём пробковый сбор — {random.choice(['пятьсот','семьсот','восемьсот'])} рублей за нарезку и подачу. Сколько гостей ожидается?"},
        {"role": "user", "content": f"Нас будет {random.choice(['восемь','десять','шесть','двенадцать'])}. А вино своё тоже можно?"},
        {"role": "assistant", "content": f"К сожалению, свой алкоголь мы не разрешаем приносить — у нас лицензия на продажу алкогольной продукции. Но у нас отличная винная карта, и сомелье с удовольствием поможет подобрать вино под ваше меню. Могу я узнать, на какую дату планируете?"},
        {"role": "user", "content": f"{maybe_filler()}{random.choice(DATES[:8])}, {random.choice(TIMES_INFORMAL)}"},
        {"role": "assistant", "content": f"Отлично! На чьё имя бронируем столик?"},
        {"role": "user", "content": f"{name}"},
        {"role": "assistant", "content": f"Записала, {name}! Бронь оформлена. Торт можете привезти заранее или в день мероприятия. Ждём вас!"},
    ]
    return convs

def scenario_secretary_booking():
    """Secretary booking for the boss."""
    r = rand_restaurant()
    sec_name, _ = rand_name()
    boss_name, bg = rand_name()
    company = random.choice(COMPANIES)
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день. Я {sec_name}, ассистент{'ка' if random.random()<0.3 else ''} {('генерального директора' if random.random()<0.5 else 'руководителя')} компании «{company}». Нужно забронировать столик для деловой встречи.{maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день, {sec_name}! С удовольствием поможем. На сколько гостей и на какую дату?"},
        {"role": "user", "content": f"{maybe_filler()}{random.choice(['На троих','На четверых','На двоих','На пятерых'])}, {random.choice(DATES[:8])}, {random.choice(TIMES[:5])}. Желательно {random.choice(['тихое место','отдельный кабинет','VIP-зал'])} — будут обсуждаться деловые вопросы."},
        {"role": "assistant", "content": f"Понимаю, конечно. У нас есть {random.choice(['VIP-кабинет на четверых','отдельная зона в каминном зале','кабинет для переговоров'])} — там тихо и комфортно. На чьё имя оформляем бронь?"},
        {"role": "user", "content": f"На {boss_name} {random.choice(['Петрович','Сергеевич','Александрович','Викторович'])}. И, пожалуйста, подготовьте счёт на компанию для бухгалтерии."},
        {"role": "assistant", "content": f"Конечно, подготовим счёт на юридическое лицо. Пришлите, пожалуйста, реквизиты на нашу почту. Бронь оформлена. Что-нибудь ещё?"},
        {"role": "user", "content": f"Нет, спасибо. Всего доброго."},
        {"role": "assistant", "content": f"Благодарим за бронирование! Хорошего дня, {sec_name}. Ждём вас!"},
    ]
    return convs

def scenario_tourist():
    """Tourist asking about local cuisine in broken Russian."""
    r = rand_restaurant()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здраствуйте! Я... {random.choice(['турист из Китая','из Турции приехал','из Кореи','гость из Японии'])}. {maybe_filler()}Хочу... кушать русский еда. Что у вас есть... {random.choice(['борщ, пельмени?','блины, пироги?','щи, каша?'])}"},
        {"role": "assistant", "content": f"Здравствуйте! Добро пожаловать! Мы очень рады гостям. В нашем меню есть блюда русской кухни — борщ, пельмени домашние, блины с различными начинками, пироги. Хотите забронировать столик?"},
        {"role": "user", "content": f"Да, да! {maybe_filler()}Столик на... {random.choice(['два человек','три','два'])}. {random.choice(['Сегодня вечер','Завтра обед','Сегодня'])}. Можно?"},
        {"role": "assistant", "content": f"Конечно! Столик на {'двоих' if random.random()<0.6 else 'троих'}, забронирован. На какое имя записать?"},
        {"role": "user", "content": f"{random.choice(['Ли','Ахмет','Юн','Хироши','Мин'])}. Спасибо болшое!"},
        {"role": "assistant", "content": f"Записала! Ждём вас, будем рады помочь с выбором блюд. Наши официанты подскажут всё о каждом блюде. До встречи!"},
    ]
    return convs

def scenario_late_cancellation():
    """Late cancellation (1 hour before)."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте, {maybe_filler()}я {name}, у меня бронь на сегодня на {random.choice(TIMES[:5])}. {maybe_filler()}Мне нужно отменить... извините, я знаю, что поздно звоню{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте, {name}. Да, вижу вашу бронь. К сожалению, при отмене менее чем за два часа мы обычно просим предупреждать заранее. Но я понимаю, бывают разные ситуации. Может быть, перенесём на другой день?"},
        {"role": "user", "content": f"{filler()}, {random.choice(['да, давайте перенесём','ну... можно на следующую неделю','нет, пока не знаю когда получится'])}"},
    ]
    if "да" in convs[-1]["content"] or "давайте" in convs[-1]["content"] or "можно" in convs[-1]["content"]:
        convs.extend([
            {"role": "assistant", "content": f"Хорошо! На какой день и время вам удобно?"},
            {"role": "user", "content": f"{maybe_filler()}{random.choice(DATES[:8])}, {random.choice(TIMES_INFORMAL)}"},
            {"role": "assistant", "content": f"Записала! Бронь перенесена. {name}, будем вас ждать. Хорошего дня!"},
        ])
    else:
        convs.extend([
            {"role": "assistant", "content": f"Хорошо, {name}, бронь отменена. Когда определитесь с датой — звоните, будем рады видеть вас снова. Всего доброго!"},
            {"role": "user", "content": "Спасибо, извините ещё раз. До свидания."},
            {"role": "assistant", "content": "Ничего страшного! Всего доброго, ждём вас в следующий раз!"},
        ])
    return convs

def scenario_specific_table():
    """Client wants a specific table."""
    r = rand_restaurant()
    name, g = rand_name()
    table = random.choice(TABLES)
    count = random.choice(["двоих","троих","четверых"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день! {maybe_filler()}Хочу забронировать столик на {count}, но мне нужен именно столик {table}. Это возможно?{maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день! На какую дату и время вы хотели бы забронировать?"},
        {"role": "user", "content": f"{random.choice(DATES[:8])}, {random.choice(TIMES_INFORMAL)}"},
    ]
    if random.random() < 0.7:
        convs.extend([
            {"role": "assistant", "content": f"Отлично, столик {table} на {count} свободен. С удовольствием забронирую. На чьё имя?"},
            {"role": "user", "content": f"{name}"},
            {"role": "assistant", "content": f"Готово, {name}! Столик {table} забронирован. Ждём вас!"},
        ])
    else:
        alt_table = random.choice([t for t in TABLES if t != table])
        convs.extend([
            {"role": "assistant", "content": f"К сожалению, столик {table} на это время уже занят. Могу предложить столик {alt_table} — там тоже очень уютно. Или можем поискать другое время для вашего столика."},
            {"role": "user", "content": f"{filler()}, ладно, давайте {alt_table} тогда"},
            {"role": "assistant", "content": f"Отлично! На чьё имя бронируем?"},
            {"role": "user", "content": f"{name}"},
            {"role": "assistant", "content": f"Записала, {name}! Столик {alt_table} забронирован. Будем рады вас видеть!"},
        ])
    return convs

def scenario_noisy_group():
    """Noisy group reservation with special requests."""
    r = rand_restaurant()
    name, g = rand_name()
    count = random.choice(["восемь","десять","двенадцать","пятнадцать"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Алло! {maybe_filler()}[голоса на фоне] Нам нужен столик на {count} человек! {maybe_filler()}Мы тут компанией отмечаем... [смех] ...короче, можно на {random.choice(DATES[:6])}?"},
        {"role": "assistant", "content": f"Здравствуйте! Конечно, с удовольствием организуем. На {count} гостей лучше всего подойдёт {random.choice(['банкетный зал','отдельная зона','VIP-зал'])}. На какое время?"},
        {"role": "user", "content": f"[голоса на фоне] {filler()}, {random.choice(TIMES_INFORMAL)}! И можно {random.choice(['караоке','музыку погромче','чтоб танцевать можно было'])}?{maybe_noise()}"},
        {"role": "assistant", "content": f"Понимаю, хотите повеселиться! {random.choice(['Караоке у нас есть в VIP-зале, аренда — три тысячи рублей за вечер.','Музыку мы подберём по вашим пожеланиям.','Танцпол у нас есть в основном зале.'])} Хотите заказать банкетное меню или будете по меню?"},
        {"role": "user", "content": f"[неразборчиво]... банкетное давайте! {filler()} А сколько стоит?"},
        {"role": "assistant", "content": f"Банкетное меню — от {random.choice(['двух тысяч','двух тысяч пятисот','трёх тысяч'])} рублей на персону. Включает закуски, горячее, десерт и напитки. На чьё имя бронируем?"},
        {"role": "user", "content": f"{name}! [смех на фоне] Записывайте!"},
        {"role": "assistant", "content": f"Записала, {name}! Бронь на {count} гостей оформлена. Позвоните нам за день до мероприятия для подтверждения. Хорошего вечера!"},
    ]
    return convs

def scenario_romantic_proposal():
    """Romantic dinner proposal setup."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте... {maybe_filler()}мне нужна ваша помощь. Я хочу сделать предложение девушке у вас в ресторане. Можете помочь организовать?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Какое трогательное событие! Конечно, мы с радостью поможем. Расскажите, как вы себе это представляете?"},
        {"role": "user", "content": f"{filler()}, ну... {random.choice(['хочу чтобы были свечи, цветы, и чтобы кольцо принесли с десертом','может музыкант подойдёт и сыграет, а потом я встану на колено','чтобы всё было красиво, лепестки роз и шампанское'])}"},
        {"role": "assistant", "content": f"Прекрасная идея! Мы можем организовать {random.choice(['отдельный столик в каминном зале с декором из свечей и цветов','романтическую зону на террасе с лепестками роз','VIP-кабинет с индивидуальным оформлением'])}. Стоимость декора — от {random.choice(['пяти','семи','десяти'])} тысяч рублей. Музыкант — {random.choice(['три','пять'])} тысяч рублей за выступление."},
        {"role": "user", "content": f"Да, давайте всё! {maybe_filler()}Мне нужно чтобы идеально было. {random.choice(DATES[:8])}, {random.choice(TIMES[:5])}"},
        {"role": "assistant", "content": f"Замечательно! Мы всё подготовим. Подскажите, как вы хотите, чтобы кольцо было подано — в бокале, с десертом, в шкатулке на подносе?"},
        {"role": "user", "content": f"{filler()}, давайте {random.choice(['в шкатулке на подносе с десертом','в бокале шампанского','пусть официант принесёт на серебряном подносе'])}"},
        {"role": "assistant", "content": f"Идеально! На чьё имя бронируем и контактный номер?"},
        {"role": "user", "content": f"{name}, {rand_phone()}"},
        {"role": "assistant", "content": f"Записала, {name}! Мы свяжемся с вами за два дня, чтобы обсудить все детали. Кольцо можете передать нам заранее или в день визита. Желаю удачи — уверена, всё пройдёт прекрасно!"},
    ]
    return convs

def scenario_complaint_rebook():
    """Complaint about previous visit + rebooking."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте. {maybe_filler()}Я {name}, был{'а' if g=='f' else ''} у вас на прошлой неделе и, честно говоря, остал{'а' if g=='f' else 'о'}сь {'недовольна' if g=='f' else 'недоволен'}. {random.choice(['Официант был невнимательный, ждали заказ больше часа.','Столик был грязный, и нам пришлось пересаживаться.','Заказали стейк medium rare, принесли well done.','Музыка играла слишком громко, невозможно было разговаривать.'])}"},
        {"role": "assistant", "content": f"Здравствуйте, {name}. Мне очень жаль, что ваш визит оставил негативное впечатление. Это совершенно не тот уровень сервиса, к которому мы стремимся. Я обязательно передам ваш отзыв руководству. Могу ли я как-то исправить ситуацию?"},
        {"role": "user", "content": f"{filler()}, ну... {random.choice(['вообще мне у вас нравится, хочу дать ещё один шанс','я всё-таки хочу попробовать ещё раз','друзья говорят, что у вас обычно всё хорошо'])}. Можно забронировать столик?"},
        {"role": "assistant", "content": f"Спасибо за ваше доверие, {name}! Мы сделаем всё, чтобы ваш следующий визит был безупречным. Я лично проконтролирую подготовку. На какую дату и время?"},
        {"role": "user", "content": f"{random.choice(DATES[:8])}, {random.choice(TIMES_INFORMAL)}, на {random.choice(GUEST_COUNTS_FORMAL[:4])}"},
        {"role": "assistant", "content": f"Записала! И в качестве извинения от ресторана мы хотели бы предложить вам {random.choice(['комплимент от шефа','бесплатный десерт','бокал вина в подарок','скидку десять процентов на весь заказ'])}. Ждём вас, {name}!"},
        {"role": "user", "content": f"Ой, спасибо! Это приятно. До свидания."},
        {"role": "assistant", "content": f"До встречи, {name}! Хорошего дня!"},
    ]
    return convs

def scenario_live_music():
    """Asking about live music schedule."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день! {maybe_filler()}А у вас бывает живая музыка? {random.choice(['Хотим посидеть под джаз','Слышала, у вас по пятницам играют','Ищем ресторан с живой музыкой'])}{maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день! Да, у нас {random.choice(['каждую пятницу и субботу','по пятницам','по субботам'])} играет живой {random.choice(['джаз-бэнд','саксофонист','пианист','ансамбль'])}. Начало в {random.choice(['двадцать часов','девятнадцать тридцать','двадцать один час'])}. Хотите забронировать столик?"},
        {"role": "user", "content": f"О, класс! {maybe_filler()}Да, давайте на {random.choice(['эту пятницу','эту субботу','следующую пятницу'])}, на {random.choice(GUEST_COUNTS_FORMAL[:4])}"},
        {"role": "assistant", "content": f"Отлично! Рекомендую столик поближе к сцене — оттуда лучше всего слышно. На чьё имя?"},
        {"role": "user", "content": f"{name}"},
        {"role": "assistant", "content": f"Записала, {name}! Столик у сцены забронирован. Приятного вечера!"},
    ]
    return convs

def scenario_allergies():
    """Client with many allergies/dietary restrictions."""
    r = rand_restaurant()
    name, g = rand_name()
    allergy1, allergy2 = random.sample(ALLERGIES, 2)
    diet = random.choice(DIETS)
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте. {maybe_filler()}Я хочу забронировать столик, но у меня сложная ситуация с питанием. У меня аллергия на {allergy1} и {allergy2}, плюс мне нужно {diet}. Вы можете что-то предложить?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Конечно, мы учтём все ваши особенности питания. Наш шеф-повар может адаптировать блюда из меню, исключив {allergy1} и {allergy2}. Также у нас есть {diet}. На какую дату хотите забронировать?"},
        {"role": "user", "content": f"{maybe_filler()}{random.choice(DATES[:8])}, на {random.choice(GUEST_COUNTS_FORMAL[:3])}. {random.choice(['И мой спутник — веган','Со мной будет подруга, она ест всё','Мы все с ограничениями'])}."},
        {"role": "assistant", "content": f"Хорошо, я сделаю пометку для кухни. Могу предложить вам созвониться с нашим шеф-поваром заранее, чтобы обсудить меню и подготовить блюда специально для вас. На чьё имя бронь?"},
        {"role": "user", "content": f"{name}. И да, {filler()}, созвониться с шефом было бы отлично!"},
        {"role": "assistant", "content": f"Замечательно, {name}! Бронь оформлена. Шеф-повар свяжется с вами по номеру, с которого вы звоните, чтобы обсудить меню. Спасибо за предупреждение — мы хотим, чтобы вы наслаждались ужином без забот!"},
    ]
    return convs

def scenario_corporate_event():
    """Corporate event with presentation needs."""
    r = rand_restaurant()
    name, g = rand_name()
    company = random.choice(COMPANIES)
    count = random.choice(["двадцать","двадцать пять","тридцать","сорок","пятьдесят"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день. {maybe_filler()}Нам нужно организовать корпоративное мероприятие с презентацией. Человек {count}. Нужен проектор, экран и микрофон.{maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день! Наш банкетный зал прекрасно подходит для таких мероприятий. Он вмещает до {random.choice(['шестидесяти','пятидесяти','восьмидесяти'])} гостей и полностью оборудован: проектор, экран, аудиосистема с микрофонами, флипчарт. На какую дату планируете?"},
        {"role": "user", "content": f"{random.choice(DATES[:8])}. Формат — {random.choice(['сначала презентация полтора часа, потом банкет','банкет с короткими выступлениями','кофе-брейк, потом заседание, потом ужин'])}"},
        {"role": "assistant", "content": f"Отлично! Мы организуем всё под ваш формат. Аренда зала с оборудованием — {random.choice(['пятнадцать','двадцать','двадцать пять'])} тысяч рублей. При заказе банкета от трёх тысяч рублей на персону аренда бесплатна. Какой бюджет на банкет?"},
        {"role": "user", "content": f"{filler()}, давайте за {random.choice(['три','три с половиной','четыре','пять'])} тысячи на человека. И {random.choice(['кофе-брейк в начале','фуршет на регистрации','приветственный бокал шампанского'])}"},
        {"role": "assistant", "content": f"Прекрасно! Всё включим в программу. На чьё имя и компанию оформляем?"},
        {"role": "user", "content": f"{name}, компания «{company}». Нам потребуется счёт на юрлицо и акт."},
        {"role": "assistant", "content": f"Конечно, {name}! Подготовим все документы. Пришлите реквизиты на нашу электронную почту. Наш менеджер по мероприятиям свяжется с вами для обсуждения деталей. Всего доброго!"},
    ]
    return convs

def scenario_wrong_restaurant():
    """Client confused between restaurants."""
    r = rand_restaurant()
    wrong_r = random.choice([x for x in RESTAURANTS if x != r])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Я хочу забронировать столик. У вас же есть суши-бар на втором этаже, да?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Нет, к сожалению, суши-бара у нас нет. Возможно, вы нас путаете с другим заведением? Мы — ресторан «{r}», у нас {random.choice(['европейская кухня','русская и европейская кухня','авторская кухня','итальянская кухня'])}."},
        {"role": "user", "content": f"Ой, {filler()}, точно! Я перепутал{'а' if random.random()<0.4 else ''}... Это же «{wrong_r}»? {maybe_filler()}А какой у вас номер-то тогда?"},
        {"role": "assistant", "content": f"Нет, вы позвонили в ресторан «{r}». Номер «{wrong_r}», к сожалению, я не подскажу. Но если вас заинтересует наше меню — мы с удовольствием примем вас! У нас {random.choice(['отличный выбор блюд','прекрасная кухня','уютная атмосфера и вкусная еда'])}."},
        {"role": "user", "content": f"{random.choice(['Ладно, спасибо, я поищу номер','А что у вас есть? Может, к вам зайду','Нет, мне именно суши нужны, спасибо'])}"},
    ]
    if "к вам" in convs[-1]["content"] or "что у вас" in convs[-1]["content"]:
        convs.extend([
            {"role": "assistant", "content": f"С удовольствием! Наши хиты — {random.choice(['паста ручной работы и стейки','домашние пельмени и борщ','ризотто и морепродукты','утиная грудка и тартар из тунца'])}. Средний чек — от полутора тысяч рублей. Хотите забронировать столик?"},
            {"role": "user", "content": f"Звучит неплохо, давайте!"},
            {"role": "assistant", "content": f"Отлично! На какую дату и сколько гостей?"},
        ])
    else:
        convs.append({"role": "assistant", "content": f"Понимаю! Удачи в поиске. Если решите зайти к нам — звоните, будем рады. Всего доброго!"})
    return convs

def scenario_takeaway():
    """Takeaway/delivery inquiry."""
    r = rand_restaurant()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Алло, {maybe_filler()}а вы доставляете?{maybe_noise()} Хочу заказать на дом."},
        {"role": "assistant", "content": f"Здравствуйте! К сожалению, доставку мы не осуществляем. Но вы можете оформить заказ навынос — мы подготовим блюда, и вы сможете забрать их в ресторане. Также мы принимаем бронирование столиков, если хотите поужинать у нас."},
        {"role": "user", "content": f"{filler()}, жалко... {random.choice(['А навынос можно тогда?','Ладно, спасибо','А если я через Яндекс Еду закажу?','Ну тогда может столик забронирую'])}"},
    ]
    if "навынос" in convs[-1]["content"]:
        convs.extend([
            {"role": "assistant", "content": f"Конечно! Позвоните за {random.choice(['тридцать','сорок','сорок пять'])} минут, и мы подготовим ваш заказ. Что бы вы хотели заказать?"},
            {"role": "user", "content": f"{maybe_filler()}{random.choice(['Два стейка и салат Цезарь','Пасту карбонара и тирамису','Борщ и пельмени на двоих'])}"},
            {"role": "assistant", "content": f"Записала! Заказ будет готов через сорок минут. Ждём вас!"},
        ])
    elif "столик" in convs[-1]["content"]:
        name, g = rand_name()
        convs.extend([
            {"role": "assistant", "content": f"С удовольствием! На какую дату и сколько гостей?"},
            {"role": "user", "content": f"{random.choice(DATES[:6])}, на {random.choice(GUEST_COUNTS_FORMAL[:3])}. На имя {name}."},
            {"role": "assistant", "content": f"Отлично, {name}! Столик забронирован. Ждём вас!"},
        ])
    else:
        convs.append({"role": "assistant", "content": f"Понимаю! Если передумаете и решите посетить нас — звоните, будем рады. Всего доброго!"})
    return convs

def scenario_dress_code():
    """Client asking about dress code."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Мы хотим прийти к вам на ужин, но не знаем — у вас есть дресс-код?{maybe_noise()} {random.choice(['Можно в джинсах?','Нужно ли в костюме?','Мужу обязательно в пиджаке?'])}"},
        {"role": "assistant", "content": f"Здравствуйте! {random.choice(['У нас нет строгого дресс-кода, но мы просим придерживаться стиля smart casual — опрятный, аккуратный вид.','Дресс-код у нас свободный, но мы просим гостей выглядеть аккуратно. Джинсы допускаются, шорты и шлёпанцы — нет.','В нашем основном зале дресс-код свободный, а для VIP-зала рекомендуем вечерний стиль.'])} Хотите забронировать столик?"},
        {"role": "user", "content": f"Ну отлично! {maybe_filler()}Тогда давайте на {random.choice(DATES[:8])}, {random.choice(TIMES_INFORMAL)}, на {random.choice(GUEST_COUNTS_FORMAL[:3])}"},
        {"role": "assistant", "content": f"Прекрасно! На чьё имя бронируем?"},
        {"role": "user", "content": f"{name}"},
        {"role": "assistant", "content": f"Готово, {name}! Столик забронирован. Ждём вас в приятном расположении духа! Хорошего дня."},
    ]
    return convs

def scenario_holiday_menu():
    """Holiday special menu booking (NY, 8 march, 23 feb, 14 feb)."""
    r = rand_restaurant()
    name, g = rand_name()
    holiday = random.choice([
        ("Новый год","тридцать первое декабря","новогоднее","от пяти тысяч"),
        ("Восьмое марта","восьмого марта","праздничное","от трёх тысяч пятисот"),
        ("Двадцать третье февраля","двадцать третьего февраля","специальное мужское","от трёх тысяч"),
        ("День святого Валентина","четырнадцатого февраля","романтическое","от четырёх тысяч"),
    ])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Хочу узнать, что у вас на {holiday[0]}? Есть специальное меню?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Да, {holiday[1]} у нас {holiday[2]} меню {holiday[3]} рублей на персону. {random.choice(['Включает приветственный бокал шампанского, пять перемен блюд и праздничный десерт.','В программе живая музыка, праздничные закуски и авторские блюда от шефа.','Специально составленное шеф-поваром меню с сезонными деликатесами.'])} Столики уже активно бронируют, рекомендую не откладывать!"},
        {"role": "user", "content": f"О, {filler()}, звучит здорово! На {random.choice(GUEST_COUNTS_FORMAL[:5])} можно?"},
        {"role": "assistant", "content": f"Конечно! На {holiday[1]}, правильно понимаю? На какое время?"},
        {"role": "user", "content": f"Да, {random.choice(TIMES_INFORMAL)}"},
        {"role": "assistant", "content": f"Отлично! На чьё имя бронируем?"},
        {"role": "user", "content": f"{name}. {maybe_filler()}А предоплата нужна?"},
        {"role": "assistant", "content": f"Да, для бронирования на {holiday[0]} мы просим предоплату {random.choice(['тридцать','пятьдесят'])} процентов. Оплатить можно переводом или в ресторане. Бронь зафиксирована, {name}! Подробности пришлём в сообщении. Хорошего дня!"},
    ]
    return convs

def scenario_kids_birthday():
    """Parent booking kids birthday with animators."""
    r = rand_restaurant()
    name, g = rand_name()
    age = random.choice(["пять","шесть","семь","восемь","девять","десять"])
    kids = random.choice(["восемь","десять","двенадцать","пятнадцать"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Хочу отпраздновать день рождения ребёнка у вас. Сыну {age} лет, будет {kids} детей и {random.choice(['пять','шесть','восемь'])} взрослых.{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Как замечательно! Мы с удовольствием организуем детский праздник. У нас есть {random.choice(['отдельный зал, который можно украсить','банкетный зал с детской зоной','уютный зал на втором этаже'])}. Нужны ли аниматоры или развлекательная программа?"},
        {"role": "user", "content": f"Да! {filler()}, {random.choice(['аниматоров бы, с пиратской тематикой','хотим аниматора в костюме супергероя','можно клоуна или фокусника'])}. И торт свой хотим привезти."},
        {"role": "assistant", "content": f"Прекрасно! Аниматоров мы можем организовать — стоимость от {random.choice(['пяти','семи','восьми'])} тысяч рублей за два часа. Свой торт — без проблем, нарезка и подача — {random.choice(['пятьсот','семьсот'])} рублей. Детское меню — {random.choice(['восемьсот','тысяча','тысяча двести'])} рублей на ребёнка, взрослое — от {random.choice(['полутора','двух'])} тысяч."},
        {"role": "user", "content": f"{maybe_filler()}Отлично! Давайте на {random.choice(DATES[:8])}, {random.choice(TIMES[:5][:3])}. {random.choice(['Можно украсить зал шариками?','И чтобы шарики были!','Ещё хотим фотозону'])}"},
        {"role": "assistant", "content": f"Конечно! Украшение шарами — {random.choice(['две','три'])} тысячи рублей. На чьё имя бронируем?"},
        {"role": "user", "content": f"{name}"},
        {"role": "assistant", "content": f"Записала, {name}! Детский праздник на {kids} детей оформлен. За три дня до мероприятия мы свяжемся для подтверждения всех деталей. С днём рождения вашего сына!"},
    ]
    return convs

def scenario_change_reservation():
    """Client wants to change reservation details."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте, это {name}. {maybe_filler()}У меня есть бронь на {random.choice(DATES[:6])}, но нужно кое-что поменять.{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте, {name}! Да, вижу вашу бронь. Что хотите изменить?"},
        {"role": "user", "content": f"{filler()}, {random.choice(['нас будет не четверо, а семеро — подтянулись друзья','можно перенести на час позже?','хотим поменять зал — лучше VIP','нужен стол побольше, добавилось трое гостей','можно вместо субботы на воскресенье?'])}"},
        {"role": "assistant", "content": f"Конечно, {name}! {random.choice(['Я перебронирую вас на стол побольше.','Перенесу бронь на час позже.','VIP-зал свободен, перевожу вашу бронь.','Увеличиваю количество гостей.','Переношу бронь на воскресенье.'])} Остальные детали остаются прежними?"},
        {"role": "user", "content": f"Да, всё остальное без изменений. Спасибо!"},
        {"role": "assistant", "content": f"Готово, {name}! Бронь обновлена. Ждём вас! Хорошего дня."},
    ]
    return convs

def scenario_indecisive():
    """Very indecisive client, admin helping choose."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте... {maybe_filler()}Я хочу забронировать столик, но не знаю... {random.choice(['какой зал выбрать','на какое время лучше','сколько нас будет','что у вас лучше — основной зал или VIP'])}...{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Ничего страшного, давайте разберёмся вместе. Расскажите, какой у вас повод?"},
        {"role": "user", "content": f"{filler()}, ну... {random.choice(['день рождения мужа, хочу чтоб красиво было','просто хотим с подругами посидеть','годовщина свадьбы','корпоратив маленький, человек десять','первое свидание, хочу произвести впечатление'])}"},
        {"role": "assistant", "content": f"Понимаю! Тогда я бы порекомендовал{'а' if random.random()<0.5 else ''} {random.choice(['наш каминный зал — там очень уютная атмосфера','VIP-зал — он более камерный и тихий','террасу — сейчас там прекрасно, свежий воздух','основной зал у окна — красивый вид и мягкий свет'])}. Сколько вас будет?"},
        {"role": "user", "content": f"{filler()}, {random.choice(['точно не знаю... может четверо, может шестеро','ну нас будет... сейчас... пять или шесть, не знаю точно','два или три, ещё подруга думает','человек десять, но может кто-то отвалится'])}"},
        {"role": "assistant", "content": f"Давайте забронируем с запасом — {random.choice(['на шестерых, если кто-то не придёт, ничего страшного','на десять, при необходимости уберём лишние приборы','на четверых, а если добавятся гости — подставим стул'])}. На какой день?"},
        {"role": "user", "content": f"{filler()}, {random.choice(DATES[:6])} наверное... {maybe_filler()}А какое время лучше?"},
        {"role": "assistant", "content": f"Для {random.choice(['романтического ужина','дружеских посиделок','праздничного вечера'])} идеально подойдёт {random.choice(TIMES[:5])} — в это время ещё спокойно, а к позднему вечеру атмосфера становится более праздничной. На чьё имя?"},
        {"role": "user", "content": f"{name}... {filler()}, да, давайте так. Спасибо, что помогли определиться!"},
        {"role": "assistant", "content": f"С удовольствием, {name}! Всё записано. Если состав гостей изменится — просто позвоните. Ждём вас!"},
    ]
    return convs

def scenario_business_lunch():
    """Asking about business lunch."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день! {maybe_filler()}А у вас есть бизнес-ланч?{maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день! Да, бизнес-ланч у нас с {random.choice(['двенадцати до пятнадцати','одиннадцати тридцати до пятнадцати','двенадцати до шестнадцати'])} часов, {random.choice(['с понедельника по пятницу','каждый будний день'])}. Стоимость — {random.choice(['триста пятьдесят','четыреста','четыреста пятьдесят','пятьсот'])} рублей. Включает {random.choice(['салат, суп, горячее и напиток','три блюда на выбор и чай или кофе','закуску, первое, второе и десерт'])}."},
        {"role": "user", "content": f"О, хорошо! {maybe_filler()}А нужно бронировать или можно просто прийти?"},
        {"role": "assistant", "content": f"В будни обычно свободные места есть, но {random.choice(['в пятницу бывает многолюдно, лучше забронировать','если вас компания — лучше предупредить заранее','для гарантии рекомендую забронировать'])}. Хотите записаться?"},
        {"role": "user", "content": f"Да, {filler()}, давайте на завтра, нас {random.choice(['двое','трое','четверо'])}. {name}."},
        {"role": "assistant", "content": f"Отлично, {name}! Столик на бизнес-ланч забронирован. Ждём вас. Приятного аппетита заранее!"},
    ]
    return convs

def scenario_large_banquet():
    """Large banquet negotiation."""
    r = rand_restaurant()
    name, g = rand_name()
    count = random.choice(["тридцать","сорок","пятьдесят","шестьдесят","восемьдесят"])
    occasion = random.choice(["свадьба","юбилей","корпоратив","выпускной","день рождения"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте. {maybe_filler()}Мы планируем {occasion} на {count} человек. Какие у вас условия?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Мы с удовольствием проведём ваше мероприятие. Наш банкетный зал вмещает до {random.choice(['шестидесяти','восьмидесяти','ста'])} гостей. Банкетное меню — от {random.choice(['двух тысяч пятисот','трёх тысяч','трёх тысяч пятисот'])} рублей на персону. На какую дату планируете?"},
        {"role": "user", "content": f"{random.choice(DATES[5:])}. {maybe_filler()}А что входит в меню за {random.choice(['три','четыре','пять'])} тысячи?"},
        {"role": "assistant", "content": f"В это меню входят: {random.choice(['три вида закусок, нарезки, два горячих блюда, гарнир, десерт и фрукты','пять закусок, салат, два горячих, торт и фруктовая ваза','фуршетная линейка, горячее из мяса и рыбы, десертный стол'])}. Напитки оплачиваются отдельно или можно взять пакет «безлимитный бар» за {random.choice(['полторы','две'])} тысячи на персону."},
        {"role": "user", "content": f"{filler()}, а скидку дадите? Нас же много{maybe_noise()}"},
        {"role": "assistant", "content": f"При заказе банкета на {count} гостей мы можем предложить {random.choice(['скидку десять процентов на меню','бесплатную аренду зала','комплимент — торт от шеф-повара','бесплатное музыкальное сопровождение'])}. Это наше специальное предложение для больших мероприятий."},
        {"role": "user", "content": f"Хорошо, нас устраивает. На имя {name} бронируйте."},
        {"role": "assistant", "content": f"Записала, {name}! Для подтверждения бронирования потребуется предоплата {random.choice(['тридцать','двадцать'])} процентов. Наш менеджер по банкетам свяжется с вами для обсуждения деталей меню и оформления договора. Всего доброго!"},
    ]
    return convs

def scenario_simple_booking():
    """Simple straightforward booking."""
    r = rand_restaurant()
    name, g = rand_name()
    count = random.choice(GUEST_COUNTS_FORMAL[:6])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"{random.choice(['Здравствуйте','Добрый день','Привет','Алло'])}! {maybe_filler()}{random.choice([f'Столик на {count}',f'Хочу забронировать на {count}',f'Можно столик на {count}?',f'Нам бы столик на {count}'])}, {random.choice(DATES[:8])}{maybe_noise()}"},
        {"role": "assistant", "content": f"{'Здравствуйте' if random.random()<0.5 else 'Добрый день'}! Конечно. На какое время?"},
        {"role": "user", "content": f"{random.choice(TIMES_INFORMAL)}{maybe_noise()}"},
        {"role": "assistant", "content": f"Отлично! На чьё имя бронируем?"},
        {"role": "user", "content": f"{maybe_filler()}{name}"},
        {"role": "assistant", "content": f"Записала, {name}! Столик на {count} забронирован. Ждём вас!"},
        {"role": "user", "content": random.choice(["Спасибо!","Благодарю, до свидания","Спасибо, всего доброго","Ок, спасибо"])},
        {"role": "assistant", "content": random.choice(["Всего доброго! До встречи!","Хорошего дня! Ждём вас!","Благодарим за бронирование! До свидания!"])},
    ]
    return convs

def scenario_menu_questions():
    """Client asking lots of questions about menu."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день! {maybe_filler()}А расскажите, что у вас по кухне? {random.choice(['Какие фирменные блюда?','Что посоветуете?','А чё у вас по еде?','Какая у вас кухня?'])}{maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день! У нас {random.choice(['авторская европейская кухня','русская и итальянская кухня','средиземноморская кухня','паназиатская кухня'])}. Наши хиты — {random.choice(['стейк рибай на углях, паста с трюфелем и тартар из лосося','домашние пельмени, борщ по-купечески и утиная ножка конфи','ризотто с белыми грибами, том ям и ролл «Филадельфия»','каре ягнёнка, крем-суп из тыквы и чизкейк Нью-Йорк'])}. Средний чек — от {random.choice(['полутора','двух','двух с половиной'])} тысяч рублей на персону."},
        {"role": "user", "content": f"{filler()}, звучит вкусно! {random.choice(['А десерты какие?','А вино у вас хорошее?','А есть блюда для вегетарианцев?','А порции большие?'])}{maybe_noise()}"},
        {"role": "assistant", "content": f"{random.choice(['Десертная карта у нас великолепная — тирамису, наполеон, шоколадный фондан и сезонные десерты от шефа.','Винная карта насчитывает более ста позиций — итальянские, французские, чилийские вина. Сомелье поможет подобрать.','Да, у нас есть вегетарианское меню — салаты, овощные блюда, пасты и ризотто без мяса.','Порции у нас щедрые — гости никогда не уходят голодными!'])} Хотите забронировать столик и попробовать?"},
        {"role": "user", "content": f"Да, давайте! {random.choice(DATES[:6])}, на {random.choice(GUEST_COUNTS_FORMAL[:4])}, {random.choice(TIMES_INFORMAL)}"},
        {"role": "assistant", "content": f"Отлично! На чьё имя?"},
        {"role": "user", "content": f"{name}"},
        {"role": "assistant", "content": f"Записала, {name}! Ждём вас. Уверена, вам понравится!"},
    ]
    return convs

def scenario_parking():
    """Client asking about parking and location."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Хочу к вам приехать, а парковка у вас есть?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! {random.choice(['Да, у нас есть собственная парковка на двадцать мест — бесплатная для гостей.','Рядом с рестораном есть городская парковка, стоимость — сто рублей в час. Для наших гостей первый час бесплатно.','К сожалению, собственной парковки нет, но в ста метрах есть подземный паркинг торгового центра.','Да, парковка прямо у входа, бесплатная.'])} Хотите забронировать столик?"},
        {"role": "user", "content": f"Да, {maybe_filler()}на {random.choice(DATES[:6])}, {random.choice(TIMES_INFORMAL)}, на {random.choice(GUEST_COUNTS_FORMAL[:4])}. {name}."},
        {"role": "assistant", "content": f"Записала, {name}! Столик забронирован. {random.choice(['Адрес ресторана пришлю в СМС.','Мы находимся на улице Ленина, дом пять.','Легко найти — мы на центральной площади.'])} Ждём вас!"},
    ]
    return convs

def scenario_anniversary():
    """Wedding anniversary or special date."""
    r = rand_restaurant()
    name, g = rand_name()
    years = random.choice(["пять","десять","пятнадцать","двадцать","двадцать пять"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}У нас с {'мужем' if g=='f' else 'женой'} годовщина — {years} лет вместе. Хочу организовать романтический ужин.{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Поздравляю вас с такой прекрасной датой — {years} лет! Мы с удовольствием сделаем ваш вечер особенным. Могу предложить {random.choice(['столик в каминном зале при свечах','отдельную зону с живыми цветами и свечами','лучший столик у панорамного окна'])}. Хотите дополнить вечер чем-то особенным?"},
        {"role": "user", "content": f"{filler()}, да! {random.choice(['Может, цветы на столе и бутылку хорошего вина заранее подготовить?','Хочу чтобы был торт с надписью','Можно музыканта? Саксофон или скрипку?','Хотелось бы фотографа на полчаса'])}"},
        {"role": "assistant", "content": f"Конечно! Мы всё организуем. {random.choice(['Букет роз на столе — от двух тысяч рублей, бутылку вина подберёт наш сомелье.','Торт с индивидуальным дизайном — от трёх тысяч рублей, нужно заказать за два дня.','Скрипач — пять тысяч рублей за час выступления.','Фотограф — от четырёх тысяч за полчаса съёмки.'])} На какую дату и время?"},
        {"role": "user", "content": f"{random.choice(DATES[:8])}, {random.choice(TIMES[:5])}"},
        {"role": "assistant", "content": f"Прекрасно! На чьё имя бронируем?"},
        {"role": "user", "content": f"{name}"},
        {"role": "assistant", "content": f"Записала, {name}! Все детали согласуем за пару дней до визита. Желаю вам прекрасного вечера и ещё много счастливых лет вместе!"},
    ]
    return convs

def scenario_work_meeting():
    """Informal work meeting over lunch/dinner."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день! {maybe_filler()}Нужен столик на деловую встречу — чтобы было тихо и можно было поговорить. {random.choice(['На двоих','На троих','На четверых'])}.{maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день! Для деловой встречи отлично подойдёт {random.choice(['наш VIP-кабинет — там полная приватность','тихая зона в глубине зала — там спокойно','столик в лаунж-зоне — комфортные диваны и тишина'])}. На какое время?"},
        {"role": "user", "content": f"{random.choice(DATES[:6])}, {random.choice(['к двенадцати на обед','в час дня','в два часа','к семи вечера'])}"},
        {"role": "assistant", "content": f"Отлично! На чьё имя?"},
        {"role": "user", "content": f"{name}. {maybe_filler()}И чтобы не рядом с кухней, пожалуйста{maybe_noise()}"},
        {"role": "assistant", "content": f"Конечно, {name}! Подберём самый тихий столик. Бронь оформлена. Ждём вас!"},
    ]
    return convs

def scenario_callback_confirm():
    """Restaurant calling back to confirm reservation."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": f"Добрый день! Ресторан «{r}», администратор. {name}, звоню вам подтвердить бронирование на сегодня, {random.choice(TIMES[:5])}. Вы придёте?"},
        {"role": "user", "content": f"{maybe_filler()}{random.choice(['Да, да, мы придём!','Ой, а можно на полчаса позже?','Ааа, я забыл совсем... Нет, не получится','Да, только нас будет не четверо, а шестеро'])}"},
    ]
    if "не получится" in convs[-1]["content"] or "забыл" in convs[-1]["content"]:
        convs.extend([
            {"role": "assistant", "content": f"Понимаю, {name}. Отменяю бронь. Хотите перенести на другой день?"},
            {"role": "user", "content": f"{maybe_filler()}{random.choice(['Да, на следующую неделю','Нет, я потом перезвоню','Давайте на эту субботу'])}"},
            {"role": "assistant", "content": f"Хорошо! {'Записала, ждём вас!' if 'да' in convs[-1]['content'].lower() or 'давайте' in convs[-1]['content'].lower() else 'Будем ждать вашего звонка. Хорошего дня!'}"},
        ])
    elif "позже" in convs[-1]["content"]:
        convs.extend([
            {"role": "assistant", "content": f"Конечно, {name}! Перенесу бронь на полчаса позже. Ждём вас!"},
            {"role": "user", "content": "Спасибо!"},
            {"role": "assistant", "content": "Всего доброго, до встречи!"},
        ])
    else:
        convs.extend([
            {"role": "assistant", "content": f"Отлично! {'Увеличу количество мест, без проблем.' if 'шестеро' in convs[-1]['content'] else 'Замечательно!'} Ждём вас, {name}. Хорошего дня!"},
            {"role": "user", "content": "Спасибо, до вечера!"},
            {"role": "assistant", "content": "До встречи!"},
        ])
    return convs

def scenario_gluten_free():
    """Specific dietary request - gluten free."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Подскажите, у вас есть безглютеновые блюда? У меня целиакия, мне это важно.{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Да, в нашем меню есть блюда без глютена — они отмечены специальным значком. Также наш шеф-повар может адаптировать многие блюда. При бронировании мы сделаем пометку для кухни, чтобы исключить перекрёстное загрязнение."},
        {"role": "user", "content": f"Отлично, это важно! {maybe_filler()}Тогда столик на {random.choice(GUEST_COUNTS_FORMAL[:4])}, {random.choice(DATES[:6])}, {random.choice(TIMES_INFORMAL)}. {name}."},
        {"role": "assistant", "content": f"Записала, {name}! Пометка о безглютеновом питании сделана. Официант предупреждён. Ждём вас!"},
    ]
    return convs

def scenario_first_date():
    """First date - nervous client."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"{maybe_filler()}Здравствуйте... {filler()}, у меня первое свидание, и я хочу, чтобы всё было идеально. Подскажите, {random.choice(['какой столик лучше взять?','у вас романтическая атмосфера?','что посоветуете заказать?'])}"},
        {"role": "assistant", "content": f"Здравствуйте! Понимаю, как это волнительно. Не переживайте, мы создадим идеальную атмосферу! Рекомендую {random.choice(['столик у окна с видом на вечерний город — при свечах очень уютно','уголок в каминном зале — там приглушённый свет и тихая музыка','столик на террасе — сейчас там прекрасно'])}. На какую дату и время?"},
        {"role": "user", "content": f"{random.choice(DATES[:6])}, {random.choice(TIMES_INFORMAL)}. {maybe_filler()}На двоих, конечно."},
        {"role": "assistant", "content": f"Замечательно! А хотите, мы подготовим что-то особенное? {random.choice(['Можем поставить на стол свечу и цветок — это бесплатно.','Могу порекомендовать наше дегустационное меню — это всегда впечатляет.','Наш сомелье подберёт идеальное вино под вечер.'])}"},
        {"role": "user", "content": f"О, да! {filler()}, это было бы здорово. На имя {name}, пожалуйста."},
        {"role": "assistant", "content": f"Записала, {name}! Всё подготовим. Уверена, вечер пройдёт прекрасно. Удачи вам!"},
    ]
    return convs

def scenario_group_birthday():
    """Adult birthday with friends group."""
    r = rand_restaurant()
    name, g = rand_name()
    count = random.choice(["восемь","десять","двенадцать","пятнадцать","двадцать"])
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Алло! {maybe_filler()}Хочу отметить день рождения, нас будет {count} человек. {random.choice(['Что можете предложить?','Какие у вас банкетные варианты?','Можно на выходных?'])}[голоса на фоне]"},
        {"role": "assistant", "content": f"Здравствуйте! С удовольствием организуем праздник! На {count} гостей у нас есть {random.choice(['банкетный зал','отдельная зона в основном зале','VIP-зал'])}. Банкетное меню — от {random.choice(['двух тысяч пятисот','трёх тысяч'])} рублей на персону. На какую дату?"},
        {"role": "user", "content": f"{random.choice(DATES[:8])}, {random.choice(TIMES_INFORMAL)}. {maybe_filler()}{random.choice(['Можно свой торт?','Нужна музыка!','А караоке есть?'])}"},
        {"role": "assistant", "content": f"Конечно! {random.choice(['Свой торт можно, нарезка — пятьсот рублей.','Музыку подберём по вашим пожеланиям!','Караоке в VIP-зале — три тысячи рублей за вечер.'])} На чьё имя?"},
        {"role": "user", "content": f"{name}"},
        {"role": "assistant", "content": f"Отлично, {name}! Праздник оформлен. С днём рождения заранее! Ждём вас!"},
    ]
    return convs

def scenario_waiting_list():
    """No tables available, offering waiting list."""
    r = rand_restaurant()
    name, g = rand_name()
    wants_waitlist = random.random() < 0.6
    if wants_waitlist:
        user_reply = random.choice(['ладно, давайте в лист ожидания','нет, нам именно в эту дату надо... ну ладно, в лист запишите','ну запишите в лист тогда'])
        final_reply = f"Записала, {name}! Как только место освободится, я сразу с вами свяжусь. Хорошего дня!"
    else:
        user_reply = random.choice(['а воскресенье подойдёт, давайте','ладно, давайте на следующую неделю тогда','ну хорошо, перенесём'])
        final_reply = f"Записала, {name}! Столик забронирован. Ждём вас! Хорошего дня!"
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Можно столик на {random.choice(['эту субботу','завтра вечером','пятницу'])} на {random.choice(GUEST_COUNTS_FORMAL[:4])}?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! К сожалению, на эту дату все столики уже забронированы — {random.choice(['суббота у нас самый популярный день','пятница вечером всегда полная посадка','завтра у нас проходит банкет'])}. Могу предложить {random.choice(['воскресенье в то же время','ту же дату, но на более раннее время — к семнадцати часам','следующую неделю'])}. Или могу записать вас в лист ожидания — если кто-то отменит бронь, я сразу вам позвоню."},
        {"role": "user", "content": f"{filler()}, {user_reply}"},
        {"role": "assistant", "content": f"Хорошо! На чьё имя и номер телефона?"},
        {"role": "user", "content": f"{name}, {rand_phone()}"},
        {"role": "assistant", "content": final_reply},
    ]
    return convs

def scenario_vip_request():
    """VIP/celebrity-style special treatment request."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Добрый день. {maybe_filler()}Мне нужен отдельный кабинет на {random.choice(['двоих','четверых','шестерых'])}. Полная приватность. {random.choice(['Никаких посторонних','Чтобы нас никто не беспокоил','Отдельный вход есть?'])}. {maybe_noise()}"},
        {"role": "assistant", "content": f"Добрый день! Конечно, у нас есть {random.choice(['VIP-кабинет с отдельным входом и персональным официантом','приватная комната на втором этаже','кабинет с шумоизоляцией и отдельным обслуживанием'])}. Стоимость аренды — {random.choice(['пять','семь','десять'])} тысяч рублей, при заказе от {random.choice(['пяти','десяти'])} тысяч рублей — бесплатно. На какую дату?"},
        {"role": "user", "content": f"{random.choice(DATES[:6])}, {random.choice(TIMES[:5])}. На имя {name}."},
        {"role": "assistant", "content": f"Записала, {name}! Кабинет забронирован. Полная конфиденциальность гарантирована. Ждём вас!"},
    ]
    return convs

def scenario_wine_pairing():
    """Wine pairing dinner request."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Слышал{'а' if g=='f' else ''}, у вас бывают винные ужины. Когда ближайший?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Да, мы регулярно проводим винные ужины с дегустацией. Ближайший — {random.choice(DATES[2:8])}, тема — «{random.choice(['Вина Тосканы','Бургундский вечер','Испанские вина','Новый Свет — Чили и Аргентина'])}». Стоимость — {random.choice(['четыре','пять','шесть'])} тысяч рублей на персону, включая {random.choice(['пять','шесть','семь'])} бокалов вина и {random.choice(['четыре','пять'])} перемен блюд. Хотите записаться?"},
        {"role": "user", "content": f"Да, звучит отлично! На {random.choice(GUEST_COUNTS_FORMAL[:3])}. {name}.{maybe_noise()}"},
        {"role": "assistant", "content": f"Замечательно, {name}! Вы записаны на винный ужин. Предоплата — пятьдесят процентов. Подробности пришлём в сообщении. До встречи!"},
    ]
    return convs

def scenario_after_theater():
    """Booking after theater/concert."""
    r = rand_restaurant()
    name, g = rand_name()
    convs = [
        {"role": "system", "content": SYSTEM},
        {"role": "assistant", "content": greeting(r)},
        {"role": "user", "content": f"Здравствуйте! {maybe_filler()}Мы идём {random.choice(['в театр','на концерт','на спектакль','в оперу'])} {random.choice(DATES[:6])}, заканчивается около {random.choice(['двадцати одного часа','двадцати двух','половины десятого'])}. Можно забронировать столик после?{maybe_noise()}"},
        {"role": "assistant", "content": f"Здравствуйте! Конечно! Мы работаем до {random.choice(['полуночи','часа ночи','двадцати трёх часов'])}. Забронирую столик на {random.choice(['двадцать один тридцать','двадцать два часа','половину десятого'])}. На сколько гостей?"},
        {"role": "user", "content": f"На {random.choice(GUEST_COUNTS_FORMAL[:4])}. {name}."},
        {"role": "assistant", "content": f"Записала, {name}! Кухня работает до {random.choice(['двадцати двух тридцати','двадцати трёх','полуночи'])}. Успеете отлично поужинать. Приятного вечера и до встречи!"},
    ]
    return convs

# ============================================================
# Generate 500 dialogs
# ============================================================

scenario_funcs = [
    (scenario_regular_table, 20),
    (scenario_surprise_party, 18),
    (scenario_own_cake_wine, 18),
    (scenario_secretary_booking, 22),
    (scenario_tourist, 18),
    (scenario_late_cancellation, 20),
    (scenario_specific_table, 22),
    (scenario_noisy_group, 18),
    (scenario_romantic_proposal, 18),
    (scenario_complaint_rebook, 20),
    (scenario_live_music, 18),
    (scenario_allergies, 20),
    (scenario_corporate_event, 22),
    (scenario_wrong_restaurant, 18),
    (scenario_takeaway, 18),
    (scenario_dress_code, 18),
    (scenario_holiday_menu, 22),
    (scenario_kids_birthday, 20),
    (scenario_change_reservation, 22),
    (scenario_indecisive, 20),
    (scenario_business_lunch, 18),
    (scenario_large_banquet, 20),
    (scenario_simple_booking, 25),
    (scenario_menu_questions, 18),
    (scenario_parking, 15),
    (scenario_anniversary, 18),
    (scenario_work_meeting, 15),
    (scenario_callback_confirm, 15),
    (scenario_gluten_free, 12),
    (scenario_first_date, 15),
    (scenario_group_birthday, 15),
    (scenario_waiting_list, 12),
    (scenario_vip_request, 10),
    (scenario_wine_pairing, 10),
    (scenario_after_theater, 10),
]

total_planned = sum(c for _, c in scenario_funcs)
print(f"Planned: {total_planned} dialogs")

for func, count in scenario_funcs:
    for _ in range(count):
        dialogs.append(func())

random.shuffle(dialogs)
dialogs = dialogs[:500]

outpath = "/Users/mihaildurnev/Desktop/voice AI/voicebook/training/dataset/restaurant_dialogs_extra.jsonl"
with open(outpath, "w", encoding="utf-8") as f:
    for d in dialogs:
        f.write(json.dumps({"conversations": d}, ensure_ascii=False) + "\n")

print(f"Written {len(dialogs)} dialogs to {outpath}")

# Validate
with open(outpath, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        try:
            obj = json.loads(line)
            assert "conversations" in obj
            assert len(obj["conversations"]) >= 4
        except Exception as e:
            print(f"ERROR at line {i+1}: {e}")
            break
    else:
        print(f"All {len(lines)} lines valid JSONL!")

# Stats
turn_counts = []
for line in lines:
    obj = json.loads(line)
    turns = len([c for c in obj["conversations"] if c["role"] in ("user","assistant")])
    turn_counts.append(turns)
print(f"Turn stats: min={min(turn_counts)}, max={max(turn_counts)}, avg={sum(turn_counts)/len(turn_counts):.1f}")
