# Create your views here.

from django.template import Context, loader
from pansionat.models import Patient
from pansionat.models import Room
from django.http import HttpResponse
from django.shortcuts import render_to_response

def index(request):
	patients_list = Patient.objects.all()
	t = loader.get_template('pansionat/index.html')
	c = Context({
	'patients_list': patients_list,
	})
	return HttpResponse(t.render(c))

def detail(request, patient_id):
    return HttpResponse("You're looking at patient %s." % patient_id)
	
	
def bookit(request):
    room_list = Room.objects.all()
    return render_to_response('pansionat/bookit.html', {'rooms':room_list})
