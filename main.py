import os
import io
import time
import base64
import logging
import sqlite3
import threading

import telebot
from telebot import types
from openai import OpenAI


# =========================================================
# USTADRIVE CONFIG
# =========================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ADMIN_ID = os.environ.get("ADMIN_ID", "").strip()

CHANNEL_1 = "@ustadriveuz"
CHANNEL_2 = "@UstaDriveMarket"

CHANNEL_1_URL = "https://t.me/ustadriveuz"
CHANNEL_2_URL = "https://t.me/UstaDriveMarket"

BOT_NAME = "UstaDrive"
DB_FILE = "ustadrive.db"

AI_MODEL = os.environ.get("AI_MODEL", "gpt-5.6-luna")


# =========================================================
# TEKSHIRUV
# =========================================================

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN Environment Variable topilmadi.")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY Environment Variable topilmadi.")


# =========================================================
# LOG
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =========================================================
# CLIENTLAR
# =========================================================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)

ai = OpenAI(
    api_key=OPENAI_API_KEY
)


# =========================================================
# DATABASE
# =========================================================

db_lock = threading.Lock()


def db():
    return sqlite3.connect(
        DB_FILE,
        check_same_thread=False
    )


def init_db():

    with db_lock:

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at INTEGER,
                messages INTEGER DEFAULT 0
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
        conn.close()


init_db()


# =========================================================
# USER SAQLASH
# =========================================================

def save_user(user):

    with db_lock:

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            INSERT OR IGNORE INTO users
            (user_id, username, first_name, joined_at, messages)
            VALUES (?, ?, ?, ?, 0)
        """, (
            user.id,
            user.username or "",
            user.first_name or "",
            int(time.time())
        ))

        cur.execute("""
            UPDATE users
            SET username = ?, first_name = ?
            WHERE user_id = ?
        """, (
            user.username or "",
            user.first_name or "",
            user.id
        ))

        conn.commit()
        conn.close()


def add_message(user_id):

    with db_lock:

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET messages = messages + 1
            WHERE user_id = ?
        """, (user_id,))

        conn.commit()
        conn.close()


# =========================================================
# STATISTIKA
# =========================================================

def get_stats():

    with db_lock:

        conn = db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(messages), 0) FROM users")
        messages = cur.fetchone()[0]

        conn.close()

    return users, messages


# =========================================================
# OBUNA
# =========================================================

def is_subscribed(user_id):

    for channel in [CHANNEL_1, CHANNEL_2]:

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

        except Exception as e:

            logging.error(
                "Kanal tekshirish xatosi %s: %s",
                channel,
                e
            )

            return False

    return True


def subscription_keyboard():

    markup = types.InlineKeyboardMarkup(
        row_width=1
    )

    markup.add(
        types.InlineKeyboardButton(
            "📢 UstaDriveUZ",
            url=CHANNEL_1_URL
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🛒 UstaDriveMarket",
            url=CHANNEL_2_URL
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_sub"
        )
    )

    return markup


def require_subscription(message):

    if is_subscribed(message.from_user.id):
        return True

    bot.send_message(
        message.chat.id,
        """
<b>🔐 UstaDrive</b>

Botdan foydalanish uchun avval ikkala kanalga ham qo‘shiling:

📢 <b>UstaDriveUZ</b>
🛒 <b>UstaDriveMarket</b>

Keyin <b>✅ Obunani tekshirish</b> tugmasini bosing.
""",
        reply_markup=subscription_keyboard()
    )

    return False


# =========================================================
# MENU
# =========================================================

def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "🤖 AI Usta",
        "🚨 Tez yordam"
    )

    markup.row(
        "📚 Avto maslahat",
        "📊 Statistika"
    )

    markup.row(
        "ℹ️ Yordam"
    )

    return markup


# =========================================================
# AI USTA
# =========================================================

SYSTEM_PROMPT = """
Sen UstaDrive nomli avtomobil yordamchi botisan.

Foydalanuvchi bilan o'zbek tilida, sodda va tushunarli gaplash.

Sening vazifang:
- avtomobil nosozligini tushunish;
- ehtimoliy sabablarni aytish;
- xavfsiz tekshiruvlarni tushuntirish;
- kerak bo'lsa ustaga murojaat qilishni tavsiya qilish;
- avtomobil rusumi va simptomlar asosida savollar berish;
- Cobalt, Nexia, Gentra, Lacetti va boshqa avtomobillar bo'yicha umumiy texnik maslahat berish.

Muhim:
- Aniq ko'rmasdan nosoz detalni 100% deb aytma.
- "Ehtimol", "bo'lishi mumkin" kabi iboralardan foydalan.
- Tormoz, rul, yoqilg'i sizishi, qizib ketish, elektr qisqa tutashuvi kabi xavfli holatlarda xavfsizlikni birinchi o'ringa qo'y.
- Qizigan radiator qopqog'ini ochishni tavsiya qilma.
- Foydalanuvchini xavfli ta'mirlashni o'zi bajarishga undama.
- Agar mashinani haydash xavfli bo'lsa, haydamaslikni va malakali ustaga murojaat qilishni ayt.
- Javobni imkon qadar amaliy va bosqichma-bosqich ber.
- Keraksiz uzun javob bermagin.
- Tibbiy, siyosiy yoki boshqa mavzularga o'tib ketma; avtomobil masalasida yordam ber.

Javob formati:
🔧 Muammo
🔎 Ehtimoliy sabablar
✅ Nima qilish mumkin
⚠️ Qachon haydamaslik kerak

Agar ma'lumot yetarli bo'lmasa, avtomobil rusumi, yili, dvigateli va simptom haqida qisqa savollar ber.
"""


