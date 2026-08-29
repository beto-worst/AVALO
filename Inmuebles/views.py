from django.shortcuts import render
from .models import Inmueble, FotosInmuebles
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q


@login_required
def index(request):
    qsearch = request.GET.get('txtSearch')
    objects_list = Inmueble.objects.all().order_by('id', 'duenio')
    if qsearch:
        objects_list = objects_list.filter(Q(duenio__nombre__icontains=qsearch) | Q(duenio__rfc__icontains=qsearch))

    paginator = Paginator(objects_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'Inmuebles/index.html', {'objects': page_obj})


@login_required
@require_POST
def imagenes_inmuebles(request):
    data = json.loads(request.body)
    id = data['id']
    imagenes = FotosInmuebles.objects.filter(inmueble_id=id).order_by('id')
    json_data = serialize('json', imagenes, fields=('foto',))
    return JsonResponse(json_data, safe=False)


@login_required
def add(request):
    return render(request, 'Inmuebles/add.html',{})
