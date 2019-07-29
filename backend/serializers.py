from rest_framework import serializers
from .models import Denuncia


class DenunciaSerializer(serializers.ModelSerializer):
    tipo = serializers.SlugRelatedField(
        read_only=True,
        slug_field='titulo'
    )

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
