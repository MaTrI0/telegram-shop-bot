# - *- coding: utf- 8 - *-
from contextlib import suppress

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import CantParseEntities, MessageCantBeDeleted

from tgbot.data.loader import dp
from tgbot.keyboards.inline_admin import category_edit_open_finl, position_edit_open_finl, category_edit_delete_finl, \
    position_edit_delete_finl, position_edit_cancel_finl, category_edit_cancel_finl
from tgbot.keyboards.inline_all import category_remove_confirm_inl, position_remove_confirm_inl, \
    close_inl
from tgbot.keyboards.inline_page import *
from tgbot.keyboards.inline_promocode import promocodes_create_swipe_fp, promocodes_type_change, \
    promocode_create_cancel_finl, promocode_create_first_buy, promocode_create_one_client, promocode_create_confirm, \
    promocode_edit_menu, promocode_delete_confirm
from tgbot.keyboards.reply_all import menu_frep, promocodes_frep
from tgbot.services.api_sqlite import *
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import get_position_admin


# Создание нового промокода
@dp.message_handler(IsAdmin(), text="🎟 Создать промокод ➕", state="*")
async def promocodes_create(message: Message, state: FSMContext):
    await state.finish()

    # await state.set_state("here_promocode_name")
    await message.answer("<b>🎟 Укажите, на какую категорию товара будет распространяться промокод</b>", reply_markup=promocodes_create_swipe_fp(0))


# Выбор категории на которую распространяется промокод
@dp.callback_query_handler(IsAdmin(), text_startswith="promocodes_create_open:", state="*")
async def promocode_create_open(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]

    await state.update_data(here_cache_category_id=int(category_id))

    get_positions = len(get_positionsx(category_id=category_id))
    get_category = get_categoryx(category_id=category_id)

    await call.message.edit_text(f"<b>🗃 Выбранная категория: <code>{get_category['category_name']}</code></b>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 f"📁 Количество товаров: <code>{get_positions}шт</code>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "🎟 Укажите тип промокода кнопкой ниже: ",
                                 reply_markup=promocodes_type_change(category_id)
                                 )


# Обработка выбранного типа промокода
@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_type:", state="*")
async def promocode_change_type(call: CallbackQuery, state: FSMContext):
    code_type = call.data.split(":")[1]

    await state.update_data(here_change_promocode_type=code_type)
    await state.set_state("here_promocode_name")

    await call.message.edit_text("🎟 Укажите название промокода (кодовое слово) 🏷")


# Обработка названия промокода
@dp.message_handler(IsAdmin(), state="here_promocode_name")
async def here_promocode_name_get(message: Message, state: FSMContext):
    if len(message.text) <= 50:
        await state.update_data(here_promocode_name=clear_html(message.text))

        await state.set_state("here_activation_count")
        await message.answer("<b>🎟 Укажите количество активации на данный промокод</b>\n"
                             "❕ Пришлите <code>0</code> чтобы активации промокода были бесконечными."
                             )
    else:
        await message.answer("<b>❌ Название не может превышать 50 символов.</b>\n"
                             "🎟 Укажите название промокода (кодовое слово) 🏷",
                             reply_markup=promocode_create_cancel_finl())


# Обработка количества активаций промокода
@dp.message_handler(IsAdmin(), state="here_activation_count")
async def here_promocode_activation_count(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            if int(message.text) == 0:
                await state.update_data(here_activation_count=int(message.text))

                await state.set_state("here_promo_code_validity_period")
                await message.answer("<b>🎟 Укажите время до которого будет действителен промокод, пример: <code>26.01.23</code></b>")
            else:
                await state.update_data(here_activation_count=int(message.text))

                await state.set_state("here_minimum_order_amount")
                await message.answer("<b>🎟 Укажите минимальную сумму заказа при которой станет активным промокод</b>\n"
                                     "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                     "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                                     "❕ Пришлите <code>0</code> чтобы отключить ограничение на минимальную сумму заказа."
                                     )
        else:
            await message.answer(
                "<b>❌ Количество активаций промокода не может быть меньше 1 или больше 10 000 000.</b>\n"
                "🎟 Укажите количество активации на данный промокод\n"
                "❕ Пришлите <code>0</code> чтобы активации промокода были бесконечными.",
                reply_markup=promocode_create_cancel_finl())
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "🎟 Укажите количество активации на данный промокод\n"
                             "❕ Пришлите <code>0</code> чтобы активации промокода были бесконечными.",
                             reply_markup=promocode_create_cancel_finl())


