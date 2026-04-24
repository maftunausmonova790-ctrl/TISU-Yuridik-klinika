import asyncio
import logging
import os
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
#  SOZLAMALAR
# ═══════════════════════════════════════════════════════════════
BOT_TOKEN  = os.getenv("BOT_TOKEN", "")
ADMIN_IDS  = list(map(int, os.getenv("ADMIN_IDS", "0").split(",")))
DB_PATH    = "legal_bot.db"
BOT_NAME   = os.getenv("BOT_NAME", "Yuridik Maslahat Boti")

# Savol kategoriyalari
CATEGORIES = {
    "mehnat":   {"uz": "💼 Mehnat huquqi",      "ru": "💼 Трудовое право",      "en": "💼 Labour Law"},
    "oila":     {"uz": "👨‍👩‍👧 Oila huquqi",       "ru": "👨‍👩‍👧 Семейное право",      "en": "👨‍👩‍👧 Family Law"},
    "mulk":     {"uz": "🏠 Mulk huquqi",         "ru": "🏠 Имущественное право", "en": "🏠 Property Law"},
    "jinoiy":   {"uz": "⚖️ Jinoiy huquq",        "ru": "⚖️ Уголовное право",     "en": "⚖️ Criminal Law"},
    "mamurii":  {"uz": "🏛️ Ma'muriy huquq",      "ru": "🏛️ Административное",    "en": "🏛️ Administrative Law"},
    "tadbirkor":{"uz": "📈 Tadbirkorlik huquqi",  "ru": "📈 Предпринимательское", "en": "📈 Business Law"},
    "boshqa":   {"uz": "📌 Boshqa",              "ru": "📌 Другое",              "en": "📌 Other"},
}

