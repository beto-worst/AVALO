from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.db.models import Q
from .models import SustentoLegal, Usodesuelo
from .forms import SustentoLegalForm, UsodeSueloForm


class SustentoList(LoginRequiredMixin, ListView):
    model = SustentoLegal
    paginate_by = 10
    template_name = 'Normativas/list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        qsearch = self.request.GET.get('txtSearch')
        queryset = SustentoLegal.objects.all().order_by('id')
        if qsearch:
            queryset = queryset.filter(Q(municipio__municipio__icontains=qsearch)
                                       | Q(municipio__estado__estado=qsearch) | Q(nombre__icontains=qsearch))
        return queryset


class SustentoDelete(LoginRequiredMixin, DeleteView):
    model = SustentoLegal
    template_name = 'Normativas/SustentoDelete.html'
    success_url = '/Normativas/SustentoLegal'
    context_object_name = 'obj'


class SustentoEdit(LoginRequiredMixin, UpdateView):
    model = SustentoLegal
    form_class = SustentoLegalForm
    pk_url_kwarg = 'pk'
    template_name = 'Normativas/SustentoEdit.html'
    success_url = '/Normativas/SustentoLegal'


class SustentoCreate(LoginRequiredMixin, CreateView):
    model = SustentoLegal
    form_class = SustentoLegalForm
    template_name = 'Normativas/SustentoCreate.html'
    success_url = '/Normativas/SustentoLegal'


class UsodesueloList(LoginRequiredMixin, ListView):
    model = Usodesuelo
    paginate_by = 10
    template_name = 'Normativas/UsoSueloList.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        qsearch = self.request.GET.get('txtSearch')
        queryset = Usodesuelo.objects.all().order_by('id')
        if qsearch:
            queryset = queryset.filter(Q(sustento__usodesuelo__uso__icontains=qsearch)
                                       | Q(uso__icontains=qsearch) | Q(
                sustento__municipio__municipio__icontains=qsearch))
        return queryset


class UsosueloDelete(LoginRequiredMixin, DeleteView):
    model = Usodesuelo
    template_name = 'Normativas/UsoSueloDelete.html'
    success_url = '/Normativas/Usodesuelo'
    context_object_name = 'obj'


class UsosueloCreate(LoginRequiredMixin, CreateView):
    model = Usodesuelo
    form_class = UsodeSueloForm
    template_name = 'Normativas/UsoSueloCreate.html'
    success_url = '/Normativas/Usodesuelo'


class UsosueloEdit(LoginRequiredMixin, UpdateView):
    model = Usodesuelo
    form_class = UsodeSueloForm
    pk_url_kwarg = 'pk'
    template_name = 'Normativas/UsoSueloCreate.html'
    success_url = '/Normativas/Usodesuelo'