from django.db import models, migrations

TIPOS = ['SPAM','Estafa','Extorsión']

def add_tipos(apps, schema_editor):
    Tipo = apps.get_model("backend", "Tipo")
    for titulo in TIPOS:
        Tipo.objects.create(titulo=titulo)


def del_tipos(apps, schema_editor):
    Tipo = apps.get_model("backend", "Tipo")
    for titulo in TIPOS:
        Tipo.objects.get(titulo=titulo).delete()
        #tip.save()

class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_tipos, del_tipos),
    ]
