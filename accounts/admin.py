from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Employee, Customer, Manager

admin.site.register(User, UserAdmin)
admin.site.register(Employee)
admin.site.register(Customer)
admin.site.register(Manager)
