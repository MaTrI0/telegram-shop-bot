# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Рассылка
mail_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("✅ Отправить", callback_data="confirm_mail:yes"),
    InlineKeyboardButton("❌ Отменить", callback_data="confirm_mail:not")
)


# Кнопки при поиске профиля через админ-меню
def profile_open_inl(item_count):
    keyboard = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton("🎁 Мои покупки", callback_data="user_history"),
        InlineKeyboardButton(f"🛒 Корзина {item_count}", callback_data="cart_open")
    ).add(
        InlineKeyboardButton("🎫 Активировать промокод", callback_data="activation_promocode")
    )

    return keyboard

# Удаление сообщения
close_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Закрыть", callback_data="close_this"),
)

######################################## ТОВАРЫ ########################################
# Удаление категорий
category_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Да, удалить всё",
                         callback_data="confirm_remove_category:yes"),
    InlineKeyboardButton("✅ Нет, отменить", callback_data="confirm_remove_category:not")
)

# Удаление позиций
position_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("❌ Да, удалить всё",
                         callback_data="confirm_remove_position:yes"),
    InlineKeyboardButton("✅ Нет, отменить", callback_data="confirm_remove_position:not")
)
