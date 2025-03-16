import asyncio
import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.buttuns.inline import settings, send_text_type, link_from_channel
from models import BotUser, Channels

bot_anons_router = Router()


def Find(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


class SendTextState(StatesGroup):
    text = State()
    video = State()
    link = State()
    confirm = State()


async def send_message_to_users(bot, users, call, photo, text, markup):
    tasks = []
    good = 0
    block = 0

    for user in users:
        tasks.append(send_individual_message(bot, user.id, photo, text, markup))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            block += 1
        else:
            good += 1

    await call.message.answer(f"📊 Xabar yuborish statistikasi:\n✅ Qabul qildi: {good}, 🚫 Block qilganlar: {block}")
    print(block, good)


async def send_individual_message(bot, chat_id, photo, text, markup):
    await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=markup)
    return True


@bot_anons_router.callback_query(F.data.startswith('send_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')[-1]
    await call.answer()
    if data == 'user':
        await call.message.edit_text("Userlar uchun xabar yuborish usulini tanlang",
                                     reply_markup=send_text_type('user'))
    if data == 'channel':
        await call.message.edit_text("Kanallar uchun xabar yuborish usulini tanlang",
                                     reply_markup=send_text_type('channel'))
    if data == 'back':
        await state.clear()
        await call.message.edit_text("Settings", reply_markup=settings())


@bot_anons_router.callback_query(F.data.startswith('types_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    await call.answer()
    await state.set_state(SendTextState.text)
    if data[1] == 'forward':
        await call.message.answer("Tayyor xabarni yuboring")
        await state.update_data(send_text=data[-1], status=data[1])
    if data[1] == 'create':
        await call.message.answer("Rasim, Video xabar kiriting")
        await state.update_data(send_text=data[-1], status=data[1])
    if data == 'back':
        await state.clear()
        await call.message.edit_text("Settings", reply_markup=settings())


@bot_anons_router.message(SendTextState.text)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data.get('status') == 'forward':
        text = message.text or message.caption
        reply_markup = message.reply_markup
        await state.set_state(SendTextState.confirm)
        buttons = reply_markup.inline_keyboard if reply_markup and isinstance(reply_markup,
                                                                              InlineKeyboardMarkup) else []
        await state.update_data(text=text, buttons=buttons, media=message.photo[
            -1].file_id if message.photo else message.video.file_id if message.video else None)

        buttons.append([
            InlineKeyboardButton(text="✅ Jo'natish", callback_data="channels_send"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="channels_cancel"),
        ])

        new_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        if message.photo:
            await message.answer_photo(photo=message.photo[-1].file_id, caption=text, reply_markup=new_markup)
        elif message.video:
            await message.answer_video(video=message.video.file_id, caption=text, reply_markup=new_markup)
        else:
            await message.answer(text=text, reply_markup=new_markup)

    else:
        if message.photo:
            await state.set_state(SendTextState.video)
            await state.update_data(photo=message.photo[-1].file_id)
            await message.answer('Text xabarni kiriting')
        elif message.video:
            await state.set_state(SendTextState.video)
            await state.update_data(video=message.video.file_id)
            await message.answer('Text xabarni kiriting')
        elif message.text:
            await state.set_state(SendTextState.link)
            await state.update_data(text=message.text)
            await message.answer("Link jo'nating")


@bot_anons_router.callback_query(SendTextState.confirm)
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    photo = data.get("media")
    text = data.get("text")
    buttons = data.get("buttons", [])
    await call.message.delete()
    markup = InlineKeyboardMarkup(inline_keyboard=buttons[:-1]) if buttons else None

    calls = call.data.split('_')[-1]
    if calls == 'send':
        send_text = data.get('send_text')

        await call.message.answer("✅ Ozgina kuting ⌛!")

        if send_text == 'user':
            users = await BotUser.all()
        else:
            users = await Channels.all()

        await send_message_to_users(bot, users, call, photo, text, markup)
        await call.message.answer("Settings", reply_markup=settings())

    else:
        await call.message.delete()
        await call.message.answer("❌ Xabar yuborish rad etildi.")
        await call.message.answer("Settings", reply_markup=settings())
    await state.clear()


@bot_anons_router.message(SendTextState.text)
async def leagues_handler(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(SendTextState.link)
    await message.answer(
        "Knopka va linkni (<b> Knopka - link </b>) formatda yuboring yoki <b>'✅ Tugatish'</b> tugmani bosing.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ Tugatish", callback_data="finish")]]
        ))


