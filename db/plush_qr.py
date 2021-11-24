from db.connection import get_connect


def pin_qr(msg_info, qr_url):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET qr_code='{qr_url}' "
                           f"WHERE peer_id={msg_info['peer_id']} AND user_id={msg_info['from_id']}")
            connect.commit()
    finally:
        connect.close()


def unpin_qr(msg_info):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET qr_code=NULL "
                           f"WHERE peer_id={msg_info['peer_id']} AND user_id={msg_info['from_id']}")
            connect.commit()
    finally:
        connect.close()


def get_qr(user_id, peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT qr_code FROM users "
                           f"WHERE peer_id={peer_id} AND user_id={user_id}")
            return cursor.fetchone()[0]
    finally:
        connect.close()


def get_all_qr(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT qr_code, first_name, last_name, user_id FROM users "
                           f"WHERE peer_id={peer_id} ORDER BY qr_code")
            return cursor.fetchall()
    finally:
        connect.close()