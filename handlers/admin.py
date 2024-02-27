from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

from services.sql import DataBase
from keyboards.keyboards import menu
from bot import dp
from loader import bot
from config import admin

cb = CallbackData('btn', 'type', 'category', 'subcategory', 'product')
db = DataBase('stock.db')


@dp.callback_query_handler(cb.filter(type='buy'))
async def send_order(call: CallbackQuery):
    user_id = call.message.chat.id
    cart = await db.get_cart(user_id)
    order_sum = 0
    if cart:
        try:
            str_cart = f"<b>ORDER</b>\n\nUser ID: {call.message.chat.id}\n" \
                       f"Username: {call.message.chat.username}\n\nProducts:\n"

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                text="Write to user", url=f"https://t.me/{call.message.chat.username}"))
            keyboard.add(
                InlineKeyboardButton(text="\U00002705 Complete order", callback_data=f'btn:complete:{user_id}:-:-'))
            keyboard.add(
                InlineKeyboardButton(text="\U0000274C Cancel order", callback_data=f'btn:cancel:{user_id}:-:-'))

            for i in cart:
                str_cart += f"{i[0]} {i[1]} {i[2]} - {i[3]} шт \n"
                order_sum += (i[4] * i[3])
            str_cart += f"\n<b>TOTAL AMOUNT</b> - {order_sum} Euros"
            await bot.send_message(admin, str_cart, reply_markup=keyboard)
            await db.empty(call.message.chat.id)
            await bot.answer_callback_query(callback_query_id=call.id, text="Order has been sent to the manager!\nYou will be contacted shortly", show_alert=True)
            logo = open("image/main.jpg", "rb")
            await call.message.edit_media(media=InputMediaPhoto(logo))
            await call.message.edit_caption(caption="This will include a welcome and a description of your company",
                                            reply_markup=menu)
            await call.answer()
        except Exception:
            await bot.answer_callback_query(callback_query_id=call.id, text="Error!", show_alert=False)
            await call.answer()
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text="Error!", show_alert=False)
        await call.answer()


@dp.callback_query_handler(cb.filter(type='complete'))
async def complete(call: CallbackQuery, callback_data: dict):
    user_id = callback_data.get("category")
    order = await db.get_order(user_id)
    if order:
        for i in order:
            try:
                category = i[0]
                subcategory = i[1]
                product = i[2]
                count = i[3]
                count_in_stock = await db.get_count_in_stock(category, subcategory, product)

                if count < count_in_stock[0][0]:
                    await db.change_products_count(count_in_stock[0][0]-count, category, subcategory, product)
                    await bot.answer_callback_query(callback_query_id=call.id, text="The order was completes!", show_alert=True)
                    await call.message.delete()
                else:
                    await db.delete_product(category, subcategory, product)
                    await bot.answer_callback_query(callback_query_id=call.id, text="The order was completes!", show_alert=True)
                    await call.message.delete()
                await db.empty_order(user_id)
                await call.answer()
            except Exception:
                await bot.answer_callback_query(callback_query_id=call.id, text="Error!", show_alert=False)
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text="Error!", show_alert=False)
        await call.answer()


@dp.callback_query_handler(cb.filter(type='cancel'))
async def cancel(call: CallbackQuery, callback_data: dict):
    user_id = callback_data.get("category")
    await db.empty_order(user_id)
    await bot.answer_callback_query(callback_query_id=call.id, text="The order was canceled!", show_alert=True)
    await call.message.delete()
    await call.answer()


@dp.message_handler(commands="edit")
async def edit(message: Message):
    if message.from_user.id == admin:
        keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Add product \U00002705"))
        keyboard.add(KeyboardButton(text="Delete product \U0000274C"))
        keyboard.add(KeyboardButton(text="Close admin panel"))
        await message.answer(text="<b>WHAT YOU CAN DO \U0001F447</b>", reply_markup=keyboard)
    else:
        await message.answer("This command is only available to the administrator")


class FSMAdmin(StatesGroup):
    category = State()
    subcategory = State()
    product = State()
    count = State()
    price = State()
    photo = State()

    del_category = State()
    del_subcategory = State()
    del_taste = State()


@dp.message_handler(lambda m: m.text == "Add product \U00002705")
async def start_add(message: Message):
    if message.from_user.id == admin:
        keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Cancel"))
        await FSMAdmin.category.set()
        await message.answer("\U0001F680 Enter product name", reply_markup=keyboard)
    else:
        await message.answer("This command is only available to the administrator")


@dp.message_handler(lambda m: m.text == "Delete product \U0000274C")
async def start_delete(message: Message):
    if message.from_user.id == admin:
        keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Cancel"))
        await FSMAdmin.del_category.set()
        await message.answer("\U0001F680 Enter product name", reply_markup=keyboard)
    else:
        await message.answer("This command is only available to the administrator")


