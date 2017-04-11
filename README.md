# ListaHu
Lista Hũ is a project that aims to create a crowdsourced database of sms spammers and blackmailers, so the numbers can be blocked in the future.

## Requirements

### Main Requirements
* Python 2.7.5+
* PostgreSQL 9.3+
* Django 1.8.14

### Other libs
`Pillow==2.9.0`
  
`django-filter==0.11.0`

`djangorestframework==3.0.5`

`psycopg2==2.6`

`vobject==0.9.2`

`django-adminactions==1.1`

`django-admin-bootstrapped==2.5.7`

`django-cors-headers==1.1.0`

`django-autoslug==1.9.3`


## Instructions


```
git clone git@github.com:melizeche/listahu.git
cd listahu
virtualenv env
source env/bin/activate 
pip install -r requirements.txt
```
Configurate listahu/settings.py (Config example listahu/settings.py.example)

```
./manage.py makemigrations backend
./manage.py migrate
./manage.py createsuperuser
```
## Optional

PostgreSQL is recommended but you can use any database supported by Django(e.g. MySQL, SQLite) 

### Necesary packages (Ubuntu/Debian)

```
apt-get install postgresql postgresql-contrib postgresql-server-dev libpq-dev libjpeg-dev python-dev python-pip python-virtualenv git
```

### Quick PostgreSQL configuration

`sudo -u postgres psql;`

`CREATE USER usuario WITH PASSWORD 'password';` (replace 'usuario' and 'password' with desired username and password)

`sudo -u postgres createdb -O usuario listahu`

## TODO

- Documentation(APIs, Configuration Options)