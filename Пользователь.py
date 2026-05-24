import telebot
from telebot import types
from dotenv import load_dotenv
import os
import random
import uuid


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

user_free_dishes = {}

users_favorite_dishes = {}

users_current_dishes = {}

users_hate_dishes = {}

temporary_dish_to_add = {}

load_dotenv()

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

managers_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
managers_menu.row('➕ Добавить блюдо', '🗑️ Удалить блюдо')
managers_menu.row('🍽️ Показать блюдо', '📋 Посмотреть избранные блюда')
managers_menu.row('⭐ Добавить в избранное', '❌ Удалить из избранного')

users_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
users_menu.row('🍽️ Показать блюдо', '⭐ Добавить в избранное')
users_menu.row('📋 Посмотреть избранные блюда', '❌ Удалить из избранного')
users_menu.row('💎 Купить бесконечные просмотры')

managers_id = {2032289255}


def get_random_dish():
    if not cooking_menu:
        return None
    return random.choice(cooking_menu)


def get_formatted_dishes(dish):
    if not dish:
        return 'Список блюд пуст'
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
    return (f"🍽️ *{name}*\n\n"
            f"📝 *Ингредиенты:*\n{ingredients_str}\n\n"
            f"💰 *Стоимость:* {price} руб.\n\n"
            f"👨‍🍳 *Приготовление:*\n{instructions}\n\n"
            f"🖼️ Фото: {photo}\n")


@bot.message_handler(func=lambda message: message.text == '➕ Добавить блюдо')
def get_user_data_for_dish(message):
    bot.send_message(
        message.chat.id,
        'Введите название блюда'
    )
    bot.register_next_step_handler(message, set_dish_name)


def set_dish_name(message):
    dish_name = message.text
    temporary_dish_to_add['name'] = dish_name
    bot.send_message(
        message.chat.id,
        text='Введите названия ингридиентов и их стоимость как показано ниже:\n'
        'лук 10\n'
        'картофель 70\n'
        'соль 5'
    )
    bot.register_next_step_handler(message, add_dish)
    

def add_dish(message):
    total_price = 0
    temporary_dish_to_add['ingredients'] = []
    for ingredients in message.text.split('\n'):
        ingredient_name, price = ingredients.split()
        total_price += int(price)
        temporary_dish_to_add['ingredients'].append(
            {
                'name': ingredient_name,
                'price': price,
            }
        )

    cooking_menu.append(
        {   
            'id': str(uuid.uuid4()),
            'photo': 'Отсутствует',
            'name': temporary_dish_to_add['name'],
            'ingredients': temporary_dish_to_add['ingredients'],
            'price': total_price,
            'instructions': f'Инструкция для приготовления '
                            f'{temporary_dish_to_add['name']}'
        }
    )
    del_temporary_data()

    bot.send_message(
        message.chat.id,
        text='Блюдо успешно добавлено'
    )


@bot.message_handler(func=lambda message: message.text == '🗑️ Удалить блюдо')
def get_dish_to_delete(message):
    if not cooking_menu:
        bot.send_message(
            message.chat.id,
            text='Список блюд пуст'
        )
        return
    current_dishes = [dish['name'] for dish in cooking_menu]
    bot.send_message(
        message.chat.id,
        f'Введите название блюда для удаления\n'
        f'Список доступных блюд: {', '.join(current_dishes)}\n'
        f'Или введите "Отмена"'
    )
    bot.register_next_step_handler(message, delete_dish)


def delete_dish(message):
    if message.text == 'Отмена':
        bot.send_message(
            message.chat.id,
            text='Удаления отменено'
        )
        return
    
    current_dishes = [dish['name'] for dish in cooking_menu]
    if message.text in current_dishes:
        for dish in cooking_menu:
            if dish['name'] == message.text:
                cooking_menu.remove(dish)

        bot.send_message(
            message.chat.id,
            text='Блюдо успешно удалено'
        )
    else:
        get_dish_to_delete(message)


def del_temporary_data():
    temporary_dish_to_add.clear()


def add_to_favorite(message):
    if not cooking_menu:
        bot.send_message(
            message.chat.id,
            text='Список блюд пуст'
        )
        return
    user_id = message.chat.id

    if user_id in users_current_dishes:
        current_dish = users_current_dishes[user_id]

        if user_id not in users_favorite_dishes:
            users_favorite_dishes[user_id] = []

        if current_dish not in users_favorite_dishes[user_id]:
            users_favorite_dishes[user_id].append(current_dish)
            bot.send_message(user_id, "⭐ Блюдо добавлено в избранное! ✅")
        else:
            bot.send_message(user_id, "⚠️ Это блюдо уже в избранном!")
    else:
        bot.send_message(user_id, "❌ Вы ещё не смотрели ни одного блюда! 👀")


def show_dishes_logic(message):
    user_id = message.chat.id
    random_dish = get_random_dish()
    if user_id not in user_free_dishes:
        user_free_dishes[user_id] = 10

    if user_free_dishes[user_id] > 0:
        bot.send_message(
            user_id,
            get_formatted_dishes(random_dish),
            reply_markup=managers_menu if is_admin(message) else users_menu
        )
        user_free_dishes[user_id] -= 1
        users_current_dishes[user_id] = random_dish
    else:
        bot.send_message(
            message.chat.id,
            '💸 Ваши бесплатные просмотры закончились! \
                😢\n\nКупите подписку, чтобы продолжить ✨'
                )


def show_favorite_dishes(message):
    if not cooking_menu:
        bot.send_message(
            message.chat.id,
            text='Список блюд пуст'
        )
        return
    user_id = message.chat.id
    if user_id not in users_favorite_dishes or not users_favorite_dishes[user_id]:
        bot.send_message(
            user_id,
            "📭 У вас пока нет избранных блюд \
                😢\n\n⭐ Нажмите 'Добавить в избранное' при просмотре блюда"
                )
        return

    for dish in users_favorite_dishes[user_id]:
        bot.send_message(
            user_id,
            get_formatted_dishes(dish),
            reply_markup=managers_menu if is_admin(message) else users_menu
        )


def delete_favorite_dishes(message):
    if not cooking_menu:
        bot.send_message(
            message.chat.id,
            text='Список блюд пуст'
        )
        return
    user_id = message.chat.id

    if user_id not in users_favorite_dishes:
        bot.send_message(user_id, '❌ У вас нет избранных блюд')
        return

    if user_id in users_favorite_dishes:
        del users_favorite_dishes[user_id]
        bot.send_message(user_id, ' Блюдо успешно удалено')


def is_admin(message):
    return message.chat.id in managers_id


@bot.message_handler(commands=['start'])
def start(message):
    if is_admin(message):
        bot.send_message(
            message.chat.id,
            '👋 С возвращением, администратор!',
            reply_markup=managers_menu
        )
    else:
        bot.send_message(
            message.chat.id,
            '🍳 Добро пожаловать!\n\nВыбирайте уникальные блюда на ваш выбор 👨‍🍳',
            reply_markup=users_menu
        )


@bot.message_handler(func=lambda message: message.text == '🍽️ Показать блюдо')
def show_dishes(message):
    show_dishes_logic(message)


@bot.message_handler(func=lambda message: message.text == '⭐ Добавить в избранное')
def add_favorite(message):
    add_to_favorite(message)


@bot.message_handler(func=lambda message: message.text == '❌ Удалить из избранного')
def delete_favorite(message):
    delete_favorite_dishes(message)


@bot.message_handler(func=lambda message: message.text == '📋 Посмотреть избранные блюда')
def show_favorite(message):
    show_favorite_dishes(message)


bot.infinity_polling()
