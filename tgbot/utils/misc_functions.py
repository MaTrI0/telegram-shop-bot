# - *- coding: utf- 8 - *-
import asyncio
import json

from aiogram import Dispatcher
from bs4 import BeautifulSoup

from tgbot.data.config import get_admins, BOT_VERSION, BOT_DESCRIPTION, PATH_DATABASE
from tgbot.data.loader import bot
from tgbot.keyboards.reply_all import menu_frep
from tgbot.services.api_session import AsyncSession
from tgbot.services.api_sqlite import get_settingsx, update_settingsx, get_userx, get_purchasesx, get_all_positionsx, \
    update_positionx, get_all_categoriesx, get_all_purchasesx, get_all_usersx, \
    get_positionx, get_categoryx, get_user_cart
from tgbot.utils.const_functions import get_unix, convert_day, get_date, ded


# Уведомление и проверка обновления при запуске бота
async def on_startup_notify(dp: Dispatcher, aSession: AsyncSession):
    if len(get_admins()) >= 1:
        await send_admins(ded(f"""
                          <b>✅ Бот был успешно запущен</b>
                          ➖➖➖➖➖➖➖➖➖➖
                          {BOT_DESCRIPTION}
                          ➖➖➖➖➖➖➖➖➖➖
                          <code>❗ Данное сообщение видят только администраторы бота.</code>
                          """),
                          markup="default")


# Рассылка сообщения всем администраторам
async def send_admins(message, markup=None, not_me=0):
    for admin in get_admins():
        if markup == "default": markup = menu_frep(admin)

        try:
            if str(admin) != str(not_me):
                await bot.send_message(admin, message, reply_markup=markup, disable_web_page_preview=True)
        except:
            pass


# Автоматическая очистка ежедневной статистики после 00:00
async def update_profit_day():
    await send_admins(get_statisctics())

    update_settingsx(misc_profit_day=get_unix())


# Автоматическая очистка еженедельной статистики в понедельник 00:01
async def update_profit_week():
    update_settingsx(misc_profit_week=get_unix())


# Автобэкапы БД для админов
async def autobackup_admin():
    for admin in get_admins():
        with open(PATH_DATABASE, "rb") as document:
            try:
                await bot.send_document(admin,
                                        document,
                                        caption=f"<b>📦 AUTOBACKUP</b>\n"
                                                f"🕰 <code>{get_date()}</code>")
            except:
                pass


# Получение faq
def get_faq(user_id, send_message):
    get_user = get_userx(user_id=user_id)

    if "{user_id}" in send_message:
        send_message = send_message.replace("{user_id}", f"<b>{get_user['user_id']}</b>")
    if "{username}" in send_message:
        send_message = send_message.replace("{username}", f"<b>{get_user['user_login']}</b>")
    if "{firstname}" in send_message:
        send_message = send_message.replace("{firstname}", f"<b>{get_user['user_name']}</b>")

    return send_message


# Проверка на перенесение БД из старого бота в нового или указание токена нового бота
async def check_bot_data():
    get_login = get_settingsx()['misc_bot']
    get_bot = await bot.get_me()

    if get_login not in [get_bot.username, "None"]:
        get_positions = get_all_positionsx()

        for position in get_positions:
            update_positionx(position['position_id'], position_photo="")

    update_settingsx(misc_bot=get_bot.username)


