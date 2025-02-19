import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand

from bot.handlers.admin import admin_router
from bot.handlers.start import start_router
from bot.language import language_router
from dispatcher import bot
from models import db


async def on_start(bot: Bot):
    commands_admin = [
        BotCommand(command='start', description="Bo'tni ishga tushirish")
    ]
    await bot.set_my_commands(commands=commands_admin)
    await db.create_all()


async def on_shutdown(bot: Bot):
    await bot.delete_my_commands()


# async def handle_chat_join_request(update: Update, bot: Bot):
#     """Обработчик входящих заявок в канал"""
#     if not update.chat_join_request:
#         return  # Если это не заявка на вступление, выходим
#
#     chat_join: ChatJoinRequest = update.chat_join_request
#     channel = await Channels.get(chat_join.chat.id)  # Получаем канал из БД
#     text: TextInSend = await TextInSend.get(1)  # Получаем текст из БД
#
#     if channel and channel.status:
#         if text:
#             await bot.send_message(
#                 chat_id=chat_join.from_user.id,
#                 text=text.text,
#                 reply_markup=link(text.link)
#             )
#         else:
#             await bot.send_message(chat_id=chat_join.from_user.id, text="Xush kelibsiz!")
#
#         await chat_join.approve()


async def main():
    dp = Dispatcher()
    dp.include_routers(start_router, language_router, admin_router)
    dp.startup.register(on_start)
    dp.shutdown.register(on_shutdown)
    # dp.update.middleware(handle_chat_join_request)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

# 1065  docker login
# 1068  docker build -t nickname/name .
# 1071  docker push nickname/name

# docker run --name db_mysql -e MYSQL_ROOT_PASSWORD=1 -d mysql