def ask_ai(text):

    try:

        response = ai.responses.create(
            model=AI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=text
        )

        answer = response.output_text.strip()

        if not answer:
            return "❌ AI javob qaytara olmadi. Birozdan keyin qayta urinib ko‘ring."

        return answer

    except Exception as e:

        logging.exception("AI xatosi")

        return """
❌ Hozir AI xizmatida vaqtinchalik muammo yuz berdi.

Iltimos, birozdan keyin qayta urinib ko‘ring.
"""


# =========================================================
# AI RASM TAHLILI
# =========================================================

def ask_ai_image(image_bytes, user_text):

    try:

        encoded = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        prompt = user_text.strip()

        if not prompt:
            prompt = """
Bu avtomobilga tegishli rasm.

Rasmda ko'rinayotgan narsani tahlil qil.
Agar paneldagi ogohlantirish belgisi bo'lsa, uning ma'nosini tushuntir.
Agar detal yoki nosozlik ko'rinsa, faqat ko'rinadigan dalillarga asoslan.
Aniq bo'lmasa, taxmin ekanini ayt.
Xavfli holat bo'lsa, xavfsizlik choralarini birinchi ayt.
Javobni o'zbek tilida ber.
"""

        response = ai.responses.create(
            model=AI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": (
                                "data:image/jpeg;base64,"
                                + encoded
                            )
                        }
                    ]
                }
            ]
        )

        answer = response.output_text.strip()

        return answer or "❌ Rasmni tahlil qilib bo‘lmadi."

    except Exception:

        logging.exception(
            "Rasm AI xatosi"
        )

        return """
❌ Rasmni hozir tahlil qilib bo‘lmadi.

Iltimos, rasmni qayta yuboring yoki muammoni matn bilan yozing.
"""


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    save_user(
        message.from_user
    )

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        f"""
<b>🚗 {BOT_NAME}ga xush kelibsiz!</b>

Men sizga avtomobil muammolarini tushunishda yordam beradigan <b>AI Usta</b>man. 🤖🔧

Menga oddiy qilib yozing:

<i>“Cobalt ertalab zo‘rg‘a o‘t olyapti”</i>

<i>“Nexia qizib ketyapti”</i>

<i>“Panelda sariq belgi chiqdi”</i>

<i>“Balonim teshildi”</i>

📸 Panel yoki detal rasmini ham yuborishingiz mumkin.
""",
        reply_markup=main_menu()
    )


# =========================================================
# OBUNA CALLBACK
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_sub"
)
def check_sub(call):

    if is_subscribed(
        call.from_user.id
    ):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.send_message(
            call.message.chat.id,
            """
<b>✅ Tayyor!</b>

Endi UstaDrive'dan foydalanishingiz mumkin. 🚗🔧

Muammoni yozing yoki rasm yuboring.
""",
            reply_markup=main_menu()
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Ikkala kanalga ham qo‘shiling.",
            show_alert=True
        )


# =========================================================
# ADMIN
# =========================================================

def is_admin(user_id):

    return (
        ADMIN_ID
        and str(user_id) == str(ADMIN_ID)
    )


@bot.message_handler(commands=["admin"])
def admin(message):

    if not is_admin(
        message.from_user.id
    ):

        bot.send_message(
            message.chat.id,
            "⛔ Bu bo‘lim faqat admin uchun."
        )

        return

    users, messages = get_stats()

    bot.send_message(
        message.chat.id,
        f"""
<b>👨‍🔧 USTADRIVE ADMIN</b>

👥 Foydalanuvchilar: <b>{users}</b>
💬 Xabarlar: <b>{messages}</b>

🤖 AI: <b>faol</b>
📢 Majburiy obuna: <b>2 kanal</b>
"""
    )


# =========================================================
# TEXT
# =========================================================

