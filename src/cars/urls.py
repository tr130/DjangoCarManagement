from django.urls import path

from . import views

app_name = 'cars'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('car_list/', views.car_list, name='car-list'),
    path('<str:pk>/', views.car_overview, name='car-overview'),
]