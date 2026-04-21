from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from texts import t
from keyboards import lang_keyboard, main_menu_keyboard, cancel_keyboard
from config import LAWYER_IDS, ADMIN_IDS

main_router = Router()


async def get_lang(user_id: int) -> str:
    user = await db.get_user(user_id)
    return user["language"] if user else "uz"


@main_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    lang = user["language"] if user else "uz"

    await db.upsert_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username or "",
        lang
    )

    await message.answer(
        t(lang, "welcome"),
        parse_mode="HTML",
        reply_markup=lang_keyboard()
    )


@main_router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await db.set_user_language(callback.from_user.id, lang)
    await callback.message.delete()
    await callback.message.answer(
        t(lang, "lang_set") + "\n\n" + t(lang, "main_menu"),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang)
    )
    await callback.answer()


@main_router.message(F.text.in_([
    "🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change language"
]))
async def change_language(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await message.answer(t(lang, "choose_lang"), reply_markup=lang_keyboard())


@main_router.message(F.text.in_([
    "🏠 Asosiy menyu", "🏠 Главное меню", "🏠 Main menu",
    "❌ Bekor qilish", "❌ Отмена", "❌ Cancel"
]))
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang), parse_mode="HTML")


@main_router.message(F.text.in_([
    "📚 Ko'p so'raladigan savollar", "📚 Часто задаваемые вопросы", "📚 FAQ"
]))
async def show_faq(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer(t(lang, "faq_text"), parse_mode="HTML")


@main_router.message(F.text.in_(["📞 Aloqa", "📞 Контакты", "📞 Contact"]))
async def show_contact(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer(t(lang, "contact_text"), parse_mode="HTML")


@main_router.message(F.text.in_([
    "📊 Mening murojaatlarim", "📊 Мои обращения", "📊 My requests"
]))
async def my_requests(message: Message):
    from keyboards import my_requests_keyboard
    lang = await get_lang(message.from_user.id)
    await message.answer(t(lang, "my_requests"), reply_markup=my_requests_keyboard(lang), parse_mode="HTML")


@main_router.callback_query(F.data.startswith("requests:"))
async def handle_requests(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    action = callback.data.split(":")[1]

    if action == "back":
        await callback.message.delete()
        await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))

    elif action == "questions":
        rows = await db.get_user_questions(callback.from_user.id)
        if not rows:
            await callback.answer(t(lang, "no_requests"), show_alert=True)
            return
        text = ""
        status_map = {
            "pending": t(lang, "status_pending"),
            "answered": t(lang, "status_answered"),
        }
        for row in rows:
            answer_block = ""
            if row["answer"]:
                answer_block = "\n" + t(lang, "answer_block", answer=row["answer"])
            text += t(lang, "question_item",
                      id=row["id"],
                      date=row["created_at"][:10],
                      question=row["question"][:120] + ("..." if len(row["question"]) > 120 else ""),
                      status=status_map.get(row["status"], row["status"]),
                      answer_block=answer_block) + "\n\n"
        await callback.message.edit_text(text.strip(), parse_mode="HTML")

    elif action == "applications":
        rows = await db.get_user_applications(callback.from_user.id)
        if not rows:
            await callback.answer(t(lang, "no_requests"), show_alert=True)
            return
        from config import APPLICATION_TYPES
        status_map = {
            "pending": t(lang, "status_pending"),
            "approved": t(lang, "status_approved"),
            "rejected": t(lang, "status_rejected"),
            "in_review": t(lang, "status_in_review"),
        }
        text = ""
        for row in rows:
            app_type_name = APPLICATION_TYPES.get(row["app_type"], {}).get(lang, row["app_type"])
            note_block = ""
            if row["lawyer_note"]:
                note_block = "\n" + t(lang, "note_block", note=row["lawyer_note"])
            text += t(lang, "application_item",
                      id=row["id"],
                      app_type=app_type_name,
                      date=row["created_at"][:10],
                      status=status_map.get(row["status"], row["status"]),
                      note_block=note_block) + "\n\n"
        await callback.message.edit_text(text.strip(), parse_mode="HTML")

    await callback.answer()
