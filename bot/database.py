import aiosqlite

DB_PATH = "bot.db"

CREATE_BOOKINGS = """
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    client_name TEXT NOT NULL,
    client_phone TEXT NOT NULL,
    service_id TEXT NOT NULL,
    service_name TEXT NOT NULL,
    service_price INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    booking_time TEXT NOT NULL,
    reminder_24h_sent INTEGER DEFAULT 0,
    reminder_1h_sent INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
)
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_bookings_datetime
ON bookings(booking_date, booking_time, status)
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_BOOKINGS)
        await db.execute(CREATE_INDEX)
        await db.commit()


async def create_booking(
    *,
    user_id: int,
    username: str | None,
    client_name: str,
    client_phone: str,
    service_id: str,
    service_name: str,
    service_price: int,
    booking_date: str,
    booking_time: str,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO bookings (
                user_id, username, client_name, client_phone,
                service_id, service_name, service_price,
                booking_date, booking_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                client_name,
                client_phone,
                service_id,
                service_name,
                service_price,
                booking_date,
                booking_time,
            ),
        )
        await db.commit()
        return cursor.lastrowid or 0


async def is_slot_taken(booking_date: str, booking_time: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT 1 FROM bookings
            WHERE booking_date = ? AND booking_time = ? AND status = 'active'
            LIMIT 1
            """,
            (booking_date, booking_time),
        )
        return await cursor.fetchone() is not None


async def get_user_active_bookings(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM bookings
            WHERE user_id = ? AND status = 'active'
            ORDER BY booking_date, booking_time
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def cancel_booking(booking_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            UPDATE bookings SET status = 'cancelled'
            WHERE id = ? AND user_id = ? AND status = 'active'
            """,
            (booking_id, user_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_bookings_for_admin(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM bookings
            WHERE status = 'active'
            ORDER BY booking_date, booking_time
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_active_bookings_for_reminders() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM bookings
            WHERE status = 'active'
              AND (reminder_24h_sent = 0 OR reminder_1h_sent = 0)
            """
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def mark_reminder_sent(booking_id: int, reminder_type: str) -> None:
    column = "reminder_24h_sent" if reminder_type == "24h" else "reminder_1h_sent"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE bookings SET {column} = 1 WHERE id = ?",
            (booking_id,),
        )
        await db.commit()
