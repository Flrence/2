import telebot
from telebot import types
from datetime import datetime
import requests
import pytz
import random
import json

# Токен бота
API_TOKEN = '7398445391:AAGUzesh_kKmJCT9FktfV4_cHgkJYLFK90o'
# Ключ OpenWeatherMap
OWM_API_KEY = 'f6cba4713126188762000e8459c15233'
# Ключ ExchangeRate-API
EXCHANGE_RATE_API_KEY = 'b0bcaa464e26f0a43ee6d76c'
bot = telebot.TeleBot(API_TOKEN)

# Создаем клавиатуру
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    weather_button = types.KeyboardButton('Погода')
    rate_button = types.KeyboardButton('Курс')
    picture_button = types.KeyboardButton('Картинка')
    game_button = types.KeyboardButton('Игра')
    keyboard.add(weather_button, rate_button, picture_button, game_button)
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = create_main_keyboard()
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=keyboard)

# Функция для получения погоды
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        return f"Погода в городе {city}:\n" \
               f"Описание: {weather_desc}\n" \
               f"Температура: {temp}°C\n" \
               f"Ощущается как: {feels_like}°C\n" \
               f"Влажность: {humidity}%"
    else:
        print(f"Error: {response.status_code}, Response: {response.text}")
        return "Не удалось получить данные о погоде. Пожалуйста, проверьте название города."


# Функция для получения курса валюты
def get_exchange_rate(currency):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rub_rate = data['conversion_rates']['RUB']
        return f"Курс {currency} к рублю: {rub_rate} RUB"
    else:
        print(f"Error: {response.status_code}, Response: {response.text}")
        return "Не удалось получить данные о курсе валюты. Пожалуйста, проверьте название валюты."


# Обработчик для кнопки "Погода"
@bot.message_handler(func=lambda message: message.text == 'Погода')
def ask_city(message):
    msg = bot.reply_to(message, "Пожалуйста, введите название города:")
    bot.register_next_step_handler(msg, send_weather)


# Отправка погоды пользователю
def send_weather(message):
    city = message.text
    weather_info = get_weather(city)
    bot.send_message(message.chat.id, weather_info)
    show_main_menu(message)


# Обработчик для кнопки "Курс"
@bot.message_handler(func=lambda message: message.text == 'Курс')
def ask_currency(message):
    msg = bot.reply_to(message, "Пожалуйста, введите название валюты (например, USD, EUR):")
    bot.register_next_step_handler(msg, send_exchange_rate)


# Отправка курса валюты пользователю
def send_exchange_rate(message):
    currency = message.text.upper()
    rate_info = get_exchange_rate(currency)
    bot.send_message(message.chat.id, rate_info)
    show_main_menu(message)

# Обработчик для кнопки "Картинка"
@bot.message_handler(func=lambda message: message.text == 'Картинка')
def send_monkey_image(message):
    response = requests.get("https://api.unsplash.com/photos/random?query=monkey&client_id=8H-itMFO3Aj6_kBSVir12FK4zGEAlPF2-twG-pD2w_g")
    if response.status_code == 200:
        data = json.loads(response.text)
        image_url = data['urls']['regular']
        bot.send_photo(message.chat.id, image_url)
    else:
        bot.send_message(message.chat.id, "Извините, не удалось получить изображение.")

# Обработчик для кнопки "Игра"
@bot.message_handler(func=lambda message: message.text == 'Игра')
def start_game(message):
    bot.send_message(message.chat.id, "Давай сыграем в игру 'Угадай число'! Я загадал число от 1 до 100. У тебя 7 попыток.")
    bot.send_message(message.chat.id, "Попробуй угадать число:")

    # Загадываем число
    secret_number = random.randint(1, 100)
    attempts = 0

    # Обработчик ввода пользователем числа
    @bot.message_handler(func=lambda message: True)
    def check_number(message):
        nonlocal attempts
        attempts += 1
        try:
            user_number = int(message.text)
            if user_number == secret_number:
                bot.send_message(message.chat.id, f"Поздравляю! Ты угадал число {secret_number}!")
                bot.remove_message_handler(check_number)
                send_main_menu(message)
            elif attempts >= 7:
                bot.send_message(message.chat.id, f"Ты проиграл! Загаданное число было: {secret_number}.")
                bot.remove_message_handler(check_number)
                send_main_menu(message)
            elif user_number < secret_number:
                bot.send_message(message.chat.id, "Загаданное число больше.")
            else:
                bot.send_message(message.chat.id, "Загаданное число меньше.")
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введи целое число.")

# Функция для показа главного меню
def show_main_menu(message):
    keyboard = create_main_keyboard()
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

# Запуск бота
bot.polling()
