from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Personas
from django.db.models import Q
from .forms import PersonasForms
from django.http import JsonResponse
from django.core.serializers import serialize


def es_administrador(user):
    return user.groups.filter(name='administrador').exists()


class PersonasDelUsuarioMixin(LoginRequiredMixin):
    """Restringe el queryset a las personas del usuario logueado.

    El grupo 'administrador' ve todo, igual que en Investigaciones.ListaInvestigaciones.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        if es_administrador(self.request.user):
            return queryset
        return queryset.filter(usuario=self.request.user)


class PersonaFList(PersonasDelUsuarioMixin, ListView):
    paginate_by = 10
    model = Personas
    context_object_name = 'object_list'
    template_name = 'Personas/PersonasList.html'

    def get_queryset(self):
        # Filtrar por el campo 'tipo' igual a 'PF' (Persona Física)
        queryset = super().get_queryset()
        queryset = queryset.filter(tipo='PF')
        qsearch = self.request.GET.get('txtSearch')

        if qsearch:
            queryset = queryset.filter(Q(nombre__icontains=qsearch) | Q(apellido1__icontains=qsearch))

        return queryset


class PersonasEdit(PersonasDelUsuarioMixin, UpdateView):
    model = Personas
    form_class = PersonasForms
    pk_url_kwarg = 'pk'
    template_name = 'Personas/PersonasEdit.html'
    success_url = '/Personas/PersonasPF'


class PersonasDelete(PersonasDelUsuarioMixin, DeleteView):
    model = Personas
    template_name = 'Personas/PersonasDelete.html'
    success_url = '/Personas/PersonasPF'


class PersonasAdd(LoginRequiredMixin, CreateView):
    model = Personas
    form_class = PersonasForms
    template_name = 'Personas/PersonasAdd.html'
    success_url = '/Personas/PersonasPF'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


@login_required
def getByIDJSON(request, id):
    # Solo se puede consultar una persona propia; el grupo 'administrador' consulta cualquiera.
    if es_administrador(request.user):
        mi_objeto = get_object_or_404(Personas, id=id)
    else:
        mi_objeto = get_object_or_404(Personas, id=id, usuario=request.user)

    # Convierte el objeto a JSON utilizando serialize
    json_data = serialize('json', [mi_objeto])

    # Retorna la respuesta JSON
    return JsonResponse(json_data, safe=False)
