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

#     # Извлечение данных из таблицы localpay_comment
#     source_cur.execute("SELECT id, text, created_at, user2_id, mont_avail_balance, mont_balance, new_avail_balance, new_balance, old_avail_balance, old_balance, type_pay FROM localpay_comment")
#     comments = source_cur.fetchall()

#     # Определение запроса для вставки данных в таблицу localpay_comments
#     insert_query = """
#     INSERT INTO localpay_comments (
#         id, 
#         text, 
#         created_at, 
#         user_id, 
#         new_spent_money, 
#         new_available_balance, 
#         add_to_spent_money, 
#         add_to_available_balance, 
#         old_spent_money, 
#         old_available_balance, 
#         payment_type
#     ) VALUES (
#         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#     )
#     """

#     # Перебор данных и вставка их в целевую таблицу
#     for comment in comments:
#         target_cur.execute(insert_query, (
#             comment[0],  # id
#             comment[1],  # text
#             comment[2],  # created_at
#             comment[3],  # user_id
#             comment[4],  # new_spent_money
#             comment[5],  # new_available_balance
#             comment[6],  # add_to_spent_money
#             comment[7],  # add_to_available_balance
#             comment[8],  # old_spent_money
#             comment[9],  # old_available_balance
#             comment[10]  # payment_type
#         ))

#     # Коммит транзакции
#     target_conn.commit()
#     print("Data transferred successfully.")

#     # Обновите последовательности для всех таблиц после переноса данных
#     update_sequence(target_cur, 'localpay_comments', 'id', 'localpay_comments_id_seq')

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

    # Извлечение данных из таблицы localpay_comment
    source_cur.execute("SELECT id, text, created_at, user2_id, mont_avail_balance, mont_balance, new_avail_balance, new_balance, old_avail_balance, old_balance, type_pay FROM localpay_comment")
    comments = source_cur.fetchall()

    # Определение запроса для вставки данных в таблицу localpay_comments
    insert_query = """
    INSERT INTO localpay_comments (
        id, 
        text, 
        created_at, 
        user_id, 
        new_spent_money, 
        new_available_balance, 
        add_to_spent_money, 
        add_to_available_balance, 
        old_spent_money, 
        old_available_balance, 
        payment_type
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (id) 
    DO UPDATE SET 
        text = EXCLUDED.text,
        created_at = EXCLUDED.created_at,
        user_id = EXCLUDED.user_id,
        new_spent_money = EXCLUDED.new_spent_money,
        new_available_balance = EXCLUDED.new_available_balance,
        add_to_spent_money = EXCLUDED.add_to_spent_money,
        add_to_available_balance = EXCLUDED.add_to_available_balance,
        old_spent_money = EXCLUDED.old_spent_money,
        old_available_balance = EXCLUDED.old_available_balance,
        payment_type = EXCLUDED.payment_type;
    """

    # Перебор данных и вставка их в целевую таблицу
    for comment in comments:
        target_cur.execute(insert_query, (
            comment[0],  # id
            comment[1],  # text
            comment[2],  # created_at
            comment[3],  # user_id
            comment[4],  # new_spent_money
            comment[5],  # new_available_balance
            comment[6],  # add_to_spent_money
            comment[7],  # add_to_available_balance
            comment[8],  # old_spent_money
            comment[9],  # old_available_balance
            comment[10]  # payment_type
        ))

    # Коммит транзакции
    target_conn.commit()
    print("Data transferred successfully.")

    # Обновите последовательности для всех таблиц после переноса данных
    update_sequence(target_cur, 'localpay_comments', 'id', 'localpay_comments_id_seq')

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
