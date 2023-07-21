# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup

from tgbot.data.config import get_admins


# Кнопки главного меню
def menu_frep(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🎁 Товары", "👤 Профиль", "🧮 Товары в наличии")
    keyboard.row("☎ Поддержка", "ℹ FAQ")

    if user_id in get_admins():
        keyboard.row("🎁 Управление товарами", "🎟 Управление промокодами")
        keyboard.row("⚙ Настройка", "📊 Статистика", "🔆 Общие функции")

    return keyboard


# Кнопки общих функций
def functions_frep(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("👤 Поиск профиля 🔍", "📢 Оповещение", "🧾 Поиск чеков 🔍")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Кнопки настроек
def settings_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🖍 Изменить данные", "🕹 Выключатели")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Кнопки изменения товаров
def items_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🎁 Создать позицию ➕", "🎁 Редактировать позицию 🖍", "🎁 Удалить все позиции ❌")
    keyboard.row("🗃 Создать категорию ➕", "🗃 Редактировать категорию 🖍", "🗃 Удалить все категории ❌")
    keyboard.row("⬅ Главное меню")

    return keyboard


# Кнопки изменения промокодов
def promocodes_frep():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🎟 Создать промокод ➕", "🎟 Редактировать промокод 🖍", "🎟 Удалить все промокоды ❌")
    keyboard.row("⬅ Главное меню")

    return keyboard


def back_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("⬅ Главное меню")

    return keyboard
