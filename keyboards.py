from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from texts import t


def lang_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbek tili", callback_data="lang:uz")
    builder.button(text="🇷🇺 Русский язык", callback_data="lang:ru")
    builder.button(text="🇬🇧 English", callback_data="lang:en")
    builder.adjust(1)
    return builder.as_markup()


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(lang, "ask_question"))
    builder.button(text=t(lang, "make_application"))
    builder.button(text=t(lang, "my_requests"))
    builder.button(text=t(lang, "faq"))
    builder.button(text=t(lang, "contact"))
    builder.button(text=t(lang, "change_lang"))
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)


def cancel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(lang, "cancel"))
    builder.button(text=t(lang, "main_menu_btn"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def cancel_skip_keyboard(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(lang, "skip"))
    builder.button(text=t(lang, "cancel"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "confirm"), callback_data="confirm:yes")
    builder.button(text=t(lang, "edit"), callback_data="confirm:no")
    builder.adjust(2)
    return builder.as_markup()


def app_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    types = [
        ("expel", "app_type_expel"),
        ("restore", "app_type_restore"),
        ("transfer", "app_type_transfer"),
        ("academic_leave", "app_type_academic_leave"),
        ("scholarship", "app_type_scholarship"),
        ("retake", "app_type_retake"),
    ]
    for key, text_key in types:
        builder.button(text=t(lang, text_key), callback_data=f"apptype:{key}")
    builder.button(text=t(lang, "back"), callback_data="apptype:back")
    builder.adjust(1)
    return builder.as_markup()


def my_requests_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "my_questions"), callback_data="requests:questions")
    builder.button(text=t(lang, "my_applications"), callback_data="requests:applications")
    builder.button(text=t(lang, "back"), callback_data="requests:back")
    builder.adjust(1)
    return builder.as_markup()


def admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Kutilayotgan savollar", callback_data="admin:questions")
    builder.button(text="📋 Kutilayotgan arizalar", callback_data="admin:applications")
    builder.button(text="📊 Statistika", callback_data="admin:stats")
    builder.adjust(1)
    return builder.as_markup()


def admin_question_keyboard(question_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Javob yozish", callback_data=f"aq:answer:{question_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin:questions")
    builder.adjust(1)
    return builder.as_markup()


def admin_application_keyboard(app_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"aa:approve:{app_id}")
    builder.button(text="❌ Rad etish", callback_data=f"aa:reject:{app_id}")
    builder.button(text="🔍 Ko'rib chiqilmoqda", callback_data=f"aa:review:{app_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin:applications")
    builder.adjust(2, 1, 1)
    return builder.as_markup()
