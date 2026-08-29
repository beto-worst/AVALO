from django.apps import AppConfig
#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from django.contrib.auth.models import User
#from Seguridad.models import ConfiguracionUsuariosLB

#@receiver(post_save, sender=User)
#def usuario_creado_handler(sender, instance, created, **kwargs):
#    if created:
#        # Código para ejecutar cuando se crea un usuario
#        user_id = instance.id
#        config = ConfiguracionUsuariosLB()
#        conf pass



class InvestigacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Investigaciones'


