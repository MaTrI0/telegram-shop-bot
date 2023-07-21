# - *- coding: utf- 8 - *-
from contextlib import suppress

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import MessageCantBeDeleted

from tgbot.data.config import BOT_DESCRIPTION
from tgbot.data.loader import dp
from tgbot.keyboards.inline_all import profile_open_inl
from tgbot.keyboards.inline_page import *
from tgbot.keyboards.inline_user import user_support_finl, products_open_finl, products_confirm_finl, \
    products_confirm_add
from tgbot.services.api_sqlite import *
from tgbot.utils.const_functions import split_messages, ded, get_date1
from tgbot.utils.misc_functions import open_profile_user, get_faq

time = get_date1()

day = time.split(".")[0]
month = time.split(".")[1]
years = time.split(".")[2].replace("20", "")

print(f'{years}')


# Открытие товаров
@dp.message_handler(text="🎁 Товары", state="*")
async def user_shop(message: Message, state: FSMContext):
    await state.finish()

    if len(get_all_categoriesx()) >= 1:
        await message.answer("<b>🎁 Выберите нужную вам категорию:</b>",
                             reply_markup=products_item_category_swipe_fp(0))
    else:
        await message.answer("<b>🎁 К сожалению, товары в настоящее время отсутствуют.</b>")


# Открытие профиля
@dp.message_handler(text="👤 Профиль", state="*")
async def user_profile(message: Message, state: FSMContext):
    cart_item = 0
    get_user_cart_items = get_user_cart(user_id=message.from_user.id)

    if get_user_cart_items is None:
        pass
    else:
        for items in get_user_cart_items:
            cart_item += 1

    await state.finish()

    await message.answer(open_profile_user(message.from_user.id), reply_markup=profile_open_inl(cart_item))


# Проверка товаров в наличии
@dp.message_handler(text="🧮 Товары в наличии", state="*")
async def user_available(message: Message, state: FSMContext):
    await state.finish()

    get_categories = get_all_categoriesx()
    save_items = []

    for category in get_categories:
        get_positions = get_positionsx(category_id=category['category_id'])
        this_items = []

        if len(get_positions) >= 1:
            this_items = [f"<b>➖➖➖ {category['category_name']} ➖➖➖</b>"]

            for position in get_positions:
                this_items.append(
                    f"{position['position_name']} | {position['position_price']}руб.")

        if len(this_items) >= 2:
            save_items.append(this_items)

    if len(save_items) >= 1:
        send_items = ":^^^^^:".join(["\n".join(item) for item in save_items])

        if len(send_items) > 3500:
            split_items = split_messages(send_items.split("\n"), 40)

            for item in split_items:
                await message.answer("\n".join(item).replace(":^^^^^:", "\n\n"))
        else:
            await message.answer("\n\n".join(["\n".join(item) for item in save_items]))
    else:
        await message.answer("<b>🎁 К сожалению, товары в настоящее время отсутствуют.</b>")


# Открытие FAQ
@dp.message_handler(text=["ℹ FAQ", "/faq"], state="*")
async def user_faq(message: Message, state: FSMContext):
    await state.finish()

    send_message = get_settingsx()['misc_faq']
    if send_message == "None":
        send_message = f"ℹ ➖➖➖➖➖➖➖➖➖➖\n{BOT_DESCRIPTION}"

    await message.answer(get_faq(message.from_user.id, send_message), disable_web_page_preview=True)


