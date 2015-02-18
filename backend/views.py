# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.models import User, Group
from django.core.servers.basehttp import FileWrapper
from rest_framework import viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, DjangoModelPermissions, DjangoObjectPermissions, IsAdminUser, AllowAny
from serializers import UserSerializer, DenunciaSerializer
from backend.models import Denuncia
from forms import DenunciaForm
from extras import validateNumber, vcard

# Create your views here.

# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class DenunciaViewSet(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticatedOrReadOnly] 
	queryset 			= Denuncia.objects.all()
	serializer_class 	= DenunciaSerializer
	filter_fields 		= ('id','tipo','numero','check')

class ListaViewSet(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticatedOrReadOnly] 
	queryset 			= Denuncia.objects.all()
	serializer_class 	= DenunciaSerializer

	def list(self, request):
		queryset = Denuncia.objects.all()
		serializer = DenunciaSerializer(queryset, many=True)
		return Response(serializer.data)

def home(request):

	if request.method == 'POST':
		form = DenunciaForm(request.POST, request.FILES)
		if form.is_valid():
			print "Es valido"
			print form.cleaned_data
			#X =  Denuncia()
			x = form.cleaned_data
			form.save()
			return HttpResponseRedirect('/buscar/%s' % x['numero'])
			return HttpResponse("Agregado con exito! <a href='/'>Volver</a>")

	else:
		print "else"
		#print form
		form = DenunciaForm()
	return render(request, 'index.html', {'form': form})

	return HttpResponse("AAAAAAAAAAA")

def buscar(request,**kargs):
	query,msg="",""
	if 'numero' in kargs:
		numero = kargs['numero']
		validado = validateNumber(numero)
		query = Denuncia.objects.filter(numero=validado)
		vcard("",query)
		if query:
			for n in query:
				print n
			resp = query
		else:
			msg = u"No se encontró %s en la base de datos" % numero

		return render(request, 'buscar.html', {'numeros': query, 'msg':msg})
	else:
		return render(request, 'buscar.html', {'numeros': query, 'msg':msg})


def download(request):
	lista = Denuncia.objects.all()
	vc = str(vcard("Todos", lista))
	response = HttpResponse(vc, content_type='application/octet-stream')
	response['Content-Disposition'] = 'attachment; filename="LISTA_NEGRA.VCF"'
	return response

def denuncia(request):

	if request.method == 'POST':
		form = DenunciaForm(request.POST, request.FILES)
		if form.is_valid():
			print "Es valido"
			print form.cleaned_data
			#X =  Denuncia()
			x = form.cleaned_data
			form.save()
			return HttpResponseRedirect('/buscar/%s' % x['numero'])
			return HttpResponse("Agregado con exito! <a href='/'>Volver</a>")

	else:
		print "else"
		#print form
		form = DenunciaForm()
	return render(request, 'denuncia.html', {'form': form})