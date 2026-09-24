import os
import logging
import telebot
from telebot import types

# =========================================================
# USTADRIVE
# =========================================================

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID", "")

CHANNEL_1 = "@ustadriveuz"
CHANNEL_2 = "@UstaDriveMarket"

BOT_NAME = "UstaDrive"

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi! Render Environment Variables ichiga BOT_TOKEN qo‘shing."
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# =========================================================
# ASOSIY MENU
# =========================================================

def main_menu():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("🔧 Avto yordam"),
        types.KeyboardButton("🚨 Tez yordam"),
    )

    markup.add(
        types.KeyboardButton("📚 Maslahatlar"),
        types.KeyboardButton("ℹ️ Yordam"),
    )

    return markup


# =========================================================
# OBUNA TEKSHIRISH
# =========================================================

def is_subscribed(user_id):
    channels = [CHANNEL_1, CHANNEL_2]

    for channel in channels:
        try:
            member = bot.get_chat_member(channel, user_id)

            if member.status in ["left", "kicked"]:
                return False

        except Exception as e:
            logging.error(
                f"Obuna tekshirishda xato: {channel} -> {e}"
            )
            return False

    return True


def subscription_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "📢 UstaDriveUZ kanaliga qo‘shilish",
            url="https://t.me/ustadriveuz"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🛒 UstaDriveMarket kanaliga qo‘shilish",
            url="https://t.me/UstaDriveMarket"
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
        """
<b>🔐 UstaDrive'ga xush kelibsiz!</b>

Botdan foydalanish uchun avval quyidagi <b>2 ta kanalga</b> qo‘shiling:

📢 <b>UstaDriveUZ</b>
🛒 <b>UstaDriveMarket</b>

Kanalga qo‘shilgandan keyin:

<b>✅ Obunani tekshirish</b>

tugmasini bosing.
""",
        reply_markup=subscription_keyboard()
    )


def require_subscription(message):
    if is_subscribed(message.from_user.id):
        return True

    send_subscription_message(message.chat.id)
    return False


# =========================================================
# AVTOMOBIL MASLAHAT TIZIMI
# =========================================================

