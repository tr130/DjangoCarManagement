from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from .forms import JobForm, LabourUnitForm, MessageForm, PartUnitForm, Message
from .models import Car, Job, PartUnit, Invoice
from parts.models import Part
from accounts.models import Manager

from datetime import timedelta
from itertools import chain
from xhtml2pdf import pisa

# Create your views here.

def get_unpaid_invoices(request):
    return Invoice.objects.filter(job__car__owner__user=request.user, job__paid=False).count()

def home(request):
    context = {}
    context['role'] = request.session['role']
    context['unread'] = Message.objects.filter(recipient = request.user, unread = True).count()
    if context['role'] == 'Customer':
        context['unpaid'] = get_unpaid_invoices(request)
    return render(request, 'cars/home.html', context)

@login_required
def job_list(request):
    role = request.session['role']
    if role == 'Employee':
        jobs = request.user.employee.assigned_job.filter(complete=False).order_by('expected_complete')
    elif role == 'Manager':
        jobs = Job.objects.all().order_by('expected_complete')
    else:
        return redirect('cars:home')
    unread = Message.objects.filter(recipient = request.user, unread = True).count()
    current_time = timezone.now()
    context = {
        'jobs': jobs,
        'current_time': current_time,
        'role': role,
        'unread': unread,
    }
    return render(request, 'cars/job_list.html', context)

@login_required
def car_list(request):
    context = {}
    context['role'] = request.session['role']
    context['unread'] = Message.objects.filter(recipient = request.user, unread = True).count()
    if context['role'] == 'Customer':
        context['cars'] = request.user.customer.car_set.all()
        context['unpaid'] = get_unpaid_invoices(request)
    elif context['role'] == 'Manager':
        context['cars'] = Car.objects.all()
    else:
        return redirect('cars:home')
    return render(request, 'cars/car_list.html', context)

@login_required
def car_overview(request, pk):
    if request.method == 'POST':
        if request.POST['form_type'] == 'job':
            job_form = JobForm(request.POST)
            job_form.save()
        return HttpResponseRedirect(reverse('cars:car-overview', args=(pk,)))
    context = {}
    car = get_object_or_404(Car, id=pk)
    context['car'] = car
    context['jobs'] = car.job_set.all()
    context['role'] = request.session['role']
    context['unread'] = Message.objects.filter(recipient = request.user, unread = True).count()
    if context['role'] == 'Customer':
        context['message_form'] = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': Manager.objects.get(id=1).user})
        if request.user != car.owner.user:
            return redirect('cars:home')
        context['unpaid'] = get_unpaid_invoices(request)
    elif context['role'] == 'Manager':
        context['job_form'] = JobForm(initial={'car': car, 'manager': request.user})
        context['message_form'] = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': car.owner.user})
    elif context['role'] == 'Employee':
        context['message_form'] = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': car.owner.user})
    context['messages'] = car.message_set.all().order_by('-created')

    return render(request, 'cars/car_overview.html', context)

@login_required
def job_details(request, pk):
    job = get_object_or_404(Job, id=pk)
    if job.invoiced:
        return redirect('cars:invoice-details', job.id)
    unread = Message.objects.filter(recipient = request.user, unread = True).count()
    time_form = None
    part_form = None
    time_spent = timedelta(hours= 0, minutes=0)
    unpaid = 0
    for labour_unit in job.labourunit_set.all():
        time_spent += labour_unit.time_spent
    role = request.session['role']
    if role == 'Customer':
        if request.user != job.car.owner.user:
            return redirect('cars:home')
        cars = request.user.customer.car_set.all()
        for car in cars:
            unpaid += car.job_set.filter(complete=True, paid=False).count()
        message_form = MessageForm(initial={
            'subject': job.title,
            'car': job.car, 
            'sender': request.user, 
            'job': job, 
            'recipient': Manager.objects.get(id=1).user,
            })

    if role == 'Employee' or role == 'Manager':
        time_form = LabourUnitForm(initial={'employee': request.user.employee.id, 'job': job})
        part_form = PartUnitForm(initial={'added_by': request.user.employee.id, 'job': job})
        message_form = MessageForm(initial={
            'subject': job.title,
            'car': job.car, 
            'sender': request.user, 
            'job': job, 
            'recipient': job.car.owner.user,
            })
    
    if request.method == 'POST':
        if request.POST['unit'] == 'labour':
            form = LabourUnitForm(request.POST)
            form.save()
            job.in_progress = True
            job.save()
        elif request.POST['unit'] == 'complete':
            job.complete = not job.complete
            job.in_progress = not job.complete
            job.save()
        
        return HttpResponseRedirect(reverse('cars:job-details', args=(job.id,)))
    current_time = timezone.now()
    message_list = job.message_set.all().order_by('-created')
    context = {
        'job': job,
        'role': role,
        'current_time': current_time,
        'time_spent': time_spent,
        'time_form': time_form,
        'part_form': part_form,
        'message_form': message_form,
        'message_list': message_list,
        'unpaid': unpaid,
        'unread': unread,
    }
    return render(request, 'cars/job_details.html', context)

