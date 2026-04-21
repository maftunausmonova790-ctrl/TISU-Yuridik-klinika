from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from texts import t
from keyboards import cancel_keyboard, confirm_keyboard, main_menu_keyboard
from config import LAWYER_IDS, ADMIN_IDS

questions_router = Router()


class QuestionForm(StatesGroup):
    full_name = State()
    student_id = State()
    faculty = State()
    question = State()
    confirm = State()


async def get_lang(user_id: int) -> str:
    user = await db.get_user(user_id)
    return user["language"] if user else "uz"


@questions_router.message(F.text.in_([
    "❓ Savol yuborish", "❓ Задать вопрос", "❓ Ask a question"
]))
async def start_question(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await state.set_state(QuestionForm.full_name)
    await message.answer(t(lang, "enter_fullname"), parse_mode="HTML", reply_markup=cancel_keyboard(lang))


@questions_router.message(QuestionForm.full_name)
async def q_get_fullname(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if len(message.text.strip()) < 5:
        await message.answer("⚠️ Iltimos, to'liq ismingizni kiriting.")
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(QuestionForm.student_id)
    await message.answer(t(lang, "enter_student_id"), parse_mode="HTML")


@questions_router.message(QuestionForm.student_id)
async def q_get_student_id(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.update_data(student_id=message.text.strip())
    await state.set_state(QuestionForm.faculty)
    await message.answer(t(lang, "enter_faculty"), parse_mode="HTML")


@questions_router.message(QuestionForm.faculty)
async def q_get_faculty(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.update_data(faculty=message.text.strip())
    await state.set_state(QuestionForm.question)
    await message.answer(t(lang, "enter_question"), parse_mode="HTML")


@questions_router.message(QuestionForm.question)
async def q_get_question(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if len(message.text.strip()) < 10:
        await message.answer("⚠️ Savolingiz juda qisqa. Iltimos, batafsil yozing.")
        return
    await state.update_data(question=message.text.strip())
    data = await state.get_data()
    await state.set_state(QuestionForm.confirm)
    await message.answer(
        t(lang, "confirm_question",
          full_name=data["full_name"],
          student_id=data["student_id"],
          faculty=data["faculty"],
          question=data["question"]),
        parse_mode="HTML",
        reply_markup=confirm_keyboard(lang)
    )


@questions_router.callback_query(QuestionForm.confirm, F.data == "confirm:yes")
async def q_confirm(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    data = await state.get_data()
    await state.clear()

    question_id = await db.save_question(
        user_id=callback.from_user.id,
        full_name=data["full_name"],
        student_id=data["student_id"],
        faculty=data["faculty"],
        question=data["question"]
    )

    await callback.message.edit_text(
        t(lang, "question_sent", id=question_id),
        parse_mode="HTML"
    )
    await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))

    notify_text = (
        f"🔔 <b>Yangi savol #{question_id}</b>\n\n"
        f"👤 {data['full_name']}\n"
        f"🎓 ID: {data['student_id']}\n"
        f"🏛 {data['faculty']}\n\n"
        f"❓ {data['question']}\n\n"
        f"Javob berish: /admin"
    )
    bot = callback.bot
    for lawyer_id in LAWYER_IDS + ADMIN_IDS:
        try:
            await bot.send_message(lawyer_id, notify_text, parse_mode="HTML")
        except Exception:
            pass

    await callback.answer()


@questions_router.callback_query(QuestionForm.confirm, F.data == "confirm:no")
async def q_edit(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    await state.set_state(QuestionForm.full_name)
    await callback.message.delete()
    await callback.message.answer(t(lang, "enter_fullname"), parse_mode="HTML", reply_markup=cancel_keyboard(lang))
    await callback.answer()
