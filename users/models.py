from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    auth_code = models.CharField(max_length=4, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(
        max_length=6, unique=True, blank=True, null=True)
    activated_invite_code = models.CharField(
        max_length=6, blank=True, null=True)
    referred_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.phone_number
