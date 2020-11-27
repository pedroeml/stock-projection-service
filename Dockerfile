FROM python:3.8

WORKDIR /var/www/

ADD requirements.txt /var/www/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ADD *.py /var/www/

EXPOSE 5000

ENTRYPOINT [ "gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--worker-class", "gevent", "--timeout", "60", "--worker-connections", "10", "--preload" ]
