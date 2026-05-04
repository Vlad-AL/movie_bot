import asyncio
import sqlite3
import re
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, MenuButtonDefault, FSInputFile
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import os
from dotenv import load_dotenv

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

# ====================== БАЗЫ ДАННЫХ ======================
users_db = sqlite3.connect("users.db", check_same_thread=False, isolation_level=None)
users_cursor = users_db.cursor()

users_cursor.execute("PRAGMA journal_mode=WAL;")
users_cursor.execute("PRAGMA synchronous=NORMAL;")

media_db = sqlite3.connect("media.db", check_same_thread=False)
media_cursor = media_db.cursor()

# ====================== ЗАГРУЗКА ВСЕХ ДАННЫХ ======================
movies = {}
series = {}

def load_media_data():
    global movies, series
    
    # === ФИЛЬМЫ ===
    media_cursor.execute("""
        SELECT code, title, year, video, description, country, director, genres 
        FROM movies
    """)
    for row in media_cursor.fetchall():
        code = row[0]
        movies[code] = {
            "title": row[1],
            "year": row[2],
            "video": row[3],
            "description": row[4],
            "country": row[5],
            "director": row[6],
            "genres": json.loads(row[7]) if row[7] and isinstance(row[7], str) and row[7].startswith('[') else 
                      row[7].split(',') if row[7] else []
        }

    # === СЕРИАЛЫ + СЕЗОНЫ + СЕРИИ ===
    # Загружаем сериалы
    media_cursor.execute("""
        SELECT code, title, year, poster, description, country, director, 
               genres, episode_counter 
        FROM series
    """)
    for row in media_cursor.fetchall():
        code = row[0]
        series[code] = {
            "title": row[1],
            "year": row[2],
            "poster": row[3],
            "description": row[4],
            "country": row[5],
            "director": row[6],
            "genres": json.loads(row[7]) if row[7] and isinstance(row[7], str) and row[7].startswith('[') else 
                      row[7].split(',') if row[7] else [],
            "episode_counter": row[8],
            "seasons": {}
        }

    # Загружаем сезоны и серии для каждого сериала
    for code in series.keys():
        # Сезоны
        media_cursor.execute("""
            SELECT season_number, title 
            FROM seasons 
            WHERE series_code = ? 
            ORDER BY season_number
        """, (code,))
        
        for season_row in media_cursor.fetchall():
            season_num = season_row[0]
            season_title = season_row[1]
            
            series[code]["seasons"][season_num] = {
                "title": season_title,
                "episodes": []
            }

        # Серии
        media_cursor.execute("""
            SELECT season_number, episode_number, title, video 
            FROM episodes 
            WHERE series_code = ? 
            ORDER BY season_number, episode_number
        """, (code,))
        
        for ep_row in media_cursor.fetchall():
            s_num = ep_row[0]
            ep_num = ep_row[1]
            ep_title = ep_row[2]
            video = ep_row[3]
            
            if s_num in series[code]["seasons"]:
                series[code]["seasons"][s_num]["episodes"].append({
                    "title": ep_title,
                    "video": video
                })

    print(f"✅ Загружено: {len(movies)} фильмов | {len(series)} сериалов")

users_cursor.execute("PRAGMA journal_mode=WAL;")
users_cursor.execute("PRAGMA synchronous=NORMAL;")

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
    if not text:
        return ""
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^\w\s]", "", text)   # убираем знаки
    text = re.sub(r"\s+", "", text)       # убираем все пробелы
    return text.strip()

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
    if not query:
        return []
    
    query_norm = normalize(query)
    
    results = []

    # Поиск по коду
    if query in movies:
        results.append(("movie", query, movies[query]))
    if query in series:
        results.append(("series", query, series[query]))

    if results:
        return results

    # Поиск по названию
    for code, movie in movies.items():
        title_norm = normalize(movie.get("title", ""))
        if query_norm in title_norm or title_norm in query_norm:
            results.append(("movie", code, movie))

    for code, serial in series.items():
        title_norm = normalize(serial.get("title", ""))
        if query_norm in title_norm or title_norm in query_norm:
            results.append(("series", code, serial))

    return results


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