from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from models import Channels


def language_inl():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text='🇺🇿Uz', callback_data='lang_uz'),
              InlineKeyboardButton(text='🇷🇺Ru', callback_data='lang_rus')])
    ikb.adjust(2)
    return ikb.as_markup()


def menu(admin=False):
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="STOCK",
                                   web_app=WebAppInfo(
                                       url=f'https://football-stock.uz/uz/'))])
    if admin:
        ikb.add(*[InlineKeyboardButton(text="⚙️Settings⚙️", callback_data='settings_stock')])
    ikb.adjust(1, 2)
    return ikb.as_markup()


def settings():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="Userlar soni", callback_data='settings_static'),
              InlineKeyboardButton(text="📝Xabar jo'natish📝", callback_data='settings_send'),
              InlineKeyboardButton(text="Obuna text", callback_data='settings_text'),
              InlineKeyboardButton(text="Kanalga qo'shish", callback_data='settings_subscribe'),
              InlineKeyboardButton(text="⬅️Ortga", callback_data='settings_back')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def link(url):
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text='Link', url=url))
    return ikb.as_markup()


def text_add(status=False):
    ikb = InlineKeyboardBuilder()
    if status:
        ikb.row(InlineKeyboardButton(text="Qo'shish", callback_data="text_add"))
    else:
        ikb.row(InlineKeyboardButton(text="O'zgartirish", callback_data="text_change"))
    return ikb.as_markup()


def send_text():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="Oddiy xabar", callback_data='send_text'),
              InlineKeyboardButton(text="📸Rasm-Videoli Xabar🎥", callback_data='send_video'),
              InlineKeyboardButton(text="⬅️Ortga", callback_data='send_back')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def confirm_text():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="✅Jo'natish✅", callback_data='confirm'),
              InlineKeyboardButton(text="❌To'xtatish❌", callback_data='stop')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def confirm_inl():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text='✅Tasdiqlash✅', callback_data=f'confirm_network'),
              InlineKeyboardButton(text="❌Toxtatish❌", callback_data=f'cancel_network')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


async def channels(channels):
    ikb = InlineKeyboardBuilder()
    for i in channels:
        ikb.add(*[
            InlineKeyboardButton(text=i.name, callback_data=f'channels_{i.id}')
        ])
    ikb.row(InlineKeyboardButton(text="Kanalga qo'shish", url=f"https://t.me/stock_security_bot?startchannel=true"))
    ikb.row(InlineKeyboardButton(text="⬅️Ortga️", callback_data="channels_back"))
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()
