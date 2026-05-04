import asyncio
import sqlite3
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
from datetime import datetime
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
import os
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import MenuButtonDefault
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from aiogram.types import FSInputFile

load_dotenv()                    # загружает .env файл
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден в .env файле!")

PROXY_URL = "http://uapkuolo:00j38yrboe49@31.59.20.176:6754"


session = AiohttpSession(
    proxy=PROXY_URL,
    timeout=60,
)

bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

users_db = sqlite3.connect("users.db", check_same_thread=False)
users_cursor = users_db.cursor()

users_cursor.execute("PRAGMA journal_mode=WAL;")
users_cursor.execute("PRAGMA synchronous=NORMAL;")


# ===== MEDIA DB =====
media_db = sqlite3.connect("media.db", check_same_thread=False)
media_cursor = media_db.cursor()

media_cursor.execute("PRAGMA journal_mode=WAL;")
media_cursor.execute("PRAGMA synchronous=NORMAL;")

ADMIN_ID = 666877639

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

db = sqlite3.connect("users.db", isolation_level=None)

logging.basicConfig(
    filename="/root/movie_bot/bot.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    encoding="utf-8"
)

def add_or_update_user(user):
    cursor = db.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE users
            SET last_seen = ?, requests_count = requests_count + 1
            WHERE user_id = ?
        """, (now, user.id))
    else:
        cursor.execute("""
            INSERT INTO users (
                user_id, username, first_name, last_name,
                first_seen, last_seen, requests_count
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            now,
            now
        ))

def get_top_users(limit=10):
    users_cursor.execute("""
        SELECT user_id, requests_count
        FROM users
        ORDER BY requests_count DESC
        LIMIT ?
    """, (limit,))
    return users_cursor.fetchall()

def get_users_count() -> int:
    users_cursor.execute("SELECT COUNT(*) FROM users")
    return users_cursor.fetchone()[0]


CHANNEL_USERNAME = "@kinonawe4er"

def get_all_users(limit: int = 20):
    users_cursor.execute("""
        SELECT user_id, username, first_name, last_name, requests_count, last_seen
        FROM users
        ORDER BY last_seen DESC
        LIMIT ?
    """, (limit,))
    return users_cursor.fetchall()

async def send_long_text(message, text, chunk_size=3800):
    for i in range(0, len(text), chunk_size):
        await message.answer(text[i:i + chunk_size])


async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in ("left", "kicked")
    except:
        return False

@dp.message(Command("top"))
async def top_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    users = get_top_users()

    text = "🏆 Топ пользователей\n\n"
    for i, (uid, count) in enumerate(users, 1):
        text += f"{i}. {uid} — {count}\n"

    await message.answer(text)


@dp.message(Command("users"))
async def show_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    users = get_all_users()

    text = "👥 Пользователи\n\n"
    for i, (uid, username, first_name, last_name, count, last_seen) in enumerate(users, 1):
        name = f"{first_name or ''} {last_name or ''}".strip() or username or "Unknown"
        text += f"{i}. {name} ({uid}) — {count}\n"

    await send_long_text(message, text)


@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    count = get_users_count()
    await message.answer(f"Всего пользователей: {count}")

movies = {
    
}

