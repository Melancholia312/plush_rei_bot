import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_connect():
    connection = psycopg2.connect(user='postgres',
                                  password='TombRaider2003',
                                  host='127.0.0.1',
                                  port='5432',
                                  database="PlushReiDB")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return connection
