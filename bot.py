import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8425155912:AAEg3-V9hNc8nugIAvTyywxc4dfUSMxWLG4"
CHANNEL_USERNAME = "@kinonawe4er"

bot = Bot(token=TOKEN)
dp = Dispatcher()

movies = {
    "001": {
        "title": "Фокус",
        "year": 2015,
        "video": "BAACAgIAAxkBAAPlaW_6qPFWLJET2IHTPZaLXu5DCB0AAkSFAALeEYBLdwlXzpGento4BA",
        "description": "История об опытном мошеннике, который влюбляется в девушку, делающую первые шаги на поприще нелегального отъема средств у граждан. Отношения становятся для них проблемой, когда обнаруживается, что романтика мешает их нечестному бизнесу.",
        "country": "США, Аргентина",
        "director": "Джон Рекуа",
        "genres": ["комедия", "криминал"]  
    },
    "002": {
        "title": "Люси",
        "year": 2014,
        "video": "BAACAgIAAxkBAAPjaW_6HHpdWPA6t9-Xlabee8F06ksAAkOFAALeEYBLBOSrtXXhzqk4BA",
        "description": "Еще вчера она была просто сексапильной блондинкой, а сегодня — самое опасное и смертоносное создание на планете со сверхъестественными способностями и интеллектом. То, что совсем недавно лучшие умы мира считали фантастической теорией, для нее стало реальностью. И теперь из добычи она превратится в охотницу.",
        "country": "Франция, США",
        "director": "Люк Бессон",
        "genres": ["научнаяфантастика", "боевик"]    
    },
    "003": {
        "title": "Исходный код",
        "year": 2011,
        "video": "BAACAgIAAxkBAAIBDWlwtpqJ8ei-QcwTlLse5r90HKNkAALGigAC3hGASw6AQA-_raWiOAQ",
        "description": "Солдат по имени Коултер мистическим образом оказывается в теле неизвестного мужчины, погибшего в железнодорожной катастрофе. Коултер вынужден переживать чужую смерть снова и снова до тех пор, пока не поймет, кто зачинщик катастрофы.",
        "country": "США, Канада",
        "director": "Данкан Джонс",
        "genres": ["научнаяфантастика", "триллер"]    
    },
    "004": {
        "warning": "Сериал скоро будет загружен в бот.. ⏳ \n\n@kinonawe4er - все наши фильмы и сериалы"
    },
    "005": {
        "title": "Век Адалин",
        "year": 2015,
        "video": "BAACAgIAAxkBAAIBD2lwtwXZFw01zkO6Ids2UWEGKVC2AALKigAC3hGASxVemJK6ItTOOAQ",
        "description": "Главная героиня родилась вместе с XX веком и живет на свете уже сто лет, но при этом не стареет. Несмотря на свою долгую жизнь,Адалин так и не смогла найти любимого человека. Однако наконец-то она встречает мужчину, ради которого сможет снова стать смертной и состариться вместе с ним.",
        "country": "США, Канада",
        "director": "Ли Толанд Кригер",
        "genres": ["мелодрама", "драма"]    
    },
    "006": {
        "title": "Счастливого дня смерти",
        "year": 2017,
        "video": "BAACAgIAAxkBAAIBEWlwt2e0i4mVpW7P8NMm_gkYSqQzAALMigAC3hGASwh-MMx_tMqGOAQ",
        "description": "Каждый в универе мечтал попасть на её день рождения, но праздник был безнадежно испорчен незнакомцем в маске, убившим виновницу торжества. Однако судьба преподнесла имениннице леденящий душу подарок — бесконечный запас жизней. И теперь у девушки появился шанс вычислить своего убийцу, ведь этот день будет повторяться снова и снова…",
        "country": "США",
        "director": "Режиссер: Кристофер Лэндон",
        "genres": ["ужасы", "детектив"]    
    },
    "007": {
        "warning": "Сериал скоро будет загружен в бот.. ⏳ \n\n@kinonawe4er - все наши фильмы и сериалы"
    },
    "008": {
        "title": "Экзамен",
        "year": 2009,
        "video": "BAACAgIAAxkBAAIBF2lwuUJufdOBy45v6czalZP3SnY7AALhigAC3hGAS5xmXrpn7-FQOAQ",
        "description": "На пути к заветной должности они уже преодолели массу испытаний, но им осталось пройти последний экзамен. Он проводится в изолированной комнате под присмотром камер и молчаливого вооружённого охранника. Суровый «Наблюдатель» оглашает задание: чтобы получить «работу мечты», нужно за отведённые 80 минут ответить «на один единственный вопрос»",
        "country": "Великобритания",
        "director": "Стюарт Хэзелдайн",
        "genres": ["триллер"]    
    },
    "009": {
        "title": "Довод",
        "year": 2020,
        "video": "BAACAgIAAxkBAAIBFWlwuKVUdobM-SCARNvJGE6tEl05AALaigAC3hGAS6w_KUC_dANAOAQ",
        "description": "Главный герой — секретный агент, который проходит жестокий тест на надежность и присоединяется к невероятной миссии. От ее выполнения зависит судьба мира, а для успеха необходимо отбросить все прежние представления о пространстве и времени",
        "country": "США, Великобритания",
        "director": "Кристофер Нолан",
        "genres": ["боевик", "триллер", "научнаяфантастика"]    
    },
    "011": {
        "title": "Невиновная",
        "year": 2020,
        "video": "BAACAgIAAxkBAAIBE2lwt9c4RCbm9ctJkdxVfDYSiqD5AALUigAC3hGAS8PrdmkrDUpdOAQ",
        "description": "На поминках в Тэчхоне происходит массовое отравление со смертельным исходом, пострадал даже мэр. Главная подозреваемая — вдова покойного. Её дочь Чон-ин, преуспевающая сеульская адвокат, возвращается в родной город и берётся защищать мать, хотя та страдает деменцией и даже не узнаёт её. Многое в этом деле кажется подозрительным, расследование было проведено с нарушениями, и Чон-ин только укрепляется во мнении, что мать невиновна, а власти явно что-то скрывают.",
        "country": "Южная Корея",
        "director": "Пак Сан-хён",
        "genres": ["детектив", "драма"]    
    },
    "012": {
        "title": "Код да Винчи",
        "year": 2006,
        "video": "BAACAgIAAxkBAAIBGWlwujj4OfEb9qTGcMUHW3jUXE8FAALvigAC3hGAS3qYfsOTvW-EOAQ",
        "description": "Гарвардского профессора Роберта Лэнгдона подозревают в чудовищном преступлении, которого он не совершал. Лэнгдон знакомится с криптографом парижской полиции Софи Невё и вместе с ней пытается раскрыть тайну, которая может подорвать могущество католической церкви.",
        "country": "США, Франция",
        "director": "Рон Ховард",
        "genres": ["триллер", "детектив", "мистика"]    
    },
    "013": {
        "title": "Французская сюита",
        "year": 2014,
        "video": "BAACAgIAAxkBAAIBbWlwyExrXb7I47JyKruAjxEhFM4YAAK3iwAC3hGAS7JG39_evKQeOAQ",
        "description": "В центре романтической истории времён Второй мировой войны — молодая девушка, живущая вместе со свекровью в оккупированной фашистами Франции. Нелюбимый муж ушёл на поле боя, и героиня влюбляется в немецкого офицера. Их объединяет любовь к музыке: она играет на фортепиано, а немец — бывший композитор.",
        "country": "США, Франция, Бельгия",
        "director": "Сол Дибб",
        "genres": ["триллер", "драма", "мелодрама", "военный"]    
    },
    "014": {
        "title": "Тоннель в лето, выход прощаний",
        "year": 2022,
        "video": "BAACAgIAAxkBAAIBI2lwvn9FQlrEzkxH-EMffkFdzemrAAIoiwAC3hGAS16awpVDUAa6OAQ",
        "description": "Когда-то у школьника Каору Тоно была дружная и счастливая семья. Но после того, как его младшая сестра Карэн погибла, всё изменилось. Родители вскоре развелись, а отношения с ними у подростка разладились. \nОднажды юноша узнаёт легенду о тоннеле Урасима. Считается, что тот, кто преодолеет его, сможет исполнить любое желание, но платить придётся годами своей жизни. Каору решает проверить слухи и попытаться вернуть свою сестру. Неожиданно к нему решает присоединиться новая ученица школы Андзу Ханасиро, у которой тоже есть заветное желание.",
        "country": "Япония",
        "director": "CLAP",
        "genres": ["драма", "аниме"]    
    },
    "015": {
        "warning": "Сериал скоро будет загружен в бот.. ⏳ \n\n@kinonawe4er - все наши фильмы и сериалы"
    },
    "016": {
        "warning": "Сериал скоро будет загружен в бот.. ⏳ \n\n@kinonawe4er - все наши фильмы и сериалы"
    },
    "017": {
        "warning": "Сериал скоро будет загружен в бот.. ⏳ \n\n@kinonawe4er - все наши фильмы и сериалы"
    },
    "018": {
        "title": "Иллюзия полёта",
        "year": 2005,
        "video": "BAACAgIAAxkBAAIBIWlwvdxti8-hhuIg-Ygy-Lw7ljjmAAIiiwAC3hGAS5kckltA5NAmOAQ",
        "description": "У Кайл Пратт неожиданно бесследно пропадает 6-летняя дочь Джулия. Переживая эмоциональный стресс после кончины мужа, Кайл отчаянно пытается доказать свою вменяемость не верящим ей членам экипажа и пассажирам. Однако ситуация выглядит настолько абсурдной и фантастичной, что она уже сама начинает сомневаться в адекватности своего восприятия реальности. Ведь факты свидетельствуют о том, что Джулии вообще не было на борту самолета.",
        "country": "США",
        "director": "Роберт Швентке",
        "genres": ["триллер", "детектив", "драма"]    
    },
    "020": {
        "title": "Сводишь с ума",
        "year": 2025,
        "video": "BAACAgIAAxkBAAIBH2lwvZFC8eeMck1XZaSR7MnZh1ApAAIZiwAC3hGAS5D4o36AK7K9OAQ",
        "description": "на просмотр квартиры в старом фонде Петербурга являются сразу двое — SMM-менеджер Алиса и бармен Иван. Квартиру сдают только паре, поэтому Иван подыгрывает девушке, представляясь её мужем. Алиса делает так, что квартира достаётся ей, а Иван вынужден искать другое жильё.После этого в зеркале она видит параллельную реальность - в ней квартиру получил Иван.\nПытаясь разобраться, что происходит и ужиться в одном пространстве герои проходят весь путь от жуткой ненависти до любви",
        "country": "Россия",
        "director": "Дарья Лебедева",
        "genres": ["мелодрама", "драма", "фантастика"]    
    },
    "021": {
        "title": "Апгрейд",
        "year": 2018,
        "video": "BAACAgIAAxkBAAIBHWlwvTI3TqmeblCqGZt4Zvw2hnBVAAIRiwAC3hGAS0u9jVRF6MppOAQ",
        "description": "2046 год. Разнообразные технологии участвуют во всех аспектах человеческой жизни. Но в этом технологичном мире Грей — один из немногих людей, кто любит работать руками. Он восстанавливает и чинит старые автомобили. Однажды, возвращаясь от клиента, Грей с женой попадают в аварию, а после — в руки банды отморозков, в результате чего Грей оказывается парализованным ниже шеи. Тот самый богатый клиент предлагает несчастному поставить экспериментальный имплант Stem, который может полностью восстановить подвижность.",
        "country": "США, Австралия",
        "director": "Ли Уоннелл",
        "genres": ["научнаяфантастика", "боевик"]    
    },
    "022": {
        "title": "Три тысячи лет желаний",
        "year": 2022,
        "video": "BAACAgIAAxkBAAIBG2lwvMns4Mfp-c7eGJ79DpoByC3ZAAINiwAC3hGAS2351aqRpX30OAQ",
        "description": "Британская лингвистка Алетея прилетает из Лондона в Стамбул, чтобы прочитать курс лекций по нарративу. Уже в аэропорту женщина начинает видеть загадочных существ, а когда в одной из многочисленных сувенирных лавочек покупает стеклянную бутылочку и пытается её отмыть, перед ней возникает самый настоящий джинн. Алетея не торопится загадывать три желания, ей интереснее послушать его историю. Джинн начинает свой рассказ.",
        "country": "США, Австралия",
        "director": "Джордж Миллер",
        "genres": ["фантастика", "драма", "мелодрама"]    
    },
    "023": {
        "title": "Министерство неджентльменских дел",
        "year": 2024,
        "video": "BAACAgIAAxkBAAIBJWlwvxdCAStPaE7lNtYJ6B7RlAOYAAIziwAC3hGAS63wf7eMbpMhOAQ",
        "description": "1942 год, Великобритания. Они — лучшие из лучших. Отпетые авантюристы и первоклассные спецы, привыкшие действовать в одиночку. Но когда на кону стоит судьба всего мира, им приходится объединиться в сверхсекретное боевое подразделение и отправиться на выполнение дерзкой миссии против нацистов.",
        "country": "США, Турция, Великобритания",
        "director": "Гай Ричи",
        "genres": ["боевик", "история", "военный"]    
    },
    "024": {
        "title": "Иллюзия контроля",
        "year": 2022,
        "video": "BAACAgIAAxkBAAIBJ2lwwCBrzhgJ3W44J1xQmhApla3PAAI7iwAC3hGAS4eckd8aBDl_OAQ",
        "description": "С самого детства Виктор прекрасно манипулировал другими в собственных интересах. Со временем эта способность начинает позволять ему контролировать и направлять крупные финансовые потоки в интересах своих клиентов. Но однажды он обнаруживает, что всю свою жизнь, с самого детства, являлся марионеткой в чьей-то весьма тонко продуманной игре.",
        "country": "Великобритания, Украина",
        "director": "Владэк Занковски",
        "genres": ["триллер", "детектив", "драма"]    
    },
    "025": {
        "title": "Джентльмены",
        "year": 2019,
        "video": "BAACAgIAAxkBAAIBKWlwwLiCL45u_gZ4i1W07rxJohbuAAJGiwAC3hGAS3j8RE4RFyUvOAQ",
        "description": "Один ушлый американец ещё со студенческих лет приторговывал наркотиками, а теперь придумал схему нелегального обогащения с использованием поместий обедневшей английской аристократии и построил на этом бизнес-империю.",
        "country": "США, Великобритания",
        "director": "Гай Ричи",
        "genres": ["криминал", "комедия"]    
    },
    "026": {
        "title": "Престиж",
        "year": 2006,
        "video": "BAACAgIAAxkBAAIBL2lwwlfee5SVCbDWwotWN7jYrVSIAAJhiwAC3hGAS0pg70l5GP6XOAQ",
        "description": "Два известных фокусника, Роберт Энджер и Альфред Борден, когда-то были приятелями, но после несчастного случая, произошедшего прямо во время выступления, их сотрудничеству пришёл конец. Теперь они не просто конкуренты, а враги.\nЛучшим трюком того времени стало «перемещение человека». Энджер посылает к Бордену свою помощницу, поручив ей хитростью выманить секрет. А если этого будет мало — Энджер готов поступиться всем ради победы. ",
        "country": "США",
        "director": "Кристофер Нолан",
        "genres": ["триллер", "научнаяфантастика"]    
    },
    "027": {
        "title": "Волк с Уолл-стрит",
        "year": 2013,
        "video": "BAACAgIAAxkBAAIBK2lwwVknmnYHl0_Wj0jGRHuQVYcIAAJPiwAC3hGAS8WzI0SGI2NeOAQ",
        "description": "Захватывающая криминальная драма о жизни Джордана Белфорта, биржевого мошенника, который стремился к богатству и власти. Фильм исследует темы коррупции, алчности и разрушительного влияния финансов на общество.",
        "country": "США",
        "director": "Мартин Скорсезе",
        "genres": ["криминал", "биография", "комедия"]    
    },
    "028": {
        "title": "Загадочная история Бенджамина Баттона",
        "year": 2018,
        "video": "BAACAgIAAxkBAAIBLWlwwdrdu7206uhvaGLjWjrVWr8tAAJbiwAC3hGAS5imizCwapazOAQ",
        "description": "Фильм о мужчине, который родился в возрасте 80 лет, а затем… начал молодеть. Этот человек, как и каждый из нас, не мог остановить время. Его путь в ХХI век, берущий свое начало в Новом Орлеане в 1918 году в самом конце Первой Мировой войны, будет столь необычен, что вряд ли мог иметь место в жизни кого-либо другого.",
        "country": "США",
        "director": "Дэвид Финчер",
        "genres": ["драма", "фантастика", "мелодрама"]    
    },
    "031": {
        "title": "Аватар",
        "year": 2009,
        "video": "BAACAgIAAxkBAAIC8WlxReRiUWPRW-o-M1IXAAH2lluWeAACEIoAAt4RiEtpScX4-OB0SjgE",
        "description": "Бывший морпех Джейк Салли прикован к инвалидному креслу. Он получает задание совершить путешествие в несколько световых лет к базе землян на планете Пандора, где корпорации добывают редкий минерал, имеющий огромное значение для выхода Земли из энергетического кризиса.",
        "country": "США",
        "director": "Джеймс Кэмерон",
        "genres": ["научнаяфантастика", "боевик", "драма", "фантастика"]    
    },
    "032": {
        "title": "Аватар 2: Путь воды",
        "year": 2022,
        "video": "BAACAgIAAxkBAAIEWWlyB5S_NWYLPe_s_nI0jSTO3xzpAAKHigACk1iRSxDSHr4ka_HKOAQ",
        "description": "Джейк Салли становится предводителем народа на'ви и берет на себя миссию по защите новых друзей от корыстных бизнесменов с Земли. Теперь ему есть за кого бороться — с Джейком его прекрасная жена Нейтири. Когда на Пандору возвращаются до зубов вооруженные земляне, Джейк готов дать им отпор.",
        "country": "США",
        "director": "Джеймс Кэмерон",
        "genres": ["научнаяфантастика", "боевик", "драма", "фантастика"]    
    },
    "034": {
        "title": "Интерстеллар",
        "year": 2014,
        "video": "BAACAgIAAxkBAAIFb2lyWHEHKbUah6sHBFYmcIMFE-QTAALkTwACwM7ZSRFWLvtg09-gOAQ",
        "description": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области пространства-времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планету с подходящими для человечества условиями.",
        "country": "США",
        "director": "Кристофер Нолан",
        "genres": ["научнаяфантастика", "драма"]    
    },
    "039": {
        "title": "Остров проклятых",
        "year": 2009,
        "video": "BAACAgIAAxkBAAIGwmlyrlTkfd7zopp-7CWqrT6Ihj9oAAJzkQACk1iZSw_Tcgn-HCUMOAQ",
        "description": "Два американских судебных пристава отправляются на один из островов в штате Массачусетс, чтобы расследовать исчезновение пациентки клиники для умалишенных преступников. При проведении расследования им придется столкнуться с паутиной лжи, обрушившимся ураганом и смертельным бунтом обитателей клиники.",
        "country": "США, Канада",
        "director": "Мартин Скорсезе",
        "genres": ["триллер", "драма", "детектив"]    
    },
    "039": {
        "title": "Матрица",
        "year": 1999,
        "video": "BAACAgIAAxkBAAIGxmlyr_uCNRe_FeVJK-ImAUDGdPT8AAJ3kQACk1iZS7gZE92G771nOAQ",
        "description": "Жизнь Томаса Андерсона разделена на две части: днём он — самый обычный офисный работник, получающий нагоняи от начальства, а ночью превращается в хакера по имени Нео, и нет места в сети, куда он бы не смог проникнуть. Но однажды всё меняется. Томас узнаёт ужасающую правду о реальности.",
        "country": "США",
        "director": "Вачовски",
        "genres": ["научнаяфантастика", "боевик"]    
    },
    "041": {
        "title": "1 + 1",
        "year": 2011,
        "video": "BAACAgIAAxkBAAIFdWlyWhSp44ei_zZqmqadfbIjtlbiAAIXkwACk1iRS9MvrGmTdbGCOAQ",
        "description": "Пострадав в результате несчастного случая, богатый аристократ Филипп нанимает в помощники человека, который менее всего подходит для этой работы, – молодого жителя предместья Дрисса, только что освободившегося из тюрьмы. Несмотря на то, что Филипп прикован к инвалидному креслу, Дриссу удается привнести в размеренную жизнь аристократа дух приключений.",
        "country": "Франция",
        "director": "Оливье Накаш",
        "genres": ["комедия", "драма"]    
    },
    "044": {
        "title": "Время",
        "year": 2011,
        "video": "BAACAgIAAxkBAAIGvmlyrQvPXZM0YSUBSHA4AlNAGyCUAAJrkQACk1iZS4T9mpwYowABtjgE",
        "description": "Человечество перестало стареть после 25 лет, а время стало единственной валютой. Теперь богачи могут жить вечно, а простые люди, чтобы не умереть, вынуждены каждый день бороться за существование, продлевая жизненный цикл.\nРабочий из гетто Уилл Салас привык считать каждую секунду. Однажды он спасает от банды грабителей времени богатого Генри Хэмилтона и получает от него 116 лет жизни, но вскоре щедрый подарок оборачивается ловушкой.",
        "country": "США",
        "director": "Эндрю Никкол",
        "genres": ["боевик", "мелодрама", "фантастика"]    
    },
    "045": {
        "title": "Черный лебедь",
        "year": 2010,
        "video": "BAACAgIAAxkBAAIGxGlyr5TjSfFcesVc-kssb8qyWSBIAAJ2kQACk1iZS1QoDpxbNYsQOAQ",
        "description": "У примы балетного театра неожиданно появляется опасная конкурентка, способная отобрать у неё все партии. Соперничество усиливается по мере приближения ответственного выступления.",
        "country": "США",
        "director": "Даррен Аронофски",
        "genres": ["триллер", "драма", "ужасы"]    
    },
    "046": {
        "title": "Искупление",
        "year": 2007,
        "video": "BAACAgIAAxkBAAIGwGlyrcC9xRq6a28iy-iQ_0QNRVfHAAJxkQACk1iZS5PfvyzvhjCZOAQ",
        "description": "Действие фильма начинается в 1935 году и разворачивается на фоне Второй мировой войны. Талантливая тринадцатилетняя писательница Бриони Таллис бесповоротно меняет ход нескольких жизней, когда обвиняет любовника старшей сестры в преступлении.",
        "country": "Великобритания, США",
        "director": "Джо Райт",
        "genres": ["драма", "мелодрама", "детектив", "военный"]    
    },
}

