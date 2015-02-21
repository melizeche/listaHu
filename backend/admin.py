# -*- encoding: utf-8 -*-
from django.contrib import admin
from backend.models import Tipo, Denuncia, Estadistica
from django.contrib.admin import site
import adminactions.actions as actions

# register all adminactions
actions.add_to_site(site)

# Register your models here.
class DenunciaAdmin(admin.ModelAdmin):
	list_display=('numero','tipo', 'check','added','votsi','votno')

admin.site.register(Denuncia, DenunciaAdmin)
admin.site.register(Tipo)
admin.site.register(Estadistica)

