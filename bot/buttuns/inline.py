from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


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
        ikb.add(*[InlineKeyboardButton(text="⚙️Settings⚙️", callback_data='game_settings')])
    ikb.adjust(1, 2)
    return ikb.as_markup()
