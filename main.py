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
    if __name__ == "__main__":
    run()# =========================================================
# ADMIN PANEL + STATISTIKA + SAVED MUSIC
# =========================================================

def is_admin(user_id):
    return ADMIN_ID != 0 and user_id == ADMIN_ID


def admin_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "📊 Statistika",
            callback_data="admin_stats"
        ),
        types.InlineKeyboardButton(
            "🎵 Audio baza",
            callback_data="admin_audio"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 Reklama",
            callback_data="admin_broadcast"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "⬅️ Asosiy menyu",
            callback_data="admin_back"
        )
    )

    return keyboard


# =========================================================
# ADMIN COMMAND
# =========================================================

@bot.message_handler(commands=["admin"])
def admin_command(message):

    save_user(message.from_user)

    if not is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⛔ Sizda admin huquqi yo‘q."
        )
        return

    bot.send_message(
        message.chat.id,
        "🛠 <b>UstaDriveBot Admin Panel</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=admin_keyboard()
    )


# =========================================================
# STATISTIKA
# =========================================================

def get_statistics():

    conn = get_db()

    users = conn.execute(
        "SELECT COUNT(*) AS total FROM users"
    ).fetchone()["total"]

    audios = conn.execute(
        "SELECT COUNT(*) AS total FROM audios"
    ).fetchone()["total"]

    searches = conn.execute(
        "SELECT COUNT(*) AS total FROM searches"
    ).fetchone()["total"]

    photos = conn.execute(
        "SELECT COUNT(*) AS total FROM photos"
    ).fetchone()["total"]

    conn.close()

    return (
        "📊 <b>BOT STATISTIKASI</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"🎵 Saqlangan audiolar: <b>{audios}</b>\n"
        f"🔎 Musiqa qidiruvlari: <b>{searches}</b>\n"
        f"📸 Yuborilgan rasmlar: <b>{photos}</b>"
    )


@bot.message_handler(commands=["stats"])
def stats_command(message):

    if not is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⛔ Ruxsat yo‘q."
        )
        return

    bot.send_message(
        message.chat.id,
        get_statistics()
    )


# =========================================================
# ADMIN CALLBACK
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
        call.data == "admin_stats"
)
def admin_stats_callback(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "⛔ Ruxsat yo‘q.",
            show_alert=True
        )

        return

    bot.answer_callback_query(
        call.id
    )

    bot.send_message(
        call.message.chat.id,
        get_statistics()
    )


# =========================================================
# AUDIO DATABASE STATISTICS
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
        call.data == "admin_audio"
)
def admin_audio_callback(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "⛔ Ruxsat yo‘q.",
            show_alert=True
        )

        return

    conn = get_db()

    rows = conn.execute("""
        SELECT
            title,
            artist,
            COUNT(*) AS amount
        FROM audios
        GROUP BY title, artist
        ORDER BY amount DESC
        LIMIT 20
    """).fetchall()

    conn.close()

    if not rows:

        bot.answer_callback_query(
            call.id
        )

        bot.send_message(
            call.message.chat.id,
            "🎵 Audio bazasi hozircha bo‘sh."
        )

        return

    text = "🎵 <b>AUDIO BAZASI</b>\n\n"

    for index, row in enumerate(
        rows,
        start=1
    ):

        text += (
            f"{index}. 🎵 <b>{row['title']}</b>\n"
            f"   👤 {row['artist']}\n"
            f"   📦 {row['amount']} ta\n\n"
        )

    bot.answer_callback_query(
        call.id
    )

    bot.send_message(
        call.message.chat.id,
        text
    )


# =========================================================
# SAVED MUSIC
# =========================================================

def get_saved_music(user_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            file_id,
            title,
            artist
        FROM audios
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 30
    """, (
        user_id,
    )).fetchall()

    conn.close()

    return rows


@bot.message_handler(commands=["saved"])
def saved_command(message):

    save_user(
        message.from_user
    )

    if not require_subscription(message):
        return

    rows = get_saved_music(
        message.from_user.id
    )

    if not rows:

        bot.send_message(
            message.chat.id,
            "💾 Sizda hali saqlangan audio yo‘q."
        )

        return

    bot.send_message(
        message.chat.id,
        "💾 <b>Siz saqlagan audiolar:</b>"
    )

    for row in rows:

        try:

            bot.send_audio(
                message.chat.id,
                row["file_id"],
                caption=(
                    f"🎵 <b>{row['title']}</b>\n"
                    f"👤 {row['artist']}"
                )
            )

        except Exception as error:

            logger.error(
                "Audio yuborish xatosi: %s",
                error
            )


# =========================================================
# BROADCAST
# =========================================================

broadcast_waiting = set()


@bot.callback_query_handler(
    func=lambda call:
        call.data == "admin_broadcast"
)
def admin_broadcast_callback(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "⛔ Ruxsat yo‘q.",
            show_alert=True
        )

        return

    broadcast_waiting.add(
        call.from_user.id
    )

    bot.answer_callback_query(
        call.id
    )

    bot.send_message(
        call.message.chat.id,
        "📢 <b>Reklama/Broadcast</b>\n\n"
        "Yubormoqchi bo‘lgan xabaringizni yozing.\n\n"
        "Bekor qilish: /cancel"
    )


@bot.message_handler(commands=["cancel"])
def cancel_broadcast(message):

    broadcast_waiting.discard(
        message.from_user.id
    )

    bot.send_message(
        message.chat.id,
        "❌ Broadcast bekor qilindi."
    )


def send_broadcast(text):

    conn = get_db()

    users = conn.execute("""
        SELECT user_id
        FROM users
        WHERE blocked=0
    """).fetchall()

    conn.close()

    sent = 0
    failed = 0

    for user in users:

        try:

            bot.send_message(
                user["user_id"],
                text
            )

            sent += 1

        except Exception:

            failed += 1

    return sent, failed


# =========================================================
# BROADCAST TEXT HANDLER
# =========================================================

@bot.message_handler(
    func=lambda message:
        message.from_user.id in broadcast_waiting,
    content_types=["text"]
)
def broadcast_message(message):

    user_id = message.from_user.id

    if not is_admin(user_id):
        broadcast_waiting.discard(user_id)
        return

    if message.text == "/cancel":

        broadcast_waiting.discard(user_id)

        bot.send_message(
            message.chat.id,
            "❌ Bekor qilindi."
        )

        return

    broadcast_waiting.discard(user_id)

    bot.send_message(
        message.chat.id,
        "📢 Xabar yuborilmoqda..."
    )

    sent, failed = send_broadcast(
        message.text
    )

    bot.send_message(
        message.chat.id,
        "✅ <b>Broadcast tugadi!</b>\n\n"
        f"📨 Yuborildi: <b>{sent}</b>\n"
        f"❌ Xato: <b>{failed}</b>"
    )


# =========================================================
# ADMIN BACK
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
        call.data == "admin_back"
)
def admin_back_callback(call):

    bot.answer_callback_query(
        call.id
    )

    bot.send_message(
        call.message.chat.id,
        "👇 Asosiy menyu:",
        reply_markup=main_keyboard(
            call.from_user.id
        )
    )


# =========================================================
# FINAL START
# =========================================================

if __name__ == "__main__":
    run()
