import logging
from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database import get_active_bookings_for_reminders, mark_reminder_sent
from bot.texts import reminder_text

logger = logging.getLogger(__name__)


def _parse_appointment(booking_date: str, booking_time: str) -> datetime:
    return datetime.strptime(f"{booking_date} {booking_time}", "%Y-%m-%d %H:%M")


async def send_reminders(bot: Bot) -> None:
    now = datetime.now()
    bookings = await get_active_bookings_for_reminders()

    for b in bookings:
        appt = _parse_appointment(b["booking_date"], b["booking_time"])
        if appt <= now:
            continue

        hours_left = (appt - now).total_seconds() / 3600

        if not b["reminder_24h_sent"] and 23 <= hours_left <= 25:
            rtype = "24h"
        elif not b["reminder_1h_sent"] and 0.83 <= hours_left <= 1.17:
            rtype = "1h"
        else:
            continue

        text = reminder_text(
            rtype, b["service_name"], b["booking_date"], b["booking_time"]
        )
        try:
            await bot.send_message(b["user_id"], text)
            await mark_reminder_sent(b["id"], rtype)
            logger.info("Reminder %s sent for booking #%s", rtype, b["id"])
        except Exception as e:
            logger.warning("Failed to send reminder for booking #%s: %s", b["id"], e)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, "interval", minutes=5, args=[bot])
    return scheduler
