from aiogram import Bot, F, Router, html
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

from bot.buttuns.inline import send_text, confirm_inl, menu, channels, link, settings, link_from_channel, \
    detail_channel, send_message_button, detail_message_channel, links_zayafka
from models import BotUser, Channels

admin_router = Router()

import re


def Find(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


class SendTextState(StatesGroup):
    text = State()
    video = State()
    link = State()
    confirm = State()


class AddTextSend(StatesGroup):
    text = State()
    link = State()


class ChangeTextSend(StatesGroup):
    text = State()


class SendTextChannel(StatesGroup):
    photo = State()
    text = State()
    link = State()


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
        await call.message.answer(html.bold("Xabarni qaysi usulda jo'natmoqchisiz❓"), parse_mode='HTML',
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


@admin_router.callback_query(F.data.startswith('send_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')[-1]
    await call.answer()
    await state.set_state(SendTextState.text)
    if data == 'text':
        await call.message.answer('Text xabarni kiriting')
    if data == 'video':
        await call.message.answer("Rasm yoki videoni kiriting")
    if data == 'back':
        await state.clear()
        await call.message.edit_text("Settings", reply_markup=settings())


@admin_router.message(SendTextState.text)
async def leagues_handler(msg: Message, state: FSMContext):
    if msg.photo:
        await state.set_state(SendTextState.video)
        await state.update_data(photo=msg.photo[-1].file_id)
        await msg.answer('Text xabarni kiriting')
    elif msg.video:
        await state.set_state(SendTextState.video)
        await state.update_data(video=msg.video.file_id)
        await msg.answer('Text xabarni kiriting')
    elif msg.text:
        await state.set_state(SendTextState.link)
        await state.update_data(text=msg.text)
        await msg.answer("Link jo'nating")


@admin_router.message(SendTextState.video)
async def leagues_handler(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    await state.set_state(SendTextState.link)
    await msg.answer("Link jo'nating")


@admin_router.message(SendTextState.link)
async def leagues_handler(msg: Message, state: FSMContext):
    await state.update_data(link=msg.text)
    data = await state.get_data()
    if len(data) == 2:
        await msg.answer(data['text'] + f'\n\n{data["link"]}', reply_markup=confirm_inl())
    else:
        if data.get('photo'):
            await msg.answer_photo(data['photo'], data['text'] + f'\n\n{data["link"]}', parse_mode='HTML',
                                   reply_markup=confirm_inl())
        else:
            await msg.answer_video(video=data['video'], caption=data['text'] + f'\n\n{data["link"]}', parse_mode='HTML',
                                   reply_markup=confirm_inl())


@admin_router.callback_query(F.data.endswith("_network"))
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split('_')
    res = await state.get_data()
    print(res)
    await call.answer()
    users: list[BotUser] = await BotUser.all()
    if data[0] == 'confirm':
        send = 0
        block = 0
        if len(res) == 2:
            for i in users:
                try:
                    await bot.send_message(i.id, res['text'], parse_mode='HTML', reply_markup=link(res['link']))
                    send += 1
                except:
                    block += 1
        else:
            if res.get('photo'):
                for i in users:
                    try:
                        await bot.send_photo(chat_id=i.id, photo=res['photo'], caption=res['text'], parse_mode='HTML',
                                             reply_markup=link(res['link']))
                        send += 1
                    except:
                        block += 1
            elif res.get('video'):
                for i in users:
                    try:
                        await bot.send_video(chat_id=i.id, video=res['video'], caption=res['text'], parse_mode='HTML',
                                             reply_markup=link(res['link']))
                        send += 1
                    except:
                        block += 1
        await call.message.answer(f'Yuborildi: {send}\nBlockda: {block}')

    elif data[0] == 'cancel':
        await call.message.delete()
        await call.message.answer("Protsess to'xtatildi")
    await state.clear()


admin_1 = 5649321700
admin_2 = 1353080275


@admin_router.my_chat_member()
async def on_bot_added_to_channel(update: ChatMemberUpdated, bot: Bot):
    if update.chat.type == "channel":
        new_status = update.new_chat_member.status
        old_status = update.old_chat_member.status

        if new_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] and old_status != new_status:
            channel = await Channels.get(update.chat.id)
            if channel is None:
                await Channels.create(chat_id=update.chat.id, name=update.chat.title, status=True)
                channels_ = await Channels.all()
                await bot.send_message(
                    admin_1,
                    f"✅ Bot kanalga qo'shildi: {update.chat.title} (Kanal ID: {update.chat.id})"
                )
                await bot.send_message(
                    admin_2,
                    f"✅ Bot kanalga qo'shildi: {update.chat.title} (Kanal ID: {update.chat.id})"
                )
                await bot.send_message(admin_1, text='Kanallar', reply_markup=await channels(channels_))
                await bot.send_message(admin_2, text='Kanallar', reply_markup=await channels(channels_))


# ========== Kanallar bilan ishlash
# ==========
# ==========
class ZayafkaState(StatesGroup):
    photo = State()
    text = State()
    link = State()


@admin_router.callback_query(F.data.startswith('channels_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    await state.update_data(channel_id=data[-1])
    if data[1] == 'back':
        await call.message.edit_text("Settings", reply_markup=settings())
    if data[1] == 'info':
        channel = await Channels.get_chat(chat_id=int(data[-1]))
        await call.message.edit_text(text=f'Detail: {channel.name}', reply_markup=await detail_channel(data[-1]))
    if data[1] == 'change':
        channel = await Channels.get(int(data[-1]))
        if channel.status:
            status = False
        else:
            status = True
        await Channels.update(int(data[-1]), status=status)
        try:
            await call.message.edit_text(text=f'Detail: {channel.name}', reply_markup=await detail_channel(data[-1]))
        except:
            await call.message.edit_reply_markup(inline_message_id=call.inline_message_id,
                                                 reply_markup=await detail_channel(data[-1]))
    if data[1] == 'send':
        await call.message.edit_text(text=f'Kanalga {data[-1]} xabar yuborish turini tanlang',
                                     reply_markup=await send_message_button())
    if data[1] == 'zayafka':
        channel: Channels = await Channels.get_chat(int(data[-1]))
        await state.update_data(channel_id=channel.id)
        await call.message.delete()
        if channel.text:
            await call.message.answer_photo(photo=channel.photo, caption=channel.text,
                                            reply_markup=detail_message_channel(channel.chat_id, channel.link))
        else:
            await state.set_state(ZayafkaState.photo)
            await call.message.answer(text="Tayyor malumotni jo'nating")
    if data[1] == 'delete':
        await call.message.delete()
        await Channels.delete(int(data[-1]))
        channels_ = await Channels.all()
        await call.message.edit_text(text='Kanallar', reply_markup=await channels(channels_))


@admin_router.message(ZayafkaState.photo)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if not message.forward_from and not message.forward_from_chat:
        await message.answer("⚠️ Tayyor xabarni yuboring.")
        return

    text = message.text or message.caption
    photo = message.photo[-1].file_id if message.photo else None
    video = message.video.file_id if message.video else None

    if message.reply_markup and isinstance(message.reply_markup, InlineKeyboardMarkup):
        buttons = [[{"text": btn.text, "url": btn.url}] for btn in sum(message.reply_markup.inline_keyboard, [])]
    else:
        buttons = None
    await Channels.update(int(data.get('channel_id')), photo=photo, video=video, text=text, buttons=buttons)
    await message.answer("✅ Xabar saqlandi!")
    channel = await Channels.get(int(data.get('channel_id')))
    buttons = channel.buttons or []

    if channel.photo:
        await bot.send_photo(chat_id=channel.chat_id, photo=channel.photo,
                             caption=channel.text, reply_markup=links_zayafka(buttons))
    elif channel.video:
        await bot.send_video(chat_id=channel.chat_id, video=channel.video,
                             caption=channel.text, reply_markup=links_zayafka(buttons))
    else:
        await bot.send_message(chat_id=channel.chat_id, text=channel.text,
                               reply_markup=links_zayafka(buttons))
    await message.answer("Settings", reply_markup=settings())

    await state.clear()


# @admin_router.message(ZayafkaState.text)
# async def leagues_handler(message: Message, state: FSMContext):
#     await state.set_state(ZayafkaState.link)
#     await state.update_data(text=message.text)
#     await message.answer(text="Link yuboring")
#
#
# @admin_router.message(ZayafkaState.link)
# async def leagues_handler(message: Message, state: FSMContext):
#     data = await state.get_data()
#     channel: Channels = await Channels.get_chat(int(data.get('channel_id')))
#     if Find(message.text):
#         await Channels.update(channel.id, link=message.text, photo=data.get('photo'), text=data.get('text'))
#         await state.clear()
#         await message.answer_photo(photo=data.get('photo'), caption=data.get('text'),
#                                    reply_markup=detail_message_channel(data.get('channel_id'),
#                                                                        url=message.text))
#     else:
#         await message.answer(text="Link notog'ri formatda")


class ForwardState(StatesGroup):
    text = State()


@admin_router.callback_query(F.data.startswith('type_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')[-1]
    if data == 'forward':
        await state.set_state(ForwardState.text)
        await call.message.answer(text=f'Tayyor xabarni kiriting')
    if data == 'send':
        await state.set_state(SendTextChannel.photo)
        await call.message.answer(text=f'Kanalga xabar yuborish uchun 🌆Rasim kiriting')
    if data == 'back':
        try:
            await call.message.edit_text("Settings", reply_markup=settings())
        except:
            await call.message.delete()
            await call.message.edit_text("Settings", reply_markup=settings())
    if data == 'change':
        pass


@admin_router.message(ForwardState.text)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if not message.forward_from and not message.forward_from_chat:
        await message.answer("⚠️ Tayyor xabarni yuboring.")
        return

    text = message.text or message.caption
    reply_markup = message.reply_markup

    if reply_markup and isinstance(reply_markup, InlineKeyboardMarkup):
        buttons = reply_markup.inline_keyboard
    else:
        buttons = []

    markup = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

    try:
        # Если в пересланном сообщении есть фото
        if message.photo:
            await bot.send_photo(
                chat_id=data.get('channel_id'),
                photo=message.photo[-1].file_id,
                caption=text,
                reply_markup=markup
            )
        # Если есть видео
        elif message.video:
            await bot.send_video(
                chat_id=data.get('channel_id'),
                video=message.video.file_id,
                caption=text,
                reply_markup=markup
            )
        # Если есть документ (PDF, DOCX и т. д.)
        elif message.document:
            await bot.send_document(
                chat_id=data.get('channel_id'),
                document=message.document.file_id,
                caption=text,
                reply_markup=markup
            )
        # Если просто текстовое сообщение
        elif text:
            await bot.send_message(
                chat_id=data.get('channel_id'),
                text=text,
                reply_markup=markup
            )
        else:
            await message.answer("⚠️ Bu turdagi xabarni bot yuborolmaydi.")
            try:
                await message.edit_text("Settings", reply_markup=settings())
            except:
                await message.answer("Settings", reply_markup=settings())
            return

        await message.answer("✅ Xabar kanalga yuborildi!")
        try:
            await message.edit_text("Settings", reply_markup=settings())
        except:
            await message.answer("Settings", reply_markup=settings())

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

    await state.clear()


@admin_router.message(SendTextChannel.photo)
async def leagues_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id, links=[])  # Добавляем список ссылок
        await state.set_state(SendTextChannel.text)
        await message.answer("Tekst kiriting")
    else:
        await message.answer("Rasim yuboring")


@admin_router.message(SendTextChannel.text)
async def leagues_handler(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(SendTextChannel.link)
    await message.answer(
        "Knopka va linkni (<b> Knopka - link </b>) formatda yuboring yoki <b>'✅ Tugatish'</b> tugmani bosing.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ Tugatish", callback_data="finish")]]
        ))


@admin_router.message(SendTextChannel.link)
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


@admin_router.callback_query(lambda c: c.data == "finish")
async def finish_sending(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    photo = data.get("photo")
    text = data.get("text")
    links = data.get("links", [])
    channel_id = data.get("channel_id")

    try:
        await bot.send_photo(channel_id, photo=photo, caption=text, reply_markup=link_from_channel(links))
        await callback.message.answer("📢 Kanalga xabar yuborildi!")
        await callback.message.answer("Settings", reply_markup=settings())
    except:
        await callback.message.answer("❌ Yuborishda xatolik, tekshirib ko'ring admin qilganmisiz kanalga.")

    await state.clear()
