from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.config import ADMIN_IDS, PORTFOLIO_ITEMS, get_service
from bot.database import cancel_booking, get_user_active_bookings
from bot.keyboards import (
    back_to_menu_kb,
    main_menu_kb,
    my_bookings_kb,
    portfolio_kb,
    service_detail_kb,
    services_kb,
)
from bot.texts import (
    contacts_text,
    my_bookings_empty,
    portfolio_intro,
    price_list_text,
    service_detail_text,
    welcome_text,
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(welcome_text(), reply_markup=main_menu_kb())


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if message.from_user and message.from_user.id not in ADMIN_IDS:
        return
    from bot.database import get_bookings_for_admin
    from bot.texts import _format_date

    bookings = await get_bookings_for_admin()
    if not bookings:
        await message.answer("📋 Активных записей пока нет.")
        return

    lines = ["📋 <b>Активные записи:</b>\n"]
    for b in bookings:
        user = f"@{b['username']}" if b.get("username") else "—"
        lines.append(
            f"#{b['id']} · {b['client_name']} ({user})\n"
            f"📞 {b['client_phone']}\n"
            f"💅 {b['service_name']} — {b['service_price']} ₽\n"
            f"📅 {_format_date(b['booking_date'])} в {b['booking_time']}\n"
        )
    await message.answer("\n".join(lines))


@router.message(F.text == "◀️ В главное меню")
@router.message(F.text.lower().in_({"меню", "назад"}))
async def back_to_menu(message: Message) -> None:
    await message.answer("Главное меню 👇", reply_markup=main_menu_kb())


@router.message(F.text == "💅 Прайс и услуги")
async def show_price(message: Message) -> None:
    await message.answer(price_list_text(), reply_markup=services_kb())


@router.callback_query(F.data == "price:list")
async def show_price_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(price_list_text(), reply_markup=services_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("svc:"))
async def show_service_detail(callback: CallbackQuery) -> None:
    service_id = callback.data.split(":")[1]
    service = get_service(service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return
    text = service_detail_text(
        service.name, service.price, service.duration_min, service.description
    )
    await callback.message.edit_text(text, reply_markup=service_detail_kb(service_id))
    await callback.answer()


@router.message(F.text == "📍 Контакты")
async def show_contacts(message: Message) -> None:
    await message.answer(contacts_text(), reply_markup=back_to_menu_kb())


@router.message(F.text == "🖼 Примеры работ")
async def show_portfolio(message: Message) -> None:
    await message.answer(portfolio_intro(), reply_markup=portfolio_kb())


@router.callback_query(F.data.startswith("portfolio:"))
async def show_portfolio_item(callback: CallbackQuery) -> None:
    idx = int(callback.data.split(":")[1])
    item = PORTFOLIO_ITEMS[idx]
    await callback.message.answer_photo(
        photo=item["url"],
        caption=item["caption"],
        reply_markup=portfolio_kb(),
    )
    await callback.answer()


@router.message(F.text == "📋 Мои записи")
async def show_my_bookings(message: Message) -> None:
    if not message.from_user:
        return
    bookings = await get_user_active_bookings(message.from_user.id)
    if not bookings:
        await message.answer(my_bookings_empty(), reply_markup=main_menu_kb())
        return

    lines = ["📋 <b>Ваши записи:</b>\n"]
    from bot.texts import _format_date
    for b in bookings:
        lines.append(
            f"• {_format_date(b['booking_date'])} в {b['booking_time']}\n"
            f"  {b['service_name']} — {b['service_price']} ₽\n"
        )
    lines.append("\nНажмите, чтобы отменить запись:")
    await message.answer(
        "\n".join(lines),
        reply_markup=my_bookings_kb(bookings),
    )


@router.callback_query(F.data.startswith("cancel_booking:"))
async def cancel_user_booking(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return
    booking_id = int(callback.data.split(":")[1])
    ok = await cancel_booking(booking_id, callback.from_user.id)
    if ok:
        await callback.message.edit_text("❌ Запись отменена.")
        await callback.answer("Запись отменена")
    else:
        await callback.answer("Не удалось отменить", show_alert=True)