series = {
    "004": {
        "title": "Алиса в пограничье",
        "year": 2020,
        "episode_counter": "22 серии",
        "description": "Японский геймер по имени Рёхэй Арису случайно устраивает аварию на пешеходном переходе и жестоко за это расплачивается. Его переносит в альтернативный Токио, в котором практически нет людей, а немногочисленные жители вынуждены играть в странные игры. Этот мир — арена, и её нельзя покинуть самовольно. Теперь Рёхэй Арису и его друзья должны следовать правилам.",
        "poster": "AgACAgIAAxkBAAISgmmIlHh_ZISWdlspR3DE5LMjghEUAAJ7FGsbiudJSLH1YBglaJ_nAQADAgADeAADOgQ",
        "country": "Япония",
        "director": "Синсуке Сато",
        "genres": ["триллер", "драма", "фантастика", "дорама"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAISjGmImZFQ8--0nY1qeOEAATsKwn4vvwAC65wAAornSUjPP4qtKX2oEDoE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISjmmImenGmbtf6WisCtgfizRmtbvRAAL1nAACiudJSAL_fu_CCL1QOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISkmmImjPl3WgPTnfG_GeTgMlkJjIiAAL7nAACiudJSGDIGaQDOHaLOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISlmmImoTSBLbwRy0bTLLVXgE8n0G6AAOdAAKK50lIVd-yGaXoeFk6BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISmGmImt4vAt5YfRl7WlndM9GPee0VAAIEnQACiudJSGCaDQl4S2ymOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISmmmImyaVVxpusopYGB-uCp_a3bnfAAIKnQACiudJSCtZbP96ZuUFOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISnGmIm3qYWqR9Yiu2ibFHdCqcEjtOAAIUnQACiudJSALg9AIDS7bEOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISnmmIm9ULhAJYtMRULNuXkcjKF7NZAAIYnQACiudJSMHSV1bM-cyLOgQ",
                    },
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAISs2mIowibLLoWhiPBCsS_OC0D1FUFAAKpnQACiudJSAFCW8dep5tvOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISuGmIo3_rNVS4lw7HbghMNC7jo_ySAAKtnQACiudJSD6K0rZtDxZqOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISummIpARLkokP3B_E-CyJVzHPASNfAALbnQACiudJSA09VnaaeEltOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISvGmIpGtFgScnu-zBO-ZQt8l2BTi5AALmnQACiudJSPyR9bhzz8NTOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISvmmIpQABwaZd5IxA2XP-vx9_OReSwQADngACiudJSJYVcoKuYhzUOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISwmmIpaPbr3TJFQxw5tZ-ozFqEjFEAAIangACiudJSLWA1ckSt3_1OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISx2mIpjVN-urtm3jsKXjoe0rX9C-pAAI2ngACiudJSEqNHqHx6jt4OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAISyWmIptyC42ESM4Azcw4_xrXNRvxMAAJJngACiudJSBgQSHd9smosOgQ",
                    },
                ]
            },
            3: {
                "title" : "Сезон 3",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIS62mIrccONzfJ8VZkxa1-1fXjBseQAAKbngACiudJSDRp2FlIgfRCOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIS7WmIri-7HePIYKJUBTxkt5zs0tb5AAKkngACiudJSI21lGLkiZygOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIS72mIrqQXuNiVEcWW8CGYytiM-Hd0AAKtngACiudJSHIvDM3tq8zYOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIS9WmIrxcy_1hmpxrgwwnTX6VNkkvQAAKzngACiudJSH6z2WcD9kGQOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIS-GmIr6r0Sxq-fKOVfucRWs-NT2sUAAK9ngACiudJSBUDmk4Lr8l5OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIS-mmIsDwUjF1CvvGScWoo1XSSy6OtAALAngACiudJSOMmY2nDLIZIOgQ",
                    },
                ]
            },
        }
    },
    "007": {
        "title": "Любовь, смерть и роботы",
        "year": 2019,
        "episode_counter": "45 серий",
        "description": "В каждой серии отдельный сюжет и своя мини вселенная.",
        "poster": "AgACAgIAAxkBAAIKqml4-4ehfa2duAbRv0c0S0bOlw9VAAI5C2sbe8zIS0z2lHElrCDJAQADAgADeQADOAQ",
        "country": "США",
        "director": "Дэвид Финчер",
        "genres": ["фантастика", "мультфильм"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "title": "Преимущества Сонни",
                        "video": "BAACAgIAAxkBAAIKTml49aABLadjojcVbdMcuDZ7IrYWAALEkwACe8zAS2twv-KI9PqiOAQ",
                    },
                    {
                        "title": "Три робота",
                        "video": "BAACAgIAAxkBAAIKUGl49cPB6VY9p6eZiOC54L5fR_GbAALFkwACe8zAS7wmBRBu6kP2OAQ",
                    },
                    {
                        "title": "Свидетель",
                        "video": "BAACAgIAAxkBAAIKUml49deIyt_oLs5wOdSizNl4YlL3AALHkwACe8zAS03kYsM3GL0fOAQ",
                    },
                    {
                        "title": "Костюмы",
                        "video": "BAACAgIAAxkBAAIKVGl49ezUbTtzmuHwjGgGKZmJQGDjAALIkwACe8zAS0IRmd-Iv7RPOAQ",
                    },
                    {
                        "title": "Глотатель душ",
                        "video": "BAACAgIAAxkBAAIKVml49f1jCI1h0Dl3DG3FLXdtfhVkAALKkwACe8zAS0W5slxgVPkqOAQ",
                    },
                    {
                        "title": "Когда йогурт захватил мир",
                        "video": "BAACAgIAAxkBAAIKWGl49geEQgrNZB95UDcFpfJQfr9GAALLkwACe8zAS_eJi3cEm8C4OAQ",
                    },
                    {
                        "title": "За разломом орла",
                        "video": "BAACAgIAAxkBAAIKWml49iFCaDfa-STVzwG84RW11nvkAALOkwACe8zAS9O7S7vM6ar4OAQ",
                    },
                    {
                        "title": "Доброй охоты",
                        "video": "BAACAgIAAxkBAAIKXGl49jKZbxyOaHDfD4tGTPOBUay-AALRkwACe8zAS5H2oU8AAbLMPDgE",
                    },
                    {
                        "title": "Свалка",
                        "video": "BAACAgIAAxkBAAIKXml49kDTvsHjKvRhQjYnxU7caC68AALUkwACe8zAS1Z3bqwUcE05OAQ",
                    },
                    {
                        "title": "Оборотни",
                        "video": "BAACAgIAAxkBAAIKYGl49lqxGlFOOCB_VjQ38PdHkRwXAALXkwACe8zAS0ljEGCcfJEZOAQ",
                    },
                    {
                        "title": "Рука помощи",
                        "video": "BAACAgIAAxkBAAIKYml49mUs396Qnd3G_VeKjOrZhvZiAALYkwACe8zASxemx66VvTxvOAQ",
                    },
                    {
                        "title": "Рыбная ночь",
                        "video": "BAACAgIAAxkBAAIKZGl49pOgmjxPvZGd7DdiBxtmzUQoAALbkwACe8zAS1VGREwUdMDfOAQ",
                    },
                    {
                        "title": "Счастливая тринашка",
                        "video": "BAACAgIAAxkBAAIKZml49qabxyQnm6Rx6ND8mmo3IwuqAALdkwACe8zASwmxMPWBZ4hvOAQ",
                    },
                    {
                        "title": "Зима блю",
                        "video": "BAACAgIAAxkBAAIKaGl49rbvflp5GVgtzYAJRWGsE8RYAALfkwACe8zASw3NQuvvMgwuOAQ",
                    },
                    {
                        "title": "Слепое пятно",
                        "video": "BAACAgIAAxkBAAIKaml49sSojSdZj2ml4mXdDZ9sfjMqAALgkwACe8zAS-L9i_uVIzrnOAQ",
                    },
                    {
                        "title": "Ледниковый период",
                        "video": "BAACAgIAAxkBAAIKbGl49tC_QhzSQsuRG5EwFmeSk10bAALikwACe8zASw3P9VPiH2gLOAQ",
                    },
                    {
                        "title": "Исторические альтернативы",
                        "video": "BAACAgIAAxkBAAIKbml49tyaSXUrBaNyoW1Rb2X2Z-mZAALjkwACe8zASx3SVLpRpx9xOAQ",
                    },
                    {
                        "title": "Тайная война",
                        "video": "BAACAgIAAxkBAAIKcGl49viJmKFwrZzksJeCg4gSm2XIAAKCigACe8zISzb-ask-CwWhOAQ",
                    },
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "title": "Автоматизированная клиентская служба",
                        "video": "BAACAgIAAxkBAAIKcml49_cG8H6Rehj8Cd7i-N70PASIAAKWigACe8zISxrejB9__2YlOAQ",
                    },
                    {
                        "title": "Лед",
                        "video": "BAACAgIAAxkBAAIKdGl4-AfAp7sJStQ8LTDZEfxdM4ohAAKYigACe8zISyoINno2lbGYOAQ",
                    },
                    {
                        "title": "Звездная команда",
                        "video": "BAACAgIAAxkBAAIKdml4-BjWWf7hzARrLudW4kP9lSHoAAKZigACe8zIS-ABrEZChJfVOAQ",
                    },
                    {
                        "title": "Сноу в пустыне",
                        "video": "BAACAgIAAxkBAAIKeGl4-CfpVnkyEdNqMCQZbgxU4ghBAAKbigACe8zIS2U9gUFChSxbOAQ",
                    },
                    {
                        "title": "Высокая трава",
                        "video": "BAACAgIAAxkBAAIKeml4-DPdXpTnxetm7zYyHj2vBtAQAAKfigACe8zISxu1-rLanhc4OAQ",
                    },
                    {
                        "title": "По всему дому",
                        "video": "BAACAgIAAxkBAAIKfGl4-D2bVqbr5PzYUut7ydZL-Q24AAKgigACe8zIS-8ZITbvFBCxOAQ",
                    },
                    {
                        "title": "Бункер",
                        "video": "BAACAgIAAxkBAAIKfml4-EySkLX7v5FutJJdM2Swa5P7AAKhigACe8zISxt6qZTc8jRpOAQ",
                    },
                    {
                        "title": "Утонувший великан",
                        "video": "BAACAgIAAxkBAAIKgGl4-FoIWf94EZlGwsdLkFQJaq5lAAKiigACe8zIS6Tm1BEFbOH-OAQ",
                    },
                ]
            },
            3: {
                "title" : "Сезон 3",
                "episodes": [
                    {
                        "title": "Три робота: Стратегии выхода",
                        "video": "BAACAgIAAxkBAAIKgml4-IMZZ23ecwzHy6r7HbBPyPPIAAKkigACe8zIS51PxKXJ53-lOAQ",
                    },
                    {
                        "title": "Плохая поездка",
                        "video": "BAACAgIAAxkBAAIKhGl4-JVPmdv-znXcGB8r4UvEkWYVAAKligACe8zIS35EIWMhxR39OAQ",
                    },
                    {
                        "title": "Живой пульс машины",
                        "video": "BAACAgIAAxkBAAIKhml4-KyNXXN-wFB3XTrNIEUglM82AAKoigACe8zIS6EtN9GbmHMgOAQ",
                    },
                    {
                        "title": "Ночь мини-мертвецов",
                        "video": "BAACAgIAAxkBAAIKiGl4-LX5iGhPUfKwmMGVeuyT_JzUAAKpigACe8zIS2EJvY-s056EOAQ",
                    },
                    {
                        "title": "Убей, команда, убей",
                        "video": "BAACAgIAAxkBAAIKiml4-MeZTw7v90CdX1zAkkv2de1PAAKrigACe8zIS3v9KBuMzPNTOAQ",
                    },
                    {
                        "title": "Рой",
                        "video": "BAACAgIAAxkBAAIKjGl4-NgH93nTm92hep2K--D2fjBFAAKvigACe8zIS-5iy1IPmcsqOAQ",
                    },
                    {
                        "title": "Крысы Мейсона",
                        "video": "BAACAgIAAxkBAAIKjml4-OT0lHwuEVUhwKyZmbSE6jfRAAKwigACe8zIS9wBHwJ4WjXEOAQ",
                    },
                    {
                        "title": "Погребённые в сводчатых залах",
                        "video": "BAACAgIAAxkBAAIKkGl4-PSjNBP6pQF1ItPG9CFJREWPAAKxigACe8zIS4STi1vZ5uNBOAQ",
                    },
                    {
                        "title": "Хибаро",
                        "video": "BAACAgIAAxkBAAIKkml4-Rg2puSKVXWoQQbMHrkmxnTiAAK1igACe8zIS0_RWVT4covWOAQ",
                    },
                ]
            },
            4: {
                "title" : "Сезон 4",
                "episodes": [
                    {
                        "title": "Неудержимые",
                        "video": "BAACAgIAAxkBAAIKlGl4-Sn6kVUnlK20F3c_gy9ijC8bAAK5igACe8zIS4MwHU1SZnRNOAQ",
                    },
                    {
                        "title": "Контакт миниатюрного масштаба",
                        "video": "BAACAgIAAxkBAAIKlml4-TKPfRDVOIOiCEYtmwuhN8QuAAK6igACe8zIS30K2y8fsC5tOAQ",
                    },
                    {
                        "title": "Паучья роза",
                        "video": "BAACAgIAAxkBAAIKmGl4-UAOdULQk-CmEBBm3D0pRwEOAAK7igACe8zISy_CqTR0SNNoOAQ",
                    },
                    {
                        "title": "Четыреста мальчиков",
                        "video": "BAACAgIAAxkBAAIKmml4-U8-DSovzLs1N8FwLv0abPXRAAK9igACe8zIS4cJKg52fv0POAQ",
                    },
                    {
                        "title": "Другая большая штука",
                        "video": "BAACAgIAAxkBAAIKnGl4-Vlq_9tvfr9VfMxmQl08ERRJAAK-igACe8zIS-amSKG_uf13OAQ",
                    },
                    {
                        "title": "Голгофа",
                        "video": "BAACAgIAAxkBAAIKnml4-WZ_xjxyOOOHFbF64R62fJgpAALAigACe8zIS79D9r0lJv5iOAQ",
                    },
                    {
                        "title": "Крик тираннозавра",
                        "video": "BAACAgIAAxkBAAIKoGl4-Xmsy4ypShNTI2ucfbY8CE8oAALBigACe8zIS__E4KZeHOKmOAQ",
                    },
                    {
                        "title": "Как Зик обрёл веру",
                        "video": "BAACAgIAAxkBAAIKoml4-YqrXMMkkU3854hDKkASac-wAALCigACe8zIS_0KB-u-OyHzOAQ",
                    },
                    {
                        "title": "Умные приборы, глупые хозяева",
                        "video": "BAACAgIAAxkBAAIKpGl4-ZJYVimXkcOGdv-hnJRwLc0wAALFigACe8zISygV-wAB8e72eTgE",
                    },
                    {
                        "title": "Ибо он может красться",
                        "video": "BAACAgIAAxkBAAIKpml4-ac2ZFBqylOzYAq72FmecwHZAALHigACe8zISzFgR9IiN8IxOAQ",
                    },
                ]
            },
        }
    },
    "010": {
        "title": "Изобретая Анну",
        "year": 2022,
        "episode_counter": "9 серий",
        "description": "Анна Делви, также известная как Анна Сорокина, под видом наследницы богатой немецкой семьи проникает в высшее общество Нью-Йорка.",
        "poster": "AgACAgIAAxkBAAIFFmlyTYbeE_aciTdJTMKNxQjlzYhpAALlEmsbk1iRS7Xo4rDBJIlNAQADAgADeQADOAQ",
        "country": "США",
        "director": "Шонда Раймс",
        "genres": ["драма", "биография"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIFP2lyUgpeSIUksrlYTYIS-mUl6RTUAAIbkgACk1iRS72dqA69ayiAOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFQWlyUjkXqEJJjaBeYEs1FZDwE5N9AAIjkgACk1iRSyqASDWZkUEiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFQ2lyUl-MKlDrnRODTBJCUyk_mLIVAAIokgACk1iRS0yNnFjozF2AOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFRWlyUof4s6HGxhUkewJBiaCu8YuFAAItkgACk1iRS7QQ7B8eFnvKOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFR2lyUq8GEyb4w6TtIRpxrnysUjdVAAIzkgACk1iRS92J78PWmPxmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFSWlyUt9OBFXDGrMxl29Gs6jrMaXrAAI8kgACk1iRS6e7G7FHk9xZOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFS2lyUwQmBr5xTeXrH1k2PoRvuVKLAAJEkgACk1iRSwf07M6ZAZcyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFTWlyUzEyvghHQjiLf62OIwABaBugfwACTZIAApNYkUtceKwu6XnkIjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIFT2lyU2KqvM4CmTZ_RWoK3TIMBf6aAAJTkgACk1iRSwIQoTNZGfRIOAQ",
            },
        ]
    },
    "015": {
        "title": "Манифест",
        "year": 2018,
        "episode_counter": "62 серии",
        "description": "Пассажиры и экипаж коммерческого авиалайнера внезапно появляются после того, как более пяти лет считались погибшими. Когда самолёт приземляется в аэропорту, они узнают, что за те несколько часов, которые они побывали в небе, весь остальной мир умудрился постареть на пять лет.",
        "poster": "AgACAgIAAxkBAAIS_GmIsGSkzmdQUxV32wUwsHUmrIppAAINFmsbiudJSPcHxA-4DwFjAQADAgADeQADOgQ",
        "country": "США",
        "director": "Дэвид Фрэнкел, Ромео Тироне, Майкл Смит, Дин Уайт, Клаудия Ярми, Марисоль Торрес",
        "genres": ["мистика", "драма"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIS_mmIsjNAyy5rSTj1sTeHARStSqIFAALjngACiudJSCeieTCWiT_hOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITAAFpiLJLRrw4CqCE_B8xdU2ocIklsAAC5Z4AAornSUiDVdlgNYAO1ToE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITAmmIsl-bVJItq6tYmFZ_4VJAQjA0AALmngACiudJSIlFy2mb_FV_OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITBGmIsndj4tzCMWAkjUaRr6zThUaOAALongACiudJSAMXek8bQptaOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITBmmIso0KSSbWE04qzU18zqfxuSNQAALqngACiudJSC91bGd8e1NIOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITCGmIsqUEzlSBof37e23kKrdG28MaAALrngACiudJSOHi9gWhNh5iOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITCmmIsr293zH-u_0c_SA3nFontsTfAALsngACiudJSCIjxbW3ydfAOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITDGmIstQo3kBmiPmhtnbVZ13WiqDsAALtngACiudJSAABo285JZhlojoE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITDmmIsvDoZb5InnAxnb39Of6-7XpJAALungACiudJSKfwD2VLhDZsOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITEGmIswjzNg_q-f0Y1f6DkEgaFCQqAALvngACiudJSArKFUuUfhqyOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITEmmIsx_QG_zmfyEa5tG2AAGj2FUyHQAC8Z4AAornSUheshljQrj7tzoE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITFGmIszTo5oUdGxjba75d-1NxoGa9AAL0ngACiudJSLQcIxkx7GPIOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITFmmIs0wQE7lVsX6nnai490InjgS4AAL1ngACiudJSMxCorbW-bLGOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITGGmIs2JfT9dORDAfKXooUjDML7j7AAL3ngACiudJSOm6E26DqLjBOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITGmmIs3ttw-DkTo0TXhQgLJiMwyAfAAL8ngACiudJSGJ-TF4fV52LOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITHGmIs5OkAAFJdIiglLWKVf0zVcTz3wAC_p4AAornSUgmHpydIYrmdDoE",
                    },
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAITJ2mItXy7sRnZI50g7awNHB5UVP50AAIdnwACiudJSEE9uuPCiIAoOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITKWmItZkanNYPgt4by_IrAxIMTRMjAAIhnwACiudJSOJNehoVSZ7QOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITK2mItbTyuZ5Q8hwLRxwopOeiqUomAAIjnwACiudJSM9kni9GElesOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITLWmItdBKMZrz9HLDi7Fj9D0qWRh6AAIknwACiudJSNciOVl1XoYsOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITL2mItem3fXyiYPJkHboRRjv3pYpiAAIlnwACiudJSOgvFk93hO48OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITMWmItgWKB0npLxpwQIkwmTxi2sJ4AAImnwACiudJSEGGDc-Bz88TOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITM2mItiMkIMUGnbhKVpfBNY-WwgG9AAInnwACiudJSJ0x6-xiSw9COgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITNWmItjnfNwz-q5WkLzFdXTdtinS_AAIonwACiudJSDHfA19wnC1sOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITN2mItlL7hKmvHx9eDA0C_CYs-GtAAAIrnwACiudJSIBBx2xcR8juOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITOWmItmw5mmN_onCxbQMuq9eN79GQAAItnwACiudJSJWY-ZJ2dA3SOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITO2mItoP2VvZ2wEYRQH665c4mzgz3AAIunwACiudJSMPOpKUv-fAROgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITPWmItpxC0oZ8YFksIEIqN68CBvbyAAIznwACiudJSKYhEZImry69OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITP2mItrXXyptKIwhTotwSSrLWbemgAAI1nwACiudJSAO2N1zesXkLOgQ",
                    },
                ]
            },
            3: {
                "title" : "Сезон 3",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAITRWmIuixEun5LlZrqz6v04Z23RuXwAAJqnwACiudJSHEl9NTbB-qoOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITR2mIukzTAAE99vJ0liecllisIbKJlwACbZ8AAornSUjojYY7YEKB1ToE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITSWmIumvwlxnN-bL9_-o5k9wwBxCyAAJvnwACiudJSPUDKRytLyBnOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITS2mIuoflv2sYZCHXYu_2dbKchQlvAAJ0nwACiudJSDOh5fB6IRc1OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITTWmIuqALuBDZ2q89l7pElvDigAc0AAJ2nwACiudJSJumc92_z-dHOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITT2mIusj4FmfBY0pHLOICGGanxHpTAAJ7nwACiudJSHfKXhABn6OiOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITUWmIut8QZ7b9KrX4UCS6ZPT4W5G3AAJ-nwACiudJSObFsq12c9p8OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITU2mIuvbLcdVGqxezoeZ-xb30J0GhAAKCnwACiudJSNbAJPi4YDprOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITVWmIuwpwJbTuY0PIhMks3QQNamQpAAKFnwACiudJSOhbPp5gGpoWOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITV2mIuyVVzhd8kINCEIenkngcsEWsAAKKnwACiudJSPtSk7TIN05EOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITWWmIuzoUJg_X21omyPsfkZzjR9eRAAKNnwACiudJSEQcOAVWOru5OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITW2mIu1NpjP09tt9kfI1SW_oDDk61AAKQnwACiudJSA3-dvroRYimOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITXWmIu236w4SxqAZkG6xTrky41_ATAAKSnwACiudJSNAk1T2RZG26OgQ",
                    },
                ]
            },
            4: {
                "title" : "Сезон 4",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAITaGmIwECz2kjiy9zgzmzVliTZc3X2AALfnwACiudJSKK9rslsgmhqOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITammIwGFg7iJFuQ3HPlumyqKIKfYCAALjnwACiudJSBIIQFPnCzQeOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITbGmIwH6Nuy_jQQpuk4oeBlSlRSGHAALlnwACiudJSPwWutPhJS0vOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITbmmIwJqU89kfaHR_9sgpls5bN01UAALqnwACiudJSEaxSHMZ8wIGOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITcGmIwL4tSz5feLwJjXGskaO2byJsAALunwACiudJSA1f0iy1wqkCOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITcmmIwOJehpzkTvj4_-R7elx3ycTsAALxnwACiudJSI__7t76JdkMOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITdGmIwQK9hvErHW_wnnpMqqjLWXekAALznwACiudJSLhdWu-IhvHDOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITdmmIwSRqMvjURHZlaxeeyNVbByRpAAL1nwACiudJSEOYWLZxbRPyOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITeGmIwT7C6F8pqb5O3zV6vVAyRBI-AAL6nwACiudJSNAxb0-KkhXlOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITemmIwVv8naWShfPk_4uzSg8-WWBOAAL8nwACiudJSC1-fQc7x-z5OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITfGmIwYB--tNvkr9sBxkLA8zsX5_KAAL-nwACiudJSIUGeljDzT6VOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITfmmIwaQVbWy-DPMRxQIjARSofRnyAAOgAAKK50lIhGV8TJjax4k6BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITgGmIwcWr1KDZglM67FRC0EzHHpVbAAIBoAACiudJSPF_qtmDhgABkzoE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITgmmIweF3QRo0RME-NRIH1tpnONQ-AAIEoAACiudJSN2itlWlRV-cOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIThGmIwgFbiDgyG_E4k9eQVTZkgqCPAAIFoAACiudJSFz3ajuDdySrOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIThmmIwiCiQ_YUqPFstzr1wJgK0E9vAAIKoAACiudJSCCtM0hlrwVTOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITiGmIwj8M5ey5gCc3q1rcmkz8fuU9AAIMoAACiudJSMAoVH1tKdFfOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITimmIwlq8Ymglf2IB-vUJ6KcDk6DcAAIPoAACiudJSM8452cEyieAOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITjGmIwndzWLoIV-Vpc6S84rkis6F9AAIRoAACiudJSP4CcQn6kF-tOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAITjmmIwqa89YlqnE_6j2e_qCoIfFPDAAIToAACiudJSHBGI2GJRpZcOgQ",
                    },
                ]
            },
        }
    },
    "016": {
        "title": "Душегубы",
        "year": 2021,
        "episode_counter": "20 серий",
        "description": "Старший следователь прокуратуры Леонид Ипатьев попадает в эпицентр охоты на самых опасных маньяков Советского Союза. Его работа — не просто расследования, это противостояние со злом, прячущимся под маской добропорядочности.",
        "poster": "AgACAgIAAxkBAAIVfmmPKfntazuj9emhb5SvqaE2F7x1AAKJGGsbKTp4SP-r9HBPl-wWAQADAgADeAADOgQ",
        "country": "Россия",
        "director": "Давид Ткебучава",
        "genres": ["детектив", "криминал"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIVUGmPJsD0LsZ5vM453GlFLYAM3C8EAAKTkAACKTp4SHcqiHhdqQrzOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVUmmPJto5bB3Ezihqeap35DWdKECxAAKXkAACKTp4SAa1oMimrXXVOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVVGmPJvUO8_zp3_1JOCy-Cqil00LpAAKakAACKTp4SE6veFhp3aIOOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVVmmPJxC_xfG4S59psbLZQHFimc1MAAKfkAACKTp4SKpXvlUXk4oMOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVWGmPJ2ae7Fhw6N8uWcP0rUcl1wKBAAKskAACKTp4SP8IbwMwpQL5OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVWmmPJ38zczaQrSy9UFnG4apwjbQkAAKtkAACKTp4SN2UsG9h-cmMOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVXGmPJ5uEdXp0BfYB41Y6C34KlIOyAAKwkAACKTp4SMApeJVLzVnrOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVXmmPJ7MWIYKugYCqweODDtHtpNZ2AAKykAACKTp4SCsf65Z6exd1OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVYGmPJ8kUs4Dt0ZiTh3QgN3z004pmAAKzkAACKTp4SKiorS5OpL5POgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVYmmPJ-LBaokOL7UOgHyXxc4XywAB-AACuJAAAik6eEigjK_b3ciVFjoE",
                    },
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIVZGmPJ_ivie_Q-hf9t09Rg2ofjvqhAAK5kAACKTp4SFOkUom6N0kdOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVZmmPKBTxDR2GDQPM_CFUc2M7F5qWAAK9kAACKTp4SO8Xaorc3xJ-OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVbWmPKC_7V0Gmbn39MBW2NghpHyXqAAK-kAACKTp4SFBiXHWArxO3OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVcGmPKElGLt-YWf2G30vaZxWKxfi9AALAkAACKTp4SAABJCCgZN7I0DoE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVcmmPKGJTjmy9MOThL-xVKoDOhyPFAALCkAACKTp4SHzAtYFkgjz6OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVdGmPKHwhP5qvm_H2p9y7nXgXZ9ubAALGkAACKTp4SEPNO5xuSm-VOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVdmmPKJZ1mqAVGCpP0P3HsHofPdDnAALHkAACKTp4SKnnrUTSGBFMOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVeGmPKLDo4vdqMKL8-HPn-aTWQGnxAALJkAACKTp4SA4JKSV4KBJIOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVemmPKMlMNaJ6sg-vwfnSvB1CrXS1AALMkAACKTp4SApL5shkb9gHOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVfGmPKOM3nWdf1UogqzXiI2q8fGtIAALPkAACKTp4SMll4GKThk2dOgQ",
                    },
                ]
            },
        }
    },
    "017": {
        "title": "Пассажиры",
        "year": 2020,
        "episode_counter": "16 серий",
        "description": "Водитель необычного такси возит души до их места назначения, но чтобы добраться, им сперва нужно признаться, что держит их на Земле.",
        "poster": "AgACAgIAAxkBAAIVgGmPKwAB-6T1iURCEU3RPJhltlD9uAAClhhrGyk6eEiv5zpDX0B8_QEAAwIAA3gAAzoE",
        "country": "Россия",
        "director": "Карен Оганесян",
        "genres": ["драма", "мистика"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIVh2mPOFA1DuMzBwuJ8pS8nbdB_DibAAKLkQACKTp4SG1IRJtgUVAqOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIViWmPOHbNUMvS89JvDTMZBWwqz8CBAAKPkQACKTp4SKj5-8pI7q10OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVi2mPOJrxDXi7-zsvJ8XIVkAS1irkAAKQkQACKTp4SIFM_v6mXWSUOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVjWmPOMPqEsFCgZQePPFC-VDH4im3AAKSkQACKTp4SEmqj9togHXtOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVj2mPOOumCSEgQA7w4IR-ZkyVLMB0AAKUkQACKTp4SDKibsJexO0SOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVkWmPORGhr6eW1ULCTsdVGx2l4oKOAAKWkQACKTp4SJb9IHPgqxWbOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVk2mPOUHW6t2PePuZgbjLAccv57C3AAKakQACKTp4SJlZatUwD4khOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVlWmPOWvh5DX3L5Nl6KTffpZH4j9uAAKbkQACKTp4SINHlM9rAAFJUToE",
                    },
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIVl2mPOZ18OveXMr5BU7ENjDaMmSCyAAKckQACKTp4SJhgcVF08uCiOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVmWmPOcePyAu6cp8jYgABExr4wroNoQACnZEAAik6eEgzmVFkVxcU1ToE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVm2mPOfGYVmGSVQdZeheXfUUvJiYHAAKikQACKTp4SBuxssDuW6CuOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVnWmPOhtwgIjD03lW4fy4G7lWgfI1AAKkkQACKTp4SA-JxE6UPPxVOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVn2mPO8MZ2SAIhUYZuwN1KqlUC9YeAAK6kQACKTp4SMhaAAHZS6DzBToE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVoWmPO8OMxCVcLQ94E5zk3kfDpv6uAAK8kQACKTp4SEEQQKTSUDqEOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVommPO8N4_zeFmcEUbx5Vw3522rv4AAK9kQACKTp4SFR1EF4kyXXWOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIVoGmPO8PDhgVjTe9gyNIeatMOfeixAAK7kQACKTp4SD2eC7c0nQABqDoE",
                    },
                ]
            },
        }
    },
    "019": {
        "title": "11/22/63",
        "year": 2016,
        "episode_counter": "8 серий",
        "description": "Учитель английского языка отправляется в прошлое, чтобы предотвратить убийство Кеннеди, но в результате сильно привязывается к той жизни, которая у него появилась в ушедшей эпохе.",
        "poster": "AgACAgIAAxkBAAIFGGlyTcwlgE7naqzzu676pm6fAUWkAALmEmsbk1iRSw5XXaQ15A__AQADAgADeQADOAQ",
        "country": "США",
        "director": "Кевин Макдональд",
        "genres": ["драма", "фантастика", "детектив"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIFWWlyU_qV_qpNnrve2RGgEN4OoZT3AAJmkgACk1iRSw7mkqzCLkzfOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFW2lyVHOJX5aL15_EtBJuFdpL1aWCAAJ9kgACk1iRS2vjZz2d2sLLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFXWlyVKkuM-AOVX5R0z_90JZCEyauAAKCkgACk1iRS2bu2-edoXrpOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFX2lyVPhgGLpcwAPi-YeSe84hVhjsAAKIkgACk1iRS8QZDT2ngFXjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFYWlyVV8BqbuKieLuZBv9PrdwTdeZAAKRkgACk1iRS4llYbmjdco7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFYWlyVV8BqbuKieLuZBv9PrdwTdeZAAKRkgACk1iRS4llYbmjdco7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFY2lyVY4xPYbS0_ExsGuVZkjjy_dJAAKZkgACk1iRS7fOOIzXiYIuOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFZWlyVbY_H0TmlNb0WIVnqXiLQt4jAAKekgACk1iRS4oFfSahMtEzOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFZ2lyVeapHUXQpOwkX3lNR-Ex9HNVAAKnkgACk1iRS8ZaYJ5MOKFQOAQ",
            },
        ]
    },
    "029": {
        "title": "Великолепный век",
        "year": 2011,
        "episode_counter": "139 серий",
        "description": "Османская империя, XVI век. Девушка Александра попадает в плен к туркам и получает новое имя Хюррем. На её долю выпадает немало испытаний, а позже она становится первой официальной женой султана Сулеймана І.",
        "poster": "AgACAgIAAxkBAAIC9mlxSbmNoUJDub1c3a3lM18fNwWyAAJXDmsb3hGISwVmModBFR_XAQADAgADeQADOAQ",
        "country": "Турция",
        "director": "Дурул Тайлан и др.",
        "genres": ["драма", "мелодрама", "история"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIBfGlw5Lhjav0uOoZ59rVvU1Fb5_DvAAJPlgAC1HloSyT9FoCIwptWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBfmlw5u7RSP9IeQgu5uF2uUDf84CbAAKglgAC1HloSygJ-copBnsROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBgGlw5ww5QJWwoWo-mXfwjWE1EJU_AAKklgAC1HloS7AhME-0inwWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBgmlw5yNuCJoYPtdBrvilXyXlHWsCAAKllgAC1HloSxHuloCaOKGqOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBhGlw50oWupU-A_ZzeFjP6o2Gxmg7AAKmlgAC1HloS_TYk6uIOVenOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBhmlw52PWX5TXt8ayKTaD1E-hHlufAAKnlgAC1HloS5w33gp8Qlm9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBiGlw53NIeGBDh-S5xZQUejU_zlbUAAKplgAC1HloSyAuHscn9d43OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBimlw545TSCSrYiMaLoXm7lAcIGpgAAKslgAC1HloS4AYBSCdS-neOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBjGlw56ZZI_C1Ci1Ezh45S6vrHxWGAAKulgAC1HloS_h6mHMfqUSVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBjmlw58MIqYnY9kcNwu5z5xv0iOs0AAKxlgAC1HloSw0fTjU0dQcSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBkGlw59LIxTyW96N4kTRo_8uGjRhjAAL0lgAC1HloSw4_noMNvAIyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBkmlw59_ralL7VDNqJZLN0ipCa15wAAL3lgAC1HloS_E0pdj-1_skOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBlGlw5_MpyqUPetAgeq2AX8i2ROT1AAL4lgAC1HloS_XLkt4IYodwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBlmlw6AAB-huXtmo0-TID0-VYTE8XLAACApcAAtR5aEsxqo9Jqpwy7zgE",
            },
            {
                "video": "BAACAgIAAxkBAAIBmGlw6A59ix522hCqqGo__Acy8vSwAAL5lgAC1HloSzap2A_N-DQZOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBmmlw6BxS6cKknJVJo7hQrFnefAOrAAIGlwAC1HloSzEsS-hNOXMVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBnGlw6C57bDhDIH__vKgz7-xnEScbAAIHlwAC1HloSzj4U44YyGAHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBnmlw6GCaJLcBwvaiHcoWIxzmjV0lAAI1kwACxdNpSxNJ8aHiyFxmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBoGlw6IoAAW-KCSUKMhRafQpPAiiaDgACP5MAAsXTaUud0eWXxxiqiTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIBomlw6Jb2X7uPriUxxcVjhv5Ah1OdAAJOkQACxdNxSykHY-azQuFEOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBpGlw6KjuRTbbRanM2CmL4LKV8kJDAAKflAACxdNxS9MwZBVT3PHCOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBpmlw6LYhCYpqkzCH2RFj2ZmcyLRgAAKrlAACxdNxS6k2TDelSIXiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBqGlw6MXcFllFOVWGZ3N6-NB1I_sfAAJTlgACxdNxS8Mo3N2KKZtaOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBqmlw6NauLDb7hPq60uudPULQn6JlAAJ1lgACxdNxS8EYNTW5gt8EOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBrGlw6O56N34MgklcB1m8fZeZ6VW8AAIllwACxdNxS4N8GNim5-hYOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBsGlw6We-eJPxZHHAAtufPILG26GtAAIylwACxdNxSx_RF1dYFCtLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBsmlw6XSyKDlpHHAmYO4hq1S7WYLjAAJ5lwACxdNxS8systZS1KRROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIBtGlw6YKHiVsjBY_akovseFz8JNM7AAL_jgACxdN5S8-1FwABZrq_uzgE",
            },
            {
                "video": "BAACAgIAAxkBAAIB9Glw9hC0_UyQih3OTix2ko3MbulpAAK5kwACONKIS858C-z8QQ5WOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB9mlw9jGj3lIt6J8k8P0hGOKVej1hAALakwACONKIS9ldjKr2qg1bOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB-Glw9j2Qu_KpfkX1I74Nsrqn2lzcAALokwACONKIS8N_bR1PinavOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB-2lw9lC_CbuyySIzd1Gi3jX4edjkAAL3kwACONKIS9zWvNduAdU_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB_Wlw9mWXtx1Gb-qt3S-EsTiQljMDAAITlAACONKIS4m9JpR6kjY0OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIB_2lw9nI5qKpUvpIAARj65VFBi_ObaAACJ5QAAjjSiEskvT3WE56gUDgE",
            },
            {
                "video": "BAACAgIAAxkBAAICAWlw9oEg4-YJDqpVV3YQbVF-HohTAAIylAACONKIS7HYAnzPent7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICA2lw9ov3CPcW9JD58zkH2bNoQw5ZAAI-lAACONKIS2m4IrYvqRgWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICBWlw9p3WuYpLBOQRvSV80JgGjLAqAAJLlAACONKIS9FFE64VMRB8OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICB2lw9s2971OUiLJZe2In4QRWr1UwAAJWlAACONKIS7x3-A5BwMg7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICCWlw9voAAalrXPj7o0sglnZUHyWJQwAC0ZQAAjjSiEvmffpanBtUHjgE",
            },
            {
                "video": "BAACAgIAAxkBAAICC2lw9wfGFlGN7ENBdXKn3q-iX3JEAALelAACONKIS-yW8h349M1sOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICDWlw-CaLWp5Wvthn5FGnSm6y1A16AAI4mQACONKIS_3zpK27VC3UOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICD2lw-DiCUUK9aiFoVCnDrVBbfYlZAAJNmQACONKISzRR9dtoYFhZOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICEWlw-GL_ZGPpQUOHL9dVN4iWk01JAAKCmQACONKIS70M5msLYGSwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICJ2lw-jz43-spcujjKPFUhknyJR0OAAKbmQACONKIS1fGc7Xviv7-OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICKWlw-kq84D_LoA6FUNXWb_M2smRpAALKmQACONKISyGdbsf720lUOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIClWlxBh4Hc6v5G82AY3DhHXwbAl14AALkmQACONKISwYYoH5I_oWGOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICmGlxBmtbfDgHzEPmSN8wazV_peZ4AAL5mQACONKISzu1Rcq_-8u3OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICmmlxBnk1ij_ch9K92O7e4AtFFLZFAAIKmgACONKISx8UlmTCTh3YOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICnGlxBoe8g6pMfq-BMMV4FTQabQPQAAIamgACONKIS3WPRBaLgJAdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICnmlxBpVI391iekanEXL7a-ZEWVhdAAIvmgACONKIS719ywoIKsYbOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICoGlxBqAgceQ2LSuPtAzpLxFia9ZYAAJFmgACONKIS_Ifr6qgoKlgOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIComlxBqvvJqsCNxkEQ0vwx09hzXo0AAJymgACONKISz_-8qkJKQ7UOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICpGlxBrjTYxAwKwSxscvx9vhlRLrnAAKDmgACONKIS8fcqgG-D5AvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICpmlxBsORnyGqB88DW8pnQMKAdLfrAAKRmgACONKIS_9_jwdha1L5OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICqGlxBtccn1QKdnQAAe1gGeSevQAB0aQAArOaAAI40ohLSWgFowqLjPo4BA",
            },
            {
                "video": "BAACAgIAAxkBAAICqmlxBuVWxcLBpZFzPKbSfjOh0dpFAALgmgACONKIS0ytrnSv93cQOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICrGlxBvHuYchq4NQCh2utm6p_SvRbAAJ3kgACONKASzLkvykqReWiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC3GlxDdnlORplNEmg4FdLZK_JyP1kAAIvmwACONKIS4TchapaBxGjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC32lxED6S1WwapgifHSLclIjzwvOOAAJbmwACONKIS0LxOJ_go7R0OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC4WlxEE1XVraGQ5bQkasYczJQq7pNAAJzmwACONKISxPFVDvfnnFxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC42lxEFn4372dp8h7q0Sn5OVHXwndAAKEmwACONKIS5HswGIi4I_KOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC5WlxEGWSDjXfZkB4_h1MClP2EWmyAAKUmwACONKIS9Mvokr-XmYBOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIC52lxEHrYHdUXpcdINUWXzh-uxNwqAAKnmwACONKIS8HqCrJs9J7WOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIWF2mSBIfsHYjlp7yQeKj48bL04f7CAAItkAACT_54StgO2s9EqO--OgQ",
            },
            {
                "video": "BAACAgIAAxkBAAIWGWmSBOnQBddN9n8_0CeHqhb_7DAVAAKliwACc3HoSm2fAcLQPtr2OgQ",
            },
            {
                "video": "BAACAgIAAxkBAAID-mlyA5VHoCRnBAvYVN5ns9i68IgcAALmmwACONKISyWgBtKKVKDQOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAID_GlyA6FbcpTHfrZR6BIV7UVwvn5TAAL6mwACONKISxzvqtiLXUADOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAID_mlyA6wLPP73ydsVCObkfRXTwhZaAAILnAACONKIS9fe4_hT8i7jOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEAAFpcgO3hTF8uwZ3_ICMqN9Kr8jKJQACMZwAAjjSiEsyyNgnzJg6KzgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEAmlyA8IAAWR8ydCkTEqRe_rLw0Fv8gACS5wAAjjSiEsN0tsJp1pdMjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEBGlyA87MCExB81XjDVKABupaqEUDAAJ0nAACONKIS9t_zObO6NlbOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEBmlyA9gkmU_nmQgTdPwsjk0VHiL3AAKTnAACONKIS5WYq97PNpAjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIECGlyA-eZ0wcoElRdZnKnRRBH0FSbAAIangACONKISz-Kowt5ERJkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIECmlyA_U-qP5gDWItXmaMHHq6AAFvygACy58AAjjSiEthJxVIOYDmmzgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEDGlyBAJ3j7Vs5XuyonvWJDu8StgCAALQnwACONKISzHrGX0GivnwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEDmlyBBCmrUgi-w6TpD4a8aivBSFCAALpnwACONKISz-hIxLokeD_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEEGlyBB_LlQo6FGBefApTevL7XweOAAIQigACTp-RS1o1AXgWX6wfOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEEmlyBC5QIfWKyJIwjBF0CYxtbMAdAAIqigACTp-RS_SeLGfntiMtOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEFGlyBDpmVIjvF6YM00aLHvWgjnk2AALunwACONKIS2xHMJHI_oMnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEFmlyBEqTNltMzTCs1t9Jr4zwAAGhKwAC758AAjjSiEuZxcZHOR_PojgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEGGlyBFQDSmAAAdQzz3l6edZiyss1zgAC8Z8AAjjSiEtTR2XuRlFfkTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEGmlyBF-y3Uh2EuCVZqQpSLpv81mmAALynwACONKIS5V3cEFaTRLVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEHWlyBG4ehbYnzAtOKEsMCMqBqfSBAALznwACONKIS6s-W_8-l4thOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEH2lyBHmsWrroLCbyMAkYVZXgce2BAAJAigACTp-RSx4c_12PdW-9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEIWlyBIM9ol64T6WS7kJXF_Pb-QqMAAICigACTp-RSwwmJhtqURbrOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEI2lyBJCeOSIhJlzFmLoTy87pxdJ6AAJdigACTp-RS9y-vZex-QLYOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEJWlyBMfG5qbivsZgfwdkeYUTSJM4AAJligACTp-RS1MqUYhZw1IxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEJ2lyBNIZPNOHNL6sVsqMumUv6ii-AAJsigACTp-RS4y9jMqYTRZROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEKWlyBN4yY1k4L2GhCTMClpGhmkCKAAJ3igACTp-RSwtf9FpkPv3sOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEK2lyBOmzOx7KMPvX0d5v_bwZ7JkGAAJ_igACTp-RS39e06I8cdETOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIELWlyBPRuTU4Qq9FbYtkxz8Y-s1rfAAKHigACTp-RSznQAwWiWAhSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEL2lyBP7YDhiKV1-q7kwT-4mRbDSHAAKRigACTp-RSyVBB1mktixjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEMWlyBRLHgpohHRqBG9BQXlKsTD_3AAKeigACTp-RS_418qF8hM-qOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEM2lyBR3D0mh0sFU4IppvXkTk0psmAAKligACTp-RS-HGtANqQVd2OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIENWlyBSpVj2M8rr9AZSe7R4SZi0L0AAK7igACTp-RS1goMhdQVcw_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEN2lyBTS94LUES6yoLDDRSXm5o6N7AALHigACTp-RS3zt5bBo_r4KOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEOWlyBVIEeG_XLNMvVHTIQFor30KdAALPigACTp-RS4kISnxU5Xq1OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEO2lyBWC4nXz47yovgYAqiV7s8ANeAALVigACTp-RS38GiSrIudJJOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEPWlyBWonWPQdGKQGd6RXavIFtD7YAALeigACTp-RS2zjGbl0yCzqOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEP2lyBXNMmSt7MjL7icEuThytcogzAALjigACTp-RS95qhX15_oYPOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEQWlyBXxsBVrT8hk64P8brd6U1konAALuigACTp-RS5mzfCw6xLs6OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEQ2lyBYX5qJkY3-58nvIVp92CAq39AAICiwACTp-RS1aRnkNr_-HkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIERWlyBY8O8vXAaGN2v6-Ivtbn5K0lAAIYiwACTp-RSwrlh4_ewOWnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIER2lyBaTdlGPjuHjBkUFyutjekjxQAAIjiwACTp-RS1uTlkKuJMqmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIESWlyBa4Es3kDDhmd6Xy1Jz2zoIzhAAItiwACTp-RS1yWuMsNCFCjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIES2lyBblFLpq7_GFMaTW0BtRFGlkWAAJKiwACTp-RS0uTHRwZeqn_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIETWlyBcxvwfoOQXnxYrY0XN8gSOsvAAJTiwACTp-RS0_SvI_k8BeyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIET2lyBdb9apapM4AQ142k5lTisaYEAAJciwACTp-RSxNdrdI-dc1JOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEUWlyBeAqhknaN06DtvOEmt5wqh9IAAJriwACTp-RSxipibdFnP5tOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEU2lyBeoYPQp8hJfE02yGwSYKPcWMAAIzjAACTp-RS_rGovo5pcQEOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEVWlyBfURnbd9ztirD2ccIhtyWmJhAAJFjAACTp-RS0fNMDokg8rXOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEgGlyPzT_V5umGhERFvjTxayuQxdGAAJkjAACTp-RSypD81HmYYbWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEgmlyP0NfAafwX_kunydUqFIemqMDAAKRjAACTp-RS_IhwRWAdLDJOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEhGlyP0939lx6cogPLrFU-1bNdzZuAAKijAACTp-RS2CHvLKfMd47OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEhmlyP17AIPyWm6WEvgwuc9wnjf8cAAKbjQACTp-RS1raFejsDiVNOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEiWlyP2lz0gOvdBaTFf7EUthiEMdsAAKkjQACTp-RSw6Dhqvmhd83OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEi2lyP3VmJJHIvfthNTdFiP9XoLNLAAK3jQACTp-RS4ZLlYMiXOViOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEjWlyP4FDaTC3Xbd0ZrYEWUT3czRGAALTjQACTp-RS33FydLJPQpHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEj2lyP46sFV6N2uZZQmIi6EnE6Qm9AALfjQACTp-RS4cvugABJUTvKDgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEkWlyP5id9E2var26kC06Mjy9OpAyAAIFjgACTp-RS38nHBHHWEtLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEk2lyP6V49jG9aEVo6fd8wEbivvCEAAIcjgACTp-RS4goHeMdoqmIOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIElWlyP7LKj5EI5FcXitU1BfnLFT5xAAIyjgACTp-RS98lqVGlImFHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEl2lyP8D9dD8JL8WcDoRGk-jBi4P6AAJHjgACTp-RS463UEW8md67OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEmWlyP8w_t4Lqmy5OS5P5cct_HrXnAAJPjgACTp-RS9LSN83ohsMdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIEm2lyP9gAARtYXARabryrUFTP-aV1LAACE5EAAk6fkUvswKnX0jXEhTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIEnWlyP-UX4Aut_B5RCcmoG-DFmXAhAAJikAACTp-RSz-UIv8p9zbWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFGmlyTu6ZgVEEqRVgmvHK9SRo-CrLAAItkQACTp-RS96sF7My6_1bOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFHGlyTvyI9PBYMVAjatk5PaN24bDsAAJIkQACTp-RS3-5-625VVWWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFHmlyTwVNv5VOT2o1GuBJuCht6sA3AAJXkQACTp-RS6RZm5z3niyFOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFIGlyTxGgCMDkZ-Lnt8I4xSjBw-pnAAJlkQACTp-RS4wy_1gvB42nOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFImlyTxwNwWO0guLA9Mf9EfQH6ziwAAKlkQACTp-RS_azRWPRNFKhOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFJGlyTyakeo2ehNMDAag0h3aboPqRAALEkQACTp-RSw4Ju_u1-xahOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFJmlyTzvxmC_ArahbH-CeQyDzN9UoAALlkQACTp-RSyOBSiOnGVOxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFKGlyT0VGt6uvUOmhmhp6l1uGshg0AAIBkgACTp-RS0G4ic1y3JTHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFK2lyUB3EngVEBeXBHa6aJL6xo1P7AAIZkgACTp-RSwmaNhtAS94IOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFLWlyUEOfGcdg8JJzKXwF_EFE31PMAAIykgACTp-RS8SLNdD6x4vvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFL2lyUGWuwHcCp5SiwbSLQux78FA_AAJYkgACTp-RS0GAasbFNF1JOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFMWlyUHLrwpZ33yJZL7-NLIWWxAWmAAJ9kgACTp-RS0cO92vNgWACOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFUWlyU3Sy0sqMvQABWDYoIqKpB79-wgACpZIAAk6fkUsyUFukoxVlhDgE",
            },
            
        ]
    },
    "030": {
        "title": "Великолепный век: империя Кёсем",
        "year": 2015,
        "episode_counter": "большинство серий длинные, у нас 88 серий",
        "description": "Спин-офф культового телесериала «Великолепный век». Сериал повествует о жизни Кёсем-султан — одной из самых известных и могущественных представительниц Османской империи.",
        "poster": "AgACAgIAAxkBAAIC-WlxTAR60GoMKlhimBdX4ZDy70X0AAJvDmsb3hGIS2HvCMOEpTeSAQADAgADeQADOAQ",
        "country": "Турция",
        "director": "Дурул Тайлан и др.",
        "genres": ["драма", "мелодрама", "история"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAICE2lw-YhK9daN1o72jPxkG-tpuk1oAAJtlgAC1HloS4knn4OmythdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICFWlw-Z8c5ML4SaXhMJsUdg6SiO41AAJ0lgAC1HloS3IzYxypqlNHOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICF2lw-bJeEmp6uJNhsI22vQfe-M3qAAJ6lgAC1HloSybBEVdzNrIdOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICGWlw-b-FBNyQ0mtp8_vIum4LEyo_AAJ-lgAC1HloS-NrqHQ3__64OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICG2lw-coXcKqnfHRxHoQxbsfehxCuAAKIlgAC1HloS_RxG0dxmJsyOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICHWlw-dYHa2y6lkmg0UJrJEVM3Ys7AAKJlgAC1HloS4twfPthUM_NOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICH2lw-e7yXQXGNV0ee3DILwiblSnMAAKUlgAC1HloS72meeyooNjDOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICIWlw-fv2lR30T-SvRk5usgeIfE12AAKXlgAC1HloS2BT_p0hd44EOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICI2lw-g7TrxYH-ZSEPriduG0mjyWfAAKZlgAC1HloS2MZ6UCgcIePOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAICJWlw-hm_VsJdPNbZpV23Z7fEudZpAAKflgAC1HloS6fiy6_fOX8GOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFM2lyUIzVHPBfOjzWiUh8AwNFNCmmAAL4kQACmliQS9E3Wqe5RgrNOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFNWlyUJed-vYFYUiwkBDXgzasNz3tAAL_kQACmliQS2IAAQiEiCfTCjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIFN2lyULoE83lSE4PEP8ayx2Ny7-YhAAKhkgACmliQSymNMngrUC-LOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFOWlyUMTjsgGU4TPhi6UQ_k3ly3XdAALlkgACmliQS-pHvBIICVrvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFO2lyUNPoBi7iCMD-VPfgwrvV4XHXAALvkgACmliQS7Ku10bMbiQiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFPWlyUOhFTU7Qfjo5eiKF0unruD3hAAK7kgACmliQS0L1drHnuVb9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFU2lyU4t5Yexgzyp-E5JFwYpVsT7LAAIRkwACmliQSzo0tpWi9twFOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFVWlyU5127E9I6smdAykGowjgAQUTAAIakwACmliQSwS1AAGQCTLJ_TgE",
            },
            {
                "video": "BAACAgIAAxkBAAIFV2lyU6vE7Gg4Zk5NnSY811drXMbbAAJPkwACmliQS4Qwp8TFe6loOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFcWlyWS8ONDplLoUSOqv5bLvqTXQQAALzkgACTp-RSx9fB0evHghjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFc2lyWVDuqu3AxESFdwRyIKLNzHKfAAIkkwACTp-RS_ooLgZpfNmkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIFd2lyWlI_HEqbjFSHp5GI5jqWB45fAAJCkwACTp-RS6NIku6_Hkh7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGOWlynQ0aGUAjQ_3HYwIx-RQhd9-fAAJ2lAACTp-RS-3VZK47dBMcOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGO2lynuISlPBdErDvgI4exsCuGzxbAAJ6lAACTp-RSyi3-8uXnqW8OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGPWlynvTlKBUXSGz3N5o12yOf8l3vAAKFlAACTp-RS5t19wM9qn4GOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGP2lynxtbMa69kFRHl2tvR_WpRlvoAAKhlAACTp-RS__isoG-LAjjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGQWlynyn_KEPZsu_AXNfMeQ53x_8dAAIllQACOr-RS4jypnCta1ctOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGQ2lynzbk7vrvOCUBYcCTqbRJW44_AAJAlQACOr-RS_Fn0JshOxK1OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGRWlyn0HbdV-Sk9p19GJsSg2Y4_9xAAIHhwACyu0pSI0d6OuGF-cOOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGR2lyn5-Fp6ExTDEpNpAsij0D6yyqAAJnlQACOr-RS69rNbBAA1M4OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGSWlyn6r6lEr6SKHy3i1LiE4LIyQBAAKJlQACOr-RS7ohmFb_MhnvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGS2lyn7e3uzTnWPQqk4-xiZeVhbjYAAKalQACOr-RS7m_EgFsKoUxOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGTWlyn8PpQf2O076XJHy4TumveJTlAAK2lQACOr-RS7IHW-Sp8PiWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGT2lyn87VIPi_5gJHP3kD6UWOxCUKAAL6lQACOr-RSxqOYs4faQpVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGUWlyn9iWLYwtLLWbAkly8rHyYQPDAAISlgACOr-RS9ZHNpSkgC7bOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGU2lyn-MhrOmhw__zfP3H5TQ3VfHQAAIflgACOr-RS3lWdJZoxCAqOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGVWlyn-4zXt-QBHqLpSqbXA226Z4NAAK1hQACCIDYShObRUvJ-jgzOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGV2lyoBqUE68JA5zLt29oLBcwCigbAAIjlgACOr-RS4ZZVjCHfeRiOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGWWlyoFMZ33SBbqablhc8kY6Ks-BgAAIolgACOr-RSyr835fG3HTtOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGW2lyoGB8bYgy6g1rEGFULRr84wiuAAItlgACOr-RS2Q4wOiePoovOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGXWlyoGqkuJn3SM51FZ9v_YGpnGuxAAIxlgACOr-RS7onbK-r6dPROAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGX2lyoJndoXUukzRxjwNRN3emElrTAAJNlgACOr-RS-1KIuoEz-LnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGYWlyoKnKLk6mQ9Mj9chavLpq3A7nAAJelgACOr-RSzXVgLAq1bkuOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGY2lyoLMDHWxEnUkNg8GOEIvaPNy4AAJnlgACOr-RSz2430A7z988OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGZWlyoMp-FLAiqYnq2Fko_XEeAfrcAAJtlgACOr-RS9OY6-OQdOUvOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGZ2lyoOQXMJoHUZNHosZXsE-fJuR3AAKElgACOr-RS2YZ5_b1Bt7kOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGaWlyoO7aE9vcA-v3AmAfRYFS3yQhAAKelgACOr-RS3YoRgN1EpkaOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGa2lyoPmpilNv1525US7GSxOm37v9AAKwlgACOr-RS5o2Mcx6GwwzOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGbWlyoQKvnkDcqMbnpewAAV9IhmEizAACv5YAAjq_kUtwWWh_RhQUQjgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGb2lyoQ4xKtKFSUSRNZl4Ld_-sayGAALRlgACOr-RS-6qZe8KPNJSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGcWlyoR3mXZhpBDFPbT9C9PGgkKrzAALplgACOr-RS--_g8rtSFQQOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGc2lyoSjzXGAMRxzMkzyhZSGow5c8AALxlgACOr-RS2y1lb1-oHhCOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGdWlyoTPeYTvBbIlYAel_oyCa7JJXAAKolQACTp-RS5Y0j2qBzFa2OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGd2lyoT022uvZeEJ_j2sGM1iBm-QYAAKulQACTp-RS8OyVV2EXzXnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGeWlyoUj8tu3bzthUZdgFIeqS2Om0AAKxlQACTp-RSzIh1dW8IHNWOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGe2lyoVLROa7Wjl39Fbgh7xjhryj-AAL7lgACOr-RS9joX2QStCgOOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGfWlyoVqUKHV3ktNok_1Qkb7QPZazAAIDlwACOr-RS-OPVjQuS-aLOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGf2lyoWVy8cqGYKQlmZ3p9gtmvgF0AALAlQACTp-RS9b--GpWCdO3OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGgWlyoW4e8FlrmO3PtmIU-GnXg3DEAALtlQACTp-RS4nEcpipoSbaOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGg2lyoXgP4N5GlZLjC25C5OWxMmYCAAOWAAJOn5FL3ZWI2xVCmwQ4BA",
            },
            {
                "video": "BAACAgIAAxkBAAIGhWlyoZAP91DmCu0oFXmpgdniQyuYAAIQlgACTp-RS_eMzVbbxV_XOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGh2lyoazYfMAtkeIkQ35S2ewf_qa4AAIUlwACOr-RS-oLZAABFV5RyTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGiWlyocD0pZowXRyWGBNwS2DMhUVJAAIjlwACOr-RS0pfmSiEpw7eOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGi2lyocrRnlMf6wGuk5zK5zG6ZEF9AALSmgACEU9hSa5YBaZL7UUwOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGjWlyoegP6j87LqrFWctUIQtOn8C7AAIrlwACOr-RS9Cn81H9_38zOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGj2lyofJf77nvUQm70e2u7t13Ttl0AAI0lgACTp-RS2vFUut4hqNVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGkWlyofyIvxzrnucppnJ0t8jO-pq1AAIilgACTp-RSzRGh8yWd4eNOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGk2lyogR2ZHDZL2_9yZcStBwEXdGjAAI2lwACOr-RS87_Pxh4wVU7OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGlWlyogsTyLBjdnTIM3clMdL0ioMPAAI3lwACOr-RS8S0vJePZr8QOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGl2lyohL7uXr_1BmcZP0xSGrH_4iXAAI5lwACOr-RS8cO2GfasfhtOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGmWlyoiSO641TYSTlPSvUacTi_EcTAAIblgACTp-RS1496IUuZRw_OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGm2lyojD1cjW1JeLYeY0_fdkHjMPlAAI-lgACTp-RS0ThbyJfAAH80DgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGnWlyolRAjbQkQe8ZmRkrEmufXo_EAAJOlgACTp-RSxnDcvvgvwGkOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGn2lyomBEutPzBgsEaX4BCT8TBhs7AAJelgACTp-RS0dmgznnZBTTOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGoWlyomyiosZZe_E8OhhOQDOww2pYAAJglgACTp-RS7iY_z3ls1ITOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGo2lyonpEd0ls5D2bh2SbK8XG79AFAAI9lwACOr-RS3dSH5vS3gEmOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGpWlyooOpiD65ENMxdfP9_aILoKPMAAJ7lgACTp-RS5LEorMEv5m1OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGp2lyooxwDjtEE2jUOn1tCiXhgRIjAAKElgACTp-RS-xwY76HQ_O9OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGqWlyopUH5a3sQNCSNE5dvkdB51i3AAKilgACTp-RSzSJSrV73r52OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGq2lyop2o37UgthQiRrRj7rrBLMA-AAKolgACTp-RSxCxXPbzr6lGOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGrWlyoqUSuhV823lUiIAUgx4AAfp3BAACR5cAAjq_kUth36_xroqEJTgE",
            },
            {
                "video": "BAACAgIAAxkBAAIGr2lyoq6GEbcr3RkDbt1Cv0D1tw5RAALClgACTp-RS6TOIE5eUMEfOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGsWlyorbQHY8QfrPTu0yaergSA6zoAALNlgACTp-RS7rRre7vzwTjOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGs2lyosE6jcBk0UixQlSNBOm-VwcRAALmlgACTp-RS6hQt4kyrWJnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGtWlyosxY59x_0obbaysQiOhExiaUAALslgACTp-RSzr3vPlsmpRFOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGt2lyotkPl0K4V1-fyVX9ZUUo0ceuAAI_lwACOr-RSxV4K0FJpqRSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGuWlyoubXZO_nMP_Sqs1pzB3UWdJEAALulgACTp-RS0P3iQZ9GRoSOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIGu2lyovBtPaQTGKswBpUnlXE4v9bsAALylgACTp-RS65EGkn9Pu28OAQ",
            },
        ]
    },
    "057": {
        "title": "Леди-баг и супер-кот",
        "year": 2015,
        "episode_counter": "онгоинг",
        "description": "С виду обычные старшеклассники Эдриан и Маринетт при малейшей угрозе Парижу становятся Леди Баг и Супер-котом. Их миссия — захватить акум (тёмных бабочек), которые превращают людей в суперзлодеев. Когда супергерои объединяются, оба не знают истинной личности другого. Маринетт не знает, что Супер-кот на самом деле Эдриан — парень, в которого она тайно влюблена, а Эдриан, чьё сердце бьётся ради Леди Баг, не знает, что под маской супергероини скрывается милая и ветреная одноклассница.",
        "poster": "AgACAgIAAxkBAAIMfWmAwIVTrgbSw1pOM45l2xz8iiosAAJ9C2sb3m0ISP_GjKaUE7RVAQADAgADeAADOAQ",
        "country": "Франция",
        "director": "Томас Астрюк",
        "genres": ["мультфильм", "фантастика", "семейный"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "title": "Непогода",
                        "video": "BAACAgIAAxkBAAIMf2mAxiLDacrsbUWQM14owvU28AuNAAONAALebQhIGkLQiQTUPts4BA",
                    },
                    {
                        "title": "Злолюстратор",
                        "video": "BAACAgIAAxkBAAIMgWmAxl7P2CYLyWP5OW3x5Yjk68kBAAIJjQAC3m0ISGyKqp5ZrncCOAQ",
                    },
                    {
                        "title": "Леди Вай-Фай",
                        "video": "BAACAgIAAxkBAAIMg2mAxr5ETKLDk4K0WyqtLv95ckvUAAISjQAC3m0ISIYPg73pdCpyOAQ",
                    },
                    {
                        "title": "Принцесса ароматов",
                        "video": "BAACAgIAAxkBAAIMhWmAxvYakziO9RdzSZdqTMxvkt7hAAIYjQAC3m0ISIXbHXreJNWeOAQ",
                    },
                    {
                        "title": "Злой купидон",
                        "video": "BAACAgIAAxkBAAIMh2mAxz0JFFV1ZEI_t1fWttTWyTnUAAIcjQAC3m0ISAmg8ehgYMoxOAQ",
                    },
                    {
                        "title": "Месье Голубь",
                        "video": "BAACAgIAAxkBAAIMiWmAx47eajVj1w_55PyDCv9by530AAIhjQAC3m0ISL4AAdLRfCFDqTgE",
                    },
                    {
                        "title": "Пикселятор",
                        "video": "BAACAgIAAxkBAAIMi2mAx8aJKh9D410uy5a2ioDeZQKlAAImjQAC3m0ISIu6KidxHxgeOAQ",
                    },
                    {
                        "title": "Двойник",
                        "video": "BAACAgIAAxkBAAIMjWmAx_xBIS3zotxFzXXEmTyUCyFRAAIsjQAC3m0ISHkVoB_sBlnwOAQ",
                    },
                    {
                        "title": "Пузырь",
                        "video": "BAACAgIAAxkBAAIMj2mAyFfJEIpZrxMngbeaTcwWHWoHAAI5jQAC3m0ISIolEnRLKOmIOAQ",
                    },
                    {
                        "title": "Гипнотизёр",
                        "video": "BAACAgIAAxkBAAIMkWmAyJbCCvkk60vT3X6_aQvTm9TyAAJBjQAC3m0ISPLUvHrWnIdpOAQ",
                    },
                    {
                        "title": "Роджер-коп",
                        "video": "BAACAgIAAxkBAAIMk2mAyNmdyxnGBJ3N3rd9XsiN5LjaAAJJjQAC3m0ISBSrfUAefydiOAQ",
                    },
                    {
                        "title": "Игрок",
                        "video": "BAACAgIAAxkBAAIMlWmAyRGiqMmowY0Lalr47hT1DJ5pAAJPjQAC3m0ISFDWgl_z4ZCnOAQ",
                    },
                    {
                        "title": "Зверочеловек",
                        "video": "BAACAgIAAxkBAAIMs2mAzeg73n9kilj3kYfC9UyYmAmgAALDjQAC3m0ISDuyT-gkMRjPOAQ",
                    },
                    {
                        "title": "Тёмный рыцарь",
                        "video": "BAACAgIAAxkBAAIMl2mAyZjRn35sXDGsDM5AplWMNW5mAAJZjQAC3m0ISKdRkAtTrrj9OAQ",
                    },
                    {
                        "title": "Фараон",
                        "video": "BAACAgIAAxkBAAIMmWmAydaj1r6pfYuFk7bEifZHHIsyAAJijQAC3m0ISHKMKpdrvxdhOAQ",
                    },
                    {
                        "title": "Повелительница времени",
                        "video": "BAACAgIAAxkBAAIMm2mAyhaF393--d245_lKuhjl2XQDAAJljQAC3m0ISHzHBFxDR9oZOAQ",
                    },
                    {
                        "title": "Страшила",
                        "video": "BAACAgIAAxkBAAIMnWmAylG39RJF6fcnSs2vE4NXLT4fAAJujQAC3m0ISCl56FUVoZ68OAQ",
                    },
                    {
                        "title": "Кукловод",
                        "video": "BAACAgIAAxkBAAIMoWmAyqZP4oio9cHvHGFWwgQ5CM8_AAJ1jQAC3m0ISOorihYeq8SvOAQ",
                    },
                    {
                        "title": "Мим",
                        "video": "BAACAgIAAxkBAAIMo2mAyt_QWyWDidPnNlXWVuzcKOuBAAJ7jQAC3m0ISM3JFIrrWQLSOAQ",
                    },
                    {
                        "title": "Злодей-гитарист",
                        "video": "BAACAgIAAxkBAAIMpWmAyx-NMpHt9BFt4Da5mBp49E_1AAKBjQAC3m0ISDbOWnPhrQqWOAQ",
                    },
                    {
                        "title": "Рефлекта",
                        "video": "BAACAgIAAxkBAAIMp2mAy1wEB3UrM27NxW3ukbeDT2twAAKEjQAC3m0ISFJf3ttwOzT5OAQ",
                    },
                    {
                        "title": "Каменное сердце, часть 1",
                        "video": "BAACAgIAAxkBAAIMqWmAy7Pd-El4TiZusMpVNvMQp6BgAAKRjQAC3m0ISKeYCxv_edJZOAQ",
                    },
                    {
                        "title": "Каменное сердце, часть 2",
                        "video": "BAACAgIAAxkBAAIMq2mAzRHw09uitKwNag9iKVIzRRUhAAKvjQAC3m0ISHnm5rB63g18OAQ",
                    },
                    {
                        "title": "АнтиБаг",
                        "video": "BAACAgIAAxkBAAIMrWmAzUY7ja7yMbnABRDv__g0EDHpAAK1jQAC3m0ISOfeUmSaZG5oOAQ",
                    },
                    {
                        "title": "Кунг-Фуд",
                        "video": "BAACAgIAAxkBAAIMr2mAzXrMvzKzCxIUmRdo8CTGSfIfAAK4jQAC3m0ISIVtEKFFivUpOAQ",
                    },
                    {
                        "title": "Вольпина",
                        "video": "BAACAgIAAxkBAAIMsWmAzbB60nWX3H-Td915yh3lQmi3AAK_jQAC3m0ISA36QxWT6k_NOAQ",
                    },
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "title": "Собиратель",
                        "video": "BAACAgIAAxkBAAIM8mmCccLB3LMsSYjQo8XYjcd5XagJAAJUjwACYFYYSLeRPagRAAF0MzgE",
                    },
                    {
                        "title": "Королева прайм-тайма",
                        "video": "BAACAgIAAxkBAAIM9GmCcfSuVjrq2SPjehOWnujug2_qAAJVjwACYFYYSHlt4BtFhIaBOAQ",
                    },
                    {
                        "title": "Лединатор",
                        "video": "BAACAgIAAxkBAAIM9mmCciVlrka5yKzFrZaf8xsQw0qUAAJWjwACYFYYSHHyBcylaIHROAQ",
                    },
                    {
                        "title": "Гневный мишка",
                        "video": "BAACAgIAAxkBAAIM-GmCclWZAAFT2fUavzxz3Nf1rk6_iAACV48AAmBWGEhqIzYbty60tzgE",
                    },
                    {
                        "title": "Бунтарка",
                        "video": "BAACAgIAAxkBAAIM-mmCcoKvDuaHJ7Tzj5AL0VlIHS2cAAJZjwACYFYYSOvwuhxjacxkOAQ",
                    },
                    {
                        "title": "Гигантиан",
                        "video": "BAACAgIAAxkBAAIM_GmCcrK8CBzMOAnm8elZtzhXJLTYAAJajwACYFYYSISjWb-130CgOAQ",
                    },
                    {
                        "title": "Укол",
                        "video": "BAACAgIAAxkBAAIM_mmCcuI0jwGBO6q9TBt19PQv4eocAAJbjwACYFYYSCITwU5ErGlAOAQ",
                    },
                    {
                        "title": "Бефана",
                        "video": "BAACAgIAAxkBAAINAAFpgnMU3nYbSUgHyTe17vqfisq2PwACXY8AAmBWGEimqpvDeLKIajgE",
                    },
                    {
                        "title": "Соловей",
                        "video": "BAACAgIAAxkBAAINAmmCc0abiz1WS5oLmubqXMxlZh60AAJfjwACYFYYSL09gvOe7HkBOAQ",
                    },
                    {
                        "title": "Горизилла",
                        "video": "BAACAgIAAxkBAAINBGmCc3l7RQmSskHWurspsxSZD2KLAAJhjwACYFYYSO9ENUuGySd6OAQ",
                    },
                    {
                        "title": "Робостус",
                        "video": "BAACAgIAAxkBAAINBmmCc6tqMV17KG42YcnBTXlawWXtAAJijwACYFYYSKKYZemIj2s-OAQ",
                    },
                    {
                        "title": "Сапотисы",
                        "video": "BAACAgIAAxkBAAINCGmCc9lzVzT8lYsKN-TpDZjX3E31AAJjjwACYFYYSHhbpviF4_6UOAQ",
                    },
                    {
                        "title": "Филин",
                        "video": "BAACAgIAAxkBAAINCmmCdAv1LtwQrHwGB8JnBUj-NebsAAJmjwACYFYYSPjjcJRfMrYEOAQ",
                    },
                    {
                        "title": "Сирена",
                        "video": "BAACAgIAAxkBAAINDGmCdD3Bq-dOei_Sgnh-5VjCFaCQAAJnjwACYFYYSEr5_980reMwOAQ",
                    },
                    {
                        "title": "Зомбизу",
                        "video": "BAACAgIAAxkBAAINDmmCdGsjKgX2vyV0pURRqYUr8XpeAAJojwACYFYYSKOST6QTvqv1OAQ",
                    },
                    {
                        "title": "Капитан хардрок",
                        "video": "BAACAgIAAxkBAAINEGmCdJ3ciGXoQK2UpOtwJfSMKh9JAAJqjwACYFYYSIMkE-0WqNcEOAQ",
                    },
                    {
                        "title": "Мороз",
                        "video": "BAACAgIAAxkBAAINEmmCdNFC5bUV5H-iGWT11OYn2VDpAAJrjwACYFYYSD2Ubm-Vt49lOAQ",
                    },
                    {
                        "title": "Королева стиля",
                        "video": "BAACAgIAAxkBAAINFmmCdTmsuS9kUjn8efAl22QJDm5RAAJwjwACYFYYSMqTr5wOx0n5OAQ",
                    },
                    {
                        "title": "Королева ос",
                        "video": "BAACAgIAAxkBAAINFGmCdQfUCXoUtAQo3ruHZpzzPRH2AAJsjwACYFYYSDiL6zAvm-1iOAQ",
                    },
                    {
                        "title": "Обратитель",
                        "video": "BAACAgIAAxkBAAINGGmCdWZoGOdfNvGoaNhVR4MqEm-6AAJxjwACYFYYSAgaZdt5nNibOAQ",
                    },
                    {
                        "title": "Ананси",
                        "video": "BAACAgIAAxkBAAINGmmCdZchlwpH22wJpgPzKHV0fZ1sAAJyjwACYFYYSENRYmexZnstOAQ",
                    },
                    {
                        "title": "Маледиктатор",
                        "video": "BAACAgIAAxkBAAINHGmCdci1A6WHzGbOVlZjrpVW6JC1AAJ0jwACYFYYSFqV9GX8i4pIOAQ",
                    },
                    {
                        "title": "Сеятель",
                        "video": "BAACAgIAAxkBAAINHmmCdfr5d6tO5sMGjU4pz4sAAcV37QACdo8AAmBWGEj7PeTnPXQH2DgE",
                    },
                    {
                        "title": "Катализатор",
                        "video": "BAACAgIAAxkBAAINIGmCdi9FAAHN3R_WtA0cPbmjm_PS7QACeI8AAmBWGEgk68FZDf0MMjgE",
                    },
                    {
                        "title": "Маюра",
                        "video": "BAACAgIAAxkBAAINImmCdmaE2UsdezRyHuFnGHMlzeTdAAJ7jwACYFYYSCXTnIbQcfsWOAQ",
                    },
                    {
                        "title": "Санта с когтями",
                        "video": "BAACAgIAAxkBAAINJGmCdqDYfBwuLf019U0ulup0dxiTAAKAjwACYFYYSBpGRBHoyVYuOAQ",
                    },
                ]
            },
            3: {
                "title" : "Сезон 3",
                "episodes": [
                    {
                        "title": "Хамелеон",
                        "video": "BAACAgIAAxkBAAINSGmDJqkObtwIYy2omseCh51H1UXnAAJ0lgACYFYYSARGwBiBYkUFOAQ",
                    },
                    {
                        "title": "Анимаэстро",
                        "video": "BAACAgIAAxkBAAINSmmDJtzrHhuRFFp6iApkL8iKwCfzAAJ8lgACYFYYSHpdodvwbWIkOAQ",
                    },
                    {
                        "title": "Пекарикс",
                        "video": "BAACAgIAAxkBAAINTGmDJzLpPTyXghxM_kuF8V5sXvcPAAKClgACYFYYSO5yhvbGs-RkOAQ",
                    },
                    {
                        "title": "Обратительница",
                        "video": "BAACAgIAAxkBAAINVWmDJ4l7HIcKFp1iIHSuMsRxCjKOAAKIlgACYFYYSE2R5hQUTFGJOAQ",
                    },
                    {
                        "title": "Рефлекдолл",
                        "video": "BAACAgIAAxkBAAINWWmDJ-FmECLL9qkZvtsWymVPWe9GAAKYlgACYFYYSLbRNKXTOvvxOAQ",
                    },
                    {
                        "title": "Оборотень",
                        "video": "BAACAgIAAxkBAAINW2mDKDeJJh_LydM6ikkChGZI5h4FAAKklgACYFYYSBntnDS-EwILOAQ",
                    },
                    {
                        "title": "Глушитель",
                        "video": "BAACAgIAAxkBAAINXWmDKI1tukOU8TTgPHX-4exmDZHkAAKwlgACYFYYSOoE04vqCe8yOAQ",
                    },
                    {
                        "title": "Они-Чан",
                        "video": "BAACAgIAAxkBAAINX2mDKOL766MmOj8jwHVenUvQRPk5AAK5lgACYFYYSPOKbnMLgYFOOAQ",
                    },
                    {
                        "title": "Талисманка",
                        "video": "BAACAgIAAxkBAAINYWmDKTjcL6zjNeicr5rO5eNt5ZqwAAK_lgACYFYYSIYT1gEMUDYWOAQ",
                    },
                    {
                        "title": "Обливио",
                        "video": "BAACAgIAAxkBAAINY2mDKY4sx-J6rY2e-0AeNFkgkogOAALBlgACYFYYSNGoXOek7rx1OAQ",
                    },
                    {
                        "title": "Десперада",
                        "video": "BAACAgIAAxkBAAINZWmDKeQzAWH-L6uG2IhoIvBVd28VAALLlgACYFYYSIZXenzov59TOAQ",
                    },
                    {
                        "title": "Крис Мастер",
                        "video": "BAACAgIAAxkBAAINZ2mDKjqcFJDsBSQPkF440w-WxTdjAALTlgACYFYYSIMPhNiUrKizOAQ",
                    },
                    {
                        "title": "Стартрейн",
                        "video": "BAACAgIAAxkBAAINaWmDKm9WEcfSdZNXXG3qr7IzrOVvAALalgACYFYYSMVGfDru1F2eOAQ",
                    },
                    {
                        "title": "Охотница за квами",
                        "video": "BAACAgIAAxkBAAINa2mDKsTL1oMPydnGF51oDt3uX-haAALhlgACYFYYSAaFDXbJTR-kOAQ",
                    },
                    {
                        "title": "Пожиратель",
                        "video": "BAACAgIAAxkBAAINbWmDKvUt-0l0LHQ4_BKBqcOk0lD0AALplgACYFYYSK5qxkGjdukaOAQ",
                    },
                    {
                        "title": "Игрок 2.0",
                        "video": "BAACAgIAAxkBAAINb2mDK0ufycaoiHgl8UEpgsRyzZcEAAL2lgACYFYYSP2wlacgyF2sOAQ",
                    },
                    {
                        "title": "Непогода 2",
                        "video": "BAACAgIAAxkBAAINcWmDK31FFzL1IafHHpocbzgMsx2yAAL_lgACYFYYSNegO5VrUKXdOAQ",
                    },
                    {
                        "title": "Икари Годзен",
                        "video": "BAACAgIAAxkBAAINc2mDK6zgvzMaXnfZU51b0ZaagZ_0AAIBlwACYFYYSHXSY-1u1uZ2OAQ",
                    },
                    {
                        "title": "Таймтэггер",
                        "video": "BAACAgIAAxkBAAINg2mDMTwWddINdQzfOHugKfsxjpbiAAKPlwACYFYYSN2JyQi3djaWOAQ",
                    },
                    {
                        "title": "Незваный гость",
                        "video": "BAACAgIAAxkBAAINdWmDLDFVkx410kml3UKrRQYrfI1jAAIQlwACYFYYSOzWkfunSkNeOAQ",
                    },
                    {
                        "title": "Кукловод 2",
                        "video": "BAACAgIAAxkBAAINd2mDLIejDzg_F2CIs48ax364ETr0AAIdlwACYFYYSIDv4qv7CmFROAQ",
                    },
                    {
                        "title": "Белый кот",
                        "video": "BAACAgIAAxkBAAINeWmDLN1Ap6D09xgM4zoBJltubGc1AAIilwACYFYYSAf50Rrs594-OAQ",
                    },
                    {
                        "title": "Феликс",
                        "video": "BAACAgIAAxkBAAINe2mDLTUVkgABECB52jg20KdcHdBYTgACMJcAAmBWGEit-u0R7TGM6DgE",
                    },
                    {
                        "title": "Леди Баг",
                        "video": "BAACAgIAAxkBAAINfWmDLYpAuHmtcFv45l6agB33QcqFAAI7lwACYFYYSM7vxX4aF4I0OAQ",
                    },
                    {
                        "title": "Сердцеед (Битва талисманов. Часть 1)",
                        "video": "BAACAgIAAxkBAAINf2mDLbzdxqp1kHZPXC0MnEd2J3sbAAI_lwACYFYYSLAaFK2lDwOjOAQ",
                    },
                    {
                        "title": "Королева талисманов (Битва талисманов. Часть 2)",
                        "video": "BAACAgIAAxkBAAINgWmDLexcSBh2XDqgKF_cWnDwZH9kAAJGlwACYFYYSO_XODWeSGV7OAQ",
                    },
                    
                ]
            },
            4: {
                "title" : "Сезон 4",
                "episodes": [
                    {
                        "title": "Правда",
                        "video": "BAACAgIAAxkBAAINummDT6cCJZbDqLWw-JWaVyZPzMawAAKRlgACYFYgSPINmq4Z_OEEOAQ",
                    },
                    {
                        "title": "Ложь",
                        "video": "BAACAgIAAxkBAAINvGmDUFdyWENW0bRC0WsAAcNNCr94wwACnZYAAmBWIEgAAZjAyjMceys4BA",
                    },
                    {
                        "title": "Банда Тайн",
                        "video": "BAACAgIAAxkBAAINvmmDUQh-ltHIDjvIDYkWWxMjvFC8AAKmlgACYFYgSPBk4xZdycTSOAQ",
                    },
                    {
                        "title": "Месье Голубь 72",
                        "video": "BAACAgIAAxkBAAINwGmDUcAuahWvKSdheCWhUlwCq_8kAAK3lgACYFYgSKJhVNhgGnlFOAQ",
                    },
                    {
                        "title": "Псикомик",
                        "video": "BAACAgIAAxkBAAINymmDUnVqi8FDFVkM7PPfPxLeQ26iAAK_lgACYFYgSCcrGZVbaOwVOAQ",
                    },
                    {
                        "title": "Разъярённый Фу",
                        "video": "BAACAgIAAxkBAAINzGmDUyQAAUtsZFWoe-nZVgeJ3oWZUQAC1JYAAmBWIEhjdCy1W92UKjgE",
                    },
                    {
                        "title": "Палач душ",
                        "video": "BAACAgIAAxkBAAINzmmDU9WksMeUqYKCG7NXFRUw9weiAALglgACYFYgSIjRQduckEb_OAQ",
                    },
                    {
                        "title": "Леди Банана",
                        "video": "BAACAgIAAxkBAAIN1WmDVIakSQKxhUAZ4HQBIDhH3iDEAALtlgACYFYgSPR9AAHH-uqxjTgE",
                    },
                    {
                        "title": "Габриель Агрест",
                        "video": "BAACAgIAAxkBAAIN3GmDVTifAmup_xoVVAxddcE5trh7AAL1lgACYFYgSCuN14CgUWV_OAQ",
                    },
                    {
                        "title": "Мегапиявка",
                        "video": "BAACAgIAAxkBAAIN3mmDVejJ7nKVqG07ZkFa4qXkj50YAAIHlwACYFYgSJoqMwQGDliLOAQ",
                    },
                    {
                        "title": "Вина",
                        "video": "BAACAgIAAxkBAAIN4GmDVph_OTJd6He5lykgP33fu84CAAIQlwACYFYgSCtQH-Mrn-6iOAQ",
                    },
                    {
                        "title": "Крокодоэль",
                        "video": "BAACAgIAAxkBAAIN4mmDV0qH3zJw8k9ufs3UuypjxfHeAAIblwACYFYgSOlQZQ1Bx_qrOAQ",
                    },
                    {
                        "title": "Оптигами",
                        "video": "BAACAgIAAxkBAAIN5GmDV_saVE3O6K9F6936s5ed6tAMAAIulwACYFYgSBtQMj_Witk8OAQ",
                    },
                    {
                        "title": "Сенсопузырь",
                        "video": "BAACAgIAAxkBAAIN5mmDWMFwDnv-hlXd4UrVrcRmbN9JAAI3lwACYFYgSPDu9Q7khm72OAQ",
                    },
                    {
                        "title": "Лединатор 2",
                        "video": "BAACAgIAAxkBAAIN6GmDWXcOPmlp_tRz9zzpKMT-IiyfAAJAlwACYFYgSOmmqxvoYxiUOAQ",
                    },
                    {
                        "title": "Хак-Сан",
                        "video": "BAACAgIAAxkBAAIN6mmDWi7Si2C4RZcvo0MRY_StTpkcAAJSlwACYFYgSImNCi6dtM8OOAQ",
                    },
                    {
                        "title": "Плакса",
                        "video": "BAACAgIAAxkBAAIN7GmDWt884Arz3AvaY8z6necDm1meAAJelwACYFYgSPoHdfymqkpIOAQ",
                    },
                    {
                        "title": "Мечтатель",
                        "video": "BAACAgIAAxkBAAIN7mmDW5KFhoN5iiGul01tmMqgxl6qAAJmlwACYFYgSPF0Ps3TCEJtOAQ",
                    },
                    {
                        "title": "Простак",
                        "video": "BAACAgIAAxkBAAIN8GmDXESefIwVsI5YQRilb73n2ok3AAJplwACYFYgSK7hFgFhZ3fwOAQ",
                    },
                    {
                        "title": "Цилинь",
                        "video": "BAACAgIAAxkBAAIN8mmDXPb2qX9P0x3xF0DAXphEcyWoAAJzlwACYFYgSCjTYDzl5lqlOAQ",
                    },
                    {
                        "title": "Дорогая семья",
                        "video": "BAACAgIAAxkBAAIN9GmDXaa91rOZ6paUW058c0oYUjiiAAKDlwACYFYgSOh-YCZ5ZvvQOAQ",
                    },
                    {
                        "title": "Эфемер",
                        "video": "BAACAgIAAxkBAAIN9mmDXl77CAtOgclqunRhGl0AAY7apwACkpcAAmBWIEhNLEqTQoPCfjgE",
                    },
                    {
                        "title": "Куро Неко",
                        "video": "BAACAgIAAxkBAAIN-GmDXxGwFpMj6IZvW5K8k4Wdho8-AAKolwACYFYgSOoJZSlWyIEVOAQ",
                    },
                    {
                        "title": "Команда Пенальти",
                        "video": "BAACAgIAAxkBAAIN-mmDX8KKh4N8Ylq_tLTEnOAuMcOzAALClwACYFYgSExg0yGzFrsBOAQ",
                    },
                    {
                        "title": "Риск (Последняя атака Мотылька. Часть 1)",
                        "video": "BAACAgIAAxkBAAIOBWmDacZDUCIatKl34f_gSfVrCp9KAAKgmAACYFYgSBWXRoFewF38OAQ",
                    },
                    {
                        "title": "Ответный удар (Последняя атака Мотылька. Часть 2)",
                        "video": "BAACAgIAAxkBAAIOB2mDanrQudhscoIcmYGEmm2ldav4AAK9mAACYFYgSLJqf18p9fR2OAQ",
                    },
                    
                ]
            },
            5: {
                "title" : "Сезон 5",
                "episodes": [
                    {
                        "title": "Эволюция",
                        "video": "BAACAgIAAxkBAAIOEGmDdq-BdnA0URIfdy_xnzRm9p7wAAITmgACYFYgSEb7xnLoBaWOOAQ",
                    },
                    {
                        "title": "Умножение",
                        "video": "BAACAgIAAxkBAAIOEmmDdvg0gx_LbEVcSIOOWHD2wTKvAAIdmgACYFYgSNrtc4HLAXXHOAQ",
                    },
                    {
                        "title": "Разрушение",
                        "video": "BAACAgIAAxkBAAIOFGmDdz_8Z0PTxtaiuZuF6bE3KaW0AAIjmgACYFYgSJK9s4vEGdLyOAQ",
                    },
                    {
                        "title": "Ликование",
                        "video": "BAACAgIAAxkBAAIOFmmDd4cUu0fs9uWY0zqcpMWz0uFHAAInmgACYFYgSBz4Z0k91kg9OAQ",
                    },
                    {
                        "title": "Иллюзия",
                        "video": "BAACAgIAAxkBAAIOGGmDd9L2xbOWSJ9YRAa84uoL8LKSAAIzmgACYFYgSOx8jSq2O0YjOAQ",
                    },
                    {
                        "title": "Решимость",
                        "video": "BAACAgIAAxkBAAIOGmmDeBtY8JE9wrw-lTolYubJ4vwoAAI5mgACYFYgSGbm8_5KZU02OAQ",
                    },
                    {
                        "title": "Страсть",
                        "video": "BAACAgIAAxkBAAIOHGmDeGVuutiBFUuzvN1zRUH_voLFAAI-mgACYFYgSPG1ancOmKUdOAQ",
                    },
                    {
                        "title": "Воссоединение",
                        "video": "BAACAgIAAxkBAAIOHmmDeK7piqLc1600o3Jz0X7d-tE1AAJDmgACYFYgSOyJE_bMyYvNOAQ",
                    },
                    {
                        "title": "Восторг",
                        "video": "BAACAgIAAxkBAAIOIGmDePkSbndCsnZGBySdfIzl2-IYAAJImgACYFYgSIWVvT1PAvicOAQ",
                    },
                    {
                        "title": "Передача (Выбор квами 1)",
                        "video": "BAACAgIAAxkBAAIOImmDeUXLuMA236GT7o86Bc2GQ3SRAAJPmgACYFYgSJOqs47MD5_iOAQ",
                    },
                    {
                        "title": "Сгорание (Выбор квами 2)",
                        "video": "BAACAgIAAxkBAAIOJGmDeZCZEgVRdBF1xLbV58NC_8xfAAJTmgACYFYgSPcXWVTNtzAeOAQ",
                    },
                    {
                        "title": "Совершенство",
                        "video": "BAACAgIAAxkBAAIOJmmDedkEuRtLWHdm_0axqPi42z-JAAJXmgACYFYgSCeNw9cUvWiXOAQ",
                    },
                    {
                        "title": "Перемещение",
                        "video": "BAACAgIAAxkBAAIOKGmDeiGJkOM4OOLSR1Tk7mmZwzINAAJgmgACYFYgSA4TAeW1qWvkOAQ",
                    },
                    {
                        "title": "Насмешка",
                        "video": "BAACAgIAAxkBAAIOKmmDemwxsPjH2e3iTKwxdGCqGwjTAAJqmgACYFYgSH9a_syNueSEOAQ",
                    },
                    {
                        "title": "Интуиция",
                        "video": "BAACAgIAAxkBAAIOLGmDerMaPsXWgGDSwEtiDvymoBm8AAJxmgACYFYgSO51f61Rz8x6OAQ",
                    },
                    {
                        "title": "Защита",
                        "video": "BAACAgIAAxkBAAIOLmmDev1ohWqqR04CEhB91G2XNkRzAAJ5mgACYFYgSE31-quYBNzQOAQ",
                    },
                    {
                        "title": "Обожание",
                        "video": "BAACAgIAAxkBAAIOMmmDe0lVyOfuQ2eKFlzbp7Wv0xv5AAKCmgACYFYgSIFozZcET36OOAQ",
                    },
                    {
                        "title": "Эмоция",
                        "video": "BAACAgIAAxkBAAIONGmDe5VPZZqP0DAJVAW4Bj_tvKJ_AAKWmgACYFYgSJDyW009jrueOAQ",
                    },
                    {
                        "title": "Притворство",
                        "video": "BAACAgIAAxkBAAIONmmDe-HFK8o9cQ2u9efiIaWOYjCbAAKjmgACYFYgSDlXv7GbdcnXOAQ",
                    },
                    {
                        "title": "Откровение",
                        "video": "BAACAgIAAxkBAAIOOGmDfC6oMexA842hKwceisQhw551AAKxmgACYFYgSJ5rjJ8Y5C3dOAQ",
                    },
                    {
                        "title": "Противостояние",
                        "video": "BAACAgIAAxkBAAIOOmmDfHrHTJCEizDgtHXsFSMHJBLwAAK6mgACYFYgSEV3-rNJHWMTOAQ",
                    },
                    {
                        "title": "Сговор",
                        "video": "BAACAgIAAxkBAAIOPmmDfMWSHh_EsIVELvP3uYVkgoURAALGmgACYFYgSGGLCgkdEjlAOAQ",
                    },
                    {
                        "title": "Революция",
                        "video": "BAACAgIAAxkBAAIOQGmDfRH66V5tbBA-iTFk8Zy8D5GQAALRmgACYFYgSEzM5jbLO48lOAQ",
                    },
                    {
                        "title": "Воплощение",
                        "video": "BAACAgIAAxkBAAIOQmmDfVzhYsG0AkUN9QjWHuuM-zv_AALmmgACYFYgSBbgan_Tzyj5OAQ",
                    },
                    {
                        "title": "Устройство (Последний день 1)",
                        "video": "BAACAgIAAxkBAAIORGmDfal8lcXmKB-pXkR2TVttydjXAAL2mgACYFYgSM-Kn9OisNZEOAQ",
                    },
                    {
                        "title": "Воссоздание (Последний день 2)",
                        "video": "BAACAgIAAxkBAAIORmmDffqKuWGXvuiieAIjfsO0TKuGAAIFmwACYFYgSKJOsy9cbygCOAQ",
                    },
                    {
                        "title": "Действие",
                        "video": "BAACAgIAAxkBAAIOSGmDfkFayiebLQQtsZ1KfrJ0p7Z3AAIWmwACYFYgSL-K_ENSM-DJOAQ",
                    },
                    
                ]
            },
            6: {
                "title" : "Сезон 6",
                "episodes": [
                    {
                        "title": "Королева Климата",
                        "video": "BAACAgIAAxkBAAIOY2mDo7qOCuu7mqOQgeeLuAgJBu8DAALRnwACYFYgSGgTZkRcDanKOAQ",
                    },
                    {
                        "title": "Визуализатор",
                        "video": "BAACAgIAAxkBAAIOZWmDpAficqgdX-bG4Z8b9K1TZVDBAALZnwACYFYgSGbTjDGfNmhrOAQ",
                    },
                    {
                        "title": "Сублимация",
                        "video": "BAACAgIAAxkBAAIOZ2mDpFIZLeVAplDs1tVHnllSNDb2AALlnwACYFYgSPjEcKW6uVmiOAQ",
                    },
                    {
                        "title": "Папакоп",
                        "video": "BAACAgIAAxkBAAIOa2mDpJv0eeAt375X22GskAwSaCNzAALtnwACYFYgSJOUo-dkpuvPOAQ",
                    },
                    {
                        "title": "Битва дедов",
                        "video": "BAACAgIAAxkBAAIObWmDpOb9Eib-vDvlR_0NMj5-Lgk0AAL2nwACYFYgSKqfGxBzF6ruOAQ",
                    },
                    {
                        "title": "Спящая Сирена",
                        "video": "BAACAgIAAxkBAAIOb2mDpURev-S0UboLVQphzVnVCqofAAL8nwACYFYgSFkya7hPzzw8OAQ",
                    },
                    {
                        "title": "Каменный Бык",
                        "video": "BAACAgIAAxkBAAIOcWmDpZEwpVkhvhF55d_SUBLy0BawAAIFoAACYFYgSP7OaHtVINMwOAQ",
                    },
                    {
                        "title": "Вампигами",
                        "video": "BAACAgIAAxkBAAIOc2mDpcUFJf4IJrE1XydzGuSoqpjoAAIQoAACYFYgSHlcZMrSY_NoOAQ",
                    },
                    {
                        "title": "Месье Агрест",
                        "video": "BAACAgIAAxkBAAIOdWmDpicLP06WQXOqyaEsZ1u-W-LHAAIZoAACYFYgSEWPlSLOSU2wOAQ",
                    },
                    {
                        "title": "Тёмный замок",
                        "video": "BAACAgIAAxkBAAIOd2mDpoIcMxtrlr5AuJCn98q2-UyoAAIjoAACYFYgSJg9ebpnHdk8OAQ",
                    },
                    {
                        "title": "Разоблачитель",
                        "video": "BAACAgIAAxkBAAIOeWmDptDWr-XsX6tUzJ_v2LLLalLfAAIooAACYFYgSHs2HrEzBfEwOAQ",
                    },
                    {
                        "title": "Исцелитель",
                        "video": "BAACAgIAAxkBAAIOgmmDpygbCdx3azauZ7iMP2UKB6HcAAIroAACYFYgSPMSVSbUUEr1OAQ",
                    },
                    {
                        "title": "Якши Годзен",
                        "video": "BAACAgIAAxkBAAIOhGmDp4Cg8KXxbFujZSaw74oAAcOvtwACMaAAAmBWIEhhUSFoOAgx5zgE",
                    },
                    {
                        "title": "Памперсайзер",
                        "video": "BAACAgIAAxkBAAIOimmDrHWnyFlt6ce2OFiTelYYIj4PAAJ7oAACYFYgSK_FltJ2guuOOAQ",
                    },
                    {
                        "title": "Властитель",
                        "video": "BAACAgIAAxkBAAIOhmmDp8d9IEnHeYmDVktDXIipGIx4AAI2oAACYFYgSJ8VfAzlxAXROAQ",
                    },
                    {
                        "title": "Ноэ",
                        "video": "BAACAgIAAxkBAAISdWmIirLYBqHjWEID41AOon8azHtIAAIdnAACiudJSNONfNKAE2PdOgQ",
                    },
                    
                ]
            },
            7: {
                "title" : "Спец Эпизоды",
                "episodes": [
                    {
                        "title": "Нью-Йорк",
                        "video": "BAACAgIAAxkBAAIOm2mDuMKYTTruUFWnYCq8E-sv8mQLAALmoAACYFYgSLRiaHwOIDJgOAQ",
                    },
                    {
                        "title": "Шанхай",
                        "video": "BAACAgIAAxkBAAIOnWmDuXfKlTvnRynguB2kufXtGXOyAALtoAACYFYgSI_G4uSJjfkjOAQ",
                    },
                    {
                        "title": "Париж",
                        "video": "BAACAgIAAxkBAAIOn2mDuhGojIQ4JLVMAg0ii7SRzIKxAALzoAACYFYgSNt5ncolSWeBOAQ",
                    },
                    {
                        "title": "Лондон",
                        "video": "BAACAgIAAxkBAAIOoWmDutUgZaoDbCuFnaIcPMGqLOJVAAL6oAACYFYgSLQCUkt9sHmtOAQ",
                    },
                ]
            },
        }
    },
    "081": {
        "title": "Ванда/Вижн",
        "year": 2021,
        "episode_counter": "9 серий",
        "description": "Ванда и Вижн — молодожены, живущие в идиллическом городке Вествью. Поначалу жизнь героев кажется им идеальной, но постепенно они понимают, что это не так.",
        "poster": "AgACAgIAAxkBAAIUSmmLYgfU0c8GmV4rynRyyGfMru6sAAKxGGsbUAhZSP87ZnaE3l1JAQADAgADeQADOgQ",
        "country": "США",
        "director": "Мэтт Шекман",
        "genres": ["фантастика", "боевик", "драма", "мелодрама"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIUTGmLYqJSXdRi4ub1xXMV36bF-t6yAAJknwACUAhZSPDnoTo1GWSgOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUTmmLYuCkN2w-vnhizBy9mOvCfUBOAAJmnwACUAhZSDyoO47817srOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUUGmLYxPFXSnEjHEV1ZFhdxkvZqVYAAJpnwACUAhZSHZdcJgWzpQeOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUUmmLY0sxgKRhybxuPgR7j2XAdyqQAAJunwACUAhZSEf44SH1hcMzOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUVGmLY41IHeDGv9-jsTHYU8MooWa9AAJxnwACUAhZSIEs1Iams5pwOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUVmmLY8tCb5gl37OkG5aiJum-_fMGAAJ5nwACUAhZSOq6Yk_rrqtaOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUWGmLZAk1PerF_FV3BtE-IiJKMxYpAAKCnwACUAhZSPrvKYM_4YkpOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUWmmLZFUxImrOnP-Do9vR_3idC8NqAAKLnwACUAhZSN1myU5jQ6BwOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUXGmLZKqrmr1RUY-IBSEfEJYc3yiEAAKVnwACUAhZSHvlhSNCM4CqOgQ",
                    },
                    
                ]
            },
        }
    },   
    "082": {
        "title": "Локи",
        "year": 2021,
        "episode_counter": "12 серий",
        "description": "Локи попадает в таинственную организацию «Управление временными изменениями» после того, как он украл Тессеракт, и путешествует во времени, меняя историю.",
        "poster": "AgACAgIAAxkBAAIURGmLV01DzsI_DBMTYaLp3u5HDbR8AAIwGGsbUAhZSCe1xQl7AopeAQADAgADeQADOgQ",
        "country": "США",
        "director": "Джастин Бенсон",
        "genres": ["фантастика", "боевик"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIULGmLURI3LK7SQIJu46VMlun0DxWvAAI1ngACUAhZSFn4zTMsmHHcOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIULmmLUYSZBJB0PUwBjPtW0HIPLK9bAAI6ngACUAhZSODsqMc_7IsuOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUMGmLUdbLWGDLoU5e89VKptyF26qLAAI-ngACUAhZSMma3FUYrCLfOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUMmmLUjDyWZvSGchxioJ5wYThgpK3AAJJngACUAhZSOmfxSGCUdPEOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUNGmLUo53F0Zhff9S9IgnG0KtI1DPAAJNngACUAhZSLN9EGa2ZNCHOgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUNmmLUuT5OdJl8U1JoSgw_CN5zC-JAAJWngACUAhZSEzqtSbmxFPfOgQ",
                    },
                    
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIUOGmLUzZ09zXuneiHM1ZPwtZPqR7VAAJZngACUAhZSHUBfRmYAAFLTDoE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUOmmLU5cMDuY5SOtpug6pnOpkz355AAJfngACUAhZSLkCqfj57li8OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUPGmLU_qgoIq8udT14Lnm4ZXfC8dqAAJmngACUAhZSJQ5XPpTu9y1OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUPmmLVEfCyWoAAeN5WelzUX3-eZzsugACbJ4AAlAIWUhox0F8LCLSxzoE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUQGmLVJtc8a-ZpQcLZoJgifG8pS7XAAJvngACUAhZSO6YJ1-r4Ja8OgQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIUQmmLVQOhojpgDfFQnsvHSGzc74NOAAJ0ngACUAhZSGlvQ078zkoNOgQ",
                    },
                    
                ]
            },
        }
    },
    "090": {
        "title": "Скажи, что ты видела",
        "year": 2020,
        "episode_counter": "16 серий",
        "description": "После взрыва, устроенного маньяком и унесшего жизнь его невесты, криминальный профайлер уехал в сельскую глушь подальше от людей. Там он знакомится с местной начинающей полицейской, у которой есть способность помнить всё, что она когда-либо видела.",
        "poster": "AgACAgIAAxkBAAIO52mEdtl6DOA7Q1UbZdbCF_ijYzvtAAI3D2sb24kpSNXfkkNE1shKAQADAgADeQADOAQ",
        "country": "Южная Корея",
        "director": "Ли Джун-хён",
        "genres": ["дорама", "триллер", "детектив", "криминал"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIOx2mEcQ7FqaHk6UhBUNb99GnfxaizAAKkhwAC24kpSATtDrROujXnOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIOyWmEcS07CYnFmQsfH8Yplq4MpQYsAAKlhwAC24kpSLuFAzJaDIZUOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIOy2mEcU5SobysyWBgYnroV6uloE8TAAKohwAC24kpSHZI6pBVDr6aOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIOzWmEcW-w620XVpmWP7CX9iGH5EQXAAKphwAC24kpSBLmFb5Ah-FVOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIOz2mEcY7JZ8UAAeNPpaDNLZvLDY8RIwACqocAAtuJKUjbtZlD-ITo6DgE",
            },
            {
                "video": "BAACAgIAAxkBAAIO0WmEca8MAlMwNe8BHBOfiG8Jo6NiAAKwhwAC24kpSJn_QpufnS5hOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO02mEcdLcHjfyCJ2gv8Vv1z8qOvKzAAK2hwAC24kpSFF458aiAq9KOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO1WmEcfOaqvweMAnYrjvBVaUg7s0zAAK8hwAC24kpSDc5J4XQQDCZOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO12mEchG-h6c5eeiH3wMCRI6UEvPzAALAhwAC24kpSHKzL6mG5rZXOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO2WmEcjMcT3YSzKT-oGQ0aw5BwlHxAALHhwAC24kpSOgwVLHKFh37OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO22mEclnIEAtdUG3yqxIF2WYuTGYCAALJhwAC24kpSEdOK_m0W0zXOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO3WmEcnrwCsSpY0K3FAZWEDuPlI7wAALMhwAC24kpSPKHFwen0LspOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO32mEcppmdDCTWBz806-JKHDwPlAzAALQhwAC24kpSAbkRbrsYqd4OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO4WmEcrT6seQQ3kPb-Pye3pHw-p4OAALVhwAC24kpSL1wdsFiXo26OAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO42mEctQlrdGpX2CO7ovm77wUfgLUAALahwAC24kpSD5Nd1aE0RGBOAQ",
            },
            {
                "video": "BAACAgIAAxkBAAIO5WmEcvLffQTwOrf4txFlvpN8raCyAALbhwAC24kpSHqCUAccqWO8OAQ",
            },
            
        ]
    },
    "096": {
        "title": "Во всем виновата она",
        "year": 2025,
        "episode_counter": "8 серий",
        "description": "Марисса Ирвин приезжает за сыном, который после школы отправился в гости к новому другу. Дверь ей открывает незнакомая женщина, утверждающая, что она ничего не знает ни о каких мальчиках. Так начинается самый страшный родительский кошмар. Обычный день превращается в цепь лжи, тайн и подозрений.",
        "poster": "AgACAgIAAxkBAAIY1WnRDizIdJ1qRu4K2R6cUoJ6vHQjAALMFWsbSvOISqdmJAP5u2nEAQADAgADeQADOwQ",
        "country": "США, Австралия",
        "director": "Кейт Дэннис, Минки Спиро",
        "genres": ["триллер", "детектив", "мистика"],
        "episodes": [
            {
                "video": "BAACAgIAAxkBAAIYxWnRDQnjvyIsr_MH4_1Zhjd5jkj3AAI3mgACSvOISsJwT9YmNtjZOwQ",
            },
            {
                "video": "BAACAgIAAxkBAAIYx2nRDSvJ5DxTJ_rn6ZFHYBn8YXtbAAI4mgACSvOISqSd1iGakaehOwQ",
            },
            {
                "video": "BAACAgIAAxkBAAIYyWnRDVB_AuZb_ozYcY_bj1GeAYNWAAI5mgACSvOISuAUgxtUXVkYOwQ",
            },
            {
                "video": "BAACAgIAAxkBAAIYy2nRDXa0IYGawNXxSK4qPA2_PyOYAAI7mgACSvOISs03771WMPnZOwQ",
            },
            {
                "video": "BAACAgIAAxkBAAIYzWnRDanJZaM_HpatKW90-O5RtXlbAAI9mgACSvOISoEtcZPqD0HFOwQ",
            },
            {
                "video": "BAACAgIAAxkBAAIYz2nRDcvSlfqi6WO8OCCr5_38-uSlAAI_mgACSvOISgEvzPW6-BF2OwQ",
            },
            {
                "video": "BAACAgIAAxkBAAIY0WnRDfKZITFyw5tziUg9dmFlRAHgAAJDmgACSvOISuELZvrJLAqoOwQ",
            },
            {
                "video": "BAACAgIAAxkBAAIY02nRDhFHfk334UL1TDED2GDa0CK1AAJFmgACSvOISszsnFNhupsyOwQ",
            },
        ]
    },
    "099": {
        "title": "Маленькие катастрофы",
        "year": 2025,
        "episode_counter": "6 серий",
        "description": "Молодая мама Джесс просыпается ночью от крика её 10-месячной дочери Бетси. Джесс как можно скорее отвозит на дочь на машине в больницу, и дежурным врачом в отделе реанимации оказывается её давняя подруга Лиз. Врач замечает на рентгеновских снимках трещины в черепе малышки и оказывается перед сложным выбором: следовать правилам и обратиться в органы опеки из-за серьёзных травм или утаить происшествие ради подруги. Лиз решает следовать правилам, и это решение подвергает испытанию дружбу в их женской компании и грозит разрушить их семьи.",
        "poster": "AgACAgIAAxkBAAIbMWndPl2yFsFDsHbT9KFrPvlZ1WuLAAKRF2sbf9rpSkx9Q2_DnV9YAQADAgADeAADOwQ",
        "country": "Великобритания",
        "director": "Эва Сигурдардоттир",
        "genres": ["драма"],
        "episodes": [
                {
                    "video": "BAACAgIAAxkBAAIbLWndPV-O9286Hi3FDmJx6UDmZSkHAALanAACf9rpSkWs3KVmeQgROwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIbL2ndPl0Eztq8K_Rb24byVRu8V2bbAALdnAACf9rpSpBOy2yWHNzTOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIbO2ndRyMhOKINvjPDK8mRSStl4JUMAAIKnQACf9rpSiPR5DMpN1WkOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIbNWndP7hAZea0SJHzlHb29OkHojC_AALonAACf9rpSt0uL40jfbq0OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIbN2ndQLY4mja-uWMJIEEuZL5EIjkNAALxnAACf9rpSkHDeEpnLvueOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIbOWndQk_kV2rDG4dRiafXInnHBn3bAAL8nAACf9rpSnW3l1c_hYi5OwQ",
                },
        ]
    },
    "100": {
        "title": "Сотня",
        "year": 2014,
        "episode_counter": "100 серий",
        "description": "События в сериале начинают разворачиваться по прошествии девяносто семи лет после того, как всю цивилизацию уничтожила страшная атомная война. Высоко в космосе на орбите Земли летает большой космический корабль, где находятся те, кто выжил после страшной катастрофы. Именно с этого последнего пристанища людей на Землю отправляют космический челнок, на котором находятся сто малолетних преступников...",
        "poster": "AgACAgIAAxkBAAIdEWnj5eyQrn7qrWjbtV4WhAMZ5lRLAAILFmsbcmogSwGpcFd7NTTsAQADAgADeAADOwQ",
        "country": "США",
        "director": "Боб Морли, Генри Иан Кьюсик и др.",
        "genres": ["фантастика", "боевик", "драма"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIczWnj10INHTyXcNJewGOCtOo5WhCEAAK5qAACcmogS1upP6Wsb3D6OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcz2nj17EIKepmqh5bjpiqPjqAUPIYAAK-qAACcmogS93mSZ13F_HGOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc02nj2BQtD-s14X9bCblHQn8LVQLiAALIqAACcmogS-QIrfleMqSwOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc1Wnj2ONHGNxqJvMXF4-t5Rb95RbzAALXqAACcmogS4ci9t5a46t-OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc12nj2XxY-dZkkmT0JL4RlieTJ0sBAAL5qAACcmogS7QRIvGzj2hbOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc2Wnj2jAOHfGBA5GAWz3_1Ys7tbBfAAInqQACcmogS8eoBna3y8iBOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc22nj2oNCBies5ww2EV_kyhHvZBT9AAIqqQACcmogS7sFhHuKcGfrOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc4Wnj2zFZqh_f-v72AsjANd8nZwjHAAIyqQACcmogS9x7T4HpSxdaOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc42nj27O7gdqN0qM5Bn1xSvTmHvV_AAI4qQACcmogS3YfxRn5qUJ1OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc5Wnj3BJqqsSZB5ROi25XeTeO4aCLAAJDqQACcmogSxZxAAFm20iazzsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc52nj3E1mq7w_2GF_5jN8xOJDB5rIAAJJqQACcmogS5EGIt_Brw73OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc6Wnj3Ix0b95JrMBmO9bgG1Kfgf_6AAJPqQACcmogSyxojfamtHJzOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc62nj3NNgJ5JHKg2hdPayFQavF_oHAAJRqQACcmogS9j6VZS41V4_OwQ",
                    },
                    
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIc7Wnj4mqWE1hWvP8uzNetd55MPzofAAKRqQACcmogSwPdObVWIyBeOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc72nj4piNfyPwn35ZeSDFMP-g7YKcAAKSqQACcmogS1twdxc-L6kEOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc8Wnj4suee70pOUq40T9k_F0uU4h9AAKVqQACcmogSys4jjD_JsnZOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc82nj4wUIfRtn0LX7ZImygnbKrPJuAAKXqQACcmogS2T5ZaDWclPJOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc9Wnj4zEkhAhh_G1cxh6RZkz7C8PjAAKYqQACcmogSzgW9yJ0IU-EOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc92nj41m18QTjSPVN5jOthlXvMNPiAAKaqQACcmogS3vO2-Kak5FEOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc-2nj44FJv3cO2WVi3kFZ1UPk5yYYAAKbqQACcmogSyao-LPCrLTUOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc_Wnj46ygpqOnUzQ7u8XbxZOGlxl3AAKdqQACcmogS9N9pRrAJ1mDOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIc_2nj49Za8GwQmnZ3Y4FJ92eXZIlZAAKeqQACcmogS6o-Gu1LsxnKOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdAWnj5AGn2EBD8dXLTTiFFUaOY6X-AAKhqQACcmogS8e1hoGsVUtbOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdA2nj5Cho7Nl5czWqZxt1IOT33gJkAAKmqQACcmogSwO2cz1oV45-OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdBWnj5FUGhksuYx3FplZyMsaW8j3JAAKrqQACcmogSymQoPYD1fZJOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdB2nj5HyVdjrg9uG_oUMJQcy51c6NAAKtqQACcmogS2GB3ZG4uqjrOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdCWnj5KUQHOs2biXVc1vsYgjxZDBxAAKuqQACcmogS768Mxq2vtkoOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdC2nj5MZlIaWk854bUi3kiQz8n1hBAAKvqQACcmogS7klyG33A2v3OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdDWnj5OxpFyVzFbj6VZ1PmXclTXJbAAKxqQACcmogSxkamOL7h3AlOwQ",
                    },
                    
                ]
            },
            3: {
                "title" : "Сезон 3",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIdGWnkuXQBA1sfeggc7Hixachpmhj-AAL0mwACcmooS1RyMv10sNm4OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdG2nkuaruKqtSJoG8t1vyZq9HngSbAAL5mwACcmooS3_W8d86_W4ROwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdHWnkudca-_abEYAVCHncVs-5KtDeAAL8mwACcmooS2sV1B4AAdEy6zsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdH2nkugin0Ceusjm_BLWNaNqMWKJDAAOcAAJyaihLOZd97WFPT507BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdIWnkujSe3iyVFXd7xmAbSKlQmJ1_AAIDnAACcmooSwnSYamHJOJjOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdI2nkul0VzOXviS-Sij_kWwc7qS6_AAIInAACcmooSyBVlZ5UnFeaOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdKmnkuohMHTKbvNpYLeg-bw9bobWqAAILnAACcmooSzLk3PN-HvUwOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdLGnkuq89YGfdB2biF0cLmgABvnJxIAACEZwAAnJqKEtZ1NDipmHGgDsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdLmnkutk1aSmsj7fXXiIUPmZ2UvvCAAIanAACcmooS5OIQnRlnCVnOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdMGnkuv_aAAG9AXaGN6BfCkcreQnJWQACHZwAAnJqKEuWoi3HdsoAAQw7BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdMmnkux_TH0YSiB0K7CrYXYXX2iZCAAIinAACcmooS-4rH9XfweKXOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdNGnku0jW_7L4ffjW7nu5-iW2SU9lAAIknAACcmooS1FVTBDTqZ-7OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdNmnku3n06nKb1dyr8VysMq2PT12-AAInnAACcmooS_LuvzQ5AmF_OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdOGnku6Rart5_LmiQE6Cuj1F5uHsbAAIqnAACcmooS9WWCyBCUS1AOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdOmnku88NLcgkSOezSpdStSpxQCPxAAItnAACcmooS-EirWx1skmPOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdPGnkvANwIGCEfid9LuoszllywtlZAAIwnAACcmooS9Uc6wVmHGXfOwQ",
                    },
                    
                ]
            },
            4: {
                "title" : "Сезон 4",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIdQGnkyiKw8d6r6zlGT7BMD6xKVSp1AAKNnAACcmooS3cS6oaIlp2VOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdQmnkyk5E_341iY1LFzUsDItjAQLvAAKOnAACcmooS4ojt6zYjWjLOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdRGnkynanZTv4esCOudL-bvgZ_LqcAAKSnAACcmooS5AMQNiCLNd_OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdRmnkyq2hAnLMr8LiLPk__KPadFZbAAKVnAACcmooS5Iikj3QedvVOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdSGnkytlwj3hb0hntW_bHDDXuw8DLAAKYnAACcmooS_vxtx-_IF4POwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdSmnkywa0E72iN_gYw9Ta715Fh3ctAAKdnAACcmooS3DDSgABxmHhOzsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdTGnkyzByPQdIN-hEARcLypTXy_DAAAKfnAACcmooS3QQYOPWCO3HOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdTmnky1dN7FJRMh2j6B7U-atWmZOnAAKinAACcmooSya8Vt1cSZ6GOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdUGnky31lEBr-Opr9oiTv0XF0EDz_AAKlnAACcmooS3sDmNOxNFrDOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdUmnky6zE6KK9Msq18G4NOuTNGgtPAAKnnAACcmooS7WmnwFw8w7_OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdVGnky83ksamwQ7mMjg8mhrLe_HqaAAKonAACcmooS9M5Iyicv57NOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdVmnky_JfkhoedvAu8_tqPmDl__6GAAKqnAACcmooSyLXQUnBrcnZOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdWGnkzB8SGzX8bs1gCzj6r1L163lYAAKtnAACcmooS15Ui-GKnPoyOwQ",
                    },
                    
                ]
            },
            5: {
                "title" : "Сезон 5",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIdZmnk07PNg7ptL_pbZKMC0MwC60RBAAIHnQACcmooS_yg5boqeh7SOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdaGnk09xg0ygDGGDEFOsn8C5AJvPAAAIInQACcmooS7wXhXwdOqTAOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdamnk1C8TKtOh4huDPEFIU9D0ZooaAAIKnQACcmooS7EUnVioY4ffOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdbGnk1Naf88lJHpAc8th2smq49gdsAAIRnQACcmooS7f3EL5sU6AlOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdbmnk1QbS4zA4rD91HdXkZwY4Wlq4AAIUnQACcmooS7jfDExk78WWOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdcGnk1T66iLj5dsDoaWPOT7hfQkIeAAIXnQACcmooS_VZdKrEX2kWOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdcmnk1Wu_6_f0uPy1EI4WNdZHsy1UAAIZnQACcmooSxVrZDnt5wltOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIddGnk1Z82dP08b33haza5AQStossaAAIcnQACcmooS23atBOr9gEwOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIddmnk1dKBE1XvZgwbdQuk0ZANCGiZAAIdnQACcmooS5PwjQlMrtRYOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdeGnk1ltsJfvKjSG5ZSUAAd2fCjj4pAACJJ0AAnJqKEur2L8S2lJ9rTsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdemnk1uvPrIUUJJES6gX6oPj-NkWZAAIsnQACcmooS-7Q2pFTaAZwOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdfGnk1x5mFi2OXiffcZqM8O3anKAqAAIynQACcmooS-FojalZysNjOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdfmnk11S0SQx0ceOiDR3e3XVEXASUAAI3nQACcmooS3wEH3V4KZpAOwQ",
                    },
                    
                ]
            },
            6: {
                "title" : "Сезон 6",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIdgmnk7Wv7Jvvw9Gr2SUxBBlgu9MGQAAOeAAJyaihLUBlSK1xk-FQ7BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdhGnk7ZoPvkhhnFxqe3_AGnhxAtY5AAIGngACcmooS5vqgBltgjItOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdhmnk7cT9HFt7_2lRZXGH5C7T4mjuAAIIngACcmooS99wSHcRCsqxOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdiGnk7fqhhfjNs2w5f5drfj9LM_4bAAIMngACcmooS6lmGLN-PLWvOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdimnk7iPgd40vPvWtQsAsswpMmq9mAAINngACcmooS9FCk8ncwkEhOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdjGnk7lMGsX22yx_kH-spQ4nlF-reAAIPngACcmooS_d-w8MS4nZvOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdjmnk7oL2YfDv23EWyTRcYzkzNymrAAIUngACcmooS3ICZI0BlLmrOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdkGnk7rAoGThjTUPJamQMq66gbjlrAAIWngACcmooS1lOFTd7Cte_OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdkmnk7to2z7F9y843dJe-c1t62GGTAAIXngACcmooS7_2O9jmYDjqOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdlGnk7w12F9eA2BlD4-TJzP-KhCvxAAIZngACcmooS65eyRo8Gw_1OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdlmnk7zX63nZHVtRxFMpfXVOF0CP-AAIbngACcmooS69_9skvdUbJOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdmGnk721tcqPpj2EwkmVJECYRU1IfAAIfngACcmooS0Am0SwDZqrVOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdmmnk77Pv3Y1ilSV7dbexQHVwqs-LAAIlngACcmooS-oPwVOoUS4WOwQ",
                    },
                    
                ]
            },
            7: {
                "title" : "Сезон 7",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIdnGnk9b2ZGsoizizkOEXZxZ7vwBX9AAJ2ngACcmooS6XF3o6Pyma4OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdnmnk9hENgjxQO5MQ97itIUlSh0EHAAJ5ngACcmooSwZIu7B4wEeqOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdoGnk9ktfhKXytGUYcXHKfdpQeN_CAAJ8ngACcmooS8vDsDtYVpJVOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdomnk9pU9-Z8pvExButF68MQtoJQYAAJ_ngACcmooS9E3OtqFHqTIOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdpGnk9thKWHZkCvqzNRI--_IYBIwFAAKAngACcmooS0c5tL58Ak1IOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdpmnk9wk4y9ZqEAtqlxOORSQE9Gi3AAKCngACcmooS0oOG1CNMPxYOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdqmnk9zy65LWo_XoIiQMhzZImOasiAAKFngACcmooSwYfHg1HwRwHOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdrGnk94YD3aCw2Z57RmhQ2V1DkY67AAKIngACcmooSyagE31qBjfkOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdrmnk99wYL2fSGxGq-Z95HRMeMibEAAKPngACcmooS-P-xN0isAQiOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdsGnk-Do22DgPODarT1_EEsnzUJO9AAKSngACcmooS6fkjqz7kAJROwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdtGnk-JkIGr8ZCclShT99dtJZXAQvAAKTngACcmooS2cW5FF4DyyjOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdtmnk-MTckSsMpKHeX09PTNypE85dAAKVngACcmooS86cjP6ibasNOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIduGnk-P5ptTMePXGO4uGLJK0eBaPAAAKXngACcmooSz9ieXiGbvxjOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdumnk-Sy8VzaYc7e4eRnCLTq1wHcCAAKYngACcmooSxySzgTKrI-dOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdvGnk-U-Vtip-lNs1De5HRHQwh3llAAKZngACcmooS_Cl6MIK1I55OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIdvmnk-Xk5Vb6pXWNWwL7PR8LI0bQgAAKbngACcmooSxas3zbJejmqOwQ",
                    },
                    
                ]
            },
            
        }
    },
    "101": {
        "title": "Переполненная комната",
        "year": 2023,
        "episode_counter": "10 серий",
        "description": "Лето 1979 года, Манхэттен. Дэнни Салливана задерживают по обвинению в убийстве. Психолог Риа проводит с Дэнни многочасовые беседы, чтобы понять, какая цепочка событий привела молодого человека к роковому дню.",
        "poster": "AgACAgIAAxkBAAIbMGndPl0mxH_O9JnLIep-IZ9Chbz-AAKQF2sbf9rpStp6D7HlEQRuAQADAgADeQADOwQ",
        "country": "США",
        "director": "Брэди Корбет",
        "genres": ["биография", "криминал"],
        "episodes": [
                {
                    "video": "BAACAgIAAxkBAAIZKGnX5NppSLGAZQ2nWZXnQXNNr1jqAAJZjwACUNa4SoKE8r8q0dJfOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZKmnX5V2wtHAMHBuiJMFQwFt-nVoiAAJpjwACUNa4SoTugBobLA33OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZLGnX5Y7iDC-jOZ3tjPhCfAU88ofpAAJrjwACUNa4SoyGouM5eQEWOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZLmnX5bzTxYh_qKx-8YtKVw-KP4piAAJtjwACUNa4SugPNOIOZojxOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZMGnX5gYdF4F7MrU-tdCTjP5SirGbAAJujwACUNa4SkavJSxNypMmOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZMmnX5kJ_dHs4BFj6HSs_E-Zh9PM1AAJyjwACUNa4SnlY7HT8ZZG_OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZNGnX5odZvS-IpMfSDeuGlYFl_LqmAAJ1jwACUNa4SmAVlHe9GnCGOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZNmnX5yWo2wV2hQwnF1FEUbBhZV4GAAJ9jwACUNa4Sp1rJ6kyumSsOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIZOGnX51ikU4FMOuosVtqR00l6kBS-AAKBjwACUNa4Sh9cq-pHAAFCGzsE",
                },
                {
                    "video": "BAACAgIAAxkBAAIZOmnX54rqOiuURK0kxMs8mcnNVCw3AAKDjwACUNa4SthYyB0ddT4HOwQ",
                },
                
        ]
    },
    "102": {
        "title": "Призраки",
        "year": 2021,
        "episode_counter": "88 серий, онгоинг",
        "description": "Молодая пара получает в наследство роскошный загородный дом. Однако вскоре выясняется, что дом населён призраками прошлых жильцов.",
        "poster": "AgACAgIAAxkBAAIesGnnai6Oy_ltpzhtlDz25h2Tk540AALSFmsb6EdBS5cKtduO4GJwAQADAgADeQADOwQ",
        "country": "Великобритания, США",
        "director": "Роуз Макайвер и др.",
        "genres": ["фантастика", "комедия"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAId9GnmtmCjjHNsiVzknIUDKcqD-LvTAAIImwAC6Ec5S5kh1y2b1qdiOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAId9mnmtm9CNrM5c8yMcSq3ORyp0mNZAAIJmwAC6Ec5S0VkH19BgqjiOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAId-Gnmtn4DRn1BEXYtTwZDoh_d7E3_AAIKmwAC6Ec5S4XTTf0iRVAIOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAId-mnmtoxQ9rzKY9EJ-3sbyt653-htAAILmwAC6Ec5S65vjP872TV0OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAId_Gnmtpmiw6TKSHqYIwqWbGRQLuisAAIMmwAC6Ec5S1NHP39aq0ChOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAId_mnmtqqw5QRMjbHuzL9Gy5R4xWa4AAINmwAC6Ec5S2eueqeGX4QrOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeAAFp5ra5Y3exWRucvrl53XivLtZ7ywACDpsAAuhHOUudmoImlbtJmDsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeAmnmtsbHyGYr4Wz1LYmQrzj6HfSgAAIPmwAC6Ec5S4t2Oa1qc3xcOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeBGnmttbUTKS388pE6NRjm3sV20WqAAIQmwAC6Ec5S1BO7Q9oFy3oOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeBmnmtuYWZWbbnckk0_rOy_JfE0xjAAIRmwAC6Ec5SwABL0ueJaoaHTsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeCGnmtvRa-VfAvD9QhIliIPE8Gry9AAISmwAC6Ec5SyPCFanx-CqjOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeCmnmtwLiVl0a12SEw8hsIyvoM_FMAAITmwAC6Ec5SxsgCWWQTt4IOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeDGnmtxExM6wW8agVryeprt_9pmAKAAIUmwAC6Ec5S_fkK5ncniA2OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeDmnmtyBNbcUS44kUg2yeeg6Yu4bIAAIVmwAC6Ec5S9R_RXMCT-FeOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeEGnmtyt6OGq3RKuBJXAljg27XCYLAAIXmwAC6Ec5S8PVOFZNF7EGOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeEmnmtzwHqcSaAYHNouqOzONPb_IQAAIYmwAC6Ec5S3lZ9Ch12iPEOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeFGnmt07CaFIRuV5089A500KfjG3hAAIZmwAC6Ec5S7aHX23FXFMvOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeFmnmt16LTTltCkgAAcTlOxirIZ-p6QACGpsAAuhHOUv1SV2xAAGgnls7BA",
                    },
                    
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIeHGnnWDRFhl1lCsdgwS68y4PgFqdcAAJ8mwAC6EdBS0MWTt0YpQY8OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeIGnnWM5a8CAsksN6GNjCtzIAAQTEXwAChJsAAuhHQUs6_98ssUQx4DsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeImnnWM5zVu3Q5EB0vMgYMbkic4wRAAKFmwAC6EdBSxotEbkW4HyWOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeJGnnWNzpn3rmRlSfLa6w-voHj0PcAAKHmwAC6EdBS52nMG4SG1LMOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeJmnnWRxxfB5jvRk199P1-duJyvO-AAKNmwAC6EdBS9C98dxK__P0OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeKGnnWTbblhu7ucAXXiDm0qDolGx6AAKPmwAC6EdBS0_v4ud_9BWKOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeKmnnWVYlzrgwFjA7EsmBikWA_FJaAAKUmwAC6EdBS--9SWjEbibmOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeK2nnWVbU_XIiZ2bDggs2_On_GfXlAAKVmwAC6EdBS1eZ6gW3aruiOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeLmnnWWXIkuIQ7gcYf0RoO-dF6TpMAAKWmwAC6EdBSxwvfXeoOM3TOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeMGnnWW4mlX63Yyj97xQersYQ3MqhAAKZmwAC6EdBS0aqfVLBdtLvOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeMmnnWX5ySbeJ4AAByCcnGKQlHFWjtwACnpsAAuhHQUt7_CTLqF_5TTsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeNGnnWYxA0OAp5MTL4dlh1JeHppSTAAKhmwAC6EdBS58N200T4hT-OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeNmnnWZqdQbEZ81K7vyOd_iLfMPgCAAKjmwAC6EdBS96bdJBKnuSJOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeOGnnWajpf8L1yoZVLvMPgLtWck1cAAKkmwAC6EdBS_lx7ZdhQDvxOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeOmnnWbQqgb4YbX0fIk_5mv1_T8bsAAKnmwAC6EdBS--7xXc01YefOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIePGnnWcIxAQW_bdFs_afDl_u8ssHwAAKqmwAC6EdBSxDc6OENBScYOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIePmnnWdCrvW25NeEJRbrHgkN46WDOAAKtmwAC6EdBSwNiEPmrHYasOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeQGnnWd1GPjRfoTJ4H_tII9FdhwoIAAKvmwAC6EdBS6rvQ2tMLi1WOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeQmnnWez4NChnPUHGfhHRZ17diqo8AAKxmwAC6EdBS-nY4D0aGNlCOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeRGnnWfh6WArmEi2FSAjAskmOr0AWAAK1mwAC6EdBS9eURrjQi_xNOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeRmnnWgXqvF7ggK1xzV83BlDibBKSAAK2mwAC6EdBS83cpKpavlSkOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeSGnnWhBZPmfu7i0GPBdq518EXUM5AAK4mwAC6EdBS-wmmwx8zNH1OwQ",
                    },
                    
                ]
            },
            3: {
                "title" : "Сезон 3",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIeSmnnWq8Z2rHs97A0QfS-4X5t4uaqAALEmwAC6EdBSxN8_9Z066ncOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeTGnnWroaC37er-D97AmCL7cb7OtxAALFmwAC6EdBS612WXbiaV_GOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeTmnnWsgLeFxFjK7x6PzKMI44HH6FAALGmwAC6EdBS3g2CZhKw_q0OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeUGnnWtX-pucjoNObE8pzvs4vuhduAALHmwAC6EdBS61MofLXsNOgOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeUmnnWuKA8C1Cd-ZuqloEJz96Iw-yAALJmwAC6EdBS6lw-LMHMgTVOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeVGnnWu9NLFS9kQjmWSeBcsPD2eisAALLmwAC6EdBS8TmGHx0lUnqOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeVmnnWv3bDC81Go1qTKD3WUCAsRpmAALNmwAC6EdBS8YNG515EH7BOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeWGnnWwsYOykDgEe6teFQE4Ac_wYUAALQmwAC6EdBS0JnSNHm2KLhOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeWmnnWxoSuBkO_LzvPekkAYhTsvmvAALSmwAC6EdBS7rPvVO3e5PuOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeXGnnWyaQMHVa6jJxcSm4mpSao5LjAALVmwAC6EdBS50yQKjHGPT5OwQ",
                    },
                    
                ]
            },
            4: {
                "title" : "Сезон 4",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIeXmnnW2YBX_5mHhGDRDGogv4xcPyzAALZmwAC6EdBS7BOicTIY4hsOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeYGnnW3SuCq_x8tSi6LlG_TBo_xscAALamwAC6EdBSwvB5kGobhPdOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeYmnnW4aNs6qW9_Qyk1ooj3KFmwVLAALcmwAC6EdBS3_12MeqmeACOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeZGnnW5Who6BDCoYyoVO72RIJ6rygAALemwAC6EdBS-kFCc-GFz7gOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeZmnnW6VpOsD8qoIv-9qoVxwfOpbBAALfmwAC6EdBSyWsXQ7LbFRMOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeaGnnW7X1dlSXPryvxFScuS32eq9AAALgmwAC6EdBSzRkwyGzlfuvOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeamnnW8N2H_Klr1JTQNeFfBlGP8auAALhmwAC6EdBS2-Hmw14Frx2OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIebGnnW9GgYGzoHgb6lrL7iyJFCQvjAALimwAC6EdBS2yyKnJE-zqhOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIebmnnW-Dc72Pnw_3ayDFenHST2UsuAALjmwAC6EdBS8NLfv93Io3DOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIecGnnW-4KzOXTo1bnl_14rT2RuhVmAALlmwAC6EdBS9vUuQ_P4g40OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIecmnnW_1VkVNhWiFa49jBO6mdTC2MAALomwAC6EdBS0teziNmHN0WOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIedGnnXAsTXnMmu8gVhjh6vYZEnvCZAALpmwAC6EdBS-VdjHS4GytHOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIedmnnXBjWWA67dy14XgrYU0udR3kyAALqmwAC6EdBS9oiZT3eidZnOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeeGnnXCMgctTJZfCaC9FcGr1-HL74AALrmwAC6EdBS8paWKnqwTbjOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeemnnXDNRQXallOla6MMx1P_jTdrfAALumwAC6EdBS71K2ODwJRqiOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIefGnnXEGuzCDESLLWPKVXyH3SCF52AALvmwAC6EdBSwABL4FEBuOI_DsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIefmnnXE8mrbGdq8AsEIMiZED53CzpAALwmwAC6EdBS8FOJQVFskASOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIegGnnXF_Av9PgzVFW3Lto9uAF_EQbAALxmwAC6EdBS2AgmnCwPiEXOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIegmnnXG15KK4mv1jCl4f9IpkjDucRAAL0mwAC6EdBSwJatQz1zEJIOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIehGnnXHrXnpUbWpxw4JQW6oGr3BB7AAL1mwAC6EdBS3QbpW8l0jnIOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIehmnnXIhUMPbsPgu0yvcVfBdYqSKBAAL4mwAC6EdBS4e_PxP89gvqOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeiGnnXJb3nzwk9Ke1fLMe91b3a7VbAAL6mwAC6EdBS5NXIg61BnA_OwQ",
                    },
                    
                ]
            },
            5: {
                "title" : "Сезон 5",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIeimnnXZLfeOOG7uwN3fRcHUq5rYBMAAIGnAAC6EdBS6Yij1UxXxgEOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIejGnnXaKuW4_XVZNXKQUHBsnxjj_5AAIInAAC6EdBS42UGeIJkeDROwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIejmnnXa9PtreICUM0564pc6Fc1NGqAAIMnAAC6EdBSz-YfiFfE8x4OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIekGnnXb0GbC9QMGm9oIdUGwRkpDU8AAINnAAC6EdBS5J61K37lC9TOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIekmnnXct1WIFBV3LxJFO1gT1vp3xNAAIQnAAC6EdBS579foe1AAHpHTsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIelGnnXdo_-saCVUqaCfODQqb0Xd0nAAISnAAC6EdBSwZ-aR2pvlpnOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIelmnnXejZIa2eUNqLqu9ohHKSLzFFAAIUnAAC6EdBSyNWHFyIPI-5OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIemGnnXfYpzhchS6nhV1abBt5iqAvhAAIVnAAC6EdBSxZyDlCayirWOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIemmnnXgqFlEvj76TjJFeihfC1pln-AAIWnAAC6EdBS0EIzltOk22cOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIenGnnXhu6m0YRaKkukk-qaiBodI1QAAIXnAAC6EdBS8jr88lRQ048OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIenmnnXixpNw9Me0H8if3eOmB1A1bLAAIYnAAC6EdBS9aNVxrfBJRDOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeoGnnXjtHGao0NGb3d5S_vf7E59cmAAIcnAAC6EdBS_SA6R-fFJRnOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeomnnXkmiXmhykCJqZrTFJA7tRSTjAAIdnAAC6EdBS5BNqF_O6VE7OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIepGnnXlm1TKKMRqyKoEMiapK93iLyAAIfnAAC6EdBS1nck05UW82IOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIepmnnXmiJ3A_7HlDVjU-O_Q2U0bBfAAIhnAAC6EdBSxMq_91bEUrOOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIeqGnnXnYZBKFn-ZoDg1UBIU96P4hPAAIinAAC6EdBSw6kba2hlsp5OwQ",
                    },
                    
                ]
            },
        }
    },
    "104": {
        "title": "Атака титанов",
        "year": 2013,
        "episode_counter": "88 серий",
        "description": "Уже многие годы человечество ведёт борьбу с титанами — огромными существами, которые не обладают особым интеллектом, зато едят людей и получают от этого удовольствие. После продолжительной борьбы остатки человечества построили высокую стену, окружившую страну людей, через которую титаны пройти не могли. С тех пор прошло сто лет, люди мирно живут под защитой стены. Но однажды подростки Эрен и Микаса становятся свидетелями страшного события — титаны нападают на город. Мальчик клянётся, что убьёт всех титанов и отомстит за человечество.",
        "poster": "AgACAgIAAxkBAAIdD2nj5SXDo_XqLsEHyEw2YqO8gRHDAAL6FWsbcmogS5jkuMO99YZeAQADAgADeQADOwQ",
        "country": "Япония",
        "director": "Хадзимэ Исаяма",
        "genres": ["аниме", "фантастика", "боевик", "драма"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIbeGnfZHtqcE8P8aAhybwlWg3fVxhXAAKqlgAC_8j4SmqMQ5izesWUOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbemnfZTfsx3dJ_H6ngt_wUh2jurVDAAK2lgAC_8j4StkVGpW9zDwfOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbfGnfZe6bh0Sv6P-mcjTZwRkM1IRRAAK7lgAC_8j4Srjv2efWVnx0OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbfmnfZqLBkr40cFVt8ey6anrtHnT_AALBlgAC_8j4Sl27F3eoiBMtOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbgGnfZ3VuDg8nvKhv6P6ZUm86j1WDAALKlgAC_8j4Sk6tem1nJXkGOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbiGnfaEX78edfJUFwZjZmQ-ttjXDHAALNlgAC_8j4SjkdqujqyoAzOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbimnfaQ-8N7KCj92rJVoaDzZoLP4wAALTlgAC_8j4SmSOI6WkkiqHOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbjGnfadHdNFFjNT8EBy65UsF5GxSJAALVlgAC_8j4SlOGEOO5S64mOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbjmnfapdaHAcmNz9gCA3dxP3IwcXVAALalgAC_8j4Sip0FMN-V5tROwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbkGnfa20C2GAXndvH0eK2ZiTy96MlAALnlgAC_8j4Sjx0__2p3k5uOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbkmnfbFnJPz28Igx_Sk9XyYP961yvAALzlgAC_8j4Sp3z0jZQl29GOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIblGnfbR0nyv8YLb0w6jZ8NW7t9cz4AAL6lgAC_8j4SoLZRCHG2jCeOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIblmnfblT46-89-6pKsCk4L3scC6w_AAOXAAL_yPhKyN8878eOd4A7BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbnGnfb2F3BUvkp-xn4HS5nmI0b6rNAAIIlwAC_8j4SrHTy2aIG_TvOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbnmnfcENTwzbcNBdkVtYmoFM161ZgAAIOlwAC_8j4Sl2f_3ZnAjWgOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIboGnfcR7Ny3o3-hedAAG-3ftJTJTNJQACFZcAAv_I-EqE0u0-NKRRBjsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbomnfceYt_Sc2xNqeu5XMPPlQPsgQAAIhlwAC_8j4ShK1yV7brdCzOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbpGnfcrBxV-wJJjvDebUowA7djj0vAAIqlwAC_8j4SklWxmkEKDcfOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbpmnfc3R0xY16ejBi6Q8eYbT4ZvciAAI3lwAC_8j4So8n-hBHR9VxOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbqGnfdB5WXcvghtH5_oHk3sfXaUMLAAI_lwAC_8j4SslP6ovxI2X_OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbqmnfdOC-Ctk6madf81P84GZ2X_JUAAJDlwAC_8j4StdFy09sBNUCOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbrGnfdbxu2TUshGxpRz_8sQZYyfayAAJTlwAC_8j4SjwqZt7qND5zOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbrmnfdoEAAQ9ZLtMG86OeSUAPHok2gwACXpcAAv_I-Ep4noI5HcljnzsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbsGnfd1M42ZLgL9FIqeRIxu1Uy878AAJklwAC_8j4Sip7AytM3LOZOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbsmnfeAZwFUlX2awOK6A8mfv-u7oWAAJnlwAC_8j4SqxmTEnTpQzsOwQ",
                    },
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIbtmnffETvggIlQ0ZLYCx5ILhRbCauAAKblwAC_8j4StrFx70du035OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbuGnffPevhBA7d4rEjuJkxG04lncLAAKnlwAC_8j4Sk7EJdA1kfd6OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbumnffeSkXu3z95D7EhFWIxPW6xf3AAKwlwAC_8j4SgSrXYuQU6StOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbvGnffq2M_stxiE_CtV5rY48QxzByAAK2lwAC_8j4SvO3xgqyefrCOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbvmnff4g96HyQuhiBhmKIurmyTCScAAK5lwAC_8j4SnSVS9ViF81rOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbwGnfgFHBM0L7SRfcO1K0ivASayw6AAK9lwAC_8j4SjHpwBq1sRbGOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbwmnfgRF0s4minoEd5uml74OqSnpnAALDlwAC_8j4So2CAAEDAgRJizsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbxGnfgdUSdCclVDI-fV7UlE3FLwO3AALLlwAC_8j4SiQ0HQ2ZKNj1OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbxmnfgqnKvTYyKEpXTdWKugPlU_10AALOlwAC_8j4SvJHrn1VvER2OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbyGnfg232iRpoouzfgSrZUWjUNGTyAALSlwAC_8j4SjRAAldcj2z0OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbymnfhE6LiO05WOdayAX_FXDKrhKDAALjlwAC_8j4Susm1XqKcP4iOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIbzGnfhRFO-_NEN9-ro_jzKDas5k2sAALylwAC_8j4SvTaFQMM8BZ5OwQ",
                    },
                ]
            },
            3: {
                "title" : "Сезон 3",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIbzmnfiWcLXPP0FIv0_zOIKlwDUKmnAAItmAAC_8j4SkQJPsZJTRUXOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb0GnfiiA7cCfl72XfIn2g0e4WqIPtAAIxmAAC_8j4SrIE1hqqFo55OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb0mnfitETGDWtFE8k-QkbL0pegdxQAAI5mAAC_8j4SurniLY_2SmqOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb1Gnfi5QQiEgfhQWXnOYjxE9ChGTuAAI_mAAC_8j4Srv2lPq327hGOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb1mnfjFizU-cOMrnNPuZQ6IG4SbjMAAJImAAC_8j4Sm_nmsXX4ZxFOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb2GnfjRbYfSgpmJVeaUCiGLZMjVF-AAJOmAAC_8j4SnIHc6BT0XXSOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb2mnfjdzDH5eBlNk6Wjb2U067-BHxAAJVmAAC_8j4SkXFcxVqZtRLOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb3Gnfjpt-utS6UP8gPotmrG783iwAA1qYAAL_yPhKsbZdGFRsOaY7BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb3mnfj1kt2lCQRKDE5cXIJmoO4OHPAAJrmAAC_8j4SoPsrNMBzVIBOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb4GnfkBOOL6NLUQOCH1Ap5Orx_XFpAAJzmAAC_8j4Sp-9cE9EP9qYOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb4mnfkMJfspmiPhFln_PvdDTYOgLAAAJ4mAAC_8j4StFgp077Q3fkOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb5GnfkYpipPUvZtkBhH8schy62Da7AAKEmAAC_8j4StCdJQO4FPfJOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb5mnfkkCb-DvioEeyyoE2ywRz4nw6AAKPmAAC_8j4SuKv5fkqVJ4eOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb6GnfkwST2qUFjxpiDY7duB-G6OE5AAKhmAAC_8j4Sgz_C1QJyw__OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb6mnfk7-m9-w9yQGyQ4NF3IT1XODWAAKvmAAC_8j4Spj18xlfDiC4OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb7GnflHNHRCY4-IQZmSCNYdjuEmHSAALCmAAC_8j4SjgWmtj5Y5QbOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb7mnflSSXmvPLxrRmD-pDth73zzPNAALPmAAC_8j4SuNnqxicbqc1OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb8GnfldU1C_XpNAecIupg-4dN1moAA9eYAAL_yPhKVe7e4LbcA2I7BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb8mnflof5-Ldde5kl-1RbEiM8jtU-AALZmAAC_8j4Soll9r8OSqW3OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb9Gnfly97l7aZevl31l2qp3QmvylVAALjmAAC_8j4SiYYt8IIEjnSOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb9mnfl-EpX_MJVuwuVJW0VZXZcZvTAALpmAAC_8j4SusEmZi747nAOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb-GnfmPNRp8wrGnQgz-lnAi-vEkp_AALxmAAC_8j4ShNW-P5oo41UOwQ",
                    },
                ]
            },
            4: {
                "title" : "Сезон 4",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIb-mnfmfVwsEeysLDVqUoIBW0di2x-AAL1mAAC_8j4SuPsb2MwlwABVTsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb_GnfmqezRdt0YlGtdLS32hz_PgZLAAOZAAL_yPhKYKOAJwp4yFI7BA",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIb_mnfm0-S9rrX03F5JE6sHON0SQ6BAAIPmQAC_8j4SqB02V8BT33hOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcAAFp35v3DPNSA_rpd2UVfziLPMqxnQACF5kAAv_I-EpytbsVzxn1hjsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcAmnfnJBjBQknR-SYCCqTjpVymnAkAAIgmQAC_8j4Sj41qfUkPQHfOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcBGnfnUjHHF1Lp9CspQlsy2lAUfsRAAIrmQAC_8j4SkSv0gUtv4nwOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcBmnfn6-ZrHF0jgVkP0UsCfV-NrojAAI5mQAC_8j4Slw6LaGHreg5OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcCGnfoGFoicwNra7p_0EeFI0Z9ZMyAAI8mQAC_8j4SpPWgcP7fx1dOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcCmnfoQhK6AKNMMGHIq-4PJdKBNNDAAJDmQAC_8j4SgABYp5V--nETTsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcDGnfobLzrIIb-VULvZNUVkLpi8N-AAJNmQAC_8j4SnjhUO3cxCoOOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcDmnfokEShcXRwN8IhEc64DKwWp7xAAJQmQAC_8j4SoZVTP8mg9ZhOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcEGnfotNqxv5QFok_893B7Pg0FUR4AAJSmQAC_8j4Suz2l3dbkxeTOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcEmnfo2OT3dlI692MhvgjZ0ovrpQSAAJTmQAC_8j4SsMZMCS81rauOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcFGnfpAKMzQvskVirgV4GfYbHQo52AAJXmQAC_8j4SjKO3Z83tb__OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcFmnfpJ7rBwQQhPkMGzL8F35jSoYBAAJomQAC_8j4So5qCjDeJypjOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcGGnfpSJgg5-hDzOq_NxmUBIQ_WPqAAJ3mQAC_8j4So_O58gP5B6aOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcGmnfpb3Id64yoHcd7x6M7L767a5qAAJ_mQAC_8j4Sqk57BPq1yGZOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcHGnfpl9kBaB8VgSlxuZHvLDQyJoIAAKHmQAC_8j4SuzESux1lQjgOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcHmnfpwJAoX6jnYDb1eHO7SA9xRb-AAKUmQAC_8j4Smt6yk8S2-AUOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcIGnfp7GkC5ifwycfMDQvd_vGwW5WAAKcmQAC_8j4Sh8rCQLZLkgfOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcImnfqFUuCTsVRsKcefLmLGjYNgQMAAKjmQAC_8j4SunwclFfn9mdOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcJGnfqPHRbq2RI8esWFVOsirKDcfOAAK1mQAC_8j4SrGpta7tI1g9OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcJmnfqYKSVczp5uQE5SFMkiJuyZ9_AAK9mQAC_8j4SuL_Awh0M7HAOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcKGnfqhGtTX_ybHQW2Z8Ti8NUJChtAALFmQAC_8j4Si2i4Ku3malGOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcKmnfqqvLUbewBRkMmQTXmn2pE61lAALKmQAC_8j4SlJVEYhjNnLeOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcLGnfq1QbThi1_8sl8s_B77KEjUrsAALPmQAC_8j4SvuGfXEd6cacOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcLmnfq_apjhU83qdlMsJ8K2fT5H9QAALTmQAC_8j4SonZVqKFRsOzOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcMGnfrKNXy7e0X3Jfg-eWEwL4X24iAALcmQAC_8j4Sg6ltH1VqC1ZOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIcMmnfrVac-8z2skj753lIxA-ed7EuAALqmQAC_8j4Sg0CbXLvDp9IOwQ",
                    },
                    
                ]
            },
        }
    },
    "105": {
        "title": "Тетрадь смерти",
        "year": 2006,
        "episode_counter": "37 серий",
        "description": "Старшекласснику Лайту Ягами в руки попадает тетрадь синигами Рюка. Каждый человек, чьё имя записать в эту тетрадку, умрёт, поэтому Лайт решает бороться со злом на земле.",
        "poster": "AgACAgIAAxkBAAIf5GnpHkO3XDPYNrpPQVPO71fGTr0RAAI9G2sbNx5IS_nXz6T_BjZYAQADAgADeQADOwQ",
        "country": "Япония",
        "director": "Madhouse",
        "genres": ["аниме", "детектив", "криминал", "фантастика", "драма"],
        "episodes": [
                {
                    "video": "BAACAgIAAxkBAAIe6Gnos5NsHuc6B7qqJONm5hzXWhH4AAKimQACNx5IS815-Tu1FLvXOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe6mnos6HEvRNM4v2dsPifwHhFupAyAAKkmQACNx5IS70IoWUtJZnEOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe7Gnos6xsw28fH45k7l4nWsXtt_YuAAKmmQACNx5IS4u0iCGXBzj4OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe7mnos7hluQWdzhI3ckRT2Sv0Dl9NAAKqmQACNx5IS2A80DIpx1UPOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe8Gnos8S0mCpuDb3i-2p0yayTbcgxAAKrmQACNx5ISwKhgObMjMzGOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe8mnos9FGkVdqGxEkFYmaq20eBQmwAAKsmQACNx5IS8pyyb5rsrh1OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe9Gnos94uM0IkfY6fi8PmyaK2zEYtAAKtmQACNx5ISxNtm3mfIruJOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe9mnos-38ugaoikoPTW2302ZUU3EbAAKvmQACNx5ISxaKdfM_bX02OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe-Gnos_svLTSGDy-cQPpCJUS847BZAAKzmQACNx5IS-7ItPGBvP3OOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe-mnotAjEHKk9EuuTavGkwzTVpcm3AAK1mQACNx5IS5Dw7YBKmYiVOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIe_GnotBdwWdnpHMgAAQsc0CUu1geBYgACt5kAAjceSEuePyQH-KHDqjsE",
                },
                {
                    "video": "BAACAgIAAxkBAAIe_mnotCPqceu-EmMgZHzIGcroC29XAAK4mQACNx5IS9gwJ7Zn7k4pOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfAAFp6LQv2ripShST2OFIAAHl11PD_AIAAryZAAI3HkhLUGjkB78IdC07BA",
                },
                {
                    "video": "BAACAgIAAxkBAAIfAmnotDuA-AehkzDkcjX42gABdgJPFgACvpkAAjceSEusm2i71SKXMDsE",
                },
                {
                    "video": "BAACAgIAAxkBAAIfBGnotEgcBbHY_PBON_n0mW-arcaKAAK_mQACNx5ISyFtbrvs2ftYOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfBmnotFXSBAhVefr-TofGz_OwfCulAALCmQACNx5IS8Fhe1HG3pnNOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfCGnotGNTLQ24vllMMFBY5L7QKHRaAALEmQACNx5IS000ptUOuMzyOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfCmnotHDruaxEhK0eA6mXiNvDti2mAALJmQACNx5IS8Q4_HPq2S-aOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfDGnotH1xlyvGgamgsIr4QBfiPx0NAALNmQACNx5IS-gxD1YVf9KcOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfDmnotIp7EPm0yd-lJ5unvoYqoQ6pAALQmQACNx5IS2IMrMvUNdzXOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfEGnotJWsf_Np37W7mqn0sxLphd_CAALRmQACNx5IS0Gi7S1tET_kOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfEmnotKHizLpgmDQ_d4l59xRmBTshAALSmQACNx5IS51T1mbYrYs_OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfFGnotK5KhDBS8d0EgYW4BLkmUjvLAALVmQACNx5IS8PhC449bY9POwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfFmnotLoBBmsJ-dJfuRA4OWTNDgcPAALYmQACNx5IS1bpDKO03UkaOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfGGnotMrvDPZCvaVbVr6CLa2kKQPxAALamQACNx5IS5HpYN2ogynEOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfGmnotNgFD30SzJfBMzB-LirS8czqAALemQACNx5IS4TBk_u_MfPSOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfHGnotORSqTDjzJVGgEohoYmqTBmMAALgmQACNx5IS47V98c_rJzcOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfHmnotPJ301VoRMKNcvsCBP02ZQABywAC4pkAAjceSEsRpDU0cRcT8jsE",
                },
                {
                    "video": "BAACAgIAAxkBAAIfIGnotP8q-aNPcD3VPgAB-AABk_Yhf1UAAuWZAAI3HkhLHymLQweHXRs7BA",
                },
                {
                    "video": "BAACAgIAAxkBAAIfImnotQxCqvLPbdAb7xnS2N9JUAcJAALnmQACNx5IS7VDtD6Kjs8GOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfJGnotRtjzWwvrjXWOIKkOKbevBBoAALomQACNx5IS2DLtDou4DvtOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfJmnotSpSWSFS0ti39Xor5Qr1_hRjAALqmQACNx5IS055kVKT15fxOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfKGnotTjk1KUgxSUwR5QAAclG8RLJkAAC65kAAjceSEu9hjRWfCfm_DsE",
                },
                {
                    "video": "BAACAgIAAxkBAAIfKmnotUUdl3OA2G2msypGLfH3FARHAALtmQACNx5IS5UySl-ENuB-OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfLGnotVONFAAB56JW56YJrszRCoLaywAC8ZkAAjceSEvIn4QYnC7_2TsE",
                },
                {
                    "video": "BAACAgIAAxkBAAIfLmnotWNJxydhiktBER8LbopjsHe1AALzmQACNx5IS7bsWR3vW7sdOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfMGnotXGu_pkT2BW4AAFssmvOZchXdAAC9ZkAAjceSEsS8Prm4vGFyTsE",
                },  
        ]
    },
    "106": {
        "title": "Эхо террора",
        "year": 2014,
        "episode_counter": "11 серий",
        "description": "В один из летних дней в Токио произошел крупный террористический акт. Виновниками террора, который разбудил самодовольную нацию ото сна, были всего два мальчика. Теперь преступники, известные как группировка «Сфинкс», начали грандиозную игру, которая охватывает всю Японию.",
        "poster": "AgACAgIAAxkBAAIf5mnpHmLTl_7sdUtOt1nKkVFSUrRWAAI-G2sbNx5IS-_U5b9AR1TLAQADAgADeQADOwQ",
        "country": "Япония",
        "director": "MAPPA",
        "genres": ["аниме", "криминал", "драма", "детектив"],
        "episodes": [
                {
                    "video": "BAACAgIAAxkBAAIfMmnoxWgebcw2lCRIbe42i1sIEC-gAALNmgACNx5IS-vmkxAKSZOBOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfNGnoxZZXIFI3X4KJA8fyJN6CgR6tAALQmgACNx5IS9nAt7GLeut4OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfNmnoxcyOkDflthIGKwqg8RpRn4kEAALXmgACNx5IS4dPExybyXDxOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfOGnoxe2tJ67vegjYBEeMx7koxeB1AALamgACNx5IS9tcHKx0sj6POwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfOmnoxhnC2gABsBRUAVaJFJanksuDpAAC3JoAAjceSEs5dYB2qKSTyjsE",
                },
                {
                    "video": "BAACAgIAAxkBAAIfPGnoxj5UZKA1nv0LI05kMD7SeKDwAALemgACNx5IS98u_mGqwrjDOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfPmnoxm-v_bRDwlbx9X3z9KQyEl6AAALgmgACNx5IS3eVKrL9e8d_OwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfQGnoxpat0NvCcmTwwyhT3tNZbeE3AALlmgACNx5IS9DkF0JpaKXnOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfQmnoxruSwk9Jg440AvwzWS78ZYPoAALmmgACNx5IS8Kpj7rwLIBmOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfRGnoxuCupNREmEt6n-2OZjt1rX0DAALpmgACNx5IS9jFIgn4lyfQOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIfRmnoxwQWB7-Gf3TUz_DpO-EKdTF0AALrmgACNx5ISyLKD5OdGvB1OwQ",
                },
                
        ]
    },
    "107": {
        "title": "Бездомный бог",
        "year": 2014,
        "episode_counter": "25 серий",
        "description": "Малоизвестный Бог Ято не имеет собственного храма, но мечтает стать уважаемым божеством с миллионами верующих. Правда, Ято не особо стремится прилагать усилия для достижения данной цели. Однажды обычная школьница Хиёри спасает его от дорожной аварии ценой собственной жизни",
        "poster": "AgACAgIAAxkBAAIf6GnpIMUVVZsse9gT8EgPqzKdaS-4AAJKG2sbNx5IS8ANlz1Us35iAQADAgADeQADOwQ",
        "country": "Япония",
        "director": "Bones",
        "genres": ["аниме", "фантастика", "драма", "комедия", "боевик"],
        "seasons": {
            1: {
                "title" : "Сезон 1",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIfVWnozebM8Tj_OnZGnHTmPaygYHoTAAJFmwACNx5IS4LcQ44h2wnpOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfV2nozhD6GsQvcrud5tWLQCCwbZYIAAJImwACNx5ISxwnVKAli95qOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfWWnozjhZ6j6ioaK414IXocot9ge-AAJLmwACNx5IS94GOuP_KSx9OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfW2nozmGLDGo9FMUcduX_O3fGohTfAAJOmwACNx5ISxKq2z05ivC7OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfXWnozopMlwrsYu9MwRV4rLI81PBIAAJRmwACNx5ISzy3_TDDBiiROwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfX2nozrSKyO6BL_UvVvrk2DGH4ZuWAAJTmwACNx5IS2mwKqKDs0fkOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfYWnoztyqtC8ObyX62kEWTj1hT1xUAAJXmwACNx5IS4pl_RB38AQwOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfY2nozwPJmoOXeJtVtGi5CkGxsaYQAAJamwACNx5IS-Q8KaeM7TgEOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfZWnozysLWiDgylvEkS4US4v5HwK5AAJbmwACNx5IS061aM7Fs4HEOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfZ2noz1Z4ub0nV3zeD6Q6ZEYgrZhHAAJdmwACNx5IS2dgiTjboatTOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfaWnoz4JbErSh5HHqF8Sfkaka1lI3AAJemwACNx5IS_HbbC8AAVdGqTsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfa2noz6nnLlssGJI5vxNhPiBopJXqAAJhmwACNx5IS1GQf7f1pCamOwQ",
                    },
                    
                ]
            },
            2: {
                "title" : "Сезон 2",
                "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIfb2no0AilVDzjlCI15R8JyXQmSlOQAAJomwACNx5ISzuPpGoLPtixOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfcWno0DYI8jlngF2Ek7xZLbhpw7c-AAJtmwACNx5IS9Nd7zOzzlw9OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfc2no0F0f932Tt776F8RWx1CBl3bVAAJzmwACNx5IS2shc_vwvO-TOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfdWno0IQqHv7h2H2bY-RrkEUkpHVCAAJ3mwACNx5IS5bNIe8-5_waOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfd2no0LDXl5ysh0dyVhzb7DU-xi8hAAJ8mwACNx5IS22WUI_gT0THOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfi2no2qODrKFYmz_QFVTb58mzgJtNAAItnAACNx5IS3KVisplNlByOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfjWno2rJ6r96sINkuhaMQlpG2reLLAAIunAACNx5IS9TXufWuf83UOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfj2no2vGYtGnFUV9jVjjLSjibbIBsAAIwnAACNx5IS-2fKtKRfXv9OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfkWno2wywhVEll_yO_ONboYVxDGUxAAIynAACNx5IS5g5mUeKILM8OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfk2no2_JMpuUJY46dEfkC9sR70lzzAAI_nAACNx5IS7605a_BYblqOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIflWno3STlrjyGZTi2yunhb8Z2K4oTAAJVnAACNx5IS91gI3485h61OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfl2no3V7Hd4JDDyIFQ1Bsr27dmmrCAAJZnAACNx5IS5NO_2FFAib2OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIfmWno3X3jQSQFlnQYkpBHNMojdGfeAAJgnAACNx5IS4G7G6AkD-X0OwQ",
                    },
                    
                ]
            },
        }
    },
    "108": {
            "title": "Дневник будущего",
            "year": 2011,
            "episode_counter": "27 серий",
            "description": "Амано Юкитэру — типичный изгой, одиночка. Все свое время он — безучастный наблюдатель, делающий записи в мобильном дневнике об окружающих событиях. Единственного постоянного собеседника, бога пространства и времени Деуса, Юки считает плодом своей фантазии. Однако всё меняется, когда Деус наделяет Юки, а точнее его дневник, вполне реальным свойством показывать события ближайшего будущего. Парень узнаёт, что подобными дневниками владеют ещё одиннадцать человек, и все вместе они являются участниками жестокой игры, выжить в которой суждено лишь одному.",
            "poster": "AgACAgIAAxkBAAIf6mnpKwEY58tnaf9mDFc8AVKOhtYlAAKPG2sbNx5IS25eYo7nB3ukAQADAgADeQADOwQ",
            "country": "Япония",
            "director": "Asread",
            "genres": ["аниме", "фантастика", "драма", "криминал"],
            "episodes": [
                    {
                        "video": "BAACAgIAAxkBAAIgGmnqF1-uqJnVt9NpOJy1pKBU_pJ7AAKZnAAC7_9QS1-CdpcXK7kZOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgHGnqF5JHeTu8ixrACW7KRepbiSqNAAKcnAAC7_9QS8ObLmCJJgs2OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgHmnqF8wGaQOXzZu7fjA4GrS8KTqnAAKdnAAC7_9QS5ZRgx7X4OAdOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgIGnqGAYi2uqZi_o4VoEU4Lv6zfa2AAKenAAC7_9QS82oBMe0TkZtOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgImnqGEJ43CkO6JOz8tVNf6KiLodqAAKgnAAC7_9QS9c9KfQ01ojtOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgJGnqGHWA5vZFkLmwHsAC0vI2L0NVAAKhnAAC7_9QSxccP5cxDAyBOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgJmnqGIaQftJa4FY4m-dMd59yxx6pAAKinAAC7_9QS9wO7b8YoEP_OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgKGnqGJek1pFFcGIdMqlqbTV5QstWAAKjnAAC7_9QS2K1R4-5a0jWOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgKmnqGKruoVOQtJXfys6ncyiHoARAAAKknAAC7_9QS9Ot20sk7SVLOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgLGnqGLtlfqMYk71ogDWCj_wz3Lj4AAKmnAAC7_9QS1dQNAvhQ8JZOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgLmnqGM3zsVSrtZVsXhCqGvzT5SEpAAKnnAAC7_9QS-Z2Ek85oyOnOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgMGnqGN23Dn7FCBY_SZvmwpRddVB8AAKonAAC7_9QS44uiVe3_82XOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgMmnqGO9AydTs1LOiXaz0VbLJ-XmxAAKpnAAC7_9QS7X9YHkJINQIOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgNGnqGQABvW64-kEZA2o1E4JFD9gSVAACqpwAAu__UEuEUjtTPD83RzsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgNmnqGRE7FuQPxfYyRAsn3sBsWmh6AAKrnAAC7_9QS-2iWUN44qH1OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgOGnqGSPPDbUjUSQsnFCU13-4bMNxAAKsnAAC7_9QS12Ut8TrP4FOOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgOmnqGTUX0egpX7kcuusswpJni4irAAKtnAAC7_9QS9W7VO72lA4yOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgPGnqGUc17SKIAAFwwkiwDP2iWb-yAgACsJwAAu__UEvXo6sjnIl8ojsE",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgPmnqGVpDsuCArJiUqj37O3sHDGmwAAKynAAC7_9QSyNTQTtoONglOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgQGnqGWzgX7lUDm5uqxWooIlfRozVAAKznAAC7_9QS3MjjgOdHm5rOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgQmnqGYDZmxohQgbu7WtqT1mlykXsAAK0nAAC7_9QSz9eO7XYDGBMOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgRGnqGZK5MJrHcJ_gT7PokfsFZqJVAAK1nAAC7_9QS_al-9KXg6xxOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgRmnqGabvgk78h8JOfrQrzmHIRIVQAAK3nAAC7_9QSzb21Yam2VKPOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgSGnqGbdJOYysvmdmr-ry3C2G1K_GAAK6nAAC7_9QSz402qjaQ1--OwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgSmnqGceSpelP3dpnvlCrrmcy7xXDAAK7nAAC7_9QS6RK4Gf63PRcOwQ",
                    },
                    {
                        "video": "BAACAgIAAxkBAAIgTGnqGdmqPkKRqFJ9UCX7Y3z9y1QlAAK8nAAC7_9QSxQ3ojgscTHtOwQ",
                    },
            ]
        },
    "120": {
        "title": "В поисках Аляски",
        "year": 2019,
        "episode_counter": "8 серий",
        "description": "Шестнадцатилетний Майлз Холтер оставляет свою скучную жизнь с родителями и отправляется учиться в новую школу Калвер Крик в поисках «Великого „Возможно“». Здесь он находит первых друзей и влюбляется в девушку по имени Аляска Янг, которая переворачивает его жизнь.",
        "poster": "AgACAgIAAxkBAAIkg2n13n0NGo6L0UiS3Ux5O6xFjBnYAALWFWsbe9CoS5PUdonmNlMeAQADAgADeQADOwQ",
        "country": "США",
        "director": "Джон Шварц и др.",
        "genres": ["драма", "мелодрама"],
        "episodes": [
                {
                    "video": "BAACAgIAAxkBAAIiuWnyFOGeNJ_uPtgK-tIyFQxftb7mAAJNnQACzDeRS3joi5ms0yCsOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIiu2nyFRnlncmfBGRo9-UDC_vqSnUGAAJPnQACzDeRS-sjrjr58SleOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIivWnyFU_wURuID8cjiGVr_Z5xTQL1AAJUnQACzDeRS_Qwu5lzSNrdOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIiv2nyFZmluzXyhpwjm5Kh98bt6RoxAAJYnQACzDeRS-34WTpdGYEcOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIiwWnyFcmJBVzpagNgmyv1LTcFpVJTAAJanQACzDeRSxVwYIboLfQEOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIiw2nyFfGqw2YmFLImNMWFb55rh75WAAJinQACzDeRSwm1g4kEBluVOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIixWnyFh1LOg1YlGmznAO-v_W2_m5hAAJknQACzDeRSwjN0Pw0wuwMOwQ",
                },
                {
                    "video": "BAACAgIAAxkBAAIix2nyFk0R_T312tm9xHKlnfHdQDmwAAJlnQACzDeRS86K6fXNq1P1OwQ",
                },
                
        ]
    },
    # "000": {
    #     "title": "",
    #     "year": 1,
    #     "episode_counter": "",
    #     "description": "",
    #     "poster": "",
    #     "country": "",
    #     "director": "",
    #     "genres": [""],
    #     "episodes": [
    #             {
    #                 "video": "",
    #             },

    #     ]
    # },
    # "000": {
    #     "title": "",
    #     "year": 1,
    #     "episode_counter": "",
    #     "description": "",
    #     "poster": "",
    #     "country": "",
    #     "director": "",
    #     "genres": [""],
    #     "seasons": {
    #         1: {
    #             "title" : "Сезон 1",
    #             "episodes": [
    #                 {
    #                     "title": "",
    #                     "video": "",
    #                 },
                    
    #             ]
    #         },
    #     }
    # },
}

