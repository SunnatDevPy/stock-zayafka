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


@bot_anons_router.callback_query(F.data.startswith('send_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')[-1]
    await call.answer()
    if data == 'user':
        await call.message.answer("Userlar uchun xabar yuborish usulini tanlang", reply_markup=send_text_type('user'))
    if data == 'channel':
        await call.message.answer("Kanallar uchun xabar yuborish usulini tanlang",
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

        if reply_markup and isinstance(reply_markup, InlineKeyboardMarkup):
            buttons = reply_markup.inline_keyboard
        else:
            buttons = []

        markup = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
        send_text = data.get('send_text')
        if send_text == 'user':
            users: list[BotUser] = await BotUser.all()
            for i in users:
                try:
                    # Если в пересланном сообщении есть фото
                    if message.photo:
                        await bot.send_photo(
                            chat_id=i.id,
                            photo=message.photo[-1].file_id,
                            caption=text,
                            reply_markup=markup
                        )
                    # Если есть видео
                    elif message.video:
                        await bot.send_video(
                            chat_id=i.id,
                            video=message.video.file_id,
                            caption=text,
                            reply_markup=markup
                        )
                    # Если есть документ (PDF, DOCX и т. д.)
                    elif message.document:
                        await bot.send_document(
                            chat_id=i.id,
                            document=message.document.file_id,
                            caption=text,
                            reply_markup=markup
                        )
                    # Если просто текстовое сообщение
                    elif text:
                        await bot.send_message(
                            chat_id=i.id,
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
        else:
            users: list[Channels] = await Channels.all()
            for i in users:
                try:
                    # Если в пересланном сообщении есть фото
                    if message.photo:
                        await bot.send_photo(
                            chat_id=i.chat_id,
                            photo=message.photo[-1].file_id,
                            caption=text,
                            reply_markup=markup
                        )
                    # Если есть видео
                    elif message.video:
                        await bot.send_video(
                            chat_id=i.chat_id,
                            video=message.video.file_id,
                            caption=text,
                            reply_markup=markup
                        )
                    # Если есть документ (PDF, DOCX и т. д.)
                    elif message.document:
                        await bot.send_document(
                            chat_id=i.chat_id,
                            document=message.document.file_id,
                            caption=text,
                            reply_markup=markup
                        )
                    # Если просто текстовое сообщение
                    elif text:
                        await bot.send_message(
                            chat_id=i.chat_id,
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
    if send_text == 'user':
        users: list[BotUser] = await BotUser.all()
        try:
            for i in users:
                await bot.send_photo(i.id, photo=photo, caption=text, reply_markup=link_from_channel(links))
            await callback.message.answer("📢 Kanalga xabar yuborildi!")
            await callback.message.answer("Settings", reply_markup=settings())
        except:
            await callback.message.answer("❌ Yuborishda xatolik, tekshirib ko'ring admin qilganmisiz kanalga.")
    else:
        users: list[Channels] = await Channels.all()
        try:
            for i in users:
                await bot.send_photo(i.chat_id, photo=photo, caption=text, reply_markup=link_from_channel(links))
            await callback.message.answer("📢 Kanalga xabar yuborildi!")
            await callback.message.answer("Settings", reply_markup=settings())
        except:
            await callback.message.answer("❌ Yuborishda xatolik, tekshirib ko'ring admin qilganmisiz kanalga.")

    await state.clear()
