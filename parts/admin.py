from django.contrib import admin

from .models import Part
# Register your models here.

class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost_price', 'customer_price']

admin.site.register(Part, PartAdmin)