# Открытие сообщения со ссылкой на поддержку
@dp.message_handler(text=["☎ Поддержка", "/support"], state="*")
async def user_support(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(f"☎ Нажмите кнопку ниже для связи с Администратором.",
                         reply_markup=user_support_finl(),
                         disable_web_page_preview=True)


################################################################################################
# Просмотр истории покупок
@dp.callback_query_handler(text="user_history", state="*")
async def user_history(call: CallbackQuery, state: FSMContext):
    cart_item = 0
    get_user_cart_items = get_user_cart(user_id=call.from_user.id)

    if get_user_cart_items is None:
        pass
    else:
        for items in get_user_cart_items:
            cart_item += 1

    last_purchases = last_purchasesx(call.from_user.id, 5)

    if len(last_purchases) >= 1:
        await call.answer("🎁 Последние 5 покупок")
        with suppress(MessageCantBeDeleted):
            await call.message.delete()

        for purchases in last_purchases:

            await call.message.answer(ded(f"""
                                      <b>🧾 Чек: <code>#{purchases['purchase_receipt']}</code></b>
                                      🎁 Пункт: <code>{purchases['purchase_position_name']} | {purchases['purchase_count']}шт | {purchases['purchase_price']}руб.</code>
                                      🕰 Дата приобретения: <code>{purchases['purchase_date']}</code>
                                      """))

        await call.message.answer(open_profile_user(call.from_user.id), reply_markup=profile_open_inl(cart_item))
    else:
        await call.answer("❗ У вас отсутствуют покупки", True)


# Возвращение к профилю
@dp.callback_query_handler(text="user_profile", state="*")
async def user_profile_return(call: CallbackQuery, state: FSMContext):
    cart_item = 0
    get_user_cart_items = get_user_cart(user_id=call.from_user.id)

    if get_user_cart_items is None:
        pass
    else:
        for items in get_user_cart_items:
            cart_item += 1

    await call.message.edit_text(open_profile_user(call.from_user.id), reply_markup=profile_open_inl(cart_item))


################################################################################################
######################################### ПОКУПКА ТОВАРА #######################################
# Переключение страниц категорий для покупки
@dp.callback_query_handler(text_startswith="buy_category_swipe:", state="*")
async def user_purchase_category_next_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🎁 Выберите нужную вам категорию:</b>",
                                 reply_markup=products_item_category_swipe_fp(remover))


