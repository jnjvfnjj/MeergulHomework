from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from config import token
import os, time, logging, sqlite3

bot = Bot(token = token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

connection = sqlite3.connect('baza.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS baza(
               id INTEGER,
               username VARCHAR (100),
               first_name VARCHAR (100),
               last_name VARCHAR (200),
               date_joined INTEGER
)''')

button = [
    types.KeyboardButton('меню'),
    types.KeyboardButton('о нас'),
    types.KeyboardButton('адрес'),
    types.KeyboardButton('заказать еду'),
]
direction_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*button)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    cursor = connection.cursor()
    cursor.execute(f'SELECT id FROM baza WHERE id = {message.from_user.id}')
    result = cursor.fetchall()
    if result == []:
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO baza (id, username, first_name, last_name, date_joined) VALUES ({message.from_user.id}, "{message.from_user.username}", "{message.from_user.first_name}", "{message.from_user.last_name}", "{time.ctime()}");')
        cursor.connection.commit()
    await message.answer(f"Привет, {message.from_user.full_name}!")
    await message.answer(f'Выбери действие:',reply_markup=direction_keyboard)

@dp.message_handler(text='меню')
async def meny(message:types.Message):
    await message.answer("https://nambafood.kg/ojak-kebap")

@dp.message_handler(text = 'о нас')
async def about_us(message:types.Message):
    await message.answer("https://ocak.uds.app/c/about")

@dp.message_handler(text = 'адрес')
async def adress(message:types.Message):
    await message.answer("​Исы Ахунбаева, 97а, ​9 филиалов. Октябрьский район, Бишкек, 720064, 2 этажа")

class MailingState(StatesGroup):
    text = State()

@dp.message_handler(commands='mailing')
async def send_mailing(message:types.Message):
    if message.from_user.id in [6290198014, ]:
        await message.answer("Введите текст для рассылки")
        await MailingState.text.set()
    else:
        await message.answer(" У вас нету домтупа")

@dp.message_handler(state=MailingState.text)
async def send_mailing_text(message:types.Message, state:FSMContext):
    cursor.execute("SELECT id FROM baza;")
    users_id = cursor.fetchall()
    for user in users_id:
        await bot.send_message(user[0], message.text)
    await state.finish()

class EnrollState(StatesGroup):
    name = State()
    phone = State()
    adress = State()
 


@dp.message_handler(text='заказать еду')
async def get_food(message:types.Message):
    await message.reply("Для доставки еды нам нужно узнать,")
    await message.answer("Ваше имя:")
    await EnrollState.name.set()

@dp.message_handler(state=EnrollState.name)
async def names(message:types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Ваш телефонный номер:')
    await EnrollState.phone.set()

@dp.message_handler(state=EnrollState.phone)
async def phones(message:types.Message, state:FSMContext):
    await state.update_data(phone=message.text)
    await message.answer('Ваш адрес: ')
    await EnrollState.adress.set()

cursor.execute('''CREATE TABLE IF NOT EXISTS come_food(
               name VARCHAR(100),
               phone INTEGER,
               adress VARCHAR (500)
)''')

cursor = connection.cursor()
@dp.message_handler(state=EnrollState.adress)
async def adresses(message:types.Message, state:FSMContext):
    await state.update_data(adress=message.text)
    await message.answer('Данные были успешно записаныб скоро с вами свяжутся :)')
    cursor = connection.cursor()
    cursor.execute(f'INSERT INTO come_food (name, phone, adress) VALUES ("{message.text}", "{message.text}", "{message.text}")')
    connection.commit()
    await state.finish()
executor.start_polling(dp, skip_updates = True)
