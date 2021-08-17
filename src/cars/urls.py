from django.urls import path

from . import views

app_name = 'cars'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('job/<str:pk>', views.job_details, name='job-details'),
    path('invoice/<str:pk>', views.invoice, name='job-invoice'),
    path('<str:pk>/', views.car_overview, name='car-overview'),
]