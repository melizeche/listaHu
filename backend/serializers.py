from rest_framework import serializers
from .models import Denuncia


class DenunciaSerializer(serializers.ModelSerializer):
    tipo = serializers.SlugRelatedField(
        read_only=True,
        slug_field='titulo'
    )
    # The model attribute is ``checked`` (``check`` clashes with
    # ``Model.check()``); the published API keeps the original key.
    check = serializers.BooleanField(source='checked', required=False,
                                     allow_null=True)

    class Meta:
        model = Denuncia
        fields = ('id', 'numero', 'tipo', 'screenshot',
                  'desc', 'check', 'added', 'votsi', 'votno')


class ListaSerializer(serializers.ModelSerializer):
    tipo = serializers.SlugRelatedField(
        read_only=True,
        slug_field='titulo'
    )

    class Meta:
        model = Denuncia
        fields = ('id', 'numero', 'tipo', 'screenshot', 'added')


class ListaUnicaSerializer(serializers.ModelSerializer):
    tipo = serializers.SlugRelatedField(
        read_only=True,
        slug_field='titulo'
    )

    class Meta:
        model = Denuncia
        fields = ('id', 'numero', 'tipo', 'added')
