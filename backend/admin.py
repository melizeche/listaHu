from django.contrib import admin
from backend.models import Tipo, Denuncia, Estadistica
from django.contrib.admin import site
import adminactions.actions as actions

# register all adminactions
actions.add_to_site(site)


class DenunciaAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "checked", "added", "votsi", "votno", "activo")
    list_filter = ("tipo", "checked", "activo")
    search_fields = ("numero", "added", "desc")


class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "valor", "otro")


admin.site.register(Denuncia, DenunciaAdmin)
admin.site.register(Tipo)
admin.site.register(Estadistica, EstadisticaAdmin)
