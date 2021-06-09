import calendar
import queue
import psycopg2
import classes
from countries import countries
from requests import get
from json import loads
from classes import Country
from time import sleep
from random import random


def create_default_config(config_path: str):
    default_conf = """
[RIPE_stat_config]

service_db_host = localhost
service_db_port = 5432

    """
    try:
        with open(config_path, "w") as config:
            config.write(default_conf)
    except Exception:
        raise


def get_country_resource_stats(
        queue: queue.Queue,
        resolution: str,
        start_time: str,
        end_time: str
):

    url = 'https://stat.ripe.net/data/country-resource-stats/data.json'
    sleep_time = round(random(), 1)
    country: classes.Country = queue.get()

    # задаем параметры для api
    # Возможные значения для resolution:
    # "5m" - 5 minutes
    # "1h" - 1 hour
    # "1d" - 1 day
    # "1w" - 1 week
    params = {"resource": country.country_code, 'starttime': start_time, 'endtime': end_time, 'resolution': resolution}

    try:
        sleep(sleep_time)
        country_stats_from_ripe = get(url, params, timeout=30)
    except Exception as err:
        country_stats_from_ripe = None
        print(f"Ашипка апи, блэт: {err}")

    if country_stats_from_ripe is not None:
        country_stats_from_ripe = loads(country_stats_from_ripe.text)['data']['stats']
        # print(dumps(country_stats_from_ripe, indent=4))
        for data_from_ripe in country_stats_from_ripe:
            country.years.append(data_from_ripe['stats_date'].split('T')[0].split('-')[0])
            country.months.append(data_from_ripe['stats_date'].split('T')[0].split('-')[1])
            country.months_human_read.append(
                calendar.month_name[int(data_from_ripe['stats_date'].split('T')[0].split('-')[1])]
            )
            country.days.append(data_from_ripe['stats_date'].split('T')[0].split('-')[2])
            country.ipv4_prefix_ris.append(data_from_ripe['v4_prefixes_ris'])
            country.ipv6_prefix_ris.append(data_from_ripe['v6_prefixes_ris'])
            country.ipv4_prefix_stats.append(data_from_ripe['v4_prefixes_stats'])
            country.ipv6_prefix_stats.append(data_from_ripe['v6_prefixes_stats'])
            country.asns_ris.append(data_from_ripe['asns_ris'])
            country.asns_stats.append(data_from_ripe['asns_stats'])
    else:
        queue.task_done()
    queue.task_done()
    queue.put(country)


def get_country_resuorce_list(
        queue: queue.Queue
):

    url = 'https://stat.ripe.net/data/country-resource-list/data.json'
    sleep_time = round(random(), 1)
    country: classes.Country = queue.get()
    # задаем параметры для api
    params = {"resource": country.country_code}

    # пытаемся получить данные по api
    try:
        sleep(sleep_time)
        country_resource_list_from_ripe = get(url, params, timeout=30)
    except Exception as err:
        country_resource_list_from_ripe = None
        print(f"Ашипка апи, блэт: {err}")

    if country_resource_list_from_ripe is not None:
        country_resource_list_from_ripe = loads(country_resource_list_from_ripe.text)["data"]
        # print(dumps(country_resource_list_from_ripe, indent=4))
        country.asns_routed = country_resource_list_from_ripe['resources']['asn']
        country.ipv4 = country_resource_list_from_ripe['resources']['ipv4']
        country.ipv6 = country_resource_list_from_ripe['resources']['ipv6']
    else:
        queue.task_done()
    queue.task_done()
    queue.put(country)


def get_country_asns_data(
        queue: queue.Queue
):
    url = 'https://stat.ripe.net/data/country-asns/data.json'
    sleep_time = round(random(), 1)
    country: classes.Country = queue.get()
    # задаем параметры для api
    params = {"resource": country.country_code, "lod": 1}

    # пытаемся получить данные по api
    try:
        sleep(sleep_time)
        country_asns_data_from_ripe = get(url, params, timeout=30)
    except Exception as err:
        country_asns_data_from_ripe = None
        print(f"Ашипка апи, блэт: {err}")
    if country_asns_data_from_ripe is not None:
        country_asns_data_from_ripe = loads(country_asns_data_from_ripe.text)
        country.asns_registered_count = country_asns_data_from_ripe["data"]["countries"][0]["stats"]["registered"]
        country.asns_routed_count = country_asns_data_from_ripe["data"]["countries"][0]["stats"]["routed"]
        if 'set()' not in country_asns_data_from_ripe["data"]["countries"][0]["routed"]:
            country.asns_routed = country_asns_data_from_ripe["data"]["countries"][0]["routed"]
        if 'set()' not in country_asns_data_from_ripe["data"]["countries"][0]["non_routed"]:
            country.asns_routed = country_asns_data_from_ripe["data"]["countries"][0]["non_routed"]
    else:
        queue.task_done()
    queue.task_done()
    queue.put(country)