def add_part_unit(request):
    error = None
    quantity = 0
    try:
        job = Job.objects.get(id=request.POST['job'])
    except:
        error = 'An error has occured'
    try:
        part = Part.objects.get(id=request.POST['part'])
    except:
        error = 'Invalid part'
    else:
        try:
            quantity = int(request.POST['quantity'])
        except:
            error = 'Invalid quantity'
        if quantity <= 0:
            error = 'Invalid quantity'
        elif quantity > part.stock_level:
            error = 'Insufficient stock'
    if error is not None:
        messages.warning(request, error)
    else:
        part.stock_level = F('stock_level') - quantity
        part.save()
        part.refresh_from_db()
        form = PartUnitForm(request.POST)
        form.save()
        job.in_progress = True
        job.save()
    try:
        return HttpResponseRedirect(request.headers['REFERER'])
    except:
        return redirect('cars:home')

def remove_part_unit(request):
    error = None
    try:
        part_unit = PartUnit.objects.get(id=request.POST['part_unit'])
    except:
        error = 'An error has occured'
    if error is None:
        part = part_unit.part
        job = part_unit.job
        part.stock_level = F('stock_level') + part_unit.quantity
        part_unit.delete()
        part.save()
        part.refresh_from_db()
        job.save()
    try:
        return HttpResponseRedirect(request.headers['REFERER'])
    except:
        return redirect('cars:home')

def generate_invoice(request, pk):
    job = get_object_or_404(Job, id=pk)
    invoice = Invoice(job=job)
    invoice.save()
    job.invoiced = True
    job.save()
    return redirect('cars:invoice-details', job.id)

@login_required
def invoice_pdf(request, pk):
    role = request.session['role']
    job = get_object_or_404(Job, id=pk)
    if not job.invoiced:
        return redirect('cars:job-details', pk)
    if role == 'Customer' and request.user != job.car.owner.user:
        return redirect('cars:home')
    invoice = Invoice.objects.get(job=job)
    context = {
        'role': role,
        'invoice': invoice,
    }

    template_path = 'cars/invoice.html'
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #if display
    response['Content-Disposition'] = 'filename="invoice.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error:
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

    #return render(request, 'cars/invoice.html', context)

@login_required
def invoice_details(request, pk):
    role = request.session['role']
    unread = Message.objects.filter(recipient = request.user, unread = True).count()
    invoice = get_object_or_404(Invoice, job__id=pk)
    unpaid = None
    # if not job.invoiced:
    #     return redirect('cars:job-details', pk)
    if role == 'Customer':
        if request.user != invoice.job.car.owner.user:
            return redirect('cars:home')
        cars = request.user.customer.car_set.all()
        unpaid = 0
        for car in cars:
            unpaid += car.job_set.filter(complete=True, paid=False).count()
        unpaid = unpaid

    if request.method == 'POST':
        invoice.job.paid = True
        invoice.job.save()
        return HttpResponseRedirect(reverse('cars:invoice-details', args=(invoice.job.id,)))

    context = {
        'role': role,
        'invoice': invoice,
        'unpaid': unpaid,
        'unread': unread,
    }
    return render(request, 'cars/invoice_details.html', context)

@login_required
def invoice_list(request):
    role = request.session['role']
    if role != 'Customer':
        return redirect('cars:home')
    cars = request.user.customer.car_set.all()
    unread = Message.objects.filter(recipient = request.user, unread = True).count()
    invoices = Invoice.objects.filter(job__car__owner__user = request.user)
    unpaid = get_unpaid_invoices(request)
    context = {
        'role': role,
        'invoices': invoices,
        'unpaid': unpaid,
        'unread': unread,
    }
    return render(request, 'cars/invoice_list.html', context)

@login_required
def receipt_pdf(request, pk):
    role = request.session['role']
    job = get_object_or_404(Job, id=pk)
    if not job.paid:
        return redirect('cars:job-details', pk)
    if role == 'Customer' and request.user != job.car.owner.user:
        return redirect('cars:home')
    invoice = Invoice.objects.get(job=job)
    context = {
        'role': role,
        'invoice': invoice,
    }
    

    template_path = 'cars/receipt.html'
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #if display
    response['Content-Disposition'] = 'filename="receipt.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error:
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def message_list(request):
    role = request.session['role']
    messages = request.user.message_sender.all().union(request.user.message_recipient.all()).order_by('-created')
    unread = Message.objects.filter(recipient = request.user, unread = True).count()
    context = {
        'role': role,
        'messages': messages,
        'unread': unread,
    }
    if role == 'Customer':
        context['unpaid'] = get_unpaid_invoices(request)
    return render(request, 'cars/messages.html', context)

@login_required
def send_message(request):
    message_form = MessageForm(request.POST)
    message_form.save()
    return HttpResponseRedirect(request.headers['Referer'])

@login_required
def mark_message_as_read(request):
    message = Message.objects.get(id=request.POST['message_id'])
    message.unread = False
    message.save()
    return HttpResponseRedirect(request.headers['Referer'])

@login_required
def assign_message_to_job(request):
    message = Message.objects.get(id=request.POST['message_id'])
    job = Job.objects.get(id=request.POST['job_id'])
    message.job = job
    message.save()
    return HttpResponseRedirect(request.headers['Referer'])