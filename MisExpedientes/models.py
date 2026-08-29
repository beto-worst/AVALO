import os
from django.db import models
from django.core.validators import FileExtensionValidator
from uuid import uuid4
from Personas.models import Personas


def file_par(instance, filename):
    upload_to = "mis_expedientes/"
    ext = filename.split('.')[-1]
    filename = f'{uuid4().hex}.{ext}'
    return os.path.join(upload_to, filename)


class CategoriaExpedientes(models.Model):
    nombre = models.CharField(max_length=50)
    estatus = models.BooleanField(default=True)

    def __str__(self) -> str:
        return "{}: {}".format(self.pk, self.nombre)


class Expedientes(models.Model):
    usuario_id = models.IntegerField(null=False)
    cliente_id = models.IntegerField(null=False)
    expediente_categoria_id = models.ForeignKey(CategoriaExpedientes, on_delete=models.DO_NOTHING)
    expediente_nombre = models.FileField(upload_to=file_par,
                                         validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'bmp'])])
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.pk)


def client_list(user_id):
    return Personas.objects.filter(usuario_id=user_id).values_list('id', 'nombre', 'apellido1', 'tipo')


def lista_categorias():
    return CategoriaExpedientes.objects.values_list('id', 'nombre')


def Expedientes_disponibles(uid, cid):
    return Expedientes.objects.filter(usuario_id=uid, cliente_id=cid).values_list('id', 'usuario_id', 'cliente_id', 'expediente_categoria_id', 'expediente_nombre').order_by('-cliente_id')


def nombre_expedinte(expediente_id):
    return Expedientes.objects.filter(id=expediente_id).values_list('expediente_nombre')


def borrar_expediente(expediente_id):
    doc_to_remove = Expedientes.objects.get(id=expediente_id)
    doc_to_remove.expediente_nombre.delete()
    doc_to_remove.delete()
    return True
