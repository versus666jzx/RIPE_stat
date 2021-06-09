import classes
import tools
import psycopg2
from requests import adapters
from configparser import ConfigParser
import os
import datetime
import random
from time import time
from queue import Queue
import threading
adapters.DEFAULT_RETRIES = 5


# Засекаем время
start_time = int(time())

queue = Queue()

conn = psycopg2.connect(host='localhost', port='5432', dbname='postgres', user='postgres', password='postgres')

sleep_time = round(random.random(), 1)
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
threads = []
if tools.create_table(conn) == 0:
    queue = tools.get_country_queue(queue)

    for i in range(1, queue.qsize()):
        tr = threading.Thread(
            target=tools.get_country_resource_stats,
            args=(
                queue,
                '1d',
                yesterday,
                today,
                sleep_time
            ),
            name=f"thread_{i}"
        )
        threads.append(tr)
        tr.start()
    [thread.join() for thread in threads]

    for i in range(1, queue.qsize()):
        tr = threading.Thread(
            target=tools.get_country_resuorce_list,
            args=(
                queue,
                sleep_time
            ),
            name=f"thread_{i}"
        )
        threads.append(tr)
        tr.start()
    [thread.join() for thread in threads]

    for i in range(1, queue.qsize()):
        tr = threading.Thread(
            target=tools.get_country_asns_data,
            args=(
                queue,
                sleep_time
            ),
            name=f"thread_{i}"
        )
        threads.append(tr)
        tr.start()
    [thread.join() for thread in threads]

    tools.insert_data_to_db(conn, queue)

print(f"Время работы программы: {int(time()) - start_time} сек.")
