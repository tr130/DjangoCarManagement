from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from .forms import JobForm, LabourUnitForm, MessageForm, PartRequestForm, PartUnitForm, Message
from .models import Car, Job, PartUnit, Invoice, PartRequest
from parts.models import Part
from accounts.models import Manager

from datetime import timedelta
from itertools import chain
from xhtml2pdf import pisa

# Create your views here.

def home(request):
    return render(request, 'cars/home.html')

@login_required
def job_list(request):
    if request.session['role'] == 'Employee':
        jobs = request.user.employee.assigned_job.filter(complete=False).order_by('expected_complete')
    elif request.session['role'] == 'Manager':
        jobs = Job.objects.all().order_by('expected_complete')
    else:
        return redirect('cars:home')
    current_time = timezone.now()
    context = {
        'jobs': jobs,
        'current_time': current_time,
    }
    return render(request, 'cars/job_list.html', context)

@login_required
def car_list(request):
    if request.session['role'] == 'Customer':
        cars = request.user.customer.car_set.all()
    elif request.session['role'] == 'Manager':
        cars = Car.objects.all()
    else:
        return redirect('cars:home')
    return render(request, 'cars/car_list.html', {'cars': cars})

@login_required
def car_overview(request, pk):
    if request.method == 'POST':
        if request.POST['form_type'] == 'job':
            try:
                job_form = JobForm(request.POST)
                job_form.save()
            except:
                messages.warning(request, 'An error has occurred. Please try again.')
                return HttpResponseRedirect(request.headers['REFERER'])
        return HttpResponseRedirect(reverse('cars:car-overview', args=(pk,)))
    context = {}
    car = get_object_or_404(Car, id=pk)
    context['car'] = car
    context['jobs'] = car.job_set.all()
    if request.session['role'] == 'Customer':
        context['message_form'] = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': Manager.objects.get(id=1).user})
        if request.user != car.owner.user:
            return redirect('cars:home')
    elif request.session['role'] == 'Manager':
        context['job_form'] = JobForm(initial={'car': car, 'manager': request.user.manager})
        context['message_form'] = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': car.owner.user})
    elif request.session['role'] == 'Employee':
        context['message_form'] = MessageForm(initial={'car': car, 'sender': request.user, 'recipient': car.owner.user})
    context['message_list'] = car.message_set.all().order_by('-created')

    return render(request, 'cars/car_overview.html', context)

@login_required
def job_details(request, pk):
    job = get_object_or_404(Job, id=pk)
    if job.invoiced:
        return redirect('cars:invoice-details', job.id)
    time_form = None
    part_form = None
    part_request_form = None
    time_spent = timedelta(hours= 0, minutes=0)
    for labour_unit in job.labourunit_set.all():
        time_spent += labour_unit.time_spent
    if request.session['role'] == 'Customer':
        if request.user != job.car.owner.user:
            return redirect('cars:home')
        message_form = MessageForm(initial={
            'subject': job.title,
            'car': job.car, 
            'sender': request.user, 
            'job': job, 
            'recipient': Manager.objects.get(id=1).user,
            })

    if request.session['role'] == 'Employee' or request.session['role'] == 'Manager':
        time_form = LabourUnitForm(initial={'employee': request.user.employee.id, 'job': job})
        part_form = PartUnitForm(initial={'added_by': request.user.employee.id, 'job': job})
        part_request_form = PartRequestForm(initial={'requested_by': request.user, 'assigned_to': job.manager, 'job':job})
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
        'current_time': current_time,
        'time_spent': time_spent,
        'time_form': time_form,
        'part_form': part_form,
        'part_request_form': part_request_form,
        'message_form': message_form,
        'message_list': message_list,
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

def request_part(request):
    error = None
    quantity = 0
    if request.POST['job']:
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
    if error is not None:
        messages.warning(request, error)
    else:
        form = PartRequestForm(request.POST)
        form.save()
        job.in_progress = True
        job.save()
        if request.session['role'] == 'Manager':
            request.session['unactioned_part_requests'] = PartRequest.objects.filter(assigned_to = request.user.manager, on_order=False).count()
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
    job = get_object_or_404(Job, id=pk)
    if not job.invoiced:
        return redirect('cars:job-details', pk)
    if request.session['role'] == 'Customer' and request.user != job.car.owner.user:
        return redirect('cars:home')
    invoice = Invoice.objects.get(job=job)
    context = {
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
    invoice = get_object_or_404(Invoice, job__id=pk)
    if request.session['role'] == 'Customer':
        if request.user != invoice.job.car.owner.user:
            return redirect('cars:home')
    if request.method == 'POST':
        invoice.job.paid = True
        invoice.job.save()
        request.session['unpaid'] = Invoice.objects.filter(job__car__owner__user=request.user, job__paid=False).count()
        return HttpResponseRedirect(reverse('cars:invoice-details', args=(invoice.job.id,)))
    context = {
        'invoice': invoice,
    }
    return render(request, 'cars/invoice_details.html', context)

@login_required
def invoice_list(request):
    if request.session['role'] != 'Customer':
        return redirect('cars:home')
    invoices = Invoice.objects.filter(job__car__owner__user = request.user)
    context = {
        'invoices': invoices,
    }
    return render(request, 'cars/invoice_list.html', context)

@login_required
def receipt_pdf(request, pk):
    job = get_object_or_404(Job, id=pk)
    if not job.paid:
        return redirect('cars:job-details', pk)
    if request.session['role'] == 'Customer' and request.user != job.car.owner.user:
        return redirect('cars:home')
    invoice = Invoice.objects.get(job=job)
    context = {
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
    message_list = request.user.message_sender.all().union(request.user.message_recipient.all()).order_by('-created')
    context = {
        'message_list': message_list,
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
    request.session['unread'] = Message.objects.filter(recipient = request.user, unread = True).count()
    return HttpResponseRedirect(request.headers['Referer'])

@login_required
def assign_message_to_job(request):
    message = Message.objects.get(id=request.POST['message_id'])
    job = Job.objects.get(id=request.POST['job_id'])
    message.job = job
    message.save()
    return HttpResponseRedirect(request.headers['Referer'])

@login_required
def report_issue(request):
    issue = MessageForm(request.POST)
    try:
        issue.save()
    except:
        messages.warning(request, 'Unable to report the issue. Please contact the administrator directly.')
    return HttpResponseRedirect(request.headers['REFERER'])
    