# ListaHũ
Lista Hũ is a project that aims to create a crowdsourced database of sms spammers and blackmailers, so the numbers can be blocked in the future.

Lista Hũ has an RESTful API to query the database and the dataset is released under the
CC BY-NC-SA 4.0 license.


## Lista Hũ in the press
* https://www.youtube.com/watch?v=yRB54L6wyGI
* http://www.lanacion.com.py/2016/04/22/lista-hu-logro-detectar-casos-de-estafa-y-extorsion/
* http://www.abc.com.py/ciencia/lista-h-contra-la-estafa-1339474.html
* http://www.extra.com.py/actualidad/surge-lista-hu-contra-estafas-y-extorsiones.html
* http://www.hoy.com.py/nacionales/lista-huu-crean-base-de-datos-de-estafadores-y-vendedores-molestos

## Awards
* World Summit Award Paraguay 2015: Winner In E-Government & Open Data

## Requirements

### Main Requirements
* Python 3.5+ (No longer compatible with Python 2.7, finally!)
* PostgreSQL 9.3+
* Django 1.8.19

### Other libs
```
Django==1.8.19
Pillow==5.1.0
django-filter==0.11.0
djangorestframework==3.1.3
psycopg2==2.7.4
vobject==0.9.2
django-adminactions==1.5
django-admin-bootstrapped==2.5.7
django-cors-headers==1.1.0
django-autoslug==1.9.3
gunicorn==19.8.1
```


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

- ~Python 3+ support~
- Upgrade Django version
- Unit tests
- Documentation(APIs, Configuration Options)

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License

This project is licensed under the terms of the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details
