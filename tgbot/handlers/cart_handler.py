from time import sleep

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.inline_all import profile_open_inl
from tgbot.keyboards.inline_page import products_item_category_swipe_fp
from tgbot.keyboards.inline_user import success_added_item_cart, cart_keyboard, cart_pay_confirm
from tgbot.keyboards.reply_all import menu_frep
from tgbot.services.api_sqlite import *
from tgbot.data.loader import dp, bot
from tgbot.utils.misc_functions import cart_logistic, open_profile_user


# Подтверждение добавление товара в кoрзину
@dp.callback_query_handler(text_startswith="cart_item_confirm:", state="*")
async def user_add_cart_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    position_id = int(call.data.split(":")[2])

    if get_action == "yes":
        get_count = int(call.data.split(":")[3])
        await state.update_data(get_count=get_count)

        get_select_color = str(call.data.split(":")[4])
        await state.update_data(get_select_color=get_select_color)

        get_select_size = str(call.data.split(":")[5])
        await state.update_data(get_select_size=get_select_size)

        await call.message.edit_text("<b>🔄 Ожидайте, товары готовятся</b>")

        get_position = get_positionx(position_id=position_id)
        await state.update_data(get_position=get_position)

        amount_pay = int(get_position['position_price'] * get_count)
        await state.update_data(amount_pay=amount_pay)

        if 1 <= int(get_count) <= 100:
            await call.message.delete()

            add_user_cart(user_id=call.from_user.id, position_id=position_id, position_count=get_count,
                          position_color=get_select_color, position_size=get_select_size, position_price=amount_pay)

            cart_item = 0
            get_user_cart_items = get_user_cart(user_id=call.from_user.id)

            if get_user_cart_items is None:
                pass
            else:
                for items in get_user_cart_items:
                    cart_item += 1

            await call.message.answer("✅ Вы успешно добавили товар в корзину, теперь вы можете: ",
                                      reply_markup=success_added_item_cart(cart_item))
        else:
            await call.message.answer("<b>🎁 Товар который вы хотели добавить в кoрзину закончился или изменился.</b>",
                                      reply_markup=menu_frep(call.from_user.id))
    else:
        if len(get_all_categoriesx()) >= 1:
            await call.message.edit_text("<b>🎁 Выберите нужный вам товар:</b>",
                                         reply_markup=products_item_category_swipe_fp(0))
        else:
            await call.message.edit_text("<b>❌ Вы отменили добавление товара в кoрзину.</b>")


# Открытие карзины
@dp.callback_query_handler(text_startswith="cart_open", state="*")
async def user_open_cart(call: CallbackQuery, state: FSMContext):
    cart = cart_logistic(user_id=call.from_user.id)

    if cart is None:
        await call.answer(f"🛒 Ваша корзина пуста :(")
    else:
        await call.message.edit_text(f"{cart}", reply_markup=cart_keyboard())


# Очистка корзины
@dp.callback_query_handler(text_startswith="clear_cart", state="*")
async def user_clear_cart(call: CallbackQuery, state: FSMContext):
    await call.answer("🛒 Корзина очищена")
    remove_cart(user_id=call.from_user.id)

    cart_item = 0
    get_user_cart_items = get_user_cart(user_id=call.from_user.id)

    if get_user_cart_items is None:
        pass
    else:
        for items in get_user_cart_items:
            cart_item += 1

    await call.message.edit_text(open_profile_user(call.from_user.id), reply_markup=profile_open_inl(cart_item))


# Оплата товара в корзине
@dp.callback_query_handler(text_startswith="cart_pay", state="*")
async def start_pay_cart(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("🛒 Вы действительно хотите купить все товары, которые находятся в корзине?", reply_markup=cart_pay_confirm())


# Возврат в меню
@dp.callback_query_handler(text_startswith="main_menu", state="*")
async def user_main_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cart_item = 0
    get_user_cart_items = get_user_cart(user_id=call.from_user.id)

    if get_user_cart_items is None:
        pass
    else:
        for items in get_user_cart_items:
            cart_item += 1

    await call.message.edit_text(open_profile_user(call.from_user.id), reply_markup=profile_open_inl(cart_item))
