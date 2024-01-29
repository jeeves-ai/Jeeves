import asyncio
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from app_class import MessageProcessor

import redis
import dill as pickle

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class Router:
    redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

    def __init__(self, bot, user_message):
        self.bot = bot
        self.user_message = user_message
        self.is_new = None
        self.old_message = None

    @staticmethod
    def save_processor(user_id, processor):
        processor_data = pickle.dumps(processor)
        Router.redis_client.setex(user_id, 600, processor_data)

    @staticmethod
    def get_processor(user_id):
        processor_data = Router.redis_client.get(user_id)
        if processor_data:
            processor = pickle.loads(processor_data)
            return processor
        return None

    async def process(self):

        template = PromptTemplate.from_template("""system" "Проанализируй сообщение и определи тип сообщения. Верни 
        (false), если сообщение уточняющее. Верни (true), если сообщение полноценное (новое).У тебя 
        есть два типа сообщщений. Первый тип сообщений - это полноценное. Из которой можно получить товар или услугу или
        источник, за которую пользователь получил или заплатил определённую сумму денег, или даже не денег, а произошёл 
        обмен или подарок. Примеры таких самостоятельных сообщений - (Купил что-то за определённую сумму. Продал что-то 
        за определённую сумму. Получил доход за что-то или от кого-то. Потратил на чо-то. Свершил какое-то действие на 
        определённую сумму. Такси за 2000. Заказ на 5к. Приготовил еды на 150 000. Пожрал говна на 200. Погуляли на лям.
        Получил зарплату 800к. Бабушка подарила 100$. Натанцевал на 20 тыщ. Оплатил интернет. Выйграл в казино. Нашёл 
        500 баксов. Украл 800 лямов. И подобные.) Второй тип сообщений - это уточняющие сообщения. Исходя из которого 
        можно поменять в предыдущем сообщение что-либо, например товар, количество, статус (траты или доход), цена за 
        единицу или общую цену или что-то ещё. Обычно в таких уточняющих предложениях есть слова маркеры, такие как 
        (нет, не, помеяй, измени). Но бывают и уточняющие предложения без слов маркеров. Например (5 бутылок). 
        Вот примеры уточняющих сообщений - (Не купил, а продал. Не 15000 а 150000. 8 бутылок. 
        Получил а не потратил. Измени количество на 20. Это общая цена. Цена за единицу товара)."
        'user message - {user_message_text}'""")

        if self.user_message.reply_to_message:
            self.is_new = False
        else:

            prompt = template.format(user_message_text=self.user_message.text)
            llm = ChatOpenAI(
                model_name="gpt-4-1106-preview",
                openai_api_key=OPENAI_API_KEY,
                temperature=0.8,
                verbose=True
            )
            result = llm.predict(prompt)

            if 'true' in result:
                self.is_new = True
            elif 'false' in result:
                self.is_new = False
            else:
                self.is_new = True

        print(f'eto is_new {self.is_new}')

        user_id = self.user_message.from_user.id

        if self.is_new:
            processor = MessageProcessor(self.bot, self.user_message)
        else:
            # processor = MessageProcessor.instances.get(user_id)
            processor = Router.get_processor(user_id)
            if processor is None:
                processor = MessageProcessor(self.bot, self.user_message)
            else:
                self.old_message = processor.full_message
                processor.cancel()
                processor = MessageProcessor(
                    bot=self.bot,
                    user_message=self.old_message,
                    additional_user_message=self.user_message
                )

        # MessageProcessor.instances[user_id] = processor
        Router.save_processor(user_id, processor)
        asyncio.create_task(processor.process())
