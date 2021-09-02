from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from .models import Part, PartsOrder, PartsOrderUnit
from .forms import PartForm

# Create your views here.
@login_required
def parts_admin(request):
    role = request.session['role']
    if role != 'Manager':
        return redirect('cars:home')
    parts = Part.objects.all().order_by('name')
    part_form = PartForm()
    context = {
        'role': role,
        'parts': parts,
        'part_form': part_form,
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

def add_part(request):
    part = PartForm(request.POST)
    part.save()
    return HttpResponseRedirect(reverse('parts:parts-admin'))

def edit_part(request):
    part = Part.objects.get(id=request.POST['part_id'])
    updated = PartForm(request.POST, instance=part)
    updated.save()
    return HttpResponseRedirect(reverse('parts:parts-admin'))

def add_part_to_order(request):
    error = None
    quantity = 0
    cost = 0.0
    try:
        quantity = int(request.POST['quantity'])
    except:
        error = 'Quantity must be a whole number.'
    if quantity < 0:
        error = 'Quantity must be a positive number.'
    try:
        cost = float(request.POST['part_cost'])
    except:
        error = 'There is an issue with the cost of this item. Please try again.'
    if error:
        messages.warning(request, error)
    else:
        if quantity == 0:
            try:
                request.session['parts_order'].pop(request.POST['part_id'])
            except KeyError:
                messages.warning(request, 'Quantity must be greater than zero')
        else:
            request.session['parts_order'][request.POST['part_id']] = {
            'name': request.POST['part_name'],
            'quantity': quantity,
            'cost': cost,
        }
        # this line necessary because you have only modified a session variable
        # rather than request.session itself so changes wouldn't save
        request.session.modified = True
    return HttpResponseRedirect(reverse('parts:parts-admin'))

def update_part_in_order(request):
    try:
        request.session['parts_order'][request.POST['part_id']]['quantity'] = request.POST['quantity']
        request.session.modified = True
    except:
        messages.warning(request, 'An error has occurred. Please retry.')
    return HttpResponseRedirect(request.headers['Referer'])

def remove_part_from_order(request):
    try:
        request.session['parts_order'].pop(request.POST['part_id'])
        request.session.modified = True
    except KeyError:
        messages.warning(request, 'An error has occurred. Please retry.')
    return HttpResponseRedirect(request.headers['Referer'])

def order_parts(request):
    if request.method == 'POST':
        order = PartsOrder()
        order.save()
        for partUnit in request.session['parts_order']:
            error = None
            quantity = 0
            try:
                quantity = int(request.session['parts_order'][partUnit]['quantity'])
            except:
                error = 'Quantity must be a whole number.'
            if quantity < 0:
                error = 'Quantity must be a positive number.'
            if error:
                messages.warning(request, error)
                HttpResponseRedirect(request.headers['Referer'])
            else:
                part = Part.objects.get(id=int(partUnit))
                partUnit = PartsOrderUnit(order=order, part=part, quantity=quantity)
                partUnit.save()
        order.save()
        order.editable = False
        order.save()
        request.session['parts_order'] = {}
        return HttpResponseRedirect(reverse('parts:parts-admin'))
    return render(request, 'parts/parts_order.html')

class PartsOrderList(generic.ListView):
    model = PartsOrder

class PartsOrderDetail(generic.DetailView):
    model = PartsOrder

def check_in_parts_order_unit(request):
    print(request.POST)
    error = None
    try:
        parts_order_unit = PartsOrderUnit.objects.get(id=request.POST['parts_order_unit'])
    except:
        error = 'An error has occured'
    if error is not None:
        messages.warning(request, error)
    else:
        part = parts_order_unit.part
        part.stock_level = F('stock_level') + parts_order_unit.quantity
        parts_order_unit.checked_in = True
        part.save()
        part.refresh_from_db()
        parts_order_unit.save()
    return HttpResponseRedirect(request.headers['Referer'])