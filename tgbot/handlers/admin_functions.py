# - *- coding: utf- 8 - *-
import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import CantParseEntities

from tgbot.data.loader import dp, bot
from tgbot.keyboards.inline_admin import profile_search_finl, profile_search_return_finl
from tgbot.keyboards.inline_all import mail_confirm_inl
from tgbot.services.api_sqlite import *
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import open_profile_admin


# Рассылка
@dp.message_handler(IsAdmin(), text="📢 Оповещение", state="*")
async def functions_mail(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_mail_text")
    await message.answer("<b>📢 Введите текст который должен прийти пользователям!</b>\n"
                         "❕ Вы можете использовать HTML разметку текста")


# Поиск профиля
@dp.message_handler(IsAdmin(), text="👤 Поиск профиля 🔍", state="*")
async def functions_profile(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_profile")
    await message.answer("<b>👤 Введите @login или ID пользователя</b>")


# # Поиск чеков
@dp.message_handler(IsAdmin(), text="🧾 Поиск чеков 🔍", state="*")
async def functions_receipt(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_receipt")
    await message.answer("<b>🧾 Введите номер чека</b>")


######################################## ПРИНЯТИЕ ПОИСКОВЫХ ДАННЫХ ########################################
# Принятие айди или логина для поиска профиля
@dp.message_handler(IsAdmin(), state="here_profile")
@dp.message_handler(IsAdmin(), text_startswith=".user")
async def functions_profile_get(message: Message, state: FSMContext):
    find_user = message.text

    if ".user" in find_user:
        find_user = message.text.split(" ")
        if len(find_user) > 1:
            find_user = find_user[1]
        else:
            await message.answer("<b>❌ Ви не указали @login либо ID пользователя.</b>\n"
                                 "👤 Введите @login или ID пользователя.")
            return

    if find_user.isdigit():
        get_user = get_userx(user_id=find_user)
    else:
        if find_user.startswith("@"): find_user = find_user[1:]
        get_user = get_userx(user_login=find_user.lower())

    if get_user is not None:
        await state.finish()
        await message.answer(open_profile_admin(get_user['user_id']),
                             reply_markup=profile_search_finl(get_user['user_id']))
    else:
        await message.answer("<b>❌ Профиль не был найден!</b>\n"
                             "👤 Введите @login или ID пользователя.")


# Принятие чека для поиска
@dp.message_handler(IsAdmin(), state="here_receipt")
@dp.message_handler(IsAdmin(), text_startswith=".rec")
async def functions_receipt_get(message: Message, state: FSMContext):
    find_receipt = message.text

    if ".rec" in find_receipt:
        find_receipt = message.text.split(" ")
        if len(find_receipt) > 1:
            find_receipt = find_receipt[1]
        else:
            await message.answer("<b>❌ Ви не указали номер чека!.</b>\n"
                                 "🧾 Введите номер чека.")
            return

    if find_receipt.startswith("#"): find_receipt = find_receipt[1:]

    get_purchase = get_purchasex(purchase_receipt=find_receipt)

    if get_purchase is not None:
        await state.finish()

        await message.answer(
            f"<b>🧾 Чек: <code>#{get_purchase['purchase_receipt']}</code></b>\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"👤 Пользователь: <a href='tg://user?id={get_purchase['user_id']}'>{get_purchase['user_name']}</a> | <code>{get_purchase['user_id']}</code>\n"
            f"🏷 Название продукта: <code>{get_purchase['purchase_position_name']}</code>\n"
            f"📦 Купили товаров: <code>{get_purchase['purchase_count']}шт</code>\n"
            f"💰 Цена одного товара: <code>{get_purchase['purchase_price_one']}руб.</code>\n"
            f"💸 Сумма покупки: <code>{get_purchase['purchase_price']}руб.</code>\n"
            f"🕰 Дата покупки: <code>{get_purchase['purchase_date']}</code>"
        )
        return
    else:
        await message.answer("<b>❌ Ви не указали номер чека!.</b>\n"
                                 "🧾 Введите номер чека.")


######################################## РАССЫЛКА ########################################
# Принятие текста для рассылки
@dp.message_handler(IsAdmin(), state="here_mail_text")
async def functions_mail_get(message: Message, state: FSMContext):
    await state.update_data(here_mail_text="📢 Оповещение.\n" + str(message.text))
    get_users = get_all_usersx()

    try:
        cache_msg = await message.answer(message.text)
        await cache_msg.delete()

        await state.set_state("here_mail_confirm")
        await message.answer(
            f"<b>📢 Отправить <code>{len(get_users)}</code> пользователям сообщения?</b>\n"
            f"{message.text}",
            reply_markup=mail_confirm_inl,
            disable_web_page_preview=True
        )
    except CantParseEntities:
        await message.answer("<b>❌ Ошибка синтекзу HTML.</b>\n"
                             "📢 Введите текст для оповещения пользователей.\n"
                             "❕ Вы можете использовать HTML разметку.")


# Подтверждение отправки рассылки
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_mail", state="here_mail_confirm")
async def functions_mail_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]

    send_message = (await state.get_data())['here_mail_text']
    get_users = get_all_usersx()
    await state.finish()

    if get_action == "yes":
        await call.message.edit_text(f"<b>📢 Оповещение началось... (0/{len(get_users)})</b>")
        asyncio.create_task(functions_mail_make(send_message, call))
    else:
        await call.message.edit_text("<b>📢 Вы отменили отправку уведомления✅</b>")


# Сама отправка рассылки
async def functions_mail_make(message, call: CallbackQuery):
    receive_users, block_users, how_users = 0, 0, 0
    get_users = get_all_usersx()
    get_time = get_unix()

    for user in get_users:
        try:
            await bot.send_message(user['user_id'], message, disable_web_page_preview=True)
            receive_users += 1
        except:
            block_users += 1

        how_users += 1

        if how_users % 10 == 0:
            await call.message.edit_text(f"<b>📢 Оповещение началось... ({how_users}/{len(get_users)})</b>")

        await asyncio.sleep(0.08)

    await call.message.edit_text(
        f"<b>📢 Оповещение было закончено за <code>{get_unix() - get_time}сек</code></b>\n"
        f"👤 Всего пользователей: <code>{len(get_users)}</code>\n"
        f"✅ Пользователи получили уведомление: <code>{receive_users}</code>\n"
        f"❌ Пользователи не получили уведомления: <code>{block_users}</code>"
    )


######################################## УПРАВЛЕНИЕ ПРОФИЛЕМ ########################################
# Обновление профиля пользователя
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_refresh", state="*")
async def functions_profile_refresh(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    await state.finish()

    await call.message.delete()
    await call.message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))


# Покупки пользователя
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_purchases", state="*")
async def functions_profile_purchases(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    last_purchases = last_purchasesx(user_id, 10)

    if len(last_purchases) >= 1:
        await call.answer("🎁 Последние 10 купленных товаров")
        await call.message.delete()

        for purchases in last_purchases:

            await call.message.answer(f"<b>🧾 Чек: <code>#{purchases['purchase_receipt']}</code></b>\n"
                                      f"🎁 Товар: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}шт | {purchases['purchase_price']}руб.</code>\n"
                                      f"🕰 Дата покупки: <code>{purchases['purchase_date']}</code>\n")

        await call.message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))
    else:
        await call.answer("❗ У пользователя отсутствуют покупки", True)


