from db.connection import get_connect


def skip_lessons(peer_id, user_id, count, of):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if of:
                mark = '_of'
            else:
                mark = '_n_of'
            cursor.execute(f"SELECT skip_lessons{mark} FROM users "
                           f"WHERE peer_id={peer_id} AND user_id={user_id}")
            already_skipped = cursor.fetchone()[0]
            new_skipped = already_skipped + count
            cursor.execute(f"UPDATE users SET skip_lessons{mark}={new_skipped} "
                           f"WHERE peer_id={peer_id} AND user_id={user_id} ")
            connect.commit()

    finally:
        connect.close()


def show_skipped_lessons(msg_info):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT skip_lessons_of, skip_lessons_n_of  FROM users "
                           f"WHERE peer_id={msg_info['peer_id']} AND user_id={msg_info['from_id']}")
            already_skipped = cursor.fetchall()[0]
            return already_skipped

    finally:
        connect.close()


def show_all_skipped_lessons(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT skip_lessons_of, skip_lessons_n_of, user_id, first_name, last_name FROM users "
                           f"WHERE peer_id={peer_id} ORDER BY -skip_lessons_n_of")
            already_skipped = cursor.fetchall()
            return already_skipped

    finally:
        connect.close()