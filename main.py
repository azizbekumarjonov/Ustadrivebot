import os
import logging
import telebot
from telebot import types

# =========================
# SOZLAMALAR
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN Environment Variable topilmadi!")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Majburiy kanallar
REQUIRED_CHANNELS = [
    {
        "username": "@UstaDriveMarket",
        "url": "https://t.me/UstaDriveMarket"
    },
    {
        "username": "@ustadriveuz",
        "url": "https://t.me/ustadriveuz"
    }
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# MAJBURIY OBUNA TEKSHIRISH
# =========================

def check_subscription(user_id):
    """
    Foydalanuvchi ikkala kanalga ham obuna bo'lganini tekshiradi.
    """
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(
                channel["username"],
                user_id
            )

            if member.status in ["left", "kicked"]:
                return False

        except Exception as e:
            logging.error(
                f"Obunani tekshirishda xato "
                f"{channel['username']}: {e}"
            )
            return False

    return True


# =========================
# OBUNA TUGMALARI
# =========================

def subscription_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)

    for channel in REQUIRED_CHANNELS:
        markup.add(
            types.InlineKeyboardButton(
                "📢 " + channel["username"],
                url=channel["url"]
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    )

    return markup


# =========================
# ASOSIY MENYU
# =========================

def main_menu():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "🤖 AI yordamchi",
        "🚗 Avto yordamchi"
    )

    markup.row(
        "🌐 Tarjimon",
        "📸 Rasm tahlili"
    )

    markup.row(
        "ℹ️ Yordam",
        "⚙️ Sozlamalar"
    )

    return markup


# =========================
# OBUNA HAQIDA XABAR
# =========================

def send_subscription_message(chat_id):
    text = (
        "👋 <b>UstaDrive AI</b> ga xush kelibsiz!\n\n"
        "Botdan foydalanishdan oldin quyidagi "
        "kanallarga obuna bo‘ling:\n\n"
        "1️⃣ @UstaDriveMarket\n"
        "2️⃣ @ustadriveuz\n\n"
        "Obuna bo‘lgach, <b>✅ Obunani tekshirish</b> "
        "tugmasini bosing."
    )

    bot.send_message(
        chat_id,
        text,
        reply_markup=subscription_keyboard()
    )


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if check_subscription(user_id):
        bot.send_message(
            message.chat.id,
            "🎉 <b>Xush kelibsiz!</b>\n\n"
            "UstaDrive AI ishga tayyor. 🤖🚗\n\n"
            "Kerakli funksiyani tanlang:",
            reply_markup=main_menu()
        )
    else:
        send_subscription_message(message.chat.id)


# =========================
# OBUNANI TEKSHIRISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_subscription_callback(call):
    user_id = call.from_user.id

    if check_subscription(user_id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.edit_message_text(
            "✅ <b>Obuna tasdiqlandi!</b>\n\n"
            "Endi UstaDrive AI xizmatlaridan "
            "foydalanishingiz mumkin. 🤖🚗",
            call.message.chat.id,
            call.message.message_id
        )

        bot.send_message(
            call.message.chat.id,
            "👇 <b>Asosiy menyu:</b>",
            reply_markup=main_menu()
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Hali barcha kanallarga obuna bo‘lmagansiz!",
            show_alert=True
        )


# =========================
# ASOSIY MENYU
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🤖 AI yordamchi"
)
def ai_menu(message):
    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "🤖 <b>AI yordamchi</b>\n\n"
        "Bu bo‘limga keyingi bosqichda AI tizimimizni ulaymiz.\n\n"
        "💬 Savolingizni oddiy tilda yozishingiz mumkin."
    )


@bot.message_handler(
    func=lambda message: message.text == "🚗 Avto yordamchi"
)
def auto_menu(message):
    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "🚗 <b>Avto yordamchi</b>\n\n"
        "Mashina muammosini yozing yoki "
        "keyingi bosqichda rasm yuboring.\n\n"
        "Masalan:\n"
        "• Cobalt ishga tushmayapti\n"
        "• Panelda belgi chiqdi\n"
        "• Motor tomondan ovoz chiqyapti"
    )


@bot.message_handler(
    func=lambda message: message.text == "🌐 Tarjimon"
)
def translator_menu(message):
    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "🌐 <b>Tarjimon</b>\n\n"
        "Keyingi bosqichda o‘zbek, rus, ingliz, "
        "arab, fors va tojik tillarini ulaymiz."
    )


@bot.message_handler(
    func=lambda message: message.text == "📸 Rasm tahlili"
)
def image_menu(message):
    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "📸 <b>Rasm tahlili</b>\n\n"
        "Keyingi bosqichda AI yordamida "
        "rasmlarni tahlil qilish funksiyasini qo‘shamiz."
    )


@bot.message_handler(
    func=lambda message: message.text == "ℹ️ Yordam"
)
def help_menu(message):
    bot.send_message(
        message.chat.id,
        "🆘 <b>Yordam</b>\n\n"
        "Botdan foydalanish uchun menyudagi "
        "kerakli bo‘limni tanlang."
    )


@bot.message_handler(
    func=lambda message: message.text == "⚙️ Sozlamalar"
)
def settings_menu(message):
    bot.send_message(
        message.chat.id,
        "⚙️ <b>Sozlamalar</b>\n\n"
        "Til va boshqa sozlamalar keyingi "
        "bosqichlarda qo‘shiladi."
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":
    logging.info("🚀 UstaDrive AI ishga tushdi!")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
        )
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"UstaDrive AI ishlayapti!")

    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "UstaDriveBot ishlayapti!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()