# Отправка сообщения пользователю
@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_message", state="*")
async def functions_profile_user_message(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]

    await state.update_data(here_profile=user_id)
    await state.set_state("here_profile_message")

    await call.message.edit_text("<b>💌 Введите сообщение для отправки</b>\n"
                                 "⚠ Сообщение будет сразу отправлено пользователю.",
                                 reply_markup=profile_search_return_finl(user_id))


# Принятие сообщения для пользователя
@dp.message_handler(IsAdmin(), state="here_profile_message")
async def functions_profile_user_message_get(message: Message, state: FSMContext):
    user_id = (await state.get_data())['here_profile']
    await state.finish()

    get_message = "<b>💌 Сообщение от администратора:</b>\n" + clear_html(message.text)
    get_user = get_userx(user_id=user_id)

    await message.bot.send_message(user_id, get_message)
    await message.answer(f"<b>✅ Пользователю <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> "
                         f"Было отправлено сообщение:</b>\n"
                         f"{get_message}")

    await message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))


@dp.callback_query_handler(IsAdmin(), text_startswith="admin_user_cart", state="*")
async def functions_profile_cart(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    get_user = get_userx(user_id=user_id)

    get_cart_items = get_user_cart(user_id=user_id)

    if not get_cart_items:
        return await call.answer("🛒 Ваша корзина пуста :(")

    await call.answer("🛒 Корзина:")
    await call.message.delete()

    i = 1

    for item in get_cart_items:
        get_position = get_positionx(position_id=item.get("position_id"))
        await call.message.answer(f"""
        {i}) 🏷 Название: {get_position.get("position_name")}
             📦 Количество: {item.get("position_count")}
             📏 Размер: {item.get("position_size")}
             🎨 Цвет: {item.get("position_color")}
             💰 Цена: {item.get("position_price")}

    ➖➖➖➖➖➖➖➖➖➖
            """)

        i += 1

    await call.message.answer(open_profile_admin(user_id), reply_markup=profile_search_finl(user_id))
