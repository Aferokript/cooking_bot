import telebot
import os
from telebot.types import ReplyKeyboardMarkup
import random
from dotenv import load_dotenv


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
]

load_dotenv()

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

managers_menu = ReplyKeyboardMarkup(resize_keyboard=True)
managers_menu.row('Добавить блюдо', 'Удалить блюдо')

users_main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
users_main_menu.row('Показать блюдо', 'Добавить в избранное', 'Купить бесконечные просмотры')

managers_id = {1341390157} # мужики не путайтесь, это такое множество

user_free_dishes = {}

users_favorite_dishes = {}


def get_random_dish():
    if not cooking_menu:
        return None
    return random.choice(cooking_menu)


def get_formatted_dishes(dishes):
    for dish in dishes:
        photo = dish.get('photo')
        name = dish.get('name')
        ingredients_list = []
        for ingredient in dish.get('ingredients'):
            ingredient_name = ingredient.get('name')
            ingredient_price = ingredient.get('price')
            ingredients_list.append(f"{ingredient_name} ({ingredient_price} руб.)")

        ingredients_str = "\n".join(ingredients_list)
        price = dish.get('price')
        instructions = dish.get('instructions')
    return (f'{photo}'
            f' Название {name}'
            f' Список ингредиентов: {ingredients_str}'
            f' Общая стоимость: {price},'
            f' Инструкция приготовления: {instructions}')


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id in managers_id:
        bot.send_message(message.chat.id, 'С возвращением, администратор', reply_markup=managers_menu)
    else:
        bot.send_message(message.chat.id, 'Выбирайте уникальные меню на ваш выбор!', reply_markup=users_main_menu)


@bot.message_handler(func=lambda message: message.text == 'Показать блюдо')
def show_dishes(message):
    user_id = message.chat.id
    random_dish = get_random_dish()

    if user_id not in user_free_dishes:
        user_free_dishes[user_id] = 3

    if user_free_dishes[user_id] > 0:
        bot.send_message(message.chat.id, get_formatted_dishes([random_dish]), reply_markup=users_main_menu)
        user_free_dishes[user_id] -= 1

    else:
        bot.send_message(message.chat.id, 'Ваши бесплатные просмотры закончились! Купите подписку')


bot.infinity_polling()