def subscribe_keyboard_movie(code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Подписаться", url="https://t.me/kinonawe4er")],
        [InlineKeyboardButton(
            text="🔎 Проверить",
            callback_data=f"check_movie:{code}"
        )]
    ])

def seasons_keyboard(code: str):
    serial = series[code]
    keyboard = []

    for season_num in sorted(serial["seasons"].keys()):
        season_data = serial["seasons"][season_num]
        season_title = season_data.get("title")

        if season_title:
            text = f"{season_title}"
        else:
            text = f"Сезон {season_num}"

        keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"season:{code}:{season_num}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"serial:{code}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@dp.callback_query(lambda c: c.data.startswith("seasons:"))
async def seasons_menu(callback: types.CallbackQuery):
    _, code = callback.data.split(":")

    await callback.message.edit_reply_markup(
        reply_markup=seasons_keyboard(code)
    )

    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("season:"))
async def season_selected(callback: types.CallbackQuery):
    _, code, season = callback.data.split(":")
    season = int(season)

    await callback.message.edit_reply_markup(
        reply_markup=series_menu_keyboard(code, page=0, season=season)
    )

    await callback.answer()


def has_only_warning(item: dict) -> bool:
    return "warning" in item and len(item.keys()) == 1

def normalize(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^\w\s]", "", text)  # удаляет знаки препинания
    text = text.replace(" ", "")
    return text