# ═══════════════════════════════════════════════════════════════
#  MATNLAR (3 TIL)
# ═══════════════════════════════════════════════════════════════
T = {
"uz": {
"welcome": (
    "⚖️ <b>{name}</b>ga xush kelibsiz!\n\n"
    "Bu bot orqali siz:\n"
    "• O'zbek qonunlari asosida maslahat olishingiz\n"
    "• Nizom va qoidalar bilan tanishishingiz\n"
    "• Qonun moddalarini qidirishingiz mumkin\n\n"
    "🔒 Savollaringiz maxfiy saqlanadi\n\n"
    "Tilni tanlang 👇"
),
"main_menu": "📌 Asosiy menyu. Bo'limni tanlang:",
"ask_q": "❓ Savol berish", "search": "🔍 Qonun qidirish",
"nizom": "📋 Nizomlar", "faq_btn": "📚 Tez-tez so'raladigan",
"stats_btn": "📊 Statistika", "lang_btn": "🌐 Til",
"anon_on": "🔒 Anonimlik: Yoqilgan", "anon_off": "🔓 Anonimlik: O'chirilgan",
"home": "🏠 Asosiy menyu", "cancel": "❌ Bekor qilish",
"back": "⬅️ Orqaga", "confirm": "✅ Yuborish", "edit": "✏️ O'zgartirish",
"choose_cat": "📂 Savol kategoriyasini tanlang:",
"enter_q": (
    "✍️ Savolingizni yozing:\n\n"
    "<i>Qanchalik batafsil yozsangiz, javob shunchalik aniq bo'ladi.\n"
    "Masalan: vaziyatingizni, sanani, tomonlarni ko'rsating.</i>"
),
"q_preview": "📋 <b>Savolingizni tekshiring:</b>\n\n🗂 Kategoriya: <b>{cat}</b>\n🔒 Anonimlik: <b>{anon}</b>\n\n❓ <b>Savol:</b>\n{q}",
"q_sent": (
    "✅ <b>Savolingiz yuborildi!</b>\n\n"
    "📌 Raqam: <b>#{id}</b>\n"
    "⏳ Javob odatda 24 soat ichida keladi\n\n"
    "Javob kelganda sizga bildirishnoma yuboriladi 🔔"
),
"auto_reply": (
    "🤖 <b>Dastlabki ma'lumot:</b>\n\n"
    "{text}\n\n"
    "<i>⏳ Mutaxassis tez orada batafsil javob beradi.</i>"
),
"no_results": "🔍 Hech narsa topilmadi. Boshqa kalit so'z kiriting.",
"search_prompt": "🔍 Qonun yoki mavzu bo'yicha kalit so'z kiriting:\n<i>Masalan: mehnat ta'tili, nafaqa, ijara shartnomasi</i>",
"anon_toggled_on": "🔒 Anonimlik yoqildi. Savolingizda ismingiz ko'rinmaydi.",
"anon_toggled_off": "🔓 Anonimlik o'chirildi.",
"my_questions": "📊 Mening savollarim:",
"no_questions": "📭 Hali savol bermagansiz.",
"cancelled": "❌ Bekor qilindi.",
"lang_set": "✅ Til: O'zbek",
"pending": "⏳ Javob kutilmoqda", "answered": "✅ Javob berildi",
},

"ru": {
"welcome": (
    "⚖️ Добро пожаловать в <b>{name}</b>!\n\n"
    "Через этот бот вы можете:\n"
    "• Получить консультацию по законам Узбекистана\n"
    "• Ознакомиться с уставами и правилами\n"
    "• Искать нормы законов\n\n"
    "🔒 Ваши вопросы хранятся конфиденциально\n\n"
    "Выберите язык 👇"
),
"main_menu": "📌 Главное меню:",
"ask_q": "❓ Задать вопрос", "search": "🔍 Поиск закона",
"nizom_btn": "📋 Уставы", "faq_btn": "📚 Частые вопросы",
"stats_btn": "📊 Статистика", "lang_btn": "🌐 Язык",
"anon_on": "🔒 Анонимно: Вкл", "anon_off": "🔓 Анонимно: Выкл",
"home": "🏠 Главное меню", "cancel": "❌ Отмена",
"back": "⬅️ Назад", "confirm": "✅ Отправить", "edit": "✏️ Изменить",
"choose_cat": "📂 Выберите категорию вопроса:",
"enter_q": (
    "✍️ Напишите ваш вопрос:\n\n"
    "<i>Чем подробнее — тем точнее ответ.\n"
    "Укажите ситуацию, даты, стороны.</i>"
),
"q_preview": "📋 <b>Проверьте вопрос:</b>\n\n🗂 Категория: <b>{cat}</b>\n🔒 Анонимно: <b>{anon}</b>\n\n❓ <b>Вопрос:</b>\n{q}",
"q_sent": (
    "✅ <b>Вопрос отправлен!</b>\n\n"
    "📌 Номер: <b>#{id}</b>\n"
    "⏳ Ответ обычно приходит в течение 24 часов\n\n"
    "Вы получите уведомление 🔔"
),
"auto_reply": (
    "🤖 <b>Предварительная информация:</b>\n\n"
    "{text}\n\n"
    "<i>⏳ Специалист скоро даст подробный ответ.</i>"
),
"no_results": "🔍 Ничего не найдено. Попробуйте другое слово.",
"search_prompt": "🔍 Введите ключевое слово:\n<i>Например: трудовой отпуск, алименты, аренда</i>",
"anon_toggled_on": "🔒 Анонимность включена.",
"anon_toggled_off": "🔓 Анонимность отключена.",
"my_questions": "📊 Мои вопросы:",
"no_questions": "📭 Вы ещё не задавали вопросов.",
"cancelled": "❌ Отменено.",
"lang_set": "✅ Язык: Русский",
"pending": "⏳ Ожидает ответа", "answered": "✅ Отвечено",
},

"en": {
"welcome": (
    "⚖️ Welcome to <b>{name}</b>!\n\n"
    "Through this bot you can:\n"
    "• Get legal advice based on Uzbekistan laws\n"
    "• Read regulations and rules\n"
    "• Search legal norms\n\n"
    "🔒 Your questions are kept confidential\n\n"
    "Choose language 👇"
),
"main_menu": "📌 Main menu:",
"ask_q": "❓ Ask a question", "search": "🔍 Search law",
"nizom_btn": "📋 Regulations", "faq_btn": "📚 FAQ",
"stats_btn": "📊 Statistics", "lang_btn": "🌐 Language",
"anon_on": "🔒 Anonymous: On", "anon_off": "🔓 Anonymous: Off",
"home": "🏠 Main menu", "cancel": "❌ Cancel",
"back": "⬅️ Back", "confirm": "✅ Submit", "edit": "✏️ Edit",
"choose_cat": "📂 Choose question category:",
"enter_q": (
    "✍️ Write your question:\n\n"
    "<i>The more detailed — the more precise the answer.\n"
    "Include your situation, dates, parties involved.</i>"
),
"q_preview": "📋 <b>Review your question:</b>\n\n🗂 Category: <b>{cat}</b>\n🔒 Anonymous: <b>{anon}</b>\n\n❓ <b>Question:</b>\n{q}",
"q_sent": (
    "✅ <b>Question submitted!</b>\n\n"
    "📌 ID: <b>#{id}</b>\n"
    "⏳ Answer usually arrives within 24 hours\n\n"
    "You will receive a notification 🔔"
),
"auto_reply": (
    "🤖 <b>Preliminary information:</b>\n\n"
    "{text}\n\n"
    "<i>⏳ A specialist will provide a detailed answer soon.</i>"
),
"no_results": "🔍 Nothing found. Try another keyword.",
"search_prompt": "🔍 Enter keyword:\n<i>Example: annual leave, alimony, lease agreement</i>",
"anon_toggled_on": "🔒 Anonymity enabled.",
"anon_toggled_off": "🔓 Anonymity disabled.",
"my_questions": "📊 My questions:",
"no_questions": "📭 You haven't asked any questions yet.",
"cancelled": "❌ Cancelled.",
"lang_set": "✅ Language: English",
"pending": "⏳ Awaiting answer", "answered": "✅ Answered",
},
}

def tx(lang, key, **kw):
    s = T.get(lang, T["uz"]).get(key) or T["uz"].get(key, key)
    return s.format(**kw) if kw else s

