from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from texts import t
from keyboards import (cancel_keyboard, cancel_skip_keyboard,
                       confirm_keyboard, app_type_keyboard, main_menu_keyboard)
from config import LAWYER_IDS, ADMIN_IDS, APPLICATION_TYPES

applications_router = Router()


class ApplicationForm(StatesGroup):
    app_type = State()
    full_name = State()
    student_id = State()
    faculty = State()
    course = State()
    group_name = State()
    phone = State()
    reason = State()
    extra_info = State()
    confirm = State()


async def get_lang(user_id: int) -> str:
    user = await db.get_user(user_id)
    return user["language"] if user else "uz"


@applications_router.message(F.text.in_([
    "📋 Ariza shakllantirish", "📋 Подать заявление", "📋 Make an application"
]))
async def start_application(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    await state.set_state(ApplicationForm.app_type)
    await message.answer(t(lang, "choose_app_type"), parse_mode="HTML", reply_markup=app_type_keyboard(lang))


@applications_router.callback_query(ApplicationForm.app_type, F.data.startswith("apptype:"))
async def a_get_type(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    app_type = callback.data.split(":")[1]

    if app_type == "back":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))
        await callback.answer()
        return

    await state.update_data(app_type=app_type)
    await state.set_state(ApplicationForm.full_name)
    await callback.message.delete()
    await callback.message.answer(t(lang, "enter_fullname"), parse_mode="HTML", reply_markup=cancel_keyboard(lang))
    await callback.answer()


@applications_router.message(ApplicationForm.full_name)
async def a_get_fullname(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if len(message.text.strip()) < 5:
        await message.answer("⚠️ To'liq ismingizni kiriting (F.I.SH).")
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(ApplicationForm.student_id)
    await message.answer(t(lang, "enter_student_id"), parse_mode="HTML")


@applications_router.message(ApplicationForm.student_id)
async def a_get_student_id(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.update_data(student_id=message.text.strip())
    await state.set_state(ApplicationForm.faculty)
    await message.answer(t(lang, "enter_faculty"), parse_mode="HTML")


@applications_router.message(ApplicationForm.faculty)
async def a_get_faculty(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.update_data(faculty=message.text.strip())
    await state.set_state(ApplicationForm.course)
    await message.answer(t(lang, "enter_course"), parse_mode="HTML")


@applications_router.message(ApplicationForm.course)
async def a_get_course(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    parts = message.text.strip().split()
    course = parts[0] if parts else message.text.strip()
    group = " ".join(parts[1:]) if len(parts) > 1 else ""
    await state.update_data(course=course, group_name=group)
    await state.set_state(ApplicationForm.phone)
    await message.answer(t(lang, "enter_phone"), parse_mode="HTML")


@applications_router.message(ApplicationForm.phone)
async def a_get_phone(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.update_data(phone=message.text.strip())
    await state.set_state(ApplicationForm.reason)
    await message.answer(t(lang, "enter_reason"), parse_mode="HTML")


@applications_router.message(ApplicationForm.reason)
async def a_get_reason(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if len(message.text.strip()) < 5:
        await message.answer("⚠️ Iltimos, sababni batafsil yozing.")
        return
    await state.update_data(reason=message.text.strip())
    await state.set_state(ApplicationForm.extra_info)
    await message.answer(t(lang, "enter_extra"), parse_mode="HTML", reply_markup=cancel_skip_keyboard(lang))


@applications_router.message(ApplicationForm.extra_info)
async def a_get_extra(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    skip_texts = ["⏭ O'tkazib yuborish", "⏭ Пропустить", "⏭ Skip"]
    extra = "" if message.text in skip_texts else message.text.strip()
    await state.update_data(extra_info=extra)
    data = await state.get_data()
    app_type_name = APPLICATION_TYPES.get(data["app_type"], {}).get(lang, data["app_type"])
    await state.set_state(ApplicationForm.confirm)
    await message.answer(
        t(lang, "confirm_application",
          full_name=data["full_name"],
          student_id=data["student_id"],
          faculty=data["faculty"],
          course=data["course"],
          group_name=data.get("group_name", "—"),
          phone=data["phone"],
          app_type=app_type_name,
          reason=data["reason"]),
        parse_mode="HTML",
        reply_markup=confirm_keyboard(lang)
    )


@applications_router.callback_query(ApplicationForm.confirm, F.data == "confirm:yes")
async def a_confirm(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    await state.clear()

    app_id = await db.save_application(data)
    app_type_name = APPLICATION_TYPES.get(data["app_type"], {}).get(lang, data["app_type"])

    await callback.message.edit_text(
        t(lang, "application_sent", id=app_id),
        parse_mode="HTML"
    )
    await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))

    notify_text = (
        f"🔔 <b>Yangi ariza #{app_id}</b>\n\n"
        f"📋 Turi: {app_type_name}\n"
        f"👤 {data['full_name']}\n"
        f"🎓 ID: {data['student_id']}\n"
        f"🏛 {data['faculty']} | {data['course']} kurs\n"
        f"📱 {data['phone']}\n\n"
        f"📝 Sabab: {data['reason']}\n\n"
        f"Ko'rish: /admin"
    )
    bot = callback.bot
    for lawyer_id in LAWYER_IDS + ADMIN_IDS:
        try:
            await bot.send_message(lawyer_id, notify_text, parse_mode="HTML")
        except Exception:
            pass
    await callback.answer()


@applications_router.callback_query(ApplicationForm.confirm, F.data == "confirm:no")
async def a_edit(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    await state.set_state(ApplicationForm.full_name)
    await callback.message.delete()
    await callback.message.answer(t(lang, "enter_fullname"), parse_mode="HTML", reply_markup=cancel_keyboard(lang))
    await callback.answer()
