# - *- coding: utf- 8 - *-
import math
import random
import sqlite3

from tgbot.data.config import PATH_DATABASE
from tgbot.utils.const_functions import get_unix, get_date, clear_html


# Преобразование полученного списка в словарь
def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


####################################################################################################
##################################### ФОРМАТИРОВАНИЕ ЗАПРОСА #######################################
# Форматирование запроса без аргументов
def update_format(sql, parameters: dict):
    if "XXX" not in sql: sql += " XXX "

    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())


# Форматирование запроса с аргументами
def update_format_args(sql, parameters: dict):
    sql = f"{sql} WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())


####################################################################################################
########################################### ЗАПРОСЫ К БД ###########################################
# Добавление пользователя
def add_userx(user_id, user_login, user_name):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_users "
                    "(user_id, user_login, user_name, user_refill, user_date, user_unix) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    [user_id, user_login, user_name, 0, get_date(), get_unix()])
        con.commit()


# Получение пользователя
def get_userx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_users"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()


# Получение пользователей
def get_usersx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_users"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchall()


# Получение всех пользователей
def get_all_usersx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_users"
        return con.execute(sql).fetchall()


# Редактирование пользователя
def update_userx(user_id, **kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE storage_users SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(user_id)
        con.execute(sql + "WHERE user_id = ?", parameters)
        con.commit()


# Удаление пользователя
def delete_userx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_users"
        sql, parameters = update_format_args(sql, kwargs)
        con.execute(sql, parameters)
        con.commit()


# Получение настроек
def get_settingsx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_settings"
        return con.execute(sql).fetchone()


# Редактирование настроек
def update_settingsx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "UPDATE storage_settings SET"
        sql, parameters = update_format(sql, kwargs)
        con.execute(sql, parameters)
        con.commit()


# Добавление категории
def add_categoryx(category_id, category_name):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_category (category_id, category_name) VALUES (?, ?)",
                    [category_id, category_name])
        con.commit()


