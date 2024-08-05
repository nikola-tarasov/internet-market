import asyncio
import logging
import sys
from os import getenv
from database import db_start,cmd_start_db, add_item, search_in_items
from aiogram.methods import DeleteWebhook # skip_updates
from aiogram import Bot, Dispatcher, Router, types,F
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext











TOKEN =("")

ADMIN =("")


dp = Dispatcher()

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


# async def start_up():
#    await db_start()




cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Отмена"),KeyboardButton(text="Помощь")]
    ],resize_keyboard=True)



keyboardMain = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Каталог"),KeyboardButton(text="Контакты"),KeyboardButton(text="Корзина")]
    ],resize_keyboard=True)

panel_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Каталог"),KeyboardButton(text="Контакты"),KeyboardButton(text="Корзина"),KeyboardButton(text="Админ-панель")]
    ],resize_keyboard=True)

# Админ клавиатура
keyboardAdminPanel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Добавить товар"),KeyboardButton(text="Удалить товар"),KeyboardButton(text="Сделать рассылку"),]
    ],resize_keyboard=True)



# строитель встроенных кнопок
listInlinCatalog = InlineKeyboardBuilder()

items = ["Футболка","Кроссовки","Шорты"]

for i in items:

    listInlinCatalog.button(text=f'{i}', callback_data=f'{i}')

listInlinCatalog.adjust(3) # умещает три кнопки в одной строке row





# Один обработчик инлайн клавиатуры
# ===============================

# @dp.callback_query(F.data == "Футболка")
# async def send_Tshort(callback: types.CallbackQuery):
#     await callback.message.answer(text="вы выбрали футболку")

# @dp.callback_query(F.data == "Кроссовки")
# async def send_snikcers(callback: types.CallbackQuery):
#     await callback.message.answer(text="вы выбрали Кроссовки")

# @dp.callback_query(F.data == "Шорты")
# async def send_shorts(callback: types.CallbackQuery):
#     await callback.message.answer(text="вы выбрали шорты")

#==================================
# Один обработчик инлайн клавиатуры


#FSM=====================================================================================================

# задаеться переменные состояния fsm 

class addOrder(StatesGroup):

    type = State()

    name = State()

    desc = State()

    price = State()

    photo = State()



@dp.message(F.text == "Добавить товар")

async def admin_add_new_order(message: types.Message, state: FSMContext) -> None:# FSM обязательно

    if message.from_user.id == int(ADMIN):  

        await state.set_state(addOrder.type) # установить состояние переменной type 

        await message.answer(F"Выберите тип товара",reply_markup= listInlinCatalog.as_markup(resize_keyboard=True)) # вызывать клавиатуру "Каталог")

    else:

        await message.answer(F'Что то пошло не так Извините')


@dp.callback_query(addOrder.type)# принимает если отправлен state машины 

async def add_item_type(callback: types.CallbackQuery, state: FSMContext):

    await state.update_data(type = callback.data)# обновить переменную состояния

    await state.set_state(addOrder.name)

    await bot.send_message(chat_id=callback.from_user.id, text='Введите название товара')



@dp.message(addOrder.name)

async def add_name_item(message: types.Message, state: FSMContext) -> None:# FSM обязательно

    await state.update_data(name=message.text)

    await state.set_state(addOrder.price)

    await message.answer(f'Введите теперь цену товара', reply_markup=cancel)


@dp.message(addOrder.price)

async def add_photo_item(message: types.Message, state: FSMContext) -> None:# FSM обязательно

    await state.update_data(price=message.text)

    await state.set_state(addOrder.photo)

    await message.answer(f'Загрузите фотографию товара', reply_markup=cancel)



#проверка если пользователь отправил не фотографию!
@dp.message(addOrder.photo)

async def add_photo_item(message: types.Message, state: FSMContext):

    if not message.photo:

        await message.answer(f'Это не фото! Отппавьте фотографию!', reply_markup=cancel)
    else:

        photo_file_id = message.photo[-1].file_id # переменная в которой будет храниться фото в телеграме ( -1 это фото в последнем качестве )

        await state.update_data(photo=photo_file_id) # обновляем стейт на переменную фото 

        data = await state.get_data() # преобразовывает в словарь

        await add_item(data) # выполняем функцию по добавлению в базу данных
    
        await message.answer(f"Добавлен!  {data['name']}", reply_markup=cancel)

        await state.clear() # заканчивает диалог fsm

      



#FSM======================================================================================================================



@dp.callback_query() #хендлер по отловке коллбек функций

async def callback_qury_keyBoard(callback: types.CallbackQuery):

    if callback.data == 'Футболка':# если в переменную data  коллбэк функции 

        a = await search_in_items()

        await bot.send_message(chat_id=callback.from_user.id, text=a)# ответ по id нажавщего инлайн кнопку

    elif callback.data == 'Кроссовки':# если в переменную data  коллбэк функции

        await bot.send_message(chat_id=callback.from_user.id, text='Вы выбрали кроссовки')# ответ по id нажавщего инлайн кнопку

    elif callback.data == 'Шорты':# если в переменную data  коллбэк функции

        await bot.send_message(chat_id=callback.from_user.id, text='Вы выбрали шорты')# ответ по id нажавщего инлайн кнопку

#==================================






@dp.message(CommandStart())
async def echo_handler(message: types.Message) -> None:
    await cmd_start_db(message.from_user.id) # функция делает запрос в базу для добавления нового пользователя в id_tg по индетефикатору
    await message.answer(f"Добро пожаловать, {hbold(message.from_user.full_name)}!", reply_markup=keyboardMain)

    if message.from_user.id == int(ADMIN):  # если id совпадает открывается админклавиатура

        await message.answer(f"Вы авторизовались как администратор, {hbold(message.from_user.full_name)}", reply_markup=panel_admin)




@dp.message(F.text == 'Каталог')

async def catalog(message: types.Message) -> None:

    await message.answer(f"Корзина пуста!", reply_markup=listInlinCatalog.as_markup(resize_keyboard=True)) # resize_keyb по экрану ширины записывать тут



@dp.message(F.text == 'Корзина')

async def cart(message: types.Message) -> None:

    await message.answer(f"корзина пуста!")



@dp.message(F.text == 'Контакты')

async def contacts(message: types.Message) -> None:

    await message.answer(f"Товары покупать у него @nikolazzzer")


@dp.message(F.text == "Админ-панель")

async def admin(message: types.Message) -> None:

    if message.from_user.id == int(ADMIN):  # проверка пользователя если откроет кнопку админ-панель

        await message.answer(F"Вы вошли в админ панель",reply_markup=keyboardAdminPanel)
    else:

        await message.answer(f'Вы вошли как обычный пользователь! Авторизуйтесь!')







async def main() -> None:

    await bot(DeleteWebhook(drop_pending_updates=True))# skip_updates = Tru сбрасывает обновления когда бот выключен

    await db_start()

    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())


