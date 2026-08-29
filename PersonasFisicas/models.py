import datetime

from django.db import models
import re
from django.core.exceptions import ValidationError
from django.utils import timezone
from phone_field import PhoneField
from Generales.models import LugarNacimientoCURP, Estados, Municipios, Colonia

def validar_rfc(value):
    """
    Función de validación personalizada para RFC.
    """
    patron_rfc = r'^[A-Z]{4}\d{6}[A-Z0-9]{3}$'
    if not re.match(patron_rfc, value):
        raise ValidationError('El RFC debe tener el formato adecuado.')


# Create your models here.
class PersonaFisica(models.Model):
    rfc = models.CharField(max_length=13, blank=False, null=False, unique=True, validators=[validar_rfc])
    curp = models.CharField(max_length=18, blank=False, null=False, unique=True)
    nombre = models.CharField(max_length=150, blank=False, default=' ')
    apellido1 = models.CharField(max_length=150, blank=True, default=' '),
    apellido2 = models.CharField(max_length=150, blank=True)
    fnacimiento = models.DateField(blank=False, null=False, default=datetime.datetime.now)
    lugarNacimiento = models.ForeignKey(LugarNacimientoCURP, on_delete=models.DO_NOTHING, default=None)
    telefono_principal = PhoneField(blank=False, help_text='Número de teléfono móvil o número principal', default=None)
    telefono_secundario = PhoneField(blank=True, help_text='Número de teléfono móvil o número principal', default=None)
    correo_electronico = models.EmailField(blank=False, unique=True, help_text='Correo eléctronico', default=None)
    calle = models.CharField(max_length=150, blank=False, null=False, default='Calle : ')
    cruzamiento1 = models.CharField(max_length=150, null=True, blank=True, default='Cruzamiento :')
    cruzamiento2 = models.CharField(max_length=150, null=True, blank=True, default='Cruzamiento 2:')
    estado = models.ForeignKey(Estados, on_delete=models.DO_NOTHING, default=None)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, default=None)
    colonia = models.ForeignKey(Colonia, on_delete=models.DO_NOTHING, default=None)
    creado_en = models.DateTimeField(auto_created=True, default=timezone.now)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PersonaFisica"
        verbose_name_plural = "PersonasFisicas"


