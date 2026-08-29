import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Personas.models import Personas
from Investigaciones.models import Investigacion
from Documentos.models import Archivos
from Generales.models import TipInmobiliario
from datetime import date
# Create your views here.
@login_required(login_url='login')
def index(request):
    today = date.today()
    tip = TipInmobiliario.objects.filter(fecha_publicacion__year=today.year, fecha_publicacion__month=today.month, fecha_publicacion__day=today.day).first()
    num_documentos = Archivos.objects.filter(usuario=request.user.id).count()
    num_investigaciones = Investigacion.objects.filter(usuario=request.user.id).count()
    ahorro_investigaciones = int(round((((num_investigaciones * 1440)) - (num_investigaciones * 5)) /60,0))
    ahorro_documentos = int(round((((num_documentos * 1440)) - (num_documentos * 150)) /60,0))
    top_vencimientos = Investigacion.objects.filter(usuario=request.user.id).order_by("-creado_en")[:5]
    return render(request, 'home.html', {'saludo': saludo_segun_hora(),'num_investigaciones':num_investigaciones,
                                         'num_documentos':num_documentos, 'top_vencidos':top_vencimientos,'tip':tip,
                                         'ahorro_investigaciones':ahorro_investigaciones, 'ahorro_documentos': ahorro_documentos})


def saludo_segun_hora():
    hora = datetime.datetime.now().hour
    if hora >= 6 and hora < 12:
        mensaje_saludo = "Buenos días"
    elif hora >= 12 and hora < 18:
        mensaje_saludo = "Buenas tardes"
    else:
        mensaje_saludo = "Buenas noches"
    return mensaje_saludo