from django.db import models


# Create your models here.
class LugarNacimientoCURP(models.Model):
    clave = models.CharField(max_length=3, unique=True, blank=False)
    lugarnacimiento = models.CharField(max_length=100, unique=True, blank=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lugar de Nacimiento (CURP)"
        verbose_name_plural = "Lugares de Nacimiento (CURP)"

    def __str__(self):
        return "{}/{}".format(self.clave, self.lugarnacimiento)


class Paises(models.Model):
    clave = models.CharField(max_length=100, unique=True, blank=False)
    pais = models.CharField(max_length=150, unique=True, blank=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paises"
        verbose_name_plural = "Paises"

    def __str__(self):
        return "{}-{}".format(self.clave, self.pais)


class Estados(models.Model):
    clave = models.CharField(max_length=100, unique=True, blank=False)
    estado = models.CharField(max_length=100, unique=True, blank=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    pais = models.ForeignKey(Paises, on_delete=models.DO_NOTHING)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estados"
        verbose_name_plural = "Estados"

    def __str__(self):
        return "{}/{}/{}".format(self.clave, self.estado, self.pais.clave)


class Municipios(models.Model):
    clave = models.CharField(max_length=200, unique=True, blank=False)
    municipio = models.CharField(max_length=200, unique=True, blank=False)
    estado = models.ForeignKey(Estados, on_delete=models.DO_NOTHING)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Municipios"
        verbose_name_plural = "Municipios"

    def __str__(self):
        return "{}{}/{}".format(self.clave, self.municipio, self.estado)


class Colonia(models.Model):
    colonia = models.CharField(max_length=250, unique=True, blank=False)
    codigo_postal = models.CharField(max_length=10, blank=False, null=False)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "Colonia"
        verbose_name_plural = "Colonias"

    def __str__(self):
        return "[{}]{}/{}".format(self.codigo_postal, self.colonia, self.municipio)


class Bancos(models.Model):
    nombrecorto = models.CharField(max_length=30, unique=True, blank=False)
    nombrecomercial = models.CharField(max_length=300)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}-[{}]".format(self.nombrecorto, self.nombrecomercial)

    class Meta:
        verbose_name = "Bancos"
        verbose_name_plural = "Bancos"


class Nacionalidades(models.Model):
    clave = models.CharField(max_length=3, unique=True, blank=False)
    nacionalidad = models.CharField(max_length=100, unique=True, blank=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nacionalidades"
        verbose_name_plural = "Nacionalidades"

    def __str__(self):
        return "{}/{}".format(self.clave, self.nacionalidad)


class OcupacionesGPrincipal(models.Model):
    clave = models.IntegerField(null=False, blank=False, unique=True,
                                help_text='Clasificación de ocupaciones según CMO')
    grupoprincipal = models.CharField(max_length=150, null=False, blank=False, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "OcupacionesGPrincipalCMO"
        verbose_name_plural = "OcupacionesGPrincipalCMO"

    def __str__(self):
        return "{}/{}".format(self.clave, self.grupoprincipal)


class EstadosCiviles(models.Model):
        estado = models.CharField(null=False, blank=False, unique=True, max_length=50)
        creado_en = models.DateTimeField(auto_now_add=True)
        modificado_en = models.DateTimeField(auto_now=True)

        def __str__(self):
            return  "{}".format(self.estado)

        class Meta:
            verbose_name = "Estados Civiles"
            verbose_name_plural = "EstadosCiviles"


class TipoINE(models.Model):
    tipo = models.CharField(max_length=2, blank=False, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tipo

class TipInmobiliario(models.Model):
    tip = models.TextField(null=False, blank = False)
    fecha_publicacion = models.DateField()
    aprobado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} / {} ".format(self.id , self.fecha_publicacion)


class Folios(models.Model):
    # folio = models.IntegerField(null=True, blank=True)
    folio = models.CharField(max_length=20, null=True, blank=True)
    usuario = models.IntegerField(null=True, blank=True)
    persona = models.IntegerField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}, {}".format(self.id, self.folio)

    class Meta:
        verbose_name_plural='Folios'

    # def save(self, *args, **kwargs):
    #     # Si no se ha asignado un valor a 'folio', asigna el siguiente valor autoincremental
    #     if not self.folio:
    #         ultima_folio = Folios.objects.last()
    #         if ultima_folio:
    #             self.folio = ultima_folio.folio + 1
    #         else:
    #             self.folio = 1
    #     super().save(*args, **kwargs)