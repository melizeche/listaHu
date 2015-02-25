# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.models import User, Group
from django.core.servers.basehttp import FileWrapper
from django.db.models import Count
from rest_framework import viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, DjangoModelPermissions, DjangoObjectPermissions, IsAdminUser, AllowAny
from serializers import UserSerializer, DenunciaSerializer, ListaSerializer
from backend.models import Denuncia, Estadistica, Tipo
from forms import DenunciaForm
from extras import validateNumber, vcard, vcard2, getCSV
import time
# Create your views here.

# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class DenunciaViewSet(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticatedOrReadOnly] 
	queryset 			= Denuncia.objects.all().order_by('-added')
	serializer_class 	= DenunciaSerializer
	filter_fields 		= ('id','tipo','numero','check')

class ListaViewSet(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticatedOrReadOnly] 
	queryset 			= Denuncia.objects.all()
	serializer_class 	= ListaSerializer
	filter_fields 		= ('id','tipo','numero','check')

	def list(self, request):
		queryset = Denuncia.objects.all()
		serializer = DenunciaSerializer(queryset, many=True)
		return Response(serializer.data)

def home(request):
	fail=""
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
			fail='fail'

	else:
		print "else"
		#print form
		form = DenunciaForm()
	try:
		cant = Estadistica.objects.get(nombre='denuncias').valor
	except Estadistica.DoesNotExist:
		cant = ""

	return render(request, 'index.html', {'form': form,'denuncias':cant, 'fail':fail})

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



def download(request, **kwargs):
	print kwargs
	if 'formato' in kwargs:
		formato = kwargs['formato']
		lista = Denuncia.objects.all()
		if formato=='csv':
			archi = getCSV(lista)
			response = HttpResponse(archi,content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="LISTA_HU_%s.csv"' % (time.strftime("%Y-%m-%d",time.localtime()))
			return response
		elif formato=='vcard':
			lista = Denuncia.objects.all().distinct('numero')
			vc = str(vcard("Todos", lista))
			response = HttpResponse(vc, content_type='text/vcard')
			response['Content-Disposition'] = 'attachment; filename="LISTA_HU_%s.VCF"' % (time.strftime("%Y-%m-%d",time.localtime()))
			return response
		elif formato=='vcard/repetidos':
			lista = Denuncia.objects.values('numero').annotate(the_count=Count('numero')).order_by('-the_count').filter(the_count__gte=2)
			vc = str(vcard("Todos", lista))
			response = HttpResponse(vc, content_type='text/vcard')
			response['Content-Disposition'] = 'attachment; filename="LISTA_HU_REP_%s.VCF"' % (time.strftime("%Y-%m-%d",time.localtime()))
			return response
		elif formato=='vcard/nospam':
			lista =  Denuncia.objects.all().distinct('numero').exclude(tipo=Tipo.objects.get(titulo='SPAM').id)
			vc = str(vcard("Todos", lista))
			response = HttpResponse(vc, content_type='text/vcard')
			response['Content-Disposition'] = 'attachment; filename="LISTA_HU_NOSPAM_%s.VCF"' % (time.strftime("%Y-%m-%d",time.localtime()))
			return response


	return render(request, 'descargar.html', {'msg':'msg'})
	return HttpResponse("<h2>Descargar:</h2><a href='vcard'>vCard</a><br><a href='csv'>CSV</a>")

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

def navegar(request):
	return render(request, 'navegar.html',{'msg':"Navegá la lista"})
def topDenuncias(request):
	query = Denuncia.objects.values('numero').annotate(count=Count('numero')).order_by('-count')[:50]

	return render(request, 'top.html',{'numeros':query})
