from django.db import models

# Create your models here.
class reponses(models.Model):
    data = models.TextField(default='')
    transaction_id = models.TextField(default='')
    curp = models.TextField(default='')
    creado_en = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return '{}'.format(self.data )