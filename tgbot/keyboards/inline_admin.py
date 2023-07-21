# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as ikb

from tgbot.services.api_sqlite import get_settingsx, get_user_cart


# # Поиск профиля
def profile_search_finl(user_id):
    cart_item = 0
    get_user_cart_items = get_user_cart(user_id=user_id)

    if get_user_cart_items is None:
        pass
    else:
        for items in get_user_cart_items:
            cart_item += 1

    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🎁 Покупки", callback_data=f"admin_user_purchases:{user_id}"),
        ikb(f"🛒 Корзина {cart_item}", callback_data=f"admin_user_cart:{user_id}")
    ).add(
        ikb("💌 Отправить СМС", callback_data=f"admin_user_message:{user_id}"),
        ikb("🔄 Обновить", callback_data=f"admin_user_refresh:{user_id}")
    ).add(
        ikb("👑 Назначить администратором", callback_data=f"add_admin_rules")
    )

    return keyboard


# Возвращение к профилю
def profile_search_return_finl(user_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Отменить", callback_data=f"admin_user_refresh:{user_id}"),
    )

    return keyboard


# Кнопки с настройками
def settings_open_finl():
    keyboard = InlineKeyboardMarkup()

    get_settings = get_settingsx()

    if "None" == get_settings['misc_faq']:
        faq_kb = ikb("Не востановлено ❌", callback_data="settings_edit_faq")
    else:
        faq_kb = ikb(f"{get_settings['misc_faq'][:15]}... ✅", callback_data="settings_edit_faq")

    keyboard.add(
        ikb("ℹ FAQ", callback_data="..."), faq_kb
    )

    return keyboard


# Выключатели
def turn_open_finl():
    keyboard = InlineKeyboardMarkup()

    get_settings = get_settingsx()
    status_buy_kb = ikb("Включено ✅", callback_data="turn_buy:False")
    status_work_kb = ikb("Включено ✅", callback_data="turn_work:False")

    if get_settings['status_buy'] == "False":
        status_buy_kb = ikb("Выключено ❌", callback_data="turn_buy:True")
    if get_settings['status_work'] == "False":
        status_work_kb = ikb("Выключено ❌", callback_data="turn_work:True")

    keyboard.row(
        ikb("⛔ Тех. работы", callback_data="..."), status_work_kb
    ).row(
        ikb("🎁 Покупки", callback_data="..."), status_buy_kb
    )

    return keyboard


######################################## ТОВАРЫ ########################################
# Изменение категории
def category_edit_open_finl(category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Измен. название", callback_data=f"category_edit_name:{category_id}:{remover}"),
        ikb("📁 Добавить продукты", callback_data=f"position_create_open:{category_id}"),
    ).add(
        ikb("⬅ Вернуться ↩", callback_data=f"catategory_edit_swipe:{remover}"),
        ikb("❌ Удалить", callback_data=f"category_edit_delete:{category_id}:{remover}")
    )

    return keyboard


# Кнопки с удалением категории
def category_edit_delete_finl(category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Да, удалить", callback_data=f"category_delete:{category_id}:yes:{remover}"),
        ikb("✅ Нет, отменить", callback_data=f"category_delete:{category_id}:not:{remover}")
    )

    return keyboard


# Отмена изменения категории и возвращение
def category_edit_cancel_finl(category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Отменить", callback_data=f"category_edit_open:{category_id}:{remover}"),
    )

    return keyboard


# Кнопки при открытии позиции для изменения
def position_edit_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🏷 Измен. название", callback_data=f"position_edit_name:{position_id}:{category_id}:{remover}"),
        ikb("💰 Измен. цену", callback_data=f"position_edit_price:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("📜 Измен. описание", callback_data=f"position_edit_description:{position_id}:{category_id}:{remover}"),
        ikb("📸 Смен. фото", callback_data=f"position_edit_photo:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("🗑 Очистить", callback_data=f"position_edit_clear:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("🎨 Измен. имеющиеся цвета", callback_data=f"position_add_colors_item:{position_id}:{category_id}:{remover}"),
        ikb("📏 Измен. имеющиеся размеры", callback_data=f"position_add_sizes_item:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("📦 Измен. цену доставки курьером", callback_data=f"position_edit_courier_delivery_price:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("🏣 Измен. цену доставки почтой России", callback_data=f"position_edit_by_mail_russia_price:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("🚚 Измен. цену доставки транспорт. комп.", callback_data=f"position_edit_transport_company_price:{position_id}:{category_id}:{remover}"),
    ).add(
        ikb("❌ Удалить", callback_data=f"position_edit_delete:{position_id}:{category_id}:{remover}"),
        ikb("⬅ Вернуться ↩", callback_data=f"position_edit_swipe:{category_id}:{remover}"),
    )

    return keyboard


# Подтверждение удаления позиции
def position_edit_delete_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Да, удалить", callback_data=f"position_delete:yes:{position_id}:{category_id}:{remover}"),
        ikb("✅ Нет, отменить", callback_data=f"position_delete:not:{position_id}:{category_id}:{remover}")
    )

    return keyboard


# Отмена изменения позиции и возвращение
def position_edit_cancel_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Отменить", callback_data=f"position_edit_open:{position_id}:{category_id}:{remover}"),
    )

    return keyboard
