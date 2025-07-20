
import asyncio
import logging
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from telethon.errors import SessionPasswordNeededError
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import nest_asyncio
import os
import random

# Дані доступу
api_id = 26549615
api_hash = "f43d6245868e5bae41c40872fb873dec"
bot_token = "7395027911:AAGkiRcvxs8hP878uv9nvo5mGwDe39loxFg"

# Канали для моніторингу
channels = [
    "https://t.me/DeepStateUA",
    "https://t.me/RVvoenkor",
    "https://t.me/sentdefender",
    "https://t.me/PpoUaRadar",
    "https://t.me/vanek_nikolaev"
]

keywords = ["шахед", "шахеди", "дрон", "ракета", "ракети", "тривога", "прильот", "вибух", "іскандер", "кінжал", "смерч", "торнадо", "гради", "повітряна", "ядерна"]

# Заміна фраз для гумору
jokes = [
    "🧠 <b>Гумор бота</b>: погані шахедики знову літають, а ми тримаємось!",
    "🤣 <b>Гумор</b>: знову ці мухожуки прилетіли! Де ракетка?",
    "🔥 <b>Коментар</b>: час сховатись у ванні та прикинутись мокрою тряпкою.",
    "📡 <b>Звіт</b>: тривога, бо ракети вирішили трохи політати.",
    "💩 <b>Інфа</b>: шахеди знову в режимі дурки — бережи голову!",
]

# Стартова клавіатура
keyboard = [[KeyboardButton("Ситуація")]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Ініціалізація Telegram бота
app = ApplicationBuilder().token(bot_token).build()

# Ініціалізація Telethon клієнта
nest_asyncio.apply()
client = TelegramClient("anon", api_id, api_hash)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Я бот Шахедик 🤖. Натисни 'Ситуація', щоб дізнатись останні новини.", reply_markup=reply_markup)

# Обробка кнопки "Ситуація"
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Ситуація":
        messages = []
        media = []

        async with client:
            for channel in channels:
                try:
                    entity = await client.get_entity(channel)
                    async for msg in client.iter_messages(entity, limit=10):
                        if msg.text and any(word in msg.text.lower() for word in keywords):
                            if not msg.text.startswith("🔞") and "@" not in msg.text:
                                messages.append(f"<b>📡 {channel.split('/')[-1]}:</b>
{msg.text[:800]}")
                            if msg.media and isinstance(msg.media, MessageMediaPhoto):
                                media.append(msg.media)

                except Exception as e:
                    print(f"❌ Помилка в {channel}: {e}")

        if messages:
            await update.message.reply_text(random.choice(jokes), parse_mode=ParseMode.HTML)
            for text in messages[:5]:
                await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("Немає актуальної інформації 💤", reply_markup=reply_markup)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

# Запуск
if __name__ == "__main__":
    client.start()
    app.run_polling()
