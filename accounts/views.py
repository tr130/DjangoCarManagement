from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from cars.models import Invoice, Message, PartRequest


def logout_view(request):
    logout(request)
    return redirect('cars:index')

def login_view(request):
    error_message = None
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.user.groups.first():
                    request.session['role'] = request.user.groups.first().name
                else:
                    request.session['role'] = None
                request.session['unread'] = Message.objects.filter(recipient = request.user, unread = True).count()
                if request.session['role'] == 'Manager':
                    request.session['parts_order'] = {}
                    request.session['unactioned_part_requests'] = PartRequest.objects.filter(assigned_to = request.user.manager, on_order=False).count()
                elif request.session['role'] == 'Customer':
                    request.session['unpaid'] = Invoice.objects.filter(job__car__owner__user=request.user, job__paid=False).count()
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else:
                    return redirect('cars:home')
        else:
            error_message = 'Something has gone wrong.'
    context = {
        'form': form,
        'error_message': error_message,
    }

    return render(request, 'accounts/login.html', context)