from aiogram import Bot, F, Router, html
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

from bot.buttuns.inline import send_text, confirm_inl, menu, channels, link, settings, text_add
from models import BotUser, Channels, TextInSend

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
    elif data == 'text':
        text: TextInSend = await TextInSend.get(1)
        if text:
            await call.message.edit_text(text=f"{text.text}\n\n{text.link}", reply_markup=text_add())
        else:
            await call.message.edit_text(text="Text qo'shilmagan", reply_markup=text_add(status=True))
    elif data == 'subscribe':
        channels_ = await Channels.all()
        if channels_:
            await call.message.edit_text(text='Kanallar', reply_markup=await channels(channels_))
        else:
            await call.message.edit_text(text="Kanallarga bot qo'shilmagan", reply_markup=await channels(channels_))
    elif data == 'back':
        await call.message.answer(text='Bosh menu', reply_markup=menu(admin=True))


@admin_router.callback_query(F.data.startswith('channels_'))
async def leagues_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = call.data.split('_')
    if data[1] == 'back':
        await call.message.edit_text("Settings", reply_markup=settings())
    if data[1] == 'send':
        await call.message.delete()
        await state.update_data(channel_id=data[-1])
        await state.set_state(SendTextChannel.photo)
        await call.message.answer(text=f'Kanalga {data[-1]} xabar yuborish uchun rasim kiriting')


@admin_router.message(SendTextChannel.photo)
async def leagues_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id, links=[])  # Добавляем список ссылок
        await state.set_state(SendTextChannel.text)
        await message.answer("Tekst kiriting")
    else:
        await message.answer("Rasim yuboring")


"Введите кнопку в формате:\n"
"`Название кнопки - ссылка`\n"


@admin_router.message(SendTextChannel.text)
async def leagues_handler(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(SendTextChannel.link)
    await message.answer(
        "Knopka va linkni (<b> Knopka - link </b>) formatda yuboring yoki <b>'✅ Tugatish'</b> tugmani bosing.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ Tugatish", callback_data="finish")]]
        ))


@admin_router.message(SendTextChannel.link)
async def leagues_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    links = data.get("links", [])

    if " - " in message.text:
        btn_text, btn_url = message.text.split(" - ", maxsplit=1)

        if Find(message.text):  # Проверяем правильность ссылки
            links.append((btn_text.strip(), btn_url.strip()))
            links.append(message.text)
            await state.update_data(links=links)

            await message.answer(
                f"✅ Link qo'shildi! -> {btn_text} - {btn_url.strip()} .\nYana qo'shing yoki <b>'✅ Tugatish'</b>  tugmani bosing",
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

    buttons = [[InlineKeyboardButton(text=btn_text, url=btn_url)] for btn_text, btn_url in links]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    try:
        await bot.send_photo(channel_id, photo=photo, caption=text, reply_markup=markup)
        await callback.message.answer("📢 Kanalga xabar yuborildi!")
    except:
        await callback.message.answer("❌ Yuborishda xatolik, tekshirib ko'ring admin qilganmisiz kanalga.")

    await state.clear()


#
#
# @admin_router.message(SendTextChannel.photo)
# async def leagues_handler(message: Message, bot: Bot, state: FSMContext):
#     if message.photo:
#         await state.update_data(photo=message.photo[-1].file_id)
#         await state.set_state(SendTextChannel.text)
#         await message.answer("Tekst kiriting")
#     else:
#         await message.answer("Rasim yuboring")
#
#
# @admin_router.message(SendTextChannel.text)
# async def leagues_handler(message: Message, state: FSMContext):
#     await state.update_data(text=message.text)
#     await state.set_state(SendTextChannel.link)
#     await message.answer("Link yuboring")
#
#
# @admin_router.message(SendTextChannel.link)
# async def leagues_handler(message: Message, bot: Bot, state: FSMContext):
#     data = await state.get_data()
#     if Find(message.text):
#         try:
#             await bot.send_photo(data.get('channel_id'), photo=data.get('photo'), caption=message.text)
#             await message.answer("Kanalga xabar yuborildi")
#             await message.answer("Settings", reply_markup=settings())
#         except:
#             await message.answer("Kanalga xabar yuborishda xatolik, meni admin qiling")
#             await message.answer("Settings", reply_markup=settings())
#         await state.clear()
#     else:
#         await message.answer("Link notog'ri formatda")


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


@admin_router.callback_query(F.data.startswith("text_"))
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split('_')[-1]
    if data == 'add':
        await state.set_state(AddTextSend.text)
        await call.message.answer("Yangi text kiriting")
    if data == "change":
        await state.set_state(ChangeTextSend.text)
        await call.message.answer("Yangi text kiriting")
    if data == 'back':
        await call.message.edit_text("Settings", reply_markup=settings())


@admin_router.message(AddTextSend.text)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(text=message.text)
    await state.set_state(AddTextSend.link)
    await message.answer("Link kiriting!")


@admin_router.message(ChangeTextSend.text)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(text=message.text)
    await TextInSend.update(1, text=message.text)
    text: TextInSend = await TextInSend.get(1)
    await message.answer(text=f"{text.text}\n\n{text.link}", reply_markup=text_add())
    # await state.set_state(AddTextSend.link)
    # await message.answer("Link kiriting!")


# @admin_router.message(ChangeTextSend.link)
# async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
#     await state.update_data(text=message.text)
#     await TextInSend.update(1, text=message.text)
#     text: TextInSend = await TextInSend.get(1)
#     await state.set_state(AddTextSend.link)
#     await message.answer("Link kiriting!")

@admin_router.message(AddTextSend.link)
async def leagues_handler(message: Message, state: FSMContext, bot: Bot):
    if Find(message.text):
        data = await state.get_data()
        await state.update_data(link=message.text)
        await TextInSend.create(text=data.get('text'), link=message.text)
        await message.answer(text=f"{data.get('text')}\n\n{message.text}", reply_markup=text_add())
    else:
        await message.answer("Link notog'ri formatda! Qayta kiriting!")


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
                await Channels.create(chat_id=update.chat.id, name=update.chat.title)

                await bot.send_message(
                    admin_1,
                    f"✅ Bot kanalga qo'shildi: {update.chat.title} (Kanal ID: {update.chat.id})"
                )
                await bot.send_message(
                    admin_2,
                    f"✅ Bot kanalga qo'shildi: {update.chat.title} (Kanal ID: {update.chat.id})"
                )

# @admin_router.callback_query(F.data.startswith('settings_stock'))
# async def leagues_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
#     await call.message.edit_text("Settings", reply_markup=settings())