def has_seasons(serial: dict) -> bool:
    return "seasons" in serial


def get_episodes(serial: dict, season: int | None = None):
    if has_seasons(serial):
        if season is None:
            season = min(serial["seasons"].keys())
        return serial["seasons"][season]["episodes"]
    else:
        return serial["episodes"]

def search_movies(query: str):
    query = normalize(query.strip())
    results = []

    for code, movie in movies.items():
        title = normalize(movie.get("title", ""))
        if query in title:
            results.append(("movie", code, movie))

    return results

def search_series(query: str):
    query = normalize(query.strip())
    results = []

    for code, serial in series.items():
        title = normalize(serial.get("title", ""))
        if query in title:
            results.append(("series", code, serial))

    return results

def search_by_code(query: str):
    query = query.strip().lower()

    if query in movies:
        return [("movie", query, movies[query])]

    if query in series:
        return [("series", query, series[query])]

    return []

def search_by_title(query: str):
    query = normalize(query)
    results = []

    for code, movie in movies.items():
        if query in normalize(movie.get("title", "")):
            results.append(("movie", code, movie))

    for code, serial in series.items():
        if query in normalize(serial.get("title", "")):
            results.append(("series", code, serial))

    return results

def search_all(query: str):
    by_code = search_by_code(query)
    if by_code:
        return by_code

    return search_by_title(query)


