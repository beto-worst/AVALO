from django.db import models
from Generales.models import Municipios


class SustentoLegal(models.Model):
    tipos = (('LF','LEY FEDERAL'),
             ('LE','LEY ESTATAL'),
             ('LM','LEY MUNICIPAL'),
             ('NOE','NORMATIVA ESTATAL'),
             ('NMU','NORMATIVA MUNICIPAL'),
             ('OT','OTROS'),
             ('SE','SIN ESPECIFICAR'),
             ('NA','NO APLICA'))
    tipo = models.CharField(max_length=4, unique=True, blank=False, null=False, default='NA', choices=tipos, verbose_name='Tipo')
    nombre = models.CharField(max_length=250, unique=True, blank=False, null=False,
                              help_text='Nombre de la normativa o ley que aplica', verbose_name='Nombre')
    articulo = models.CharField(max_length=300, blank=True, null=True, help_text='Articulo al que hace referencia', verbose_name='Articulo')
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, verbose_name='Municipio')
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in SustentoLegal._meta.fields]

    def __str__(self):
        return "{} [{}]".format(self.nombre, self.municipio)


class Usodesuelo(models.Model):
    uso = models.CharField(max_length=200, blank=False, null=False, help_text='Uso de suelo')
    sustento = models.ForeignKey(SustentoLegal, on_delete=models.DO_NOTHING)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} [{}]".format(self.uso,  self.sustento.municipio)
