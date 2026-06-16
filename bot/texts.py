from bot.config import MASTER_ADDRESS, MASTER_INSTAGRAM, MASTER_NAME, MASTER_PHONE, MASTER_TELEGRAM, SERVICES


def welcome_text() -> str:
    return (
        f"💅 <b>Студия маникюра — {MASTER_NAME}</b>\n\n"
        "Добро пожаловать! Я помогу вам:\n"
        "• посмотреть прайс и услуги\n"
        "• записаться на удобное время\n"
        "• узнать адрес и контакты\n"
        "• посмотреть примеры работ\n\n"
        "Выберите нужный раздел в меню 👇"
    )


def price_list_text() -> str:
    lines = ["💅 <b>Прайс-лист</b>\n"]
    for s in SERVICES:
        lines.append(f"<b>{s.name}</b> — {s.price} ₽")
        lines.append(f"  ⏱ ~{s.duration_min} мин · {s.description}\n")
    lines.append("Нажмите на услугу, чтобы узнать подробнее или записаться.")
    return "\n".join(lines)


def service_detail_text(name: str, price: int, duration: int, description: str) -> str:
    return (
        f"💅 <b>{name}</b>\n\n"
        f"💰 Стоимость: <b>{price} ₽</b>\n"
        f"⏱ Длительность: ~{duration} мин\n\n"
        f"{description}"
    )


def contacts_text() -> str:
    return (
        f"📍 <b>Контакты</b>\n\n"
        f"👤 Мастер: {MASTER_NAME}\n"
        f"📞 Телефон: {MASTER_PHONE}\n"
        f"📍 Адрес: {MASTER_ADDRESS}\n"
        f"📸 Instagram: {MASTER_INSTAGRAM}\n"
        f"💬 Telegram: {MASTER_TELEGRAM}\n\n"
        f"🕐 <b>Режим работы:</b> Пн–Сб, 10:00–19:00\n"
        f"📅 Запись через бота или по телефону"
    )


def portfolio_intro() -> str:
    return (
        "🖼 <b>Примеры работ</b>\n\n"
        "Выберите работу, чтобы посмотреть фото.\n"
        "Больше работ — в Instagram 📸"
    )


def ask_name_text() -> str:
    return "📝 Как к вам обращаться? Напишите ваше имя:"


def ask_phone_text() -> str:
    return (
        "📞 Укажите номер телефона для связи.\n"
        "Можно нажать кнопку ниже или написать вручную."
    )


def booking_summary(
    service_name: str,
    price: int,
    booking_date: str,
    booking_time: str,
    client_name: str,
    client_phone: str,
) -> str:
    date_fmt = _format_date(booking_date)
    return (
        "📋 <b>Проверьте запись:</b>\n\n"
        f"💅 Услуга: {service_name}\n"
        f"💰 Стоимость: {price} ₽\n"
        f"📅 Дата: {date_fmt}\n"
        f"🕐 Время: {booking_time}\n"
        f"👤 Имя: {client_name}\n"
        f"📞 Телефон: {client_phone}\n\n"
        "Подтвердите запись или отмените."
    )


def booking_confirmed(
    service_name: str,
    price: int,
    booking_date: str,
    booking_time: str,
) -> str:
    return (
        "✅ <b>Вы записаны!</b>\n\n"
        f"💅 {service_name} — {price} ₽\n"
        f"📅 {_format_date(booking_date)} в {booking_time}\n"
        f"📍 {MASTER_ADDRESS}\n\n"
        "Мы напомним вам за день и за час до визита.\n"
        "Если планы изменились — отмените запись в «Мои записи»."
    )


def reminder_text(reminder_type: str, service_name: str, booking_date: str, booking_time: str) -> str:
    when = "завтра" if reminder_type == "24h" else "через час"
    return (
        f"⏰ <b>Напоминание о записи</b>\n\n"
        f"Ваш визит {when}:\n"
        f"💅 {service_name}\n"
        f"📅 {_format_date(booking_date)} в {booking_time}\n"
        f"📍 {MASTER_ADDRESS}\n\n"
        "Ждём вас! 💅"
    )


def admin_new_booking(
    client_name: str,
    client_phone: str,
    username: str | None,
    service_name: str,
    price: int,
    booking_date: str,
    booking_time: str,
) -> str:
    user_line = f"@{username}" if username else "без username"
    return (
        "🆕 <b>Новая запись!</b>\n\n"
        f"👤 {client_name} ({user_line})\n"
        f"📞 {client_phone}\n"
        f"💅 {service_name} — {price} ₽\n"
        f"📅 {_format_date(booking_date)} в {booking_time}"
    )


def _format_date(iso_date: str) -> str:
    y, m, d = iso_date.split("-")
    months = [
        "", "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
    ]
    return f"{int(d)} {months[int(m)]}"


def my_bookings_empty() -> str:
    return "У вас пока нет активных записей.\n\nНажмите «📅 Записаться», чтобы выбрать время."