series = {
    "010": {
        "title": "Изобретая Анну",
        "year": 2022,
        "description": "Анна Делви, также известная как Анна Сорокина, под видом наследницы богатой немецкой семьи проникает в высшее общество Нью-Йорка.",
        "poster": "AgACAgIAAxkBAAIFFmlyTYbeE_aciTdJTMKNxQjlzYhpAALlEmsbk1iRS7Xo4rDBJIlNAQADAgADeQADOAQ",
        "country": "США",
        "director": "Шонда Раймс",
        "genres": ["драма", "биография"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIFP2lyUgpeSIUksrlYTYIS-mUl6RTUAAIbkgACk1iRS72dqA69ayiAOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFQWlyUjkXqEJJjaBeYEs1FZDwE5N9AAIjkgACk1iRSyqASDWZkUEiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFQ2lyUl-MKlDrnRODTBJCUyk_mLIVAAIokgACk1iRS0yNnFjozF2AOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFRWlyUof4s6HGxhUkewJBiaCu8YuFAAItkgACk1iRS7QQ7B8eFnvKOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFR2lyUq8GEyb4w6TtIRpxrnysUjdVAAIzkgACk1iRS92J78PWmPxmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFSWlyUt9OBFXDGrMxl29Gs6jrMaXrAAI8kgACk1iRS6e7G7FHk9xZOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFS2lyUwQmBr5xTeXrH1k2PoRvuVKLAAJEkgACk1iRSwf07M6ZAZcyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFTWlyUzEyvghHQjiLf62OIwABaBugfwACTZIAApNYkUtceKwu6XnkIjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIFT2lyU2KqvM4CmTZ_RWoK3TIMBf6aAAJTkgACk1iRSwIQoTNZGfRIOAQ",
            },
        ]
    },
    "019": {
        "title": "11/22/63",
        "year": 2016,
        "description": "Учитель английского языка отправляется в прошлое, чтобы предотвратить убийство Кеннеди, но в результате сильно привязывается к той жизни, которая у него появилась в ушедшей эпохе.",
        "poster": "AgACAgIAAxkBAAIFGGlyTcwlgE7naqzzu676pm6fAUWkAALmEmsbk1iRSw5XXaQ15A__AQADAgADeQADOAQ",
        "country": "США",
        "director": "Кевин Макдональд",
        "genres": ["драма", "фантастика", "детектив"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIFWWlyU_qV_qpNnrve2RGgEN4OoZT3AAJmkgACk1iRSw7mkqzCLkzfOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFW2lyVHOJX5aL15_EtBJuFdpL1aWCAAJ9kgACk1iRS2vjZz2d2sLLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFXWlyVKkuM-AOVX5R0z_90JZCEyauAAKCkgACk1iRS2bu2-edoXrpOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFX2lyVPhgGLpcwAPi-YeSe84hVhjsAAKIkgACk1iRS8QZDT2ngFXjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFYWlyVV8BqbuKieLuZBv9PrdwTdeZAAKRkgACk1iRS4llYbmjdco7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFYWlyVV8BqbuKieLuZBv9PrdwTdeZAAKRkgACk1iRS4llYbmjdco7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFY2lyVY4xPYbS0_ExsGuVZkjjy_dJAAKZkgACk1iRS7fOOIzXiYIuOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFZWlyVbY_H0TmlNb0WIVnqXiLQt4jAAKekgACk1iRS4oFfSahMtEzOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFZ2lyVeapHUXQpOwkX3lNR-Ex9HNVAAKnkgACk1iRS8ZaYJ5MOKFQOAQ",
            },
        ]
    },
    "029": {
        "title": "Великолепный век",
        "year": 2011,
        "description": "Османская империя, XVI век. Девушка Александра попадает в плен к туркам и получает новое имя Хюррем. На её долю выпадает немало испытаний, а позже она становится первой официальной женой султана Сулеймана І.",
        "poster": "AgACAgIAAxkBAAIC9mlxSbmNoUJDub1c3a3lM18fNwWyAAJXDmsb3hGISwVmModBFR_XAQADAgADeQADOAQ",
        "country": "Турция",
        "director": "Дурул Тайлан и др.",
        "genres": ["драма", "мелодрама", "история"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIBfGlw5Lhjav0uOoZ59rVvU1Fb5_DvAAJPlgAC1HloSyT9FoCIwptWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBfmlw5u7RSP9IeQgu5uF2uUDf84CbAAKglgAC1HloSygJ-copBnsROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBgGlw5ww5QJWwoWo-mXfwjWE1EJU_AAKklgAC1HloS7AhME-0inwWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBgmlw5yNuCJoYPtdBrvilXyXlHWsCAAKllgAC1HloSxHuloCaOKGqOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBhGlw50oWupU-A_ZzeFjP6o2Gxmg7AAKmlgAC1HloS_TYk6uIOVenOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBhmlw52PWX5TXt8ayKTaD1E-hHlufAAKnlgAC1HloS5w33gp8Qlm9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBiGlw53NIeGBDh-S5xZQUejU_zlbUAAKplgAC1HloSyAuHscn9d43OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBimlw545TSCSrYiMaLoXm7lAcIGpgAAKslgAC1HloS4AYBSCdS-neOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBjGlw56ZZI_C1Ci1Ezh45S6vrHxWGAAKulgAC1HloS_h6mHMfqUSVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBjmlw58MIqYnY9kcNwu5z5xv0iOs0AAKxlgAC1HloSw0fTjU0dQcSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBkGlw59LIxTyW96N4kTRo_8uGjRhjAAL0lgAC1HloSw4_noMNvAIyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBkmlw59_ralL7VDNqJZLN0ipCa15wAAL3lgAC1HloS_E0pdj-1_skOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBlGlw5_MpyqUPetAgeq2AX8i2ROT1AAL4lgAC1HloS_XLkt4IYodwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBlmlw6AAB-huXtmo0-TID0-VYTE8XLAACApcAAtR5aEsxqo9Jqpwy7zgE",
            },
            {
                "video": "BAACAgIAAxkBAAIBmGlw6A59ix522hCqqGo__Acy8vSwAAL5lgAC1HloSzap2A_N-DQZOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBmmlw6BxS6cKknJVJo7hQrFnefAOrAAIGlwAC1HloSzEsS-hNOXMVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBnGlw6C57bDhDIH__vKgz7-xnEScbAAIHlwAC1HloSzj4U44YyGAHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBnmlw6GCaJLcBwvaiHcoWIxzmjV0lAAI1kwACxdNpSxNJ8aHiyFxmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBoGlw6IoAAW-KCSUKMhRafQpPAiiaDgACP5MAAsXTaUud0eWXxxiqiTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIBomlw6Jb2X7uPriUxxcVjhv5Ah1OdAAJOkQACxdNxSykHY-azQuFEOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBpGlw6KjuRTbbRanM2CmL4LKV8kJDAAKflAACxdNxS9MwZBVT3PHCOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBpmlw6LYhCYpqkzCH2RFj2ZmcyLRgAAKrlAACxdNxS6k2TDelSIXiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBqGlw6MXcFllFOVWGZ3N6-NB1I_sfAAJTlgACxdNxS8Mo3N2KKZtaOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBqmlw6NauLDb7hPq60uudPULQn6JlAAJ1lgACxdNxS8EYNTW5gt8EOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBrGlw6O56N34MgklcB1m8fZeZ6VW8AAIllwACxdNxS4N8GNim5-hYOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBsGlw6We-eJPxZHHAAtufPILG26GtAAIylwACxdNxSx_RF1dYFCtLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBsmlw6XSyKDlpHHAmYO4hq1S7WYLjAAJ5lwACxdNxS8systZS1KRROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBtGlw6YKHiVsjBY_akovseFz8JNM7AAL_jgACxdN5S8-1FwABZrq_uzgE",
            },
            {
                "video": "BAACAgIAAxkBAAIB9Glw9hC0_UyQih3OTix2ko3MbulpAAK5kwACONKIS858C-z8QQ5WOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB9mlw9jGj3lIt6J8k8P0hGOKVej1hAALakwACONKIS9ldjKr2qg1bOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB-Glw9j2Qu_KpfkX1I74Nsrqn2lzcAALokwACONKIS8N_bR1PinavOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB-2lw9lC_CbuyySIzd1Gi3jX4edjkAAL3kwACONKIS9zWvNduAdU_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB_Wlw9mWXtx1Gb-qt3S-EsTiQljMDAAITlAACONKIS4m9JpR6kjY0OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB_2lw9nI5qKpUvpIAARj65VFBi_ObaAACJ5QAAjjSiEskvT3WE56gUDgE",
            },
            {
                "video": "BAACAgIAAxkBAAICAWlw9oEg4-YJDqpVV3YQbVF-HohTAAIylAACONKIS7HYAnzPent7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICA2lw9ov3CPcW9JD58zkH2bNoQw5ZAAI-lAACONKIS2m4IrYvqRgWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICBWlw9p3WuYpLBOQRvSV80JgGjLAqAAJLlAACONKIS9FFE64VMRB8OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICB2lw9s2971OUiLJZe2In4QRWr1UwAAJWlAACONKIS7x3-A5BwMg7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICCWlw9voAAalrXPj7o0sglnZUHyWJQwAC0ZQAAjjSiEvmffpanBtUHjgE",
            },
            {
                "video": "BAACAgIAAxkBAAICC2lw9wfGFlGN7ENBdXKn3q-iX3JEAALelAACONKIS-yW8h349M1sOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICDWlw-CaLWp5Wvthn5FGnSm6y1A16AAI4mQACONKIS_3zpK27VC3UOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICD2lw-DiCUUK9aiFoVCnDrVBbfYlZAAJNmQACONKISzRR9dtoYFhZOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICEWlw-GL_ZGPpQUOHL9dVN4iWk01JAAKCmQACONKIS70M5msLYGSwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICJ2lw-jz43-spcujjKPFUhknyJR0OAAKbmQACONKIS1fGc7Xviv7-OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICKWlw-kq84D_LoA6FUNXWb_M2smRpAALKmQACONKISyGdbsf720lUOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIClWlxBh4Hc6v5G82AY3DhHXwbAl14AALkmQACONKISwYYoH5I_oWGOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICmGlxBmtbfDgHzEPmSN8wazV_peZ4AAL5mQACONKISzu1Rcq_-8u3OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICmmlxBnk1ij_ch9K92O7e4AtFFLZFAAIKmgACONKISx8UlmTCTh3YOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICnGlxBoe8g6pMfq-BMMV4FTQabQPQAAIamgACONKIS3WPRBaLgJAdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICnmlxBpVI391iekanEXL7a-ZEWVhdAAIvmgACONKIS719ywoIKsYbOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICoGlxBqAgceQ2LSuPtAzpLxFia9ZYAAJFmgACONKIS_Ifr6qgoKlgOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIComlxBqvvJqsCNxkEQ0vwx09hzXo0AAJymgACONKISz_-8qkJKQ7UOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICpGlxBrjTYxAwKwSxscvx9vhlRLrnAAKDmgACONKIS8fcqgG-D5AvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICpmlxBsORnyGqB88DW8pnQMKAdLfrAAKRmgACONKIS_9_jwdha1L5OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICqGlxBtccn1QKdnQAAe1gGeSevQAB0aQAArOaAAI40ohLSWgFowqLjPo4BA",
            },
            {
                "video": "BAACAgIAAxkBAAICqmlxBuVWxcLBpZFzPKbSfjOh0dpFAALgmgACONKIS0ytrnSv93cQOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICrGlxBvHuYchq4NQCh2utm6p_SvRbAAJ3kgACONKASzLkvykqReWiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC3GlxDdnlORplNEmg4FdLZK_JyP1kAAIvmwACONKIS4TchapaBxGjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC32lxED6S1WwapgifHSLclIjzwvOOAAJbmwACONKIS0LxOJ_go7R0OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC4WlxEE1XVraGQ5bQkasYczJQq7pNAAJzmwACONKISxPFVDvfnnFxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC42lxEFn4372dp8h7q0Sn5OVHXwndAAKEmwACONKIS5HswGIi4I_KOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC5WlxEGWSDjXfZkB4_h1MClP2EWmyAAKUmwACONKIS9Mvokr-XmYBOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC52lxEHrYHdUXpcdINUWXzh-uxNwqAAKnmwACONKIS8HqCrJs9J7WOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC6WlxEIxEigRoubR6P1r-tfznKJwLAAK8mwACONKIS-vOkJ10G0Z_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAID-GlyA4LTiLJeTmfQuxILbuA8QInGAALNmwACONKIS4e08Kb-Nwf1OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAID-mlyA5VHoCRnBAvYVN5ns9i68IgcAALmmwACONKISyWgBtKKVKDQOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAID_GlyA6FbcpTHfrZR6BIV7UVwvn5TAAL6mwACONKISxzvqtiLXUADOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAID_mlyA6wLPP73ydsVCObkfRXTwhZaAAILnAACONKIS9fe4_hT8i7jOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEAAFpcgO3hTF8uwZ3_ICMqN9Kr8jKJQACMZwAAjjSiEsyyNgnzJg6KzgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEAmlyA8IAAWR8ydCkTEqRe_rLw0Fv8gACS5wAAjjSiEsN0tsJp1pdMjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEBGlyA87MCExB81XjDVKABupaqEUDAAJ0nAACONKIS9t_zObO6NlbOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEBmlyA9gkmU_nmQgTdPwsjk0VHiL3AAKTnAACONKIS5WYq97PNpAjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIECGlyA-eZ0wcoElRdZnKnRRBH0FSbAAIangACONKISz-Kowt5ERJkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIECmlyA_U-qP5gDWItXmaMHHq6AAFvygACy58AAjjSiEthJxVIOYDmmzgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEDGlyBAJ3j7Vs5XuyonvWJDu8StgCAALQnwACONKISzHrGX0GivnwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEDmlyBBCmrUgi-w6TpD4a8aivBSFCAALpnwACONKISz-hIxLokeD_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEEGlyBB_LlQo6FGBefApTevL7XweOAAIQigACTp-RS1o1AXgWX6wfOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEEmlyBC5QIfWKyJIwjBF0CYxtbMAdAAIqigACTp-RS_SeLGfntiMtOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEFGlyBDpmVIjvF6YM00aLHvWgjnk2AALunwACONKIS2xHMJHI_oMnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEFmlyBEqTNltMzTCs1t9Jr4zwAAGhKwAC758AAjjSiEuZxcZHOR_PojgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEGGlyBFQDSmAAAdQzz3l6edZiyss1zgAC8Z8AAjjSiEtTR2XuRlFfkTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEGmlyBF-y3Uh2EuCVZqQpSLpv81mmAALynwACONKIS5V3cEFaTRLVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEHWlyBG4ehbYnzAtOKEsMCMqBqfSBAALznwACONKIS6s-W_8-l4thOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEH2lyBHmsWrroLCbyMAkYVZXgce2BAAJAigACTp-RSx4c_12PdW-9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEIWlyBIM9ol64T6WS7kJXF_Pb-QqMAAICigACTp-RSwwmJhtqURbrOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEI2lyBJCeOSIhJlzFmLoTy87pxdJ6AAJdigACTp-RS9y-vZex-QLYOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEJWlyBMfG5qbivsZgfwdkeYUTSJM4AAJligACTp-RS1MqUYhZw1IxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEJ2lyBNIZPNOHNL6sVsqMumUv6ii-AAJsigACTp-RS4y9jMqYTRZROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEKWlyBN4yY1k4L2GhCTMClpGhmkCKAAJ3igACTp-RSwtf9FpkPv3sOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEK2lyBOmzOx7KMPvX0d5v_bwZ7JkGAAJ_igACTp-RS39e06I8cdETOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIELWlyBPRuTU4Qq9FbYtkxz8Y-s1rfAAKHigACTp-RSznQAwWiWAhSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEL2lyBP7YDhiKV1-q7kwT-4mRbDSHAAKRigACTp-RSyVBB1mktixjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEMWlyBRLHgpohHRqBG9BQXlKsTD_3AAKeigACTp-RS_418qF8hM-qOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEM2lyBR3D0mh0sFU4IppvXkTk0psmAAKligACTp-RS-HGtANqQVd2OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIENWlyBSpVj2M8rr9AZSe7R4SZi0L0AAK7igACTp-RS1goMhdQVcw_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEN2lyBTS94LUES6yoLDDRSXm5o6N7AALHigACTp-RS3zt5bBo_r4KOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEOWlyBVIEeG_XLNMvVHTIQFor30KdAALPigACTp-RS4kISnxU5Xq1OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEO2lyBWC4nXz47yovgYAqiV7s8ANeAALVigACTp-RS38GiSrIudJJOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEPWlyBWonWPQdGKQGd6RXavIFtD7YAALeigACTp-RS2zjGbl0yCzqOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEP2lyBXNMmSt7MjL7icEuThytcogzAALjigACTp-RS95qhX15_oYPOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEQWlyBXxsBVrT8hk64P8brd6U1konAALuigACTp-RS5mzfCw6xLs6OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEQ2lyBYX5qJkY3-58nvIVp92CAq39AAICiwACTp-RS1aRnkNr_-HkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIERWlyBY8O8vXAaGN2v6-Ivtbn5K0lAAIYiwACTp-RSwrlh4_ewOWnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIER2lyBaTdlGPjuHjBkUFyutjekjxQAAIjiwACTp-RS1uTlkKuJMqmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIESWlyBa4Es3kDDhmd6Xy1Jz2zoIzhAAItiwACTp-RS1yWuMsNCFCjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIES2lyBblFLpq7_GFMaTW0BtRFGlkWAAJKiwACTp-RS0uTHRwZeqn_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIETWlyBcxvwfoOQXnxYrY0XN8gSOsvAAJTiwACTp-RS0_SvI_k8BeyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIET2lyBdb9apapM4AQ142k5lTisaYEAAJciwACTp-RSxNdrdI-dc1JOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEUWlyBeAqhknaN06DtvOEmt5wqh9IAAJriwACTp-RSxipibdFnP5tOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEU2lyBeoYPQp8hJfE02yGwSYKPcWMAAIzjAACTp-RS_rGovo5pcQEOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEVWlyBfURnbd9ztirD2ccIhtyWmJhAAJFjAACTp-RS0fNMDokg8rXOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEgGlyPzT_V5umGhERFvjTxayuQxdGAAJkjAACTp-RSypD81HmYYbWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEgmlyP0NfAafwX_kunydUqFIemqMDAAKRjAACTp-RS_IhwRWAdLDJOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEhGlyP0939lx6cogPLrFU-1bNdzZuAAKijAACTp-RS2CHvLKfMd47OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEhmlyP17AIPyWm6WEvgwuc9wnjf8cAAKbjQACTp-RS1raFejsDiVNOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEiWlyP2lz0gOvdBaTFf7EUthiEMdsAAKkjQACTp-RSw6Dhqvmhd83OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEi2lyP3VmJJHIvfthNTdFiP9XoLNLAAK3jQACTp-RS4ZLlYMiXOViOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEjWlyP4FDaTC3Xbd0ZrYEWUT3czRGAALTjQACTp-RS33FydLJPQpHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEj2lyP46sFV6N2uZZQmIi6EnE6Qm9AALfjQACTp-RS4cvugABJUTvKDgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEkWlyP5id9E2var26kC06Mjy9OpAyAAIFjgACTp-RS38nHBHHWEtLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEk2lyP6V49jG9aEVo6fd8wEbivvCEAAIcjgACTp-RS4goHeMdoqmIOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIElWlyP7LKj5EI5FcXitU1BfnLFT5xAAIyjgACTp-RS98lqVGlImFHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEl2lyP8D9dD8JL8WcDoRGk-jBi4P6AAJHjgACTp-RS463UEW8md67OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEmWlyP8w_t4Lqmy5OS5P5cct_HrXnAAJPjgACTp-RS9LSN83ohsMdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEm2lyP9gAARtYXARabryrUFTP-aV1LAACE5EAAk6fkUvswKnX0jXEhTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEnWlyP-UX4Aut_B5RCcmoG-DFmXAhAAJikAACTp-RSz-UIv8p9zbWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFGmlyTu6ZgVEEqRVgmvHK9SRo-CrLAAItkQACTp-RS96sF7My6_1bOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFHGlyTvyI9PBYMVAjatk5PaN24bDsAAJIkQACTp-RS3-5-625VVWWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFHmlyTwVNv5VOT2o1GuBJuCht6sA3AAJXkQACTp-RS6RZm5z3niyFOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFIGlyTxGgCMDkZ-Lnt8I4xSjBw-pnAAJlkQACTp-RS4wy_1gvB42nOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFImlyTxwNwWO0guLA9Mf9EfQH6ziwAAKlkQACTp-RS_azRWPRNFKhOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFJGlyTyakeo2ehNMDAag0h3aboPqRAALEkQACTp-RSw4Ju_u1-xahOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFJmlyTzvxmC_ArahbH-CeQyDzN9UoAALlkQACTp-RSyOBSiOnGVOxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFKGlyT0VGt6uvUOmhmhp6l1uGshg0AAIBkgACTp-RS0G4ic1y3JTHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFK2lyUB3EngVEBeXBHa6aJL6xo1P7AAIZkgACTp-RSwmaNhtAS94IOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFLWlyUEOfGcdg8JJzKXwF_EFE31PMAAIykgACTp-RS8SLNdD6x4vvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFL2lyUGWuwHcCp5SiwbSLQux78FA_AAJYkgACTp-RS0GAasbFNF1JOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFMWlyUHLrwpZ33yJZL7-NLIWWxAWmAAJ9kgACTp-RS0cO92vNgWACOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFUWlyU3Sy0sqMvQABWDYoIqKpB79-wgACpZIAAk6fkUsyUFukoxVlhDgE",
            },
            
        ]
    },
    "030": {
        "title": "Великолепный век: империя Кёсем",
        "year": 2015,
        "description": "Спин-офф культового телесериала «Великолепный век». Сериал повествует о жизни Кёсем-султан — одной из самых известных и могущественных представительниц Османской империи.",
        "poster": "AgACAgIAAxkBAAIC-WlxTAR60GoMKlhimBdX4ZDy70X0AAJvDmsb3hGIS2HvCMOEpTeSAQADAgADeQADOAQ",
        "country": "Турция",
        "director": "Дурул Тайлан и др.",
        "genres": ["драма", "мелодрама", "история"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAICE2lw-YhK9daN1o72jPxkG-tpuk1oAAJtlgAC1HloS4knn4OmythdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICFWlw-Z8c5ML4SaXhMJsUdg6SiO41AAJ0lgAC1HloS3IzYxypqlNHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICF2lw-bJeEmp6uJNhsI22vQfe-M3qAAJ6lgAC1HloSybBEVdzNrIdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICGWlw-b-FBNyQ0mtp8_vIum4LEyo_AAJ-lgAC1HloS-NrqHQ3__64OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICG2lw-coXcKqnfHRxHoQxbsfehxCuAAKIlgAC1HloS_RxG0dxmJsyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICHWlw-dYHa2y6lkmg0UJrJEVM3Ys7AAKJlgAC1HloS4twfPthUM_NOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICH2lw-e7yXQXGNV0ee3DILwiblSnMAAKUlgAC1HloS72meeyooNjDOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICIWlw-fv2lR30T-SvRk5usgeIfE12AAKXlgAC1HloS2BT_p0hd44EOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICI2lw-g7TrxYH-ZSEPriduG0mjyWfAAKZlgAC1HloS2MZ6UCgcIePOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICJWlw-hm_VsJdPNbZpV23Z7fEudZpAAKflgAC1HloS6fiy6_fOX8GOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFM2lyUIzVHPBfOjzWiUh8AwNFNCmmAAL4kQACmliQS9E3Wqe5RgrNOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFNWlyUJed-vYFYUiwkBDXgzasNz3tAAL_kQACmliQS2IAAQiEiCfTCjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIFN2lyULoE83lSE4PEP8ayx2Ny7-YhAAKhkgACmliQSymNMngrUC-LOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFOWlyUMTjsgGU4TPhi6UQ_k3ly3XdAALlkgACmliQS-pHvBIICVrvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFO2lyUNPoBi7iCMD-VPfgwrvV4XHXAALvkgACmliQS7Ku10bMbiQiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFPWlyUOhFTU7Qfjo5eiKF0unruD3hAAK7kgACmliQS0L1drHnuVb9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFU2lyU4t5Yexgzyp-E5JFwYpVsT7LAAIRkwACmliQSzo0tpWi9twFOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFVWlyU5127E9I6smdAykGowjgAQUTAAIakwACmliQSwS1AAGQCTLJ_TgE",
            },
            {
                "video": "BAACAgIAAxkBAAIFV2lyU6vE7Gg4Zk5NnSY811drXMbbAAJPkwACmliQS4Qwp8TFe6loOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFcWlyWS8ONDplLoUSOqv5bLvqTXQQAALzkgACTp-RSx9fB0evHghjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFc2lyWVDuqu3AxESFdwRyIKLNzHKfAAIkkwACTp-RS_ooLgZpfNmkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFd2lyWlI_HEqbjFSHp5GI5jqWB45fAAJCkwACTp-RS6NIku6_Hkh7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGOWlynQ0aGUAjQ_3HYwIx-RQhd9-fAAJ2lAACTp-RS-3VZK47dBMcOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGO2lynuISlPBdErDvgI4exsCuGzxbAAJ6lAACTp-RSyi3-8uXnqW8OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGPWlynvTlKBUXSGz3N5o12yOf8l3vAAKFlAACTp-RS5t19wM9qn4GOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGP2lynxtbMa69kFRHl2tvR_WpRlvoAAKhlAACTp-RS__isoG-LAjjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGQWlynyn_KEPZsu_AXNfMeQ53x_8dAAIllQACOr-RS4jypnCta1ctOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGQ2lynzbk7vrvOCUBYcCTqbRJW44_AAJAlQACOr-RS_Fn0JshOxK1OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGRWlyn0HbdV-Sk9p19GJsSg2Y4_9xAAIHhwACyu0pSI0d6OuGF-cOOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGR2lyn5-Fp6ExTDEpNpAsij0D6yyqAAJnlQACOr-RS69rNbBAA1M4OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGSWlyn6r6lEr6SKHy3i1LiE4LIyQBAAKJlQACOr-RS7ohmFb_MhnvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGS2lyn7e3uzTnWPQqk4-xiZeVhbjYAAKalQACOr-RS7m_EgFsKoUxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGTWlyn8PpQf2O076XJHy4TumveJTlAAK2lQACOr-RS7IHW-Sp8PiWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGT2lyn87VIPi_5gJHP3kD6UWOxCUKAAL6lQACOr-RSxqOYs4faQpVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGUWlyn9iWLYwtLLWbAkly8rHyYQPDAAISlgACOr-RS9ZHNpSkgC7bOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGU2lyn-MhrOmhw__zfP3H5TQ3VfHQAAIflgACOr-RS3lWdJZoxCAqOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGVWlyn-4zXt-QBHqLpSqbXA226Z4NAAK1hQACCIDYShObRUvJ-jgzOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGV2lyoBqUE68JA5zLt29oLBcwCigbAAIjlgACOr-RS4ZZVjCHfeRiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGWWlyoFMZ33SBbqablhc8kY6Ks-BgAAIolgACOr-RSyr835fG3HTtOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGW2lyoGB8bYgy6g1rEGFULRr84wiuAAItlgACOr-RS2Q4wOiePoovOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGXWlyoGqkuJn3SM51FZ9v_YGpnGuxAAIxlgACOr-RS7onbK-r6dPROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGX2lyoJndoXUukzRxjwNRN3emElrTAAJNlgACOr-RS-1KIuoEz-LnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGYWlyoKnKLk6mQ9Mj9chavLpq3A7nAAJelgACOr-RSzXVgLAq1bkuOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGY2lyoLMDHWxEnUkNg8GOEIvaPNy4AAJnlgACOr-RSz2430A7z988OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGZWlyoMp-FLAiqYnq2Fko_XEeAfrcAAJtlgACOr-RS9OY6-OQdOUvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGZ2lyoOQXMJoHUZNHosZXsE-fJuR3AAKElgACOr-RS2YZ5_b1Bt7kOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGaWlyoO7aE9vcA-v3AmAfRYFS3yQhAAKelgACOr-RS3YoRgN1EpkaOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGa2lyoPmpilNv1525US7GSxOm37v9AAKwlgACOr-RS5o2Mcx6GwwzOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGbWlyoQKvnkDcqMbnpewAAV9IhmEizAACv5YAAjq_kUtwWWh_RhQUQjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGb2lyoQ4xKtKFSUSRNZl4Ld_-sayGAALRlgACOr-RS-6qZe8KPNJSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGcWlyoR3mXZhpBDFPbT9C9PGgkKrzAALplgACOr-RS--_g8rtSFQQOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGc2lyoSjzXGAMRxzMkzyhZSGow5c8AALxlgACOr-RS2y1lb1-oHhCOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGdWlyoTPeYTvBbIlYAel_oyCa7JJXAAKolQACTp-RS5Y0j2qBzFa2OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGd2lyoT022uvZeEJ_j2sGM1iBm-QYAAKulQACTp-RS8OyVV2EXzXnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGeWlyoUj8tu3bzthUZdgFIeqS2Om0AAKxlQACTp-RSzIh1dW8IHNWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGe2lyoVLROa7Wjl39Fbgh7xjhryj-AAL7lgACOr-RS9joX2QStCgOOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGfWlyoVqUKHV3ktNok_1Qkb7QPZazAAIDlwACOr-RS-OPVjQuS-aLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGf2lyoWVy8cqGYKQlmZ3p9gtmvgF0AALAlQACTp-RS9b--GpWCdO3OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGgWlyoW4e8FlrmO3PtmIU-GnXg3DEAALtlQACTp-RS4nEcpipoSbaOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGg2lyoXgP4N5GlZLjC25C5OWxMmYCAAOWAAJOn5FL3ZWI2xVCmwQ4BA",
            },
            {
                "video": "BAACAgIAAxkBAAIGhWlyoZAP91DmCu0oFXmpgdniQyuYAAIQlgACTp-RS_eMzVbbxV_XOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGh2lyoazYfMAtkeIkQ35S2ewf_qa4AAIUlwACOr-RS-oLZAABFV5RyTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGiWlyocD0pZowXRyWGBNwS2DMhUVJAAIjlwACOr-RS0pfmSiEpw7eOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGi2lyocrRnlMf6wGuk5zK5zG6ZEF9AALSmgACEU9hSa5YBaZL7UUwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGjWlyoegP6j87LqrFWctUIQtOn8C7AAIrlwACOr-RS9Cn81H9_38zOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGj2lyofJf77nvUQm70e2u7t13Ttl0AAI0lgACTp-RS2vFUut4hqNVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGkWlyofyIvxzrnucppnJ0t8jO-pq1AAIilgACTp-RSzRGh8yWd4eNOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGk2lyogR2ZHDZL2_9yZcStBwEXdGjAAI2lwACOr-RS87_Pxh4wVU7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGlWlyogsTyLBjdnTIM3clMdL0ioMPAAI3lwACOr-RS8S0vJePZr8QOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGl2lyohL7uXr_1BmcZP0xSGrH_4iXAAI5lwACOr-RS8cO2GfasfhtOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGmWlyoiSO641TYSTlPSvUacTi_EcTAAIblgACTp-RS1496IUuZRw_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGm2lyojD1cjW1JeLYeY0_fdkHjMPlAAI-lgACTp-RS0ThbyJfAAH80DgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGnWlyolRAjbQkQe8ZmRkrEmufXo_EAAJOlgACTp-RSxnDcvvgvwGkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGn2lyomBEutPzBgsEaX4BCT8TBhs7AAJelgACTp-RS0dmgznnZBTTOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGoWlyomyiosZZe_E8OhhOQDOww2pYAAJglgACTp-RS7iY_z3ls1ITOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGo2lyonpEd0ls5D2bh2SbK8XG79AFAAI9lwACOr-RS3dSH5vS3gEmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGpWlyooOpiD65ENMxdfP9_aILoKPMAAJ7lgACTp-RS5LEorMEv5m1OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGp2lyooxwDjtEE2jUOn1tCiXhgRIjAAKElgACTp-RS-xwY76HQ_O9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGqWlyopUH5a3sQNCSNE5dvkdB51i3AAKilgACTp-RSzSJSrV73r52OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGq2lyop2o37UgthQiRrRj7rrBLMA-AAKolgACTp-RSxCxXPbzr6lGOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGrWlyoqUSuhV823lUiIAUgx4AAfp3BAACR5cAAjq_kUth36_xroqEJTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGr2lyoq6GEbcr3RkDbt1Cv0D1tw5RAALClgACTp-RS6TOIE5eUMEfOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGsWlyorbQHY8QfrPTu0yaergSA6zoAALNlgACTp-RS7rRre7vzwTjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGs2lyosE6jcBk0UixQlSNBOm-VwcRAALmlgACTp-RS6hQt4kyrWJnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGtWlyosxY59x_0obbaysQiOhExiaUAALslgACTp-RSzr3vPlsmpRFOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGt2lyotkPl0K4V1-fyVX9ZUUo0ceuAAI_lwACOr-RSxV4K0FJpqRSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGuWlyoubXZO_nMP_Sqs1pzB3UWdJEAALulgACTp-RS0P3iQZ9GRoSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGu2lyovBtPaQTGKswBpUnlXE4v9bsAALylgACTp-RS65EGkn9Pu28OAQ",
            },
        ]
    }
}

