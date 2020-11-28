# stock-projection-service
Python 3.8 Flask web service

## Installation

```bash
$ pip install -r requirements.txt
```

You need to set some environment variables:

```bash
export WEB_CONCURRENCY=3
export MONGODB_DATABASE=stock-db
export MONGODB_HOSTNAME=<HOSTNAME>
export MONGODB_PASSWORD=<PASSWORD>
export MONGODB_USERNAME=<USERNAME>
```

## Running the app

```bash
# development
$ gunicorn app:app --worker-class gevent --timeout 60 --worker-connections 10 --preload
```

Navigate to [`http://localhost:8000/`](http://localhost:8000/) or [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/).

## Serve on a Docker container

```bash
# starting up
$ docker-compose up

# shutting down
$ docker-compose down
```

Open your browser on [`http://localhost:5000/`](http://localhost:5000/) or [`http://127.0.0.1:5000/`](http://127.0.0.1:5000/).
