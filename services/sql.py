from config import admin
import sqlite3


class DataBase:
    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    async def add_users(self, user_id, name):
        with self.connect:
            return self.cursor.execute("""INSERT INTO users (user_id, name, role) VALUES (?, ?, ?)""",
                                       [user_id, name, 'admin' if user_id == admin else 'user'])

    async def get_categories(self):
        with self.connect:
            return self.cursor.execute("""SELECT DISTINCT category FROM products""").fetchall()

    async def get_subcategories(self, category):
        with self.connect:
            return self.cursor.execute("""SELECT DISTINCT subcategory FROM products WHERE category=(?)""", [category]).fetchall()

    async def get_tastes(self, category, subcategory):
        with self.connect:
            return self.cursor.execute("""SELECT taste FROM products WHERE category=(?) AND subcategory=(?)""", [category, subcategory]).fetchall()

    async def get_photo(self, category, subcategory, taste):
        with self.connect:
            return self.cursor.execute("""SELECT photo FROM products WHERE category=(?) AND subcategory=(?) AND taste=(?)""", [category, subcategory, taste]).fetchall()

    async def get_price(self, category, subcategory, taste):
        with self.connect:
            return self.cursor.execute("""SELECT price FROM products WHERE category=(?) AND subcategory=(?) AND taste=(?)""", [category, subcategory, taste]).fetchall()

    async def add_to_cart(self, user_id, category, subcategory, taste, price):
        with self.connect:
            return self.cursor.execute("""INSERT INTO cart (user_id, category, subcategory, taste, count, price) VALUES (?, ?, ?, ?, ?, ?)""",
                                       [user_id, category, subcategory, taste, 1, price]), self.cursor.execute("""INSERT INTO orders (user_id, category, subcategory, taste, count, price) VALUES (?, ?, ?, ?, ?, ?)""",
                                       [user_id, category, subcategory, taste, 1, price])

    async def get_cart(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT category, subcategory, taste, count, price FROM cart WHERE user_id=(?)""", [user_id]).fetchall()

    async def get_count_in_cart(self, user_id, category, subcategory, taste):
        with self.connect:
            return self.cursor.execute("""SELECT count FROM cart WHERE user_id=(?) AND category=(?) AND subcategory=(?) AND taste=(?)""",
                                       [user_id, category, subcategory, taste]).fetchall()

    async def get_count_in_stock(self, category, subcategory, taste):
        with self.connect:
            return self.cursor.execute("""SELECT count FROM products WHERE category=(?) AND subcategory=(?) AND 
                taste=(?)""", [category, subcategory, taste]).fetchall()

    async def change_count(self, count, category, subcategory, taste, user_id):
        with self.connect:
            return self.cursor.execute("""UPDATE cart SET count=(?) WHERE category=(?) AND subcategory=(?) AND taste=(?) AND user_id=(?)""",
                                       [count, category, subcategory, taste, user_id]), self.cursor.execute("""UPDATE orders SET count=(?) WHERE category=(?) AND subcategory=(?) AND taste=(?) AND user_id=(?)""",
                                       [count, category, subcategory, taste, user_id])

    async def empty_cart(self, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE FROM cart WHERE user_id=(?)""", [user_id]), self.cursor.execute("""DELETE FROM orders WHERE user_id=(?)""", [user_id])

    async def empty(self, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE FROM cart WHERE user_id=(?)""", [user_id])

    async def get_order(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT category, subcategory, taste, count FROM orders WHERE user_id=(?)""", [user_id]).fetchall()

    async def change_products_count(self, count, category, subcategory, taste):
        with self.connect:
            return self.cursor.execute("""UPDATE products SET count=(?) WHERE category=(?) AND subcategory=(?) AND taste=(?)""",
                                       [count, category, subcategory, taste])

    async def empty_order(self, user_id):
        with self.connect:
            self.cursor.execute("""DELETE FROM orders WHERE user_id=(?)""", [user_id])

    async def add_product(self, category, subcategory, taste, count, photo, price):
        with self.connect:
            return self.cursor.execute("""INSERT INTO products (category, subcategory, taste, count, photo, price) VALUES (?, ?, ?, ?, ?, ?)""",
                                       [category, subcategory, taste, count, photo, price])

    async def delete_product(self, category, subcategory, taste):
        with self.connect:
            return self.cursor.execute("""DELETE FROM products WHERE category=(?) AND subcategory=(?) AND taste=(?)""",
                                       [category, subcategory, taste])