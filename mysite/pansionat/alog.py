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

def log_message(request, message):
    l = ActionLog(ip = request.META['REMOTE_ADDR'], user = request.user, path = request.path,
        message = message, dt = datetime.datetime.now())
    l.save()

@login_required
def lastlog(request):
    dt = datetime.date.today()
    ls = ActionLog.objects.all().order_by('-dt')[:100]
    m = dict()
    m["ls"] = ls
    td = datetime.timedelta(days=1)
    pday = dt - td
    nday = dt + td
    m["pday"] = str(pday)
    m["nday"] = str(nday)
    return render_to_response('pansionat/log.html', MenuRequestContext(request, m))

@login_required
def lastlog_day(request, year, month, day):
    dt = datetime.date(int(year),int(month),int(day))
    td = datetime.timedelta(days=1)
    pday = dt - td
    nday = dt + td
    ls = ActionLog.objects.filter(dt__range = (dt,nday)).order_by('-dt')[:100]
    m = dict()
    m["ls"] = ls
    m["pday"] = str(pday)
    m["nday"] = str(nday)
    return render_to_response('pansionat/log.html', MenuRequestContext(request, m))