# ═══════════════════════════════════════════════════════════════
#  QONUNLAR BAZASI — siz to'ldirasiz
# ═══════════════════════════════════════════════════════════════
LAWS_DB = {
    "mehnat": [
        {
            "title": "Mehnat kodeksi — Yillik ta'til",
            "article": "Mehnat kodeksi 134-modda",
            "text": "Har bir xodim yiliga kamida 15 ish kuni asosiy yillik ta'tilga haqli. Ba'zi toifalar uchun (o'qituvchilar, shifokorlar) ta'til 35 kungacha uzaytiriladi.",
            "keywords": ["ta'til", "yillik", "dam olish", "отпуск", "vacation", "leave"],
        },
        {
            "title": "Mehnat kodeksi — Ishdan bo'shatish",
            "article": "Mehnat kodeksi 100-modda",
            "text": "Xodimni asossiz ishdan bo'shatish taqiqlanadi. Ishdan bo'shatishdan 2 hafta oldin yozma ogohlantirish talab etiladi. Noqonuniy ishdan bo'shatish uchun xodim sudga murojaat qilishi mumkin.",
            "keywords": ["ishdan bo'shatish", "увольнение", "dismissal", "xodim", "ish"],
        },
        {
            "title": "Mehnat kodeksi — Ish haqi",
            "article": "Mehnat kodeksi 153-modda",
            "text": "Ish haqi oyiga kamida bir marta to'lanishi shart. Kechiktirilgan ish haqi uchun ish beruvchi penyа to'laydi. Eng kam ish haqi miqdori hukumat tomonidan belgilanadi.",
            "keywords": ["ish haqi", "maosh", "зарплата", "salary", "wage", "pul"],
        },
    ],
    "oila": [
        {
            "title": "Oila kodeksi — Nikoh yoshi",
            "article": "Oila kodeksi 14-modda",
            "text": "O'zbekistonda nikoh yoshi: erkaklar uchun 18 yosh, ayollar uchun 17 yosh. Nikoh ZAGS organlarida rasmiylashtirилади.",
            "keywords": ["nikoh", "turmush", "брак", "marriage", "yosh"],
        },
        {
            "title": "Oila kodeksi — Alimentlar",
            "article": "Oila kodeksi 98-modda",
            "text": "Bolalar uchun alimentlar: 1 bola uchun daromadning 1/4, 2 bola uchun 1/3, 3 va undan ko'p uchun 1/2 qismi undiriladi.",
            "keywords": ["aliment", "nafaqa", "bola", "алименты", "alimony", "child support"],
        },
    ],
    "mulk": [
        {
            "title": "Fuqarolik kodeksi — Ijara shartnomasi",
            "article": "Fuqarolik kodeksi 535-modda",
            "text": "Ijara shartnomasi yozma shaklda tuzilishi shart (1 yildan ortiq muddat uchun notarial tasdiq talab etiladi). Ijarachiнинг huquqlari: shartnoma tugaguncha mulkdan foydalanish.",
            "keywords": ["ijara", "arenda", "аренда", "lease", "rent", "shartnoma"],
        },
    ],
    "jinoiy": [
        {
            "title": "Jinoiy kodeks — O'g'irlik",
            "article": "Jinoiy kodeks 169-modda",
            "text": "O'g'irlik (yashirin o'g'irlik) 3 yilgacha ozodlikdan mahrum qilish yoki jarima bilan jazolanadi. Takroriy yoki guruh tomonidan amalga oshirilsa jazо kuchayadi.",
            "keywords": ["o'g'irlik", "kradeja", "кража", "theft", "jinoyat"],
        },
    ],
    "mamurii": [
        {
            "title": "Ma'muriy javobgarlik kodeksi — Jarimalar",
            "article": "Ma'muriy javobgarlik kodeksi 50-modda",
            "text": "Ma'muriy jarima eng kam ish haqining 0.1 baravaridan 50 baravarigacha belgilanishi mumkin. Jarima to'lash muddati 30 kun.",
            "keywords": ["jarima", "штраф", "fine", "penalty", "ma'muriy"],
        },
    ],
    "tadbirkor": [
        {
            "title": "Tadbirkorlik faoliyati to'g'risida Qonun",
            "article": "2000 yil 25 may, 69-II-son",
            "text": "Tadbirkorlik erkinligi kafolatlangan. Ruxsatnoma talab etilmagan faoliyat turlari ro'yxatdan o'tkazilgandan so'ng darhol boshlanishi mumkin. Soliq imtiyozlari birinchi 2 yil uchun amal qiladi.",
            "keywords": ["tadbirkor", "biznes", "бизнес", "business", "litsenziya", "ro'yxat"],
        },
    ],
}

# Nizomlar bazasi — siz o'zingiz qo'shasiz
NIZOMS_DB = [
    {
        "id": 1,
        "title": "Namuna nizom #1",
        "category": "Umumiy",
        "text": "Bu yerga muassasangiz nizomini qo'shing. /admin buyrug'i orqali yangi nizom qo'shishingiz mumkin.",
        "date": "2024-01-01",
    },
]

