from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup

from bot.config import ADMIN_IDS, TIME_SLOTS, get_service
from bot.database import create_booking, is_slot_taken
from bot.keyboards import confirm_booking_kb, dates_kb, main_menu_kb, times_kb
from bot.states import BookingStates
from bot.texts import (
    admin_new_booking,
    ask_name_text,
    ask_phone_text,
    booking_confirmed,
    booking_summary,
)

router = Router()

# Временное хранилище данных записи в FSM
BOOKING_KEY = "booking"


@router.message(F.text == "📅 Записаться")
async def book_from_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Выберите услугу для записи:",
        reply_markup=_services_book_kb(),
    )


@router.callback_query(F.data == "book:start")
async def book_start_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(
        "Выберите услугу для записи:",
        reply_markup=_services_book_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("book:"))
async def book_service(callback: CallbackQuery, state: FSMContext) -> None:
    action = callback.data.split(":")[1]
    if action == "cancel":
        await state.clear()
        await callback.message.edit_text("Запись отменена.")
        await callback.answer()
        return
    if action == "start":
        return

    service = get_service(action)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await state.update_data(**{BOOKING_KEY: {"service_id": service.id, "service_name": service.name, "price": service.price}})
    await callback.message.edit_text(
        f"📅 Выберите дату для «{service.name}»:",
        reply_markup=dates_kb(service.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("date:"))
async def pick_date(callback: CallbackQuery) -> None:
    _, service_id, booking_date = callback.data.split(":")
    service = get_service(service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    taken = set()
    for slot in TIME_SLOTS:
        if await is_slot_taken(booking_date, slot):
            taken.add(slot)

    from bot.texts import _format_date
    await callback.message.edit_text(
        f"🕐 Выберите время на {_format_date(booking_date)}:",
        reply_markup=times_kb(service_id, booking_date, taken),
    )
    await callback.answer()


@router.callback_query(F.data == "slot:taken")
async def slot_taken(callback: CallbackQuery) -> None:
    await callback.answer("Это время уже занято", show_alert=True)


@router.callback_query(F.data.startswith("time:"))
async def pick_time(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":")
    service_id, booking_date, booking_time = parts[1], parts[2], ":".join(parts[3:])

    if await is_slot_taken(booking_date, booking_time):
        await callback.answer("Это время только что заняли", show_alert=True)
        return

    data = await state.get_data()
    booking = data.get(BOOKING_KEY, {})
    booking.update({
        "service_id": service_id,
        "booking_date": booking_date,
        "booking_time": booking_time,
    })
    service = get_service(service_id)
    if service:
        booking["service_name"] = service.name
        booking["price"] = service.price

    await state.update_data(**{BOOKING_KEY: booking})
    await state.set_state(BookingStates.waiting_name)
    await callback.message.edit_text(ask_name_text())
    await callback.answer()


@router.message(BookingStates.waiting_name)
async def receive_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введите имя (минимум 2 символа):")
        return

    data = await state.get_data()
    booking = data.get(BOOKING_KEY, {})
    booking["client_name"] = name
    await state.update_data(**{BOOKING_KEY: booking})
    await state.set_state(BookingStates.waiting_phone)

    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Отправить телефон", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(ask_phone_text(), reply_markup=phone_kb)


@router.message(BookingStates.waiting_phone, F.contact)
async def receive_phone_contact(message: Message, state: FSMContext) -> None:
    phone = message.contact.phone_number
    await _show_confirmation(message, state, phone)


@router.message(BookingStates.waiting_phone)
async def receive_phone_text(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if len(phone) < 6:
        await message.answer("Введите корректный номер телефона:")
        return
    await _show_confirmation(message, state, phone)


async def _show_confirmation(message: Message, state: FSMContext, phone: str) -> None:
    data = await state.get_data()
    booking = data.get(BOOKING_KEY, {})
    booking["client_phone"] = phone
    await state.update_data(**{BOOKING_KEY: booking})
    await state.set_state(None)

    text = booking_summary(
        booking["service_name"],
        booking["price"],
        booking["booking_date"],
        booking["booking_time"],
        booking["client_name"],
        phone,
    )
    await message.answer(
        text,
        reply_markup=confirm_booking_kb(
            booking["service_id"],
            booking["booking_date"],
            booking["booking_time"],
        ),
    )


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_booking(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if not callback.from_user:
        return

    parts = callback.data.split(":")
    service_id, booking_date, booking_time = parts[1], parts[2], ":".join(parts[3:])

    if await is_slot_taken(booking_date, booking_time):
        await callback.answer("Это время уже занято. Выберите другое.", show_alert=True)
        return

    data = await state.get_data()
    booking = data.get(BOOKING_KEY, {})
    service = get_service(service_id)
    if not service or not booking.get("client_name"):
        await callback.answer("Данные записи устарели. Начните заново.", show_alert=True)
        await state.clear()
        return

    await create_booking(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        client_name=booking["client_name"],
        client_phone=booking["client_phone"],
        service_id=service.id,
        service_name=service.name,
        service_price=service.price,
        booking_date=booking_date,
        booking_time=booking_time,
    )

    await callback.message.edit_text(
        booking_confirmed(service.name, service.price, booking_date, booking_time)
    )
    await callback.message.answer("Главное меню 👇", reply_markup=main_menu_kb())
    await state.clear()
    await callback.answer("Вы записаны! ✅")

    admin_text = admin_new_booking(
        booking["client_name"],
        booking["client_phone"],
        callback.from_user.username,
        service.name,
        service.price,
        booking_date,
        booking_time,
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception:
            pass


def _services_book_kb():
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from bot.config import SERVICES

    buttons = [
        [InlineKeyboardButton(
            text=f"{s.name} — {s.price} ₽",
            callback_data=f"book:{s.id}",
        )]
        for s in SERVICES
    ]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="book:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