def search_results_keyboard(results):
    keyboard = []

    for item_type, code, item in results:
        emoji = "🎬" if item_type == "movie" else "📺"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {item['title']} {(item['year'])}",
                callback_data=f"open:{item_type}:{code}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)




ITEMS_PER_PAGE = 6

# --- Получаем все жанры ---
def get_all_genres():
    genres = set()
    for movie in movies.values():
        genres.update(movie.get("genres", []))
    for serial in series.values():
        genres.update(serial.get("genres", []))
    return sorted(genres)


# --- Кнопки для жанров ---
def genres_keyboard():
    keyboard = []
    for genre in get_all_genres():
        keyboard.append([
            InlineKeyboardButton(
                text=genre.capitalize(),
                callback_data=f"genre:{genre}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- Фильтруем по жанру ---

def find_by_genre(genre: str):
    results = []

    for code, movie in movies.items():
        if genre in movie.get("genres", []):
            results.append(("movie", code, movie))

    for code, serial in series.items():
        if genre in serial.get("genres", []):
            results.append(("series", code, serial))

    return results

# --- Получаем страницу ---
def genre_page(genre: str, page: int):
    items = find_by_genre(genre)
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    return items[start:end], total_pages


# --- Кнопки фильмов/сериалов с пагинацией ---
def genre_keyboard(genre: str, page: int, total_pages: int, items):
    keyboard = []

    for item_type, code, item in items:
        emoji = "🎬" if item_type == "movie" else "📺"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {item['title']}",
                callback_data=f"open:{item_type}:{code}"
            )
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"genre_page:{genre}:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"genre_page:{genre}:{page+1}"))

    keyboard.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- Хендлер нажатия на жанр ---
@dp.callback_query(lambda c: c.data.startswith("genre:"))
async def genre_selected(callback: types.CallbackQuery):
    genre = callback.data.split(":")[1]
    items, total_pages = genre_page(genre, 0)

    if not items:
        await callback.message.answer(f"<b>❌ Ничего не найдено\n\n@kinonawe4er - все наши фильмы и сериалы</b>\n\n<b>/genres - сортировка по жанрам</b>",
        parse_mode="HTML")
        await callback.answer()
        return

    await callback.message.edit_text(
        f"<b>🎭 Жанр: {genre.capitalize()}</b>",
        reply_markup=genre_keyboard(genre, 0, total_pages, items),
        parse_mode="HTML"
    )
    await callback.answer()


# --- Хендлер переключения страниц жанра ---
@dp.callback_query(lambda c: c.data.startswith("genre_page:"))
async def genre_page_switch(callback: types.CallbackQuery):
    _, genre, page = callback.data.split(":")
    page = int(page)
    items, total_pages = genre_page(genre, page)

    await callback.message.edit_reply_markup(
        reply_markup=genre_keyboard(genre, page, total_pages, items)
    )
    await callback.answer()


# --- Хендлер открытия фильма/сериала по кнопке ---
@dp.callback_query(lambda c: c.data.startswith("open:"))
async def open_item(callback: types.CallbackQuery):
    _, item_type, code = callback.data.split(":")
    user_id = callback.from_user.id
    
    if item_type == "movie":
        if not await is_subscribed(user_id):
            await callback.message.answer(
                "Для просмотра фильма подпишитесь на канал @kinonawe4er",
                reply_markup=subscribe_keyboard_movie(code)
            )
            await callback.answer()
            return
        movie = movies[code]  # создаем movie первым!

        if has_only_warning(movie):
            await callback.message.answer(
                f"<b>{movie['warning']}</b>",
                parse_mode="HTML"
            )
            await callback.answer()
            return

        hashtags = " ".join(f"#{g.replace(' ', '_')}@kinonawe4er" for g in movie.get('genres', []))
        
        await callback.message.answer_video(
            video=movie["video"],
            caption=(
                f"<b>⭐️ фильм «{movie['title']}», {movie['year']}</b>\n\n"
                f"<i>{movie.get('description', '')}</i>\n\n"
                f"<u>Жанр:</u> {hashtags}\n\n"
                f"<u>Страна:</u> {movie.get('country', '')}\n"
                f"<u>Режиссер:</u> {movie.get('director', '')}\n\n"
                f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
                f"Наш канал @kinonawe4er ✨"
            ),
            parse_mode="HTML"
        )
    else:  # сериал
        await send_serial_card(callback.message, code)
    
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("check_movie:"))
async def check_movie_callback(callback: types.CallbackQuery):
    _, code = callback.data.split(":")
    user_id = callback.from_user.id

    if not await is_subscribed(user_id):
        await callback.answer("❌ Вы ещё не подписались", show_alert=True)
        return

    movie = movies.get(code)
    if not movie:
        await callback.answer("❌ Фильм не найден", show_alert=True)
        return

    if has_only_warning(movie):
        await callback.message.answer(
            f"<b>{movie['warning']}</b>",
            parse_mode="HTML"
        )
        return

    hashtags = " ".join(f"#{g.replace(' ', '_')}@kinonawe4er" for g in movie.get('genres', []))

    await callback.message.answer_video(
        video=movie["video"],
        caption=(
            f"<b>⭐️ фильм «{movie['title']}», {movie['year']}</b>\n\n"
            f"<i>{movie.get('description', '')}</i>\n\n"
            f"<u>Жанр:</u> {hashtags}\n\n"
            f"<u>Страна:</u> {movie.get('country', '')}\n"
            f"<u>Режиссер:</u> {movie.get('director', '')}\n\n"
            f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
            f"Наш канал @kinonawe4er ✨"
        ),
        parse_mode="HTML"
    )

    await callback.answer("✅ Подписка подтверждена")


def serial_start_keyboard(code: str):
    serial = series[code]

    if has_seasons(serial):
        return InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="📂 ВЫБРАТЬ СЕЗОН",
                    callback_data=f"seasons:{code}"
                )
            ]]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="📋 ВЫБРАТЬ СЕРИЮ",
                    callback_data=f"menu:{code}:0"
                )
            ]]
        )


