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

### run and hot-reloads for development

```
FLASK_ENV=development FLASK_DEBUG=1 flask run
```

### run for development

```
FLASK_ENV=development flask run
```

### run for production

```
flask run
```

## License

[Apache License 2.0](./LICENSE)