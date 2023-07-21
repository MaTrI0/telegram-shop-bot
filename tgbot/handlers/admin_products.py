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
from tgbot.services.api_sqlite import *
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.utils.misc_functions import get_position_admin


# Создание новой категории
@dp.message_handler(IsAdmin(), text="🗃 Создать категорию ➕", state="*")
async def product_category_create(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_category_name")
    await message.answer("<b>🗃 Введите название для категории 🏷</b>")


# Открытие страниц выбора категорий для редактирования
@dp.message_handler(IsAdmin(), text="🗃 Редактировать категорию 🖍", state="*")
async def product_category_edit(message: Message, state: FSMContext):
    await state.finish()

    if len(get_all_categoriesx()) >= 1:
        await message.answer("<b>🗃 Выберите категорию для изменения 🖍</b>",
                             reply_markup=category_edit_swipe_fp(0))
    else:
        await message.answer("<b>❌ Отсутствуют категории для изменения категорий</b>")


# Окно с уточнением удалить все категории (позиции и товары включительно)
@dp.message_handler(IsAdmin(), text="🗃 Удалить все категории ❌", state="*")
async def product_category_remove(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🗃 Вы действительно хотите удалить все категории? ❌</b>\n"
                         "❗ Так же будут удалены все позиции и товары",
                         reply_markup=category_remove_confirm_inl)


# Создание новой позиции
@dp.message_handler(IsAdmin(), text="🎁 Создать позицию ➕", state="*")
async def product_position_create(message: Message, state: FSMContext):
    await state.finish()

    if len(get_all_categoriesx()) >= 1:
        await message.answer("<b>🎁 Выберите категорию для позиции</b>",
                             reply_markup=position_create_swipe_fp(0))
    else:
        await message.answer("<b>❌ Отсутствуют категории для создания позиции</b>")


# Начальные категории для изменения позиции
@dp.message_handler(IsAdmin(), text="🎁 Редактировать позицию 🖍", state="*")
async def product_position_edit(message: Message, state: FSMContext):
    await state.finish()

    if len(get_all_categoriesx()) >= 1:
        await message.answer("<b>🎁 Выберите категорию с нужной позицией🖍</b>",
                             reply_markup=position_edit_category_swipe_fp(0))
    else:
        await message.answer("<b>❌ Отсутствуют категории для изменения позиций</b>")


# Подтверждение удаления всех позиций
@dp.message_handler(IsAdmin(), text="🎁 Удалить все позиции ❌", state="*")
async def product_position_remove(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🎁 Вы действительно хотите удалить все позиции? ❌</b>\n"
                         "❗ Так же будут удалены все товары",
                         reply_markup=position_remove_confirm_inl)


################################################################################################
####################################### СОЗДАНИЕ КАТЕГОРИЙ #####################################
# Принятие названия категории для её создания
@dp.message_handler(IsAdmin(), state="here_category_name")
async def product_category_create_name(message: Message, state: FSMContext):
    if len(message.text) <= 50:
        category_id = get_unix()
        add_categoryx(category_id, clear_html(message.text))

        await state.finish()

        get_positions = len(get_positionsx(category_id=category_id))
        get_category = get_categoryx(category_id=category_id)

        await message.answer(f"<b>🗃 Категория: <code>{get_category['category_name']}</code></b>\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             f"🎁 Количество позиций: <code>{get_positions}шт</code>",
                             reply_markup=category_edit_open_finl(category_id, 0))
    else:
        await message.answer("<b>❌ Название не может превышать 50 символов.</b>\n"
                             "🗃 Введите название для категории 🏷")


################################################################################################
####################################### ИЗМЕНЕНИЕ КАТЕГОРИИ ####################################
# Выбор текущей категории для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="category_edit_open:", state="*")
async def product_category_edit_open(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    await state.finish()

    get_positions = len(get_positionsx(category_id=category_id))
    get_category = get_categoryx(category_id=category_id)

    await call.message.edit_text(f"<b>🗃 Категория: <code>{get_category['category_name']}</code></b>\n"
                                 "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                 f"🎁 Количество позиций: <code>{get_positions}шт</code>",
                                 reply_markup=category_edit_open_finl(category_id, remover))


# Страница выбора категорий для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="catategory_edit_swipe:", state="*")
async def product_category_edit_swipe(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🗃 Выберите категорию для изменения 🖍</b>",
                                 reply_markup=category_edit_swipe_fp(remover))


######################################## САМО ИЗМЕНЕНИЕ КАТЕГОРИИ ########################################
# Изменение названия категории
@dp.callback_query_handler(IsAdmin(), text_startswith="category_edit_name:", state="*")
async def product_category_edit_name(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_category_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_category_name")
    await call.message.answer("<b>🗃 Введите новое название для категории 🏷</b>",
                              reply_markup=category_edit_cancel_finl(category_id, remover))


# Принятие нового имени для категории
@dp.message_handler(IsAdmin(), state="here_change_category_name")
async def product_category_edit_name_get(message: Message, state: FSMContext):
    category_id = (await state.get_data())['here_cache_category_id']
    remover = (await state.get_data())['here_cache_category_remover']

    if len(message.text) <= 50:
        await state.finish()

        update_categoryx(category_id, category_name=clear_html(message.text))

        get_positions = get_positionsx(category_id=category_id)
        get_category = get_categoryx(category_id=category_id)

        await message.answer(f"<b>🗃 Категория: <code>{get_category['category_name']}</code></b>\n"
                             "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             f"🎁 Количество позиций: <code>{len(get_positions)}шт</code>",
                             reply_markup=category_edit_open_finl(category_id, remover))
    else:
        await message.answer("<b>❌ Название не может превышать 50 символов.</b>\n"
                             "🗃 Введите новое название для категории 🏷",
                             reply_markup=category_edit_cancel_finl(category_id, remover))


# Окно с уточнением удалить категорию
@dp.callback_query_handler(IsAdmin(), text_startswith="category_edit_delete:", state="*")
async def product_category_edit_delete(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    await call.message.edit_text("<b>❗ Вы действительно хотите удалить категорию и все ее данные?</b>",
                                 reply_markup=category_edit_delete_finl(category_id, remover))


# Отмена удаления категории
@dp.callback_query_handler(IsAdmin(), text_startswith="category_delete:", state="*")
async def product_category_edit_delete_confirm(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    get_action = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    if get_action == "yes":
        remove_categoryx(category_id=category_id)
        remove_positionx(category_id=category_id)

        await call.answer("🗃 Категория и все ее данные были успешно удалены✅")
        if len(get_all_categoriesx()) >= 1:
            await call.message.edit_text("<b>🗃 Выберите категорию для изменения 🖍</b>",
                                         reply_markup=category_edit_swipe_fp(remover))
        else:
            with suppress(MessageCantBeDeleted):
                await call.message.delete()
    else:
        get_fat_count = len(get_positionsx(category_id=category_id))
        get_category = get_categoryx(category_id=category_id)

        await call.message.edit_text(f"<b>🗃 Категория: <code>{get_category['category_name']}</code></b>\n"
                                     "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                     f"🎁 Количество позиций: <code>{get_fat_count}шт</code>",
                                     reply_markup=category_edit_open_finl(category_id, remover))


################################################################################################
#################################### УДАЛЕНИЕ ВСЕХ КАТЕГОРИЙ ###################################
# Подтверждение на удаление всех категорий (позиций и товаров включительно)
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_remove_category:", state="*")
async def product_category_remove_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]

    if get_action == "yes":
        get_categories = len(get_all_categoriesx())
        get_positions = len(get_all_positionsx())

        clear_categoryx()
        clear_positionx()

        await call.message.edit_text(
            f"<b>🗃 Вы удалили все категории<code>({get_categories}шт)</code>, "
            f"позиции<code>({get_positions}шт)</code>)</code> ☑</b>")
    else:
        await call.message.edit_text("<b>🗃 Вы отменили удаление всех категорий ✅</b>")


################################################################################################
####################################### ДОБАВЛЕНИЕ ПОЗИЦИИ #####################################
# Следующая страница выбора категорий для создания позиций
@dp.callback_query_handler(IsAdmin(), text_startswith="position_create_swipe:", state="*")
async def product_position_create_swipe(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🎁 Выберите категорию для позиции ➕</b>",
                                 reply_markup=position_create_swipe_fp(remover))


# Выбор категории для создания позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_create_open:", state="*")
async def product_position_create_select_category(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]

    await state.update_data(here_cache_change_category_id=category_id)

    await state.set_state("here_position_name")
    await call.message.edit_text("<b>🎁 Введите название для позиции 🏷</b>")


# Принятие имени для создания позиции
@dp.message_handler(IsAdmin(), state="here_position_name")
async def product_position_create_name(message: Message, state: FSMContext):
    if len(message.text) <= 50:
        await state.update_data(here_position_name=clear_html(message.text))

        await state.set_state("here_position_price")
        await message.answer("<b>🎁 Введите цену для позиции 💰</b>")
    else:
        await message.answer("<b>❌ Название не может превышать 50 символов.</b>\n"
                             "🎁 Введите название для позиции 🏷")


# Принятие цены позиции для её создания
@dp.message_handler(IsAdmin(), state="here_position_price")
async def product_position_create_price(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.update_data(here_position_price=message.text)

            await state.set_state("here_position_courier_delivery_price")
            await message.answer("<b>🎁 Введите цену для доставки курьером 📦</b>\n"
                                 "❕ Пришлите <code>0</code> чтобы сделать этот способ доставки недоступным."
                                 )
        else:
            await message.answer("<b>❌ Цена не может быть меньше 0 руб. или больше 10 000 000руб.</b>\n"
                                 "🎁 Введите цену для позиции 💰")
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "🎁 Введите цену для позиции 💰")


# Принятие цены для доставки курьером
@dp.message_handler(IsAdmin(), state="here_position_courier_delivery_price")
async def product_position_airplane_price(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.update_data(here_position_courier_delivery_price=message.text)

            await state.set_state("here_position_by_mail_russia_price")
            await message.answer("<b>🎁 Введите цену для доставки почтой России 🏣</b>\n"
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным."
                                 )
        else:
            await message.answer("<b>❌ Цена доставки не может быть меньше 0 руб. или больше 10 000 000руб.</b>\n" 
                                 "🎁 Введите цену для доставки курьером 📦\n" 
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным."
                                 )
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n" 
                             "🎁 Введите цену для доставки курьером 📦\n" 
                             "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным."
                             )


# Принятие цены для доставки почтой России
@dp.message_handler(IsAdmin(), state="here_position_by_mail_russia_price")
async def product_position_ship_price(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.update_data(here_position_by_mail_russia_price=message.text)

            await state.set_state("here_position_transport_company_price")
            await message.answer("<b>🎁 Введите цену для доставки транспортной компанией 🚚</b>\n"
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным."
                                 )
        else:
            await message.answer("<b>❌ Цена доставки не может быть меньше 1 руб. или больше 10 000 000руб.</b>\n" 
                                 "🎁 Введите цену для доставки почтой России 🏣\n" 
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным." )
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n" 
                             "🎁 Введите цену для доставки почтой России 🏣\n" 
                             "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным."
                             )


# Принятие цены для доставки транспортной компанией
@dp.message_handler(IsAdmin(), state="here_position_transport_company_price")
async def product_position_ship_price(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.update_data(here_position_transport_company_price=message.text)

            await state.set_state("here_position_description")
            await message.answer("<b>🎁 Введите описание для позиции 📜</b>\n" 
                                 "❕ Вы можете использовать HTML разметку\n" 
                                 "❕ Отправьте <code>0</code> чтобы пропустить."
                                 )
        else:
            await message.answer("<b>❌ Цена доставки не может быть меньше 1 руб. или больше 10 000 000руб.</b>\n" 
                                 "🎁 Введите цену для доставки транспортной компанией 🚚\n" 
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным." )
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n" 
                             "🎁 Введите цену для доставки транспортной компанией 🚚\n" 
                             "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным."
                             )


# Принятие описания позиции для её создания
@dp.message_handler(IsAdmin(), state="here_position_description")
async def product_position_create_description(message: Message, state: FSMContext):
    try:
        if len(message.text) <= 600:
            if message.text != "0":
                cache_msg = await message.answer(message.text)
                await cache_msg.delete()

            await state.update_data(here_position_description=message.text)

            await state.set_state("here_position_photo")
            await message.answer("<b>🎁 Пришлите изображение для позиции 📸</b>\n" 
                                 "❕ Пришлите <code>0</code> чтобы пропустить."
                                 )
        else:
            await message.answer("<b>❌ Описание не может превышать 600 символов.</b>\n" 
                                 "🎁 Введите новое описание для позиции 📜\n" 
                                 "❕ Вы можете использовать HTML разметку\n" 
                                 "❕ Отправьте <code>0</code> чтобы пропустить."
                                 )
    except CantParseEntities:
        await message.answer("<b>❌ Ошибка синтаксиса HTML.</b>\n" 
                             "🎁 Введите описание для позиции 📜\n" 
                             "❕ Вы можете использовать HTML разметку\n" 
                             "❕ Отправьте <code>0</code> чтобы пропустить."
                             )


# Принятие изображения позиции для её создания
@dp.message_handler(IsAdmin(), content_types="photo", state="here_position_photo")
@dp.message_handler(IsAdmin(), text="0", state="here_position_photo")
async def product_position_create_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        position_name = clear_html(data['here_position_name'])
        position_price = data['here_position_price']
        courier_delivery_price = data['here_position_courier_delivery_price']
        by_mail_russia_price = data['here_position_by_mail_russia_price']
        transport_company_price = data['here_position_transport_company_price']
        category_id = data['here_cache_change_category_id']
        position_description = data['here_position_description']
    await state.finish()

    position_id, position_photo = get_unix(), ""

    if "text" not in message:
        position_photo = message.photo[-1].file_id

    add_positionx(position_id, position_name, position_price, courier_delivery_price, by_mail_russia_price, transport_company_price, position_description, "", "", position_photo, category_id)
    get_message, get_photo = get_position_admin(position_id)

    if get_photo is not None:
        await message.answer_photo(get_photo, get_message,
                                   reply_markup=position_edit_open_finl(position_id, category_id, 0))
    else:
        await message.answer(get_message, reply_markup=position_edit_open_finl(position_id, category_id, 0))


################################################################################################
####################################### ИЗМЕНЕНИЕ ПОЗИЦИИ #####################################
# Выбор категории с нужной позицией
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_category_open:", state="*")
async def product_position_edit_category_open(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]

    get_category = get_categoryx(category_id=category_id)
    get_positions = get_positionsx(category_id=category_id)

    if len(get_positions) >= 1:
        await call.message.edit_text("<b>🎁 Выберите нужную вам позицию 🖍</b>",
                                     reply_markup=position_edit_swipe_fp(0, category_id))
    else:
        await call.answer(f"🎁 Позиции в категории {get_category['category_name']} отсутствуют")


# Перемещение по страницам категорий для редактирования позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_category_swipe:", state="*")
async def product_position_edit_category_swipe(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🎁 Выберите категорию с нужной позицией 🖍</b>",
                                 reply_markup=position_edit_category_swipe_fp(remover))


# Выбор позиции для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_open:", state="*")
async def product_position_edit_open(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    get_message, get_photo = get_position_admin(position_id)
    await state.finish()

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    if get_photo is not None:
        await call.message.answer_photo(get_photo, get_message,
                                        reply_markup=position_edit_open_finl(position_id, category_id, remover))
    else:
        await call.message.answer(get_message,
                                  reply_markup=position_edit_open_finl(position_id, category_id, remover))


# Перемещение по страницам позиций для редактирования позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_swipe:", state="*")
async def product_position_edit_swipe(call: CallbackQuery, state: FSMContext):
    category_id = call.data.split(":")[1]
    remover = int(call.data.split(":")[2])

    with suppress(MessageCantBeDeleted):
        await call.message.delete()
    await call.message.answer("<b>🎁 Выберите категорию с нужной позицией 🖍</b>",
                              reply_markup=position_edit_swipe_fp(remover, category_id))


######################################## САМО ИЗМЕНЕНИЕ ПОЗИЦИИ ########################################
# Изменение имени позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_name:", state="*")
async def product_position_edit_name(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_name")
    await call.message.answer("<b>🎁 Введите новое название для позиции 🏷</b>",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Принятие имени позиции для её изменения
@dp.message_handler(IsAdmin(), state="here_change_position_name")
async def product_position_edit_name_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data['here_cache_position_id']
        category_id = data['here_cache_category_id']
        remover = data['here_cache_position_remover']

    if len(message.text) <= 50:
        await state.finish()

        update_positionx(position_id, position_name=clear_html(message.text))
        get_message, get_photo = get_position_admin(position_id)

        if get_photo is not None:
            await message.answer_photo(get_photo, get_message,
                                       reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer(get_message, reply_markup=position_edit_open_finl(position_id, category_id, remover))
    else:
        await message.answer("<b>❌ Название не может превышать 50 символов.</b>\n"
                             "🎁 Введите новое название для позиции 🏷",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Изменение цены позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_price:", state="*")
async def product_position_edit_price(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_price")
    await call.message.answer("<b>🎁 Введите новую цену для позиции 💰</b>",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Принятие цены позиции для её изменения
@dp.message_handler(IsAdmin(), state="here_change_position_price")
async def product_position_edit_price_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data['here_cache_position_id']
        category_id = data['here_cache_category_id']
        remover = data['here_cache_position_remover']

    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.finish()

            update_positionx(position_id, position_price=message.text)
            get_message, get_photo = get_position_admin(position_id)

            if get_photo is not None:
                await message.answer_photo(get_photo, get_message,
                                           reply_markup=position_edit_open_finl(position_id, category_id, remover))
            else:
                await message.answer(get_message,
                                     reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer("<b>❌ Цена не может быть меньше 1 руб. или больше 10 000 000грн..</b>\n"
                                 "🎁 Введите цену для позиции 💰",
                                 reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "🎁 Введите цену для позиции 💰",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Изменение описания позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_description:", state="*")
async def product_position_edit_description(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_description")
    await call.message.answer("<b>🎁 Введите новое описание для позиции 📜</b>\n"
                              "❕ Вы можете использовать HTML разметку\n"
                              "❕ Отправьте <code>0</code> чтобы пропустить.",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# !!! Количество товара, закоменчено на случай, если понадобиться
# # Изменение кол-ва товара
# @dp.callback_query_handler(IsAdmin(), text_startswith="position_add_count:", state="*")
# async def position_add_count(call: CallbackQuery, state: FSMContext):
#     position_id = call.data.split(":")[1]
#     category_id = call.data.split(":")[2]
#     remover = int(call.data.split(":")[3])
#
#     await state.update_data(here_cache_position_id=position_id)
#     await state.update_data(here_cache_category_id=category_id)
#     await state.update_data(here_cache_position_remover=remover)
#
#     with suppress(MessageCantBeDeleted):
#         await call.message.delete()
#
#     await state.set_state("here_change_position_count")
#     await call.message.answer("<b>🎁 Введите количество товара, которое есть у вас</b>",
#                               reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
#
#
# @dp.message_handler(IsAdmin(), state="here_change_position_count")
# async def product_position_edit_count_get(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         category_id = data['here_cache_category_id']
#         position_id = data['here_cache_position_id']
#         remover = data['here_cache_position_remover']
#
#     try:
#         if message.text.isdigit():
#             await state.finish()
#
#             update_positionx(position_id, position_count=int(message.text))
#             get_message, get_photo = get_position_admin(position_id)
#
#             if get_photo is not None:
#                 await message.answer_photo(get_photo, get_message,
#                                            reply_markup=position_edit_open_finl(position_id, category_id, remover))
#             else:
#                 await message.answer(get_message,
#                                      reply_markup=position_edit_open_finl(position_id, category_id, remover))
#         else:
#             await message.answer("<b>❌ Вы можете указать только число.</b>\n"
#                                  "🎁 Введите количество товара, которое есть у вас",
#                                  reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
#     except CantParseEntities:
#         await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
#                              "🎁 Введите количество вашего товара",
#                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Изменение цветов товара
@dp.callback_query_handler(IsAdmin(), text_startswith="position_add_colors_item:", state="*")
async def position_add_color(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_color")
    await call.message.answer("<b>Введите имеющиеся у вас цвета через запятую, на пример: красный, синий, желтый</b>",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


@dp.message_handler(IsAdmin(), state="here_change_position_color")
async def product_position_edit_color_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        category_id = data['here_cache_category_id']
        position_id = data['here_cache_position_id']
        remover = data['here_cache_position_remover']

    try:
        if len(message.text) <= 1000:
            await state.finish()

            if message.text != "0":
                cache_msg = await message.answer(message.text)
                await cache_msg.delete()

            update_positionx(position_id, position_colors=message.text)
            get_message, get_photo = get_position_admin(position_id)

            if get_photo is not None:
                await message.answer_photo(get_photo, get_message,
                                           reply_markup=position_edit_open_finl(position_id, category_id, remover))
            else:
                await message.answer(get_message,
                                     reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer("<b>❌ Количество цветов не может превышать 1000 символов.</b>\n"
                                 "🎁 Введите цвета еще раз 📜\n",
                                 reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
    except CantParseEntities:
        await message.answer("<b>❌ Ошибка синтаксиса.</b>\n",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Изменение размеров товара
@dp.callback_query_handler(IsAdmin(), text_startswith="position_add_sizes_item:", state="*")
async def position_add_size(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_size")
    await call.message.answer("<b>Введите размеры, имеющиеся у вас через запятую, на пример: XL, XS, S, XSL</b>",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


@dp.message_handler(IsAdmin(), state="here_change_position_size")
async def product_position_edit_size_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        category_id = data['here_cache_category_id']
        position_id = data['here_cache_position_id']
        remover = data['here_cache_position_remover']

    try:
        if len(message.text) <= 1000:
            await state.finish()

            cache_msg = await message.answer(message.text)
            await cache_msg.delete()

            update_positionx(position_id, position_sizes=message.text)
            get_message, get_photo = get_position_admin(position_id)

            if get_photo is not None:
                await message.answer_photo(get_photo, get_message,
                                           reply_markup=position_edit_open_finl(position_id, category_id, remover))
            else:
                await message.answer(get_message,
                                     reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer("<b>❌ Количество размеров не может превышать 1000 символов.</b>\n"
                                 "🎁 Введите размеры еще раз 📜\n",
                                 reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
    except CantParseEntities:
        await message.answer("<b>❌ Ошибка синтаксису.</b>\n",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Принятие описания позиции для её изменения
@dp.message_handler(IsAdmin(), state="here_change_position_description")
async def product_position_edit_description_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        category_id = data['here_cache_category_id']
        position_id = data['here_cache_position_id']
        remover = data['here_cache_position_remover']

    try:
        if len(message.text) <= 600:
            await state.finish()

            if message.text != "0":
                cache_msg = await message.answer(message.text)
                await cache_msg.delete()

            update_positionx(position_id, position_description=message.text)
            get_message, get_photo = get_position_admin(position_id)

            if get_photo is not None:
                await message.answer_photo(get_photo, get_message,
                                           reply_markup=position_edit_open_finl(position_id, category_id, remover))
            else:
                await message.answer(get_message,
                                     reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer("<b>❌ Описание не может превышать 600 символов.</b>\n"
                                 "🎁 Введите новое описание для позиции 📜\n"
                                 "❕ Вы можете использовать HTML разметку\n"
                                 "❕ Отправьте <code>0</code> чтобы пропустить.",
                                 reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
    except CantParseEntities:
        await message.answer("<b>❌ Ошибка синтаксису HTML.</b>\n"
                             "🎁 Введите новое описание для позиции 📜\n"
                             "❕ Вы можете использовать HTML разметку\n"
                             "❕ Отправьте <code>0</code> чтобы пропустить.",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Изменение изображения позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_photo:", state="*")
async def product_position_edit_photo(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_photo")
    await call.message.answer("<b>🎁 Отправьте новое изображение для позиции 📸</b>\n"
                              "❕ Отправьте <code>0</code> чтобы пропустить.",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Принятие нового фото для позиции
@dp.message_handler(IsAdmin(), content_types="photo", state="here_change_position_photo")
@dp.message_handler(IsAdmin(), text="0", state="here_change_position_photo")
async def product_position_edit_photo_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data['here_cache_position_id']
        category_id = data['here_cache_category_id']
        remover = data['here_cache_position_remover']
    await state.finish()

    if "text" in message:
        position_photo = ""
    else:
        position_photo = message.photo[-1].file_id

    update_positionx(position_id, position_photo=position_photo)
    get_message, get_photo = get_position_admin(position_id)

    if get_photo is not None:
        await message.answer_photo(get_photo, get_message,
                                   reply_markup=position_edit_open_finl(position_id, category_id, remover))
    else:
        await message.answer(get_message, reply_markup=position_edit_open_finl(position_id, category_id, remover))


# Изменение цены за доставку курьером
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_courier_delivery_price:", state="*")
async def product_position_edit_airplain(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_courier_delivery")
    await call.message.answer("<b>🎁 Введите новую цену доставки курьером в чат 📦</b>\n"
                              "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Принятие цены за доставку курьером для её изменения
@dp.message_handler(IsAdmin(), state="here_change_position_courier_delivery")
async def product_position_edit_airplain_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data['here_cache_position_id']
        category_id = data['here_cache_category_id']
        remover = data['here_cache_position_remover']

    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.finish()

            update_positionx(position_id, courier_delivery_price=message.text)
            get_message, get_photo = get_position_admin(position_id)

            if get_photo is not None:
                await message.answer_photo(get_photo, get_message,
                                           reply_markup=position_edit_open_finl(position_id, category_id, remover))
            else:
                await message.answer(get_message,
                                     reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer("<b>❌ Цена за доставку курьером не может быть меньше 1 руб. или больше 10 000 000 руб.</b>\n"
                                 "🎁 Введите новую цену доставки курьером в чат 📦\n"
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                                 reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "🎁 Введите новую цену доставки курьером в чат 📦\n"
                             "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Изменение цены за доставку почтой росссии
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_by_mail_russia_price:", state="*")
async def product_position_edit_ship(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_by_mail_russia_price")
    await call.message.answer("<b>🎁 Введите новую цену доставки почтой России в чат 🏣</b>\n"
                              "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Принятие цены за доставку почтой россии для её изменения
@dp.message_handler(IsAdmin(), state="here_change_position_by_mail_russia_price")
async def product_position_edit_ship_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data['here_cache_position_id']
        category_id = data['here_cache_category_id']
        remover = data['here_cache_position_remover']

    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.finish()

            update_positionx(position_id, by_mail_russia_price=message.text)
            get_message, get_photo = get_position_admin(position_id)

            if get_photo is not None:
                await message.answer_photo(get_photo, get_message,
                                           reply_markup=position_edit_open_finl(position_id, category_id, remover))
            else:
                await message.answer(get_message,
                                     reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer("<b>❌ Цена за доставку почтой России не может быть меньше 1 руб. или больше 10 000 000 руб.</b>\n"
                                 "🎁 Введите новую цену доставки почтой России в чат 🏣\n"
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                                 reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "🎁 Введите новую цену доставки почтой России в чат 🏣\n"
                             "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Изменение цены за доставку транспортной компанией
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_transport_company_price:", state="*")
async def product_position_edit_ship(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    await state.update_data(here_cache_position_id=position_id)
    await state.update_data(here_cache_category_id=category_id)
    await state.update_data(here_cache_position_remover=remover)

    with suppress(MessageCantBeDeleted):
        await call.message.delete()

    await state.set_state("here_change_position_transport_company_price")
    await call.message.answer("<b>🎁 Введите новую цену доставки транспортной компанией в чат 🚚</b>\n"
                              "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                              reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Принятие цены за доставку почтой россии для её изменения
@dp.message_handler(IsAdmin(), state="here_change_position_transport_company_price")
async def product_position_edit_ship_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data['here_cache_position_id']
        category_id = data['here_cache_category_id']
        remover = data['here_cache_position_remover']

    if message.text.isdigit():
        if 0 <= int(message.text) <= 10000000:
            await state.finish()

            update_positionx(position_id, transport_company_price=message.text)
            get_message, get_photo = get_position_admin(position_id)

            if get_photo is not None:
                await message.answer_photo(get_photo, get_message,
                                           reply_markup=position_edit_open_finl(position_id, category_id, remover))
            else:
                await message.answer(get_message,
                                     reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await message.answer("<b>❌ Цена за доставку транспортной компанией не может быть меньше 1 руб. или больше 10 000 000 руб.</b>\n"
                                 "🎁 Введите новую цену доставки транспортной компанией в чат 🚚\n"
                                 "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                                 reply_markup=position_edit_cancel_finl(position_id, category_id, remover))
    else:
        await message.answer("<b>❌ Данные были введены неправильно.</b>\n"
                             "🎁 Введите новую цену доставки транспортной компанией в чат 🚚\n"
                             "❕ Отправьте <code>0</code> чтобы сделать этот способ доставки недоступным.",
                             reply_markup=position_edit_cancel_finl(position_id, category_id, remover))


# Удаление позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_delete:", state="*")
async def product_position_edit_delete(call: CallbackQuery, state: FSMContext):
    position_id = call.data.split(":")[1]
    category_id = call.data.split(":")[2]
    remover = int(call.data.split(":")[3])

    with suppress(MessageCantBeDeleted):
        await call.message.delete()
    await call.message.answer("<b>🎁 Вы действительно хотите удалить позицию? ❌</b>",
                              reply_markup=position_edit_delete_finl(position_id, category_id, remover))


# Подтверждение удаления позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_delete:", state="*")
async def product_position_edit_delete_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]
    position_id = call.data.split(":")[2]
    category_id = call.data.split(":")[3]
    remover = int(call.data.split(":")[4])

    if get_action == "yes":
        remove_positionx(position_id=position_id)

        await call.answer("🎁 Вы успешно удалили позицию и ее товары ✅")

        if len(get_positionsx(category_id=category_id)) >= 1:
            await call.message.edit_text("<b>🎁 Выберите нужную вам позицию 🖍</b>",
                                         reply_markup=position_edit_swipe_fp(remover, category_id))
        else:
            with suppress(MessageCantBeDeleted):
                await call.message.delete()
    else:
        get_message, get_photo = get_position_admin(position_id)

        with suppress(MessageCantBeDeleted):
            await call.message.delete()

        if get_photo is not None:
            await call.message.answer_photo(get_photo, get_message,
                                            reply_markup=position_edit_open_finl(position_id, category_id, remover))
        else:
            await call.message.answer(get_message,
                                      reply_markup=position_edit_open_finl(position_id, category_id, remover))


################################################################################################
###################################### УДАЛЕНИЕ ВСЕХ ПОЗИЦИЙ ###################################
# Согласие на удаление всех позиций и товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_remove_position:", state="*")
async def product_position_remove(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]

    if get_action == "yes":
        get_positions = len(get_all_positionsx())

        clear_positionx()

        await call.message.edit_text(
            f"<b>🎁 Вы удалили все позиции<code>({get_positions}шт)</code></b>")
    else:
        await call.message.edit_text("<b>🎁 Вы отменили удаление всех позиций ✅</b>")