import telebot
import psycopg2
import db
import two_gis
import Wialon
from psycopg2 import pool
from telebot import types
import requests.exceptions
from email_validator import validate_email, EmailNotValidError

TOKEN = '6533641586:AAFkAJp9yGESjbrUWFImonttWRZHvZmHahw'

bot = telebot.TeleBot(TOKEN)

host = "localhost"
port = 5433
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=host,
    dbname = "tasyma",
    user = "postgres",
    password = "postgres",
    port = port

)
##################################################################################

###-----------------Create Order --------------
# message, data =>  telegram_id, service_id, analog_id, marka
#     data ne kerek 0^           1^          2^         3^
def get_order_text(data):
    sp = data.split("?")
    telegram_id, service_id, analog_id, marka, kub, price, A, B = sp
    order_info = "Проверьте ваш заказ:\n"
    order_info += f"Груз: {marka}\n"
    order_info += f"Куб: {kub}\n"
    if A == "Поставщик":
        order_info += f"Точка прибытия: {B}\n"
    elif B == "Поставщик":
        order_info += f"Точка прибытия: {A}\n"
    else:
        order_info += f"Точка отправки: {A}\n"
        order_info += f"Точка прибытия: {B}\n"
    order_info += f"Цена: {round(1.1 * 1000 * int(price), 2)}"
    print(order_info)
    return order_info


def create_order(message, data): #data: telegram_id, service_id, analog_id, marka
    print(data)
    sp = data.split("?")
    bot.send_message(message.chat.id, f"Ведите сколько куба ({sp[3]}) вам нужно:")
    bot.register_next_step_handler(message, process_kub, data)


def process_kub(message, data): #data: telegram_id, service_id, analog_id, marka, kub, price
    kub = message.text
    data += "?" + str(kub)
    print(data)
    sp = data.split("?")
    price = db.take_order_price(sp[1], sp[2], ("k"+str(kub)))
    if price:
        data += "?"+str(price)
        order_id = db.create_order(sp[0], sp[1], sp[2], sp[3], sp[4], str(price))
    else:
        user = db.get_user_info(sp[0])
        send_direct_message_to_manager(
            f"Поступил заказ от:\n"
            f"{user[0]} {user[1]}, {user[3]}"
            f"Груз :{sp[3]}, Куб :{sp[4]}")
        bot.send_message(message.chat.id,
                         "Пока такой заказ автоматический принять не можем.\n Закажите по телефону: +7 776 266 3985")
        return
    service_id, analog_id = sp[1], sp[2]
    points = db.get_AB(service_id, analog_id)
    A, B = points[0], points[1]
    print(A, B)
    if A == "Клиент":
        bot.send_message(message.chat.id, "Напишите точку отправки:")
        bot.register_next_step_handler(message, process_get_A, data, B, order_id)
    elif A == "Поставщик":
        data += "?" + A
        bot.send_message(message.chat.id, "Напишите точку назначения:")
        bot.register_next_step_handler(message, process_get_B, data, order_id)


def process_get_A(message, data, B, order_id): #data: telegram_id, service_id, analog_id, marka, kub, price, A
    A = (message.text)
    data += "?"+A
    db.update_order(order_id, "departure_point", A)
    if B == "Клиент":
        bot.send_message(message.chat.id, "Напишите точку назначения:")
        bot.register_next_step_handler(message, process_get_B, data, order_id)
def process_get_B(message, data, order_id): # data: telegram_id, service_id, analog_id, marka, kub, price, A, B
    B = (message.text)            #                  0            1           2           3     4   5      6  7
    data += "?" + B
    A = data.split("?")[6]
    print(data)
    db.update_order(order_id, "destination_point", B)
    if A == "Поставщик":
        providers = Wialon.avl_resources()# key:value   name, geoid, lon, lat
        provider_name = ""
        for provider in providers:
            provider_name = provider.get("name")
            #kak to tekseru kerek osy marka barma
        db.update_order(order_id, "departure_point", provider_name)
    bot_text = get_order_text(data)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Да, Подтверждаю", callback_data=f"Да?{order_id}")
    markup.add(btn1)
    btn2 = types.InlineKeyboardButton("Нет, Отклоняю", callback_data=f"Нет?{order_id}")
    markup.add(btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)

##############
#b_lat, b_lan =  two_gis.get_point(B)

# points = []
# units = Wialon.get_active_units()

# for unit in units:
    #     lat = unit.get('lat')
    #     lon = unit.get('lon')
        # points.append({lat, lon})

# mynda po idei products tablitsada postavshiktardyn adresstaryn alu
# for provider in providers:
# lat = provider.get('lat')
# lon = provider.get('lon')
# points.append({lat, lon})
# calculate dist  transports-providers
# two_gis.get_distances(points, list(range(len(units))), list(range(len(units), len(units) + len(providers) )))
# lat, lot = two_gis.get_point(A)
# points.append({'lat': lat, 'lon': lon})
# # calculate dist  transports-point A
# two_gis.get_distances(points, list(range(len(units))), list(range(len(units), len(units) + 1)))


