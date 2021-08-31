from django.db import models
from parts.models import Part
from accounts.models import User, Employee, Customer, Manager
from datetime import timedelta, datetime

# Create your models here.
class Car(models.Model):
    model_name = models.CharField(max_length=200)
    year = models.IntegerField()
    reg = models.CharField(max_length=10)
    owner = models.ForeignKey(Customer, on_delete=models.PROTECT)
    notes = models.TextField()

    def __str__(self):
        return f"{self.year} {self.model_name} ({self.owner}; {self.reg})"

class Job(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='assigned_job')
    manager = models.ForeignKey(Manager, on_delete=models.PROTECT, related_name='supervised_job')
    in_progress = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    estimated_time = models.DurationField(default=timedelta())
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expected_complete = models.DateTimeField(blank=True)
    invoiced = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Invoice(models.Model):
    job = models.OneToOneField(Job, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    time_spent = models.DurationField(default=timedelta())
    labour_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self):
        self.time_spent = timedelta(hours= 0, minutes=0)
        for labour_unit in self.job.labourunit_set.all():
            self.time_spent += labour_unit.time_spent
            self.labour_cost += labour_unit.total_cost
        for part_unit in self.job.partunit_set.all():
            self.parts_cost += part_unit.total_cost
        self.sub_total = self.labour_cost + self.parts_cost
        self.vat = float(self.sub_total) * 0.2
        self.grand_total = float(self.sub_total) + self.vat
        self.job.invoiced = True
        return super().save()

    def __str__(self):
        return f"{self.job.title} - {self.job.car.reg}"

class PartUnit(models.Model):
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    cost_each = models.DecimalField(max_digits=10, decimal_places=2,)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    added_by = models.ForeignKey(Employee, on_delete=models.PROTECT)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def __str__(self):
        return f"{self.job.car.reg} - {self.part} x {self.quantity}"

    def save(self):
        self.cost_each = self.part.customer_price
        self.total_cost = self.cost_each * self.quantity
        return super().save()

class LabourUnit(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    description = models.TextField()
    time_spent = models.DurationField(default=timedelta())
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def __str__(self):
        return f"{self.job.car.reg} - {self.job} - {self.time_spent}"

    def save(self):
        self.hourly_rate = self.employee.hourly_rate
        self.total_cost = self.time_spent.seconds/3600 * float(self.hourly_rate)
        return super().save()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='message_sender')
    recipient = models.ForeignKey(User, on_delete=models.PROTECT, related_name='message_recipient')
    car = models.ForeignKey(Car, on_delete=models.PROTECT, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.PROTECT, null=True, blank=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    unread = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    # class Meta:
    #     ordering = ['-unread', '-created']

