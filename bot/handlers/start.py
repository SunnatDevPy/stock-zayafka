from aiogram import Router, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatJoinRequest, ChatMemberUpdated

from bot.buttuns.inline import language_inl, start, channels, links_zayafka
from models import BotUser, Channels
from models.users import TextZayafka

start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    data = await state.get_data()
    locale = data.get('locale')
    if locale == 'rus':
        til = "Выберите язык"
    else:
        til = 'Til tanlang'
    await message.answer(til, reply_markup=language_inl())


text = """
⚽️ Futbol natijalari va jadvallarni real vaqt rejimida kuzatib boring!

📊 Turnir holati va jamoalar joylashuvi
⚡️ Jonli natijalar va statistikalar
📅 O‘yin taqvimi va natijalar

Hammasi bizning botda – qo‘shiling!"""


@start_router.chat_join_request()
async def zayafka(chat_join: ChatJoinRequest, bot: Bot):
    user = await BotUser.get(chat_join.from_user.id)
    zayafka_text: TextZayafka = await TextZayafka.get(1)
    if not user:
        from_user = chat_join.from_user
        await BotUser.create(id=from_user.id, first_name=from_user.first_name,
                             last_name=from_user.last_name,
                             username=from_user.username)
    channel: Channels = await Channels.get_chat(chat_join.chat.id)
    # if channel:
    #     try:
    #         if channel.text and channel.photo:
    #             await bot.send_photo(chat_id=chat_join.from_user.id, photo=channel.photo, caption=channel.text,
    #                                  reply_markup=await links_zayafka(channel.chat_id))
    #         if zayafka_text:
    #             await bot.send_photo(chat_id=chat_join.from_user.id, photo=zayafka_text.photo,
    #                                  caption=zayafka_text.name)
    #         else:
    #             await bot.send_message(chat_id=chat_join.from_user.id, text=text,
    #                                    reply_markup=start())
    #     except:
    #         if zayafka_text:
    #             await bot.send_photo(chat_id=chat_join.from_user.id, photo=zayafka_text.photo,
    #                                  caption=zayafka_text.name)
    #         else:
    #             await bot.send_message(chat_id=chat_join.from_user.id, text=text,
    #                                    reply_markup=start())
    # else:
    #     if zayafka_text:
    #         await bot.send_photo(chat_id=chat_join.from_user.id, photo=zayafka_text.photo, caption=zayafka_text.name)
    #     else:
    await bot.send_message(chat_id=chat_join.from_user.id, text=text,
                                   reply_markup=start())
    try:
        await chat_join.approve()
    except:
        pass


admin_1 = 5649321700


@start_router.my_chat_member()
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
                # await bot.send_message(
                #     admin_2,
                #     f"✅ Bot kanalga qo'shildi: {update.chat.title} (Kanal ID: {update.chat.id})"
                # )
                await bot.send_message(admin_1, text='Kanallar', reply_markup=await channels(channels_))
                # await bot.send_message(admin_2, text='Kanallar', reply_markup=await channels(channels_))
            else:
                await bot.send_message(
                    update.chat.id,
                    f"✅ Bot kanalga qo'shildi: {update.chat.title} (Kanal ID: {update.chat.id})"
                )

# channel: Channels = await Channels.get_chat(chat_join.chat.id)
# print(chat_join)
# if channel:
#     if channel.status:
#         if channel.text:
#             await chat_join.approve()
#             buttons = channel.buttons or []
#
#             if channel.photo:
#                 await bot.send_photo(chat_id=chat_join.from_user.id, photo=channel.photo,
#                                      caption=channel.text, reply_markup=links_zayafka(buttons))
#             elif channel.video:
#                 await bot.send_video(chat_id=chat_join.from_user.id, video=channel.video,
#                                      caption=channel.text, reply_markup=links_zayafka(buttons))
#             else:
#                 await bot.send_message(chat_id=chat_join.from_user.id, text=channel.text,
#                                        reply_markup=links_zayafka(buttons))
#         else:
#             await bot.send_message(chat_id=chat_join.from_user.id, text='Xush kelibsiz')
# else:
#     await bot.send_message(chat_id=chat_join.from_user.id, text="Xatolik yuz berdi")
