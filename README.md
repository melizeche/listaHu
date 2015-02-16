##Paquetes necesarios (Ubuntu/Debian)

`apt-get install postgresql-9.3 postgresql-contrib-9.3 postgresql-server-dev-9.3 python-dev python-pip python-virtualenv git`

##Configuracion de la base de datos

`sudo -u postgres psql`

`ALTER ROLE postgres with PASSWORD 'password'` (cambiar por el password deseado)

`sudo -u postgres createdb -O postgres listahu`

##Instalación

`git clone git@github.com:melizeche/listahu.git`

`virtualenv env`

`source env/bin/activate `

`pip install -r requirements.txt`

Configurar listahu/settings.py

`./manage.py makemigrations backend`

`./manage.py migrate`

`./manage.py createsuperuser`
