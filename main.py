import os
import re
import sqlite3
import logging
import telebot
from telebot import types

# =========================
# SOZLAMALAR
# =========================

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN Environment Variable topilmadi!")

ADMIN_ID = os.environ.get("ADMIN_ID", "")

BOT_NAME = "UstaDrive"
DB_FILE = "ustadrive.db"

CHANNEL_1 = "@ustadriveuz"
CHANNEL_2 = "@UstaDriveMarket"

CHANNEL_1_URL = "https://t.me/ustadriveuz"
CHANNEL_2_URL = "https://t.me/UstaDriveMarket"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# =========================
# DATABASE
# =========================

def db_connect():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            messages INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def save_user(user):
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, messages)
        VALUES (?, ?, ?, 0)
    """, (
        user.id,
        user.username or "",
        user.first_name or ""
    ))

    conn.commit()
    conn.close()


def add_message(user_id):
    conn = db_connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET messages = messages + 1 WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def get_stats():
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(messages), 0) FROM users")
    messages = cur.fetchone()[0]

    conn.close()

    return users, messages


# =========================
# OBUNA TEKSHIRISH
# =========================

def is_subscribed(user_id):
    try:
        member1 = bot.get_chat_member(CHANNEL_1, user_id)
        member2 = bot.get_chat_member(CHANNEL_2, user_id)

        good_status = ["member", "administrator", "creator"]

        return (
            member1.status in good_status
            and member2.status in good_status
        )

    except Exception as e:
        logging.warning(f"Obuna tekshirish xatosi: {e}")
        return False


def subscription_keyboard():
    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "📢 UstaDrive Uzbekistan",
            url=CHANNEL_1_URL
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🛒 UstaDrive Market",
            url=CHANNEL_2_URL
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    )

    return markup


def ask_subscription(chat_id):
    bot.send_message(
        chat_id,
        "🚗 <b>UstaDrive</b>\n\n"
        "Botdan foydalanish uchun quyidagi 2 ta kanalga obuna bo‘ling.\n\n"
        "Obuna bo‘lgach, <b>✅ Obunani tekshirish</b> tugmasini bosing.",
        reply_markup=subscription_keyboard()
    )


# =========================
# ASOSIY MENU
# =========================

def main_menu():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        "🤖 AI Usta",
        "🚨 Tez yordam"
    )

    markup.add(
        "📚 Avto maslahat",
        "📊 Statistika"
    )

    markup.add(
        "ℹ️ Yordam"
    )

    return markup


# =========================
# AVTO JAVOB TIZIMI
# =========================

def car_advice(text):
    text = text.lower().strip()

    # BALON
    if any(x in text for x in [
        "balon", "shina", "g'ildirak", "gildirak",
        "shina tesh", "balon tesh"
    ]):
        return (
            "🛞 <b>Balon/shina muammosi</b>\n\n"
            "1️⃣ Mashinani xavfsiz joyga chetga oling.\n"
            "2️⃣ Avariyka chiroqlarini yoqing.\n"
            "3️⃣ Agar shina juda bo‘shagan bo‘lsa, uzoqqa haydamang.\n"
            "4️⃣ Zapaska bo‘lsa, almashtirish mumkin.\n"
            "5️⃣ Domkratni faqat tekis va xavfsiz joyda ishlating.\n\n"
            "⚠️ Tezlikda yoki shikastlangan shina bilan yurish xavfli."
        )

    # AKKUMULYATOR
    if any(x in text for x in [
        "akkum", "akum", "batareya",
        "tok yo'q", "tok yoq", "zaryad"
    ]):
        return (
            "🔋 <b>Akkumulyator muammosi</b>\n\n"
            "Agar starter umuman aylanmasa yoki faqat "
            "«chert» ovozi chiqsa:\n\n"
            "1️⃣ Akkumulyator klemmalarini tekshiring.\n"
            "2️⃣ Klemma bo‘sh yoki oksidlangan bo‘lsa, tozalang.\n"
            "3️⃣ Faralar juda xira bo‘lsa, akkumulyator zaryadi past bo‘lishi mumkin.\n"
            "4️⃣ Imkon bo‘lsa kuchlanishni o‘lchang.\n\n"
            "⚠️ Simlarni noto‘g‘ri ulashdan ehtiyot bo‘ling."
        )

    # STARTER
    if "starter" in text or "start olmay" in text or "zavodka" in text:
        return (
            "🔑 <b>Starter / dvigatel ishga tushmasligi</b>\n\n"
            "Avval quyidagilarni tekshiring:\n"
            "1️⃣ Panel chiroqlari yonadimi?\n"
            "2️⃣ Starter aylanadimi?\n"
            "3️⃣ Faqat «chert» ovozi chiqadimi?\n"
            "4️⃣ Akkumulyator kuchlimi?\n"
            "5️⃣ Mashinada benzin yetarlimi?\n\n"
            "Agar starter aylanadi, lekin motor ishlamasa, "
            "muammo yoqilg‘i, uchqun yoki sensorlar tomonda bo‘lishi mumkin."
        )

    # QIZIB KETISH
    if any(x in text for x in [
        "qizib", "qiziyapti", "temperatura",
        "harorat", "peregrev", "antifriz"
    ]):
        return (
            "🌡️ <b>Dvigatel qizib ketayotgan bo‘lsa</b>\n\n"
            "1️⃣ Xavfsiz joyga to‘xtang.\n"
            "2️⃣ Dvigatelni zo‘riqtirmang.\n"
            "3️⃣ Harorat juda yuqori bo‘lsa, mashinani o‘chiring.\n"
            "4️⃣ Radiator va antifriz tizimini tekshirtiring.\n\n"
            "⚠️ Issiq radiator qopqog‘ini darhol ochmang — "
            "qaynagan suyuqlik kuyishga olib kelishi mumkin."
        )

    # MOTOR MOYI
    if any(x in text for x in [
        "moy", "maslo", "oil", "dvigatel moyi"
    ]):
        return (
            "🛢️ <b>Dvigatel moyi</b>\n\n"
            "Moy sathi past bo‘lsa, dvigatelni uzoq ishlatmang.\n\n"
            "1️⃣ Mashinani tekis joyga qo‘ying.\n"
            "2️⃣ Dvigatelni o‘chirib biroz kuting.\n"
            "3️⃣ Shchup orqali moy sathini tekshiring.\n"
            "4️⃣ Moy sizib chiqayotgan bo‘lsa, sababini aniqlating.\n\n"
            "⚠️ Moy bosimi chirog‘i yonib tursa, haydashni davom ettirmang."
        )

    # BRAKE
    if any(x in text for x in [
        "tormoz", "kolodka", "brake"
    ]):
        return (
            "🛑 <b>Tormoz muammosi</b>\n\n"
            "Tormoz pedali juda yumshoq bo‘lsa, "
            "mashina bir tomonga tortsa yoki tormoz samarasi kamaygan bo‘lsa:\n\n"
            "⚠️ Mashinani tez haydamang.\n"
            "⚠️ Imkon qadar xavfsiz joyda to‘xtang.\n"
            "🔧 Tormoz tizimini ustaga ko‘rsatish kerak."
        )

    # CHECK ENGINE
    if any(x in text for x in [
        "check engine", "check", "motor chirog'i",
        "motor chirogi", "dvigatel chirog"
    ]):
        return (
            "🟠 <b>Check Engine</b>\n\n"
            "Bu chiroq turli sabablar bilan yonishi mumkin:\n\n"
            "• Sensor xatosi\n"
            "• Shamlar yoki ignition tizimi\n"
            "• Yoqilg‘i tizimi\n"
            "• Havo aralashmasi\n"
            "• Katalizator va boshqa tizimlar\n\n"
            "🔧 Aniq sababni OBD diagnostika orqali aniqlash mumkin.\n\n"
            "Agar chiroq miltillayotgan bo‘lsa yoki motor kuchli "
            "titratayotgan bo‘lsa, mashinani zo‘riqtirmang."
        )

    # ELEKTRIKA
    if any(x in text for x in [
        "elektr", "predoxranitel", "fuse",
        "chiroq", "far", "signal"
    ]):
        return (
            "⚡ <b>Elektr tizimi</b>\n\n"
            "Muammo qaysi qurilmada ekanini aniqlash muhim.\n\n"
            "1️⃣ Akkumulyator kuchlanishini tekshiring.\n"
            "2️⃣ Klemma va massa ulanishlarini ko‘ring.\n"
            "3️⃣ Tegishli predoxranitelni tekshiring.\n"
            "4️⃣ Simlarda kuyish yoki uzilish bor-yo‘qligini ko‘ring.\n\n"
            "⚠️ Noma’lum simlarni bir-biriga ulab ko‘rmang."
        )

    # KALIT / SIGNALIZATSIYA
    if any(x in text for x in [
        "kalit", "signalizatsiya", "signalizaciya",
        "alarm", "pult"
    ]):
        return (
            "🔑 <b>Kalit / signalizatsiya</b>\n\n"
            "1️⃣ Pult batareyasini tekshiring.\n"
            "2️⃣ Zaxira kalit bo‘lsa, sinab ko‘ring.\n"
            "3️⃣ Akkumulyator kuchlanishini tekshiring.\n"
            "4️⃣ Immobilayzer belgisi yonayotgan bo‘lsa, "
            "diagnostika talab qilinishi mumkin."
        )

    # COBALT
    if "cobalt" in text:
        return (
            "🚗 <b>Chevrolet Cobalt</b>\n\n"
            "Muammoni aniqroq aniqlash uchun quyidagilarni yozing:\n\n"
            "• Mashina ishga tushmayaptimi?\n"
            "• Motor qiziyaptimi?\n"
            "• Check Engine yonib turibdimi?\n"
            "• G‘alati ovoz bormi?\n"
            "• Tormoz yoki rulda muammo bormi?\n\n"
            "Muammoni oddiy tilda yozing — UstaDrive mos tekshiruvlarni tavsiya qiladi."
        )

    # NEXIA
    if "nexia" in text:
        return (
            "🚗 <b>Chevrolet Nexia</b>\n\n"
            "Muammoni yozing: motor, starter, tormoz, "
            "qizish, elektr yoki boshqa muammo."
        )

    # GENTRA
    if "gentra" in text:
        return (
            "🚗 <b>Chevrolet Gentra</b>\n\n"
            "Muammoni batafsil yozing. Masalan:\n"
            "«Gentra ishga tushmayapti» yoki "
            "«Gentra qizib ketyapti»."
        )

    # LACETTI
    if "lacetti" in text:
        return (
            "🚗 <b>Chevrolet Lacetti</b>\n\n"
            "Muammoni yozing: motor, tormoz, "
            "elektr, qizish yoki boshqa nosozlik."
        )

    # DEFAULT
    return (
        "🤖 <b>UstaDrive Usta</b>\n\n"
        "Muammoni tushundim, lekin aniqroq maslahat berish "
        "uchun biroz ko‘proq ma’lumot kerak.\n\n"
        "Masalan:\n"
        "🛞 «Cobalt baloni teshilib qoldi»\n"
        "🔋 «Akkumulyator o‘tirib qoldi»\n"
        "🔑 «Mashina zavod olmayapti»\n"
        "🌡️ «Motor qizib ketyapti»\n"
        "🟠 «Check Engine yondi»\n"
        "🛑 «Tormoz yumshab qoldi»\n\n"
        "Muammoni oddiy tilda yozavering."
    )


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user)

    if not is_subscribed(message.from_user.id):
        ask_subscription(message.chat.id)
        return

    bot.send_message(
        message.chat.id,
        "🚗 <b>UstaDrive'ga xush kelibsiz!</b>\n\n"
        "Men sizga avtomobil muammolarini tushunishda yordam beraman.\n\n"
        "Muammoni oddiy tilda yozing. Masalan:\n"
        "«Cobalt baloni teshilib qoldi, nima qilay?»",
        reply_markup=main_menu()
    )


# =========================
# OBUNA CALLBACK
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription(call):

    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.send_message(
            call.message.chat.id,
            "🎉 <b>Obuna tasdiqlandi!</b>\n\n"
            "Endi UstaDrive'dan foydalanishingiz mumkin.",
            reply_markup=main_menu()
        )

    else:
        bot.answer_callback_query(
            call.id,
            "❌ Ikkala kanalga ham obuna bo‘ling!",
            show_alert=True
        )


# =========================
# ADMIN
# =========================

@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(
            message,
            "⛔ Siz admin emassiz."
        )
        return

    users, messages = get_stats()

    bot.send_message(
        message.chat.id,
        f"👑 <b>ADMIN PANEL</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"💬 Xabarlar: <b>{messages}</b>"
    )


# =========================
# YORDAM
# =========================

@bot.message_handler(commands=["help"])
def help_command(message):

    bot.send_message(
        message.chat.id,
        "ℹ️ <b>UstaDrive yordam</b>\n\n"
        "Mashina muammosini oddiy tilda yozing.\n\n"
        "Masalan:\n"
        "• Cobalt baloni teshildi\n"
        "• Mashina zavod olmayapti\n"
        "• Akkumulyator o‘tirib qoldi\n"
        "• Motor qiziyapti\n"
        "• Check Engine yondi\n"
        "• Tormoz ishlamayapti\n\n"
        "⚠️ Xavfli vaziyatlarda avvalo xavfsiz joyga to‘xtang."
    )


# =========================
# TEXT HANDLER
# =========================

@bot.message_handler(content_types=["text"])
def text_handler(message):

    save_user(message.from_user)

    if not is_subscribed(message.from_user.id):
        ask_subscription(message.chat.id)
        return

    add_message(message.from_user.id)

    text = message.text.strip()

    if text == "🤖 AI Usta":
        bot.send_message(
            message.chat.id,
            "🤖 <b>Usta bilan gaplashing</b>\n\n"
            "Mashina muammosini oddiy tilda yozing."
        )
        return

    if text == "🚨 Tez yordam":
        bot.send_message(
            message.chat.id,
            "🚨 <b>TEZ YORDAM</b>\n\n"
            "Agar mashina yo‘lda qolgan bo‘lsa:\n\n"
            "1️⃣ Xavfsiz joyga o‘ting.\n"
            "2️⃣ Avariyka chiroqlarini yoqing.\n"
            "3️⃣ Muammoni yozing.\n\n"
            "Masalan: «Cobalt yo‘lda o‘chib qoldi»."
        )
        return

    if text == "📚 Avto maslahat":
        bot.send_message(
            message.chat.id,
            "📚 <b>Avto maslahatlar</b>\n\n"
            "🛢 Moyni vaqtida almashtirish\n"
            "🌡 Antifriz va haroratni nazorat qilish\n"
            "🔋 Akkumulyatorni tekshirish\n"
            "🛞 Shina bosimini nazorat qilish\n"
            "🛑 Tormozlarni vaqtida tekshirtirish\n"
            "⚡ Elektr tizimini ehtiyot qilish"
        )
        return

    if text == "📊 Statistika":
        users, messages = get_stats()

        bot.send_message(
            message.chat.id,
            f"📊 <b>UstaDrive statistikasi</b>\n\n"
            f"👥 Foydalanuvchilar: {users}\n"
            f"💬 Jami murojaatlar: {messages}"
        )
        return

    if text == "ℹ️ Yordam":
        help_command(message)
        return

    # Oddiy avtomobil savoli
    answer = car_advice(text)

    bot.reply_to(
        message,
        answer
    )


# =========================
# PHOTO HANDLER
# =========================

@bot.message_handler(content_types=["photo"])
def photo_handler(message):

    save_user(message.from_user)

    if not is_subscribed(message.from_user.id):
        ask_subscription(message.chat.id)
        return

    add_message(message.from_user.id)

    bot.reply_to(
        message,
        "🖼️ <b>Rasm qabul qilindi.</b>\n\n"
        "Hozircha rasmni avtomatik AI orqali tahlil qilish "
        "funksiyasi ulanmagan.\n\n"
        "Rasmda nima muammo ekanini yozib yuborsangiz, "
        "UstaDrive maslahat beradi.\n\n"
        "Masalan: «Paneldagi mana shu chiroq nimani bildiradi?»"
    )


# =========================
# ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":
    init_db()

    print("🚗 UstaDrive ishga tushdi!")

    bot.infinity_polling(
        skip_pending=True,
        timeout=60,
        long_polling_timeout=60
        )
