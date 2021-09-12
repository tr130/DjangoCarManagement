from django.contrib import admin
from .models import Car, Job, PartUnit, LabourUnit, Invoice, PartRequest

# Register your models here.
admin.site.register(Car)
admin.site.register(Job)
admin.site.register(PartUnit)
admin.site.register(LabourUnit)
admin.site.register(Invoice)
admin.site.register(PartRequest)
