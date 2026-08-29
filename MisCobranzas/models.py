from django.db import models
from django.contrib.auth.models import User
from Personas.models import Personas
from Generales.models import Folios
from django.utils.translation import gettext_lazy as _
import re


# Create your models here.
class FrequencyChoice(models.TextChoices):
    DAILY = 'daily', _("Diario")
    WEEKLY = 'weekly', _("Semanal")
    MONTHLY = 'monthly', _("Mensual")
    BIANUAL = 'biannual', _("Semestral")


class NotificationChoice(models.TextChoices):
    WAP = 'whatsapp', _("WhatsApp")
    SMS = 'sms', _("SMS")
    MAI = 'mail', _("Mail")
    CAL = 'llamar', _("Llamar")


class CobranzasMessages(models.Model):
    Broker = models.ForeignKey(User, on_delete=models.CASCADE)
    Client = models.ForeignKey(Personas, on_delete=models.CASCADE)
    Notification = models.CharField(max_length=10, choices=NotificationChoice.choices)
    Frequency = models.CharField(max_length=10, choices=FrequencyChoice.choices)
    folio = models.CharField(max_length=20, null=True, blank=True)
    email_subject = models.CharField(max_length=100, default='Recordatorio de pago')
    body = models.TextField(max_length=1500)
    status = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.Broker} {self.Client} {self.Notification} {self.Frequency} {self.status} {self.delivered} {self.created} {self.updated}'


class CobranzasPlantillas(models.Model):
    Broker = models.ForeignKey(User, on_delete=models.CASCADE)
    Notification = models.CharField(max_length=10, choices=NotificationChoice.choices)
    Frequency = models.CharField(max_length=10, choices=FrequencyChoice.choices)
    name_subject = models.CharField(max_length=100)
    body = models.TextField(max_length=1500)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'ID: {self.pk} -  Nombre: {self.name_subject} - Actualizada: {self.updated}'


def client_list(user_id):
    """get a list of Personas by user_id (broker)"""
    return Personas.objects.filter(usuario_id=user_id).all()


def collection_templates(user_id, template_id=1):
    """get a list of Personas by user_id"""
    return CobranzasPlantillas.objects.filter(Broker=user_id, pk=template_id)


def client(id):
    """get a Personas by id"""
    return Personas.objects.filter(id=id).get()


def collection_lst(user_id):
    """get a list of CobranzasMessages by user_id"""""
    return CobranzasMessages.objects.filter(Broker=user_id).all().order_by('-created')


def get_phone(id):
    """get a Personas telefono_principal as a sting by id"""
    pf_object = Personas.objects.filter(id=id).values_list('telefono_principal', flat=True).get()
    if pf_object is None:
        return None
    digits = re.findall(r"\d", str(pf_object.base_number))  # returns a list of digits
    if digits[0] == '1':
        digits = digits[1:]
    return "".join(digits)


def get_folios(user_id, person_id):
    """get a list of Folios by broker_id and person_id"""
    return Folios.objects.filter(usuario=user_id, persona=person_id).all()