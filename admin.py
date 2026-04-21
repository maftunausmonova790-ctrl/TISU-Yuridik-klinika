from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import admin_main_keyboard, admin_question_keyboard, admin_application_keyboard
from config import LAWYER_IDS, ADMIN_IDS, APPLICATION_TYPES

admin_router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in LAWYER_IDS or user_id in ADMIN_IDS


class AdminAnswer(StatesGroup):
    answering_question = State()
    rejecting_application = State()
    question_id = State()
    app_id = State()


@admin_router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Sizda bu bo'limga kirish huquqi yo'q.")
        return
    stats = await db.get_stats()
    text = (
        f"⚖️ <b>TISU Yuridik Klinika — Admin Panel</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['total_users']}</b>\n\n"
        f"❓ Savollar: <b>{stats['total_questions']}</b> jami | "
        f"<b>{stats['pending_questions']}</b> kutilmoqda\n"
        f"📋 Arizalar: <b>{stats['total_applications']}</b> jami | "
        f"<b>{stats['pending_applications']}</b> kutilmoqda"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=admin_main_keyboard())


@admin_router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    stats = await db.get_stats()
    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n\n"
        f"❓ Jami savollar: <b>{stats['total_questions']}</b>\n"
        f"  ⏳ Kutilmoqda: <b>{stats['pending_questions']}</b>\n"
        f"  ✅ Javob berildi: <b>{stats['done_questions']}</b>\n\n"
        f"📋 Jami arizalar: <b>{stats['total_applications']}</b>\n"
        f"  ⏳ Kutilmoqda: <b>{stats['pending_applications']}</b>\n"
        f"  ✅ Ko'rib chiqildi: <b>{stats['done_applications']}</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:questions")
async def admin_questions(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    rows = await db.get_pending_questions()
    if not rows:
        await callback.answer("✅ Kutilayotgan savollar yo'q!", show_alert=True)
        return
    for row in rows:
        text = (
            f"❓ <b>Savol #{row['id']}</b>\n"
            f"📅 {row['created_at'][:16]}\n\n"
            f"👤 {row['full_name']}\n"
            f"🎓 {row['student_id']} | 🏛 {row['faculty']}\n\n"
            f"💬 {row['question']}"
        )
        await callback.message.answer(
            text, parse_mode="HTML",
            reply_markup=admin_question_keyboard(row["id"])
        )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("aq:answer:"))
async def admin_answer_question(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    question_id = int(callback.data.split(":")[2])
    await state.set_state(AdminAnswer.answering_question)
    await state.update_data(question_id=question_id)
    await callback.message.answer(
        f"✍️ <b>#{question_id}-savol uchun javob yozing:</b>",
        parse_mode="HTML"
    )
    await callback.answer()


@admin_router.message(AdminAnswer.answering_question)
async def admin_save_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question_id = data["question_id"]
    await state.clear()

    user_id = await db.answer_question(question_id, message.text.strip(), message.from_user.id)

    await message.answer(f"✅ Javob #{question_id} uchun saqlandi va foydalanuvchiga yuborildi.")

    if user_id:
        user = await db.get_user(user_id)
        lang = user["language"] if user else "uz"
        notify = (
            f"⚖️ <b>TISU Yuridik Klinika</b>\n\n"
            f"✅ <b>#{question_id}-savolingizga javob keldi!</b>\n\n"
            f"📝 <b>Javob:</b>\n{message.text.strip()}"
        )
        try:
            await message.bot.send_message(user_id, notify, parse_mode="HTML")
        except Exception:
            pass


@admin_router.callback_query(F.data == "admin:applications")
async def admin_applications(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    rows = await db.get_pending_applications()
    if not rows:
        await callback.answer("✅ Kutilayotgan arizalar yo'q!", show_alert=True)
        return
    for row in rows:
        app_type_name = APPLICATION_TYPES.get(row["app_type"], {}).get("uz", row["app_type"])
        text = (
            f"📋 <b>Ariza #{row['id']}</b> — {app_type_name}\n"
            f"📅 {row['created_at'][:16]}\n\n"
            f"👤 {row['full_name']}\n"
            f"🎓 {row['student_id']} | 🏛 {row['faculty']}\n"
            f"📅 {row['course']} kurs | {row['group_name']} guruh\n"
            f"📱 {row['phone']}\n\n"
            f"📝 <b>Sabab:</b> {row['reason']}"
        )
        if row["extra_info"]:
            text += f"\n📎 <b>Qo'shimcha:</b> {row['extra_info']}"
        await callback.message.answer(
            text, parse_mode="HTML",
            reply_markup=admin_application_keyboard(row["id"])
        )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("aa:"))
async def admin_update_application(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    parts = callback.data.split(":")
    action, app_id = parts[1], int(parts[2])

    if action == "approve":
        user_id = await db.update_application_status(app_id, "approved", callback.from_user.id, "")
        await callback.message.edit_reply_markup()
        await callback.message.answer(f"✅ Ariza #{app_id} tasdiqlandi.")
        if user_id:
            try:
                await callback.bot.send_message(
                    user_id,
                    f"⚖️ <b>TISU Yuridik Klinika</b>\n\n✅ <b>#{app_id}-arizangiz tasdiqlandi!</b>\n\nBatafsil ma'lumot uchun yuridik klinikaga murojaat qiling.",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    elif action == "reject":
        await state.set_state(AdminAnswer.rejecting_application)
        await state.update_data(app_id=app_id)
        await callback.message.answer(f"❌ <b>#{app_id}-ariza rad etish sababini yozing:</b>", parse_mode="HTML")

    elif action == "review":
        user_id = await db.update_application_status(app_id, "in_review", callback.from_user.id, "Ko'rib chiqilmoqda")
        await callback.message.edit_reply_markup()
        await callback.message.answer(f"🔍 Ariza #{app_id} ko'rib chiqilmoqda deb belgilandi.")
        if user_id:
            try:
                await callback.bot.send_message(
                    user_id,
                    f"⚖️ <b>TISU Yuridik Klinika</b>\n\n🔍 <b>#{app_id}-arizangiz ko'rib chiqilmoqda.</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    elif action == "back":
        await callback.message.delete()

    await callback.answer()


@admin_router.message(AdminAnswer.rejecting_application)
async def admin_reject_with_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    app_id = data["app_id"]
    await state.clear()

    user_id = await db.update_application_status(app_id, "rejected", message.from_user.id, message.text.strip())
    await message.answer(f"❌ Ariza #{app_id} rad etildi.")

    if user_id:
        try:
            await message.bot.send_message(
                user_id,
                f"⚖️ <b>TISU Yuridik Klinika</b>\n\n❌ <b>#{app_id}-arizangiz rad etildi.</b>\n\n📝 <b>Sabab:</b> {message.text.strip()}",
                parse_mode="HTML"
            )
        except Exception:
            pass
