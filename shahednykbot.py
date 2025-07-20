import asyncio
import logging
import random
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from telethon.errors import SessionPasswordNeededError
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 🔐 Дані для Telethon
api_id = 26549615
api_hash = 'f43d6245868e5bae41c40872fb873dec'
phone_number = '+380500290291'

# 🤖 Токен бота
BOT_TOKEN = '7395027911:AAGkiRcvxs8hP878uv9nvo5mGwDe39loxFg'

# 📡 Канали для моніторингу
CHANNELS = [
    'https://t.me/DeepStateUA',
    'https://t.me/RVvoenkor',
    'https://t.me/sentdefender',
    'https://t.me/PpoUaRadar',
    'https://t.me/vanek_nikolaev'
]

# 🧠 Запамʼятовуємо останні ID повідомлень
last_messages = {}
logging.basicConfig(level=logging.INFO)

# ▶️ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Ситуація ⚠️")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Привіт! Я бот Шахедик. Натисни кнопку 'Ситуація', щоб перевірити обстановку.",
        reply_markup=markup
    )

# 🛑 Unknown текст
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Просто натисни кнопку 'Ситуація'. Я не читаю повідомлення.")

# 📡 Реакція на кнопку
async def situation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Перевіряю повідомлення з каналів...")
    messages = await fetch_latest_posts()
    if messages:
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text("✅ Все спокійно, нічого нового не зафіксовано.")

# 📥 Отримання новин з каналів (з гумором та фільтром)
async def fetch_latest_posts():
    client = TelegramClient('anon_session', api_id, api_hash)
    await client.connect()
    messages = []

    keywords = ['шахед', 'шаходрон', 'дрон', 'ракета', 'кінжал', 'іскандер', 'удар', 'приліт', 'карта', 'тривога']
    humor = [
        'Погані шахедики знову летять 😒',
        'Горєшнік говнєшнік десь в дорозі ✈️',
        'Геть смерть і воші — сховайся, друже 🐀',
        'Нічна карта прилетів — романтика...',
        'Ракетна вечеря — не для нас 😬',
        'Щось мчить... мабуть не голуб миру 🕊️',
        'Летить, але не сюрприз від Санти 🎅',
    ]

    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone_number)
            code = input("Введи код з Telegram: ")
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            pw = input("Telegram просить пароль (2FA): ")
            await client.sign_in(password=pw)

    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)
            async for msg in client.iter_messages(entity, limit=5):
                if msg.id == last_messages.get(channel):
                    break

                text_matched = False
                if msg.text:
                    lower_text = msg.text.lower()
                    if any(kw in lower_text for kw in keywords):
                        text_matched = True
                        funny = random.choice(humor)
                        messages.append(f"📡 {channel.split('/')[-1]}:\n{funny}\n\n{msg.text[:800]}")

                if msg.media and isinstance(msg.media, MessageMediaPhoto):
                    messages.append(f"🗺 Карта або фото з {channel.split('/')[-1]} — подивись сам.")

                if text_matched or msg.media:
                    last_messages[channel] = msg.id

        except Exception as e:
            messages.append(f"⚠️ Не вдалось прочитати {channel}: {e}")

    await client.disconnect()
    return messages

# 🚀 Запуск бота
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(Ситуація ⚠️)$"), situation))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    print("✅ Бот Шахедик запущено. Слухаємо канали.")
    await app.run_polling()

# 🟢 Запускаємо
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())




