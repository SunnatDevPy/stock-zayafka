from aiogram.types import InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
              InlineKeyboardButton(text="➕Kanallar➕", callback_data='settings_subscribe'),
              InlineKeyboardButton(text="⬅️Ortga", callback_data='settings_back')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def link(url):
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text='Link', url=url))
    return ikb.as_markup()


def link_from_channel(links):
    ikb = InlineKeyboardBuilder()
    for btn in links:
        ikb.add(InlineKeyboardButton(text=btn[0], url=btn[-1]))
    ikb.adjust(1)
    return ikb.as_markup()


def text_add(status=False):
    ikb = InlineKeyboardBuilder()
    if status:
        ikb.row(InlineKeyboardButton(text="➕Qo'shish➕", callback_data="text_add"))
    else:
        ikb.row(InlineKeyboardButton(text="🔃O'zgartirish🔃", callback_data="text_change"))
    ikb.row(InlineKeyboardButton(text="👈Ortga👈", callback_data="text_back"))
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
            InlineKeyboardButton(text=i.name, callback_data=f'channels_info_{i.chat_id}')
        ])
    # ikb.row(InlineKeyboardButton(text="Kanalga qo'shish", url=f"https://t.me/asamax_prizbot?startchannel=true"))
    ikb.row(InlineKeyboardButton(text="Kanalga qo'shish", url=f"https://t.me/Stockfootball_bot?startchannel=true"))
    ikb.row(InlineKeyboardButton(text="⬅️Ortga️", callback_data="channels_back"))
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()


async def detail_channel(channel_id):
    ikb = InlineKeyboardBuilder()
    channel = await Channels.get(int(channel_id))
    if channel:
        pass
    else:
        channel = await Channels.get_chat(int(channel_id))
    ikb.add(
        *[InlineKeyboardButton(text='✅Ishlamoqda✅' if channel.status else '❌O\'chiq❌',
                               callback_data=f'channels_change_{channel.id}'),
          InlineKeyboardButton(text="Xabar jo'natish", callback_data=f'channels_send_{channel_id}'),
          InlineKeyboardButton(text="Zayafka uchun xabar", callback_data=f'channel_zayafka_{channel_id}'),
          InlineKeyboardButton(text="Ortga", callback_data=f'channels_back_{channel_id}'),
          ])
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()


async def send_message_button():
    ikb = InlineKeyboardBuilder()
    ikb.add(
        *[InlineKeyboardButton(text="Ko'chirilgan xabar", callback_data=f'type_forward'),
          InlineKeyboardButton(text="Custom yaratish", callback_data=f'type_send'),
          InlineKeyboardButton(text="Ortga", callback_data=f'type_back'),
          ])
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()


async def detail_message_channel(channel_id, url=None):
    ikb = InlineKeyboardBuilder()
    ikb.add(
        *[InlineKeyboardButton(text="Link", url=url) if url else None,
          InlineKeyboardButton(text="O'zgartirish", callback_data=f'type_change_{channel_id}'),
          InlineKeyboardButton(text="Ortga", callback_data=f'type_back'),
          ])
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()
