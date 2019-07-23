from os import path
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Count
from rest_framework import viewsets, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly,
                                        DjangoModelPermissions, DjangoObjectPermissions, IsAdminUser, AllowAny)
from .serializers import DenunciaSerializer, ListaSerializer, ListaUnicaSerializer
from backend.models import Denuncia, Estadistica, Tipo
from backend.filters import DenunciaFilter
from .forms import DenunciaForm
from .extras import validateNumber, vcard, getCSV


class DenunciaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Denuncia.objects.filter(activo=True).order_by('-added')
    serializer_class = DenunciaSerializer
    filter_class = DenunciaFilter


class ListaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Denuncia.objects.filter(activo=True)
    serializer_class = ListaSerializer
    filter_class = DenunciaFilter

    def list(self, request):
        query = DenunciaFilter(
            request.GET, queryset=Denuncia.objects.filter(activo=True))
        serializer = DenunciaSerializer(query.qs, many=True)
        return Response(serializer.data)


class ListaUnicaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Denuncia.objects.filter(activo=True)
    serializer_class = ListaUnicaSerializer
    filter_class = DenunciaFilter

    def list(self, request):
        raw_queryset = Denuncia.objects.raw(
            'select * from (select distinct on (numero) * from backend_denuncia)' \
            ' distinct_num  order by distinct_num.added')
        ids = [denuncia.id for denuncia in raw_queryset]
        queryset = Denuncia.objects.filter(id__in=ids)
        query = DenunciaFilter(
            request.GET, queryset=queryset)
        serializer = DenunciaSerializer(query.qs, many=True)
        return Response(serializer.data)


def home(request):
    fail = ""
    if request.method == 'POST':
        form = DenunciaForm(request.POST, request.FILES)
        if form.is_valid():
            x = form.cleaned_data
            form.save()
            messages.success(request, "Se agregó correctamente!")
            return HttpResponseRedirect('/buscar/%s' % x['numero'])
        else:
            fail = 'fail'

    else:
        form = DenunciaForm()
    try:
        cant = Estadistica.objects.get(nombre='denuncias').valor
    except Estadistica.DoesNotExist:
        cant = ""

    return render(request, 'index.html', {'form': form, 'denuncias': cant, 'fail': fail})


def buscar(request, **kargs):
    query, msg, withthumbs = "", "", ""
    if 'numero' in kargs:
        numero = kargs['numero']
        validado = validateNumber(numero)
        query = Denuncia.objects.filter(numero=validado, activo=True)
        vcard("", query)
        if query:
            msg = validado
            withthumbs = []
            for denuncia in query:
                withthumbs.append((denuncia, "%s_th%s" % (path.splitext(str(denuncia.screenshot))[0],
                                                          path.splitext(str(denuncia.screenshot))[1])))
        else:
            msg = "No se encontró %s en la base de datos" % numero

    return render(request, 'buscar.html', {'msg': msg, 'withthumbs': withthumbs})


def download(request, **kwargs):
    if 'formato' in kwargs:
        formato = kwargs['formato']
        lista = Denuncia.objects.filter(activo=True)
        # CSV
        if formato == 'csv':
            archi = getCSV(lista)
            response = HttpResponse(archi, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="LISTA_HU_%s.csv"' % (
                time.strftime("%Y-%m-%d", time.localtime()))
            return response
        # vCard all
        elif formato == 'vcard':
            lista = Denuncia.objects.filter(activo=True).distinct('numero')
            vc = str(vcard("Todos", lista))
            response = HttpResponse(vc, content_type='text/vcard')
            response['Content-Disposition'] = 'attachment; filename="LISTA_HU_%s.VCF"' % (
                time.strftime("%Y-%m-%d", time.localtime()))
            return response
        # vCard with more than 1 denuncia
        elif formato == 'vcard/repetidos':
            lista = Denuncia.objects.values('numero').annotate(
                the_count=Count('numero')).order_by('-the_count').filter(the_count__gte=2)
            vc = str(vcard("Todos", lista))
            response = HttpResponse(vc, content_type='text/vcard')
            response['Content-Disposition'] = 'attachment; filename="LISTA_HU_REP_%s.VCF"' % (
                time.strftime("%Y-%m-%d", time.localtime()))
            return response
        # vCard just estafa y extorsión
        elif formato == 'vcard/nospam':
            lista = Denuncia.objects.filter(activo=True).distinct('numero').exclude(
                tipo=Tipo.objects.get(titulo='SPAM').id)
            vc = str(vcard("Todos", lista))
            response = HttpResponse(vc, content_type='text/vcard')
            response['Content-Disposition'] = 'attachment; filename="LISTA_HU_NOSPAM_%s.VCF"' % (
                time.strftime("%Y-%m-%d", time.localtime()))
            return response

    return render(request, 'descargar.html', {'msg': 'msg'})


def denuncia(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST, request.FILES)
        if form.is_valid():
            x = form.cleaned_data
            form.save()
            return HttpResponseRedirect('/buscar/%s' % x['numero'])

    else:
        form = DenunciaForm()
    return render(request, 'denuncia.html', {'form': form})


def navegar(request):
    return render(request, 'navegar.html', {'msg': "Navegá la lista"})


def topDenuncias(request):
    query = Denuncia.objects.filter(activo=True).values('numero').annotate(
        count=Count('numero')).order_by('-count')[:50]
    return render(request, 'top.html', {'numeros': query})
