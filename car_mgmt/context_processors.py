from cars.forms import MessageForm
from accounts.models import Manager

def report_form(request):
    report_form = MessageForm(initial={'sender': request.user, 'recipient': Manager.objects.get(id=1).user})
    return {'report_form': report_form}