async def check_user_subscription(user_id: int):
    """Проверяет, подписан ли пользователь на канал"""
    try:
        member = await bot.get_chat_member("@kinonawe4er", user_id)
        return member.status not in ("left", "kicked")
    except:
        return False

def subscription_keyboard(item_type: str, code: str, episode_index: int = 0):
    """Кнопки подписки и проверки"""
    callback_data = f"check_sub:{item_type}:{code}"
    if item_type == "series":
        callback_data += f":{episode_index}"  # для серий указываем индекс

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Подписаться", url="https://t.me/kinonawe4er")],
        [InlineKeyboardButton(text="🔎 Проверить", callback_data=callback_data)]
    ])
    return keyboard

@dp.callback_query(lambda c: c.data.startswith("check_sub:"))
async def check_subscription_callback(callback: types.CallbackQuery):
    parts = callback.data.split(":")
    item_type = parts[1]
    code = parts[2]
    user_id = callback.from_user.id

    subscribed = await check_user_subscription(user_id)
    if not subscribed:
        await callback.answer("Вы все еще не подписаны на канал!", show_alert=True)
        return

    # Если подписан — показываем контент
    if item_type == "movie":
        movie = movies[code]
        hashtags = " ".join(f"#{g.replace(' ', '_')}" for g in movie.get('genres', []))
        await callback.message.answer_video(
            video=movie["video"],
            caption=(
                f"<b>⭐️ фильм «{movie['title']}», {movie['year']}</b>\n\n"
                f"<i>{movie.get('description', '')}</i>\n\n"
                f"<u>Жанр:</u> {hashtags}\n\n"
                f"<u>Страна:</u> {movie.get('country', '')}</u>\n"
                f"<u>Режиссер:</u> {movie.get('director', '')}</u>\n\n"
                f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
                f"Наш канал @kinonawe4er ✨"
            ),
            parse_mode="HTML"
        )

    elif item_type == "series":
        episode_index = int(parts[3])  # получаем серию
        await send_episode(callback, code, episode_index)

    await callback.answer()



