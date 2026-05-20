import telebot
import os
from telebot.types import ReplyKeyboardMarkup
import random


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
        "Общая стоимость": 0,
        "Инструкция приготовления": '',
    },
]

managers_id = {7280963930} # мужики не путайтесь, это такое множество

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

managers_menu = ReplyKeyboardMarkup()
managers_menu.row('Добавить блюдо', 'Удалить блюдо')

users_main_menu = ReplyKeyboardMarkup()
users_main_menu.row('Посмотреть рецепт', 'Добавить в избранное', 'Купить бесконечные просмотры')


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in managers_id:
        bot.send_message(message.chat.id, 'С возвращением, администратор', reply_markup=managers_menu)
    else:
        bot.send_message(message.chat.id, 'Выбирайте уникальные меню на ваш выбор!', reply_markup=users_main_menu)


bot.polling()