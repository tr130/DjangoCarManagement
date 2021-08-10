from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Car, Job, PartUnit, LabourUnit
from .forms import JobForm

# Create your views here.

def home(request):
    print(dir(request.user))
    print('authenticated:')
    print(request.user.is_authenticated)
    print(request.user.groups.first())
    print(request.user.groups.filter(name = 'Customer').exists())
    role = request.user.groups.first().name
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
    role = request.user.groups.first().name
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
    role = request.user.groups.first().name
    context = {
        'job': job,
        'role': role,
    }
    return render(request, 'cars/job_details.html', context)