def has_only_warning(item: dict) -> bool:
    return "warning" in item and len(item.keys()) == 1

def normalize(text: str) -> str:
    return text.lower().replace("ё", "е").replace(" ", "")

def search_movies(query: str):
    query = normalize(query.strip())
    results = []

    for code, movie in movies.items():
        title = normalize(movie.get("title", ""))
        if query in title:
            results.append(("movie", code, movie))

    return results

def search_series(query: str):
    query = normalize(query.strip())
    results = []

    for code, serial in series.items():
        title = normalize(serial.get("title", ""))
        if query in title:
            results.append(("series", code, serial))

    return results

def search_by_code(query: str):
    query = query.strip().lower()

    if query in movies:
        return [("movie", query, movies[query])]

    if query in series:
        return [("series", query, series[query])]

    return []

def search_by_title(query: str):
    query = normalize(query)
    results = []

    for code, movie in movies.items():
        if query in normalize(movie.get("title", "")):
            results.append(("movie", code, movie))

    for code, serial in series.items():
        if query in normalize(serial.get("title", "")):
            results.append(("series", code, serial))

    return results

def search_all(query: str):
    by_code = search_by_code(query)
    if by_code:
        return by_code

    return search_by_title(query)


def search_results_keyboard(results):
    keyboard = []

    for item_type, code, item in results:
        emoji = "🎬" if item_type == "movie" else "📺"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {item['title']}",
                callback_data=f"open:{item_type}:{code}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)




