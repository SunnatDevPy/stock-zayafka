from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.buttuns.inline import send_text, menu, channels, settings
from models import BotUser, Channels

admin_router = Router()

import re


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
        await call.message.answer(text='Bosh menu', reply_markup=menu(admin=True))
