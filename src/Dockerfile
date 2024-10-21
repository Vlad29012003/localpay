FROM python:3.10


LABEL maintainer="vladosmen29@gmail.com"


ENV PYTHONUNBUFFERED=1


WORKDIR /app


COPY requirements.txt /app/


RUN apt-get update && apt-get upgrade -y


RUN pip install -r requirements.txt


COPY pgbouncer.ini /etc/pgbouncer/pgbouncer.ini


COPY userlist.txt /etc/pgbouncer/userlist.txt


RUN chmod 600 /etc/pgbouncer/pgbouncer.ini /etc/pgbouncer/userlist.txt


COPY . .


VOLUME ["/app/staticfiles", "/app/media"]


EXPOSE 8000


CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

