from django.contrib.auth.forms import AuthenticationForm
from cars.forms import MessageForm
from accounts.models import Manager

def report_form(request):
    report_form = MessageForm(initial={'sender': request.user, 'recipient': Manager.objects.get(id=1).user})
    return {'report_form': report_form}

def login_form(request):
    login_form = AuthenticationForm()
    return {'login_form': login_form}