from django.urls import path

from . import views

app_name = 'parts'

urlpatterns = [
    path('parts_admin/', views.parts_admin, name='parts-admin'),
    path('part_details/<str:pk>', views.part_details, name='part-details'),
    path('add_part/', views.add_part, name='add-part'),
    path('edit_part/', views.edit_part, name='edit-part'),
    path('add_part_to_order/', views.add_part_to_order, name='add-part-to-order'),
    path('order_parts/', views.order_parts, name='order-parts'),
    path('remove_part_from_order/', views.remove_part_from_order, name='remove-part-from-order'),
    path('update_part_in_order/', views.update_part_in_order, name='update-part-in-order'),
    path('partsorder_list/', views.PartsOrderList.as_view(), name='parts-order-list'),
    path('partsorder_detail/<str:pk>', views.PartsOrderDetail.as_view(), name='parts-order-detail'),
    path('part_request_list/', views.part_request_list, name='part-request-list'),
    path('delete_part_request/', views.delete_part_request, name='delete-part-request'),
    path('check_in_parts_order_unit/', views.check_in_parts_order_unit, name='check-in-parts-order-unit'),
    ]