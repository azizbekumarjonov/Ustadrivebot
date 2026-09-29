import os
import time
import logging
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Render Environment Variables orqali beriladi
ADMIN_IDS_TEXT = os.getenv("ADMIN_IDS", "")

CHANNELS = [
    "@ustadriveuz",
    "@UstaDriveMarket"
]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN Environment Variable topilmadi!")

try:
    ADMIN_IDS = {
        int(x.strip())
        for x in ADMIN_IDS_TEXT.split(",")
        if x.strip().isdigit()
    }
except Exception:
    ADMIN_IDS = set()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Foydalanuvchi tillari
user_languages = {}

# =========================
# MATNLAR
# =========================

WELCOME = """
<b>🚗 UstaDrive'ga xush kelibsiz!</b>

Bu bot avtomobil haqida o‘rganish,
nosozliklarni tushunish va avtomobil
qismlari haqida ma’lumot olishga yordam beradi.

👇 Kerakli bo‘limni tanlang:
"""

SUBSCRIBE_TEXT = """
<b>🔐 Botdan foydalanish uchun kanallarimizga obuna bo‘ling.</b>

1️⃣ @ustadriveuz
2️⃣ @UstaDriveMarket

Obuna bo‘lgach, <b>✅ Tekshirish</b> tugmasini bosing.
"""

# =========================
# KLAVIATURALAR
# =========================

def subscription_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)

    kb.add(
        types.InlineKeyboardButton(
            "📢 UstaDrive",
            url="https://t.me/ustadriveuz"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🛒 UstaDrive Market",
            url="https://t.me/UstaDriveMarket"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "✅ Tekshirish",
            callback_data="check_subscription"
        )
    )

    return kb


def main_keyboard():
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    kb.add(
        types.KeyboardButton("🔧 Diagnostika"),
        types.KeyboardButton("📚 Avto darslar")
    )

    kb.add(
        types.KeyboardButton("⚙️ Ehtiyot qismlar"),
        types.KeyboardButton("📸 Rasm yuborish")
    )

    kb.add(
        types.KeyboardButton("🌐 Til"),
        types.KeyboardButton("ℹ️ Yordam")
    )

    return kb


def lessons_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)

    kb.add(
        types.InlineKeyboardButton(
            "🔋 Elektr tizimi",
            callback_data="lesson_electric"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🛢 Dvigatel",
            callback_data="lesson_engine"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "⚙️ Uzatmalar qutisi",
            callback_data="lesson_gearbox"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🛞 Tormoz va yurish qismi",
            callback_data="lesson_brake"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "❄️ Sovutish tizimi",
            callback_data="lesson_cooling"
        )
    )

    return kb


# =========================
# OBUNA TEKSHIRISH
# =========================

def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)

            if member.status in ["left", "kicked"]:
                return False

        except ApiTelegramException as e:
            logging.error(
                f"Obuna tekshirishda xato {channel}: {e}"
            )
            return False

        except Exception as e:
            logging.error(
                f"Noma'lum obuna xatosi {channel}: {e}"
            )
            return False

    return True


def send_subscription_check(chat_id):
    bot.send_message(
        chat_id,
        SUBSCRIBE_TEXT,
        reply_markup=subscription_keyboard()
    )


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        send_subscription_check(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        WELCOME,
        reply_markup=main_keyboard()
    )


# =========================
# OBUNA CALLBACK
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_subscription_callback(call):

    user_id = call.from_user.id

    if is_subscribed(user_id):

        try:
            bot.answer_callback_query(
                call.id,
                "✅ Obuna tasdiqlandi!"
            )
        except Exception:
            pass

        bot.send_message(
            call.message.chat.id,
            WELCOME,
            reply_markup=main_keyboard()
        )

    else:

        try:
            bot.answer_callback_query(
                call.id,
                "❌ Hali barcha kanallarga obuna bo‘lmagansiz.",
                show_alert=True
            )
        except Exception:
            pass


# =========================
# UMUMIY OBUNA NAZORATI
# =========================

def check_access(message):
    if not is_subscribed(message.from_user.id):
        send_subscription_check(message.chat.id)
        return False

    return True


# =========================
# DIAGNOSTIKA
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🔧 Diagnostika"
)
def diagnostics(message):

    if not check_access(message):
        return

    bot.send_message(
        message.chat.id,
        """
<b>🔧 UstaDrive Diagnostika</b>

Avtomobilingizdagi muammoni oddiy qilib yozing.

Masalan:

• Cobalt o't olmayapti
• Mashina qizib ketyapti
• Faralar ishlamayapti
• Akkumulyator tez o'tirib qolmoqda
• Tormozda g‘alati ovoz chiqyapti
• Check Engine yondi

Men ehtimoliy sabablarni va tekshirish kerak bo‘lgan narsalarni tushuntiraman.

⚠️ Aniq ta’mirlashdan oldin avtomobilni xavfsiz holatda tekshiring.
"""
    )


