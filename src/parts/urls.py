from django.urls import path

from . import views

app_name = 'parts'

urlpatterns = [
    path('parts_admin/', views.parts_admin, name='parts-admin'),
    path('part_details/<str:pk>', views.part_details, name='part-details'),
    path('edit_part/', views.edit_part, name='edit-part'),
    path('add_part_to_order/', views.add_part_to_order, name='add-part-to-order'),
    path('order_parts/', views.order_parts, name='order-parts'),
    ]