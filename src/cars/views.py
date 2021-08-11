from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Car, Job, PartUnit, LabourUnit
from parts.models import Part
from .forms import JobForm, LabourUnitForm, PartUnitForm
from datetime import timedelta
from django.utils import timezone

# Create your views here.

def home(request):
    print(request.user)
    print('authenticated:')
    print(request.user.is_authenticated)
    print(request.user.groups.first())
    print(request.user.groups.filter(name = 'Customer').exists())
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    #print(request.user.first_name)
    return render(request, 'cars/home.html', {'role': role})

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
        return redirect('cars:car-list')
    elif role == 'Manager':
        job_form = JobForm(initial={'car': car, 'manager': request.user})

    context = {
        'car': car,
        'role': role,
        'job_form': job_form,
        'jobs': jobs,
    }
    return render(request, 'cars/car_overview.html', context)

def car_list(request):
    if request.user.groups.filter(name = 'Customer').exists():
        cars = Car.objects.filter(owner = request.user.customer)
    else:
        cars = Car.objects.all()
    context = {
        'cars': cars,
    }
    return render(request, 'cars/car_list.html', context)

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
        if request.POST['unit'] == 'labour':
            form = LabourUnitForm(request.POST)
        elif request.POST['unit'] == 'part':
            error = None
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
            else:
                print('success')
                #form = PartUnitForm(request.POST)
        ##form.save()
        #job.save()
        return HttpResponseRedirect(reverse('cars:job-details', args=(job.id,)))
    context = {
        'job': job,
        'role': role,
        'time_spent': time_spent,
        'time_form': time_form,
        'part_form': part_form,
    }
    return render(request, 'cars/job_details.html', context)