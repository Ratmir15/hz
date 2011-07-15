# Create your views here.

from django.template import Context, loader
from pansionat.models import Patient
from django.http import HttpResponse

def index(request):
	patients_list = Patient.objects.all()
	t = loader.get_template('pansionat/index.html')
	c = Context({
	'patients_list': patients_list,
	})
	return HttpResponse(t.render(c))

def detail(request, patient_id):
    return HttpResponse("You're looking at patient %s." % patient_id)
	
	