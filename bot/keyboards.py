from datetime import date, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot.config import PORTFOLIO_ITEMS, SERVICES, TIME_SLOTS, WORKING_WEEKDAYS


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💅 Прайс и услуги"), KeyboardButton(text="📅 Записаться")],
            [KeyboardButton(text="🖼 Примеры работ"), KeyboardButton(text="📍 Контакты")],
            [KeyboardButton(text="📋 Мои записи")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел меню",
    )


def back_to_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ В главное меню")]],
        resize_keyboard=True,
    )


def services_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"{s.name} — {s.price} ₽",
            callback_data=f"svc:{s.id}",
        )]
        for s in SERVICES
    ]
    buttons.append([InlineKeyboardButton(text="📅 Записаться", callback_data="book:start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def service_detail_kb(service_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📅 Записаться на эту услугу",
                callback_data=f"book:{service_id}",
            )],
            [InlineKeyboardButton(text="◀️ К списку услуг", callback_data="price:list")],
        ]
    )


def available_dates(days: int = 14) -> list[date]:
    today = date.today()
    result = []
    for i in range(days):
        d = today + timedelta(days=i)
        if d.weekday() in WORKING_WEEKDAYS:
            result.append(d)
    return result


def dates_kb(service_id: str) -> InlineKeyboardMarkup:
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    buttons = []
    row = []
    for d in available_dates():
        label = f"{weekdays_ru[d.weekday()]} {d.strftime('%d.%m')}"
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=f"date:{service_id}:{d.isoformat()}",
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="book:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def times_kb(service_id: str, booking_date: str, taken_slots: set[str]) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for slot in TIME_SLOTS:
        if slot in taken_slots:
            row.append(InlineKeyboardButton(text=f"🚫 {slot}", callback_data="slot:taken"))
        else:
            row.append(InlineKeyboardButton(
                text=slot,
                callback_data=f"time:{service_id}:{booking_date}:{slot}",
            ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data=f"book:{service_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="book:cancel"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_booking_kb(service_id: str, booking_date: str, booking_time: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Подтвердить запись",
                callback_data=f"confirm:{service_id}:{booking_date}:{booking_time}",
            )],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="book:cancel")],
        ]
    )


def portfolio_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=item["title"], callback_data=f"portfolio:{i}")]
        for i, item in enumerate(PORTFOLIO_ITEMS)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def my_bookings_kb(bookings: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for b in bookings:
        label = f"❌ {b['booking_date']} {b['booking_time']} — {b['service_name']}"
        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=f"cancel_booking:{b['id']}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
