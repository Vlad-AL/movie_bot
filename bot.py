import asyncio
import sqlite3
import re
import os
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove, MenuButtonDefault,
    FSInputFile, InputMediaVideo
)
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from dotenv import load_dotenv

# ================== CONFIG ==================
load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN not found")

PROXY_URL = "http://uapkuolo:00j38yrboe49@31.59.20.176:6754"

session = AiohttpSession(proxy=PROXY_URL, timeout=60)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

ADMIN_ID = 666877639
CHANNEL_USERNAME = "@kinonawe4er"

# ================== DB ==================
db_users = sqlite3.connect("users.db", check_same_thread=False)
cur_users = db_users.cursor()

db_media = sqlite3.connect("media.db", check_same_thread=False)
cur_media = db_media.cursor()

cur_users.execute("PRAGMA journal_mode=WAL;")
cur_users.execute("PRAGMA synchronous=NORMAL;")

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    encoding="utf-8"
)

# ================== HELPERS ==================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def normalize(text: str) -> str:
    return re.sub(r"[^\w]", "", text.lower().replace("ё", "е"))


# ================== MEDIA DB ==================
def get_movie(code):
    cur_media.execute("SELECT * FROM movies WHERE code=?", (code,))
    row = cur_media.fetchone()
    if not row:
        return None
    return {
        "code": row[0],
        "title": row[1],
        "year": row[2],
        "video": row[3],
        "description": row[4],
        "country": row[5],
        "director": row[6],
        "genres": row[7].split(",") if row[7] else []
    }


def get_series(code):
    cur_media.execute("SELECT * FROM series WHERE code=?", (code,))
    row = cur_media.fetchone()
    if not row:
        return None
    return {
        "code": row[0],
        "title": row[1],
        "year": row[2],
        "episode_counter": row[3],
        "description": row[4],
        "poster": row[5],
        "country": row[6],
        "director": row[7],
        "genres": row[8].split(",") if row[8] else []
    }


def get_episodes(code, season=None):
    if season is None:
        cur_media.execute("""
            SELECT episode_number, video, title
            FROM episodes
            WHERE series_code=?
            ORDER BY episode_number
        """, (code,))
    else:
        cur_media.execute("""
            SELECT episode_number, video, title
            FROM episodes
            WHERE series_code=? AND season_number=?
            ORDER BY episode_number
        """, (code, season))

    return [
        {"num": r[0], "video": r[1], "title": r[2]}
        for r in cur_media.fetchall()
    ]


# ================== USERS ==================
def add_or_update_user(user):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur_users.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,))
    exists = cur_users.fetchone()

    if exists:
        cur_users.execute("""
            UPDATE users SET last_seen=?, requests_count=requests_count+1
            WHERE user_id=?
        """, (now, user.id))
    else:
        cur_users.execute("""
            INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            now,
            now
        ))


def get_users_count():
    return cur_users.execute("SELECT COUNT(*) FROM users").fetchone()[0]


# ================== SUB ==================
async def is_subscribed(user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status not in ("left", "kicked")
    except:
        return False


# ================== KEYBOARDS ==================
def subscribe_keyboard_movie(code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📍 Подписаться", url="https://t.me/kinonawe4er")],
        [InlineKeyboardButton("🔎 Проверить", callback_data=f"check_movie:{code}")]
    ])


# ================== SEARCH ==================
def search_movies(query):
    query = normalize(query)
    cur_media.execute("SELECT code, title FROM movies")
    return [
        ("movie", r[0], get_movie(r[0]))
        for r in cur_media.fetchall()
        if query in normalize(r[1])
    ]


def search_series(query):
    query = normalize(query)
    cur_media.execute("SELECT code, title FROM series")
    return [
        ("series", r[0], get_series(r[0]))
        for r in cur_media.fetchall()
        if query in normalize(r[1])
    ]


def search_all(query):
    res = search_movies(query)
    if res:
        return res
    return search_series(query)


# ================== HANDLERS ==================
@dp.message(Command("start"))
async def start(m: types.Message):
    add_or_update_user(m.from_user)
    await m.answer("Введи название фильма или сериала", reply_markup=ReplyKeyboardRemove())


@dp.message()
async def handle(m: types.Message):
    res = search_all(m.text)

    if not res:
        await m.answer("Ничего не найдено")
        return

    if len(res) == 1:
        t, code, item = res[0]

        if t == "movie":
            await m.answer_video(item["video"], caption=item["title"])
        else:
            await m.answer(item["title"])
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'🎬' if t=='movie' else '📺'} {i['title']}",
            callback_data=f"open:{t}:{code}"
        )]
        for t, code, i in res
    ])

    await m.answer("Выбери:", reply_markup=kb)


# ================== MAIN ==================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())