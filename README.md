#Requerimientos
`Django==1.7.4`

`Pillow==2.7.0`

`django-filter==0.9.2`

`djangorestframework==3.0.5`

`psycopg2==2.6`

`vobject==0.6.6`

`django-adminactions`

`django-admin-bootstrapped`

`django-cors-headers`

#Instalación

`git clone git@github.com:melizeche/listahu.git`

`virtualenv env`

`source env/bin/activate `

`pip install -r requirements.txt`

Configurar listahu/settings.py

`./manage.py makemigrations backend`

`./manage.py migrate`

`./manage.py createsuperuser`

#Opcional

Se recomienda PostgreSQL pero se puede utilizar cualquier base de datos soportada por Django(ej. MySQL, SQLite) 

##Paquetes necesarios (Ubuntu/Debian)

`apt-get install postgresql-9.3 postgresql-contrib-9.3 postgresql-server-dev-9.3 libpq-dev libjpeg-dev python-dev python-pip python-virtualenv git`

##Configuracion rápida PostgreSQL

`sudo -u postgres psql;`

`CREATE USER usuario WITH PASSWORD 'password';`(cambiar por el usuario y password deseado)

`sudo -u postgres createdb -O usuario listahu`