import asyncio
import os
import telebot.async_telebot
from dotenv import load_dotenv
from app_class import SendWelcome
from routerV2 import Router

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.async_telebot.AsyncTeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    commands_handler = SendWelcome(bot)
    await commands_handler.send_welcome(message)


@bot.message_handler(commands=['report'])
async def send_record(message):
    user_id = message.from_user.id
    record_link = f"http://localhost:8000/record/{user_id}"
    await bot.reply_to(message, f"Вы можете просмотреть свои финансовые записи [здесь]({record_link}).")


@bot.message_handler(content_types=["text"])
async def handle_text(message: telebot.types.Message):
    router = Router(bot=bot, user_message=message)
    print(f'ETO MESSAGE V BOTE {message.text}')
    asyncio.create_task(router.process())


asyncio.run(bot.polling())