# =========================
# AVTO DARSLAR
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📚 Avto darslar"
)
def lessons(message):

    if not check_access(message):
        return

    bot.send_message(
        message.chat.id,
        "<b>📚 Avtomobil darslari</b>\n\nKerakli mavzuni tanlang:",
        reply_markup=lessons_keyboard()
    )


# =========================
# EHTIYOT QISMLARI
# =========================

@bot.message_handler(
    func=lambda message: message.text == "⚙️ Ehtiyot qismlar"
)
def parts(message):

    if not check_access(message):
        return

    bot.send_message(
        message.chat.id,
        """
<b>⚙️ Ehtiyot qismlar</b>

Quyidagilar haqida so‘rashingiz mumkin:

🔋 Akkumulyator
⚡ Generator
🔌 Starter
🛢 Moy filtri
🌬 Havo filtri
⛽ Yoqilg‘i filtri
🛞 Tormoz kolodkasi
🔩 Svecha
🌡 Termostat
💧 Radiator

Masalan:
<b>“Generator nima vazifa bajaradi?”</b>
"""
    )


# =========================
# RASM
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📸 Rasm yuborish"
)
def photo_help(message):

    if not check_access(message):
        return

    bot.send_message(
        message.chat.id,
        """
📸 <b>Avtomobil muammosining rasmini yuboring.</b>

Hozirgi bepul versiyada men rasmni avtomatik AI diagnostika qilmayman.

Rasm bilan birga muammoni yozsangiz, mavjud ma’lumotlar asosida yo‘naltirishga harakat qilaman.

Masalan:
“Bu joydan moy sizyapti.”
"""
    )


@bot.message_handler(content_types=["photo"])
def receive_photo(message):

    if not check_access(message):
        return

    bot.send_message(
        message.chat.id,
        """
📸 Rasm qabul qilindi.

Endi shu avtomobilning:
• markasi/modeli
• muammo qachondan boshlanganligi
• qanday belgi borligi

haqida yozing.

Shunda muammoni tushunishga yordam beraman.
"""
    )


# =========================
# TIL
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🌐 Til"
)
def language(message):

    if not check_access(message):
        return

    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            "🇺🇿 O‘zbek",
            callback_data="lang_uz"
        ),
        types.InlineKeyboardButton(
            "🇷🇺 Русский",
            callback_data="lang_ru"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🇬🇧 English",
            callback_data="lang_en"
        )
    )

    bot.send_message(
        message.chat.id,
        "🌐 Tilni tanlang:",
        reply_markup=kb
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("lang_")
)
def language_callback(call):

    lang = call.data.replace("lang_", "")
    user_languages[call.from_user.id] = lang

    texts = {
        "uz": "🇺🇿 O‘zbek tili tanlandi.",
        "ru": "🇷🇺 Русский язык выбран.",
        "en": "🇬🇧 English selected."
    }

    bot.answer_callback_query(
        call.id,
        texts.get(lang, "Til tanlandi.")
    )


# =========================
# YORDAM
# =========================

@bot.message_handler(
    func=lambda message: message.text == "ℹ️ Yordam"
)
def help_handler(message):

    if not check_access(message):
        return

    bot.send_message(
        message.chat.id,
        """
<b>ℹ️ UstaDrive yordam</b>

🚗 Avtomobil muammosi — <b>🔧 Diagnostika</b>
📚 O‘rganish — <b>📚 Avto darslar</b>
⚙️ Detallar — <b>⚙️ Ehtiyot qismlar</b>
📸 Muammo rasmi — <b>📸 Rasm yuborish</b>
🌐 Til — <b>🌐 Til</b>

Oddiy savolingizni ham yozishingiz mumkin.
"""
    )


# =========================
# DARS CALLBACKLARI
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("lesson_")
)
def lesson_callback(call):

    lessons_data = {

        "lesson_electric": """
<b>🔋 Elektr tizimi</b>

Avtomobil elektr tizimiga akkumulyator,
generator, starter, sug‘urtalar va boshqa
elektr jihozlari kiradi.

Akkumulyator dvigatelni ishga tushirishda
va elektr tizimini quvvatlashda muhim rol o‘ynaydi.
""",

        "lesson_engine": """
<b>🛢 Dvigatel</b>

Dvigatel yoqilg‘i energiyasini mexanik
energiyaga aylantiradi.

Asosiy qismlar:
• porshen
• silindr
• klapanlar
• krank vali
• taqsimlash vali
""",

        "lesson_gearbox": """
<b>⚙️ Uzatmalar qutisi</b>

Uzatmalar qutisi dvigatel momentini
g‘ildiraklarga kerakli uzatish nisbatida yetkazadi.

Mexanik va avtomatik turlari mavjud.
""",

        "lesson_brake": """
<b>🛞 Tormoz va yurish qismi</b>

Tormoz tizimi avtomobil tezligini kamaytirish
va uni to‘xtatish uchun xizmat qiladi.

Yurish qismiga osma, amortizator,
prujina va boshqa qismlar kiradi.
""",

        "lesson_cooling": """
<b>❄️ Sovutish tizimi</b>

Sovutish tizimi dvigatelning ish haroratini
me’yorda ushlab turishga yordam beradi.

Asosiy qismlar:
• radiator
• termostat
• suv nasosi
• ventilyator
"""
    }

    text = lessons_data.get(
        call.data,
        "Bu dars hozircha tayyor emas."
    )

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        text
    )