###########        1. Registration / Login
def process_user_name(message):
    name = message.text
    bot.send_message(message.chat.id,
                     "Пожалуйста, введите свою фамилию.")
    bot.register_next_step_handler(message, process_user_surname,name)

def process_user_surname(message, name):
    surname = message.text
    bot.send_message(message.chat.id,
                     "Теперь введите свой адрес электронной почты.")
    bot.register_next_step_handler(message, process_user_email,name, surname)

def is_valid_email(email):
    try:
        # Пытаемся валидировать email
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        # Email не прошел валидацию
        return False
def process_user_email(message, name, surname):
    email = message.text
    if is_valid_email(email):
        bot.send_message(message.chat.id,
                          "Напишите свой телефонный номер.")
        bot.register_next_step_handler(message, process_user_contact, name, surname, email)
    else:
        bot.send_message(message.chat.id,
                         "Введенный вами email не существует. Пожалуйста, введите его снова:")
        bot.register_next_step_handler(message, process_user_email, name, surname)
def process_user_contact(message, name, surname, email):
    contact_number = message.text
    telegram_id = message.chat.id
    db.registrate_user(telegram_id, name, surname, email, contact_number)
    bot.send_message(message.chat.id,
                     "Спасибо за регистрацию! Нажмите еще раз /start")

############       4. feedback
def process_feedback(message):
    db.write_Feedback(message.chat.id, message.text)
    bot.send_message(message.chat.id,"Спасибо за Обратную связь")

###########    send message to manager :
manager = [1116588122]
def send_direct_message_to_manager(data):
    bot.send_message(manager[0], data)

def send_message_to_manager(order_id):
    res = db.get_order_info(order_id)

    user = db.get_user_info(res[1])
    kub = int(res[5])
    transport = "Хово"
    if kub <= 11:
        transport = "Камаз"
    if kub <= 6:
        transport = "Зил"
    bot.send_message(manager[0], f"Поступил Заказ (номер заказа {order_id}) от:\n"
                                 f"{user[0]} {user[1]}, {user[3]}\n"
                                 f"Груз: {res[4]} - Куб: {res[5]}\n"
                                 f"Откуда : {res[6]}\n"
                                 f"Куда   : {res[7]}\n"
                                 f"Транспорт: {transport}\n"
                                 f"Цена: {round(1.1 * 1000 * int(res[10]), 2)}")


#############--------------- Start -----------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    name = db.check_user(message.chat.id)
    num = 1
    if name is None:
        btn1 = types.InlineKeyboardButton(f"{num}. Регистрация", callback_data="1.")
        markup.add(btn1)
        num += 1
    else:
        btn3 = types.InlineKeyboardButton(f"{num}. Поиск грузоперевозок:", callback_data="2.")
        markup.add(btn3)
        num += 1
        btn4 = types.InlineKeyboardButton(f"{num}. Управление заказами:", callback_data="3.")
        markup.add(btn4)
        num += 1
        btn5 = types.InlineKeyboardButton(f"{num}. Обратная связь:", callback_data="4.")
        markup.add(btn5)
    if name:
        bot.send_message(message.chat.id, f"Добрый день! Готовы заказать грузоперевозки? Если у вас есть крупные заказы, звоните на номер +77762663985.", reply_markup=markup)# list of services
    else:
        bot.send_message(message.chat.id, f"Добрый день! Готовы заказать грузоперевозки? Если у вас есть крупные заказы, звоните на номер +77762663985.", reply_markup=markup)# list of services

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = "Привет! Я бот справки. Вот список доступных команд:\n\n" \
                "/start - Для начала с ботом нажмите\n"\
                "/help - Получить справочную информацию и список доступных команд.\n" \
                "/feedback - Оставить обратную связь и задать вопросы администратору"
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['feedback'])
def send_feedback(message):
    feedback_text = "Спасибо за обратную связь! Если у вас есть вопросы или предложения, пожалуйста, напишите их здесь."
    bot.register_next_step_handler(message.chat.id, process_feedback)



