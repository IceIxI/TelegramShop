from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


menu_buttons = [
        InlineKeyboardButton(text="\U0001F680 Catalog", callback_data="catalog"),
        InlineKeyboardButton(text="\U0001F6D2 Shopping cart", callback_data="cart"),
        InlineKeyboardButton(text="\U0000260E Support", callback_data="support"),
        InlineKeyboardButton(text="\U00002709 Reviews", callback_data="reviews"),
    ]


menu = InlineKeyboardMarkup(row_width=2)
menu.add(*menu_buttons)
