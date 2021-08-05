from django.db import models
from parts.models import Part
from accounts.models import User, Employee, Customer, Manager

# Create your models here.
class Car(models.Model):
    model_name = models.CharField(max_length=200)
    year = models.IntegerField()
    reg = models.CharField(max_length=10)
    owner = models.ForeignKey(Customer, on_delete=models.PROTECT)
    notes = models.TextField()

class Job(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='assigned_job')
    manager = models.ForeignKey(Manager, on_delete=models.PROTECT, related_name='supervised_job')
    complete = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expected_complete = models.DateTimeField(blank=True)

class PartUnit(models.Model):
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

class LabourUnit(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    consumables = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