async def send_serial_card(message: types.Message, code: str):
    serial = series[code]
    hashtags = " ".join(f"#{g.replace(' ', '_')}@kinonawe4er" for g in serial.get('genres', []))
    text = (
        f"<b>⭐️ «{serial['title']}», {serial['year']}, ({serial['episode_counter']})</b>\n\n"
        f"<i>{serial['description']}</i>\n\n"
        f"<u>Жанр:</u> {hashtags}\n\n"
        f"<u>Страна:</u> {serial['country']}\n"
        f"<u>Режиссер:</u> {serial['director']}\n\n"
    )

    await message.answer_photo(
        photo=serial["poster"],
        caption=text,
        parse_mode="HTML",
        reply_markup=serial_start_keyboard(code)
    )


def episode_keyboard(code: str, episode_index: int, total: int, season: int | None = None):
    serial = series[code]

    # Верхний ряд — кнопки «Выбрать серию» и «К сезонам» (если есть)
    top_row = []

    if has_seasons(serial) and season is not None:
        top_row.append(
            InlineKeyboardButton(
                text="📂 К сезонам",
                callback_data=f"seasons:{code}"
            )
        )

    top_row.append(
        InlineKeyboardButton(
            text="📋 ВЫБРАТЬ СЕРИЮ",
            callback_data=f"menu:{code}:{season if season is not None else -1}"
        )
    )

    # Нижний ряд — кнопки навигации вперед/назад
    nav_row = []
    if episode_index > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"prev:{code}:{season if season is not None else -1}:{episode_index}"
            )
        )
    if episode_index < total - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"next:{code}:{season if season is not None else -1}:{episode_index}"
            )
        )

    # Формируем клавиатуру с двумя рядами
    keyboard = [top_row]
    if nav_row:
        keyboard.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)








