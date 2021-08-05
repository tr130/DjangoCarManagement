from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"