@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cancel(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Add product \U00002705"))
        keyboard.add(KeyboardButton(text="Delete product \U0000274C"))
        keyboard.add(KeyboardButton(text="Close admin panel"))
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.answer("<b>\U0000274C Operation was canceled</b>", reply_markup=keyboard)
    else:
        await message.answer("This command is only available to the administrator")


@dp.message_handler(lambda m: m.text == "Close admin panel")
async def close_admin_keyboard(message: Message):
    if message.from_user.id == admin:
        await message.answer(text="<b>\U0000274C Admin panel was closed</b>", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("This command is only available to the administrator")


@dp.message_handler(state=FSMAdmin.category)
async def load_category(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        async with state.proxy() as data:
            data['category'] = message.text
        await FSMAdmin.next()
        await message.answer("\U0001F4A8 Enter a subcategory")


@dp.message_handler(state=FSMAdmin.subcategory)
async def load_subcategory(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        async with state.proxy() as data:
            try:
                data['subcategory'] = int(message.text)
            except Exception:
                keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                keyboard.add(KeyboardButton(text="Add product \U00002705"))
                keyboard.add(KeyboardButton(text="Delete product \U0000274C"))
                keyboard.add(KeyboardButton(text="Close admin panel"))
                await message.answer(
                    "<b>COUNT MUST BE A NUMBER \U0000203C</b>\nThe add function is disabled, try again", reply_markup=keyboard)
                await state.finish()
                return
        await FSMAdmin.next()
        await message.answer("\U0001F924 Enter option")

@dp.message_handler(state=FSMAdmin.product)
async def load_product(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        async with state.proxy() as data:
            data['product'] = message.text
        await FSMAdmin.next()
        await message.answer("\U0001F4AF Enter count")


@dp.message_handler(state=FSMAdmin.count)
async def load_count(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        async with state.proxy() as data:
            try:
                data['count'] = int(message.text)
            except Exception:
                keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                keyboard.add(KeyboardButton(text="Add product \U00002705"))
                keyboard.add(KeyboardButton(text="Delete product \U0000274C"))
                keyboard.add(KeyboardButton(text="Close admin panel"))
                await message.answer(
                    "<b>COUNT MUST BE A NUMBER \U0000203C</b>\nThe add function is disabled, try again", reply_markup=keyboard)
                await state.finish()
                return
        await FSMAdmin.next()
        await message.answer("\U0001F4B5 Enter price")


@dp.message_handler(state=FSMAdmin.price)
async def load_price(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        async with state.proxy() as data:
            try:
                data['price'] = int(message.text)
            except Exception:
                keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                keyboard.add(KeyboardButton(text="Add product \U00002705"))
                keyboard.add(KeyboardButton(text="Delete product \U0000274C"))
                keyboard.add(KeyboardButton(text="Close admin panel"))
                await message.answer(
                    "<b>COUNT MUST BE A NUMBER \U0000203C</b>\nThe add function is disabled, try again", reply_markup=keyboard)
                await state.finish()
                return
        await FSMAdmin.next()
        await message.answer("\U0001F4F7 Enter url of image")


@dp.message_handler(state=FSMAdmin.photo)
async def load_photo(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Add product \U00002705"))
        keyboard.add(KeyboardButton(text="Delete product \U0000274C"))
        keyboard.add(KeyboardButton(text="Close admin panel"))
        async with state.proxy() as data:
            data['photo'] = message.text
            try:
                category = data['category']
                subcategory = data['subcategory']
                product = data['product']
                count = data['count']
                photo = data['photo']
                price = data['price']
                await db.add_product(category, subcategory, product, count, photo, price)
                await message.answer("<b>\U00002705 The product was added</b>",
                                     reply_markup=keyboard)
            except Exception:
                await message.answer("\U0000274C Error", reply_markup=keyboard)
        await state.finish()


@dp.message_handler(state=FSMAdmin.del_category)
async def load_del_category(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        async with state.proxy() as data:
            data['category'] = message.text
        await FSMAdmin.next()
        await message.answer("\U0001F4A8 Enter subcategory")


@dp.message_handler(state=FSMAdmin.del_subcategory)
async def load_del_subcategory(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        async with state.proxy() as data:
            data['subcategory'] = message.text
        await FSMAdmin.next()
        await message.answer("\U0001F924 Enter option")


@dp.message_handler(state=FSMAdmin.del_taste)
async def load_del_product(message: Message, state: FSMContext):
    if message.from_user.id == admin:
        keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Add product \U00002705"))
        keyboard.add(KeyboardButton(text="Delete product \U0000274C"))
        keyboard.add(KeyboardButton(text="Close admin panel"))
        async with state.proxy() as data:
            data['product'] = message.text
            try:
                category = data['category']
                subcategory = data['subcategory']
                taste = data['product']
                await db.delete_product(category, subcategory, taste)
                await message.answer("<b>\U00002705 The product was deleted</b>", reply_markup=keyboard)
            except Exception:
                await message.answer("\U0000274C Error", reply_markup=keyboard)
        await state.finish()