def insert_data_to_db(
        conn: psycopg2.connect,
        queue: queue.Queue
):
    cursor = conn.cursor()

    queue_size = queue.qsize()
    while not queue.empty():
        country_data: classes.Country = queue.get()
        # обрабатываем строку типа {AsnSingle(32055)} в asns_routed
        # print("++++++++++++++ БЫЛО ++++++++++++++")
        # print(country_data.asns_routed)
        # print(type(country_data.asns_routed))
        if isinstance(country_data.asns_routed, str):
            try:
                asns_routed = country_data.asns_routed.split(',')
                country_data.asns_routed = [int(asns.split('(')[1].split(')')[0]) for asns in asns_routed]
            except Exception:
                country_data.asns_routed = [int(asns.split('(')[1].split(')')[0]) for asns in country_data.asns_routed]
        # print("++++++++++++++ СТАЛО ++++++++++++++")
        # print(country_data.asns_routed)
        sql = """
        INSERT INTO country_data (
            country_code, 
            country_name, 
            ipv4_prefix_stats, 
            ipv4_prefix_ris, 
            ipv6_prefix_stats, 
            ipv6_prefix_ris, 
            asns_routed, 
            asns_stats, 
            asns_ris, 
            asns_registered_count, 
            asns_routed_count, 
            asns_non_routed, 
            days, 
            months, 
            months_human_read, 
            years, 
            ipv4, 
            ipv6
        ) 
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        record_to_insert = (
            country_data.country_code,
            country_data.country_name,
            country_data.ipv4_prefix_stats,
            country_data.ipv4_prefix_ris,
            country_data.ipv6_prefix_stats,
            country_data.ipv6_prefix_ris,
            [int(asns) for asns in country_data.asns_routed],
            country_data.asns_stats,
            country_data.asns_ris,
            country_data.asns_registered_count,
            country_data.asns_routed_count,
            [int(non_routed_asn) for non_routed_asn in country_data.asns_non_routed],
            list(set([int(day) for day in country_data.days])),
            list(set([int(month) for month in country_data.months])),
            list(set(country_data.months_human_read)),
            list(set([int(year) for year in country_data.years])),
            country_data.ipv4,
            country_data.ipv6,
        )

        cursor.execute(sql, record_to_insert)
        conn.commit()
        queue.task_done()

        queue_size -= 1
        print(f"Осталось вставить {queue_size} записей")


def create_table(conn):
    cursor = conn.cursor()
    create_table_sql = """
    create table country_data(
    country_code          text,
    country_name          text,
    ipv4_prefix_stats     integer[],
    ipv4_prefix_ris       integer[],
    ipv6_prefix_stats     integer[],
    ipv6_prefix_ris       integer[],
    asns_routed           integer[],
    asns_stats            integer[],
    asns_ris              integer[],
    asns_registered_count integer,
    asns_routed_count     integer,
    asns_non_routed       integer[],
    days                  integer[],
    months                integer[],
    months_human_read     text[],
    years                 integer[],
    ipv4                  text[],
    ipv6                  text[],
    asns_neighbour_count  integer,
    asns_neighbours       integer[]
    );

    alter table country_data
        owner to postgres;
    """

    check_table_exist = "SELECT table_name FROM information_schema.tables where table_name = 'country_data';"
    try:
        cursor.execute(check_table_exist)
        res = cursor.fetchall()
    except Exception as err:
        print(f"Не удалось выполнить запрос к БД: {check_table_exist}")
    if len(res) == 0:
        try:
            cursor.execute(create_table_sql)
            return 0
        except Exception as err:
            print(f"Не удалось создать таблицу в БД: {err}")
            return 1
    else:
        return 0


def get_country_queue(
        queue: queue.Queue
) -> queue.Queue:
    """
    Формирует очередь объектов для заполнения данными

    :param queue: асинхронная очередь
    :return: асинхронная очередь с шаблонами объектов
    """

    for country_data_from_file in countries:
        # создаем объект класса
        country = Country(country_code=country_data_from_file["code"],
                          country_name=country_data_from_file["name"],
                          ipv4_prefix_stats=[],
                          ipv4_prefix_ris=[],
                          ipv6_prefix_stats=[],
                          ipv6_prefix_ris=[],
                          asns=[],
                          asns_stats=[],
                          asns_ris=[],
                          asns_registered=[],
                          asns_routed="",
                          asns_non_routed="",
                          days=[],
                          months=[],
                          months_human_read=[],
                          years=[],
                          ipv4=[],
                          ipv6=[]
                          )
        queue.put(country)
    return queue
