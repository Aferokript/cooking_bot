import telebot
import os
from telebot.apihelper import ApiTelegramException
from telebot.types import ReplyKeyboardMarkup
import random
from dotenv import load_dotenv
import requests
import sqlite3


DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER,
                    dish_id INTEGER,
                    PRIMARY KEY (user_id, dish_id)
                 )''')
    conn.commit()
    conn.close()

init_db()


cooking_menu = [
    {
        "id": 1,
        "photo": r"C:\Users\Admin\Python312\pythonProject\dishes_images",
        "name": "Имя Блюда",
        "ingredients": [
            {"name": "Имя ингредиента", "price": 0},
            {"name": "Имя ингредиента", "price": 0},
            {"name": "Имя ингредиента", "price": 0}
        ],
        "price": 0,
        "instructions": '',
    },
    {
        "id": 2,
        "photo": None,
        "name": "Борщ",
        "ingredients": [
            {"name": "Имя ингредиента", "price": 0},
            {"name": "Имя ингредиента", "price": 0},
            {"name": "Имя ингредиента", "price": 0}
        ],
        "price": 290,
        "instructions": '',
    },
]

user_free_dishes = {}

users_favorite_dishes = {}

users_current_dishes = {}

load_dotenv()

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

managers_menu = ReplyKeyboardMarkup(resize_keyboard=True)
managers_menu.row('➕ Добавить блюдо', '🗑️ Удалить блюдо')

users_main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
users_main_menu.row('🍽️ Показать блюдо', '⭐ Добавить в избранное')
users_main_menu.row('📋 Посмотреть избранные блюда', '💎 Купить бесконечные просмотры')


managers_id = {1341390157} # мужики не путайтесь, это такое множество


def get_random_dish():
    if not cooking_menu:
        return None
    return random.choice(cooking_menu)


def get_formatted_dishes(dishes):
    for dish in dishes:
        name = dish.get('name')
        ingredients_list = []
        for ingredient in dish.get('ingredients'):
            ingredient_name = ingredient.get('name')
            ingredient_price = ingredient.get('price')
            ingredients_list.append(f"{ingredient_name} ({ingredient_price} руб.)")

        ingredients_str = "\n".join(ingredients_list)
        price = dish.get('price')
        instructions = dish.get('instructions')
        photo = dish.get('photo')
        
        text = (f"🍽️ {name}\n\n"
                f"📝 Ингредиенты:\n{ingredients_str}\n\n"
                f"💰 Стоимость: {price} руб.\n\n"
                f"👨‍🍳 Приготовление:\n{instructions}")
        if photo:
            text += f"\n\n🖼️ Фото: {photo}"
        yield text


def add_to_favorite(message):
    user_id = message.chat.id
    current_dish = users_current_dishes.get(user_id)
    if not current_dish:
        bot.send_message(user_id, "❌ Вы ещё не смотрели ни одного блюда! 👀")
        return

    dish_id = current_dish["id"]
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favorites WHERE user_id = ? AND dish_id = ?", (user_id, dish_id))
    if cursor.fetchone():
        bot.send_message(user_id, "⚠️ Это блюдо уже в избранном!")
    else:
        cursor.execute("INSERT INTO favorites (user_id, dish_id) VALUES (?, ?)", (user_id, dish_id))
        conn.commit()
        bot.send_message(user_id, "⭐ Блюдо добавлено в избранное! ✅")
    conn.close()


def show_dishes_logic(message, user_id):
    random_dish = get_random_dish()
    if user_id not in user_free_dishes:
        user_free_dishes[user_id] = 3

    if user_free_dishes[user_id] > 0:
        for text in get_formatted_dishes([random_dish]):
            bot.send_message(message.chat.id, text)
        user_free_dishes[user_id] -= 1
        users_current_dishes[user_id] = random_dish
    else:
        bot.send_message(message.chat.id, '💸 Ваши бесплатные просмотры закончились! 😢\n\nКупите подписку, чтобы продолжить ✨')


def show_favorite_dishes(message):
    user_id = message.chat.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT dish_id FROM favorites WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        bot.send_message(user_id, "📭 У вас пока нет избранных блюд 😢\n\n⭐ Нажмите 'Добавить в избранное' при просмотре блюда")
        return

    favorite_ids = {row[0] for row in rows}
    favorite_dishes = [dish for dish in cooking_menu if dish["id"] in favorite_ids]

    for text in get_formatted_dishes(favorite_dishes):
        bot.send_message(user_id, text)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id in managers_id:
        bot.send_message(message.chat.id,  '👋 С возвращением, администратор!', reply_markup=managers_menu, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, '🍳 Добро пожаловать!\n\nВыбирайте уникальные блюда на ваш выбор 👨‍🍳',reply_markup=users_main_menu)


@bot.message_handler(func=lambda message: message.text == '🍽️ Показать блюдо')
def show_dishes(message):
    user_id = message.chat.id

    try:
        show_dishes_logic(message, message.chat.id)
    except ApiTelegramException:
        bot.send_message(user_id, '⚠️ Слишком много запросов, попробуйте позже ⚠️')
    except requests.exceptions.RequestException:
        bot.send_message(user_id, '⚠️ Проблемы на стороне сервера, приносим свои извинения')


@bot.message_handler(func=lambda message: message.text == '⭐ Добавить в избранное')
def add_favorite(message):
    user_id = message.chat.id

    try:
        add_to_favorite(message)
    except ApiTelegramException:
        bot.send_message(user_id, '⚠️ Слишком много запросов, попробуйте позже')
    except requests.exceptions.RequestException:
        bot.send_message(user_id, '⚠️ Проблемы на стороне сервера, приносим свои извинения ⚠️')


@bot.message_handler(func=lambda message: message.text == '📋 Посмотреть избранные блюда')
def show_favorite(message):
    user_id = message.chat.id

    try:
        show_favorite_dishes(message)
    except ApiTelegramException:
        bot.send_message(user_id, '⚠️ Слишком много запросов, попробуйте позже')
    except requests.exceptions.RequestException:
        bot.send_message(user_id, '⚠️ Проблемы на стороне сервера, приносим свои извинения ⚠️')


bot.infinity_polling(interval=3)
