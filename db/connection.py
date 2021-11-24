import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import urllib.parse

result = urllib.parse.urlparse("postgres://qpobxihgxvpgun:0466a9f70793348cb8bbba02592318898c1d3917792e4da5363ed8115ad7d0d6@ec2-3-248-87-6.eu-west-1.compute.amazonaws.com:5432/d3ogdamab7jk17")
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

