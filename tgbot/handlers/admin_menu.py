# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.data.config import BOT_VERSION, PATH_LOGS, PATH_DATABASE
from tgbot.data.loader import dp
from tgbot.keyboards.reply_all import settings_frep, functions_frep, items_frep, promocodes_frep
from tgbot.utils.const_functions import get_date
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import get_statisctics


# Настройки бота
@dp.message_handler(IsAdmin(), text="⚙ Настройка", state="*")
async def admin_settings(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>⚙ Основные настройки бота.</b>", reply_markup=settings_frep())


# Общие функции
@dp.message_handler(IsAdmin(), text="🔆 Общие функции", state="*")
async def admin_functions(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🔆 Выберите нужную функцию.</b>", reply_markup=functions_frep(message.from_user.id))


# Керування товарами
@dp.message_handler(IsAdmin(), text="🎁 Управление товарами", state="*")
async def admin_products(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🎁 Редактирование товаров</b>", reply_markup=items_frep())


# Керування товарами
@dp.message_handler(IsAdmin(), text="🎟 Управление промокодами", state="*")
async def admin_products(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🎟 Редактирование промокодов</b>", reply_markup=promocodes_frep())


# Cтатистики бота
@dp.message_handler(IsAdmin(), text="📊 Статистика", state="*")
async def admin_statistics(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(get_statisctics())


# Получение БД
@dp.message_handler(IsAdmin(), commands=['db', 'database'], state="*")
async def admin_database(message: Message, state: FSMContext):
    await state.finish()

    with open(PATH_DATABASE, "rb") as document:
        await message.answer_document(document,
                                      caption=f"<b>📦 BACKUP\n"
                                              f"🕰 <code>{get_date()}</code></b>")


# Получение Логов
@dp.message_handler(IsAdmin(), commands=['log', 'logs'], state="*")
async def admin_log(message: Message, state: FSMContext):
    await state.finish()

    with open(PATH_LOGS, "rb") as document:
        await message.answer_document(document,
                                      caption=f"<b>🖨 LOGS\n"
                                              f"🕰 <code>{get_date()}</code></b>")


# Получение версии бота
@dp.message_handler(commands=['version', 'log'], state="*")
async def admin_version(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(f"<b>❇ Текущая версия бота: <code>{BOT_VERSION}</code></b>")
