import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))
LAWYER_IDS = list(map(int, os.getenv("LAWYER_IDS", "987654321").split(",")))
DATABASE_URL = os.getenv("DATABASE_URL", "tisu_legal.db")

UNIVERSITY_NAME = "TISU"
LEGAL_CLINIC_NAME = "TISU Yuridik Klinikasi"

LANGUAGES = {
    "uz": "🇺🇿 O'zbek tili",
    "ru": "🇷🇺 Rus tili",
    "en": "🇬🇧 Ingliz tili",
}

APPLICATION_TYPES = {
    "expel": {
        "uz": "📋 O'qishdan chetlash arizasi",
        "ru": "📋 Заявление об отчислении",
        "en": "📋 Expulsion Application",
    },
    "restore": {
        "uz": "🔄 Qayta tiklash arizasi",
        "ru": "🔄 Заявление о восстановлении",
        "en": "🔄 Reinstatement Application",
    },
    "transfer": {
        "uz": "🔀 O'qishni ko'chirish arizasi",
        "ru": "🔀 Заявление о переводе",
        "en": "🔀 Transfer Application",
    },
    "academic_leave": {
        "uz": "📅 Akademik ta'til arizasi",
        "ru": "📅 Заявление на академический отпуск",
        "en": "📅 Academic Leave Application",
    },
    "scholarship": {
        "uz": "💰 Stipendiya masalasi arizasi",
        "ru": "💰 Заявление по вопросу стипендии",
        "en": "💰 Scholarship Issue Application",
    },
    "retake": {
        "uz": "📝 Imtihon qayta topshirish arizasi",
        "ru": "📝 Заявление о пересдаче экзамена",
        "en": "📝 Exam Retake Application",
    },
}