# =========================
# AVTOMOBIL SAVOL-JAVOB
# =========================

def diagnose_text(text):

    t = text.lower()

    if any(x in t for x in [
        "o't olmay",
        "ot olmay",
        "ishga tushmay",
        "yurmayapti"
    ]):
        return """
<b>🔧 Ehtimoliy sabablar:</b>

1. Akkumulyator kuchsiz bo‘lishi
2. Starter bilan muammo
3. Yoqilg‘i kelmasligi
4. Uchqun tizimida muammo
5. Datchik yoki elektr tizimida nosozlik

Avval akkumulyator holati va starter
ishlashini tekshirish kerak.
"""

    if any(x in t for x in [
        "qizib",
        "qiziyapti",
        "harorat"
    ]):
        return """
<b>🌡 Dvigatel qizib ketayotgan bo‘lishi mumkin.</b>

Ehtimoliy sabablar:
• sovutish suyuqligi kamaygan
• radiator muammosi
• termostat
• ventilyator
• suv nasosi

⚠️ Dvigatel juda qizigan bo‘lsa,
darhol to‘xtab, xavfsiz joyda sovishini kuting.
"""

    if any(x in t for x in [
        "far",
        "fara",
        "chiroq",
        "svet"
    ]):
        return """
<b>💡 Chiroq/fara muammosi</b>

Tekshiriladiganlar:
• lampochka
• sug‘urta
• rele
• simlar
• massa
• kalit

Agar faqat bitta fara ishlamasa,
lampochka yoki uning zanjirini tekshirishdan boshlash mumkin.
"""

    if any(x in t for x in [
        "akkumulyator",
        "akumulyator",
        "batareya"
    ]):
        return """
<b>🔋 Akkumulyator</b>

Akkumulyator tez o‘tirayotgan bo‘lsa:

• akkumulyatorning o‘zi
• generator zaryadi
• klemmalar
• avtomobildagi yashirin tok iste’moli

tekshirilishi kerak.
"""

    if any(x in t for x in [
        "check engine",
        "check",
        "motor chirog'i",
        "motor chirogi"
    ]):
        return """
<b>⚠️ Check Engine</b>

Bu indikator dvigatel yoki uning boshqaruv
tizimida xatolik qayd etilganini bildirishi mumkin.

Aniq sababni bilish uchun OBD diagnostika
qurilmasi orqali xato kodlarini o‘qish kerak.
"""

    return """
<b>🔧 UstaDrive</b>

Muammoni biroz batafsilroq yozing.

Masalan:

“Cobalt sovuqda o't olmayapti”
“Faralardan biri ishlamayapti”
“Dvigatel qizib ketyapti”
“Check Engine yondi”

Shunda ehtimoliy sabablarni tushuntiraman.
"""


@bot.message_handler(
    func=lambda message: message.text is not None
)
def text_handler(message):

    if not check_access(message):
        return

    text = message.text.strip()

    if not text:
        return

    # Menyu tugmalari yuqorida alohida handlerlarda ushlanadi.
    answer = diagnose_text(text)

    bot.send_message(
        message.chat.id,
        answer
    )


# =========================
# ADMIN
# =========================

@bot.message_handler(commands=["admin"])
def admin_handler(message):

    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(
            message.chat.id,
            "❌ Siz admin emassiz."
        )
        return

    bot.send_message(
        message.chat.id,
        """
<b>👨‍💼 UstaDrive Admin</b>

Bot ishlayapti.

Keyingi bosqichlarda:
• statistika
• reklama
• foydalanuvchilar
• xabar yuborish
• kanal boshqaruvi

kabi funksiyalarni qo‘shish mumkin.
"""
    )


# =========================
# XATOLARNI USHLASH
# =========================

def polling():

    while True:
        try:
            logging.info("UstaDriveBot ishga tushmoqda...")

            bot.remove_webhook()

            time.sleep(1)

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )

        except ApiTelegramException as e:

            logging.error(
                f"Telegram API xatosi: {e}"
            )

            # 409 Conflict bo‘lsa, boshqa bot instance
            # polling qilayotgan bo‘lishi mumkin.
            time.sleep(10)

        except Exception as e:

            logging.exception(
                f"Kutilmagan xato: {e}"
            )

            time.sleep(10)


# =========================
# START
# =========================

if __name__ == "__main__":
    polling()
