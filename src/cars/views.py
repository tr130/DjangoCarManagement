from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from .forms import JobForm, LabourUnitForm, PartUnitForm
from .models import Car, Job, PartUnit, LabourUnit
from parts.models import Part

from datetime import timedelta
from xhtml2pdf import pisa

# Create your views here.

def home(request):
    print(request.user)
    print('authenticated:')
    print(request.user.is_authenticated)
    print(request.user.groups.first())
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    if role == 'Employee':
        jobs = request.user.employee.assigned_job.all().order_by('expected_complete')
        current_time = timezone.now()
        context = {
            'current_time': current_time,
            'jobs': jobs,
        }
        return render(request, 'cars/job_list.html', context)
    elif role == 'Customer':
        cars = request.user.customer.car_set.all()
        context = {
            'cars': cars,
        }
        return render(request, 'cars/car_list.html', context)
    elif role == 'Manager':
        jobs = Job.objects.all().order_by('expected_complete')
        current_time = timezone.now()
        context = {
            'jobs': jobs,
            'current_time': current_time,
        }
        return render(request, 'cars/job_list.html', context)

@login_required
def car_overview(request, pk):
    if request.method == 'POST':
        job_form = JobForm(request.POST)
        job_form.save()
    car = get_object_or_404(Car, id=pk)
    jobs = car.job_set.all()
    for job in jobs:
        print(job)
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    job_form = None
    if role == 'Customer' and request.user != car.owner.user:
        return redirect('cars:home')
    elif role == 'Manager':
        job_form = JobForm(initial={'car': car, 'manager': request.user})

    context = {
        'car': car,
        'role': role,
        'job_form': job_form,
        'jobs': jobs,
    }
    return render(request, 'cars/car_overview.html', context)

@login_required
def job_details(request, pk):
    job = get_object_or_404(Job, id=pk)
    time_form = None
    part_form = None
    time_spent = timedelta(hours= 0, minutes=0)
    for labour_unit in job.labourunit_set.all():
        time_spent += labour_unit.time_spent
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    if role == 'Employee':
        time_form = LabourUnitForm(initial={'employee': request.user.employee.id, 'job': job})
        part_form = PartUnitForm(initial={'added_by': request.user.employee.id, 'job': job})
    if request.method == 'POST':
        error = None
        if request.POST['unit'] == 'labour':
            form = LabourUnitForm(request.POST)
            form.save()
            job.in_progress = True
            job.save()
        elif request.POST['unit'] == 'part':
            quantity = 0
            print(request.POST)
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
                print(error)
                messages.warning(request, error)
            else:
                print('success')
                part.stock_level = F('stock_level') - quantity
                part.save()
                part.refresh_from_db()
                form = PartUnitForm(request.POST)
                form.save()
                job.in_progress = True
                job.save()
        elif request.POST['unit'] == 'complete':
            job.complete = not job.complete
            job.in_progress = False
            job.save()
        return HttpResponseRedirect(reverse('cars:job-details', args=(job.id,)))
    current_time = timezone.now()
    context = {
        'job': job,
        'role': role,
        'current_time': current_time,
        'time_spent': time_spent,
        'time_form': time_form,
        'part_form': part_form,
    }

    return render(request, 'cars/job_details.html', context)

@login_required
def invoice(request, pk):
    job = get_object_or_404(Job, id=pk)
    if not job.complete:
        return redirect('cars:job-details', pk)
    time_spent = timedelta(hours= 0, minutes=0)
    labour_cost = 0.0
    parts_cost = 0.0
    for labour_unit in job.labourunit_set.all():
        time_spent += labour_unit.time_spent
        labour_cost += labour_unit.get_cost()
    for part_unit in job.partunit_set.all():
        parts_cost += float(part_unit.get_cost())
    grand_total = labour_cost + parts_cost
    context = {
        'job': job,
        'time_spent': time_spent,
        'labour_cost': labour_cost,
        'parts_cost': parts_cost,
        'grand_total': grand_total,
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