-- Для таблицы localpay_users
SELECT setval(
    'localpay_users_id_seq',  -- Имя вашей последовательности для таблицы localpay_users
    (SELECT COALESCE(MAX(id), 1) FROM localpay_users)
);

-- Для таблицы localpay_payments
SELECT setval(
    'localpay_payments_id_seq',  -- Имя вашей последовательности для таблицы localpay_payments
    (SELECT COALESCE(MAX(id), 1) FROM localpay_payments)
);

-- Для таблицы localpay_comments
SELECT setval(
    'localpay_comments_id_seq',  -- Имя вашей последовательности для таблицы localpay_comments
    (SELECT COALESCE(MAX(id), 1) FROM localpay_comments)
);
