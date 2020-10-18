# HOW TO DEPLOY THE PROJECT

## REQUIREMENTS

* Python3 (> 3.4 version)
* MySQL (> 5.5 version)
* [Redis](https://redis.io/)
* pip3
* [shadowsocks](https://github.com/shadowsocks/shadowsocks) or [shadowsocks-libev](https://github.com/shadowsocks/shadowsocks-libev)
* [ScholarToolFrontEnd](https://github.com/celerysoft/ScholarToolFrontEnd)

## Project setup

### Create Database

database schema file is locate at /application/config/schema.sql

### Setup virtual environment

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

### Initialization and Configure

```
# activate venv first
source venv/bin/activate
# create config file on project_base_dir/local_settings.py
FLASK_APP=manage.py flask create
# modify local_settings.py for your own.
vim local_settings.py
# after you finish this, run next command
FLASK_APP=manage.py flask init
```

now you have a superuser:

username: admin

password: 12345679

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

### Time-bound Task

> activate venv first

`15 1 1 * * python application/schedule/a000_execute_a_series_schedules.py`

`*/30 * * * * python application/schedule/b000_execute_b_series_schedules.py`

`15 0 * * * python application/schedule/c000_execute_c_series_schedules.py`


# Sponsor

[JetBrains](https://www.jetbrains.com/community/opensource/)

# License

[Apache License 2.0](./LICENSE)