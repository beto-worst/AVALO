from django.db import models
import re
from django.core.exceptions import ValidationError
from Generales.models import LugarNacimientoCURP, Estados, Municipios, Colonia, EstadosCiviles
from phone_field import PhoneField
import datetime
from django.contrib.auth.models import User

def validar_rfc(value):
    """
    Función de validación personalizada para RFC.
    """

    patron_rfc = r'^([A-Z]{3}|[A-Z]{4})\d{6}([A-Z0-9]{3}|[A-Z0-9]{2}\d{1})$'
    if not re.match(patron_rfc, value):
        raise ValidationError('El RFC debe tener el formato adecuado.')


class Personas(models.Model):
    tipos_persona = (('PF','PERSONA FISICA'),
                    ('PM','PERSONA MORAL'))
    rfc = models.CharField(max_length=13, blank=False, null=False, unique=False, validators=[validar_rfc])
    curp = models.CharField(max_length=18, blank=False, null=False, unique=False)
    razonsocial = models.CharField(max_length=300, blank=False, null=False, help_text='Nombre completo o Razón social')
    nombre = models.CharField(max_length=150, blank=False, default=' ')
    apellido1 = models.CharField(max_length=150, blank=True, default=' ')
    apellido2 = models.CharField(max_length=150, blank=True)
    estadocivil = models.ForeignKey(EstadosCiviles, on_delete=models.DO_NOTHING)
    fnacimiento = models.DateField(blank=False, null=False, default=datetime.datetime.now)
    lugarNacimiento = models.ForeignKey(LugarNacimientoCURP, on_delete=models.DO_NOTHING, default=None)
    telefono_principal = PhoneField(blank=False, help_text='Número de teléfono móvil o número principal', default=None)
    telefono_secundario = PhoneField(blank=True, help_text='Número de teléfono móvil o número principal', default=None)
    correo_electronico = models.EmailField(blank=False, help_text='Correo eléctronico', default='persona@legalbit.mx')
    calle = models.CharField(max_length=150, blank=False, null=False, default='Calle : ')
    cruzamiento1 = models.CharField(max_length=150, null=True, blank=True, default='Cruzamiento :')
    cruzamiento2 = models.CharField(max_length=150, null=True, blank=True, default='Cruzamiento 2:')
    numInterior = models.CharField(max_length=150, null=True, blank=True, default='..')
    numExterior = models.CharField(max_length=150, null=True, blank=True, default='')
    estado = models.ForeignKey(Estados, on_delete=models.DO_NOTHING, default=None)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, default=None)
    colonia = models.ForeignKey(Colonia, on_delete=models.DO_NOTHING, default=None)
    tipo = models.CharField(choices=tipos_persona, max_length=2)
    direccionine = models.TextField(default='')
    inejson = models.TextField(default='')
    inejson2 = models.TextField(default='')
    uuidnss = models.TextField(default='')
    uuidnss_sem = models.TextField(default='')
    inefront = models.ImageField(blank=True, upload_to='docs')
    inerevers = models.ImageField(blank=True, upload_to='docs')
    uuid_imss = models.TextField(default='')
    uuid_issste = models.TextField(default='')
    validaine= models.TextField(default='')
    manual = models.BooleanField(default=False)
    clave_elector = models.TextField(default='')
    cic_ine = models.TextField(default='')
    identificador_ine = models.TextField(default='')
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{} {}{}".format(self.id, self.curp, self.apellido1)

    def nombreCompleto(self):
        return "{} {} {}".format(self.apellido1, self.apellido2, self.nombre)

    class Meta:
        verbose_name = 'Personas'
        verbose_name_plural = 'Personas'
