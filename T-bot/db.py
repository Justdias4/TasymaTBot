import psycopg2
from psycopg2 import pool
host = "localhost"
port = 5433
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=host,
    dbname="tasyma",
    user="postgres",
    password="postgres",
    port=port

)
def get_user_info(telegram_id):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT name, surname, email, contact_number FROM users
                                    WHERE telegram_id = %s""", (telegram_id,))
            res = cur.fetchone()
            return res
        except psycopg2.Error as e:
            print("db err:", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None


def get_order_info(order_id):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT * FROM orders
                                WHERE id = %s""", (order_id, ))
            res = cur.fetchone()
            return res
        except psycopg2.Error as e:
            print("db err:", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None

def get_my_orders(telegram_id):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT marka, kub, departure_point, destination_point, transport, status, id FROM orders  WHERE telegram_id = %s""", (telegram_id,))
            result = cur.fetchall()
            return result
        except psycopg2.Error as e:
            print("db err:", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None

def delete_order(id):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""DELETE FROM orders 
                        WHERE id = %s""", (id, ))
            conn.commit()
            cur.close()
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            connection_pool.putconn(conn)
def update_order(id, column, value):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            query = """UPDATE orders 
                                   SET {} = %s
                                   WHERE id = %s""".format(column)
            cur.execute(query, (value, id))
            conn.commit()
            cur.close()
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            connection_pool.putconn(conn)

def take_order_price(service_id, analog_id, k):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            query = """SELECT {} FROM services
                            WHERE service_id = %s AND analog_id = %s""".format(k)
            cur.execute(query, (service_id, analog_id))
            result = cur.fetchone()[0]
            cur.close()
            return result
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            connection_pool.putconn(conn)
def create_order(telegram_id, service_id, analog_id, marka, kub, price):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""INSERT INTO orders (telegram_id, service_id, analog_id, marka, kub, price) 
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""", (telegram_id, service_id, analog_id, marka, kub, price))
            order_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return order_id
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            connection_pool.putconn(conn)

def get_AB(service_id, analog_id):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT departure_point, destination_point FROM services
                WHERE service_id = %s and analog_id = %s""",
                (service_id, analog_id))
            results = cur.fetchone()
            return results
        except psycopg2.Error as e:
            print("db err:", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None

def get_address(marka):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT addresss FROM products  WHERE marka = %s""", (marka,))
            result = cur.fetchone()
            return result
        except psycopg2.Error as e:
            print("db err:", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None
def get_cargo_marks(cargo):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT cargo, marka FROM products  WHERE cargo = %s""", (cargo, ))
            results = cur.fetchall()
            return results
        except psycopg2.Error as e:
            print("db err:", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None

def get_service_analog(id = 10):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""SELECT service_id, analog_id, service_name, cargo FROM services  WHERE service_id = %s AND analog_id != 1 ORDER BY analog_id""", (id, ))
            results = cur.fetchall()
            return results
        except psycopg2.Error as e:
            print("db err:", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None


def get_service_list(): # esli est' mnogo servisov poka 4to ony koldanbaimyz
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""WITH ranked_objects AS (
                            SELECT *,
                                   ROW_NUMBER() OVER (PARTITION BY service_id ORDER BY analog_id) AS object_rank,
                                   COUNT(*) OVER (PARTITION BY service_id) AS object_count
                            FROM "Услуги"
                        )
                        SELECT service_id, service_name
                        FROM ranked_objects
                        WHERE object_rank = 1
                        ORDER BY object_count DESC;
                        """)
            services = cur.fetchall()
            return services
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        print("Failed to obtain database connection")
def check_user(telegram_id):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT name FROM users WHERE telegram_id = {telegram_id}")
            result = cur.fetchone()
            if result is not None:
                return result[0]
            else:
                return None
        except psycopg2.Error as e:
            print("db err: ", e)
            return None
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        return None

def registrate_user(telegram_id, name, surname, email, contact_number):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (telegram_id, name, surname, email, contact_number) VALUES (%s, %s, %s, %s, %s)",
                        (telegram_id, name, surname, email, contact_number))
            conn.commit()
            cur.close()
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            connection_pool.putconn(conn)
def write_Feedback(telegram_id, feedback):
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO feedbacks (telegram_id, message) VALUES (%s, %s)",
                    (telegram_id, feedback))
            conn.commit()
            cur.close()
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            connection_pool.putconn(conn)