# Получить информацию о позиции для админа
def get_position_admin(position_id):
    get_settings = get_settingsx()
    get_position = get_positionx(position_id=position_id)
    get_purchases = get_purchasesx(purchase_position_id=position_id)
    get_category = get_categoryx(category_id=get_position['category_id'])

    show_profit_amount_all, show_profit_amount_day, show_profit_amount_week = 0, 0, 0
    show_profit_count_all, show_profit_count_day, show_profit_count_week = 0, 0, 0
    text_description = "<code>Отсутствует ❌</code>"
    photo_text = "<code>Отсутствует ❌</code>"
    color_text = "<code>Отсутствует ❌</code>"
    size_text = "<code>Отсутствует ❌</code>"
    courier_delivery_text = "<code>Не доступно ❌</code>"
    by_mail_russia_text = "<code>Не доступно ❌</code>"
    transport_company_text = "<code>Не доступно ❌</code>"
    get_photo = None

    if len(get_position['position_photo']) >= 5:
        photo_text = "<code>Присутствует ✅</code>"
        get_photo = get_position['position_photo']

    if get_position['position_description'] != "0":
        text_description = f"\n{get_position['position_description']}"

    if get_position["position_colors"] != "":
        color_text = f"{get_position['position_colors']}"

    if get_position["position_sizes"] != "":
        size_text = f"{get_position['position_sizes']}"

    if get_position["courier_delivery_price"] != 0:
        courier_delivery_text = f"{get_position['courier_delivery_price']}руб."

    if get_position["by_mail_russia_price"] != 0:
        by_mail_russia_text = f"{get_position['by_mail_russia_price']}руб"

    if get_position["transport_company_price"] != 0:
        transport_company_text = f"{get_position['transport_company_price']}руб"

    for purchase in get_purchases:
        show_profit_amount_all += purchase['purchase_price']
        show_profit_count_all += purchase['purchase_count']

        if purchase['purchase_unix'] - get_settings['misc_profit_day'] >= 0:
            show_profit_amount_day += purchase['purchase_price']
            show_profit_count_day += purchase['purchase_count']
        if purchase['purchase_unix'] - get_settings['misc_profit_week'] >= 0:
            show_profit_amount_week += purchase['purchase_price']
            show_profit_count_week += purchase['purchase_count']

    # 📦 Кількість: < code > {int(get_position['position_count'])}шт < / code >

    get_message = ded(f"""
                  <b>📁 Товар: <code>{get_position['position_name']}</code></b>
                  ➖➖➖➖➖➖➖➖➖➖
                  🗃 Категория: <code>{get_category['category_name']}</code>
                  💰 Стоимость: <code>{get_position['position_price']}руб.</code>
                  🎨 Цвета: <code>{color_text}</code>
                  📏 Размеры: <code>{size_text}</code>
                  📦 Доставка курьером: <code>{courier_delivery_text}</code>
                  🏣 Доставка почтой России: <code>{by_mail_russia_text}</code>
                  🚚 Доставка транспортной компанией: <code>{transport_company_text}</code>
                  📸 Изображение: {photo_text}
                  📜 Описание: {text_description}

                  💸 Продажи за День: <code>{show_profit_count_day}шт</code> - <code>{show_profit_amount_day}руб.</code>
                  💸 Продажи за неделю: <code>{show_profit_count_week}шт</code> - <code>{show_profit_amount_week}руб.</code>
                  💸 Продажи за всё время: <code>{show_profit_count_all}шт</code> - <code>{show_profit_amount_all}руб.</code>
                  """)

    return get_message, get_photo


# Открытие своего профиля
def open_profile_user(user_id):
    get_purchases = get_purchasesx(user_id=user_id)
    get_user = get_userx(user_id=user_id)

    how_days = int(get_unix() - get_user['user_unix']) // 60 // 60 // 24
    count_items = sum([items['purchase_count'] for items in get_purchases])

    return ded(f"""
           <b>👤 Ваш профиль:</b>
           ➖➖➖➖➖➖➖➖➖➖
           🆔 ID: <code>{get_user['user_id']}</code>
           🎁 Куплено товаров: <code>{count_items}шт</code>
           🕰 Регистрация: <code>{get_user['user_date'].split(' ')[0]} ({convert_day(how_days)})</code>
           """)


