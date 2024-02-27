from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from loader import dp, bot
from services.sql import DataBase
from keyboards.keyboards import menu

db = DataBase('stock.db')


@dp.message_handler(Command('start'))
async def start(message: Message):
    try:
        await db.add_users(message.chat.id, message.chat.first_name)
    except Exception as e:
        pass
    finally:
        main_image = open("image/main.jpg", "rb")
        await bot.send_photo(message.chat.id, photo=main_image,
                             caption="💨 Here you can write a description of your company 💨 \n\n🔥 <b>And here you can also address the user</b> 🔥",
                             reply_markup=menu)
