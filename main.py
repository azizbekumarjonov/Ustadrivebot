import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(BOT_TOKEN)

CHANNELS = [
    "@ustadriveuz",
    "@UstaDriveMarket"
]


def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)

            if member.status in ["left", "kicked"]:
                return False

        except Exception:
            return False

    return True


def subscription_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🚗 UstaDriveUZ",
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
            "✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    )

    return keyboard


def send_subscription_message(chat_id):
    bot.send_message(
        chat_id,
        "🚗 UstaDriveBot'ga xush kelibsiz!\n\n"
        "Botdan foydalanish uchun quyidagi kanallarga "
        "avval obuna bo‘ling 👇",
        reply_markup=subscription_keyboard()
    )


@bot.message_handler(commands=["start"])
def start(message):
    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row("🔧 Avto yordam", "📚 Avto bilim")
    keyboard.row("🚘 Ehtiyot qismlar", "ℹ️ Yordam")

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum! 🚗\n\n"
        "Men UstaDriveBotman.\n"
        "Avtomobil bo‘yicha savollaringizga yordam beraman.",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_callback(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.send_message(
            call.message.chat.id,
            "🎉 Zo‘r! Obuna tasdiqlandi.\n\n"
            "Endi UstaDriveBot'dan foydalanishingiz mumkin."
        )

    else:
        bot.answer_callback_query(
            call.id,
            "❌ Hali barcha kanallarga obuna bo‘lmagansiz.",
            show_alert=True
        )


@bot.message_handler(func=lambda message: True)
def messages(message):
    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    text = message.text.lower()

    if text == "🔧 avto yordam":
        bot.send_message(
            message.chat.id,
            "🔧 Avto yordam\n\n"
            "Mashina muammosini yozing.\n\n"
            "Masalan:\n"
            "• Cobalt o't olmayapti\n"
            "• Faralar yonmayapti\n"
            "• Motor qizib ketyapti\n"
            "• Shina teshildi"
        )

    elif text == "📚 avto bilim":
        bot.send_message(
            message.chat.id,
            "📚 Avto bilim\n\n"
            "Bu bo‘limda avtomobilning motor, "
            "elektrika, tormoz, uzatma va boshqa "
            "tizimlari haqida ma’lumot beramiz."
        )

    elif text == "🚘 ehtiyot qismlar":
        bot.send_message(
            message.chat.id,
            "🚘 Ehtiyot qismlar\n\n"
            "Kerakli ehtiyot qism nomini yozing."
        )

    elif text == "ℹ️ yordam":
        bot.send_message(
            message.chat.id,
            "ℹ️ Yordam\n\n"
            "Muammoingizni oddiy qilib yozing. "
            "Masalan: «Cobalt o't olmayapti»."
        )

    else:
        bot.send_message(
            message.chat.id,
            "🔧 Muammoingizni yozing.\n\n"
            "Masalan:\n"
            "«Cobalt o't olmayapti»\n"
            "«Faralar yonmayapti»\n"
            "«Motor qizib ketyapti»"
        )


print("UstaDriveBot ishga tushdi...")

bot.infinity_polling(
    skip_pending=True,
    allowed_updates=["message", "callback_query"]
)
