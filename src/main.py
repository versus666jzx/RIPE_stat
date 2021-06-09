import tools
import psycopg2
from requests import adapters
import datetime
import random
from time import time
from queue import Queue
import threading

# устанавливаем дефолтное количество попыток обратиться по апи
adapters.DEFAULT_RETRIES = 5

# Засекаем время
start_time = int(time())

# инициализируем очередь
queue = Queue()

# инициализируем коннект до БД
conn = psycopg2.connect(host='localhost', port='5432', dbname='postgres', user='postgres', password='postgres')

# устанавливаем временной диапазон для сбора данных
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# тут будут потоки
threads = []

# собираем инфу из Country Resource Stats
if tools.create_table(conn) == 0:
    queue = tools.get_country_queue(queue)

    for i in range(1, queue.qsize()):
        tr = threading.Thread(
            target=tools.get_country_resource_stats,
            args=(
                queue,
                '1d',
                yesterday,
                today
            ),
            name=f"thread_{i}"
        )
        threads.append(tr)
        tr.start()

    # ждем завершения сбора инфы по странам
    [thread.join() for thread in threads]

    # собираем инфу из Country Resource List
    for i in range(1, queue.qsize()):
        tr = threading.Thread(
            target=tools.get_country_resuorce_list,
            args=(
                queue,
            ),
            name=f"thread_{i}"
        )
        threads.append(tr)
        tr.start()

    # ждем завершения сбора инфы по странам
    [thread.join() for thread in threads]

    # собираем инфу из Country ASNs
    for i in range(1, queue.qsize()):
        tr = threading.Thread(
            target=tools.get_country_asns_data,
            args=(
                queue,
            ),
            name=f"thread_{i}"
        )
        threads.append(tr)
        tr.start()

    # ждем завершения сбора инфы по странам
    [thread.join() for thread in threads]

    # вставляем данные в бд
    tools.insert_data_to_db(conn, queue)

print(f"Время работы программы: {int(time()) - start_time} сек.")