# Открытие категории для покупки
@dp.callback_query_handler(text_startswith="buy_category_open:", state="*")
async def user_purchase_category_open(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_category = get_categoryx(category_id=category_id)
    get_positions = get_positionsx(category_id=category_id)

    if len(get_positions) >= 1:
        with suppress(MessageCantBeDeleted):
            await call.message.delete()

        await call.message.answer(f"<b>🎁 Текущая категория: <code>{get_category['category_name']}</code></b>",
                                  reply_markup=products_item_position_swipe_fp(remover, category_id))
    else:
        if remover == "0":
            await call.message.edit_text("<b>🎁 К сожалению, товары в настоящее время отсутствуют.</b>")
            await call.answer("❗ Позиции были изменены или удалены")
        else:
            await call.answer(f"❕ Товары в категории {get_category['category_name']} отсутствовуют")


# Открытие позиции для покупки
@dp.callback_query_handler(text_startswith="buy_position_open:", state="*")
async def user_purchase_position_open(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    get_position = get_positionx(position_id=position_id)
    get_category = get_categoryx(category_id=category_id)

    if get_position['position_description'] == "0":
        text_description = ""
    else:
        text_description = f"\n📜 Описание:\n{get_position['position_description']}"

    color_text = "<code>Отсутствует ❌</code>"
    size_text = "<code>Отсутствует ❌</code>"

    if get_position["position_colors"] != "":
        color_text = f"{get_position['position_colors']}"

    if get_position["position_sizes"] != "":
        size_text = f"{get_position['position_sizes']}"

    send_msg = ded(f"""
               <b>🎁 Покупка товаров:</b>
               ➖➖➖➖➖➖➖➖➖➖
               🏷 Название: <code>{get_position['position_name']}</code>
               🗃 Категория: <code>{get_category['category_name']}</code>
               💰 Стоимость: <code>{get_position['position_price']}руб.</code>
               🎨 Цвета: <code>{color_text}</code>
               📏 Размеры: <code>{size_text}</code>
               {text_description}
               """)

    if len(get_position['position_photo']) >= 5:
        with suppress(MessageCantBeDeleted):
            await call.message.delete()
        await call.message.answer_photo(get_position['position_photo'],
                                        send_msg, reply_markup=products_open_finl(position_id, category_id, remover))
    else:
        await call.message.edit_text(send_msg,
                                     reply_markup=products_open_finl(position_id, category_id, remover))


# Переключение страницы позиций для покупки
@dp.callback_query_handler(text_startswith="buy_position_swipe:", state="*")
async def user_purchase_position_next_page(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    get_category = get_categoryx(category_id=category_id)

    await call.message.edit_text(f"<b>🎁 Текущая категория: <code>{get_category['category_name']}</code></b>",
                                 reply_markup=products_item_position_swipe_fp(remover, category_id))


########################################### ДОБАВЛЕНИЕ В КОРЗИНУ ##########################################
# Выбор цвета товара для корзины
@dp.callback_query_handler(text_startswith="cart_item_open:", state="*")
async def user_purchase_select(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]

    get_position = get_positionx(position_id=position_id)

    await state.update_data(here_cache_position_id=position_id)
    await state.set_state("cart_item_color")

    await call.message.answer(ded(f"""
                              <b>🎁 Введите цвет товара для добавления в корзину</b>
                              ▶ <code>{get_position['position_colors']}</code>
                              ➖➖➖➖➖➖➖➖➖➖
                              🎁 Пункт: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}руб.</code>
                              """))


# Выбор размера товара для корзины
@dp.message_handler(state="cart_item_color")
async def user_purchase_select_color(message: Message, state: FSMContext):
    position_id = (await state.get_data())['here_cache_position_id']
    get_position = get_positionx(position_id=position_id)

    if message.text in get_position['position_colors']:
        await state.update_data(changed_color=message.text)

        await state.set_state("cart_item_size")

        await message.answer(ded(f"""
                                  <b>🎁 Введите размер товара для добавления в корзину</b>
                                  ▶ <code>{get_position['position_sizes']}</code>
                                  ➖➖➖➖➖➖➖➖➖➖
                                  🎁 Пункт: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}руб.</code>
                                  """))
    else:
        await message.answer("<b>❌ Такого цвета нет в наличии</b>\n"
                             "Укажите цвет, который написан ниже:\n"
                             f"\t\t▶ <code>{get_position['position_colors']}</code>")


# Выбор размера товара для корзины
@dp.message_handler(state="cart_item_size")
async def user_purchase_select_size(message: Message, state: FSMContext):
    position_id = (await state.get_data())['here_cache_position_id']
    get_position = get_positionx(position_id=position_id)

    if message.text in get_position['position_sizes']:
        await state.update_data(changed_size=message.text)

        await state.set_state("cart_here_item_count")

        await message.answer(ded(f"""
                       ➖➖➖➖➖➖➖➖➖➖
                       🎁 Введите количество товаров для добавления в корзину
                       ▶ От <code>1</code> до <code>100</code>
                       ➖➖➖➖➖➖➖➖➖➖
                       🎁 Пункт: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}руб.</code>
                       """))
    else:
        await message.answer("<b>Такого размера нет в наличии</b>\n"
                             "Укажите размер, который написан ниже:\n"
                             f"\t\t▶ <code>{get_position['position_sizes']}</code>")


# Принятие количества товаров для корзины
@dp.message_handler(state="cart_here_item_count")
async def user_purchase_select_count(message: Message, state: FSMContext):
    position_id = (await state.get_data())['here_cache_position_id']
    get_select_color = (await state.get_data())['changed_color']
    get_select_size = (await state.get_data())['changed_size']

    get_position = get_positionx(position_id=position_id)

    send_message = ded(f"""
                   ➖➖➖➖➖➖➖➖➖➖
                   🎁 Введите количество товаров для добавления в корзину
                   ▶ От <code>1</code> до <code>100</code>
                   ➖➖➖➖➖➖➖➖➖➖
                   🎁 Пункт: <code>{get_position['position_name']}</code> - <code>{get_position['position_price']}руб.</code>
                   """)

    if message.text.isdigit():
        get_count = int(message.text)
        amount_pay = int(get_position['position_price']) * get_count

        if 1 <= get_count <= 100:
            await state.finish()
            await message.answer(ded(f"""
                                 <b>🎁 Вы действительно хотите добавить товар(ы) в корзину?</b>
                                 ➖➖➖➖➖➖➖➖➖➖
                                 🎁 Пункт: <code>{get_position['position_name']}</code>
                                 📦 Количество: <code>{get_count}шт</code>
                                 🎨 Цвет: <code>{get_select_color}</code>
                                 📏 Размер: <code>{get_select_size}</code>
                                 💰 Сумма для добавления в корзину: <code>{amount_pay}руб.</code>
                                 """),
                                 reply_markup=products_confirm_add(position_id, get_count, get_select_color, get_select_size))
        else:
            await message.answer(f"<b>❌ Неправильное количество товаров.</b>\n" + send_message)
    else:
        await message.answer(f"<b>❌ Данные были введены неправильно.</b>\n" + send_message)


##############################################################################################
########################################### ПРОМОКОДЫ ##########################################
# Активирование промокода
@dp.callback_query_handler(text_startswith="activation_promocode", state="*")
async def activation_promocode(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await state.set_state("promocode_name")

    await call.message.answer("🎫 Введите название промокода")


@dp.message_handler(state="promocode_name")
async def promocode_name_get(message: Message, state: FSMContext):
    await state.update_data(promocode_name=message.text)

    async with state.proxy() as data:
        promocode_name = data['promocode_name']

        await state.finish()

        prom = get_promocode(promocode_name=promocode_name)
        purchasex = get_purchasex(user_id=message.from_user.id)

        if prom is not None:
            prom_user = get_promocode_activation_user(promocode_name=promocode_name)
            if prom_user is None:
                if prom['promocode_first_buy'] == "yes":
                    if purchasex is not None:
                        await message.answer(
                            "<b>❌ Этот промокод распространяется только на первую покупку, вы уже делали покупки в данном магазине</b>")
                else:
                    if prom['promocode_activation_count'] == 0:
                        if prom['promocode_valid_period'] == '00.00.00':
                            await message.answer(
                                "<b>❌ Количество активаций этого промокода закончилось</b>")
                        else:
                            if prom['promocode_activation_count'] == 0:
                                if prom['promocode_valid_period'] == f'{day}.{month}.{years}':
                                    await message.answer("<b>❌ Время действия данного промокода истеко</b>")
                    else:
                        new_prom_activation_count = prom['promocode_activation_count'] - 1
                        update_promocode(prom['promocode_name'], promocode_activation_count=new_prom_activation_count)
                        add_promocode_activation_user(message.from_user.id, prom['promocode_name'], 1)
                        update_userx(message.from_user.id, user_promocode=prom['promocode_name'])

                        await message.answer("<b>✅ Промокод был успешно активирован, он будет применен автоматически при следующей покупке</b>")
            else:
                if prom['promocode_one_client'] == "yes":
                    if prom_user['activation_count'] == 1:
                        await message.answer("<b>❌ Этот промокод одноразовый, вы уже использовали свою попытку</b>")
                else:
                    if prom['promocode_first_buy'] == "yes":
                        if purchasex is not None:
                            await message.answer("<b>❌ Этот промокод распространяется только на первую покупку, вы уже делали покупки в данном магазине</b>")
                    else:
                        if prom['promocode_activation_count'] == 0:
                            if prom['promocode_valid_period'] == '00.00.00':
                                await message.answer(
                                    "<b>❌ Количество активаций этого промокода закончилось</b>")
                            else:
                                if prom['promocode_activation_count'] == 0:
                                    if prom['promocode_valid_period'] == f'{day}.{month}.{years}':
                                        await message.answer("<b>❌ Время действия данного промокода истеко</b>")
                        else:
                            new_activation_count = prom_user['activation_count'] + 1
                            new_prom_activation_count = prom['promocode_activation_count'] - 1
                            update_promocode_activation_user(message.from_user.id, activation_count=new_activation_count)
                            update_promocode(prom['promocode_name'], promocode_activation_count=new_prom_activation_count)
                            update_userx(message.from_user.id, user_promocode=prom['promocode_name'])

                            await message.answer(
                                "<b>✅ Промокод был успешно активирован, он будет применен автоматически при следующей покупке</b>")
        else:
            await message.answer("<b>❌ Промокода с данным названием не существует</b>")
