import tools
import psycopg2
from queue import Queue


queue = Queue()
conn = psycopg2.connect(host='172.21.78.111', port='5432', dbname='postgres', user='postgres', password='postgres')

country_data = tools.get_country_info(queue)
tools.insert_data_to_db(conn, queue)
