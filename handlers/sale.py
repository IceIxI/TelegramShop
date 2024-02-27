from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.utils.callback_data import CallbackData
from services.sql import DataBase
from bot import dp
from keyboards.keyboards import menu
from loader import bot

cb = CallbackData('btn', 'type', 'category', 'subcategory', 'product')
db = DataBase('stock.db')


@dp.callback_query_handler(lambda callback_query: callback_query.data == "catalog")
async def categories(call: CallbackQuery):
    data = await db.get_categories()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in data:
        keyboard.insert(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:category:{i[0]}:-:-'))
    keyboard.row(InlineKeyboardButton(text='\U00002B05 Back', callback_data=f'btn:back_to_begin:-:-:-'))
    await call.message.edit_caption(caption="\U0001F680 Choose a category:",
                                    reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(cb.filter(type='category'))
async def subcategories(call: CallbackQuery, callback_data: dict):
    category_name = callback_data.get('category')
    data = await db.get_subcategories(category_name)
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in data:
        keyboard.insert(
            InlineKeyboardButton(text=f'{i[0]} \U0001F4A8', callback_data=f'btn:subcategory:{category_name}:{i[0]}:-'))
    keyboard.row(InlineKeyboardButton(text='\U00002B05 Back', callback_data=f'btn:back_to_category:-:-:-'))

    await call.message.edit_caption(caption="\U0001F4A8 Choose a subcategory:",
                                    reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(cb.filter(type='subcategory'))
async def products(call: CallbackQuery, callback_data: dict):
    category_name = callback_data.get('category')
    subcategory_name = callback_data.get('subcategory')
    data = await db.get_tastes(category_name, subcategory_name)
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in data:
        keyboard.insert(
            InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:product:{category_name}:{subcategory_name}:{i[0]}'))
    keyboard.row(InlineKeyboardButton(text='\U00002B05 Back', callback_data=f'btn:back_to_subcategory:{category_name}:-:-'))

    await call.message.edit_caption(caption="\U0001F924 Choose a option:",
                                 reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(cb.filter(type='product'))
async def card_of_product(call: CallbackQuery, callback_data: dict):
    try:
        category = callback_data.get('category')
        subcategory = callback_data.get('subcategory')
        product = callback_data.get('product')
        photo = await db.get_photo(callback_data.get('category'), callback_data.get('subcategory'), callback_data.get('product'))
        count_in_cart = await db.get_count_in_cart(call.message.chat.id, category, subcategory, product)
        count_in_stock = await db.get_count_in_stock(callback_data.get('category'), callback_data.get('subcategory'),
                                                     callback_data.get('product'))
        if count_in_stock[0][0] == 0:
            await bot.answer_callback_query(callback_query_id=call.id, text="Item is out of stock", show_alert=False)
            await call.answer()
            return 0
        elif not count_in_cart or count_in_cart[0][0] == 0 or count_in_cart[0][0] < count_in_stock[0][0]:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="\U00002705 Add to cart",
                                              callback_data=f'btn:add:{callback_data.get("category")}:{callback_data.get("subcategory")}:{callback_data.get("product")}'))
            keyboard.add(InlineKeyboardButton(text="\U00002B05 Back", callback_data=f'btn:back_to_products:{callback_data.get("category")}:{callback_data.get("subcategory")}:-'))
            await call.message.edit_media(media=InputMediaPhoto(photo[0][0]))
            await call.message.edit_caption(f"<b>{category}</b> {subcategory} {product}", reply_markup=keyboard)
            await call.answer()
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="Item is out of stock", show_alert=False)
            await call.answer()
            return 0
    except Exception:
        await bot.answer_callback_query(callback_query_id=call.id, text="Error!", show_alert=False)


@dp.callback_query_handler(cb.filter(type='add'))
async def add_to_cart(call: CallbackQuery, callback_data: dict):
    try:
        category = callback_data.get('category')
        subcategory = callback_data.get('subcategory')
        product = callback_data.get('product')
        price = await db.get_price(category, subcategory, product)
        count_in_cart = await db.get_count_in_cart(call.message.chat.id, category, subcategory, product)
        count_in_stock = await db.get_count_in_stock(callback_data.get('category'), callback_data.get('subcategory'),
                                                     callback_data.get('product'))
        if not count_in_cart or count_in_cart[0][0] == 0:
            await db.add_to_cart(call.message.chat.id, category, subcategory, product, price[0][0])
            await bot.answer_callback_query(callback_query_id=call.id, text="Item added to your cart!", show_alert=True)
            await call.answer()
        elif count_in_cart[0][0] < count_in_stock[0][0]:
            await db.change_count(count_in_cart[0][0] + 1, category, subcategory, product, call.message.chat.id)
            await bot.answer_callback_query(callback_query_id=call.id, text="Item added to your cart!", show_alert=True)
            await call.answer()
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="Item is out of stock", show_alert=False)
            await call.answer()
            return 0
    except Exception:
        await bot.answer_callback_query(callback_query_id=call.id, text="Error!", show_alert=False)


@dp.callback_query_handler(cb.filter(type='back_to_begin'))
async def back_to_begin(call: CallbackQuery):
    await call.message.edit_caption(caption="💨 Here you can write a description of your company 💨 \n\n🔥 <b>And here you can also address the user</b> 🔥",
                                    reply_markup=menu)
    await call.answer()


@dp.callback_query_handler(cb.filter(type='back_to_main'))
async def back_to_main(call: CallbackQuery):
    logo = open("image/main.jpg", "rb")
    await call.message.edit_media(media=InputMediaPhoto(logo))
    await call.message.edit_caption(caption="💨 Here you can write a description of your company 💨 \n\n🔥 <b>And here you can also address the user</b> 🔥",
                                    reply_markup=menu)
    await call.answer()


@dp.callback_query_handler(cb.filter(type='back_to_category'))
async def back_to_category(call: CallbackQuery):
    data = await db.get_categories()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in data:
        keyboard.insert(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:category:{i[0]}:-:-'))
    keyboard.row(InlineKeyboardButton(text='\U00002B05 Back', callback_data=f'btn:back_to_begin:-:-:-'))
    await call.message.edit_caption(caption="\U0001F680 Choose a category:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(cb.filter(type='back_to_subcategory'))
async def back_to_subcategory(call: CallbackQuery, callback_data: dict):
    category_name = callback_data.get('category')
    data = await db.get_subcategories(category_name)
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in data:
        keyboard.insert(
            InlineKeyboardButton(text=f'{i[0]} \U0001F4A8', callback_data=f'btn:subcategory:{category_name}:{i[0]}:-'))
    keyboard.row(InlineKeyboardButton(text='\U00002B05 Back', callback_data=f'btn:back_to_category:-:-:-'))

    await call.message.edit_caption(caption="\U0001F4A8 Choose a subcategory:",
                                 reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(cb.filter(type='back_to_products'))
async def back_to_products(call: CallbackQuery, callback_data: dict):
    category_name = callback_data.get('category')
    subcategory_name = callback_data.get('subcategory')
    data = await db.get_tastes(category_name, subcategory_name)
    logo = open("image/main.jpg", "rb")
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in data:
        keyboard.insert(
            InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:product:{category_name}:{subcategory_name}:{i[0]}'))
    keyboard.row(InlineKeyboardButton(text='\U00002B05 Back', callback_data=f'btn:back_to_subcategory:{category_name}:-:-'))
    await call.message.edit_media(media=InputMediaPhoto(logo))
    await call.message.edit_caption(caption="\U0001F924 Choose a option:",
                                 reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data == "cart")
async def show_cart(call: CallbackQuery):
    cart = await db.get_cart(call.message.chat.id)
    order_sum = 0
    cart_photo = open("image/cart.jpg", "rb")
    if cart:
        str_cart = "<b>SHOPPING CART</b> \U0001F6D2 \n\n"

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="\U00002705 Order", callback_data=f'btn:buy:-:-:-'))
        keyboard.add(InlineKeyboardButton(text="\U0000274C Empty", callback_data=f'btn:empty:-:-:-'))
        keyboard.add(InlineKeyboardButton(text="\U00002B05 Back", callback_data=f'btn:back_to_main:-:-:-'))

        for i in cart:
            str_cart += f"{i[0]} {i[1]} {i[2]} - {i[3]} pcs. \n"
            order_sum += (i[4] * i[3])
        str_cart += f"\n<b>TOTAL AMOUNT</b> - {order_sum} Euro"
        await call.message.edit_media(media=InputMediaPhoto(cart_photo))
        await call.message.edit_caption(caption=str_cart, reply_markup=keyboard)
        await call.answer()
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text="Shopping cart is empty!", show_alert=True)
        await call.answer()


@dp.callback_query_handler(cb.filter(type='empty'))
async def empty(call: CallbackQuery):
    logo = open("image/main.jpg", "rb")
    await db.empty_cart(call.message.chat.id)
    await bot.answer_callback_query(callback_query_id=call.id, text="Shopping cart cleared!", show_alert=True)
    await call.message.edit_media(media=InputMediaPhoto(logo))
    await call.message.edit_caption(caption="💨 Here you can write a description of your company 💨 \n\n🔥 <b>And here you can also address the user</b> 🔥",
                                    reply_markup=menu)
    await call.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data == "support")
async def support(call: CallbackQuery):
    support_photo = open("image/support.jpg", "rb")
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Write to support",
                                      url="t.me/"),
                 InlineKeyboardButton(text="\U00002B05 Back", callback_data=f'btn:back_to_main:-:-:-'))
    await call.message.edit_media(media=InputMediaPhoto(support_photo))
    await call.message.edit_caption(caption="<b>Click the button below to contact the administrator</b> \U0000260E ", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data == "reviews")
async def reviews(call: CallbackQuery):
    reviews_photo = open("image/reviews.jpg", "rb")
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Go to the group with reviews",
                                      url="t.me/"),
                 InlineKeyboardButton(text="\U00002B05 Back", callback_data=f'btn:back_to_main:-:-:-'))
    await call.message.edit_media(media=InputMediaPhoto(reviews_photo))
    await call.message.edit_caption(caption="<b>Customer reviews</b> \U00002709", reply_markup=keyboard)
    await call.answer()
