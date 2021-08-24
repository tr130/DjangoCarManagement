from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from .forms import JobForm, LabourUnitForm, MessageForm, PartUnitForm, Message
from .models import Car, Job, PartUnit
from parts.models import Part
from accounts.models import Manager

from datetime import timedelta
from itertools import chain
from xhtml2pdf import pisa

# Create your views here.

def home(request):
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None

    return render(request, 'cars/home.html', {'role':role,})

@login_required
def job_list(request):
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    if role == 'Employee':
        jobs = request.user.employee.assigned_job.filter(complete=False).order_by('expected_complete')
        current_time = timezone.now()
        context = {
            'current_time': current_time,
            'jobs': jobs,
            'role': role,
        }
    elif role == 'Customer':
        return redirect('cars:home')
    elif role == 'Manager':
        jobs = Job.objects.all().order_by('expected_complete')
        current_time = timezone.now()
        context = {
            'jobs': jobs,
            'current_time': current_time,
            'role': role,
        }
    return render(request, 'cars/job_list.html', context)

@login_required
def car_list(request):
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    if role == 'Customer':
        cars = request.user.customer.car_set.all()
        unpaid = 0
        for car in cars:
            unpaid += car.job_set.filter(complete=True, paid=False).count()
        context = {
            'cars': cars,
            'role': role,
            'unpaid': unpaid,
        }
    elif role == 'Manager':
        cars = Car.objects.all()
        context = {
            'cars': cars,
            'role': role,
        }
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
    unpaid = 0
    car = get_object_or_404(Car, id=pk)
    jobs = car.job_set.all()
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    job_form = None
    if role == 'Customer':
        message_form = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': Manager.objects.get(id=1).user})
        if request.user != car.owner.user:
            return redirect('cars:home')
        cars = request.user.customer.car_set.all()
        for vehicle in cars:
            unpaid += vehicle.job_set.filter(complete=True, paid=False).count()
    elif role == 'Manager':
        job_form = JobForm(initial={'car': car, 'manager': request.user})
        message_form = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': car.owner.user})
    elif role == 'Employee':
        message_form = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': car.owner.user})
    messages = car.message_set.all().order_by('-created')

    context = {
        'car': car,
        'role': role,
        'job_form': job_form,
        'message_form': message_form,
        'jobs': jobs,
        'unpaid': unpaid,
        'messages': messages,
    }
    return render(request, 'cars/car_overview.html', context)

@login_required
def job_details(request, pk):
    job = get_object_or_404(Job, id=pk)
    if job.paid:
        return redirect('cars:invoice-details', job.id)
    time_form = None
    part_form = None
    time_spent = timedelta(hours= 0, minutes=0)
    unpaid = 0
    for labour_unit in job.labourunit_set.all():
        time_spent += labour_unit.time_spent
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    if role == 'Customer':
        if request.user != job.car.owner.user:
            return redirect('cars:home')
        cars = request.user.customer.car_set.all()
        for car in cars:
            unpaid += car.job_set.filter(complete=True, paid=False).count()
        message_form = MessageForm(initial={
            'car': job.car, 
            'sender': request.user, 
            'job': job, 
            'recipient': Manager.objects.get(id=1).user,
            })

    if role == 'Employee' or role == 'Manager':
        time_form = LabourUnitForm(initial={'employee': request.user.employee.id, 'job': job})
        part_form = PartUnitForm(initial={'added_by': request.user.employee.id, 'job': job})
        message_form = MessageForm(initial={
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
    print(request.POST)
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
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    time_spent = timedelta(hours= 0, minutes=0)
    labour_cost = 0.0
    parts_cost = 0.0
    for labour_unit in job.labourunit_set.all():
        time_spent += labour_unit.time_spent
        labour_cost += labour_unit.get_cost()
    for part_unit in job.partunit_set.all():
        parts_cost += float(part_unit.get_cost())
    sub_total = labour_cost + parts_cost
    grand_total = sub_total * 1.2
    context = {
        'job': job,
        'time_spent': time_spent,
        'labour_cost': labour_cost,
        'parts_cost': parts_cost,
        'sub_total': sub_total,
        'grand_total': grand_total,
        'role': role,
    }
    return context

@login_required
def invoice_pdf(request, pk):
    job = get_object_or_404(Job, id=pk)
    if not job.complete:
        return redirect('cars:job-details', pk)
    context = generate_invoice(request, pk)
    if context['role'] == 'Customer' and request.user != job.car.owner.user:
        return redirect('cars:home')
    

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
    job = get_object_or_404(Job, id=pk)
    if not job.complete:
        return redirect('cars:job-details', pk)
    context = generate_invoice(request, pk)
    if context['role'] == 'Customer':
        if request.user != job.car.owner.user:
            return redirect('cars:home')
        cars = request.user.customer.car_set.all()
        unpaid = 0
        for car in cars:
            unpaid += car.job_set.filter(complete=True, paid=False).count()
        context['unpaid'] = unpaid

    if request.method == 'POST':
        job.paid = True
        job.save()
        return HttpResponseRedirect(reverse('cars:invoice-details', args=(job.id,)))
    return render(request, 'cars/invoice_details.html', context)

@login_required
def invoice_list(request, pk):
    if request.user.customer.id != int(pk):
        return redirect('cars:home')
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    cars = request.user.customer.car_set.all()
    invoices = []
    unpaid = 0
    for car in cars:
        invoices.append(car.job_set.filter(complete=True))
        unpaid += car.job_set.filter(complete=True, paid=False).count()
    # combine the separate querysets in the invoices list
    invoices = list(chain(*invoices))
    context = {
        'role': role,
        'invoices': invoices,
        'unpaid': unpaid,
    }
    return render(request, 'cars/invoice_list.html', context)

@login_required
def receipt_pdf(request, pk):
    job = get_object_or_404(Job, id=pk)
    if not job.paid:
        return redirect('cars:job-details', pk)
    context = generate_invoice(request, pk)
    if context['role'] == 'Customer' and request.user != job.car.owner.user:
        return redirect('cars:home')
    

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
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    messages = request.user.message_sender.all().union(request.user.message_recipient.all()).order_by('-created')
    context = {
        'role': role,
        'messages': messages,
    }
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