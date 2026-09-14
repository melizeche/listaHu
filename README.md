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
* Django 2.2+

### Other libs
```
Django==2.2.3
django-adminactions==1.6.0
django-autoslug==1.9.4
django-cors-headers==3.0.2
django-filter==2.2.0
djangorestframework==3.10.1
gunicorn==19.9.0
Pillow==6.1.0
psycopg2-binary==2.8.3
unicodecsv==0.14.1
vobject==0.9.6.1
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
sudo apt install postgresql postgresql-contrib postgresql-server-dev libpq-dev libjpeg-dev python3-dev python3-pip python3-virtualenv git
```

### Quick PostgreSQL configuration

`sudo -u postgres psql;`

`CREATE USER usuario WITH PASSWORD 'password';` (replace 'usuario' and 'password' with desired username and password)

`sudo -u postgres createdb -O usuario listahu`

## TODO

- ~Python 3+ support~
- ~Upgrade Django version~
- ~Unit tests~
- Documentation(APIs, Configuration Options)

## Tests

The suite ships with its own settings module, so it runs without a
`conf/settings.py` and without a database server (SQLite is used by default):

```
./manage.py test --settings=conf.settings_test
```

A few endpoints rely on PostgreSQL-only features (`DISTINCT ON`): the download
of the full/no-spam vCards and the `/api/v1/numeros/` endpoint. Those tests are
skipped automatically on SQLite. To run them too, point the suite at a
PostgreSQL server:

```
LISTAHU_TEST_DB=postgres ./manage.py test --settings=conf.settings_test
```

The connection can be tuned with `LISTAHU_TEST_DB_NAME`, `LISTAHU_TEST_DB_USER`,
`LISTAHU_TEST_DB_PASSWORD`, `LISTAHU_TEST_DB_HOST` and `LISTAHU_TEST_DB_PORT`.

Tests live in `backend/tests/`, one module per layer (`test_models.py`,
`test_forms.py`, `test_filters.py`, `test_serializers.py`, `test_views.py`,
`test_api.py`, `test_admin.py` and the shared `helpers.py`).

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License

This project is licensed under the terms of the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details
