"""
Viewset filters.
"""
import django_filters

from backend.models import Denuncia, Estadistica, Tipo


class DenunciaFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter(name='tipo__slug')
    numero = django_filters.CharFilter(name='numero', lookup_type='icontains')
    id_from = django_filters.NumberFilter(name='id', lookup_type='gte')
    id_to = django_filters.NumberFilter(name='id', lookup_type='lte')
    added_from = django_filters.DateTimeFilter(
        name='added', lookup_type='gte')
    added_to = django_filters.DateTimeFilter(
        name='added', lookup_type='lt')
    check = django_filters.BooleanFilter(name='check')

    class Meta:
        model = Denuncia
        fields = ('tipo', 'numero', 'id', 'added', 'check')