ITEMS_PER_PAGE = 6

# --- Получаем все жанры ---
def get_all_genres():
    genres = set()
    for movie in movies.values():
        genres.update(movie.get("genres", []))
    for serial in series.values():
        genres.update(serial.get("genres", []))
    return sorted(genres)


# --- Кнопки для жанров ---
def genres_keyboard():
    keyboard = []
    for genre in get_all_genres():
        keyboard.append([
            InlineKeyboardButton(
                text=genre.capitalize(),
                callback_data=f"genre:{genre}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- Фильтруем по жанру ---

def find_by_genre(genre: str):
    results = []

    for code, movie in movies.items():
        if genre in movie.get("genres", []):
            results.append(("movie", code, movie))

    for code, serial in series.items():
        if genre in serial.get("genres", []):
            results.append(("series", code, serial))

    return results

# --- Получаем страницу ---
def genre_page(genre: str, page: int):
    items = find_by_genre(genre)
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    return items[start:end], total_pages


# --- Кнопки фильмов/сериалов с пагинацией ---
def genre_keyboard(genre: str, page: int, total_pages: int, items):
    keyboard = []

    for item_type, code, item in items:
        emoji = "🎬" if item_type == "movie" else "📺"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {item['title']}",
                callback_data=f"open:{item_type}:{code}"
            )
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"genre_page:{genre}:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"genre_page:{genre}:{page+1}"))

    keyboard.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- Хендлер нажатия на жанр ---
@dp.callback_query(lambda c: c.data.startswith("genre:"))
async def genre_selected(callback: types.CallbackQuery):
    genre = callback.data.split(":")[1]
    items, total_pages = genre_page(genre, 0)

    if not items:
        await callback.message.answer(f"<b>❌ Ничего не найдено\n\n@kinonawe4er - все наши фильмы и сериалы</b>\n\n<b>/genres - сортировка по жанрам</b>",
        parse_mode="HTML")
        await callback.answer()
        return

    await callback.message.edit_text(
        f"<b>🎭 Жанр: {genre.capitalize()}</b>",
        reply_markup=genre_keyboard(genre, 0, total_pages, items),
        parse_mode="HTML"
    )
    await callback.answer()


# --- Хендлер переключения страниц жанра ---
@dp.callback_query(lambda c: c.data.startswith("genre_page:"))
async def genre_page_switch(callback: types.CallbackQuery):
    _, genre, page = callback.data.split(":")
    page = int(page)
    items, total_pages = genre_page(genre, page)

    await callback.message.edit_reply_markup(
        reply_markup=genre_keyboard(genre, page, total_pages, items)
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("open:"))
async def open_item(callback: types.CallbackQuery):
    _, item_type, code = callback.data.split(":")

    user_id = callback.from_user.id
    subscribed = await check_user_subscription(user_id)
    
    if not subscribed:
        # Если фильм
        if item_type == "movie":
            await callback.message.answer(
                "Для использования бота подпишитесь на канал @kinonawe4er",
                reply_markup=subscription_keyboard("movie", code)
            )
        else:  # сериал
            await callback.message.answer(
                "Для просмотра этой серии подпишитесь на канал @kinonawe4er",
                reply_markup=subscription_keyboard("series", code, 0)
            )
        await callback.answer()
        return

    # Если подписан — показываем контент
    if item_type == "movie":
        movie = movies[code]

        if has_only_warning(movie):
            await callback.message.answer(f"<b>{movie['warning']}</b>", parse_mode="HTML")
            await callback.answer()
            return

        hashtags = " ".join(f"#{g.replace(' ', '_')}" for g in movie.get('genres', []))
        await callback.message.answer_video(
            video=movie["video"],
            caption=(
                f"<b>⭐️ фильм «{movie['title']}», {movie['year']}</b>\n\n"
                f"<i>{movie.get('description', '')}</i>\n\n"
                f"<u>Жанр:</u> {hashtags}\n\n"
                f"<u>Страна:</u> {movie.get('country', '')}</u>\n"
                f"<u>Режиссер:</u> {movie.get('director', '')}</u>\n\n"
                f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
                f"Наш канал @kinonawe4er ✨"
            ),
            parse_mode="HTML"
        )
    else:
        await send_serial_card(callback.message, code)

    await callback.answer()





def serial_start_keyboard(code: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="📋 ВЫБРАТЬ СЕРИЮ",
                callback_data=f"menu:{code}:0"
            )
        ]]
    )