def car_advice(text):

    t = text.lower().strip()

    # -----------------------------------------------------
    # SALOMLASHISH
    # -----------------------------------------------------

    if any(word in t for word in [
        "salom",
        "assalom",
        "assalomu",
        "hello",
        "hi"
    ]):
        return """
<b>👋 Assalomu alaykum!</b>

Men <b>UstaDrive</b> — avtomobil muammolarini tushuntirishga yordam beradigan botman. 🚗🔧

Muammoni oddiy qilib yozing.

Masalan:

🛞 Cobalt baloni teshilib qoldi
🔋 Akkumulyator o‘tirib qoldi
🚗 Mashina o‘t olmayapti
🌡 Cobalt qizib ketyapti
🚨 Check Engine yonib qoldi
🛑 Tormoz yaxshi ishlamayapti
"""


    # -----------------------------------------------------
    # BALON / SHINA
    # -----------------------------------------------------

    if any(word in t for word in [
        "balon",
        "shina",
        "g'ildirak",
        "gildirak",
        "teshildi",
        "teshib",
        "teshik",
        "baloni"
    ]):

        return """
<b>🛞 BALON / SHINA MUAMMOSI</b>

Agar shina teshilgan bo‘lsa:

1️⃣ Mashinani xavfsiz joyga sekin to‘xtating.
2️⃣ Avariya chirog‘ini yoqing.
3️⃣ Shina juda bo‘shagan bo‘lsa, haydashni davom ettirmang.
4️⃣ Zapas balon bo‘lsa, uni qo‘yish mumkin.
5️⃣ Domkratni faqat tekis va mustahkam joyda ishlating.

Agar shina yon tomondan jiddiy shikastlangan bo‘lsa, ta’mirlashga urinmasdan vulkanizatsiyaga murojaat qilish kerak.

⚠️ Mashina ostiga faqat domkratga tayanib kirmang.
"""


    # -----------------------------------------------------
    # AKKUMULYATOR
    # -----------------------------------------------------

    if any(word in t for word in [
        "akkumulyator",
        "akumulyator",
        "akum",
        "akkum",
        "batareya",
        "tok yo'q",
        "tok yoq"
    ]):

        return """
<b>🔋 AKKUMULYATOR MUAMMOSI</b>

Agar mashina starter aylantirmayotgan bo‘lsa:

• Faralar juda xira bo‘lsa — akkumulyator zaryadi past bo‘lishi mumkin.
• Klemalar bo‘sh yoki oksidlangan bo‘lishi mumkin.
• Akkumulyator kuchsiz bo‘lsa, tok berish kerak bo‘lishi mumkin.
• Starter faqat “chert” etsa — akkumulyator yoki starter tizimini tekshirish kerak.

⚠️ Boshqa mashinadan tok berishda + va − qutblarni adashtirmang.
"""


    # -----------------------------------------------------
    # MASHINA O'T OLMAYAPTI
    # -----------------------------------------------------

    if any(word in t for word in [
        "o't olmay",
        "ot olmay",
        "ot olmayapti",
        "o't olmayapti",
        "ishga tushmay",
        "ishga tushmayapti",
        "start olmay",
        "yurmayapti",
        "yurmayabdi"
    ]):

        return """
<b>🚗 MASHINA O‘T OLMAYAPTI</b>

Avval quyidagilarni aniqlang:

1️⃣ Starter aylanadimi?
2️⃣ Panel chiroqlari yonadimi?
3️⃣ Yoqilg‘i bormi?
4️⃣ Starter aylanganda noodatiy ovoz bormi?
5️⃣ Panelda Check Engine yoki boshqa belgi bormi?

🔋 Starter umuman aylanmasa — akkumulyator, klemma yoki starter tizimi sabab bo‘lishi mumkin.

⚙️ Starter aylansa-yu, motor ishga tushmasa — yoqilg‘i, uchqun yoki dvigatel boshqaruv tizimini tekshirtirish kerak bo‘lishi mumkin.
"""


    # -----------------------------------------------------
    # QIZIB KETISH
    # -----------------------------------------------------

    if any(word in t for word in [
        "qizib",
        "qiziyapti",
        "qizib ket",
        "temperatura",
        "harorat",
        "bug'",
        "bug‘",
        "bug chiq",
        "radiator"
    ]):

        return """
<b>🌡 DVIGATEL QIZIB KETMOQDA</b>

Agar harorat juda ko‘tarilgan yoki kapot ostidan bug‘ chiqayotgan bo‘lsa:

1️⃣ Xavfsiz joyga to‘xtang.
2️⃣ Dvigatelni zo‘riqtirmang.
3️⃣ Qizigan radiator qopqog‘ini darhol ochmang.
4️⃣ Dvigatel sovishini kuting.
5️⃣ Sovigandan keyin sovutish suyuqligi kamaygan-kamaymaganini tekshirish mumkin.

Agar suyuqlik oqayotgan bo‘lsa yoki mashina yana tez qizisa, haydashni davom ettirmang.

🔧 Ustaga ko‘rsatish kerak.
"""


    # -----------------------------------------------------
    # CHECK ENGINE
    # -----------------------------------------------------

    if any(word in t for word in [
        "check",
        "check engine",
        "checkengine",
        "motor chirog'i",
        "motor chirogi",
        "dvigatel chirog'i",
        "dvigatel chirogi"
    ]):

        return """
<b>🚨 CHECK ENGINE</b>

Check Engine yonishi dvigatel yoki uning boshqaruv tizimida xatolik borligini bildirishi mumkin.

🔎 Aniq sababni bilish uchun OBD diagnostika kerak bo‘lishi mumkin.

Agar Check Engine <b>miltillayotgan</b> bo‘lsa yoki mashina kuchli titrasa, haydashni davom ettirmaslik xavfsizroq.

🔧 Diagnostika qildirish tavsiya etiladi.
"""


    # -----------------------------------------------------
    # MOY
    # -----------------------------------------------------

    if any(word in t for word in [
        "moy",
        "maslo",
        "yog'",
        "yog‘",
        "motor moyi"
    ]):

        return """
<b>🛢 DVIGATEL MOYI</b>

Moyni tekshirish:

1️⃣ Mashinani tekis joyga qo‘ying.
2️⃣ Dvigatelni o‘chiring.
3️⃣ Biroz kuting.
4️⃣ Shchup orqali moy darajasini tekshiring.
5️⃣ Daraja MIN dan past bo‘lsa, mos moy masalasini hal qilish kerak.

⚠️ Agar moy bosimi chirog‘i yonib turgan bo‘lsa, mashinani haydashda davom etmang.
"""


    # -----------------------------------------------------
    # TORMOZ
    # -----------------------------------------------------

    if any(word in t for word in [
        "tormoz",
        "kolodka",
        "tormozlamay",
        "tormoz ishlamay",
        "tormoz ishlamayapti"
    ]):

        return """
<b>🛑 TORMOZ MUAMMOSI</b>

Agar:

• pedal juda yumshoq bo‘lsa;
• pedal juda past tushsa;
• tormozlash keskin yomonlashgan bo‘lsa;
• tormoz suyuqligi sizayotgan bo‘lsa;

⚠️ Mashinani haydashni davom ettirmang.

Tormoz tizimi xavfsizlik uchun juda muhim.

🔧 Usta tomonidan tekshirtirish kerak.
"""


    # -----------------------------------------------------
    # STARTER
    # -----------------------------------------------------

    if any(word in t for word in [
        "starter",
        "startyor",
        "start",
        "chert",
        "klik",
        "starter aylanmay"
    ]):

        return """
<b>🔑 STARTER MUAMMOSI</b>

Kalitni buraganda faqat “chert” etsa:

🔋 Akkumulyator kuchsiz bo‘lishi mumkin.
🔩 Klemalar bo‘sh yoki oksidlangan bo‘lishi mumkin.
⚙️ Starter yoki rele tizimida muammo bo‘lishi mumkin.

Akkumulyator yaxshi bo‘lsa-yu starter ishlamasa, diagnostika kerak.
"""


    # -----------------------------------------------------
    # ELEKTR
    # -----------------------------------------------------

    if any(word in t for word in [
        "elektr",
        "svet",
        "svetlar",
        "chiroq",
        "far",
        "fara",
        "signal",
        "predoxranitel",
        "predoxranitel",
        "fuse"
    ]):

        return """
<b>💡 ELEKTR TIZIMI</b>

Elektr jihoz ishlamasa:

• Predoxranitelni tekshirish mumkin.
• Klemma va ulanishlarni ko‘rish kerak.
• Lampochka kuygan bo‘lishi mumkin.
• Bir nechta qurilma birdan ishlamasa, asosiy elektr ta’minoti yoki sug‘urta tizimida muammo bo‘lishi mumkin.

⚠️ Simlarni tasodifiy ulab ko‘rmang — qisqa tutashuv xavfi bor.
"""


    # -----------------------------------------------------
    # ANTIFRIZ
    # -----------------------------------------------------

    if any(word in t for word in [
        "antifriz",
        "antifreez",
        "sovutish suyuqligi"
    ]):

        return """
<b>💧 ANTIFRIZ</b>

Antifriz kamaygan bo‘lsa, faqat to‘ldirish bilan cheklanmasdan sizib chiqish sababini ham aniqlash kerak.

⚠️ Qizigan dvigatelda radiator qopqog‘ini ochmang.

Agar suyuqlik tez kamayib ketsa yoki mashina qizisa, ustaga murojaat qiling.
"""


    # -----------------------------------------------------
    # KALIT / SIGNALIZATSIYA
    # -----------------------------------------------------

    if any(word in t for word in [
        "kalit",
        "signalizatsiya",
        "pult",
        "eshik ochilmay",
        "qulf"
    ]):

        return """
<b>🔐 KALIT / SIGNALIZATSIYA</b>

Agar pult ishlamayotgan bo‘lsa:

🔋 Pult batareyasi tugagan bo‘lishi mumkin.
🚗 Mashina akkumulyatorini tekshirish kerak.
🔑 Zaxira kalit bo‘lsa, undan foydalanib ko‘ring.

Immobilayzer belgisi chiqsa, kalitni tanimaslik bilan bog‘liq muammo bo‘lishi mumkin.
"""


    # -----------------------------------------------------
    # COBALT
    # -----------------------------------------------------

    if "cobalt" in t:

        return """
<b>🚗 CHEVROLET COBALT</b>

Cobalt bo‘yicha yordam beraman.

Muammoni aniqroq yozing:

🛞 Cobalt baloni teshildi
🔋 Cobalt akkumulyatori o‘tirib qoldi
🚗 Cobalt o‘t olmayapti
🌡 Cobalt qizib ketyapti
🚨 Cobalt panelida Check yondi
🛑 Cobalt tormozi qattiq bo‘lib qoldi

Muammoni qancha batafsil yozsangiz, shuncha aniqroq maslahat beraman.
"""


    # -----------------------------------------------------
    # NEXIA
    # -----------------------------------------------------

    if "nexia" in t:

        return """
<b>🚗 NEXIA</b>

Nexia bo‘yicha ham yordam beraman.

Muammoni yozing:

• o‘t olmayapti
• qizib ketyapti
• starter ishlamayapti
• balon teshildi
• akkumulyator o‘tirib qoldi
• Check Engine yondi
"""


    # -----------------------------------------------------
    # GENTRA / LACETTI
    # -----------------------------------------------------

    if any(word in t for word in [
        "gentra",
        "lacetti",
        "lasetti"
    ]):

        return """
<b>🚗 AVTOMOBIL MUAMMOSI</b>

Bu avtomobil bo‘yicha ham yordam beraman.

Muammoni belgisi bilan yozing.

Masalan:

<i>Gentra starter aylanadi, lekin motor o‘t olmayapti.</i>

yoki:

<i>Lacetti qizib ketyapti.</i>
"""


    # -----------------------------------------------------
    # UMUMIY YORDAM
    # -----------------------------------------------------

    if any(word in t for word in [
        "yordam",
        "nima qilay",
        "nima qilaman"
    ]):

        return """
<b>🔧 UstaDrive yordam beradi</b>

Muammoni avtomobil rusumi bilan yozing.

Masalan:

🚗 Cobalt — o‘t olmayapti
🛞 Cobalt — baloni teshildi
🔋 Nexia — akkumulyator o‘tirib qoldi
🌡 Gentra — qizib ketyapti
🚨 Lacetti — Check Engine yondi
"""


    # -----------------------------------------------------
    # TOPILMAGAN MUAMMO
    # -----------------------------------------------------

    return """
<b>🤔 Muammoni to‘liq tushunmadim.</b>

Avtomobil rusumi + muammoni yozib ko‘ring.

Masalan:

<i>Cobalt baloni teshilib qoldi nima qilay?</i>

yoki:

<i>Nexia 3 starter aylanyapti lekin motor o't olmayapti.</i>

🔧 Muammoni qancha batafsil yozsangiz, shuncha yaxshi tahlil qilaman.
"""


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    if not require_subscription(message):
        return

    name = message.from_user.first_name or "do‘st"

    bot.send_message(
        message.chat.id,
        f"""
<b>🚗 UstaDrive</b>

Assalomu alaykum, <b>{name}</b>! 👋

Men avtomobil muammolarini tushuntirishga yordam beraman. 🔧

<b>Tugma bosishingiz shart emas.</b>

Muammoni oddiy qilib yozing.

Masalan:

<i>“Cobalt baloni teshilib qoldi, nima qilay?”</i>

Men imkon qadar bosqichma-bosqich yordam beraman.
""",
        reply_markup=main_menu()
    )


