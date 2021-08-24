from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Part
from .forms import PartForm

# Create your views here.
@login_required
def parts_admin(request):
    parts = Part.objects.all().order_by('name')
    context = {
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