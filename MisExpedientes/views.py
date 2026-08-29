from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# from django.http import HttpResponse
from django.urls import reverse
from .forms import ExpeditensForm
from .models import lista_categorias, Expedientes_disponibles, borrar_expediente, client_list, Expedientes, CategoriaExpedientes
from django.http import JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder



@login_required(login_url='login')
def getCategorias(request):
    try:
        categorias_objs = CategoriaExpedientes.objects.all()
    except CategoriaExpedientes.DoesNotExist:
        # Manejar el caso en que no existan categorías
        return JsonResponse({'error': 'No existen categorías'}, status=404)

    # Convertir los objetos a una lista de diccionarios o serializarlos según tus necesidades
    categorias_data = [{'id': cat.id, 'nombre': cat.nombre} for cat in categorias_objs]

    # Opción 1: Retornar la lista de diccionarios como JSON usando JsonResponse
    return JsonResponse(categorias_data, safe=False)


@login_required(login_url='login')
def getCategoriaByID(request, categoria):
    try:
        categoria_obj = CategoriaExpedientes.objects.get(id=categoria)
    except CategoriaExpedientes.DoesNotExist:
        # Manejar el caso en que la categoría no existe
        return JsonResponse({'error': 'La categoría no existe'}, status=404)

    # Convertir el objeto a un diccionario o serializarlo según tus necesidades
    categoria_data = {
        'id': categoria_obj.id,
        'nombre': categoria_obj.nombre,
        # Agrega más campos según tu modelo
    }

    # Opción 1: Retornar el diccionario como JSON usando JsonResponse
    return JsonResponse(categoria_data)


@login_required(login_url='login')
def getInfoAPI(request, persona):
     print('API Persona ', request.user.id)
     # Realizar la consulta y obtener los valores
     queryset = Expedientes.objects.filter(usuario_id=request.user.id, cliente_id=persona).values_list('id', 'usuario_id', 'cliente_id', 'expediente_categoria_id', 'expediente_nombre').order_by('-cliente_id')
     obj  = Expedientes.objects.filter(usuario_id=request.user.id, cliente_id=persona)
     print('el objeto', obj)
     expedientes_list = list(queryset)

    # Devolver la respuesta como JSON usando JsonResponse y el serializador DjangoJSONEncoder
     return JsonResponse({'expedientes': expedientes_list}, encoder=DjangoJSONEncoder, safe=False)

@login_required(login_url='login')
def index(request, cliente_id=None, page=None, err=None):

    lista_de_clentes = client_list(request.user.id).order_by('-id')

    if cliente_id:
        cliente = Expedientes_disponibles(request.user.id, cliente_id)
    else:
        cliente = Expedientes_disponibles(request.user.id, None)
    #es_administrador = request.user.groups.filter(name='administrador').exists()
    #if es_administrador:
    #    print('modo admin en expedientes')
    #    cliente = Expedientes_disponibles(None, cliente_id)

# ------ modify 'lista_categoria' to include 'found' value

    updated_categorias = []
    for c in lista_categorias():
        found = False
        for cl in cliente:
            if c[0] == cl[3]:
                updated_categorias.append((c[0], c[1], 1))
                found = True
        if not found:
            updated_categorias.append((c[0], c[1], 0))

# ------ modify 'lista_de_clientes' to include 'found' value

    def extention_filter(filename):
        ext = filename.split('.')[-1]
        return ext

    updated_cliente = []
    for a, b, c, d, e in cliente:
        extention = extention_filter(e)
        updated_cliente.append((a, b, c, d, e, extention))
    cliente = updated_cliente

    paginator = Paginator(lista_de_clentes, 15)
    page_number = request.GET.get("page", page)
    page = paginator.get_page(page_number)

    context = {'page': page,
               'paginator': paginator,
               'cliente_id': cliente_id,
               'cliente': cliente,
               'lista_categorias': updated_categorias,
               'error': err
               }

    return render(request, 'MisExpedientes/index.html', context)


@login_required(login_url='login')
def up_load(request):
    if request.method == 'POST':
        form = ExpeditensForm(request.POST, request.FILES)
        c_id = request.POST.get('cliente_id', '/')
        p = request.POST.get('page', '/')
        if form.is_valid():
            form.save()
            return redirect(reverse('MisExpedientes:index', kwargs={'cliente_id': c_id, 'page': p}))
        else:
            err = 1
            return redirect(reverse('MisExpedientes:index', kwargs={'cliente_id': c_id, 'page': p, 'err': err}))


@login_required(login_url='login')
def delete_document(request, cliente_id=None, doc_id=None, page=None):
    if request.method == 'GET':
        if borrar_expediente(doc_id) is True:
            return redirect(reverse('MisExpedientes:index', kwargs={'cliente_id': cliente_id, 'page': page}))
        else:
            err = 2
            return redirect(reverse('MisExpedientes:index', kwargs={'cliente_id': cliente_id, 'page': page, 'err': err}))