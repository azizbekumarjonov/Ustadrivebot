import os
import logging
import telebot
from telebot import types

# ==========================================
# SOZLAMALAR
# ==========================================

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)

BOT_NAME = "UstaDriveBot"

# ==========================================
# MAJBURIY OBUNA KANALLARI
# ==========================================

REQUIRED_CHANNELS = [
    "@UstaDriveMarket",
    "@ustadriveuz",
]


# ==========================================
# OBUNANI TEKSHIRISH
# ==========================================

def check_subscription(user_id):

    for channel in REQUIRED_CHANNELS:

        try:
            member = bot.get_chat_member(channel, user_id)

            if member.status in ["left", "kicked"]:
                return False

        except Exception as e:
            logging.error(f"{channel} tekshirishda xato: {e}")
            return False

    return True


# ==========================================
# OBUNA MENYUSI
# ==========================================

def subscription_menu():

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "📢 UstaDrive Market",
            url="https://t.me/UstaDriveMarket"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "📢 UstaDrive",
            url="https://t.me/ustadriveuz"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    )

    return markup


def send_subscription_message(chat_id):

    bot.send_message(
        chat_id,
        "🔐 <b>UstaDriveBot'dan foydalanish uchun "
        "kanallarimizga obuna bo‘ling.</b>\n\n"
        "1️⃣ Ikkala kanalga ham kiring\n"
        "2️⃣ Obuna bo‘ling\n"
        "3️⃣ «✅ Obunani tekshirish» tugmasini bosing",
        parse_mode="HTML",
        reply_markup=subscription_menu()
    )


# ==========================================
# ASOSIY MENYU
# ==========================================

def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("🚗 Avtomobil"),
        types.KeyboardButton("🔧 Usta xizmatlari"),
        types.KeyboardButton("📚 Foydali ma'lumot"),
        types.KeyboardButton("📞 Usta bilan bog‘lanish"),
        types.KeyboardButton("ℹ️ Yordam")
    )

    return markup


# ==========================================
# START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "🚗 <b>UstaDriveBot</b> ga xush kelibsiz!\n\n"
        "Avtomobil bo‘yicha foydali ma’lumotlar, "
        "diagnostika va usta xizmatlaridan foydalanishingiz mumkin.\n\n"
        "👇 Kerakli bo‘limni tanlang.",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# ==========================================
# OBUNANI QAYTA TEKSHIRISH
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_subscription_callback(call):

    if check_subscription(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!",
            show_alert=True
        )

        bot.send_message(
            call.message.chat.id,
            "🎉 <b>Rahmat!</b>\n\n"
            "Obuna tasdiqlandi. Endi botdan foydalanishingiz mumkin.",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Hali ikkala kanalga ham obuna bo‘lmagansiz!",
            show_alert=True
        )


# ==========================================
# AVTOMOBIL
# ==========================================

@bot.message_handler(func=lambda message: message.text == "🚗 Avtomobil")
def avtomobil(message):

    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🔍 Diagnostika",
            callback_data="diagnostika"
        ),
        types.InlineKeyboardButton(
            "⚠️ Xatoliklar",
            callback_data="xatolik"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🛠 Texnik xizmat",
            callback_data="texnik"
        ),
        types.InlineKeyboardButton(
            "💡 Maslahat",
            callback_data="maslahat"
        )
    )

    bot.send_message(
        message.chat.id,
        "🚗 <b>Avtomobil bo‘limi</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        parse_mode="HTML",
        reply_markup=markup
    )


# ==========================================
# USTA XIZMATLARI
# ==========================================

@bot.message_handler(func=lambda message: message.text == "🔧 Usta xizmatlari")
def usta_xizmatlari(message):

    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "🔧 <b>Usta xizmatlari</b>\n\n"
        "• Kompyuter diagnostikasi\n"
        "• Elektrik ishlari\n"
        "• Dvigatel bo‘yicha xizmat\n"
        "• Elektronika\n"
        "• Avtomobil nosozliklarini aniqlash\n\n"
        "📞 Usta bilan bog‘lanish uchun "
        "«📞 Usta bilan bog‘lanish» tugmasini bosing.",
        parse_mode="HTML"
    )


# ==========================================
# FOYDALI MA'LUMOT
# ==========================================

@bot.message_handler(func=lambda message: message.text == "📚 Foydali ma'lumot")
def foydali(message):

    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🚘 Dvigatel",
            callback_data="dvigatel"
        ),
        types.InlineKeyboardButton(
            "🔋 Elektrika",
            callback_data="elektrika"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🛞 Shina",
            callback_data="shina"
        ),
        types.InlineKeyboardButton(
            "🛢 Moy",
            callback_data="moy"
        )
    )

    bot.send_message(
        message.chat.id,
        "📚 <b>Foydali ma’lumotlar</b>\n\n"
        "Kerakli mavzuni tanlang:",
        parse_mode="HTML",
        reply_markup=markup
    )


