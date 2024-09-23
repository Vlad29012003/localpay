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

# try:
#     source_cur = source_conn.cursor()
#     target_cur = target_conn.cursor()

#     # Извлечение данных из таблицы localpay_pays
#     source_cur.execute("SELECT id, number_payment, date_payment, accept_payment, ls_abon, money, status_payment, user_id, annulment, comment, updated_at, document_number FROM localpay_pays")
#     payments = source_cur.fetchall()

#     # Определение запроса для вставки данных в таблицу localpay_payments
#     insert_query = """
#     INSERT INTO localpay_payments (
#         id, 
#         payment_number, 
#         payment_date, 
#         payment_accept, 
#         ls_abon, 
#         money, 
#         payment_status, 
#         user_id, 
#         annulment, 
#         comment, 
#         updated_at, 
#         document_number
#     ) VALUES (
#         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#     )
#     """

#     # Перебор данных и вставка их в целевую таблицу
#     for payment in payments:
#         target_cur.execute(insert_query, (
#             payment[0],  # id
#             payment[1],  # payment_number
#             payment[2],  # payment_date
#             payment[3],  # payment_accept
#             payment[4],  # ls_abon
#             payment[5],  # money
#             payment[6],  # payment_status
#             payment[7],  # user_id
#             payment[8],  # annulment
#             payment[9],  # comment
#             payment[10], # updated_at
#             payment[11]  # document_number
#         ))

#     # Коммит транзакции
#     target_conn.commit()
#     print("Data transferred successfully.")

#     # Обновите последовательности для всех таблиц после переноса данных
#     update_sequence(target_cur, 'localpay_payments', 'id', 'localpay_payments_id_seq')

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

    # Извлечение данных из таблицы localpay_pays
    source_cur.execute("SELECT id, number_payment, date_payment, accept_payment, ls_abon, money, status_payment, user_id, annulment, comment, updated_at, document_number FROM localpay_pays")
    payments = source_cur.fetchall()

    # Определение запроса для вставки данных в таблицу localpay_payments
    insert_query = """
    INSERT INTO localpay_payments (
        id, 
        payment_number, 
        payment_date, 
        payment_accept, 
        ls_abon, 
        money, 
        payment_status, 
        user_id, 
        annulment, 
        comment, 
        updated_at, 
        document_number
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (id) 
    DO UPDATE SET 
        payment_number = EXCLUDED.payment_number,
        payment_date = EXCLUDED.payment_date,
        payment_accept = EXCLUDED.payment_accept,
        ls_abon = EXCLUDED.ls_abon,
        money = EXCLUDED.money,
        payment_status = EXCLUDED.payment_status,
        user_id = EXCLUDED.user_id,
        annulment = EXCLUDED.annulment,
        comment = EXCLUDED.comment,
        updated_at = EXCLUDED.updated_at,
        document_number = EXCLUDED.document_number;
    """

    # Перебор данных и вставка их в целевую таблицу
    for payment in payments:
        target_cur.execute(insert_query, (
            payment[0],  # id
            payment[1],  # payment_number
            payment[2],  # payment_date
            payment[3],  # payment_accept
            payment[4],  # ls_abon
            payment[5],  # money
            payment[6],  # payment_status
            payment[7],  # user_id
            payment[8],  # annulment
            payment[9],  # comment
            payment[10], # updated_at
            payment[11]  # document_number
        ))

    # Коммит транзакции
    target_conn.commit()
    print("Data transferred successfully.")

    # Обновите последовательности для всех таблиц после переноса данных
    update_sequence(target_cur, 'localpay_payments', 'id', 'localpay_payments_id_seq')

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
