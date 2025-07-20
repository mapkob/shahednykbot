import logging
import asyncio
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from telethon.tl.functions.messages import GetHistoryRequest
import nest_asyncio

nest_asyncio.apply()

# Дані для Telegram API
api_id = 26549615
api_hash = 'f43d6245868e5bae41c40872fb873dec'
bot_token = '7395027911:AAGkiRcvxs8hP878uv9nvo5mGwDe39loxFg'
target_chat_id = None  # буде встановлено під час /start

# Канали для перевірки
channels = [
    'https://t.me/DeepStateUA',
    'https://t.me/RVvoenkor',
    'https://t.me/sentdefender',
    'https://t.me/PpoUaRadar',
    'https://t.me/vanek_nikolaev'
]

# Ключові слова для фільтрації
keywords = ['шахед', 'шахеди', 'Shahed', 'Shaheds', 'дрон', 'ракета', 'ракети', 'прильот', 'тривога', 'повітряна', 'вибух', 'київ', 'карта', 'іскандер', 'кінжал', 'x-101', 'x101']

# Гумористичні фрази
jokes = [
    '🧻 Гуркотять погані шахедики!',
    '🔥 Горєшнік говнєшнік знову активізувався!',
    '🛑 Геть смерть і воші!',
    '💩 Іскандери на горизонті — тримай труси!',
    '☠️ Нехай Бог охороняє всіх людей!',
    '🧠 Ракетна дурня знову в ефірі!',
    '🚽 Увімкни VPN і молись!',
    '😂 Смійся, бо ліпше вже не стане!',
    '🌪️ Смерчі дурні — але ми не дурні!'
]

# Налаштування логів
logging.basicConfig(level=logging.INFO)

# Ініціалізація Telethon-клієнта
telethon_client = TelegramClient('anon', api_id, api_hash)


async def fetch_and_send_messages(bot: Bot):
    await telethon_client.start()
    for url in channels:
        channel = url.split('/')[-1]
        try:
            entity = await telethon_client.get_entity(channel)
            history = await telethon_client(GetHistoryRequest(
                peer=entity,
                limit=5,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            for msg in reversed(history.messages):
                text = msg.message.lower() if hasattr(msg, 'message') and msg.message else ''
                if any(kw in text for kw in keywords):
                    caption = f"<b>📡 {channel}:</b>\n{text[:800]}"
                    joke = f"\n\n<b>{jokes[hash(text) % len(jokes)]}</b>"

                    if target_chat_id:
                        if msg.media and isinstance(msg.media, MessageMediaPhoto):
                            photo = await telethon_client.download_media(msg.media)
                            with open(photo, 'rb') as photo_file:
                                await bot.send_photo(chat_id=target_chat_id, photo=photo_file)
                        await bot.send_message(chat_id=target_chat_id, text=caption + joke, parse_mode=ParseMode.HTML)

        except Exception as e:
            print(f'Помилка з каналом {channel}: {e}')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global target_chat_id
    target_chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=target_chat_id, text="✅ Шахедик увімкнено. Очікуй свіжі жарти та дрони.")
    while True:
        await fetch_and_send_messages(context.bot)
        await asyncio.sleep(60)


def main():
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == '__main__':
    main()