# ==========================================
# USTA BILAN BOG'LANISH
# ==========================================

@bot.message_handler(
    func=lambda message: message.text == "📞 Usta bilan bog‘lanish"
)
def boglanish(message):

    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "📞 <b>Usta bilan bog‘lanish</b>\n\n"
        "Muammoingizni shu yerga yozib yuboring.\n\n"
        "Masalan:\n"
        "🚗 Cobalt\n"
        "⚠️ Check yonib qoldi\n"
        "🔧 Mashina titrayapti",
        parse_mode="HTML"
    )


# ==========================================
# YORDAM
# ==========================================

@bot.message_handler(func=lambda message: message.text == "ℹ️ Yordam")
def yordam(message):

    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "ℹ️ <b>UstaDriveBot yordam</b>\n\n"
        "🚗 Avtomobil — avtomobil bo‘yicha bo‘limlar\n"
        "🔧 Usta xizmatlari — xizmatlar\n"
        "📚 Foydali ma’lumot — maslahatlar\n"
        "📞 Usta bilan bog‘lanish — usta bilan aloqa\n\n"
        "Savolingizni oddiy xabar sifatida ham yuborishingiz mumkin.",
        parse_mode="HTML"
    )


# ==========================================
# INLINE BO'LIMLAR
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data in [
        "diagnostika",
        "xatolik",
        "texnik",
        "maslahat",
        "dvigatel",
        "elektrika",
        "shina",
        "moy"
    ]
)
def callback(call):

    if not check_subscription(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "❌ Avval kanallarga obuna bo‘ling!",
            show_alert=True
        )

        send_subscription_message(call.message.chat.id)
        return

    texts = {

        "diagnostika":
            "🔍 <b>Diagnostika</b>\n\n"
            "Avtomobildagi xatoliklarni kompyuter "
            "diagnostikasi orqali aniqlash mumkin.",

        "xatolik":
            "⚠️ <b>Xatoliklar</b>\n\n"
            "Paneldagi ogohlantirish chiroqlarini "
            "e’tiborsiz qoldirmaslik kerak.",

        "texnik":
            "🛠 <b>Texnik xizmat</b>\n\n"
            "Moy, filtr, tormoz va boshqa qismlarni "
            "vaqtida tekshirtirib turish kerak.",

        "maslahat":
            "💡 <b>Maslahat</b>\n\n"
            "Avtomobilingizdagi muammoni yozing "
            "yoki rasmini yuboring.",

        "dvigatel":
            "🚘 <b>Dvigatel</b>\n\n"
            "Dvigatelda titrash, qizish yoki quvvat "
            "pasayishi kuzatilsa, diagnostika qilish kerak.",

        "elektrika":
            "🔋 <b>Elektrika</b>\n\n"
            "Akkumulyator, generator, starter va boshqa "
            "elektr tizimlarini tekshirish mumkin.",

        "shina":
            "🛞 <b>Shinalar</b>\n\n"
            "Shina bosimi va yeyilish holatini "
            "muntazam tekshiring.",

        "moy":
            "🛢 <b>Dvigatel moyi</b>\n\n"
            "Moyni ishlab chiqaruvchi tavsiya qilgan "
            "muddatda almashtirish kerak."
    }

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        texts[call.data],
        parse_mode="HTML"
    )


# ==========================================
# ADMIN
# ==========================================

@bot.message_handler(commands=["admin"])
def admin(message):

    if str(message.from_user.id) != str(ADMIN_ID):

        bot.reply_to(
            message,
            "⛔ Siz admin emassiz."
        )
        return

    bot.send_message(
        message.chat.id,
        "👑 <b>ADMIN PANEL</b>\n\n"
        "Bot ishlayapti ✅",
        parse_mode="HTML"
    )


# ==========================================
# ODDIY XABARLAR
# ==========================================

@bot.message_handler(content_types=["text"])
def other_messages(message):

    if message.text.startswith("/"):
        return

    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    if ADMIN_ID:

        try:

            bot.send_message(
                ADMIN_ID,
                "📩 <b>Yangi murojaat</b>\n\n"
                f"👤 {message.from_user.first_name}\n"
                f"🆔 <code>{message.from_user.id}</code>\n\n"
                f"💬 {message.text}",
                parse_mode="HTML"
            )

        except Exception as e:
            logging.error(e)

    bot.reply_to(
        message,
        "✅ Xabaringiz qabul qilindi."
    )


# ==========================================
# BOTNI ISHGA TUSHIRISH
# ==========================================

print("🚗 UstaDriveBot ishga tushdi!")

bot.infinity_polling(
    skip_pending=True,
    timeout=30,
    long_polling_timeout=30
        )
