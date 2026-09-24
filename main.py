import os
import logging
import telebot
from telebot import types

# =========================
# SOZLAMALAR
# =========================

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(level=logging.INFO)

# =========================
# ASOSIY MENU
# =========================

def main_menu():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("🚗 Usta chaqirish"),
        types.KeyboardButton("🔧 Xizmatlar"),
        types.KeyboardButton("📍 Manzil"),
        types.KeyboardButton("📞 Aloqa"),
        types.KeyboardButton("ℹ️ Biz haqimizda")
    )

    return markup


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name or "Do‘stimiz"

    text = (
        f"👋 Assalomu alaykum, {name}!\n\n"
        "🚗 UstaDriveBot'ga xush kelibsiz!\n\n"
        "Avtomobilingiz bo‘yicha kerakli xizmatni "
        "quyidagi menyudan tanlang 👇"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu()
    )


# =========================
# USTA CHAQIRISH
# =========================

@bot.message_handler(func=lambda message: message.text == "🚗 Usta chaqirish")
def call_master(message):
    markup = types.InlineKeyboardMarkup()

    btn = types.InlineKeyboardButton(
        "📞 Usta bilan bog‘lanish",
        url="https://t.me/Umarjonow_c"
    )

    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "🚗 Usta chaqirish uchun quyidagi tugmani bosing:",
        reply_markup=markup
    )


# =========================
# XIZMATLAR
# =========================

@bot.message_handler(func=lambda message: message.text == "🔧 Xizmatlar")
def services(message):

    text = (
        "🔧 <b>Bizning xizmatlar:</b>\n\n"
        "🚗 Avtomobil diagnostikasi\n"
        "🔋 Elektr tizimini tekshirish\n"
        "🛠️ Dvigatel bo‘yicha xizmatlar\n"
        "⚙️ Kompyuter diagnostikasi\n"
        "🔧 Avtomobil ta’mirlash\n"
        "🚨 Nosozliklarni aniqlash\n\n"
        "📞 Batafsil ma’lumot uchun usta bilan bog‘laning."
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML"
    )


# =========================
# MANZIL
# =========================

@bot.message_handler(func=lambda message: message.text == "📍 Manzil")
def location(message):

    text = (
        "📍 <b>Bizning manzil:</b>\n\n"
        "🇺🇿 Toshkent shahri\n\n"
        "📌 Aniq manzilni bilish uchun administrator bilan bog‘laning."
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML"
    )


# =========================
# ALOQA
# =========================

@bot.message_handler(func=lambda message: message.text == "📞 Aloqa")
def contact(message):

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "👨‍🔧 Administrator",
            url="https://t.me/Umarjonow_c"
        )
    )

    bot.send_message(
        message.chat.id,
        "📞 Biz bilan bog‘lanish:",
        reply_markup=markup
    )


# =========================
# BIZ HAQIMIZDA
# =========================

@bot.message_handler(func=lambda message: message.text == "ℹ️ Biz haqimizda")
def about(message):

    text = (
        "ℹ️ <b>UstaDrive</b>\n\n"
        "🚗 Avtomobil egalari uchun qulay xizmat.\n\n"
        "🔧 Avtomobil diagnostikasi\n"
        "🛠️ Ta’mirlash xizmatlari\n"
        "📞 Usta bilan bog‘lanish\n\n"
        "Tezkor va qulay xizmat olish uchun "
        "menyudan foydalaning."
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML"
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

print("🚗 UstaDriveBot ishga tushdi!")

bot.infinity_polling(
    skip_pending=True
)
