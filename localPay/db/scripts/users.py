# import psycopg2

# # Подключение к первой базе данных (myproject)
# source_conn = psycopg2.connect(
#     dbname="myproject",
#     user="postgres",
#     password="skynet",
#     host="91.210.169.237"
# )

# # Подключение ко второй базе данных (localPayDev)
# target_conn = psycopg2.connect(
#     dbname="localPayDev",
#     user="postgres",
#     password="postgres",
#     host="db"
# )

# def update_sequence(cursor, table_name, id_column, sequence_name):
#     cursor.execute(f"""
#         SELECT setval(
#             %s,
#             (SELECT COALESCE(MAX({id_column}), 1) FROM {table_name}),
#             false
#         );
#     """, (sequence_name,))


# def user_exists(cursor, user_id):
#     cursor.execute("SELECT 1 FROM localpay_users WHERE id = %s", (user_id,))
#     return cursor.fetchone() is not None


# try:
#     source_cur = source_conn.cursor()
#     target_cur = target_conn.cursor()

#     # Извлечение данных из таблицы localpay_user_mon
#     source_cur.execute("""
#         SELECT 
#             id, name, surname, login, password, date_reg, is_staff, is_active, 
#             balance, avail_balance, region, refill, write_off, comment, planup_id 
#         FROM localpay_user_mon
#     """)
#     users = source_cur.fetchall()

#     # Определение запроса для вставки данных в таблицу localpay_users
#     insert_query = """
#     INSERT INTO localpay_users (
#         id, 
#         name, 
#         surname, 
#         login, 
#         hashed_password, 
#         date_reg, 
#         access_to_payments, 
#         is_active, 
#         available_balance, 
#         spent_money, 
#         region, 
#         refill, 
#         write_off, 
#         role, 
#         planup_id
#     ) VALUES (
#         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#     )
#     """

#     # Перебор данных и вставка их в целевую таблицу
#     for user in users:
#         target_cur.execute(insert_query, (
#             user[0],  # id
#             user[1],  # name
#             user[2],  # surname
#             user[3],  # login
#             user[4],  # hashed_password
#             user[5],  # date_reg
#             user[6],  # access_to_payments (ранее is_staff)
#             user[7],  # is_active
#             user[9],  # available_balance (ранее avail_balance)
#             user[8],  # spent_money (ранее balance)
#             # Преобразование region в ENUM
#             'CHUY' if user[10] == 'Чуйская' else
#             'ISSYK_KUL' if user[10] == 'Иссык-кульская' else
#             'NARYN' if user[10] == 'Нарынская' else
#             'JALAL_ABAD' if user[10] == 'Джалал-Абадская' else
#             'BATKEN' if user[10] == 'Баткенская' else
#             'OSH' if user[10] == 'Ошская' else
#             'TALAS' if user[10] == 'Таласская' else None,
#             user[11], # refill
#             user[12], # write_off
#             'USER',   # role
#             user[14]  # planup_id
#         ))

#     # Коммит транзакции
#     target_conn.commit()
#     print("Data transferred successfully.")

#     # Обновите последовательности для всех таблиц после переноса данных
#     update_sequence(target_cur, 'localpay_users', 'id', 'localpay_users_id_seq')

#     # Коммит транзакции для обновления последовательностей
#     target_conn.commit()
#     print("Sequences updated successfully.")

# except (Exception, psycopg2.DatabaseError) as error:
#     print(f"Error: {error}")
#     if target_conn:
#         target_conn.rollback()
# finally:
#     if source_cur:
#         source_cur.close()
#     if source_conn:
#         source_conn.close()
#     if target_cur:
#         target_cur.close()
#     if target_conn:
#         target_conn.close()




import psycopg2

# Подключение к первой базе данных (myproject)
source_conn = psycopg2.connect(
    dbname="myproject",
    user="postgres",
    password="skynet",
    host="91.210.169.237"
)

# Подключение ко второй базе данных (localPayDev)
target_conn = psycopg2.connect(
    dbname="localPayDev",
    user="postgres",
    password="postgres",
    host="db"
)

def update_sequence(cursor, table_name, id_column, sequence_name):
    cursor.execute(f"""
        SELECT setval(
            %s,
            (SELECT COALESCE(MAX({id_column}), 1) FROM {table_name}),
            false
        );
    """, (sequence_name,))

try:
    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()

    # Извлечение данных из таблицы localpay_user_mon
    source_cur.execute("""
        SELECT 
            id, name, surname, login, password, date_reg, is_staff, is_active, 
            balance, avail_balance, region, refill, write_off, comment, planup_id 
        FROM localpay_user_mon
    """)
    users = source_cur.fetchall()

    # Определение запроса для вставки данных в таблицу localpay_users
    insert_query = """
    INSERT INTO localpay_users (
        id, 
        name, 
        surname, 
        login, 
        hashed_password, 
        date_reg, 
        access_to_payments, 
        is_active, 
        available_balance, 
        spent_money, 
        region, 
        refill, 
        write_off, 
        role, 
        planup_id
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (id) 
    DO UPDATE SET 
        name = EXCLUDED.name,
        surname = EXCLUDED.surname,
        login = EXCLUDED.login,
        hashed_password = EXCLUDED.hashed_password,
        date_reg = EXCLUDED.date_reg,
        access_to_payments = EXCLUDED.access_to_payments,
        is_active = EXCLUDED.is_active,
        available_balance = EXCLUDED.available_balance,
        spent_money = EXCLUDED.spent_money,
        region = EXCLUDED.region,
        refill = EXCLUDED.refill,
        write_off = EXCLUDED.write_off,
        role = EXCLUDED.role,
        planup_id = EXCLUDED.planup_id;
    """

    # Перебор данных и вставка их в целевую таблицу
    for user in users:
        target_cur.execute(insert_query, (
            user[0],  # id
            user[1],  # name
            user[2],  # surname
            user[3],  # login
            user[4],  # hashed_password
            user[5],  # date_reg
            user[6],  # access_to_payments (ранее is_staff)
            user[7],  # is_active
            user[9],  # available_balance (ранее avail_balance)
            user[8],  # spent_money (ранее balance)
            # Преобразование region в ENUM
            'CHUY' if user[10] == 'Чуйская' else
            'ISSYK_KUL' if user[10] == 'Иссык-кульская' else
            'NARYN' if user[10] == 'Нарынская' else
            'JALAL_ABAD' if user[10] == 'Джалал-Абадская' else
            'BATKEN' if user[10] == 'Баткенская' else
            'OSH' if user[10] == 'Ошская' else
            'TALAS' if user[10] == 'Таласская' else None,
            user[11], # refill
            user[12], # write_off
           # 'USER',   # role
            'ADMIN' if user[6] == True else 'USER',
            user[14]  # planup_id
        ))

    # Коммит транзакции
    target_conn.commit()
    print("Data transferred successfully.")

    # Обновите последовательности для всех таблиц после переноса данных
    update_sequence(target_cur, 'localpay_users', 'id', 'localpay_users_id_seq')

    # Коммит транзакции для обновления последовательностей
    target_conn.commit()
    print("Sequences updated successfully.")

except (Exception, psycopg2.DatabaseError) as error:
    print(f"Error: {error}")
    if target_conn:
        target_conn.rollback()
finally:
    if source_cur:
        source_cur.close()
    if source_conn:
        source_conn.close()
    if target_cur:
        target_cur.close()
    if target_conn:
        target_conn.close()
