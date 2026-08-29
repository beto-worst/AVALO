from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from Personas.models import Personas


class TiposDocumento(models.Model):
    clave = models.CharField(max_length=10, unique=True, blank=False, null=False, help_text='Una clave que identifique'
                                                                                            ' al documento')
    nombre = models.CharField(max_length=150, unique=True, blank=False, null=False, help_text='Nombre del coumento')
    descripcion = models.TextField(max_length=300, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'TiposDocumentos'
        verbose_name='Tipos de Documento'

    def __str__(self):
        return "{}/{}".format(self.clave, self.nombre)


class FormatosDocumento(models.Model):
    tipo = models.ForeignKey(TiposDocumento, on_delete=models.DO_NOTHING)
    clave = models.CharField(max_length=10, unique=True, blank=False, null=False)
    nombre = models.CharField(max_length=150, unique=True, blank=False, null=False)
    version = models.CharField(max_length=100, blank=False,
                               null=False, default='1', help_text='Versión del Documento: Ej:1.0.0 , 1.0, A1, etc.')
    contenido = RichTextField()
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}-{}/[{}] Ver:{}".format(self.clave, self.nombre, self.tipo.nombre, self.version)


class Archivos(models.Model):
    tipo = models.ForeignKey(TiposDocumento, on_delete=models.DO_NOTHING)
    persona = models.ForeignKey(Personas, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    uuid_archivo = models.TextField(blank=False, null=False)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}/{}/{}".format(self.tipo, self.usuario, self.uuid_archivo)