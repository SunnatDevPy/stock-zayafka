from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatJoinRequest

from bot.buttuns.inline import language_inl, links_zayafka
from models import Channels

start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    data = await state.get_data()
    locale = data.get('locale')
    if locale == 'rus':
        til = "Выберите язык"
    else:
        til = 'Til tanlang'
    await message.answer(til, reply_markup=language_inl())


@start_router.chat_join_request()
async def zayafka(chat_join: ChatJoinRequest, bot: Bot):
    channel: Channels = await Channels.get_chat(chat_join.chat.id)
    if channel:
        if channel.status:
            if channel.text:
                await chat_join.approve()
                buttons = channel.buttons or []

                if channel.photo:
                    await bot.send_photo(chat_id=chat_join.from_user.id, photo=channel.photo,
                                         caption=channel.text, reply_markup=links_zayafka(buttons))
                elif channel.video:
                    await bot.send_video(chat_id=chat_join.from_user.id, video=channel.video,
                                         caption=channel.text, reply_markup=links_zayafka(buttons))
                else:
                    await bot.send_message(chat_id=chat_join.from_user.id, text=channel.text,
                                           reply_markup=links_zayafka(buttons))
            else:
                await bot.send_message(chat_id=chat_join.from_user.id, text='Xush kelibsiz')
    # else:
    #     await bot.send_message(chat_id=chat_join.from_user.id, text="Xatolik yuz berdi")
