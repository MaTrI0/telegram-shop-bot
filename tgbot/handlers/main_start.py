# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.data.loader import dp
from tgbot.keyboards.inline_user import user_support_finl
from tgbot.keyboards.reply_all import menu_frep
from tgbot.utils.misc.bot_filters import IsBuy, IsWork

# Игнор-колбэки покупок
prohibit_buy = ['buy_category_open', 'buy_category_swipe', 'buy_position_open', 'buy_position_swipe',
                'buy_item_open', 'buy_item_confirm']

# Игнор-колбэки пополнений
prohibit_refill = ['user_refill', 'refill_choice', 'Pay:', 'Pay:Form', 'Pay:Number', 'Pay:Nickname']


####################################################################################################
######################################## ТЕХНИЧЕСКИЕ РАБОТЫ ########################################
# Фильтр на технические работы - сообщение
@dp.message_handler(IsWork(), state="*")
async def filter_work_message(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Бот находится на технической паузе.</b>", reply_markup=user_support_finl())


# Фильтр на технические работы - колбэк
@dp.callback_query_handler(IsWork(), state="*")
async def filter_work_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Бот находится на технической паузе.", True)


####################################################################################################
########################################### СТАТУС ПОКУПОК #########################################
# Фильтр на доступность покупок - сообщение
@dp.message_handler(IsBuy(), text="🎁 Товары", state="*")
@dp.message_handler(IsBuy(), state="here_item_count")
async def filter_buy_message(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⛔ Просмотр и покупка товаров временно отключена.</b>")


# Фильтр на доступность покупок - колбэк
@dp.callback_query_handler(IsBuy(), text_startswith=prohibit_buy, state="*")
async def filter_buy_callback(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.answer("⛔ Просмотр и покупка товаров временно отключена.", True)


####################################################################################################
############################################## ПРОЧЕЕ ##############################################
# Открытие главного меню
@dp.message_handler(text=['⬅ Главное меню', '/start'], state="*")
async def main_start(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("🔸 Бот готов для использования.\n"
                         "🔸 Если не появятся вспомогательные кнопки\n"
                         "▶  Введите /start",
                         reply_markup=menu_frep(message.from_user.id))
