from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.buttuns.inline import language_inl

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
