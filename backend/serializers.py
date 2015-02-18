# -*- encoding: utf-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import User
from models import Denuncia

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('url', 'username', 'email', 'groups')

class DenunciaSerializer(serializers.ModelSerializer):
	tipo = serializers.SlugRelatedField(
        read_only=True,
        slug_field='titulo'
     )
	class Meta:
		model = Denuncia
		fields = ('id', 'numero', 'tipo', 'screenshot', 'check','added','votsi','votno')

class ListaSerializer(serializers.ModelSerializer):
	tipo = serializers.SlugRelatedField(
        read_only=True,
        slug_field='titulo'
     )
	class Meta:
		model = Denuncia
		fields = ('id', 'numero', 'tipo', 'screenshot','added')