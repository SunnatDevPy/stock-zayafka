# Список заблокированных пользователей (Можно хранить в БД)
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

blocked_users = set()

block_router = Router()

# Клавиатура для разблокировки
def unblock_keyboard(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Разблокировать", callback_data=f"unblock_{user_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ]
    )

# Обработчик команды /check_requests (можно автоматизировать)
@block_router.message(Command("check_requests"))
async def check_requests(message: Message, bot: Bot):
    chat_id = "@your_channel"  # ID или username канала
    join_requests = await bot.get_chat(chat_id)

    for request in join_requests:
        user_id = request.from_user.id
        username = request.from_user.username or "Без имени"

        if user_id in blocked_users:
            text = (f"Администратор канала хочет связаться с вами по поводу заявки на вступление.\n\n"
                    f"Чтобы заявка была рассмотрена, удалите бота из списка заблокированных пользователей "
                    f"или нажмите кнопку ниже.")

            await bot.send_message(user_id, text, reply_markup=unblock_keyboard(user_id))

# Обработчик кнопки разблокировки
@block_router.callback_query(lambda c: c.data.startswith("unblock_"))
async def unblock_user(callback: CallbackQuery, bot: Bot):
    user_id = int(callback.data.split("_")[1])
    blocked_users.discard(user_id)  # Удаляем из блок-листа

    await callback.message.edit_text("✅ Вы разблокировали бота. Заявка будет рассмотрена.")
    await bot.approve_chat_join_request("@your_channel", user_id)

# Обработчик кнопки отмены
@block_router.callback_query(lambda c: c.data == "cancel")
async def cancel(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Отменено.")
