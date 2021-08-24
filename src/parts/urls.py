from django.urls import path

from . import views

app_name = 'parts'

urlpatterns = [
    path('parts_admin/', views.parts_admin, name='parts-admin'),
    path('part_details/<str:pk>', views.part_details, name='part-details'),
    path('edit_part/', views.edit_part, name='edit-part'),
    ]