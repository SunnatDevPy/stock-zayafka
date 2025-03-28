import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, InlineKeyboardButton

from bot.buttuns.inline import settings, detail_channel, send_message_button, detail_message_channel, channels, \
    link_from_channel
from models import Channels
from models.users import Buttons

channel_router = Router()


def Find(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


class ForwardState(StatesGroup):
    text = State()
    confirm = State()


class ZayafkaState(StatesGroup):
    text = State()


class SendTextChannelState(StatesGroup):
    media = State()
    text = State()
    link = State()
    confirm = State()


@channel_router.callback_query(F.data.startswith('channels_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    await state.update_data(channel_id=data[-1])
    channel = await Channels.get(int(data[2]))
    if data[1] == 'back':
        await call.message.edit_text("Settings", reply_markup=settings())
    if data[1] == 'info':
        await call.message.edit_text(text=f'Detail: {channel.name}. id: {channel.id}, chat_id: {channel.chat_id}',
                                     reply_markup=await detail_channel(data[2]))
    if data[1] == 'change':
        if channel.status:
            status = False
        else:
            status = True
        await Channels.update(int(data[2]), status=status)
        try:
            await call.message.edit_text(text=f'Detail: {channel.name}', reply_markup=await detail_channel(data[2]))
        except:
            await call.message.edit_reply_markup(inline_message_id=call.inline_message_id,
                                                 reply_markup=await detail_channel(data[2]))
    if data[1] == 'send':
        await call.message.edit_text(text=f'Kanalga {data[-1]} xabar yuborish turini tanlang',
                                     reply_markup=await send_message_button())
    if data[1] == 'zayafka':
        channel: Channels = await Channels.get(int(data[2]))
        await state.update_data(channel_id=channel.id)
        await call.message.delete()
        if channel.text:
            try:
                await call.message.answer_photo(photo=channel.photo, caption=channel.text,
                                                reply_markup=await detail_message_channel(channel.id))
            except:
                await call.message.answer(text=channel.text, reply_markup=await detail_message_channel(channel.id))
        else:
            await state.set_state(ZayafkaState.text)
            await call.message.answer(text="Tayyor malumotni jo'nating")
    if data[1] == 'delete':
        await call.message.delete()
        await Channels.delete(int(data[2]))
        channels_ = await Channels.all()
        try:
            await call.message.edit_text(text='Kanallar', reply_markup=await channels(channels_))
        except:
            await call.message.answer(text='Kanallar', reply_markup=await channels(channels_))


@channel_router.callback_query(F.data.startswith('type_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')[1]
    if data == 'forward':
        await state.set_state(ForwardState.text)
        await call.message.answer(text=f'Tayyor xabarni kiriting')
    if data == 'send':
        await state.set_state(SendTextChannelState.media)
        await call.message.answer(text=f'Kanalga xabar yuborish uchun media kiriting')
    if data == 'back':
        try:
            await call.message.edit_text("Settings", reply_markup=settings())
        except:
            await call.message.delete()
            await call.message.answer("Settings", reply_markup=settings())
    if data == 'change':
        await call.message.delete()
        await state.set_state(ZayafkaState.text)
        await call.message.answer(text="Tayyor malumotni jo'nating")


@channel_router.message(ZayafkaState.text)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    channel: Channels = await Channels.get(int(data.get('channel_id')))

    text = message.text or message.caption
    reply_markup = message.reply_markup
    photo = message.photo[-1].file_id if message.photo else None
    await Channels.update(channel.id, text=text, photo=photo)
    buttons = await Buttons.get_chat(channel.chat_id)
    for i in buttons:
        await Buttons.delete(i.id)

    if reply_markup and isinstance(reply_markup, InlineKeyboardMarkup):
        for row in reply_markup.inline_keyboard:
            for button in row:
                if button.url:
                    await Buttons.create(channel_id=channel.id, name=button.text, link=button.url)
    await message.answer_photo(photo=channel.photo, caption=channel.text,
                               reply_markup=await detail_message_channel(channel.id))
    await state.clear()


@channel_router.message(ForwardState.text)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    text = message.text or message.caption
    reply_markup = message.reply_markup

    buttons = reply_markup.inline_keyboard if reply_markup and isinstance(reply_markup, InlineKeyboardMarkup) else []

    buttons.append([
        InlineKeyboardButton(text="✅ Jo'natish", callback_data="message_send"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="message_cancel"),
    ])

    new_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.update_data(text=text, buttons=buttons, media=message.photo[
        -1].file_id if message.photo else message.video.file_id if message.video else None)

    if message.photo:
        await message.answer_photo(photo=message.photo[-1].file_id, caption=text, reply_markup=new_markup)
    elif message.video:
        await message.answer_video(video=message.video.file_id, caption=text, reply_markup=new_markup)
    else:
        await message.answer(text=text, reply_markup=new_markup)

    await state.clear()


@channel_router.message(SendTextChannelState.media)
async def leagues_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id, links=[])  # Добавляем список ссылок
        await state.set_state(SendTextChannelState.text)
        await message.answer("Tekst kiriting")
    else:
        await message.answer("Rasim yuboring")


@channel_router.callback_query(F.data.startswith('message_'))
async def send_to_channel(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    call = callback_query.data.split('_')[-1]
    if call == 'send':
        data = await state.get_data()
        channel_id = data.get("channel_id")  # Получаем ID канала
        text = data.get("text")
        media = data.get("media")
        buttons = data.get("buttons")

        markup = InlineKeyboardMarkup(
            inline_keyboard=buttons[:-1]) if buttons else None

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


@channel_router.message(SendTextChannelState.text)
async def leagues_handler(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(SendTextChannelState.link)
    await message.answer(
        "Knopka va linkni (<b> Knopka - link </b>) formatda yuboring yoki <b>'✅ Tugatish'</b> tugmani bosing.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ Tugatish", callback_data="finish")]]
        ))


@channel_router.message(SendTextChannelState.link)
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
                    inline_keyboard=[[InlineKeyboardButton(text="✅ Tugatish", callback_data="finish")]]
                ))
        else:
            await message.answer("Link notog'ri formatda")
    else:
        await message.answer("❌ Format notog'ri. Knopka va linkni (<b> Knopka - link </b>) formatda yuboring.")


@channel_router.callback_query(lambda c: c.data == "finish")
async def finish_sending(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    photo = data.get("photo")
    text = data.get("text")
    links = data.get("links", [])
    channel_id = data.get("channel_id")
    channel = await Channels.get(int(channel_id))
    await callback.message.delete()
    try:
        await bot.send_photo(channel_id, photo=photo, caption=text, reply_markup=link_from_channel(links))
        await callback.message.answer(f"📢 Kanalga xabar yuborildi: <b>{channel.name}</b>!", parse_mode='html')
        await callback.message.answer("Settings", reply_markup=settings())
    except:
        await callback.message.answer("❌ Yuborishda xatolik, tekshirib ko'ring admin qilganmisiz kanalga.")
        await callback.message.answer("Settings", reply_markup=settings())
    await state.clear()
