import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import urllib.parse

result = urllib.parse.urlparse("postgres")
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port


def get_connect():
    connection = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return connection

