from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.buttuns.inline import menu
from models import BotUser

language_router = Router()


@language_router.callback_query(F.data.startswith('lang_'))
async def language_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    lang_code = call.data.split('lang_')[-1]
    if lang_code == 'rus':
        salom = "Здравствуйте"
        til = "Язык выбран"
    else:
        til = "Til tanlandi"
        salom = "Assalomu aleykum"
    await call.message.delete()
    await state.update_data(locale=lang_code)
    await call.answer(til, show_alert=True)
    user = await BotUser.get(call.from_user.id)
    if not user:
        from_user = call.from_user
        try:
            await BotUser.create(id=from_user.id, first_name=from_user.first_name,
                                 last_name=from_user.last_name,
                                 username=from_user.username)
        except:
            await bot.send_message(5649321700, f'user: {from_user}')
        if call.from_user.id in [5649321700, 1353080275]:
            await call.message.answer(f'{salom} Admin {call.from_user.first_name}', reply_markup=menu(admin=True))
        else:
            await call.message.answer(f"{salom} {call.from_user.first_name}", reply_markup=menu())
    else:
        if call.from_user.id in [5649321700, 1353080275]:
            await call.message.answer(f'{salom} Admin {call.from_user.first_name}', reply_markup=menu(admin=True))
        else:
            await call.message.answer(f"{salom} {call.from_user.first_name}", reply_markup=menu())