def series_menu_keyboard(code: str, page: int = 0, season: int | None = None):
    serial = series[code]
    episodes = get_episodes(serial, season)
    total = len(episodes)

    per_page = 10
    start = page * per_page
    end = min(start + per_page, total)

    keyboard = []
    row = []

    # --- КНОПКИ СЕРИЙ ---
    for i in range(start, end):
        row.append(
            InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f"ep:{code}:{season if season is not None else 0}:{i}"
            )
        )

        if len(row) == 5:  # 5 в ряд
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    # --- ПАГИНАЦИЯ ---
    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"page:{code}:{season if season is not None else 0}:{page-1}"
            )
        )

    if end < total:
        nav.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"page:{code}:{season if season is not None else 0}:{page+1}"
            )
        )

    if nav:
        keyboard.append(nav)

    # --- КНОПКИ ВОЗВРАТА ---
    back_buttons = []

    # если есть сезоны → к сезонам
    if "seasons" in serial:
        back_buttons.append(
            InlineKeyboardButton(
                text="📀 К сезонам",
                callback_data=f"seasons:{code}"
            )
        )

    # назад к сериалу
    back_buttons.append(
        InlineKeyboardButton(
            text="К сериалу",
            callback_data=f"serial:{code}"
        )
    )

    # добавляем внизу
    keyboard.append(back_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)