@bot_anons_router.message(SendTextState.link)
async def leagues_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    links = data.get("links", [])

    if " - " in message.text:
        btn_text, btn_url = message.text.split(" - ", maxsplit=1)

        if Find(message.text):
            links.append((btn_text.strip(), btn_url.strip()))
            await state.update_data(links=links)

            await message.answer(
                f"✅ Link qo'shildi! -> {btn_text} - {btn_url.strip()} .\nYana qo'shing yoki <b>'✅ Tugatish'</b>  tugmani bosing",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="✅ Tugatish", callback_data="finish_")]]
                ))
        else:
            await message.answer("Link notog'ri formatda")
    else:
        await message.answer("❌ Format notog'ri. Knopka va linkni (<b> Knopka - link </b>) formatda yuboring.")


@bot_anons_router.callback_query(lambda c: c.data == "finish_")
async def finish_sending(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    photo = data.get("photo")
    text = data.get("text")
    links = data.get("links", [])
    send_text = data.get('send_text')
    block = 0
    good = 0
    if send_text == 'user':
        users: list[BotUser] = await BotUser.all()
        for i in users:
            try:
                await bot.send_photo(i.id, photo=photo, caption=text, reply_markup=link_from_channel(links))
                good += 1
            except Exception as e:
                block += 1
        else:
            await callback.message.answer(
                f"Xabar yuborish statistikasi\n Qabul qildi: {good},\nBlock qilgandlar: {block}")
            try:
                await callback.message.edit_text("Settings", reply_markup=settings())
            except:
                await callback.message.answer("Settings", reply_markup=settings())
    else:
        users: list[Channels] = await Channels.all()
        for i in users:
            try:
                await bot.send_photo(i.chat_id, photo=photo, caption=text, reply_markup=link_from_channel(links))
                good += 1
            except Exception as e:
                block += 1
        else:
            await callback.message.answer(
                f"Xabar yuborish statistikasi\n Qabul qildi: {good},\nBlock qilgandlar: {block}")
            try:
                await callback.message.edit_text("Settings", reply_markup=settings())
            except:
                await callback.message.answer("Settings", reply_markup=settings())
    await state.clear()


@bot_anons_router.callback_query(F.data.startswith('message_'))
async def send_to_channel(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    call = callback_query.data.split('_')[-1]
    if call == 'send':
        data = await state.get_data()
        channel_id = data.get("channel_id")  # Получаем ID канала
        text = data.get("text")
        media = data.get("media")
        buttons = data.get("buttons")

        markup = InlineKeyboardMarkup(
            inline_keyboard=buttons[:-1]) if buttons else None  # Убираем кнопки "Отправить" и "Отменить"

        if media:
            if callback_query.message.photo:
                await bot.send_photo(chat_id=channel_id, photo=media, caption=text, reply_markup=markup)
            elif callback_query.message.video:
                await bot.send_video(chat_id=channel_id, video=media, caption=text, reply_markup=markup)
        else:
            await bot.send_message(chat_id=channel_id, text=text, reply_markup=markup)
        channel = await Channels.get(int(channel_id))
        await callback_query.message.answer(f"📢 Xabar kanalga yuborildi: <b>{channel.name}</b> ✅!", parse_mode='html')
    else:
        await callback_query.message.delete()
        await callback_query.message.answer("❌ Xabar yuborish rad etildi.")
        await callback_query.message.answer("Settings", reply_markup=settings())
    await state.clear()
