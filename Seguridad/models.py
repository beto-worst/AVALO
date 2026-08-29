from django.db import models
from django.contrib.auth.models import User


class CustomUser(models.Model):
    nombre = models.CharField(max_length=50, null=False, blank=False)
    apellido1 = models.CharField(max_length=50,null=False, blank=False)
    apellido2 = models.CharField(max_length=50)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(upload_to='usuarios/profilepictures')
    modificado_en = models.DateTimeField(auto_now=True)



class ConfiguracionUsuariosLB(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    max_investigaciones = models.IntegerField(default=3)

    def __str__(self):
        return "{} {} {}".format(self.usuario.id, self.usuario.username,self.max_investigaciones)