# Ko'p so'raladigan savollar
FAQ_DATA = {
    "uz": [
        ("💼 Ishdan asossiz bo'shatilsam nima qilaman?", "Mehnat kodeksi 100-moddasi bo'yicha sudga murojaat qiling. Sud qaroriga ko'ra qayta ishlashga tiklanish yoki kompensatsiya olish mumkin. Murojaat muddati: 3 oy."),
        ("👨‍👩‍👧 Ajrashgandan keyin bola kim bilan qoladi?", "Oila kodeksi bo'yicha sud bolaning manfaatini hisobga olib qaror qabul qiladi. Odatda ona bilan qoldirish amaliyoti ko'proq, ammo otaning huquqlari ham saqlanadi."),
        ("🏠 Ijarachim shartnomani buzsa nima qilaman?", "Fuqarolik kodeksi 556-moddasi bo'yicha yozma ogohlantirish yuboring. Bajarilmasa, sudga murojaat qilib shartnomani bekor qilish va zararni undirish mumkin."),
        ("📈 Yakka tartibli tadbirkorni qanday ro'yxatdan o'tkazaman?", "Soliq organiga murojaat qiling yoki my.gov.uz orqali onlayn ro'yxatdan o'ting. Hujjatlar: pasport, ariza. Ro'yxatga olish 1 ish kuni davom etadi."),
        ("⚖️ Jinoiy ish bo'yicha advokat tutish majburiymi?", "Majburiy emas, ammo tavsiya etiladi. Sudda o'zingiz himoyalanish huquqingiz bor. Davlat advokati bepul taqdim etiladi."),
    ],
    "ru": [
        ("💼 Что делать при незаконном увольнении?", "По статье 100 ТК обратитесь в суд. Возможно восстановление на работе или компенсация. Срок обращения — 3 месяца."),
        ("👨‍👩‍👧 С кем останется ребёнок после развода?", "Суд решает исходя из интересов ребёнка. Как правило, с матерью, но права отца сохраняются."),
        ("🏠 Арендатор нарушил договор — что делать?", "Направьте письменное предупреждение. Если не исполнит — обратитесь в суд для расторжения договора и взыскания убытков."),
        ("📈 Как зарегистрировать ИП?", "Обратитесь в налоговый орган или зарегистрируйтесь онлайн на my.gov.uz. Документы: паспорт, заявление. Срок — 1 рабочий день."),
        ("⚖️ Нужен ли адвокат по уголовному делу?", "Необязательно, но рекомендуется. Государственный защитник предоставляется бесплатно."),
    ],
    "en": [
        ("💼 What to do if illegally dismissed?", "Under Labour Code Art. 100, file a lawsuit. You may be reinstated or receive compensation. Filing deadline: 3 months."),
        ("👨‍👩‍👧 Who gets custody after divorce?", "Court decides based on the child's best interests. Usually with the mother, but father's rights are preserved."),
        ("🏠 Tenant violated the lease — what to do?", "Send written notice. If unresolved, go to court to terminate the contract and claim damages."),
        ("📈 How to register a sole proprietorship?", "Visit the tax office or register online at my.gov.uz. Documents: passport, application. Processing: 1 business day."),
        ("⚖️ Is a lawyer required for criminal cases?", "Not required, but recommended. A public defender is provided free of charge."),
    ],
}

# ═══════════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════════
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY, username TEXT,
            full_name TEXT, language TEXT DEFAULT 'uz',
            anonymous INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, category TEXT, question TEXT,
            answer TEXT, auto_answer TEXT, anonymous INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            answered_at TEXT, admin_id INTEGER)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS nizoms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, category TEXT, text TEXT,
            file_id TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        await db.commit()
    logger.info("✅ Baza tayyor")

async def get_user(uid):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        return await c.fetchone()