async def send_serial_card(message: types.Message, code: str):
    serial = series[code]
    hashtags = " ".join(f"#{g.replace(' ', '_')}" for g in serial.get("genres", []))
    text = (
        f"<b>⭐️ «{serial['title']}», {serial['year']}</b>\n\n"
        f"<i>{serial['description']}</i>\n\n"
        f"<u>Жанр:</u> {hashtags}\n\n"
        f"<u>Страна:</u> {serial['country']}\n"
        f"<u>Режиссер:</u> {serial['director']}\n\n"
    )

    await message.answer_photo(
        photo=serial["poster"],
        caption=text,
        parse_mode="HTML",
        reply_markup=serial_start_keyboard(code)
    )


def episode_keyboard(code: str, episode: int, total: int):
    row = []

    if episode > 0:
        row.append(
            InlineKeyboardButton(text="⬅️ пред", callback_data=f"prev:{code}:{episode}")
        )

    row.append(
        InlineKeyboardButton(text="ВЫБРАТЬ СЕРИЮ", callback_data=f"menu:{code}:0")
    )

    if episode < total - 1:
        row.append(
            InlineKeyboardButton(text="след ➡️", callback_data=f"next:{code}:{episode}")
        )

    return InlineKeyboardMarkup(inline_keyboard=[row])


