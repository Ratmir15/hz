# coding: utf-8
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import ActionLog

__author__ = 'rpanov'

def log_it(request):
    #pass
    l = ActionLog(ip = request.META['REMOTE_ADDR'], user = request.user, path = request.path,
        message = 'Печать отчета', dt = datetime.datetime.now())
    l.save()

@login_required
def lastlog(request):
    ls = ActionLog.objects.all().order_by('-dt')[:100]
    m = dict()
    m["ls"] = ls
    return render_to_response('pansionat/log.html', MenuRequestContext(request, m))