@bot.message_handler(
    content_types=["text"]
)
def text_handler(message):

    save_user(
        message.from_user
    )

    if not require_subscription(message):
        return

    text = message.text.strip()

    if text == "🤖 AI Usta":

        bot.send_message(
            message.chat.id,
            """
<b>🤖 AI Usta</b>

Avtomobil muammosini oddiy gap bilan yozing.

Masalan:

<i>Cobalt baloni teshilib qoldi, nima qilay?</i>

<i>Gentra qizib ketyapti.</i>

<i>Nexia starteri aylanadi, lekin o't olmayapti.</i>
"""
        )

        return


    if text == "🚨 Tez yordam":

        bot.send_message(
            message.chat.id,
            """
<b>🚨 TEZ YORDAM</b>

Agar mashina yo'lda xavfli tarzda buzilgan bo'lsa:

1. Xavfsiz joyga to'xtang.
2. Avariya chirog'ini yoqing.
3. Yo'l harakatiga xalaqit bermang.
4. Xavfli nosozlik bo'lsa, mashinani haydamang.
5. Zarur bo'lsa, malakali usta yoki yo'l yordamiga murojaat qiling.
"""
        )

        return


    if text == "📚 Avto maslahat":

        bot.send_message(
            message.chat.id,
            """
<b>📚 AVTO MASLAHATLAR</b>

🛢 Moyni nazorat qilish
💧 Antifrizni tekshirish
🔋 Akkumulyatorni tekshirish
🛞 Shina bosimini nazorat qilish
🛑 Tormozlarni vaqtida tekshirtirish
🚨 Panel belgilarini e'tiborsiz qoldirmaslik
🔧 G'alati tovushlarni vaqtida tekshirtirish
"""
        )

        return


    if text == "📊 Statistika":

        users, messages = get_stats()

        bot.send_message(
            message.chat.id,
            f"""
<b>📊 UstaDrive</b>

👥 Foydalanuvchilar: <b>{users}</b>
💬 Jami xabarlar: <b>{messages}</b>
"""
        )

        return


    if text == "ℹ️ Yordam":

        bot.send_message(
            message.chat.id,
            """
<b>ℹ️ QANDAY FOYDALANISH</b>

Tugma bosish shart emas.

Shunchaki yozing:

🚗 Cobalt o‘t olmayapti
🛞 Balon teshildi
🔋 Akkumulyator o‘tirib qoldi
🌡 Motor qizib ketdi
🚨 Check Engine yondi
🛑 Tormoz yumshab qoldi

📸 Rasm yuborsangiz, AI uni ham tahlil qilishga harakat qiladi.
"""
        )

        return


    # Oddiy savol -> AI

    add_message(
        message.from_user.id
    )

    bot.send_chat_action(
        message.chat.id,
        "typing"
    )

    answer = ask_ai(
        text
    )

    bot.send_message(
        message.chat.id,
        answer,
        reply_markup=main_menu()
    )


# =========================================================
# PHOTO
# =========================================================

@bot.message_handler(
    content_types=["photo"]
)
def photo_handler(message):

    save_user(
        message.from_user
    )

    if not require_subscription(message):
        return

    bot.send_chat_action(
        message.chat.id,
        "typing"
    )

    try:

        photo = message.photo[-1]

        file_info = bot.get_file(
            photo.file_id
        )

        image_bytes = bot.download_file(
            file_info.file_path
        )

        caption = (
            message.caption
            or
            "Rasmdagi avtomobil muammosini tahlil qil."
        )

        add_message(
            message.from_user.id
        )

        answer = ask_ai_image(
            image_bytes,
            caption
        )

        bot.send_message(
            message.chat.id,
            answer,
            reply_markup=main_menu()
        )

    except Exception:

        logging.exception(
            "Photo handler xatosi"
        )

        bot.send_message(
            message.chat.id,
            "❌ Rasmni qayta ishlashda xatolik yuz berdi."
        )


# =========================================================
# UNKNOWN COMMAND
# =========================================================

@bot.message_handler(
    commands=["help"]
)
def help_command(message):

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        """
<b>🆘 UstaDrive yordam</b>

Avtomobil muammosini oddiy qilib yozing yoki rasm yuboring.

Masalan:

“Cobalt qizib ketyapti”
“Panelda qizil belgi chiqdi”
“Balon teshildi”
“Starter ishlamayapti”
"""
    )


# =========================================================
# ISHGA TUSHIRISH
# =========================================================

print("================================")
print("🚗 UstaDrive ishga tushmoqda...")
print("🤖 AI tizimi: tayyor")
print("📢 Kanal tekshiruvi: tayyor")
print("📸 Rasm tahlili: tayyor")
print("📊 Statistika: tayyor")
print("================================")


bot.infinity_polling(
    skip_pending=True,
    timeout=60,
    long_polling_timeout=60
)
