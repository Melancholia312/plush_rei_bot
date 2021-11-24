from db.connection import get_connect


def pin_homework(peer_id, name, text_homework, attach_homework):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"DELETE FROM homework WHERE peer_id={peer_id} and name='{name}'")
            cursor.execute(f"INSERT INTO homework(peer_id, name, text_homework, attach_homework) "
                           f"VALUES({peer_id}, '{name}', '{text_homework}', '{attach_homework}')")
            connect.commit()
    finally:
        connect.close()


def get_homework(peer_id, name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM homework WHERE peer_id={peer_id} and name='{name}'")
            homework = cursor.fetchone()
            return homework
    finally:
        connect.close()


def get_subjects(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT name FROM homework WHERE peer_id={peer_id}")
            subjects = cursor.fetchall()
            return subjects
    finally:
        connect.close()


def unpin_homework(peer_id, name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"DELETE FROM homework WHERE peer_id={peer_id} and name='{name}'")
            connect.commit()
    finally:
        connect.close()