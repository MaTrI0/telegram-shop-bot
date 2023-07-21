from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ShippingOption, ShippingQuery, LabeledPrice, PreCheckoutQuery, CallbackQuery
from aiogram.types.message import ContentType

from tgbot.keyboards.inline_all import profile_open_inl
from tgbot.keyboards.reply_all import menu_frep
from tgbot.services.api_sqlite import *
from tgbot.data.config import PAYMENTS_TOKEN, BOT_TECH_CHAT_ID
from tgbot.data.loader import dp, bot
from tgbot.utils.const_functions import get_unix, get_date, ded
from tgbot.utils.misc_functions import open_profile_user

shipping_options = []
receipt = get_unix()
buy_time = get_date()


# Подтверждение покупки товара
@dp.callback_query_handler(text_startswith="pay_cart:", state="*")
async def start_pay_cart(call: CallbackQuery, state: FSMContext):
    shipping_options.clear()
    get_action = call.data.split(":")[1]
    buy_item_count = 0

    get_cart_items = get_user_cart(user_id=call.from_user.id)

    for item in get_cart_items:
        buy_item_count += 1

    if get_action == "yes":
        await state.finish()
        buy_product_count = 0
        buy_position_cost = 0
        PRICES = []

        courier_delivery_price = 0
        by_mail_russia_price = 0
        transport_company_price = 0

        if not get_cart_items:
            return await call.answer(f"🛒 Ваша корзина пуста :(")

        for item in get_cart_items:
            get_position = get_positionx(position_id=item.get("position_id"))
            amount_pay = int(item.get('position_price'))
            PRICES.append(LabeledPrice(label=f'{get_position["position_name"]}', amount=(amount_pay * 100)))

            buy_product_count += item.get("position_count")
            buy_position_cost += item.get("position_price")

            courier_delivery_price = get_position["courier_delivery_price"]
            by_mail_russia_price = get_position["by_mail_russia_price"]
            transport_company_price = get_position["transport_company_price"]

        COURIER_DELIVERY_OPTIONS = ShippingOption(
            id='courier_delivery',
            title='Курьерская доставка'
        ).add(LabeledPrice("Курьерская доставка", (courier_delivery_price * 100)))
        shipping_options.append(COURIER_DELIVERY_OPTIONS)

        BY_MAIL_RUSSIA_OPTIONS = ShippingOption(
            id='by_mail_russia',
            title='Почтой России'
        ).add(LabeledPrice("Почтой России", (by_mail_russia_price * 100)))
        shipping_options.append(BY_MAIL_RUSSIA_OPTIONS)

        TRANSPORT_COMPANY_OPTIONS = ShippingOption(
            id='transport_company',
            title='Транспортная компания'
        ).add(LabeledPrice("Транспортная компания", (transport_company_price * 100)))
        shipping_options.append(TRANSPORT_COMPANY_OPTIONS)

        await call.message.delete()

        await bot.send_invoice(call.message.chat.id,
                               title="Оплата корзины",
                               description='В этом окне вы можете все товары имеющиеся в корзине.',
                               provider_token=PAYMENTS_TOKEN,
                               currency='rub',
                               need_email=True,
                               need_phone_number=True,
                               need_shipping_address=True,
                               is_flexible=True,
                               prices=PRICES,
                               start_parameter='cart-payment',
                               payload='test-invoice-payload',
                               )
    else:
        if buy_item_count >= 1:
            await call.message.edit_text(open_profile_user(call.from_user.id), reply_markup=profile_open_inl(buy_item_count))
        else:
            await call.message.edit_text("<b>❌ Вы отменили оплату корзины.</b>")


@dp.shipping_query_handler(lambda q: True)
async def shiping_process(shiping_query: ShippingQuery):
    if shiping_query.shipping_address.country_code != "RU":
        return await bot.answer_shipping_query(
            shiping_query.id,
            ok=False,
            error_message="На данный момент доставка осуществляется только на территории России"
        )

    if shiping_query.shipping_address.city == 'Омск':
        PICKUP_OPTIONS = ShippingOption(
            id='pickup',
            title='Самовывоз'
        ).add(LabeledPrice("Самовывоз в Омске", (50 * 100)))
        shipping_options.append(PICKUP_OPTIONS)

    await bot.answer_shipping_query(
        shiping_query.id,
        ok=True,
        shipping_options=shipping_options
    )
    shipping_options.clear()


@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state='*')
async def successful_payment(message: Message, state: FSMContext):
    buy_item_count = 0
    buy_product_count = 0
    buy_position_cost = 0
    amount_pay = 0
    products = """"""
    await state.finish()

    get_cart_items = get_user_cart(user_id=message.from_user.id)
    get_user = get_userx(user_id=message.from_user.id)

    for item in get_cart_items:
        get_position = get_positionx(position_id=item.get("position_id"))
        products += f"\n<code>{get_position['position_name']} | {item.get('position_count')}шт | {item.get('position_price')}руб.</code>"

        buy_item_count += 1
        buy_product_count += item.get("position_count")
        buy_position_cost += item.get("position_price")

    add_purchasex(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt, buy_product_count,
                  buy_position_cost, None, None,
                  f"Оплата корзины-{receipt}", buy_time, receipt, None, None)

    remove_cart(user_id=message.from_user.id)

    await bot.send_message(
        message.chat.id,
        ded(f"""
                <b>✅ Вы успешно купили товар(ы)</b>
                ➖➖➖➖➖➖➖➖➖➖
                🧾 Чек: <code>#{receipt}</code>
                🛒 Товары в корзине успешно оплачены!
                Количество купленных товаров: <code>{buy_item_count}</code>
                Общая сумма покупки: <code>{buy_position_cost}</code>
                Способ доставки: <code>{message.successful_payment.shipping_option_id}</code>
                🕰 Дата приобретения: <code>{buy_time}</code>
            """),
        reply_markup=menu_frep(message.from_user.id)
    )

    await message.bot.send_message(chat_id=BOT_TECH_CHAT_ID,
                                   text=ded(f"""
                                            <b>✅ Пользователь <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> успешно купил товар(ы)</b>
                                            ➖➖➖➖➖➖➖➖➖➖
                                            🧾 Чек: <code>#{receipt}</code>

                                            🎁 Товары: {products}

                                            Способ доставки: <code>{message.successful_payment.shipping_option_id}</code>
                                            Данные для связи: \n\t Телефон: <code>{message.successful_payment.order_info.phone_number}</code> \n\t Email: <code>{message.successful_payment.order_info.email}</code>
                                            Полный адрес доставки: \n\t\t Адрес 1: <code>{message.successful_payment.order_info.shipping_address.street_line1}</code> \n\t\t Адрес 2: <code>{message.successful_payment.order_info.shipping_address.street_line2}</code> \n\t\t Страна: <code>{message.successful_payment.order_info.shipping_address.country_code}</code> \n\t\t Индекс: <code>{message.successful_payment.order_info.shipping_address.post_code}</code> \n\t\t Область: <code>{message.successful_payment.order_info.shipping_address.state}</code> \n\t\t Город: <code>{message.successful_payment.order_info.shipping_address.city}</code> \n\t\t
                                            ➖➖➖➖➖➖➖➖➖➖
                                            🕰 Дата покупки: <code>{buy_time}</code>
                                        """),)

