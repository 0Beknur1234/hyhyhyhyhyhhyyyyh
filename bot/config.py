import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Service:
    id: str
    name: str
    price: int
    duration_min: int
    description: str


SERVICES: list[Service] = [
    Service(
        "classic",
        "Маникюр классический",
        1500,
        60,
        "Обработка кутикулы, придание формы, без покрытия",
    ),
    Service(
        "gel",
        "Маникюр + гель-лак",
        2200,
        90,
        "Маникюр, покрытие гель-лаком, база и топ",
    ),
    Service(
        "remove_gel",
        "Снятие + маникюр + покрытие",
        2500,
        120,
        "Безопасное снятие старого покрытия и новое",
    ),
    Service(
        "design",
        "Дизайн (за 1 ноготь)",
        150,
        15,
        "Рисунок, стразы, фольга — добавляется к основной услуге",
    ),
    Service(
        "pedicure",
        "Педикюр + покрытие",
        2800,
        120,
        "Аппаратный или классический педикюр с покрытием",
    ),
    Service(
        "strengthen",
        "Укрепление ногтей",
        800,
        30,
        "Гелевая база или акригель для укрепления",
    ),
]

# Рабочие слоты (Пн–Сб)
TIME_SLOTS = ["10:00", "11:30", "13:00", "14:30", "16:00", "17:30"]
WORKING_WEEKDAYS = {0, 1, 2, 3, 4, 5}  # Пн=0 … Сб=5

PORTFOLIO_ITEMS = [
    {
        "title": "Нюдовый маникюр",
        "caption": "💅 Нюдовый маникюр с минималистичным дизайном",
        "url": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&q=80",
    },
    {
        "title": "Фrench",
        "caption": "✨ Классический French с блёстками",
        "url": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=800&q=80",
    },
    {
        "title": "Яркий дизайн",
        "caption": "🌸 Весенний дизайн с цветочками",
        "url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80",
    },
    {
        "title": "Матовое покрытие",
        "caption": "🖤 Матовый маникюр — стильно и аккуратно",
        "url": "https://images.unsplash.com/photo-1519014816548-bf271f360712?w=800&q=80",
    },
]


def get_service(service_id: str) -> Service | None:
    return next((s for s in SERVICES if s.id == service_id), None)


def parse_admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "")
    return {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = parse_admin_ids()
MASTER_NAME = os.getenv("MASTER_NAME", "Анна")
MASTER_PHONE = os.getenv("MASTER_PHONE", "+7 (999) 123-45-67")
MASTER_ADDRESS = os.getenv("MASTER_ADDRESS", "г. Москва, ул. Примерная, 10")
MASTER_INSTAGRAM = os.getenv("MASTER_INSTAGRAM", "@nail_master_demo")
MASTER_TELEGRAM = os.getenv("MASTER_TELEGRAM", "@nail_master_demo")