async def send_episode(
    target,
    code: str,
    episode_index: int,
    season: int | None = None
):
    user_id = target.from_user.id if isinstance(target, types.CallbackQuery) else target.chat.id

    if not await is_subscribed(user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📍 Подписаться", url="https://t.me/kinonawe4er")],
            [InlineKeyboardButton(
                text="🔎 Проверить",
                callback_data=f"check_sub:{code}:{episode_index}"
            )]
        ])

        await target.message.answer(
            "Для просмотра серии подпишитесь на канал @kinonawe4er",
            reply_markup=keyboard
        )
        return

    serial = series[code]
    episodes = get_episodes(serial, season)
    total = len(episodes)
    episode = episodes[episode_index]
    episode_title = episode.get("title")

    # ---- Название сезона ----
    season_text = ""
    if has_seasons(serial) and season is not None:
        season_title = serial["seasons"][season].get("title")
        if season_title:
            season_text = f"{season_title}, "
        else:
            season_text = f"Сезон {season}, "

    if episode_title:
        episode_line = f"{season_text}серия {episode_index + 1} из {total} «{episode_title}»"
    else:
        episode_line = f"{season_text}серия {episode_index + 1} из {total}"

    caption = (
        f"<b>⭐️ «{serial['title']}», {serial['year']}, ({serial['episode_counter']})</b>\n\n"
        f"{episode_line}\n\n"
        f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
        f"Наш канал @kinonawe4er ✨"
    )

    keyboard = episode_keyboard(code, episode_index, total, season)

    if isinstance(target, types.CallbackQuery):
        await target.message.edit_media(
            media=types.InputMediaVideo(
                media=episode["video"],
                caption=caption,
                parse_mode="HTML"
            ),
            reply_markup=keyboard
        )
    else:
        await target.answer_video(
            video=episode["video"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@dp.callback_query(lambda c: c.data.startswith("check_sub:"))
async def check_sub_callback(callback: types.CallbackQuery):
    _, code, episode = callback.data.split(":")
    await send_episode(callback, code, int(episode))


# Функция для поиска фильма по коду или названию
def find_movie(query: str):
    query = normalize(query.strip())

    # Сначала ищем по коду
    for code, movie in movies.items():
        if query == code.lower():
            return movie

    # Потом ищем по названию
    for movie in movies.values():
        title = normalize(movie.get("title", ""))
        if query in title:
            return movie

    return None

def find_series(query: str):
    query = normalize(query.strip())

    for code, serial in series.items():

        if query == str(code).lower():
            return code

        title = normalize(serial.get("title", ""))
        if query in title:
            return code

    return None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    add_or_update_user(message.from_user)
    await message.answer(
        "<b>Для просмотра введите название ИЛИ код</b>\n\n"
        "<b>Например: «Фокус» ИЛИ же его код «001»</b>\n\n"
        "<b>https://t.me/kinonawe4er - наш канал ✨</b>\n\n"
        "<b>/genres - сортировка по жанрам</b>",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Command("genres"))
async def cmd_genres(message: types.Message):
    add_or_update_user(message.from_user)
    await message.answer(
        "<b>🎭 Выберите жанр:</b>",
        reply_markup=genres_keyboard(),
        parse_mode="HTML"
    )

# ==================== РАССЫЛКА ====================
class BroadcastState(StatesGroup):
    waiting_for_confirm = State()


@dp.message(Command("broadcast"))
async def broadcast_start(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    text = message.text.partition(" ")[2].strip()
    
    if not text:
        await message.answer("❌ Использование:\n`/broadcast Текст сообщения`", parse_mode="Markdown")
        return

    await state.update_data(broadcast_text=text)
    users_count = get_users_count()

    await message.answer(
        f"⚠️ <b>Подтверждение рассылки</b>\n\n"
        f"Получателей: <b>{users_count}</b>\n\n"
        f"Сообщение:\n{text}\n\n"
        f"Напиши <b>Да</b> — чтобы отправить\n"
        f"Напиши <b>/cancel</b> — чтобы отменить",
        parse_mode="HTML"
    )
    
    await state.set_state(BroadcastState.waiting_for_confirm)


@dp.message(Command("cancel"))
async def cancel_broadcast(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Рассылка отменена.")


@dp.message(BroadcastState.waiting_for_confirm)
async def broadcast_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() not in ["да", "yes"]:
        await message.answer("Рассылка отменена.")
        await state.clear()
        return

    data = await state.get_data()
    text = data.get("broadcast_text")

    users = get_all_users(limit=999999)
    success = 0
    failed = 0

    status_msg = await message.answer("⏳ Начинаю рассылку...")

    for user_id, *_ in users:
        try:
            await bot.send_message(
                user_id, 
                text, 
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            success += 1
        except:
            failed += 1

    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"✅ Доставлено: <b>{success}</b>\n"
        f"❌ Ошибок: <b>{failed}</b>\n"
        f"📊 Всего в базе: <b>{len(users)}</b>",
        parse_mode="HTML"
    )
    
    await state.clear()

# # Основной хендлер сообщений

@dp.message(lambda m: m.video and m.from_user.id == ADMIN_ID)
async def get_video_id(message: types.Message):
    await message.answer(message.video.file_id)


@dp.message(lambda m: m.photo and m.from_user.id == ADMIN_ID)
async def get_photo_id(message: types.Message):
    await message.answer(message.photo[-1].file_id)

@dp.message(lambda m: m.text and not m.text.startswith("/"))
async def handle_message(message: types.Message):
    user = message.from_user
    name = user.username or f"{user.first_name or ''} {user.last_name or ''}".strip()

    logging.info(
        f"MSG | ID:{user.id} | USER:{name} | USERNAME:@{user.username} | TEXT:{message.text}"
    )

    query = message.text.strip().lower()

    results = search_all(query)

    if not results:
        await message.answer(f"<b>❌ Ничего не найдено\n\n@kinonawe4er - все наши фильмы и сериалы</b>\n\n<b>/genres - сортировка по жанрам</b>",
        parse_mode="HTML")
        return

    # один результат — открываем сразу
    if len(results) == 1:
        item_type, code, _ = results[0]

        if item_type == "movie":
            if not await is_subscribed(message.from_user.id):
                await message.answer(
                    "Для просмотра фильма подпишитесь на канал @kinonawe4er",
                        reply_markup=subscribe_keyboard_movie(code)
                )
                return
            movie = movies[code]

            if has_only_warning(movie):
                await message.answer(
                    f"<b>{movie['warning']}</b>",
                    parse_mode="HTML"
                )
                return

            hashtags = " ".join(f"#{g.replace(' ', '_')}@kinonawe4er" for g in movie.get('genres', []))

            await message.answer_video(
                video=movie["video"],
                caption=f"<b>⭐️ фильм «{movie['title']}», {movie['year']}</b>\n\n"
                        f"<i>{movie['description']}</i>\n\n"
                        f"<u>Жанр:</u> {hashtags}\n\n"
                        f"<u>Страна:</u> {movie['country']}\n"
                        f"<u>Режиссер:</u> {movie['director']}\n\n"
                        f"Смотреть бесплатно фильмы и сериалы 👉🏻 @kinonawe4er_bot\n"
                        f"Наш канал @kinonawe4er ✨",
                parse_mode="HTML"
            )
        else:
            await send_serial_card(message, code)

        return

    # несколько результатов — выбор
    await message.answer(
        "<b>🔍 Найдено несколько вариантов:</b>",
        reply_markup=search_results_keyboard(results),
        parse_mode="HTML"
    )
    



@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    user = callback.from_user
    name = user.username or f"{user.first_name or ''} {user.last_name or ''}".strip()

    logging.info(
        f"BTN | ID:{user.id} | USER:{name} | USERNAME:@{user.username} | DATA:{callback.data}"
    )
    
    data = callback.data.split(":")
    action = data[0]

    if action in ("menu", "prev", "next", "ep", "page"):
        code = data[1]

        # Для всех этих действий берем сезон
        season = None
        if len(data) > 2:
            s = data[2]
            if s not in ("None", "-1"):
                season = int(s)

        # В зависимости от действия
        if action == "menu":
            await callback.message.edit_reply_markup(
                reply_markup=series_menu_keyboard(code, page=0, season=season)
            )

        elif action in ("prev", "next"):
            episode = int(data[3])
            episode = episode - 1 if action == "prev" else episode + 1
            await send_episode(callback, code, episode, season)

        elif action == "ep":
            episode = int(data[3])
            await send_episode(callback, code, episode, season)

        elif action == "page":
            page = int(data[3])
            await callback.message.edit_reply_markup(
                reply_markup=series_menu_keyboard(code, page=page, season=season)
            )

    elif action == "serial":
        _, code = data
        await callback.message.delete()
        await send_serial_card(callback.message, code)

    elif action == "seasons":
        _, code = data
        await callback.message.edit_reply_markup(
            reply_markup=seasons_keyboard(code)
        )

    elif action == "season":
        _, code, season = data
        season = int(season)
        await callback.message.edit_reply_markup(
            reply_markup=series_menu_keyboard(code, page=0, season=season)
        )

    await callback.answer()

@dp.message(Command("log"))
async def log_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    file_path = "bot.log"

    if not os.path.exists(file_path):
        await message.answer("Лог файл не найден")
        return

    file = FSInputFile(file_path)

    await message.answer_document(file)


# Запуск бота
async def main():
    await bot.set_chat_menu_button(menu_button=MenuButtonDefault())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())