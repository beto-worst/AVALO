from django.db import models
from Personas.models import Personas as Personasm
from Generales.models import Estados, Municipios, Colonia
from Normativas.models import Usodesuelo


class TipoInmueble(models.Model):
    tipo = models.CharField(max_length=150, unique=True, blank=False, null=False)
    descripcion = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)


class Inmueble(models.Model):
    tipo_inmueble = models.ForeignKey(TipoInmueble, on_delete=models.DO_NOTHING)
    duenio = models.ForeignKey(Personasm, on_delete=models.DO_NOTHING)
    calle = models.CharField(max_length=150, blank=False, null=False, default='Calle : ')
    cruzamiento1 = models.CharField(max_length=150, null=True, blank=True, default='Cruzamiento :')
    cruzamiento2 = models.CharField(max_length=155, null=True, blank=True, default='Cruzamiento 2:')
    num_interior = models.CharField(max_length=20, null=True, blank=True)
    num_exterior = models.CharField(max_length=20, null=True, blank=True)
    colonia = models.ForeignKey(Colonia, on_delete=models.DO_NOTHING, default=None)
    uso = models.ForeignKey(Usodesuelo, on_delete=models.DO_NOTHING)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    def nombreduenio(self):
        return "{}-{} {} {}".format(self.duenio.rfc, self.duenio.apellido1, self.duenio.apellido2, self.duenio.nombre)

    def direccioncompleta(self):
        return "Calle {}  X {}  y {}  Num. Int:{} Num.Ext{} {}" \
            .format(self.calle, self.cruzamiento1, self.cruzamiento2, self.num_interior, self.num_exterior
                    , self.colonia)

    def __str__(self):
        return "{} {} {}".format(self.tipo_inmueble.tipo, self.duenio.rfc, self.colonia)


class FotosInmuebles(models.Model):
    inmueble_id = models.ForeignKey(Inmueble, on_delete=models.DO_NOTHING)
    foto = models.ImageField(upload_to='Inmuebles/fotos')
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)
