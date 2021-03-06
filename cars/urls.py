from django.urls import path

from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('car/<str:pk>/', views.car_overview, name='car-overview'),
    path('job/<str:pk>', views.job_details, name='job-details'),
    path('job_list/', views.job_list, name='job-list'),
    path('car_list/', views.car_list, name='car-list'),
    path('add_part_unit/', views.add_part_unit, name='add-part-unit'),
    path('remove_part_unit/', views.remove_part_unit, name='remove-part-unit'),
    path('request_part/', views.request_part, name='request-part'),
    path('message_list/', views.message_list, name='message-list'),
    path('message_read/', views.mark_message_as_read, name='message-read'),
    path('send_message/', views.send_message, name='send-message'),
    path('assign_message_to_job/', views.assign_message_to_job, name='assign-message-to-job'),
    path('generate_invoice/<str:pk>', views.generate_invoice, name='generate-invoice'),
    path('invoice_pdf/<str:pk>', views.invoice_pdf, name='invoice-pdf'),
    path('invoice_details/<str:pk>', views.invoice_details, name='invoice-details'),
    path('invoice_list/', views.invoice_list, name='invoice-list'),
    path('receipt/<str:pk>', views.receipt_pdf, name='receipt-pdf'),
    path('report-issue', views.report_issue, name='report-issue'),
]