from cars.models import PartRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import generic

from .forms import PartForm
from .models import Part, PartsOrder, PartsOrderUnit


# Create your views here.
@permission_required('parts.add_part')
def parts_admin(request):
    """Show all parts, ordered by name."""
    # if request.session['role'] != 'Manager':
    #     return redirect('cars:home')
    parts = Part.objects.all().order_by('name')
    part_form = PartForm()
    context = {
        'parts': parts,
        'part_form': part_form,
    }
    return render(request, 'parts/parts_admin.html', context)

@permission_required('parts.add_part')
def part_details(request, pk):
    """Display details of a part with option to edit."""
    if request.session['role'] != 'Manager':
        return redirect('cars:home')
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

@permission_required('parts.add_part')
def add_part(request):
    """Save PartForm received via request as a new Part instance."""
    part = PartForm(request.POST)
    part.save()
    return HttpResponseRedirect(reverse('parts:parts-admin'))

@permission_required('parts.add_part')
def edit_part(request):
    """Update an existing Part using PartForm received via request."""
    part = Part.objects.get(id=request.POST['part_id'])
    updated = PartForm(request.POST, instance=part)
    updated.save()
    return HttpResponseRedirect(reverse('parts:parts-admin'))

@permission_required('parts.add_part')
def add_part_to_order(request):
    """After validation, add a part to the parts order session variable."""
    error = None
    quantity = 0
    cost = 0.0
    part_request = None
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
    if 'part_request_id' in request.POST:
        try:
            part_request = PartRequest.objects.get(id=request.POST['part_request_id'])
        except:
            error = 'There was an issue with the request. Please try again.'
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
        if part_request:
            part_request.on_order = True
            part_request.save()
            request.session['unactioned_part_requests'] = PartRequest.objects.filter(assigned_to = request.user.manager, on_order=False).count()
    return HttpResponseRedirect(request.headers['Referer'])

@permission_required('parts.add_part')
def update_part_in_order(request):
    """Update the quantity of a part in the parts order session variable."""
    try:
        request.session['parts_order'][request.POST['part_id']]['quantity'] = request.POST['quantity']
        request.session.modified = True
    except:
        messages.warning(request, 'An error has occurred. Please retry.')
    return HttpResponseRedirect(request.headers['Referer'])

@permission_required('parts.add_part')
def remove_part_from_order(request):
    """Remove a part from the parts order session variable."""
    try:
        request.session['parts_order'].pop(request.POST['part_id'])
        request.session.modified = True
    except KeyError:
        messages.warning(request, 'An error has occurred. Please retry.')
    return HttpResponseRedirect(request.headers['Referer'])

@permission_required('parts.add_part')
def order_parts(request):
    """Create new PartsOrder.
    
    For each part in the PartsOrder, validate and create a new PartsOrderUnit,
    linked to the PartsOrder
    """
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

class PartsOrderList(PermissionRequiredMixin, generic.ListView):
    """List PartsOrders, ordered by most recent."""
    permission_required = 'parts.add_part'
    model = PartsOrder

    def get_ordering(self):
        return '-placed'

class PartsOrderDetail(PermissionRequiredMixin, generic.DetailView):
    """Show details for a PartsOrder"""
    permission_required = 'parts.add_part'
    model = PartsOrder

@permission_required('parts.add_part')
def check_in_parts_order_unit(request):
    """Mark a PartsOrderUnit as checked in and update stock level of Part."""
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

@permission_required('parts.add_part')
def part_request_list(request):
    """List current PartRequests."""
    part_requests = PartRequest.objects.filter(assigned_to = request.user.manager)
    context = {
        'part_requests': part_requests,
    }
    return render(request, 'parts/partrequest_list.html', context)

@permission_required('parts.add_part')
def delete_part_request(request):
    """Delete a PartRequest."""
    try:
        PartRequest.objects.get(id=request.POST['part_request_id']).delete()
    except:
        messages.warning(request, 'An error has occured. Please try again.')
    return HttpResponseRedirect(request.headers['Referer'])
