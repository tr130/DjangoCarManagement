from django.contrib import admin
from .models import Car, Job, PartUnit, LabourUnit

# Register your models here.
admin.site.register(Car)
admin.site.register(Job)
admin.site.register(PartUnit)
admin.site.register(LabourUnit)