import aiosqlite
from datetime import datetime
from config import DATABASE_URL


async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                full_name   TEXT,
                username    TEXT,
                language    TEXT DEFAULT 'uz',
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                full_name   TEXT,
                student_id  TEXT,
                faculty     TEXT,
                question    TEXT NOT NULL,
                answer      TEXT,
                status      TEXT DEFAULT 'pending',
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                answered_at TEXT,
                lawyer_id   INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER,
                full_name    TEXT,
                student_id   TEXT,
                faculty      TEXT,
                course       TEXT,
                group_name   TEXT,
                phone        TEXT,
                app_type     TEXT NOT NULL,
                reason       TEXT,
                extra_info   TEXT,
                status       TEXT DEFAULT 'pending',
                file_path    TEXT,
                created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
                reviewed_at  TEXT,
                lawyer_id    INTEGER,
                lawyer_note  TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()


async def upsert_user(user_id: int, full_name: str, username: str, language: str = "uz"):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            INSERT INTO users (user_id, full_name, username, language)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                username  = excluded.username
        """, (user_id, full_name, username, language))
        await db.commit()


async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        await db.commit()


async def save_question(user_id: int, full_name: str, student_id: str, faculty: str, question: str) -> int:
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            INSERT INTO questions (user_id, full_name, student_id, faculty, question)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, full_name, student_id, faculty, question))
        await db.commit()
        return cursor.lastrowid


async def save_application(data: dict) -> int:
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            INSERT INTO applications
                (user_id, full_name, student_id, faculty, course, group_name, phone, app_type, reason, extra_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["user_id"], data["full_name"], data["student_id"],
            data["faculty"], data["course"], data["group_name"],
            data["phone"], data["app_type"], data["reason"], data.get("extra_info", "")
        ))
        await db.commit()
        return cursor.lastrowid


async def get_pending_questions():
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM questions WHERE status = 'pending' ORDER BY created_at DESC"
        )
        return await cursor.fetchall()


async def get_pending_applications():
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM applications WHERE status = 'pending' ORDER BY created_at DESC"
        )
        return await cursor.fetchall()


async def get_user_questions(user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM questions WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        )
        return await cursor.fetchall()


async def get_user_applications(user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        )
        return await cursor.fetchall()


async def answer_question(question_id: int, answer: str, lawyer_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            UPDATE questions SET answer = ?, status = 'answered',
            answered_at = ?, lawyer_id = ?
            WHERE id = ?
        """, (answer, datetime.now().isoformat(), lawyer_id, question_id))
        await db.commit()
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id FROM questions WHERE id = ?", (question_id,))
        row = await cursor.fetchone()
        return row["user_id"] if row else None


async def update_application_status(app_id: int, status: str, lawyer_id: int, note: str = ""):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            UPDATE applications SET status = ?, lawyer_id = ?,
            lawyer_note = ?, reviewed_at = ?
            WHERE id = ?
        """, (status, lawyer_id, note, datetime.now().isoformat(), app_id))
        await db.commit()
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id FROM applications WHERE id = ?", (app_id,))
        row = await cursor.fetchone()
        return row["user_id"] if row else None


async def get_stats():
    async with aiosqlite.connect(DATABASE_URL) as db:
        stats = {}
        for table, col in [("questions", "questions"), ("applications", "applications")]:
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"total_{col}"] = (await cursor.fetchone())[0]
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table} WHERE status='pending'")
            stats[f"pending_{col}"] = (await cursor.fetchone())[0]
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table} WHERE status='answered' OR status='approved'")
            stats[f"done_{col}"] = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        stats["total_users"] = (await cursor.fetchone())[0]
        return stats
