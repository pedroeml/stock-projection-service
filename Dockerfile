FROM python:3.8-slim

WORKDIR /var/www/

ADD requirements.txt /var/www/
RUN pip install --no-cache-dir -r requirements.txt

ADD *.py /var/www/

EXPOSE 5000

ENTRYPOINT [ "gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--worker-class", "gevent", "--worker-connections", "100", "--preload" ]
