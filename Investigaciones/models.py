from django.db import models
from datetime import timedelta
from django.utils import timezone
from Personas.models import Personas
from django.contrib.auth.models import User


# Create your models here.
class Investigacion(models.Model):
    nombre_archivo = models.TextField(default=None)
    folio = models.IntegerField(unique=True, null=True)
    investigado = models.ForeignKey(Personas, on_delete=models.DO_NOTHING)
    burojson = models.TextField(default='')
    satblacklistjson = models.TextField(default='')
    antecedentesjson = models.TextField(default='')
    estudiosprofesionalesjson = models.TextField(default='')
    listanegraintl = models.TextField(default='')
    creado_en = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    notas = models.TextField(max_length=350, blank=True, null=True)
    modificado_en = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        get_latest_by = 'creado_en'
    
    

    def vencida(self):
         one_month_ago = timezone.now() - timedelta(days=30)
         return self.creado_en <  one_month_ago
    def __str__(self):
        return "{} Folio: {}/{}".format(self.id, self.folio, self.investigado.rfc)


class InvestigacionPremium(models.Model):
    principal = models.ForeignKey('Investigacion', on_delete=models.DO_NOTHING, related_name='investigacion_principal')
    conyugue = models.ForeignKey('Investigacion',null=True, blank=True, on_delete=models.DO_NOTHING, related_name='conyugue_investigacion')
    padre_principal = models.ForeignKey('Investigacion', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='padre_investigacion')
    madre_principal = models.ForeignKey('Investigacion', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='madre_investigacion')
    padre_conyugue = models.ForeignKey('Investigacion', null=True,  blank=True,on_delete=models.DO_NOTHING, related_name='padre_conyugue_investigacion')
    madre_conyugue = models.ForeignKey('Investigacion',null=True, blank=True,on_delete=models.DO_NOTHING, related_name='madre_conyugue_investigacion')
    aval = models.ForeignKey('Investigacion',  blank=True, null=True, on_delete=models.DO_NOTHING, related_name='aval_investigacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    #val empresarial
    nombre = models.CharField(max_length=300, blank=True , null=True)
    rfc = models.CharField(max_length=18, blank=True , null=True)
    telefono =models.CharField(max_length=10, blank=True , null=True)
    notas_valemp = models.CharField(max_length=300, blank=True , null=True)
    #val emrpesarial
    #val laboral
    es_empleado = models.CharField(max_length=10, blank=True , null=True)
    trabaja_ahi = models.CharField(max_length=10, blank=True , null=True)
    puesto = models.CharField(max_length=300, blank=True , null=True)
    antiguedad = models.CharField(max_length=100, blank=True , null=True)
    salario = models.CharField(max_length=100, blank=True , null=True)
    desempenio = models.CharField(max_length=300, blank=True , null=True)
    #val laboral
    creado_en = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    modificado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {}".format(self.principal.investigado.rfc, self.principal.investigado)
    


class validacionEmpresarial(models.Model):
    investigacion_premium = models.ForeignKey('InvestigacionPremium',null=True, blank=True, on_delete=models.DO_NOTHING)
    nombre = models.TextField(max_length=350, blank=True, null=True)
    razonsocial = models.TextField(max_length=350, blank=True, null=True)

class Referencias(models.Model):
    investigacion_premium = models.ForeignKey('InvestigacionPremium',null=True, blank=True, on_delete=models.DO_NOTHING)
    nombre = models.TextField(max_length=350, blank=True, null=True)
    parentesco = models.TextField(max_length=350, blank=True, null=True)
    telefono = models.TextField(max_length=10, blank=True, null=True)
    notas = models.TextField(max_length=350, blank=True, null=True)