# Обработка минимальной суммы заказа товаров
@dp.message_handler(IsAdmin(), state="here_promo_code_validity_period")
async def here_promocode_activation_count(message: Message, state: FSMContext):
    if len(message.text) == 8:
        by1 = message.text.split(".")[0]
        by2 = message.text.split(".")[1]
        by3 = message.text.split(".")[2]

        print(f'{by1}, {by2}, {by3}')

        if by1.isdigit() and by2.isdigit() and by3.isdigit():
            await state.update_data(here_promo_code_validity_period=message.text)

            await state.set_state("here_minimum_order_amount")
            await message.answer("<b>🎟 Укажите минимальную сумму заказа при которой станет активным промокод</b>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                                 "❕ Пришлите <code>0</code> чтобы отключить ограничение на минимальную сумму заказа."
                                 )
        else:
            await message.answer(
                "<b>❌ Дата указана не верно, на месте цифр буквы.</b>\n"
                "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                "🎟 Укажите время до которого будет действителен промокод, пример: <code>26.01.23</code>",
                reply_markup=promocode_create_cancel_finl())
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>"
                             "🎟 Укажите время до которого будет действителен промокод, пример: <code>04.02.23</code>",
                             reply_markup=promocode_create_cancel_finl())


# Обработка минимальной суммы заказа товаров
@dp.message_handler(IsAdmin(), state="here_minimum_order_amount")
async def here_promocode_activation_count(message: Message, state: FSMContext):
    async with state.proxy() as data:
        promo_type = data['here_change_promocode_type']

        if message.text.isdigit():
            if 0 <= int(message.text) <= 10000000:
                await state.update_data(here_minimum_order_amount=int(message.text))

                if promo_type == "currency":
                    await state.set_state("here_discount_amount_currency")
                    await message.answer("<b>🎟 Укажите скидку промокода в валюте</b>\n"
                                         "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         "<code>Например при значении 100, от общей суммы заказа будет отнято 100 грн. То есть, если сумма была 400, то после применения скидки, сумма станет 300.</code>\n"
                                         "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                                         )
                elif promo_type == "percentage":
                    await state.set_state("here_discount_amount_percentage")
                    await message.answer("<b>🎟 Укажите скидку промокода в процентах</b>\n"
                                         "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         "<code>Например, для значения 10. Скидка будет 10% т.е. при конечной стоимости заказа 100, после применения промокода стоимость заказа станет 90. При значении 100 заказ будет выдан бесплатно!!!</code>\n"
                                         "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                                         )
            else:
                await message.answer(
                    "<b>❌ Минимальная сумма не может быть меньше 1 или больше 10 000 000.</b>\n"
                    "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    "🎟 Укажите минимальную сумму заказа при которой станет активным промокод\n"
                    "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                    "❕ Пришлите <code>0</code> чтобы отключить ограничение на минимальную сумму заказа.",
                    reply_markup=promocode_create_cancel_finl())
        else:
            await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "🎟 Укажите минимальную сумму заказа при которой станет активным промокод\n"
                                 "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                                 "❕ Пришлите <code>0</code> чтобы отключить ограничение на минимальную сумму заказа.",
                                 reply_markup=promocode_create_cancel_finl())


@dp.message_handler(IsAdmin(), state="here_discount_amount_currency")
async def here_promocode_discount_amount_currency(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.update_data(here_discount_amount_currency=int(message.text))

            await message.answer("🎟 Промокод будет распространяться только на первую покупку?",
                                 reply_markup=promocode_create_first_buy())
        else:
            await message.answer("❌ Валютное значение промокода не может быть меньше 0 и больше 10 000 000 000."
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "🎟 Укажите скидку промокода в валюте\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "<code>Например при значении 100, от общей суммы заказа будет отнято 100 грн. То есть, если сумма была 400, то после применения скидки, сумма станет 300.</code>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                                 reply_markup=promocode_create_cancel_finl()
                                 )
    else:
        await message.answer("<b>❌ Данные были введены неправильно. <code>Значение должно быть числовым.</code></b>\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             "🎟 Укажите скидку промокода в валюте\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             "<code>Например при значении 100, от общей суммы заказа будет отнято 100 грн. То есть, если сумма была 400, то после применения скидки, сумма станет 300.</code>\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                             reply_markup=promocode_create_cancel_finl())


@dp.message_handler(IsAdmin(), state="here_discount_amount_percentage")
async def here_promocode_discount_amount_currency(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 100:
            await state.update_data(here_discount_amount_percentage=int(message.text))

            await message.answer("<b>🎟 Промокод будет распространяться только на первую покупку?</b>",
                                 reply_markup=promocode_create_first_buy())
        else:
            await message.answer(
                "<b>❌ Процентное значение не может быть меньше 0 и больше 100.</b>\n"
                "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                "🎟 Укажите скидку промокода в процентах\n"
                "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                "<code>Например, для значения 10. Скидка будет 10% т.е. при конечной стоимости заказа 100, после применения промокода стоимость заказа станет 90. При значении 100 заказ будет выдан бесплатно!!!</code>\n"
                "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                reply_markup=promocode_create_cancel_finl())
    else:
        await message.answer("<b>❌ Данные были введены неправильно. <code>Значение должно быть числовым.</code></b>\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             "🎟 Укажите скидку промокода в процентах\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             "<code>Например, для значения 10. Скидка будет 10% т.е. при конечной стоимости заказа 100, после применения промокода стоимость заказа станет 90. При значении 100 заказ будет выдан бесплатно!!!</code>\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                             reply_markup=promocode_create_cancel_finl())


@dp.callback_query_handler(IsAdmin(), text_startswith="first_buy:", state="*")
async def promocode_change_first_buy(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]

    await state.update_data(here_change_first_buy=data)

    await call.message.edit_text("<b>🎟 Запретить использование промокода одному клиенту несколько раз?</b>",
                                 reply_markup=promocode_create_one_client())


@dp.callback_query_handler(IsAdmin(), text_startswith="one_client:", state="*")
async def promocode_change_one_client(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        res = call.data.split(":")[1]
        category_id = data['here_cache_category_id']
        promocode_type = data['here_change_promocode_type']
        promocode_name = data['here_promocode_name']
        activation_count = data['here_activation_count']
        print(f"{activation_count}")
        if activation_count == 0:
            promocode_valid_period = data['here_promo_code_validity_period']
        minimum_order_amount = data['here_minimum_order_amount']
        if promocode_type == "currency":
            discount_amount_currency = data['here_discount_amount_currency']
            promocode_type_ = "валютный"
        elif promocode_type == "percentage":
            discount_amount_percentage = data['here_discount_amount_percentage']
            promocode_type_ = "процентный"
        first_buy = data['here_change_first_buy']
        one_client = res

        get_positions = len(get_positionsx(category_id=category_id))
        get_category = get_categoryx(category_id=category_id)

        await state.update_data(here_change_one_client=res)

        def test(count):
            if count == 0:
                return f"🎟 Период действия промокода: <code>{promocode_valid_period}</code>"
            else:
                return f"🎟 Количество активаций на промокод: <code>{activation_count}</code>"

        def test2(type_):
            if type_ == "currency":
                return f"🎟 Валютная скидка: <code>{discount_amount_currency}</code>"
            elif type_ == "percentage":
                return f"🎟 Процентная скидка: <code>{discount_amount_percentage}</code>"

        await call.message.edit_text("<b>Вы действительно хотите создать промокод?</b>\n"
                                     "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                     f"🗃 Выбранная категория: <code>{get_category['category_name']}</code>\n"
                                     f"📁 Количество товаров: <code>{get_positions}шт</code>\n"
                                     f"🎟 Тип промокода: <code>{promocode_type_}</code>\n"
                                     f"🎟 Название промокода: <code>{promocode_name}</code>\n"
                                     f"{test(activation_count)}\n"
                                     f"🎟 Минимальная сумма заказа: <code>{minimum_order_amount}</code>\n"
                                     f"{test2(promocode_type)}\n"
                                     f"🎟 Промокод действует только на первую покупку: <code>{first_buy}</code>\n"
                                     f"🎟 Пользователь может использовать промокод только один раз: <code>{one_client}</code>\n",
                                     reply_markup=promocode_create_confirm())


@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_create_confirm:", state="*")
async def get_promocode_create_confirm(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        response = call.data.split(":")[1]
        print(f"{data}")
        category_id = data['here_cache_category_id']
        promocode_name = data['here_promocode_name']
        promocode_type = data['here_change_promocode_type']
        activation_count = data['here_activation_count']
        if activation_count == 0:
            promocode_valid_period = data['here_promo_code_validity_period']
        else:
            promocode_valid_period = "00.00.00"
        minimum_order_amount = data['here_minimum_order_amount']
        if promocode_type == "currency":
            discount_amount_currency = data['here_discount_amount_currency']
            discount_amount_percentage = 0
        elif promocode_type == "percentage":
            discount_amount_percentage = data['here_discount_amount_percentage']
            discount_amount_currency = 0
        first_buy = data['here_change_first_buy']
        one_client = data['here_change_one_client']

        if response == "yes":
            await state.finish()

            add_promocode(category_id, promocode_name, promocode_type, activation_count, minimum_order_amount, discount_amount_currency, discount_amount_percentage,
                          first_buy, one_client, promocode_valid_period)

            await call.message.delete()
            await call.message.answer("🎟 Промокод успешно создан, для его редактирования нажмите соответствующую кнопку в меню", reply_markup=menu_frep(call.from_user.id))
        else:
            await state.finish()
            await call.message.delete()
            await call.message.answer("<b>🎟 Вы отменили создание этого промокода.</b>", reply_markup=promocodes_frep())


# Страница выбора категорий для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="promocodes_create_swipe:", state="*")
async def product_category_edit_swipe(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🗃 Выберите категорию на которую будет распространяться промокод 🖍</b>",
                                 reply_markup=promocodes_create_swipe_fp(remover))


# отмена создания промокода
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_cancel", state="*")
async def product_category_edit_swipe(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("🔸 Бот готов для использования.\n",
                              reply_markup=menu_frep(call.from_user.id))


#######################################################################
#################### Редактирование промокода #########################
# Обработка нажатия кнопки редактирования
@dp.message_handler(IsAdmin(), text="🎟 Редактировать промокод 🖍", state="*")
async def promocodes_edit(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("get_promocode_name")
    await message.answer("<b>Введите название промокода</b>")


# Отправка меню с кнопка на редактирование
@dp.message_handler(IsAdmin(), state="get_promocode_name")
async def promocode_edit_answer_menu(message: Message, state: FSMContext):
    prom = get_promocode(promocode_name=message.text)

    if prom is not None:
        await state.finish()
        amount = 0
        if prom['promocode_type'] == "currency":
            amount = prom['promocode_discount_amount_currency']
        elif prom['promocode_type'] == "percentage":
            amount = prom['promocode_discount_amount_percentage']

        await message.answer("<b>🎟 Редактирование промокода</b>\n"
                             f"Название промокода: <code>{prom['promocode_name']}</code>\n"
                             f"Минимальная сумма заказа: <code>{prom['promocode_minimum_order_amount']}</code>\n"
                             f"Скидка: <code>{amount}</code>\n"
                             f"Количество активаций: <code>{prom['promocode_activation_count']}</code>\n",
                             reply_markup=promocode_edit_menu(prom['promocode_name']))
    else:
        await message.answer("<b>Этого промокода не существует</b>\n"
                             "Попробуйте один раз.",
                             reply_markup=promocode_create_cancel_finl())


# Редактирование названия промокода
@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_edit_name:", state="*")
async def edit_promocode_name(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer(cache_time=60)
    await call.message.delete()
    prom_name = call.data.split(":")[1]

    await state.update_data(prom_name=prom_name)

    await state.set_state(f"promocode_edit_name_get")
    await call.message.answer("Введите новое название промокода")


# Принятие нового названия промокода
@dp.message_handler(IsAdmin(), state='promocode_edit_name_get')
async def edit_promocode_name_get(message: Message, state: FSMContext):
    back_prom_name = (await state.get_data())['prom_name']

    update_promocode(back_prom_name, promocode_name=message.text)
    await state.finish()

    await message.answer(f"Название промокода было изменено на <code>{message.text}</code>", reply_markup=promocodes_frep())


# Редактирования минимальной суммы заказа для активации промокода
@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_edit_minimum_order:", state="*")
async def edit_promocode_order(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer(cache_time=60)
    await call.message.delete()
    prom_name = call.data.split(":")[1]

    await state.update_data(prom_name=prom_name)

    await state.set_state(f"promocode_edit_minimum_order")
    await call.message.answer("🎟 Введите новую минимальную цену при которой промокод станет активным\n"
                              "<code>Введите 0 чтобы убрать ограничение суммы</code>")


# Принятие новой минимальной суммы заказа для активации промокода
@dp.message_handler(IsAdmin(), state="promocode_edit_minimum_order")
async def edit_promocode_order_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            prom_name = (await state.get_data())['prom_name']

            update_promocode(prom_name, promocode_minimum_order_amount=message.text)
            await state.finish()
            await message.answer("Минимальная сумма заказа при которой станет активным промокод была успешно изменена", reply_markup=promocodes_frep())
        else:
            await message.answer(
                "<b>❌ Минимальная сумма не может быть меньше 1 или больше 10 000 000.</b>\n"
                "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                "🎟 Укажите минимальную сумму заказа при которой станет активным промокод\n"
                "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                "❕ Отправьте <code>0</code> чтобы отключить ограничение на минимальную сумму заказа.",
                reply_markup=promocode_create_cancel_finl())
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             "🎟 Укажите минимальную сумму заказа при которой станет активным промокод\n"
                             "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                             "❕ Отправьте <code>0</code> чтобы отключить ограничение на минимальную сумму заказа.",
                             reply_markup=promocode_create_cancel_finl())


# Редактирование скидки, которую даёт промокод
@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_edit_discount:", state="*")
async def edit_promocode_discount(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer(cache_time=60)
    await call.message.delete()
    prom_name = call.data.split(":")[1]
    prom = get_promocode(promocode_name=prom_name)

    await state.update_data(prom_name=prom_name)

    if prom['promocode_type'] == "currency":
        await state.set_state(f"promocode_edit_discount")
        await call.message.answer("<b>🎟 Укажите новую скидку промокода в валюте</b>\n"
                                  "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                  "<code>Например при значении 100, от общей суммы заказа будет отнято 100 грн. То есть, если сумма была 400, то после применения скидки, сумма станет 300.</code>\n"
                                  "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                  "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                                  )
    elif prom['promocode_type'] == "percentage":
        await state.set_state(f"promocode_edit_discount")
        await call.message.answer("<b>🎟 Укажите новую скидку промокода в процентах</b>\n"
                                  "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                  "<code>Например, для значения 10. Скидка будет 10% т.е. при конечной стоимости заказа 100, после применения промокода стоимость заказа станет 90. При значении 100 заказ будет выдан бесплатно!!!</code>\n"
                                  "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                  "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n"
                                  )


# Принятия данных для редактирования скидки, которую даёт промокод
@dp.message_handler(IsAdmin(), state="promocode_edit_discount")
async def edit_promocode_discount_get(message: Message, state: FSMContext):
    prom_name = (await state.get_data())['prom_name']
    prom = get_promocode(promocode_name=prom_name)

    if prom['promocode_type'] == "currency":
        if message.text.isdigit():
            if 0 <= int(message.text) <= 10000000:
                update_promocode(prom_name, promocode_discount_amount_currency=message.text)
                await state.finish()
                await message.answer("🎟 Новая валютная скидка промокода сохранена", reply_markup=promocodes_frep())
            else:
                await message.answer("❌ Валютное значение скидки не может быть меньше 0 и больше 10 000 000."
                                     "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                     "🎟 Укажите скидку промокода в валюте\n"
                                     "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                     "<code>Например при значении 100, от общей суммы заказа будет отнято 100 грн. То есть, если сумма была 400, то после применения скидки, сумма станет 300.</code>\n"
                                     "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                     "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                                     reply_markup=promocode_create_cancel_finl()
                                     )
        else:
            await message.answer("<b>❌ Данные были введены неправильно. <code>Значение должно быть числовым.</code></b>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "🎟 Укажите скидку промокода в валюте\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "<code>Например при значении 100, от общей суммы заказа будет отнято 100 грн. То есть, если сумма была 400, то после применения скидки, сумма станет 300.</code>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                                 reply_markup=promocode_create_cancel_finl())
    elif prom['promocode_type'] == "percentage":
        if message.text.isdigit():
            if 0 <= int(message.text) <= 100:
                update_promocode(prom_name, promocode_discount_amount_percentage=message.text)
                await state.finish()
                await message.answer("<b>🎟 Новая процентная скидка промокода сохранена</b>", reply_markup=promocodes_frep())
            else:
                await message.answer(
                    "<b>❌ Процентное значение скидки не может быть меньше 0 и больше 100.</b>\n"
                    "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    "🎟 Укажите скидку промокода в процентах\n"
                    "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    "<code>Например, для значения 10. Скидка будет 10% т.е. при конечной стоимости заказа 100, после применения промокода стоимость заказа станет 90. При значении 100 заказ будет выдан бесплатно!!!</code>\n"
                    "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                    reply_markup=promocode_create_cancel_finl())
        else:
            await message.answer("<b>❌ Данные были введены неправильно. <code>Значение должно быть числовым.</code></b>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "🎟 Укажите скидку промокода в процентах\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "<code>Например, для значения 10. Скидка будет 10% т.е. при конечной стоимости заказа 100, после применения промокода стоимость заказа станет 90. При значении 100 заказ будет выдан бесплатно!!!</code>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 "<code>Учитывайте, что пользователь может оплатить за раз только один товар.</code>\n",
                                 reply_markup=promocode_create_cancel_finl())


# Редактирования количества активаций промокода
@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_edit_activation_count:", state="*")
async def edit_promocode_order(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer(cache_time=60)
    await call.message.delete()
    prom_name = call.data.split(":")[1]

    await state.update_data(prom_name=prom_name)

    await state.set_state(f"promocode_edit_activation_count")
    await call.message.answer("🎟 Введите новое количество ативаций промокода")


# Принятие нового количества активаций промокода
@dp.message_handler(IsAdmin(), state="promocode_edit_activation_count")
async def edit_promocode_order_get(message: Message, state: FSMContext):
    prom_name = (await state.get_data())['prom_name']

    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            if int(message.text) == 0:
                await message.answer("<b>🎟 Если вы хотите создать бессрочный промокод, то вам в меню создания промокдов</b>\n"
                                     "<code>Введите новое количество активаций на промокод</code>")
            else:
                update_promocode(prom_name, promocode_activation_count=message.text)
                await state.finish()
                await message.answer("<b>🎟 Количество активаций промокода, успешно изменено</b>", reply_markup=promocodes_frep())
        else:
            await message.answer(
                "<b>❌ Количество активаций промокода не может быть меньше 1 или больше 10 000 000.</b>\n"
                "🎟 Укажите количество активации на данный промокод",
                reply_markup=promocode_create_cancel_finl())
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "🎟 Укажите количество активации на данный промокод",
                             reply_markup=promocode_create_cancel_finl())


# Удаление промокода
@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_delete:", state="*")
async def promocode_delete(call: CallbackQuery, state: FSMContext):
    prom_name = call.data.split(":")[1]
    await call.message.delete()

    remove_promocode(promocode_name=prom_name)
    await call.answer("Промокод был успешно удален", False)
    await call.message.delete()


# Удаление всех промокодов
@dp.message_handler(IsAdmin(), text="🎟 Удалить все промокоды ❌", state="*")
async def promocodes_edit(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>Вы уверены, что хотите удалить все промокоды?</b>",
                         reply_markup=promocode_delete_confirm())


@dp.callback_query_handler(IsAdmin(), text_startswith="promocode_delete_confirm:", state="*")
async def promocode_delete(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]

    if data == "yes":
        clear_promocode()
        clear_promocode_activation_user()
        await call.answer("Все промокоды были успешно удалены", False)
        await call.message.delete()
    else:
        await call.message.answer("Вы отменили удаление всех промокодов", reply_markup=menu_frep(call.from_user.id))
        await call.message.delete()
