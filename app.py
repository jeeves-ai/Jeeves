import asyncio

import telebot.async_telebot
import os
from dotenv import load_dotenv
from app_class import SendWelcome, HandleText, SendJson
#from report_generator import PDFGenerator

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.async_telebot.AsyncTeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    commands_handler = SendWelcome(bot)
    commands_handler.send_welcome(message)


@bot.message_handler(commands=['report'])
async def send_record(message):
    user_id = message.from_user.id
    record_link = f"http://localhost:8000/record/{user_id}"
    await bot.reply_to(message, f"Вы можете просмотреть свои финансовые записи [здесь]({record_link}).")


@bot.message_handler(content_types=["text"])
async def handle_text(message: telebot.types.Message):
    commands_handler = HandleText(bot) 
    await commands_handler.handle_text(message)


asyncio.run(bot.polling())