###########-----------------callback ---------------------
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    print(callback.data)
    if callback.data.startswith("1."):
        name = db.check_user(callback.message.chat.id)
        if name:
            bot.send_message(callback.message.chat.id,
                             f"Вы уже зарегистрированы {name}")
        else:
            bot.send_message(callback.message.chat.id,
                             "Для регистрации, пожалуйста, введите своё имя.")
        bot.register_next_step_handler(callback.message, process_user_name)

    elif callback.data.startswith("2."):
        Wialon.login()
        services = db.get_service_analog()
        markup = types.InlineKeyboardMarkup()
        for service in services: # service_id, analog_id, service_name, cargo
            callback_data= f"service?{service[0]}?{service[1]}?{service[3]}"
            btn = types.InlineKeyboardButton(service[2], callback_data=callback_data)
            markup.add(btn)
        bot.send_message(callback.message.chat.id, "Выберите пожалуйста :", reply_markup=markup)
    elif callback.data.startswith("3."):
        telegram_id = callback.message.chat.id
        orders = db.get_my_orders(telegram_id)
        if len(orders) == 0:
            bot.send_message(callback.message.chat.id, "У вас пока что нету закаазов")
        else:
            bot.send_message(callback.message.chat.id, "Ваши Заказы :")
            for number, order in enumerate(orders, start=1):
                if order[5] == "Pending":
                    markup = types.InlineKeyboardMarkup()
                    btn = types.InlineKeyboardButton("Удалить", callback_data="Нет?"+str(order[6]))
                    markup.add(btn)
                    bot.send_message(callback.message.chat.id,
                                 f"№{number}\n "
                                 f"Груз: {order[0]}\n"
                                 f"Куб: {order[1]}\n"
                                 f"Откуда: {order[2]}\n"
                                 f"Куда: {order[3]}\n"
                                 f"Транспорт: {order[4]}\n "
                                 f"Статус заказа: {order[5]}", reply_markup=markup)
                else :
                    bot.send_message(callback.message.chat.id,
                                     f"№{number}\n "
                                     f"Груз: {order[0]}\n"
                                     f"Куб: {order[1]}\n"
                                     f"Откуда: {order[2]}\n"
                                     f"Куда: {order[3]}\n"
                                     f"Транспорт: {order[4]}\n "
                                     f"Статус заказа: {order[5]}")



    elif callback.data.startswith("4."):
        bot.send_message(callback.message.chat.id,
        "Привет! Мы очень ценим ваше мнение и готовы ответить на любые вопросы. Пожалуйста, оставьте свой отзыв или задайте вопрос, и мы свяжемся с вами как можно скорее.")
        bot.register_next_step_handler(callback.message, process_feedback)

    elif callback.data.startswith('service'): # service_id analog_id cargo
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        sp = callback.data.split("?")
        service_id, analog_id, cargo = sp[1:]
    #     marks = db.get_cargo_marks(cargo)
    #     if len(marks) > 1:
    #         markup=types.InlineKeyboardMarkup(0)
    #         for mark in marks:
    #             callback_data = f"marka?{service_id}?{analog_id}?{mark[1]}"
    #             btn=types.InlineKeyboardButton(f"{mark[1]}", callback_data=callback_data)
    #             markup.add(btn)
    #         bot.send_message(callback.message.chat.id, "выберите марку, пожалуйста", reply_markup=markup)
    #     elif len(marks) == 1:
    #         print(marks)
    #         markup = types.InlineKeyboardMarkup(0)
    #         callback_data = f"marka?{service_id}?{analog_id}?{marks[0][1]}"
    #         btn = types.InlineKeyboardButton(f"{marks[0][1]}", callback_data=callback_data)
    #         markup.add(btn)
    #         bot.send_message(callback.message.chat.id, "выберите марку, пожалуйста", reply_markup=markup)
    #     else :
    #         marka = cargo
    #         telegram_id = callback.message.chat.id
    #         data = f"{telegram_id}?{service_id}?{analog_id}?{marka}"
    #         create_order(callback.message, data)
    # elif callback.data.startswith('marka'):
    #     bot.delete_message(callback.message.chat.id, callback.message.message_id)
    #     sp = callback.data.split("?")
    #     service_id, analog_id, marka = sp[1:]
        telegram_id = callback.message.chat.id
        marka = cargo
        data = f"{telegram_id}?{service_id}?{analog_id}?{marka}"
        create_order(callback.message, data)

    elif callback.data.startswith("Да"):  # callback.data: order_id
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        sp = callback.data.split("?")
        order_id = sp[1]
        send_message_to_manager(order_id)
        bot.send_message(callback.message.chat.id, "Спасибо, ваша заявка принята. "
                                                   "Наша команда уже ищет для вас грузоперевозчика, пожалуйста "
                                                   "ожидайте, мы свяжемся с вами по указанному номеру: +7 776 266 3985")

    #########################
    #poisk transporta
    #   calculate_time
    #########################
    elif callback.data.startswith("Нет"):
        sp = callback.data.split("?")
        db.delete_order(sp[1])
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id,
                         f"/start")



@bot.message_handler(content_types = ['location'])
def get_location(message):
    print(message)
    bot.send_message(message.chat.id, f"address dostavki longitude: {message.location.longitude}, latitude: {message.location.latitude} ")

try:
    # Start infinite polling
    bot.infinity_polling()
except requests.exceptions.ReadTimeout:
    # Handle read timeout error
    print("Read timeout occurred. Retrying...")
    # You can implement your retry logic here or simply exit the program
    # For example, you can call bot.infinity_polling() again to restart polling
except Exception as e:
    # Handle other exceptions
    print("An error occurred:", e)