# Открытие профиля при поиске
def open_profile_admin(user_id):
    get_purchases = get_purchasesx(user_id=user_id)
    get_user = get_userx(user_id=user_id)

    how_days = int(get_unix() - get_user['user_unix']) // 60 // 60 // 24
    count_items = sum([items['purchase_count'] for items in get_purchases])

    cart_item = 0
    get_user_cart_items = get_user_cart(user_id=user_id)

    if get_user_cart_items is None:
        pass
    else:
        for items in get_user_cart_items:
            cart_item += 1

    return ded(f"""
           <b>👤 Профиль пользователя: <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a></b>
           ➖➖➖➖➖➖➖➖➖➖
           🆔 ID: <code>{get_user['user_id']}</code>
           👤 Логин: <b>@{get_user['user_login']}</b>
           Ⓜ Имя: <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a>
           🕰 Регистрация: <code>{get_user['user_date']} ({convert_day(how_days)})</code>
            
           🎁 Куплено товаров: <code>{count_items}шт</code>
           🛒 Товаров к корзине: <code>{cart_item}шт</code>
           """)


# Статистика бота
def get_statisctics():
    show_profit_amount_all, show_profit_amount_day, show_profit_amount_week = 0, 0, 0
    show_profit_count_all, show_profit_count_day, show_profit_count_week = 0, 0, 0
    show_users_all, show_users_day, show_users_week, show_users_money = 0, 0, 0, 0

    get_categories = get_all_categoriesx()
    get_positions = get_all_positionsx()
    get_purchases = get_all_purchasesx()
    get_settings = get_settingsx()
    get_users = get_all_usersx()
    #
    # for position in get_positions:
    #     position_item_count = position['position_count']

    for purchase in get_purchases:
        show_profit_amount_all += purchase['purchase_price']
        show_profit_count_all += purchase['purchase_count']

        if purchase['purchase_unix'] - get_settings['misc_profit_day'] >= 0:
            show_profit_amount_day += purchase['purchase_price']
            show_profit_count_day += purchase['purchase_count']
        if purchase['purchase_unix'] - get_settings['misc_profit_week'] >= 0:
            show_profit_amount_week += purchase['purchase_price']
            show_profit_count_week += purchase['purchase_count']

    for user in get_users:
        show_users_all += 1

        if user['user_unix'] - get_settings['misc_profit_day'] >= 0:
            show_users_day += 1
        if user['user_unix'] - get_settings['misc_profit_week'] >= 0:
            show_users_week += 1

    return ded(f"""
           <b>📊 СТАТУСЫ БОТА</b>
           ➖➖➖➖➖➖➖➖➖➖
           <b>🔶 Пользователи 🔶</b>
           👤 Юзеров за день: <code>{show_users_day}</code>
           👤 Пользователей в неделю: <code>{show_users_week}</code>
           👤 Юзеров за все время: <code>{show_users_all}</code>
            
           <b>🔶 Средства 🔶</b>
           💸 Продажи за день: <code>{show_profit_count_day}шт</code> - <code>{show_profit_amount_day}руб.</code>
           💸 Продажи за неделю: <code>{show_profit_count_week}шт</code> - <code>{show_profit_amount_week}руб.</code>
           💸 Продаж за все время: <code>{show_profit_count_all}шт</code> - <code>{show_profit_amount_all}руб.</code>
            
           <b>🔶 Другое 🔶</b>
           🎁 Позиции: <code>{len(get_positions)}шт</code>
           🗃 Категорий: <code>{len(get_categories)}шт</code>
           
           """)
# 🎁 Товары: < code > {int(position_item_count)}шт < / code >


def cart_logistic(user_id):
    HEADER_CART = f"""
        🛒 Ваша корзина: 
➖➖➖➖➖➖➖➖➖➖
        """

    text = """"""
    i = 0
    cost = 0

    get_cart_items = get_user_cart(user_id=user_id)

    if not get_cart_items:
        return None

    for item in get_cart_items:
        get_position = get_positionx(position_id=item.get("position_id"))
        text += f"""
    {i+1}) 🏷 Название: {get_position.get("position_name")}
         📦 Количество: {item.get("position_count")}
         📏 Размер: {item.get("position_size")}
         🎨 Цвет: {item.get("position_color")}
         💰 Цена: {item.get("position_price")}
             
➖➖➖➖➖➖➖➖➖➖
        """

        i += 1
        cost += item.get("position_price")

    end_text = f"""
    
    💰 Общая стоимость товаров: {cost}
    📦 Количество товаров в корзине: {i}
    """

    response = HEADER_CART + text + end_text

    return response