def series_menu_keyboard(code: str, total: int, page: int = 0):
    per_page = 10
    start = page * per_page
    end = min(start + per_page, total)

    keyboard = []
    row = []

    for i in range(start, end):
        row.append(
            InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f"ep:{code}:{i}"
            )
        )
        if len(row) == 5:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"page:{code}:{page-1}")
        )

    if end < total:
        nav.append(
            InlineKeyboardButton(text="➡️", callback_data=f"page:{code}:{page+1}")
        )

    keyboard.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



async def send_episode(target, code: str, episode_index: int):
    user_id = target.from_user.id if isinstance(target, types.CallbackQuery) else target.chat.id

    # Проверка подписки
    member = await bot.get_chat_member("@kinonawe4er", user_id)
    if member.status == "left":  # не подписан
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📍 Подписаться", url="https://t.me/kinonawe4er")],
            [InlineKeyboardButton(text="🔎 Проверить", callback_data=f"check_sub:{code}:{episode_index}")]
        ])
        await target.message.answer(
            "Для просмотра этой серии подпишитесь на канал @kinonawe4er",
            reply_markup=keyboard
        )
        return

    # Если подписан — показываем видео
    serial = series[code]
    total = len(serial["episodes"])
    episode = serial["episodes"][episode_index]
    
    caption = (
        f"<b>⭐️ «{serial['title']}», {serial['year']}</b>\n\n"
        f"Серия {episode_index + 1} из {total}\n\n"
        f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
        f"Наш канал @kinonawe4er ✨"
    )

    keyboard = episode_keyboard(code, episode_index, total)

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_media(
            media=types.InputMediaVideo(
                media=episode["video"],
                caption=caption,
                parse_mode="HTML"
            ),
            reply_markup=keyboard
        )
    else:
        await target.answer_video(
            video=episode["video"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )


# Функция для поиска фильма по коду или названию
def find_movie(query: str):
    query = normalize(query.strip())

    # Сначала ищем по коду
    for code, movie in movies.items():
        if query == code.lower():
            return movie

    # Потом ищем по названию
    for movie in movies.values():
        title = normalize(movie.get("title", ""))
        if query in title:
            return movie

    return None

def find_series(query: str):
    query = normalize(query.strip())

    for code, serial in series.items():

        if query == str(code).lower():
            return code

        title = normalize(serial.get("title", ""))
        if query in title:
            return code

    return None

# # Основной хендлер сообщений

@dp.message()
async def handle_message(message: types.Message):
    query = message.text.strip().lower()  # приведение к нижнему регистру

    if query == "/start":
        await message.answer(
            "<b>Для просмотра введите название или код, которые указаны в канале https://t.me/kinonawe4er</b>\n\n"
            "<b>Например: «Фокус» или же его код «001»</b>\n\n"
            "<b>/genres - сортировка по жанрам</b>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return
    
    if query == "/genres":
        await message.answer(
            "<b>🎭 Выберите жанр:</b>",
            reply_markup=genres_keyboard(),
            parse_mode="HTML"
        )
        return
    
    results = search_all(message.text)
    if not results:
        await message.answer("❌ Ничего не найдено")
        return

    results = search_all(query)

    if not results:
        await message.answer(f"<b>❌ Ничего не найдено\n\n@kinonawe4er - все наши фильмы и сериалы</b>\n\n<b>/genres - сортировка по жанрам</b>",
        parse_mode="HTML")
        return

    # один результат — открываем сразу
    if len(results) == 1:
        item_type, code, _ = results[0]

        if item_type == "movie":
            movie = movies[code]

            if has_only_warning(movie):
                await message.answer(
                    f"<b>{movie['warning']}</b>",
                    parse_mode="HTML"
                )
                return

            hashtags = " ".join(f"#{g.replace(' ', '_')}" for g in movie.get("genres", []))

            await message.answer_video(
                video=movie["video"],
                caption=f"<b>⭐️ фильм «{movie['title']}», {movie['year']}</b>\n\n"
                        f"<i>{movie['description']}</i>\n\n"
                        f"<u>Жанр:</u> {hashtags}\n\n"
                        f"<u>Страна:</u> {movie['country']}\n"
                        f"<u>Режиссер:</u> {movie['director']}\n\n"
                        f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
                        f"Наш канал @kinonawe4er ✨",
                parse_mode="HTML"
            )
        else:
            await send_serial_card(message, code)

        return

    # несколько результатов — выбор
    await message.answer(
        "<b>🔍 Найдено несколько вариантов:</b>",
        reply_markup=search_results_keyboard(results),
        parse_mode="HTML"
    )
    



@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    data = callback.data.split(":")
    action = data[0]

    # открыть меню серий
    if action == "series_menu":
        _, code, page = data
        total = len(series[code]["episodes"])
        await callback.message.edit_reply_markup(
            reply_markup=series_menu_keyboard(code, total, int(page))
        )

    if action in ("prev", "next"):
        _, code, episode = data
        episode = int(episode)

        if action == "prev":
            episode -= 1
        else:
            episode += 1

        await send_episode(callback, code, episode)

        await callback.answer()
        return



    # перелистывание страниц
    elif action == "page":
        _, code, page = data
        total = len(series[code]["episodes"])
        await callback.message.edit_reply_markup(
            reply_markup=series_menu_keyboard(code, total, int(page))
        )

    # выбор серии → ВКЛЮЧАЕМ ВИДЕО
    elif action == "ep":
        _, code, episode = data
        await send_episode(callback, code, int(episode))

    # назад к карточке сериала
    elif action == "serial":
        _, code = data
        await callback.message.delete()
        await send_serial_card(callback.message, code)

    elif action == "menu":
        _, code, page = data
        total = len(series[code]["episodes"])

        await callback.message.edit_reply_markup(
            reply_markup=series_menu_keyboard(code, total, int(page))
    )

    await callback.answer()

# Загрузка видосов
@dp.message()
async def get_file_id(message: types.Message):
    if message.video:
        await message.answer(message.video.file_id)

# Загрузка фото
@dp.message()
async def get_photo_id(message: types.Message):
    if message.photo:
        await message.answer(message.photo[-1].file_id)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())