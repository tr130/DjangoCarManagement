from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Part
from .forms import PartForm

# Create your views here.
@login_required
def parts_admin(request):
    if request.user.groups.first():
        role = request.user.groups.first().name
    else:
        role = None
    if role != 'Manager':
        return redirect('cars:home')
    parts = Part.objects.all().order_by('name')
    print(request.session['parts_order'])
    print(request.session['role'])
    context = {
        'role': role,
        'parts': parts,
    }
    return render(request, 'parts/parts_admin.html', context)

def part_details(request, pk):
    try:
        part = Part.objects.get(id=pk)
    except:
        return redirect('parts:parts-admin')
    part_form = PartForm(instance=part)
    context = {
        'part': part,
        'part_form': part_form,
    }
    return render(request, 'parts/part_details.html', context)

def edit_part(request):
    part = Part.objects.get(id=request.POST['part_id'])
    updated = PartForm(request.POST, instance=part)
    updated.save()
    return HttpResponseRedirect(reverse('parts:parts-admin'))

def add_part_to_order(request):
    print(request.POST)
    # part_to_order = {
    #     'part_id': request.POST['part_id'],
    #     'quantity': request.POST['quantity'],
    # }
    # for part in request.session['parts_order']:
    #     if part['part_id'] == part_to_order['part_id']:
    #         part['quantity'] += part_to_order['quantity']
    #     else:
    #         request.session['parts_order'].append(part_to_order)

    request.session['parts_order'][request.POST['part_id']] = {
        'name': request.POST['part_name'],
        'quantity': int(request.POST['quantity']),
        'cost': float(request.POST['part_cost']),
    }
    

    # this line necessary because you have only modified a session variable
    # rather than request.session itself so changes wouldn't save
    request.session.modified = True
    print(request.session['parts_order'])
    return HttpResponseRedirect(reverse('parts:parts-admin'))

def order_parts(request):
    return HttpResponseRedirect(reverse('parts:parts-admin'))