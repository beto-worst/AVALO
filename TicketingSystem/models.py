from django.db import models
from django.contrib.auth.models import User
from Personas.models import Personas

# Create your models here.


class TicketPriority(models.TextChoices):
    BAJA = 'Baja'
    MEDIA = 'Media'
    ALTA = 'Alta'


class TicketStatus(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.name

    def get_default_status(self):
        return TicketStatus.objects.get(pk=2)


class TicketCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.name


class TicketSubCategory(models.Model):
    category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    sub_name = models.CharField(max_length=100)
    sub_description = models.TextField()
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.category.name + ' - ' + self.sub_name


class Ticket(models.Model):
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='creator')
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(TicketCategory, null=True, blank=True, on_delete=models.CASCADE)
    status = models.ForeignKey(TicketStatus, null=True, blank=True, on_delete=models.CASCADE)
    priority = models.CharField(max_length=25, choices=TicketPriority.choices, default=TicketPriority.MEDIA)
    description = models.TextField()
    # viewed = models.BooleanField(default=False)
    # Polarity
    # Subjectivity
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.title


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    creator_comment = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.TextField()
    # viewed = models.BooleanField(default=False)
    # Polarity
    # Subjectivity
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return self.comment


def client_list(user_id):
    # get 15 clients sorted most recent first
    # raise TypeError("Cannot reorder a query once a slice has been taken.")
    # return Personas.objects.all().order_by('-created_at')[:15].values_list('id', 'nombre', 'apellido1', 'tipo')
    return Personas.objects.filter(usuario_id=user_id).values_list('id', 'nombre', 'apellido1', 'tipo')
