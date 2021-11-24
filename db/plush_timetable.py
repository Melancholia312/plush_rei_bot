from db.connection import get_connect


def pin_timetable(url_id, peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"DELETE FROM timetables WHERE peer_id={peer_id}")
            cursor.execute(f"INSERT INTO timetables(url, peer_id) "
                           f"VALUES({url_id}, {peer_id})")
            connect.commit()

    finally:
        connect.close()


def get_url_id(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT url FROM timetables WHERE peer_id={peer_id}")
            url_id = cursor.fetchone()[0]
            return url_id

    finally:
        connect.close()