# Изменение категории
def update_categoryx(category_id, **kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE storage_category SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(category_id)
        con.execute(sql + "WHERE category_id = ?", parameters)
        con.commit()


# Получение категории
def get_categoryx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_category"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()


# Получение категорий
def get_categoriesx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_category"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchall()


# Получение всех категорий
def get_all_categoriesx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_category"
        return con.execute(sql).fetchall()


# Удаление всех категорий
def clear_categoryx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_category"
        con.execute(sql)
        con.commit()


# Удаление категории
def remove_categoryx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_category"
        sql, parameters = update_format_args(sql, kwargs)
        con.execute(sql, parameters)
        con.commit()


# Добавление категории
def add_positionx(position_id, position_name, position_price, courier_delivery_price, by_mail_russia_price, transport_company_price, position_description, position_colors, position_sizes, position_photo, category_id):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_position "
                    "(position_id, position_name, position_price, courier_delivery_price, by_mail_russia_price, transport_company_price, position_description, position_colors, position_sizes, position_photo, position_date, category_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [position_id, position_name, position_price, courier_delivery_price, by_mail_russia_price, transport_company_price, position_description, position_colors, position_sizes, position_photo, get_date(), category_id])
        con.commit()


# Изменение позиции
def update_positionx(position_id, **kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE storage_position SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(position_id)
        con.execute(sql + "WHERE position_id = ?", parameters)
        con.commit()


# Получение категории
def get_positionx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_position"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()


# Получение категорий
def get_positionsx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_position"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchall()


# Получение всех категорий
def get_all_positionsx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_position"
        return con.execute(sql).fetchall()


# Удаление всех позиций
def clear_positionx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_position"
        con.execute(sql)
        con.commit()


# Удаление позиции
def remove_positionx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_position"
        sql, parameters = update_format_args(sql, kwargs)
        con.execute(sql, parameters)
        con.commit()


# Добавление товара в карзину
def add_user_cart(user_id, position_id, position_count, position_color, position_size, position_price):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_cart "
                    "(user_id, position_id, position_count, position_color, position_size, position_price) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    [user_id, position_id, position_count, position_color, position_size, position_price]
                    )
        con.commit()


# Получение корзины
def get_user_cart(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_cart"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchall()


# Удаление корзины
def remove_cart(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_cart"
        sql, parameters = update_format_args(sql, kwargs)
        con.execute(sql, parameters)
        con.commit()


# добавдение промокода
def add_promocode(category_id, promocode_name, promocode_type, promocode_activation_count, promocode_minimum_order_amount, promocode_discount_amount_currency,
                  promocode_discount_percentage, promocode_first_buy, promocode_one_client, promocode_valid_period):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_promocodes "
                    "(category_id, promocode_name, promocode_type, promocode_activation_count, promocode_minimum_order_amount, promocode_discount_amount_currency, "
                    "promocode_discount_amount_percentage, promocode_first_buy, promocode_one_client, promocode_valid_period) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [category_id, promocode_name, promocode_type, promocode_activation_count, promocode_minimum_order_amount, promocode_discount_amount_currency,
                     promocode_discount_percentage, promocode_first_buy, promocode_one_client, promocode_valid_period]
                    )
        con.commit()


# Получение промокода
def get_promocode(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_promocodes"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()


# Получение всех промокодов
def get_all_promocodesx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELCT * FROM storage_promocodes"
        return con.execute(sql).fetchall()


# Изменение промокода
def update_promocode(promocode_nam, **kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE storage_promocodes SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(promocode_nam)
        con.execute(sql + "WHERE promocode_name = ?", parameters)
        con.commit()


# Удаление всех промокодов
def clear_promocode():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_promocodes"
        con.execute(sql)
        con.commit()


# Удаление промокода
def remove_promocode(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE FROM storage_promocodes"
        sql, parameters = update_format_args(sql, kwargs)
        con.execute(sql, parameters)
        con.commit()


# Добавление пользователя активировавшего промокод
def add_promocode_activation_user(user_id, promocode_name, activation_count):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_promocodes_users "
                    "(user_id, promocode_name, activation_count) "
                    "VALUES (?, ?, ?)",
                    [user_id, promocode_name, activation_count]
                    )
        con.commit()


# Получение пользователя активировавшего промокод
def get_promocode_activation_user(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_promocodes_users"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()


# Изменение промокода
def update_promocode_activation_user(user_id, **kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE storage_promocodes_users SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(user_id)
        con.execute(sql + "WHERE user_id = ?", parameters)
        con.commit()


# Удаление всех промокодов
def clear_promocode_activation_user():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "DELETE * FROM storage_promocodes_users"
        con.execute(sql)
        con.commit()


# Получение всех пользователей активироваших промокод
def get_all_promocodesx_activation_user():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_promocodes_users"
        return con.execute(sql).fetchall()


# Добавление покупки
def add_purchasex(user_id, user_login, user_name, purchase_receipt, purchase_count, purchase_price, purchase_price_one,
                  purchase_position_id, purchase_position_name, purchase_date, purchase_unix, changed_color, changed_size):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_purchases "
                    "(user_id, user_login, user_name, purchase_receipt, purchase_count, purchase_price, purchase_price_one, purchase_position_id, "
                    "purchase_position_name, purchase_date, purchase_unix, purchase_changed_color, purchase_changed_size) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [user_id, user_login, user_name, purchase_receipt, purchase_count, purchase_price,
                     purchase_price_one, purchase_position_id, purchase_position_name, purchase_date,
                     purchase_unix, changed_color, changed_size])
        con.commit()


# Получение покупки
def get_purchasex(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_purchases"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()


# Получение покупок
def get_purchasesx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_purchases"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchall()


# Получение всех покупок
def get_all_purchasesx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_purchases"
        return con.execute(sql).fetchall()


# Последние N покупок
def last_purchasesx(user_id, count):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_purchases WHERE user_id = ? ORDER BY increment DESC LIMIT {count}"
        return con.execute(sql, [user_id]).fetchall()


# Создание всех таблиц для БД
def create_dbx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

        # Создание БД с хранением данных пользователей
        if len(con.execute("PRAGMA table_info(storage_users)").fetchall()) == 8:
            print("DB was found(1/8)")
        else:
            con.execute("CREATE TABLE storage_users("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "user_id INTEGER,"
                        "user_login TEXT,"
                        "user_name TEXT,"
                        "user_promocode TEXT,"
                        "user_refill INTEGER,"
                        "user_date TIMESTAMP,"
                        "user_unix INTEGER)")
            print("DB was not found(1/8) | Creating...")

        # Создание БД с хранением настроек
        if len(con.execute("PRAGMA table_info(storage_settings)").fetchall()) == 9:
            print("DB was found(2/8)")
        else:
            con.execute("CREATE TABLE storage_settings("
                        "status_work TEXT,"
                        "status_refill TEXT,"
                        "status_buy TEXT,"
                        "misc_faq TEXT,"
                        "misc_support TEXT,"
                        "misc_bot TEXT,"
                        "misc_update TEXT,"
                        "misc_profit_day INTEGER,"
                        "misc_profit_week INTEGER)")

            con.execute("INSERT INTO storage_settings("
                        "status_work, status_refill, status_buy, misc_faq, misc_support,"
                        "misc_bot, misc_update, misc_profit_day, misc_profit_week)"
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        ["True", "False", "False", "None", "None", "None", "False", get_unix(), get_unix()])
            print("DB was not found(2/8) | Creating...")

        # Создание БД с хранением категорий
        if len(con.execute("PRAGMA table_info(storage_category)").fetchall()) == 3:
            print("DB was found(3/8)")
        else:
            con.execute("CREATE TABLE storage_category("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "category_id INTEGER,"
                        "category_name TEXT)")
            print("DB was not found(3/8) | Creating...")

        # Создание БД с хранением позиций
        if len(con.execute("PRAGMA table_info(storage_position)").fetchall()) == 13:
            print("DB was found(4/8)")
        else:
            con.execute("CREATE TABLE storage_position("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "position_id INTEGER,"
                        "position_name TEXT,"
                        "position_price INTEGER,"
                        "courier_delivery_price INTEGER," 
                        "by_mail_russia_price INTEGER,"
                        "transport_company_price INTEGER,"
                        "position_description TEXT,"
                        "position_colors TEXT,"
                        "position_sizes TEXT,"
                        "position_photo TEXT,"
                        "position_date TIMESTAMP,"
                        "category_id INTEGER)")
            print("DB was not found(4/8) | Creating...")

        # # Создание БД с хранением покупок
        if len(con.execute("PRAGMA table_info(storage_purchases)").fetchall()) == 14:
            print("DB was found(5/8)")
        else:
            con.execute("CREATE TABLE storage_purchases("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "user_id INTEGER,"
                        "user_login TEXT,"
                        "user_name TEXT,"
                        "purchase_receipt TEXT,"
                        "purchase_count INTEGER,"
                        "purchase_price INTEGER,"
                        "purchase_price_one INTEGER,"
                        "purchase_position_id INTEGER,"
                        "purchase_position_name TEXT,"
                        "purchase_changed_color TEXT," 
                        "purchase_changed_size TEXT,"
                        "purchase_date TIMESTAMP,"
                        "purchase_unix INTEGER)")
            print("DB was not found(5/8) | Creating...")

        # # Создание БД с хранением промокодов
        if len(con.execute("PRAGMA table_info(storage_promocodes)").fetchall()) == 11:
            print("DB was found(6/8)")
        else:
            con.execute("CREATE TABLE storage_promocodes("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "category_id INTEGER,"
                        "promocode_name TEXT,"
                        "promocode_type TEXT,"
                        "promocode_activation_count INTEGER,"
                        "promocode_minimum_order_amount INTEGER,"
                        "promocode_discount_amount_currency INTEGER,"
                        "promocode_discount_amount_percentage INTEGER,"
                        "promocode_first_buy TEXT,"
                        "promocode_one_client TEXT,"
                        "promocode_valid_period TIMESTAMP)")
            print("DB was found(6/8) | Creating...")

        # # Создание БД с хранением пользователей активировавших прокод
        if len(con.execute("PRAGMA table_info(storage_promocodes_users)").fetchall()) == 4:
            print("DB was found(7/8)")
        else:
            con.execute("CREATE TABLE storage_promocodes_users("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "user_id INTEGER,"
                        "promocode_name TEXT,"
                        "activation_count INTEGER)")
            print("DB was found(7/8) | Creating...")

        # # Создание БД с хранением карзины
        if len(con.execute("PRAGMA table_info(storage_cart)").fetchall()) == 7:
            print("DB was found(8/8)")
        else:
            con.execute("CREATE TABLE storage_cart("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "user_id INTEGER,"
                        "position_id INTEGER,"
                        "position_count INTEGER,"
                        "position_color STRING,"
                        "position_size STRING,"
                        "position_price INTEGER)")
            print("DB was found(8/8) | Creating...")

        con.commit()
