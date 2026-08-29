from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from .models import Municipios, Paises, Estados, TipoINE, LugarNacimientoCURP
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.db.models import Q
from .forms import MunicipiosForm, EstadosForm
import json
from django.core.serializers import serialize

# Municipios
class MunicipiosList(LoginRequiredMixin, ListView):
    paginate_by = 10
    model = Municipios
    template_name = 'Generales/MunicipiosList.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        qsearch = self.request.GET.get('txtSearch')
        queryset = Municipios.objects.all().order_by('id')
        if qsearch:
            queryset = queryset.filter(Q(municipio__icontains=qsearch) | Q(estado__estado__icontains=qsearch))
        return queryset


class MunicipiosAdd(LoginRequiredMixin, CreateView):
    model = Municipios
    form_class = MunicipiosForm
    template_name = 'Generales/MunicipiosAdd.html'
    success_url = '/Generales/Municipios'


class MunicipiosEdit(LoginRequiredMixin, UpdateView):
    model = Municipios
    form_class = MunicipiosForm
    pk_url_kwarg = 'pk'
    template_name = 'Generales/MunicipiosEdit.html'
    success_url = '/Generales/Municipios'


class MunicipiosDelete(LoginRequiredMixin, DeleteView):
    model = Municipios
    template_name = 'Generales/MunicipiosDelete.html'
    success_url = '/Generales/Municipios'

#Estados


class EstadosList(LoginRequiredMixin, ListView):
    paginate_by = 10
    model = Estados
    template_name = 'Generales/EstadosList.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        qsearch = self.request.GET.get('txtSearch')
        queryset = Estados.objects.all().order_by('id')
        if qsearch:
            queryset = queryset.filter(Q(estado__icontains=qsearch) | Q(pais__pais__icontains=qsearch))
        return queryset


class EstadosEdit(LoginRequiredMixin, UpdateView):
    paginate_by = 10
    form_class = EstadosForm
    model = Estados
    template_name = 'Generales/EstadosEdit.html'
    context_object_name = 'object_list'
    success_url = '/Generales/Estados'


class EstadosAdd(LoginRequiredMixin, CreateView):
    model = Estados
    form_class = EstadosForm
    template_name = 'Generales/EstadosAdd.html'
    success_url = '/Generales/Estados'


class EstadosDelete(LoginRequiredMixin, DeleteView):
    model = Estados
    template_name = 'Generales/EstadosDelete.html'
    success_url = '/Generales/Estados'
    


@login_required
def apiTipoINE(request):
    tine = TipoINE.objects.all()
    data = [{'pk': item.pk, 'tipo': item.tipo} for item in tine]
    return JsonResponse(data, safe=False)



@login_required
def apiLugarNacimiento(request):
    obj = LugarNacimientoCURP.objects.all()
    data = [{'pk': item.id, 'lugar': item.lugarnacimiento, 'clave':item.clave} for item in obj]
    return JsonResponse(data, safe=False)


