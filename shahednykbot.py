import asyncio
import random
import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
import os

# 🔐 Конфіденційні змінні
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = ['DeepStateUA', 'RVvoenkor', 'sentdefender', 'PpoUaRadar', 'vanek_nikolaev']

# 🧠 Ключові слова, які бот вважає "важливими"
keywords = ['шахед', 'ракета', 'іскандер', 'кінжал', 'дрон', 'бпла', 'х-101', 'загроза', 'повітряна тривога', 'летить', 'ппо']

# 😂 Гумористичні коментарі
jokes = [
    '🚀 Шахедик вилетів — тримай капелюха!',
    '🧠 ППО працює, а ти працюй над собою!',
    '💩 Летить гівно — як завжди по графіку!',
    '🧻 Прилетіла ср...а — тримай туалет!',
    '🪖 Кінжал летить — заховайся в каструлю!',
    '🔥 Ракета на підльоті — не панікуй, гори спокійно!',
    '🫣 Знову? Та скільки можна!',
    '😵 Шахедик прилетів привітати тебе з ранком!',
    '🎯 Надіюсь, сьогодні пролетить мимо.',
    '📡 Локатор сказав — шось летить... а що — фіг його знає.'
]

# ⚙️ Telegram боти
bot = Bot(token=BOT_TOKEN)
client = TelegramClient('session', API_ID, API_HASH)

# 🧹 Фільтрація повідомлення
def is_alerting_text(text):
    text_lower = text.lower()
    return any(word in text_lower for word in keywords)

def clean_text(text):
    lines = text.split('\n')
    clean_lines = [line for line in lines if not line.lower().startswith('підписуйся') and 'telegram' not in line.lower()]
    return '\n'.join(clean_lines)

# 🟢 Обробка повідомлень із каналів
@client.on(events.NewMessage(chats=CHANNELS))
async def handler(event):
    try:
        message = event.message
        text = message.message or ""
        if is_alerting_text(text):
            cleaned = clean_text(text)
            joke = f"<b>{random.choice(jokes)}</b>"
            full_message = f"{joke}\n\n{cleaned}" if cleaned else joke

            # Відправити текст
            await bot.send_message(chat_id='@Shahednykbot', text=full_message, parse_mode=ParseMode.HTML)

            # Відправити фото, якщо є
            if message.media and isinstance(message.media, MessageMediaPhoto):
                file = await message.download_media()
                await bot.send_photo(chat_id='@Shahednykbot', photo=open(file, 'rb'))
                os.remove(file)

    except Exception as e:
        logging.error(f"❌ Помилка при обробці повідомлення: {e}")

# 🔘 Обробник команди /start
async def start(update, context):
    await update.message.reply_text("👋 Я Шахедик-бот. Тисни /situation, якщо хочеш дізнатися, що летить.")

# 🧨 Обробник команди /situation
async def situation(update, context):
    text = random.choice(jokes)
    await update.message.reply_text(f"📡 Поточна ситуація:\n\n<b>{text}</b>", parse_mode=ParseMode.HTML)

# 🔁 Запуск усіх сервісів
async def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("situation", situation))

    # Запуск Telethon
    await client.start()
    await client.connect()
    logging.info("✅ Telethon підʼєднано")

    # Запуск бота
    asyncio.create_task(app.run_polling())
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
