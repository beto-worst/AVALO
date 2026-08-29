from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Products(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    stripe_price_id = models.CharField(max_length=500)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=500)
    notes = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class UserPaymentHistory(models.Model):
    user_payment_id = models.ForeignKey(UserPayment, on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)
    plan = models.CharField(max_length=100, null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.user_payment_id.user.username


# class UserAccount(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     balance = models.FloatField(default=0)
    # date = models.DateTimeField(auto_now_add=True)
    # stripe_charge_id = models.CharField(max_length=50)
