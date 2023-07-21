# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🛒 В корзину", callback_data=f"cart_item_open:{position_id}")
    ).add(
        InlineKeyboardButton("⬅ Вернуться ↩", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard


def cart_keyboard():
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🛒 Очистить корзину", callback_data="clear_cart"),
        InlineKeyboardButton("💰 Оплатить товары", callback_data="cart_pay")
    ).add(
        InlineKeyboardButton("⬅ Назад", callback_data="main_menu")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count, color, size):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}:{color}:{size}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


def cart_pay_confirm():
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"pay_cart:yes"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"pay_cart:not")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_add(position_id, get_count, color, size):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"cart_item_confirm:yes:{position_id}:{get_count}:{color}:{size}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"cart_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl():
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"http://t.me/suport31_bot"),
    )

    return keyboard


def success_added_item_cart(item_count):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton(f"🛒 Корзина {item_count}", callback_data=f"cart_open"),
        InlineKeyboardButton("🗃 К просмотру товара", callback_data=f"buy_category_swipe:{0}")
    )

    return keyboard