async def upsert_user(uid, uname, fname, lang="uz"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO users(user_id,username,full_name,language)
            VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username, full_name=excluded.full_name""",
            (uid, uname or "", fname or "", lang))
        await db.commit()

async def set_lang(uid, lang):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language=? WHERE user_id=?", (lang, uid))
        await db.commit()

async def toggle_anon(uid):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET anonymous = CASE WHEN anonymous=1 THEN 0 ELSE 1 END WHERE user_id=?", (uid,))
        await db.commit()
        db.row_factory = aiosqlite.Row
        c = await db.execute("SELECT anonymous FROM users WHERE user_id=?", (uid,))
        r = await c.fetchone()
        return r["anonymous"] if r else 0

async def get_lang(uid):
    u = await get_user(uid)
    return u["language"] if u else "uz"

async def get_anon(uid):
    u = await get_user(uid)
    return u["anonymous"] if u else 0

async def save_question(uid, category, question, anonymous, auto_answer=""):
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO questions(user_id,category,question,anonymous,auto_answer) VALUES(?,?,?,?,?)",
            (uid, category, question, anonymous, auto_answer))
        await db.commit()
        return c.lastrowid

async def get_pending_questions():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute("SELECT * FROM questions WHERE status='pending' ORDER BY created_at")
        return await c.fetchall()

async def get_user_questions(uid):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute(
            "SELECT * FROM questions WHERE user_id=? ORDER BY created_at DESC LIMIT 15", (uid,))
        return await c.fetchall()

async def answer_question(qid, answer, admin_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE questions SET answer=?,status='answered',answered_at=?,admin_id=? WHERE id=?",
            (answer, datetime.now().isoformat(), admin_id, qid))
        await db.commit()
        db.row_factory = aiosqlite.Row
        c = await db.execute("SELECT user_id,anonymous,category FROM questions WHERE id=?", (qid,))
        return await c.fetchone()

async def get_nizoms():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        c = await db.execute("SELECT * FROM nizoms ORDER BY created_at DESC")
        return await c.fetchall()

async def add_nizom(title, category, text, file_id=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO nizoms(title,category,text,file_id) VALUES(?,?,?,?)",
            (title, category, text, file_id))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        s = {}
        c = await db.execute("SELECT COUNT(*) FROM users"); s["users"] = (await c.fetchone())[0]
        c = await db.execute("SELECT COUNT(*) FROM questions"); s["total_q"] = (await c.fetchone())[0]
        c = await db.execute("SELECT COUNT(*) FROM questions WHERE status='pending'"); s["pend"] = (await c.fetchone())[0]
        c = await db.execute("SELECT COUNT(*) FROM questions WHERE status='answered'"); s["ans"] = (await c.fetchone())[0]
        c = await db.execute("SELECT category, COUNT(*) as cnt FROM questions GROUP BY category ORDER BY cnt DESC LIMIT 3")
        s["top_cats"] = await c.fetchall()
        return s

# ═══════════════════════════════════════════════════════════════
#  QONUN QIDIRISH
# ═══════════════════════════════════════════════════════════════
def search_laws(query: str, category: str = None) -> list:
    query_lower = query.lower()
    results = []
    cats = [category] if category else list(LAWS_DB.keys())
    for cat in cats:
        for law in LAWS_DB.get(cat, []):
            if any(kw in query_lower or query_lower in kw for kw in law["keywords"]):
                results.append((cat, law))
    return results[:5]

def auto_answer_for_question(question: str, category: str) -> str:
    results = search_laws(question, category)
    if not results:
        results = search_laws(question)
    if not results:
        return ""
    lines = []
    for cat, law in results[:2]:
        lines.append(f"📖 <b>{law['title']}</b>\n🔖 {law['article']}\n{law['text']}")
    return "\n\n".join(lines)

# ═══════════════════════════════════════════════════════════════
#  KLAVIATURALAR
# ═══════════════════════════════════════════════════════════════
def kb_lang():
    b = InlineKeyboardBuilder()
    b.button(text="🇺🇿 O'zbekcha", callback_data="lang:uz")
    b.button(text="🇷🇺 Русский", callback_data="lang:ru")
    b.button(text="🇬🇧 English", callback_data="lang:en")
    b.adjust(1); return b.as_markup()

def kb_main(lang, anon=0):
    b = ReplyKeyboardBuilder()
    b.button(text=tx(lang, "ask_q"))
    b.button(text=tx(lang, "search"))
    b.button(text=tx(lang, "nizom_btn") if lang != "uz" else "📋 Nizomlar")
    b.button(text=tx(lang, "faq_btn"))
    b.button(text="📊 Mening savollarim" if lang=="uz" else ("📊 Мои вопросы" if lang=="ru" else "📊 My questions"))
    b.button(text=tx(lang, "anon_on") if anon else tx(lang, "anon_off"))
    b.button(text=tx(lang, "lang_btn"))
    b.adjust(2, 2, 2, 1)
    return b.as_markup(resize_keyboard=True)

def kb_cancel(lang):
    b = ReplyKeyboardBuilder()
    b.button(text=tx(lang, "cancel")); b.button(text=tx(lang, "home"))
    b.adjust(2); return b.as_markup(resize_keyboard=True)

def kb_confirm(lang):
    b = InlineKeyboardBuilder()
    b.button(text=tx(lang, "confirm"), callback_data="q:send")
    b.button(text=tx(lang, "edit"), callback_data="q:edit")
    b.adjust(2); return b.as_markup()

def kb_categories(lang):
    b = InlineKeyboardBuilder()
    for key, names in CATEGORIES.items():
        b.button(text=names.get(lang, names["uz"]), callback_data=f"cat:{key}")
    b.button(text=tx(lang, "back"), callback_data="cat:back")
    b.adjust(2); return b.as_markup()

def kb_laws_results(results, lang):
    b = InlineKeyboardBuilder()
    for i, (cat, law) in enumerate(results):
        b.button(text=f"📖 {law['title'][:40]}", callback_data=f"law:{cat}:{i}")
    b.button(text=tx(lang, "back"), callback_data="law:back")
    b.adjust(1); return b.as_markup()

def kb_nizoms(nizoms, lang):
    b = InlineKeyboardBuilder()
    for n in nizoms:
        b.button(text=f"📋 {n['title'][:45]}", callback_data=f"niz:{n['id']}")
    b.button(text=tx(lang, "back"), callback_data="niz:back")
    b.adjust(1); return b.as_markup()

def kb_faq(lang):
    b = InlineKeyboardBuilder()
    for i, (q, _) in enumerate(FAQ_DATA.get(lang, FAQ_DATA["uz"])):
        b.button(text=q[:50], callback_data=f"faq:{i}")
    b.button(text=tx(lang, "back"), callback_data="faq:back")
    b.adjust(1); return b.as_markup()

def kb_admin_q(qid):
    b = InlineKeyboardBuilder()
    b.button(text="✍️ Javob yozish", callback_data=f"adm:ans:{qid}")
    b.button(text="🗑 O'tkazib yuborish", callback_data=f"adm:skip:{qid}")
    b.adjust(2); return b.as_markup()

def kb_admin_main():
    b = InlineKeyboardBuilder()
    b.button(text="❓ Kutilayotgan savollar", callback_data="adm:list")
    b.button(text="📋 Nizom qo'shish", callback_data="adm:addnizom")
    b.button(text="📊 Statistika", callback_data="adm:stats")
    b.button(text="📢 Xabar yuborish", callback_data="adm:broadcast")
    b.adjust(2, 2); return b.as_markup()

# ═══════════════════════════════════════════════════════════════
#  FSM
# ═══════════════════════════════════════════════════════════════
class AskQ(StatesGroup):
    category = State()
    question = State()
    confirm  = State()

class SearchS(StatesGroup):
    query = State()

class AdminS(StatesGroup):
    answering   = State()
    nizom_title = State()
    nizom_cat   = State()
    nizom_text  = State()
    broadcasting = State()

# ═══════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════
router = Router()
CANCEL_TEXTS = [
    "❌ Bekor qilish","❌ Отмена","❌ Cancel",
    "🏠 Asosiy menyu","🏠 Главное меню","🏠 Main menu"
]
MY_Q_TEXTS = ["📊 Mening savollarim","📊 Мои вопросы","📊 My questions"]

# ── START ──────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    u = await get_user(message.from_user.id)
    lang = u["language"] if u else "uz"
    await upsert_user(message.from_user.id, message.from_user.username,
                      message.from_user.full_name, lang)
    await message.answer(
        tx(lang, "welcome", name=BOT_NAME),
        parse_mode="HTML", reply_markup=kb_lang())

# ── TIL ───────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("lang:"))
async def cb_lang(cb: CallbackQuery):
    lang = cb.data.split(":")[1]
    await set_lang(cb.from_user.id, lang)
    anon = await get_anon(cb.from_user.id)
    await cb.message.delete()
    await cb.message.answer(
        tx(lang, "lang_set") + "\n\n" + tx(lang, "main_menu"),
        parse_mode="HTML", reply_markup=kb_main(lang, anon))
    await cb.answer()

@router.message(F.text.in_(["🌐 Til","🌐 Язык","🌐 Language"]))
async def change_lang(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await message.answer(tx(lang, "welcome", name=BOT_NAME),
                         parse_mode="HTML", reply_markup=kb_lang())

# ── CANCEL / HOME ─────────────────────────────────────────────
@router.message(F.text.in_(CANCEL_TEXTS))
async def go_home(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    anon = await get_anon(message.from_user.id)
    await message.answer(tx(lang, "main_menu"),
                         reply_markup=kb_main(lang, anon), parse_mode="HTML")

# ── ANONIMLIK ─────────────────────────────────────────────────
@router.message(F.text.contains("Anonimlik") | F.text.contains("Анонимно") | F.text.contains("Anonymous"))
async def toggle_anonymous(message: Message):
    anon = await toggle_anon(message.from_user.id)
    lang = await get_lang(message.from_user.id)
    text = tx(lang, "anon_toggled_on") if anon else tx(lang, "anon_toggled_off")
    await message.answer(text, reply_markup=kb_main(lang, anon))

# ── SAVOL BERISH ──────────────────────────────────────────────
@router.message(F.text.in_(["❓ Savol berish","❓ Задать вопрос","❓ Ask a question"]))
async def ask_start(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await state.set_state(AskQ.category)
    await message.answer(tx(lang, "choose_cat"),
                         parse_mode="HTML", reply_markup=kb_categories(lang))

@router.callback_query(AskQ.category, F.data.startswith("cat:"))
async def ask_cat(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    val = cb.data.split(":")[1]
    if val == "back":
        await state.clear(); await cb.message.delete()
        anon = await get_anon(cb.from_user.id)
        await cb.message.answer(tx(lang,"main_menu"),
                                reply_markup=kb_main(lang,anon)); await cb.answer(); return
    await state.update_data(category=val)
    await state.set_state(AskQ.question)
    await cb.message.delete()
    await cb.message.answer(tx(lang,"enter_q"),
                            parse_mode="HTML", reply_markup=kb_cancel(lang))
    await cb.answer()

@router.message(AskQ.question)
async def ask_question(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if len(message.text.strip()) < 10:
        await message.answer("⚠️ Savol juda qisqa. Iltimos, batafsil yozing."); return
    await state.update_data(question=message.text.strip())
    await state.set_state(AskQ.confirm)
    d = await state.get_data()
    anon = await get_anon(message.from_user.id)
    cat_name = CATEGORIES.get(d["category"], {}).get(lang, d["category"])
    anon_text = ("🔒 Ha" if lang=="uz" else ("🔒 Да" if lang=="ru" else "🔒 Yes")) if anon else \
                ("🔓 Yo'q" if lang=="uz" else ("🔓 Нет" if lang=="ru" else "🔓 No"))
    await message.answer(
        tx(lang, "q_preview", cat=cat_name, anon=anon_text, q=d["question"]),
        parse_mode="HTML", reply_markup=kb_confirm(lang))

@router.callback_query(AskQ.confirm, F.data.startswith("q:"))
async def ask_confirm(cb: CallbackQuery, state: FSMContext, bot: Bot):
    lang = await get_lang(cb.from_user.id)
    if cb.data == "q:edit":
        await state.set_state(AskQ.question)
        await cb.message.delete()
        await cb.message.answer(tx(lang,"enter_q"),
                                parse_mode="HTML", reply_markup=kb_cancel(lang))
        await cb.answer(); return

    d = await state.get_data(); await state.clear()
    anon = await get_anon(cb.from_user.id)

    # Avtomatik javob qidirish
    auto = auto_answer_for_question(d["question"], d["category"])
    qid = await save_question(cb.from_user.id, d["category"], d["question"], anon, auto)

    await cb.message.edit_text(tx(lang,"q_sent",id=qid), parse_mode="HTML")
    anon_val = await get_anon(cb.from_user.id)
    await cb.message.answer(tx(lang,"main_menu"),
                            reply_markup=kb_main(lang, anon_val))

    # Avtomatik javob yuborish
    if auto:
        await asyncio.sleep(2)
        await cb.message.answer(tx(lang,"auto_reply",text=auto), parse_mode="HTML")

    # Admin(lar)ga xabar
    u = await get_user(cb.from_user.id)
    cat_name = CATEGORIES.get(d["category"], {}).get("uz", d["category"])
    sender = "🔒 Anonim" if anon else f"👤 {u['full_name']} (@{u['username']})"
    notify = (
        f"🔔 <b>Yangi savol #{qid}</b>\n"
        f"🗂 {cat_name}\n"
        f"{sender}\n\n"
        f"❓ {d['question']}\n\n"
        f"Javob berish: /admin"
    )
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid, notify, parse_mode="HTML")
        except: pass
    await cb.answer()

# ── QONUN QIDIRISH ────────────────────────────────────────────
@router.message(F.text.in_(["🔍 Qonun qidirish","🔍 Поиск закона","🔍 Search law"]))
async def search_start(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await state.set_state(SearchS.query)
    await message.answer(tx(lang,"search_prompt"),
                         parse_mode="HTML", reply_markup=kb_cancel(lang))

@router.message(SearchS.query)
async def search_query(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.clear()
    results = search_laws(message.text.strip())
    if not results:
        await message.answer(tx(lang,"no_results"),
                             reply_markup=kb_main(lang, await get_anon(message.from_user.id)))
        return
    await message.answer(
        f"🔍 <b>{len(results)} ta natija topildi:</b>",
        parse_mode="HTML",
        reply_markup=kb_laws_results(results, lang))
    # Store results in state temporarily
    await state.update_data(search_results=[(c, json.dumps(l)) for c, l in results])

@router.callback_query(F.data.startswith("law:"))
async def show_law(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    parts = cb.data.split(":")
    if parts[1] == "back":
        await state.clear(); await cb.message.delete()
        anon = await get_anon(cb.from_user.id)
        await cb.message.answer(tx(lang,"main_menu"),
                                reply_markup=kb_main(lang,anon)); await cb.answer(); return
    cat, idx = parts[1], int(parts[2])
    laws = LAWS_DB.get(cat, [])
    if idx < len(laws):
        law = laws[idx]
        await cb.message.answer(
            f"📖 <b>{law['title']}</b>\n🔖 <i>{law['article']}</i>\n\n{law['text']}",
            parse_mode="HTML")
    await cb.answer()

# ── NIZOMLAR ──────────────────────────────────────────────────
@router.message(F.text.in_(["📋 Nizomlar","📋 Уставы","📋 Regulations"]))
async def show_nizoms(message: Message):
    lang = await get_lang(message.from_user.id)
    nizoms = await get_nizoms()
    if not nizoms:
        await message.answer("📭 Hozircha nizomlar yo'q."); return
    await message.answer("📋 <b>Nizomlar ro'yxati:</b>",
                         parse_mode="HTML", reply_markup=kb_nizoms(nizoms, lang))

@router.callback_query(F.data.startswith("niz:"))
async def show_nizom(cb: CallbackQuery):
    lang = await get_lang(cb.from_user.id)
    val = cb.data.split(":")[1]
    if val == "back":
        await cb.message.delete()
        anon = await get_anon(cb.from_user.id)
        await cb.message.answer(tx(lang,"main_menu"),
                                reply_markup=kb_main(lang,anon)); await cb.answer(); return
    nizoms = await get_nizoms()
    niz = next((n for n in nizoms if str(n["id"]) == val), None)
    if niz:
        text = f"📋 <b>{niz['title']}</b>\n🗂 {niz['category']}\n📅 {niz['date'] if 'date' in niz.keys() else ''}\n\n{niz['text']}"
        if niz["file_id"]:
            await cb.message.answer_document(niz["file_id"], caption=text, parse_mode="HTML")
        else:
            await cb.message.answer(text, parse_mode="HTML")
    await cb.answer()

# ── FAQ ───────────────────────────────────────────────────────
@router.message(F.text.in_(["📚 Tez-tez so'raladigan","📚 Частые вопросы","📚 FAQ"]))
async def show_faq(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer("📚 <b>Tez-tez so'raladigan savollar:</b>",
                         parse_mode="HTML", reply_markup=kb_faq(lang))

@router.callback_query(F.data.startswith("faq:"))
async def show_faq_answer(cb: CallbackQuery):
    lang = await get_lang(cb.from_user.id)
    val = cb.data.split(":")[1]
    if val == "back":
        await cb.message.delete(); await cb.answer(); return
    idx = int(val)
    faqs = FAQ_DATA.get(lang, FAQ_DATA["uz"])
    if idx < len(faqs):
        q, a = faqs[idx]
        await cb.message.answer(f"{q}\n\n{a}", parse_mode="HTML")
    await cb.answer()

# ── MENING SAVOLLARIM ─────────────────────────────────────────
@router.message(F.text.in_(MY_Q_TEXTS))
async def my_questions(message: Message):
    lang = await get_lang(message.from_user.id)
    rows = await get_user_questions(message.from_user.id)
    if not rows:
        await message.answer(tx(lang,"no_questions")); return
    st_map = {"pending": tx(lang,"pending"), "answered": tx(lang,"answered")}
    text = tx(lang,"my_questions") + "\n\n"
    for r in rows:
        cat = CATEGORIES.get(r["category"],{}).get(lang, r["category"])
        status = st_map.get(r["status"], r["status"])
        text += f"{'─'*25}\n📌 <b>#{r['id']}</b> {cat} | {status}\n❓ {r['question'][:80]}...\n"
        if r["answer"]:
            text += f"✅ <b>Javob:</b> {r['answer'][:120]}...\n"
    await message.answer(text, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════════
def is_admin(uid): return uid in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Ruxsat yo'q."); return
    s = await get_stats()
    await message.answer(
        f"⚖️ <b>Admin Panel</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{s['users']}</b>\n"
        f"❓ Jami savollar: <b>{s['total_q']}</b>\n"
        f"⏳ Javob kutilmoqda: <b>{s['pend']}</b>\n"
        f"✅ Javob berildi: <b>{s['ans']}</b>",
        parse_mode="HTML", reply_markup=kb_admin_main())

@router.callback_query(F.data == "adm:list")
async def adm_list(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔"); return
    rows = await get_pending_questions()
    if not rows:
        await cb.answer("✅ Kutilayotgan savol yo'q!", show_alert=True); return
    for r in rows:
        cat = CATEGORIES.get(r["category"],{}).get("uz", r["category"])
        anon_mark = "🔒 Anonim" if r["anonymous"] else f"ID: {r['user_id']}"
        auto_block = f"\n\n🤖 <i>Avto-javob yuborildi:</i>\n{r['auto_answer'][:200]}" if r["auto_answer"] else ""
        text = (
            f"❓ <b>Savol #{r['id']}</b>\n"
            f"🗂 {cat} | {anon_mark}\n"
            f"📅 {r['created_at'][:16]}\n\n"
            f"{r['question']}{auto_block}"
        )
        await cb.message.answer(text, parse_mode="HTML", reply_markup=kb_admin_q(r["id"]))
    await cb.answer()

@router.callback_query(F.data.startswith("adm:ans:"))
async def adm_ans_start(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id): await cb.answer("⛔"); return
    qid = int(cb.data.split(":")[2])
    await state.set_state(AdminS.answering)
    await state.update_data(qid=qid)
    await cb.message.answer(
        f"✍️ <b>#{qid}-savol uchun javob yozing:</b>\n\n"
        f"<i>Qonun moddalarini ham ko'rsating.</i>",
        parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data.startswith("adm:skip:"))
async def adm_skip(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔"); return
    await cb.message.edit_reply_markup()
    await cb.answer("O'tkazib yuborildi")

@router.message(AdminS.answering)
async def adm_save_answer(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id): return
    d = await state.get_data(); qid = d["qid"]; await state.clear()
    row = await answer_question(qid, message.text.strip(), message.from_user.id)
    await message.answer(f"✅ #{qid}-savol javob berildi va foydalanuvchiga yuborildi.")
    if row and not row["anonymous"]:
        uid = row["user_id"]
        cat = CATEGORIES.get(row["category"], {}).get("uz", "")
        try:
            await bot.send_message(
                uid,
                f"⚖️ <b>Savolingizga javob keldi!</b>\n\n"
                f"📌 Savol #{qid} | {cat}\n\n"
                f"✅ <b>Javob:</b>\n{message.text.strip()}",
                parse_mode="HTML")
        except: pass

# ── NIZOM QO'SHISH ────────────────────────────────────────────
@router.callback_query(F.data == "adm:addnizom")
async def adm_nizom_start(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id): await cb.answer("⛔"); return
    await state.set_state(AdminS.nizom_title)
    await cb.message.answer("📋 Nizom sarlavhasini yozing:")
    await cb.answer()

@router.message(AdminS.nizom_title)
async def adm_nizom_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminS.nizom_cat)
    await message.answer("🗂 Kategoriyasini yozing (masalan: Umumiy, Moliyaviy):")

@router.message(AdminS.nizom_cat)
async def adm_nizom_cat(message: Message, state: FSMContext):
    await state.update_data(cat=message.text.strip())
    await state.set_state(AdminS.nizom_text)
    await message.answer("📝 Nizom matnini yozing yoki hujjat yuboring:")

@router.message(AdminS.nizom_text)
async def adm_nizom_text(message: Message, state: FSMContext):
    d = await state.get_data(); await state.clear()
    file_id = ""
    text = message.text or message.caption or ""
    if message.document:
        file_id = message.document.file_id
    await add_nizom(d["title"], d["cat"], text, file_id)
    await message.answer(f"✅ Nizom qo'shildi: <b>{d['title']}</b>", parse_mode="HTML")

# ── STATISTIKA ────────────────────────────────────────────────
@router.callback_query(F.data == "adm:stats")
async def adm_stats(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔"); return
    s = await get_stats()
    top = ""
    for row in s["top_cats"]:
        cat_name = CATEGORIES.get(row[0],{}).get("uz", row[0])
        top += f"  • {cat_name}: {row[1]} ta\n"
    await cb.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{s['users']}</b>\n"
        f"❓ Jami savollar: <b>{s['total_q']}</b>\n"
        f"⏳ Kutilayotgan: <b>{s['pend']}</b>\n"
        f"✅ Javob berildi: <b>{s['ans']}</b>\n\n"
        f"🔝 <b>Top kategoriyalar:</b>\n{top}",
        parse_mode="HTML", reply_markup=kb_admin_main())
    await cb.answer()

# ── XABAR YUBORISH (BROADCAST) ────────────────────────────────
@router.callback_query(F.data == "adm:broadcast")
async def adm_broadcast_start(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id): await cb.answer("⛔"); return
    await state.set_state(AdminS.broadcasting)
    await cb.message.answer(
        "📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:")
    await cb.answer()

@router.message(AdminS.broadcasting)
async def adm_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id): return
    await state.clear()
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute("SELECT user_id FROM users")
        users = await c.fetchall()
    sent, failed = 0, 0
    for (uid,) in users:
        try:
            await bot.send_message(uid, f"📢 <b>E'lon:</b>\n\n{message.text}", parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)
        except: failed += 1
    await message.answer(f"✅ Yuborildi: {sent} | ❌ Yuborilmadi: {failed}")

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
async def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi! Railway Variables ga kiriting.")
        return
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await init_db()
    logger.info(f"✅ {BOT_NAME} ishga tushdi!")
    await dp.start_polling(bot, allowed_updates=["message","callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
