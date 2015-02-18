# -*- encoding: utf-8 -*-
from django.contrib import admin
from backend.models import Tipo, Denuncia, Estadistica

# Register your models here.
class DenunciaAdmin(admin.ModelAdmin):
	list_display=('numero','tipo', 'check','added','votsi','votno')

admin.site.register(Denuncia, DenunciaAdmin)
admin.site.register(Tipo)
admin.site.register(Estadistica)

