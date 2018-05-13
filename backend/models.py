# -*- encoding: utf-8 -*-
from django.db import models
import os
import time
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from autoslug import AutoSlugField
from backend.extras import create_thumbnail

# Create your models here.

THUMBNAIL_BASEWIDTH = 200


def rename(instance, filename):
    # print instance.numero
    path = "denuncias/"
    filename = filename.replace(" ", "_")
    if not instance.numero:
        format = time.strftime("%Y%m%d%H%M", time.localtime()) + "-" + filename
    else:
        format = str(instance.numero) + "_" + \
                 time.strftime("%Y%m%d%H%M", time.localtime()) + "_" + filename
    return os.path.join(path, format)


class Estadistica(models.Model):
    nombre = models.CharField("Titulo de la Estadistica", max_length=30)
    valor = models.IntegerField(null=True, blank=True, default=0)
    otro = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.nombre


class Tipo(models.Model):
    titulo = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from='titulo', unique=True, blank=True, null=True)
    desc = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.titulo


class Denuncia(models.Model):
    tipo = models.ForeignKey(Tipo)
    numero = models.CharField(max_length=30,
                              help_text="Podes ingresar como 09XXXXXXXX, 5959XXXXXXXX o +5959XXXXXXXX")
    screenshot = models.ImageField('Captura de pantalla', upload_to=rename,
                                   help_text="Si fue una llamada hacer captura del registro de llamadas")
    desc = models.TextField('Descripción o comentarios al respecto', null=True, blank=True,
                            help_text="Completar especialmente si fue una llamada")
    check = models.NullBooleanField(null=True, default=False)
    votsi = models.IntegerField(null=True, blank=True, default=0)
    votno = models.IntegerField(null=True, blank=True, default=0)
    activo = models.BooleanField(default=True)
    added = models.DateTimeField(
        'Agregado', auto_now_add=True, null=True, blank=True)

    def validateNumber(self, number):
        number = number.replace(" ", "")
        number = number.replace("-", "")
        number = number.replace(")", "")
        number = number.replace("(", "")
        if number.startswith('09'):
            new = "5959" + number[2:]
        elif number.startswith('+'):
            new = number[1:]
        else:
            new = number

        if len(new) == 12:
            return new
        else:
            return new

    def save(self, *args, **kwargs):
        self.numero = self.validateNumber(self.numero)
        super(Denuncia, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.numero + " - " + unicode(self.tipo)


def update_stats(sender, instance, created, **kwargs):
    try:
        cant = Estadistica.objects.get(nombre='denuncias')
    except Estadistica.DoesNotExist:
        cant = None
    if created:
        if cant:
            cant.valor = Denuncia.objects.all().count()
            cant.save()

        else:
            cant = Denuncia.objects.all().count()
            a = Estadistica(nombre="denuncias", valor=cant)
            a.save()


def thumbnail(sender, instance, created, **kwargs):
    if created:
        try:
            img = create_thumbnail(settings.MEDIA_ROOT + str(instance.screenshot), THUMBNAIL_BASEWIDTH)
        except:
            pass


post_save.connect(update_stats, sender=Denuncia)
post_save.connect(thumbnail, sender=Denuncia)
