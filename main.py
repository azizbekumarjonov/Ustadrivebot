import os
import sqlite3
import logging
from datetime import datetime

import requests
import telebot
from telebot import types


# =========================================================
# USTADRIVE + SAVETUNE BOT
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

CHANNELS = [
    "@ustadriveuz",
    "@UstaDriveMarket",
]

DB_NAME = "ustadrive.db"


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML",
    threaded=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'uz',
            joined_at TEXT,
            last_seen TEXT,
            blocked INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            title TEXT,
            artist TEXT,
            caption TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_user(user):
    conn = get_db()

    now = datetime.utcnow().isoformat()

    conn.execute("""
        INSERT INTO users
        (
            user_id,
            username,
            first_name,
            language,
            joined_at,
            last_seen
        )
        VALUES (?, ?, ?, 'uz', ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_seen = excluded.last_seen
    """, (
        user.id,
        user.username or "",
        user.first_name or "",
        now,
        now
    ))

    conn.commit()
    conn.close()


def get_language(user_id):
    conn = get_db()

    row = conn.execute(
        "SELECT language FROM users WHERE user_id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    if row:
        return row["language"]

    return "uz"


def set_language(user_id, language):
    conn = get_db()

    conn.execute(
        "UPDATE users SET language=? WHERE user_id=?",
        (language, user_id)
    )

    conn.commit()
    conn.close()


# =========================================================
# TEXTLAR
# =========================================================

TEXTS = {

    "uz": {

        "welcome":
            "🚗 <b>UstaDrive</b> + 🎵 <b>SaveTune</b> botiga "
            "xush kelibsiz!\n\n"
            "Avtomobil bo‘yicha savol bering yoki musiqa qidiring.",

        "menu":
            "👇 Kerakli bo‘limni tanlang:",

        "car":
            "🚗 UstaDrive",

        "music":
            "🎵 SaveTune",

        "language":
            "🌐 Til",

        "help":
            "ℹ️ Yordam",

        "admin":
            "🛠 Admin",

        "subscribe":
            "🔐 Botdan foydalanish uchun quyidagi kanallarga "
            "obuna bo‘ling:",

        "not_subscribed":
            "❗ Barcha kanallarga obuna bo‘lgach "
            "<b>Tekshirish</b> tugmasini bosing.",

        "verified":
            "✅ Obuna tasdiqlandi!",

        "car_help":
            "🚗 <b>UstaDrive</b>\n\n"
            "Avtomobil muammosini oddiy qilib yozing.\n\n"
            "Masalan:\n"
            "• Cobalt o‘t olmayapti\n"
            "• Faralar ishlamayapti\n"
            "• Motor qizib ketyapti\n"
            "• Mashina titrayapti\n"
            "• Akkumulyator chirog‘i yondi\n\n"
            "📸 Muammo rasmini ham yuborishingiz mumkin.",

        "music_help":
            "🎵 <b>SaveTune</b>\n\n"
            "Qo‘shiq nomi yoki ijrochini yozing.\n"
            "Telegram orqali audio yuborsangiz, uni "
            "bot bazasida saqlashimiz mumkin.",

        "language_menu":
            "🌐 Tilni tanlang:",

        "help_text":
            "ℹ️ <b>Yordam</b>\n\n"
            "🚗 UstaDrive — avtomobil bo‘yicha yordam.\n"
            "🎵 SaveTune — musiqa qidiruvi va audio saqlash.\n\n"
            "Muammo bo‘lsa administratorga murojaat qiling."
    },

    "ru": {

        "welcome":
            "🚗 <b>UstaDrive</b> + 🎵 <b>SaveTune</b>\n\n"
            "Задайте вопрос об автомобиле или найдите музыку.",

        "menu":
            "👇 Выберите раздел:",

        "car":
            "🚗 UstaDrive",

        "music":
            "🎵 SaveTune",

        "language":
            "🌐 Язык",

        "help":
            "ℹ️ Помощь",

        "admin":
            "🛠 Админ",

        "subscribe":
            "🔐 Подпишитесь на каналы:",

        "not_subscribed":
            "❗ После подписки нажмите <b>Проверить</b>.",

        "verified":
            "✅ Подписка подтверждена!",

        "car_help":
            "🚗 <b>UstaDrive</b>\n\n"
            "Опишите проблему автомобиля простыми словами "
            "или отправьте фото.",

        "music_help":
            "🎵 <b>SaveTune</b>\n\n"
            "Введите название песни или исполнителя.",

        "language_menu":
            "🌐 Выберите язык:",

        "help_text":
            "ℹ️ <b>Помощь</b>\n\n"
            "UstaDrive помогает разбираться с автомобилями.\n"
            "SaveTune предназначен для поиска информации о музыке "
            "и сохранения отправленных аудиофайлов."
    },

    "en": {

        "welcome":
            "🚗 <b>UstaDrive</b> + 🎵 <b>SaveTune</b>\n\n"
            "Ask about a car problem or search for music.",

        "menu":
            "👇 Choose a section:",

        "car":
            "🚗 UstaDrive",

        "music":
            "🎵 SaveTune",

        "language":
            "🌐 Language",

        "help":
            "ℹ️ Help",

        "admin":
            "🛠 Admin",

        "subscribe":
            "🔐 Subscribe to the channels:",

        "not_subscribed":
            "❗ Subscribe and press <b>Check</b>.",

        "verified":
            "✅ Subscription verified!",

        "car_help":
            "🚗 <b>UstaDrive</b>\n\n"
            "Describe your car problem or send a photo.",

        "music_help":
            "🎵 <b>SaveTune</b>\n\n"
            "Type a song title or artist.",

        "language_menu":
            "🌐 Choose a language:",

        "help_text":
            "ℹ️ <b>Help</b>\n\n"
            "UstaDrive helps with car problems.\n"
            "SaveTune searches music information and stores "
            "audio files sent to the bot."
    }
}


def txt(user_id, key):
    language = get_language(user_id)

    return TEXTS.get(
        language,
        TEXTS["uz"]
    ).get(
        key,
        TEXTS["uz"].get(key, key)
    )


# =========================================================
# KEYBOARD
# =========================================================

def main_keyboard(user_id):

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    keyboard.add(
        types.KeyboardButton(txt(user_id, "car")),
        types.KeyboardButton(txt(user_id, "music"))
    )

    keyboard.add(
        types.KeyboardButton(txt(user_id, "language")),
        types.KeyboardButton(txt(user_id, "help"))
    )

    if ADMIN_ID and user_id == ADMIN_ID:
        keyboard.add(
            types.KeyboardButton(txt(user_id, "admin"))
        )

    return keyboard


def subscription_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 UstaDriveUZ",
            url="https://t.me/ustadriveuz"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🛒 UstaDriveMarket",
            url="https://t.me/UstaDriveMarket"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "✅ Tekshirish",
            callback_data="check_sub"
        )
    )

    return keyboard


