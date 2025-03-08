from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from bot.buttuns.inline import send_text, menu, channels, settings, zayafka_change
from models import BotUser, Channels
from models.users import TextZayafka

admin_router = Router()

import re


class ZayafkaText(StatesGroup):
    photo = State()
    text = State()


def Find(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


@admin_router.callback_query(F.data.startswith('settings_stock'))
async def leagues_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.edit_text("Settings", reply_markup=settings())


@admin_router.callback_query(F.data.startswith('settings_'))
async def leagues_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = call.data.split('_')[-1]
    await call.answer()
    if data == 'static':
        users = await BotUser.count()
        channel = await Channels.count()
        await call.message.answer(
            html.bold(f'Admin\nUserlar soni: <b>{users},\nKanallar soni: {channel}</b>'), parse_mode='HTML')
    elif data == 'send':
        await call.message.answer(html.bold("Xabarni yuborish turini tanlang❓"), parse_mode='HTML',
                                  reply_markup=send_text())
    elif data == 'subscribe':
        channels_ = await Channels.all()
        if channels_:
            try:
                await call.message.edit_text(text='Kanallar', reply_markup=await channels(channels_))
            except:
                await call.message.answer(text='Kanallar', reply_markup=await channels(channels_))

        else:
            try:
                await call.message.edit_text(text='Kanallar', reply_markup=await channels(channels_))
            except:
                await call.message.answer(text='Kanallar', reply_markup=await channels(channels_))
    elif data == 'back':
        try:
            await call.message.delete()
        except:
            pass
        await call.message.answer(text=f'Assalomu aleykum Admin {call.from_user.first_name}',
                                  reply_markup=menu(admin=True))
    elif data == 'zayafka':
        zayafka_text = await TextZayafka.get(1)
        if zayafka_text:
            await call.message.answer_photo(photo=zayafka_text.photo, caption=zayafka_text.name,
                                            reply_markup=zayafka_change())
        else:
            await state.set_state(ZayafkaText.photo)
            await call.message.answer('Rasim yuboring')


@admin_router.message(ZayafkaText.photo)
async def leagues_handler(message: Message, bot: Bot, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
        await state.set_state(ZayafkaText.text)
        await message.answer('Text kiriting')
    else:
        await message.answer("Rasim jo'nating")


@admin_router.message(ZayafkaText.text)
async def leagues_handler(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    zayafka_text = await TextZayafka.get(1)
    if message.photo:
        try:
            if zayafka_text:
                await TextZayafka.update(1, photo=data.get('photo'), text=message.text)
                await message.answer("Muvoffaqyatli o'zgardi!✅")
                await message.answer_photo(photo=data.get('photo'), caption=message.text, reply_markup=zayafka_change())
            else:
                text = await TextZayafka.create(photo=data.get('photo'), text=message.text)
                await message.answer("Muvoffaqyatli saqlandi!✅")
                await message.answer_photo(photo=text.photo, caption=text.name, reply_markup=zayafka_change())
        except:
            await message.answer("Saqlashda xatolik!❌")
            await message.answer("Settings", reply_markup=settings())

    else:
        await message.answer("Rasim jo'nating⚡")


@admin_router.callback_query(F.data.startswith('zayafka_'))
async def leagues_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = call.data.split('_')[-1]
    if data == 'change':
        await state.set_state(ZayafkaText.photo)
        await call.message.answer("Rasim kiriting")
    else:
        await call.message.answer("Settings", reply_markup=settings())
