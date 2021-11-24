from db.connection import get_connect


def configure():
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute("""CREATE TABLE users 
                             (
                                id serial,
                                user_id int NOT NULL,
                                peer_id int NOT NULL,
                                first_name varchar(100) NOT NULL,
                                last_name varchar(100) NOT NULL,
                                skip_lessons_of int NOT NULL DEFAULT 0,
                                skip_lessons_n_of int NOT NULL DEFAULT 0,
                                qr_code varchar(150)
                             )""")
            cursor.execute("""CREATE TABLE timetables 
                                         (
                                            url int NOT NULL,
                                            peer_id int NOT NULL
                                         )""")
            cursor.execute("""CREATE TABLE homework 
                                                     (  peer_id int NOT NULL,
                                                        name text NOT NULL,
                                                        text_homework text,
                                                        attach_homework text
                                                     )""")
            connect.commit()

    finally:
        connect.close()