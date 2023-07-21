# - *- coding: utf- 8 - *-
import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as ikb

from tgbot.services.api_sqlite import get_all_categoriesx


# Кнопки при открытии самого товара
def promocodes_type_change(category_id):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("Для скидки в валюте", callback_data=f"promocode_type:currency:{category_id}")
    ).add(
        ikb("Для скидки в процентах", callback_data=f"promocode_type:percentage:{category_id}")
    )
    return keyboard


def promocode_create_first_buy():
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("✅ Да", callback_data=f"first_buy:yes")
    ).add(
        ikb("❌ Нет", callback_data=f"first_buy:no")
    )
    return keyboard


def promocode_create_one_client():
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("✅ Да", callback_data=f"one_client:yes")
    ).add(
        ikb("❌ Нет", callback_data=f"one_client:no")
    )
    return keyboard


def promocode_create_confirm():
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("✅ Подтвердить", callback_data=f"promocode_create_confirm:yes:"),
        ikb("❌ Отменить", callback_data=f"promocode_create_confirm:not:")
    )

    return keyboard


def promocode_delete_confirm():
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("✅ Подтвердить", callback_data=f"promocode_delete_confirm:yes:"),
        ikb("❌ Отменить", callback_data=f"promocode_delete_confirm:not:")
    )

    return keyboard


# Отмена изменения позиции и возвращение
def promocode_create_cancel_finl():
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("❌ Отменить", callback_data=f"position_edit_cancel"),
    )

    return keyboard


def promocode_edit_menu(promocode):
    keyboard = InlineKeyboardMarkup(
    ).add(
        ikb("🎟 Измен. название", callback_data=f"promocode_edit_name:{promocode}"),
        ikb("🎟 Измен. мин. сумму заказа", callback_data=f"promocode_edit_minimum_order:{promocode}"),
    ).add(
        ikb("🎟 Измен. скидку", callback_data=f"promocode_edit_discount:{promocode}"),
        ikb("🎟 Измен. количество активаций", callback_data=f"promocode_edit_activation_count:{promocode}"),
    ).add(
        ikb("⬅ Назад", callback_data=f"position_edit_cancel"),
        ikb("❌ Удалить", callback_data=f"promocode_delete:{promocode}"),
    )

    return keyboard


# Стартовые страницы выбора категории для изменения
def promocodes_create_swipe_fp(remover):
    get_categories = get_all_categoriesx()
    keyboard = InlineKeyboardMarkup()

    if remover >= len(get_categories):
        remover -= 10

    for count, a in enumerate(range(remover, len(get_categories))):
        if count < 10:
            keyboard.add(ikb(get_categories[a]['category_name'],
                             callback_data=f"promocodes_create_open:{get_categories[a]['category_id']}:{remover}"))

    if len(get_categories) <= 10:
        pass
    elif len(get_categories) > 10 > remover:
        keyboard.add(
            ikb(f"🔸 1/{math.ceil(len(get_categories) / 10)} 🔸", callback_data="..."),
            ikb("Дальше ➡", callback_data=f"promocodes_create_swipe:{remover + 10}")
        )
    elif remover + 10 >= len(get_categories):
        keyboard.add(
            ikb("⬅ Назад", callback_data=f"promocodes_create_swipe:{remover - 10}"),
            ikb(f"🔸 {str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)} 🔸", callback_data="...")
        )
    else:
        keyboard.add(
            ikb("⬅ Назад", callback_data=f"promocodes_create_swipe:{remover - 10}"),
            ikb(f"🔸 {str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)} 🔸", callback_data="..."),
            ikb("Дальше ➡", callback_data=f"promocodes_create_swipe:{remover + 10}"),
        )

    return keyboard
