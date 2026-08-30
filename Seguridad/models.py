from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


@receiver(post_save, sender=User)
def crear_configuracion_usuario(sender, instance, created, **kwargs):
    """Todo usuario nuevo necesita su fila de configuracion.

    Las vistas de Investigaciones hacen ConfiguracionUsuariosLB.objects.get(...)
    sin manejar DoesNotExist, asi que un usuario sin esta fila recibe un error
    500 al intentar iniciar una investigacion. Antes se creaba a mano desde el
    admin y era facil olvidarlo.
    """
    if created:
        ConfiguracionUsuariosLB.objects.get_or_create(usuario=instance)