def get_services():
    conn = connection_pool.getconn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""WITH ranked_objects AS (
                            SELECT *,
                                   ROW_NUMBER() OVER (PARTITION BY id ORDER BY "Аналог") AS object_rank,
                                   COUNT(*) OVER (PARTITION BY id) AS object_count
                            FROM "Услуги"
                        )
                        SELECT id, "Услуга"
                        FROM ranked_objects
                        WHERE object_rank = 1
                        ORDER BY object_count DESC;
                        """)
            services = cur.fetchall()
            return services
        except psycopg2.Error as e:
            print("db err:", e)
        finally:
            cur.close()
            connection_pool.putconn(conn)
    else:
        print("Failed to obtain database connection")

#
# cur = conn.cursor()
# #do
# cur.execute("""CREATE TABLE IF NOT EXISTS Order (
#     id SERIAL PRIMARY KEY,
#     услуга_id int,
#     услуга_Аналог int,
#     Услуга VARCHAR(256),
#     Груз VARCHAR(256),
#     Откуда VARCHAR(256),
#     Куда VARCHAR(256),
#     Тариф VARCHAR(256),
#     куб VARCHAR(256),
#     тонна VARCHAR(256),
#     километр VARCHAR(256),
#     плотность VARCHAR(256),
#     час VARCHAR(256),
#     рейс VARCHAR(256)
#
#     )
# """)
#
# conn.commit()
#
#
# # cur.execute("""
# #     INSERT INTO products (product, marka, kub, tonnes, density, company, longitude, latitude)
# #     VALUES
# #         ('Щебень', 'Щебень 10-20', 3500.00, 2500.00, 1400.0, 'Карьер-Аксай', 43.18513, 76.789393),
# #         ('Щебень', 'Щебень 20-40', 3000.00, 2084.00, 1.440, 'Карьер-Аксай', 43.18514, 76.789394),
# #         ('Камень', 'Камень бутовый (Окол) 70-120', 3000.00, 1875.00, 1.600, 'Карьер-Аксай', 43.18515, 76.789395),
# #         ('Отсев', 'Песок дробленный(отсев)', 2500.00, 1724.00, 1.450, 'Карьер-Аксай', 43.18516, 76.789396),
# #         ('Песок', 'Песок мытый', 3000.00, 1875.00, 1.600, 'Карьер-Аксай', 43.18517, 76.789397),
# #         ('Баласт', 'ГПС природная (баласт)', 1100.00, 611.00, 1.800, 'Карьер-Аксай', 43.18518, 76.789398),
# #         ('ГПС', 'ГПС обогащенная', 1800.00, 1164.00, 1.560, 'Карьер-Аксай', 43.18519, 76.789399),
# #         ('ГЩС', 'ГЩС', 2000.00, 1212.00, 1.650, 'Карьер-Аксай', 43.18520, 76.789400),
# #         ('Окатыш', 'Окатыш', 1500.00, 1014.00, 1.480, 'Карьер-Аксай', 43.18521, 76.789401)
# # """)
# # cur.execute("SELECT product, marka, tonnes FROM products")
# # res = cur.fetchall()
# # # print(res)
# # for prod in res:
# #     product, marka, tonnes= prod
# data = [
#
#     (1, 1, 1, 'Вывоз мусора', 'мусор', 'Клиент', 'Свалка', 'рейс', None, None, None, None, None, None),
#     (2, 1, 2, 'Вывоз строительного мусора', 'мусор строительный', 'Клиент', 'Свалка', 'рейс', None, None, None, None, None, None),
#     (3, 1, 3, 'Вывоз бытового отхода', 'отход', 'Клиент', 'Свалка', 'рейс', None, None, None, None, None, None),
#     (4, 1, 4, 'Вывоз хлама', 'хлам', 'Клиент', 'Свалка', 'рейс', None, None, None, None, None, None),
#     (5, 1, 5, 'Вывоз бытового мусора', 'мусор бытовой', None, None, None, None, None, None, None, None, None),
#     (6, 1, 6, 'Вывоз ТБО', 'ТБО', None, None, None, None, None, None, None, None, None),
#     (7, 1, 7, 'Вывоз старой мебели', 'мебель старая', None, None, None, None, None, None, None, None, None),
#     (8, 1, 8, 'Утилизация мебели', 'мебель старая', None, None, None, None, None, None, None, None, None),
#     (9, 1, 9, 'Вывоз бытовой техники', 'техника бытовая', None, None, None, None, None, None, None, None, None),
#     (10, 7, 1, 'Услуга перегона техники', 'техника', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (11, 3, 1, 'Услуга манипулятора', 'любой', 'Клиент', 'Клиент', 'час', None, None, None, None, None, None),
#     (12, 4, 1, 'Услуги ассинизатора', 'канализационные отходы', 'Клиент', 'Приемка', 'куб', None, None, None, None, None, None),
#     (13, 4, 2, 'Откачка септиков', 'канализационные отходы', 'Клиент', 'Приемка', 'куб', None, None, None, None, None, None),
#     (14, 4, 3, 'Откачка туалет', 'канализационные отходы', 'Клиент', 'Приемка', 'куб', None, None, None, None, None, None),
#     (15, 4, 4, 'Услуги гавновоза', 'канализационные отходы', 'Клиент', 'Приемка', 'куб', None, None, None, None, None, None),
#     (16, 5, 1, 'Вывоз снега', 'снег', 'Клиент', 'Свалка', 'рейс', None, None, None, None, None, None),
#     (17, 6, 1, 'Услуги выемки грунта', 'грунт', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (18, 6, 2, 'Вывоз грунта', 'грунт', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (19, 6, 3, 'Выемка котлована', 'котлован', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (20, 6, 4, 'Выемка траншеи', 'траншея', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (21, 6, 5, 'Уплотнение грунта', 'грунт', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (22, 7, 1, 'Услуги эвакуатора', 'техника', 'Клиент', 'Клиент', 'километр', None, None, None, None, None, None),
#     (23, 7, 2, 'Услуги автоперевозок', 'автомобиль', None, None, None, None, None, None, None, None, None),
#     (24, 7, 3, 'Автовозы', 'автомобиль', None, None, None, None, None, None, None, None, None),
#     (25, 7, 4, 'Услуги низкорамного тралла', 'автомобиль', None, None, None, None, None, None, None, None, None),
#     (26, 7, 5, 'Услуги трал', 'автомобиль', None, None, None, None, None, None, None, None, None),
#     (27, 7, 6, 'Автоперегон', 'автомобиль', None, None, None, None, None, None, None, None, None),
#     (28, 7, 7, 'Услуги длинномер', 'груз крупногабаритный', None, None, None, None, None, None, None, None, None),
#     (29, 7, 8, 'Услуги шаланда', 'груз крупногабаритный', None, None, None, None, None, None, None, None, None),
#     (30, 8, 1, 'Услуги манипулятора', 'любой', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (31, 8, 2, 'Перевозка контейнеров', 'контейнер', None, None, None, None, None, None, None, None, None),
#     (32, 8, 3, 'Перевозка колец', 'колца', None, None, None, None, None, None, None, None, None),
#     (33, 8, 4, 'Перевозка станков', 'станок', None, None, None, None, None, None, None, None, None),
#     (34, 8, 5, 'Контейнеровоз', 'контейнер', None, None, None, None, None, None, None, None, None),
#     (35, 9, 1, 'Услуги переезда', 'любой', 'Клиент', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (36, 9, 2, 'Услуги переезда офиса', 'офис', None, None, None, None, None, None, None, None, None),
#     (37, 9, 3,  'Услуги переезда квартир', 'квартира', None, None, None, None, None, None, None, None, None),
#     (38, 9, 4, 'Услуги переезда дома', 'дом', None, None, None, None, None, None, None, None, None),
#     (39, 9, 5, 'Перевозка мебели', 'мебель', None, None, None, None, None, None, None, None, None),
#     (40, 9, 6, 'Перевозка пианин', 'пианино', None, None, None, None, None, None, None, None, None),
#     (41, 9, 7, 'Перевозка рояль', 'рояль', None, None, None, None, None, None, None, None, None),
#     (42, 9, 8, 'Перевозка бильярд', 'бильярд', None, None, None, None, None, None, None, None, None),
#     (43, 9, 9, 'Мебелевоз с гидробортом', 'мебель', None, None, None, None, None, None, None, None, None),
#     (44, 9, 10, 'Перевозка сейфа', 'сейф', None, None, None, None, None, None, None, None, None),
#     (45, 10, 1, 'Доставка сыпучих материалов', 'сыпучие материалы', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (46, 10, 2, 'Доставка инертных матриалов', 'инертные материалы', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (47, 10, 3, 'Доставка песка', 'песок', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (48, 10, 4, 'Доставка мытого песка', 'песок мытый', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (49, 10, 5, 'Доставка барханного песка', 'песок барханный', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (50, 10, 6, 'Доставка мелького песка', 'песок мелький', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (51, 10, 7, 'Доставка угля', 'уголь', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (52, 10, 8, 'Доставка калиброванного угля', 'уголь калиброванный', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (53, 10, 9, 'Доставка угля каражыра', 'уголь каражыра', None, None, None, None, None, None, None, None, None),
#     (54, 10, 10, 'Доставка угля шубаркуль', 'уголь шубаркуль', None, None, None, None, None, None, None, None, None),
#     (55, 10, 11, 'Доставка щебня', 'щебень', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (56, 10, 12,  'Доставка глины', 'глина', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (57, 10, 13, 'Доставка отсева', 'отсев', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (58, 10, 14, 'Доставка мытого отсева', 'отсев мытый', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (59, 10, 15, 'Доставка балласта', 'балласт', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (60, 10, 16, 'Доставка сникерса', 'сникерс', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (61, 10, 17, 'Доставка гравий', 'гравий', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (62, 10, 18, 'Доставка чернозем', 'чернозем', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (63, 10, 19, 'Доставка ПГС', 'ПГС', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (64, 10, 20, 'Доставка ГЩС', 'ГЩС', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (65, 10, 21, 'Доставка камня', 'камень', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (66, 10, 22, 'Доставка камня для бетон', 'камень для бетон', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (67, 10, 23, 'Доставка бутового камня', 'камень бутовый', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (68, 10, 24, 'Доставка дровь', 'дрова', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (69, 10, 25, 'Доставка навоз', 'навоз', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (70, 10, 26, 'Доставка опилки', 'опилка', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (71, 10, 27, 'Доставка шлака', 'шлак', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (72, 10, 28, 'Доставка керамзит', 'керамзит', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (73, 10, 29, 'Доставка асфальта', 'асфальт', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (74, 10, 30, 'Доставка дресва', 'дресва', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (75, 10, 31, 'Доставка ИТД', 'ИТД', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (76, 10, 32, 'Доставка перегной', 'перегной', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (77, 10, 33, 'Доставка скальника', 'скальник', 'Поставщик', 'Клиент', 'рейс', None, None, None, None, None, None),
#     (78, 10, 34, 'Доставка окол', 'окол', None, None, None, None, None, None, None, None, None),
#     (79, 10, 35, 'Доставка сен', 'сено', None, None, None, None, None, None, None, None, None),
#     (80, 10, 36, 'Доставка булыжник', 'булыжник', None, None, None, None, None, None, None, None, None),
#     (81, 11, 1, 'Перевозка стекол', 'стекло', None, None, 'рейс', None, None, None, None, None, None),
#     (82, 11, 2, 'Перевозка окон', 'окно', None, None, None, None, None, None, None, None, None),
#     (83, 11, 3, 'Перевозка ДСП', 'ДСП', None, None, None, None, None, None, None, None, None),
#     (84, 11, 4, 'Доставка пирамид', 'пирамида', None, None, None, None, None, None, None, None, None),
#     (85, 11, 5, 'Перевозка стеклотар', 'стеклотара', None, None, None, None, None, None, None, None, None),
#     (86, 12, 1, 'Услуги рефрижиратора', 'рефрижиратор', None, None, None, None, None, None, None, None, None),
#     (87, 12, 2, 'Доставка с температурным режимом', 'температурный режим', None, None, None, None, None, None, None, None, None),
#     (88, 12, 3, 'Грузоперевозка термобудка', 'термобудка', None, None, None, None, None, None, None, None, None),
#     (89, 13, 1, 'Услуги водовоза', 'вода', None, None, None, None, None, None, None, None, None),
#     (90, 13, 2, 'Доставка воды', 'вода', None, None, None, None, None, None, None, None, None),
#     (91, 14, 1, 'Услуги бетоновоз', None, None, None, None, None, None, None, None, None, None),
#     (92, 15, 1, 'Услуги Услуги цементовоза', None, None, None, None, None, None, None, None, None, None)
# ]
# #     print(product, " ", marka, " ", tonnes)
# for i, row in enumerate(data):
#     while len(row) < 14:
#         row += (None,)
#         print(i, " ", row)
#     data[i] = row
#
#
#
# # for row in data:
# #     cur.execute("""INSERT INTO Услуги (серийник, id, Аналог, Услуга, Груз, Откуда, Куда, Тариф, куб, тонна, километр, плотность, час, рейс)
# #                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", row)
#
# conn.commit()
# cur.close()
# conn.close()

















 #  kazirgi table
 # INSERT INTO services
# (service_id, analog_id, service_name, cargo, departure_point, destination_point, tariff)
# VALUES
# (10, 1, 'Доставка сыпучих/инертных материалов', 'сыпучие материалы', 'Поставщик', 'Клиент', 'рейс'),
# -- (10, 2, 'Доставка инертных матриалов', 'инертные материалы', 'Поставщик', 'Клиент', 'рейс'),
# (10, 3, 'Доставка песка', 'песок', 'Поставщик', 'Клиент', 'рейс'),
# (10, 4, 'Доставка мытого песка', 'песок мытый', 'Поставщик', 'Клиент', 'рейс'),
# (10, 5, 'Доставка барханного песка', 'песок барханный', 'Поставщик', 'Клиент', 'рейс'),
# (10, 6, 'Доставка мелького песка', 'песок мелький', 'Поставщик', 'Клиент', 'рейс'),
# (10, 7, 'Доставка угля', 'уголь', 'Поставщик', 'Клиент', 'рейс'),
# (10, 8, 'Доставка калиброванного угля', 'уголь калиброванный', 'Поставщик', 'Клиент', 'рейс'),
# (10, 9, 'Доставка угля каражыра', 'уголь каражыра', 'Поставщик', 'Клиент', 'рейс'),
# (10, 10, 'Доставка угля шубаркуль', 'уголь шубаркуль', 'Поставщик', 'Клиент', 'рейс'),
# (10, 11, 'Доставка щебня', 'щебень', 'Поставщик', 'Клиент', 'рейс'),
# (10, 12, 'Доставка глины', 'глина', 'Поставщик', 'Клиент', 'рейс'),
# (10, 13, 'Доставка отсева', 'отсев', 'Поставщик', 'Клиент', 'рейс'),
# (10, 14, 'Доставка мытого отсева', 'отсев мытый', 'Поставщик', 'Клиент', 'рейс'),
# (10, 15, 'Доставка балласта', 'балласт', 'Поставщик', 'Клиент', 'рейс'),
# (10, 16, 'Доставка сникерса', 'сникерс', 'Поставщик', 'Клиент', 'рейс'),
# (10, 17, 'Доставка гравий', 'гравий', 'Поставщик', 'Клиент', 'рейс'),
# (10, 18, 'Доставка чернозем', 'чернозем', 'Поставщик', 'Клиент', 'рейс'),
# (10, 19, 'Доставка ПГС', 'ПГС', 'Поставщик', 'Клиент', 'рейс'),
# (10, 20, 'Доставка ГЩС', 'ГЩС', 'Поставщик', 'Клиент', 'рейс'),
# (10, 21, 'Доставка камня', 'камень', 'Поставщик', 'Клиент', 'рейс'),
# (10, 22, 'Доставка камня для бетон', 'камень для бетон', 'Поставщик', 'Клиент', 'рейс'),
# (10, 23, 'Доставка бутового камня', 'камень бутовый', 'Поставщик', 'Клиент', 'рейс'),
# (10, 24, 'Доставка дровь', 'дрова', 'Поставщик', 'Клиент', 'рейс'),
# (10, 25, 'Доставка навоз', 'навоз', 'Поставщик', 'Клиент', 'рейс'),
# (10, 26, 'Доставка опилки', 'опилка', 'Поставщик', 'Клиент', 'рейс'),
# (10, 27, 'Доставка шлака', 'шлак', 'Поставщик', 'Клиент', 'рейс'),
# (10, 28, 'Доставка керамзит', 'керамзит', 'Поставщик', 'Клиент', 'рейс'),
# (10, 29, 'Доставка асфальта', 'асфальт', 'Поставщик', 'Клиент', 'рейс'),
# (10, 30, 'Доставка дресва', 'дресва', 'Поставщик', 'Клиент', 'рейс'),
# (10, 31, 'Доставка ИТД', 'ИТД', 'Поставщик', 'Клиент', 'рейс'),
# (10, 32, 'Доставка перегной', 'перегной', 'Поставщик', 'Клиент', 'рейс'),
# (10, 33, 'Доставка скальника', 'скальник', 'Поставщик', 'Клиент', 'рейс'),
# (10, 34, 'Доставка окол', 'окол', 'Поставщик', 'Клиент', 'рейс'),
# (10, 35, 'Доставка сен', 'сено', 'Поставщик', 'Клиент', 'рейс'),
# (10, 36, 'Доставка булыжник', 'булыжник', 'Поставщик', 'Клиент', 'рейс')