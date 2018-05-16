# -*- coding: utf-8 -*-


from django.db import migrations, models
import backend.models
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Denuncia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.CharField(help_text=b'Podes ingresar como 09XXXXXXXX, 5959XXXXXXXX o +5959XXXXXXXX', max_length=30)),
                ('screenshot', models.ImageField(help_text=b'Si fue una llamada hacer captura del registro de llamadas', upload_to=backend.models.rename, verbose_name=b'Captura de pantalla')),
                ('desc', models.TextField(help_text=b'Completar especialmente si fue una llamada', null=True, verbose_name=b'Descripci\xc3\xb3n o comentarios al respecto', blank=True)),
                ('check', models.NullBooleanField(default=False)),
                ('votsi', models.IntegerField(default=0, null=True, blank=True)),
                ('votno', models.IntegerField(default=0, null=True, blank=True)),
                ('activo', models.BooleanField(default=True)),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name=b'Agregado', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Estadistica',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=30, verbose_name=b'Titulo de la Estadistica')),
                ('valor', models.IntegerField(default=0, null=True, blank=True)),
                ('otro', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=30)),
                ('slug', autoslug.fields.AutoSlugField(null=True, populate_from=b'titulo', editable=False, blank=True, unique=True)),
                ('desc', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='denuncia',
            name='tipo',
            field=models.ForeignKey(to='backend.Tipo'),
        ),
    ]
