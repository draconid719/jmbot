## Requirements

- Python 3.7+ (preferred 3.8)
- Pip 19+

***
## Installation
```
cd wide-bot
```

Installing Virtual environment
```
pip install virtualenv
sudo apt-get install python3-venv

```

Creating Virtual environment
```
python -m venv <environment_name>
```

Initiating Virtual environment
```
source ./<environment_name>/bin/activate
```

> **mariadbclient** should be installed
```
libmariadbclient-dev or default-libmysqlclient-dev
```
Please check `https://pypi.org/project/mysqlclient/`

Installing packages
```
pip install -r requirements.txt
```
#### Set up database
```
python manage.py migrate
```
***
### Starting bot
Input API key for exchanges

```
vim wide-bot\jmproject\.env
```

***
### Launch Bot

```
cd wide-bot\jmproject

python manage.py createsuperuser
python manage.py createcachetable // Create cache table

...
python manage.py runserver
```

Go to:
http://127.0.0.1:8000 home page
http://127.0.0.1:8000/admin django administrator page