def language_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "🇺🇿 O‘zbek",
            callback_data="language_uz"
        ),
        types.InlineKeyboardButton(
            "🇷🇺 Русский",
            callback_data="language_ru"
        ),
        types.InlineKeyboardButton(
            "🇬🇧 English",
            callback_data="language_en"
        )
    )

    return keyboard


# =========================================================
# MAJBURIY OBUNA
# =========================================================

def check_subscription(user_id):

    for channel in CHANNELS:

        try:

            member = bot.get_chat_member(
                channel,
                user_id
            )

            if member.status in [
                "left",
                "kicked"
            ]:
                return False

        except Exception as error:

            logger.error(
                "Obuna tekshirish xatosi: %s",
                error
            )

            return False

    return True


def require_subscription(message):

    if check_subscription(
        message.from_user.id
    ):
        return True

    bot.send_message(
        message.chat.id,
        txt(
            message.from_user.id,
            "subscribe"
        )
        + "\n\n"
        + txt(
            message.from_user.id,
            "not_subscribed"
        ),
        reply_markup=subscription_keyboard()
    )

    return False


# =========================================================
# START
# =========================================================

@bot.message_handler(
    commands=["start"]
)
def start(message):

    save_user(
        message.from_user
    )

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        txt(
            message.from_user.id,
            "welcome"
        )
        + "\n\n"
        + txt(
            message.from_user.id,
            "menu"
        ),
        reply_markup=main_keyboard(
            message.from_user.id
        )
    )


# =========================================================
# HELP
# =========================================================

@bot.message_handler(
    commands=["help"]
)
def help_command(message):

    save_user(
        message.from_user
    )

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        txt(
            message.from_user.id,
            "help_text"
        ),
        reply_markup=main_keyboard
