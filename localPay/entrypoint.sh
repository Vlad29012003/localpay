#!/bin/sh
alembic upgrade head
python ./db/scripts/users.py
python ./db/scripts/payments.py
python ./db/scripts/comments.py
exec uvicorn main:app --host 0.0.0.0 --port 8000
