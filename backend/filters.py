"""
Viewset filters.
"""
import django_filters

from backend.models import Denuncia, Estadistica, Tipo


class DenunciaFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter(field_name='tipo__slug')
    numero = django_filters.CharFilter(field_name='numero', lookup_expr='icontains')
    id_from = django_filters.NumberFilter(field_name='id', lookup_expr='gte')
    id_to = django_filters.NumberFilter(field_name='id', lookup_expr='lte')
    added_from = django_filters.DateTimeFilter(
        field_name='added', lookup_expr='gte')
    added_to = django_filters.DateTimeFilter(
        field_name='added', lookup_expr='lt')
    check = django_filters.BooleanFilter(field_name='check')

    class Meta:
        model = Denuncia
        fields = ('tipo', 'numero', 'id', 'added', 'check')