# =========================================================
# OBUNA TEKSHIRISH TUGMASI
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_subscription_callback(call):

    if is_subscribed(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.send_message(
            call.message.chat.id,
            """
<b>✅ Obuna tasdiqlandi!</b>

UstaDrive'dan foydalanishingiz mumkin. 🚗🔧

Avtomobil muammosini yozing.
""",
            reply_markup=main_menu()
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Hali ikkala kanalga ham qo‘shilmagansiz.",
            show_alert=True
        )


# =========================================================
# MATNLI XABAR
# =========================================================

@bot.message_handler(content_types=["text"])
def text_handler(message):

    if not require_subscription(message):
        return

    text = message.text.strip()

    # MENU TUGMALARI
    if text == "🔧 Avto yordam":

        bot.send_message(
            message.chat.id,
            """
<b>🔧 Avto yordam</b>

Avtomobil muammosini oddiy qilib yozing.

Masalan:

<i>Cobalt baloni teshildi nima qilay?</i>
""",
            reply_markup=main_menu()
        )

        return


    if text == "🚨 Tez yordam":

        bot.send_message(
            message.chat.id,
            """
<b>🚨 TEZKOR YORDAM</b>

Agar mashina yo‘lda buzilgan bo‘lsa:

1️⃣ Xavfsiz joyga to‘xtang.
2️⃣ Avariya chirog‘ini yoqing.
3️⃣ Yo‘l harakatiga xalaqit bermang.
4️⃣ Xavfli nosozlik bo‘lsa, haydashni davom ettirmang.

Muammoni yozing — nima qilish mumkinligini tushuntiraman.
""",
            reply_markup=main_menu()
        )

        return


    if text == "📚 Maslahatlar":

        bot.send_message(
            message.chat.id,
            """
<b>📚 AVTO MASLAHATLAR</b>

🛢 Dvigatel moyini tekshirish
💧 Antifriz darajasini nazorat qilish
🔋 Akkumulyator holatini tekshirish
🛞 Shina bosimini nazorat qilish
🛑 Tormoz tizimini vaqtida tekshirtirish
🚨 Paneldagi ogohlantirishlarni e'tiborsiz qoldirmaslik
🔧 G‘alati tovushlarni vaqtida tekshirtirish
""",
            reply_markup=main_menu()
        )

        return


    if text == "ℹ️ Yordam":

        bot.send_message(
            message.chat.id,
            """
<b>ℹ️ UstaDrive</b>

Tugmalar bilan yoki oddiy yozib foydalanishingiz mumkin.

Masalan:

🚗 Cobalt o‘t olmayapti
🛞 Balon teshildi
🔋 Akkumulyator o‘tirib qoldi
🌡 Motor qizib ketdi
🚨 Check Engine yondi
🛑 Tormoz ishlamayapti
""",
            reply_markup=main_menu()
        )

        return


    # ODDIY SAVOL
    answer = car_advice(text)

    bot.send_message(
        message.chat.id,
        answer,
        reply_markup=main_menu()
    )


# =========================================================
# RASM
# =========================================================

@bot.message_handler(content_types=["photo"])
def photo_handler(message):

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        """
<b>📸 Rasm qabul qilindi.</b>

Rasmni ko‘rdim, lekin hozirgi versiyada avtomatik AI rasm diagnostikasi ulanmagan.

Rasm bilan birga muammoni yozing:

<i>“Panelda shu belgi chiqdi, bu nima?”</i>

Keyingi versiyada rasmni avtomatik tahlil qilish modulini ham ulashimiz mumkin.
""",
        reply_markup=main_menu()
    )


# =========================================================
# ADMIN
# =========================================================

@bot.message_handler(commands=["admin"])
def admin(message):

    if not ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "⚠️ ADMIN_ID sozlanmagan."
        )
        return

    if str(message.from_user.id) != str(ADMIN_ID):

        bot.send_message(
            message.chat.id,
            "⛔ Siz admin emassiz."
        )

        return

    bot.send_message(
        message.chat.id,
        """
<b>👨‍🔧 UstaDrive ADMIN PANEL</b>

✅ Bot ishlayapti.

Keyingi kengaytirishlar:

📊 Statistika
👥 Foydalanuvchilar
📢 Reklama yuborish
➕ Yangi maslahat qo‘shish
🚗 Yangi avtomobil qo‘shish
🛠 Diagnostika bazasi
"""
    )


# =========================================================
# BOTNI ISHGA TUSHIRISH
# =========================================================

print("🚗 UstaDrive ishga tushdi...")

bot.infinity_polling(
    skip_pending=True,
    timeout=60,
    long_polling_timeout=60
    )
