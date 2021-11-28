from db.connection import get_connect


def plush_init(users_list, peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            for user in users_list:
                if user['member_id'] > 0:
                    res = cursor.execute(f"SELECT user_id FROM users "
                                         f"WHERE peer_id={peer_id} and user_id={user['member_id']}")
                    if not res:
                        cursor.execute(f"INSERT INTO users(peer_id, user_id, first_name, last_name) "
                                       f"VALUES({peer_id}, {user['member_id']}, '{user['first_name']}', '{user['last_name']}')")
            connect.commit()
    finally:
        connect.close()



