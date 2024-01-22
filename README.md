import asyncio
import os
import telebot.async_telebot
from dotenv import load_dotenv
from app_class import SendWelcome
from routerV2 import Router
from pdf_generator import PDFGenerator


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
    record_link = f"http://64.226.65.160:8000/record/{user_id}"
    await bot.reply_to(message, f"Вы можете просмотреть свои финансовые записи [здесь]({record_link}).")


@bot.message_handler(commands=['pdf'])
async def send_report(message):
    user_id = message.from_user.id
    pdf_generator = PDFGenerator()
    pdf_filename = pdf_generator.generate_pdf_report(user_id)

    if pdf_filename:
        with open(pdf_filename, "rb") as pdf_file:
            await bot.send_document(message.chat.id, pdf_file, caption="Financial Report")
        os.remove(pdf_filename)
    else:
        await bot.reply_to(message, "Unable to generate the report.")


@bot.message_handler(content_types=["text"])
async def handle_text(message: telebot.types.Message):
    router = Router(bot=bot, user_message=message)
    print(f'ETO MESSAGE V BOTE {message.text}')
    asyncio.create_task(router.process())


asyncio.run(bot.polling())
