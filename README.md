# HOW TO DEPLOY THE PROJECT

## REQUIREMENTS
    * Python3 (> 3.4 version)
    * MySQL (> 5.5 version)
    * Redis
    * pip3

## Project setup

### setup virtual environment

#### VirtualEnv

```
pip install virtualenv
virtualenv -p python3 --no-site-packages /path/to/new/virtual/environment 
```
	
#### venv

```
python3 -m venv /path/to/new/virtual/environment
```

### install requirements

```
pip install -r requirements.txt
```

### Configure

    * Go to project base dir .
    * touch local_settings.py
    * Modify local_settings.py for your own.

## Run

### Back-end service

#### run and hot-reloads for development

```
FLASK_ENV=development FLASK_DEBUG=1 flask run
```

#### run for development

```
FLASK_ENV=development flask run
```

#### run for production

```
flask run
```

### Task Queue

recommend use [Supervisor](http://supervisord.org/) to handle the following processes

```
# activate venv first
source venv/bin/activate

# common background task
celery -A application.util.background_task worker --loglevel=info
# scholar payment
celery -A application.module.payment.scholar.app worker --loglevel=info
# network usage monitor
python application/module/network_usage_monitor/app.py
```

## License

[Apache License 2.0](./LICENSE)