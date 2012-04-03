# Create your views here.
# coding: utf-8
import re
from string import upper
import user
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.aggregates import Count, Sum, Max
from django.forms.fields import CharField
from django.forms.widgets import Textarea

from django.template import loader
from pansionat.gavnetso import initfuckinghistory
from pansionat.models import Patient
from pansionat.models import RoomType
from pansionat.models import Room
from pansionat.models import Book
from pansionat.models import RoomBook
from pansionat.models import Order
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import redirect 
import logging
from mysite.pansionat import gavnetso
from mysite.pansionat.documents import createNakladnaya, getOrCreateDocItem
from mysite.pansionat.models import IllHistory, Customer, IllHistoryFieldType, IllHistoryFieldValue, IllHistoryRecord, OrderMedicalProcedure, MedicalProcedureType, OrderMedicalProcedureSchedule, Occupied, IllHistoryFieldTypeGroup, EmployerRoleHistory, Role, Employer, OrderDiet, Diet, OrderDay, OrderType, DietItems, Item, ItemPiece, Piece, MARRIAGE, EmployerCabinet, OrderDocumentItem
from mysite.pansionat.orders import room_availability, fill_cust_list, return_orders_list
from mysite.pansionat.proc import MenuRequestContext, MedicalPriceReport
from mysite.pansionat.reports import DietForm, DateFilterForm, PFCondition, ElseCondition, SPCondition, PPCondition, RCondition, SzCondition, HzCondition, HzSzCondition
from pytils import numeral
from mysite.pansionat.gavnetso import monthlabel, nextmonthfirstday, initbase, initroles, initroomtypes, initp, initdiet, fillBookDays, fillOrderDays, inithistory, import_bron, import_proc, import_rooms, import_ordertypes, fillBookAllDays, getEmployersByRoleAndDate
import datetime
import time
from django import forms
from django.forms import ModelForm
from django.core.context_processors import csrf
from django.db.models import Q

from mysite.pansionat.xltemplates import fill_excel_template, fill_excel_template_s_gavnom, fill_excel_template_porcii, fill_excel_template_with_many_tp


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def index(request):
	t = loader.get_template('pansionat/index.html')
	c = MenuRequestContext(request, {
        'next': request.GET.get('next','')
	})
	return HttpResponse(t.render(c))

def forbidden(request):
	t = loader.get_template('pansionat/forbidden.html')
	c = MenuRequestContext(request, {
        'next': request.GET.get('next','')
	})
	return HttpResponse(t.render(c))

@login_required
@permission_required('pansionat.add_patient', login_url='/forbidden/')
def patients(request):
	patients_list = Patient.objects.all()
	t = loader.get_template('pansionat/patients.html')
	c = MenuRequestContext(request, {
	'patients_list': patients_list,
	})
	return HttpResponse(t.render(c))

@login_required
def clients(request):
	clients_list = Customer.objects.all()
	t = loader.get_template('pansionat/clients.html')
	c = MenuRequestContext(request, {
	'clients_list': clients_list,
	})
	return HttpResponse(t.render(c))

def return_order_menu(form, request):
    t = loader.get_template('pansionat/ordersmenu.html')
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    year = datetime.date.today().year
    c = MenuRequestContext(request, {
        "months": months,
        "year": year,
        "today": datetime.date.today(),
        "form": form
    })
    resp = HttpResponse(t.render(c))
    return resp


@login_required
def ordersmenu(request):
    form = DateFilterForm()
    return return_order_menu(form, request)

@login_required
def orders_by_month(request, year, month):
    intyear = int(year)
    intmonth = int(month)
    cd = datetime.date(intyear, intmonth,1)
    fd = nextmonthfirstday(intyear, intmonth)
    occupied_list = Order.objects.filter(start_date__range=(cd,fd)).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
    return return_orders_list(occupied_list, request, str(intyear)+"/"+str(intmonth))


@login_required
def filterorders(request):
    form = DateFilterForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data.get("start_date",datetime.date.today())
        fd = form.cleaned_data.get("end_date",datetime.date.today())
        occupied_list = Order.objects.filter(start_date__range=(cd,fd)).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
        return return_orders_list(occupied_list, request,"С "+str(cd)+" по "+str(fd))
    else:
        return return_order_menu(form, request)

@login_required
def orders(request):
    occupied_list = Order.objects.all().values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
    return return_orders_list(occupied_list, request,"")

@login_required
def books(request):
    occupied_list = Book.objects.all()
    t = loader.get_template('pansionat/books.html')
    c = MenuRequestContext(request, {
        'occupied_list': occupied_list,
    })
    resp = HttpResponse(t.render(c))
    return resp

@login_required
def book_enable(request, instance_id):
    instance = Book.objects.get(id = instance_id)
    clearBookDays(instance)
    instance.status = 0
    instance.save()
    fillBookAllDays(instance)
    return redirect("/rmregbook/")

@login_required
def book_disable(request, instance_id):
    instance = Book.objects.get(id = instance_id)
    clearBookDays(instance)
    instance.status = -1
    instance.save()
    return redirect("/rmregbook/")

@login_required
def book_edit(request, instance_id):
    instance = Book.objects.get(id = instance_id)
    rbs = instance.roombook_set.all()
    rooms = ""
    for rb in rbs:
        if rooms == "":
            rooms += upper(rb.room.name)
        else:
            rooms += ","+upper(rb.room.name)
    form = BookEditForm(initial = {'rooms' : rooms}, instance=instance)
    values = {'form' : form,\
                'instance_id' : instance_id}
    return render_to_response('pansionat/book_edit.html', MenuRequestContext(request, values))

@login_required
def book_new(request):
    instance = Book()
    rooms = ""
    form = BookEditForm(initial = {'rooms' : rooms}, instance=instance)
    values = {'form' : form,\
                'instance_id' : ""}
    return render_to_response('pansionat/book_edit.html', MenuRequestContext(request, values))

def my_view(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            url = request.POST.get("next",request.META['HTTP_REFERER'])
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect('/?msg="Пользователь не активирован"/')
            # Return a 'disabled account' error message
    else:
        return HttpResponseRedirect('/?msg="Необходимо авторизоваться"/')
        # Return an 'invalid login' error message.

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def orders_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    occupied_list = Order.objects.filter(patient = patient).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
    return return_orders_list(occupied_list, request, u"Пациент:"+patient.fio())

@login_required
def orders_room(request, room_id):
    room = Room.objects.get(id=room_id)
    occupied_list = Order.objects.filter(room = room).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("-start_date")
    return return_orders_list(occupied_list, request, u"Номер:"+room.name)

@login_required
def patient_edit(request, patient_id):
    patient = Patient.objects.get(id = patient_id)
    grades = set()
    pwhs = set()
    ps = Patient.objects.all()
    for p in ps:
        grades.add(p.grade)
        pwhs.add(p.passport_whom)
    patient_form = PatientForm(instance=patient)
    values = {'patient_form' : patient_form,\
                'allgrades' : grades,
                'allpw' : pwhs,
                'patient_id' : patient_id}
    return render_to_response('pansionat/patient.html', MenuRequestContext(request, values))

@login_required
def patient_new(request):
    patient_form = PatientForm()
    grades = set()
    pwhs = set()
    ps = Patient.objects.all()
    for p in ps:
        grades.add(p.grade)
        pwhs.add(p.passport_whom)
    values = {'patient_form' : patient_form,
              'allgrades' : grades,
              'allpw' : pwhs
    }
    return render_to_response('pansionat/patient.html', MenuRequestContext(request, values))

@login_required
def patient_save(request):
    if request.method == 'POST':
        patient_form = None
        patient_id = request.POST.get('patient_id')
        if patient_id is None:
            patient_form = PatientForm(request.POST) 
        else:
            patient = Patient.objects.get(id = patient_id)            
            patient_form = PatientForm(request.POST, instance = patient)

        if patient_form.is_valid():
            patient = patient_form.save()
            patient_form = PatientForm(instance = patient)
            values = {'patient_form' : patient_form, 'patient_id' : patient.id}
            return render_to_response('pansionat/patient.html', MenuRequestContext(request, values))
        else:
            values = {'patient_form' : patient_form, 'patient_id' : patient_id}
            return render_to_response('pansionat/patient.html', MenuRequestContext(request, values))
    return patient_new(request) #if method is't post then show empty form

@login_required
def client_edit(request, client_id):
    client = Customer.objects.get(id = client_id)
    client_form = CustomerForm(instance=client)
    values = {'client_form' : client_form,\
                'client_id' : client_id}
    return render_to_response('pansionat/client.html', MenuRequestContext(request, values))

@login_required
def client_new(request):
    client_form = CustomerForm()
    values = {'client_form' : client_form}
    return render_to_response('pansionat/client.html', MenuRequestContext(request, values))

@login_required
def client_save(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        if client_id is None:
            client_form = CustomerForm(request.POST)
        else:
            patient = Customer.objects.get(id = client_id)
            client_form = CustomerForm(request.POST, instance = patient)

        if client_form.is_valid():
            client = client_form.save()
            values = {'client_form' : client_form, 'client_id' : client.id}
        else:
            values = {'client_form' : client_form, 'client_id' : client_id}
        return render_to_response('pansionat/client.html', MenuRequestContext(request, values))
    return patient_new(request) #if method is't post then show empty form

@login_required
def record_edit(request, object_id):
    obj = IllHistoryRecord.objects.get(id = object_id)
    form = RecordForm(instance=obj)
    values = {'form' : form,\
                'object_id' : object_id,
                'ill_history_id' : obj.ill_history.id}
    return render_to_response('pansionat/record.html', MenuRequestContext(request, values))

@login_required
def record_new(request, ill_history_id):
    form = RecordForm()
    values = {'form' : form, 'ill_history_id': ill_history_id}
    return render_to_response('pansionat/record.html', MenuRequestContext(request, values))

@login_required
def record_save(request):
    if request.method == 'POST':
        object_id = request.POST.get('object_id')
        if object_id is None:
            obj = IllHistoryRecord(ill_history = IllHistory.objects.get(id = request.POST.get('id_ill_history_id')))
        else:
            obj = IllHistoryRecord.objects.get(id = object_id)

        form = RecordForm(request.POST, instance = obj)
        if form.is_valid():
            obj = form.save()
            return records(request, obj.ill_history.order.id)
        else:
            values = {'form' : form, 'object_id' : object_id}
            return render_to_response('pansionat/record.html', MenuRequestContext(request, values))
    return record_new(request)

@login_required
def records(request, order_id):
    ord = Order.objects.get(id = order_id)
    ill_historys = IllHistory.objects.filter(order = ord)
    values = {}
    if len(ill_historys)>0:
        ill_history = ill_historys[0]
        values['ill_history_id'] = ill_history.id
    else:
        ill_history = IllHistory(order = ord)
        ill_history.save()
    list = IllHistoryRecord.objects.filter(ill_history = ill_history)
    t = loader.get_template('pansionat/records.html')
    c = MenuRequestContext(request, {
    'list': list,
    'ill_history': ill_history,
    'order': ord,
    })
    return HttpResponse(t.render(c))

@login_required
def medical_procedures_schedule(request, order_id, mp_type_order):
    ord = Order.objects.get(id = order_id)
    mps = MedicalProcedureType.objects.filter(order = mp_type_order)
    mp = mps[0]
    omps = OrderMedicalProcedure.objects.filter(order = ord, mp_type = mp)
    cur_omp = omps[0]

    blockdates = []
    delta = datetime.timedelta(days=1)
    tdelta = datetime.timedelta(minutes=mp.duration)
    hasMoreDays = True
    d = ord.start_date-datetime.timedelta(days=(ord.start_date.weekday()))
    finish_datetime = datetime.datetime.combine(d,mp.finish_time)
    c_day = 0
    week = 0
    curcnt = 0

    sched = {}
    set_checked = set()
    all_scheduled = OrderMedicalProcedureSchedule.objects.filter(mp_type = mp, p_date__gte = ord.start_date, p_date__lte = ord.end_date)
    for sch in all_scheduled:
        key = str(sch.slot)+"_"+str(sch.p_date)
        x = sched.get(key,[])
        x.append(sch.order)
        sched[key] = x
        if ord == sch.order:
            curcnt +=1
            set_checked.add(key)

    days_per_row = 14

    set_another = set()
    order_scheduled = OrderMedicalProcedureSchedule.objects.filter(order = ord, p_date__gte = ord.start_date, p_date__lte = ord.end_date)
    another_sched = dict()
    for sch in order_scheduled:
        t1 = datetime.datetime.combine(d,mp.start_time)
        t2 = datetime.datetime.combine(d,sch.mp_type.start_time)
        t2delta = datetime.timedelta(minutes=sch.mp_type.duration)
        t3 = t2 + (sch.slot-1) * t2delta
        t4 = t2 + sch.slot * t2delta
        i = 1
        while t1<= finish_datetime:
            t11 = t1 + tdelta
            if (t1>=t3 and t1<t4) or (t11>t3 and t11<=t4) or (t1<=t3 and t4<=t11):
                key = str(i)+"_"+str(sch.p_date)
                set_another.add(key)
                another_sched[key] = sch
            t1 = t11
            i +=1

    while hasMoreDays:
        week += 1

        t = datetime.datetime.combine(d,mp.start_time)
        finish_datetime = datetime.datetime.combine(d,mp.finish_time)
        slot = 1
        dates = []
        times = []
        for i in xrange(0,days_per_row):
            cdate = d + datetime.timedelta(days=i)
            day = str(cdate.day)
            if len(day)==1:
                day = "0"+day
            month = str(cdate.month)
            if len(month)==1:
                month = "0"+month
            strd = day+"."+month
            dates.append((strd,cdate>=ord.start_date and cdate<=ord.end_date))

        while t<= finish_datetime:
            hour = str(t.hour)
            if len(hour)==1:
                hour = "0"+hour
            minute = str(t.minute)
            if len(minute)==1:
                minute = "0"+minute
            slots = []
            for i in xrange(0,days_per_row):

                cdate = d + datetime.timedelta(days=i)

                key = str(slot)+"_"+str(cdate)
                orders = sched.get(key,[])
                already = key in set_checked

                a_sch = ""

                if len(orders)>0:
                    lo = len(orders)
                else:
                    lo = ""
                mark = ""
                if already:
                    mark = "checked"
                else:
                    another = key in set_another
                    if another:
                        a_sch = another_sched[key]
                        mark = "another"
                    else:
                        if len(orders)>=cur_omp.mp_type.capacity:
                            mark = "blocked"
                slots.append((already, c_day + i, slot, orders, lo, mark,a_sch))
            times.append((hour+":"+minute, slots, week, slot))

            t += tdelta
            slot +=1

        strd = str(d.year)+"."+str(d.month)+str(d.day)
        blockdates.append((strd,dates,times))
        d+=days_per_row*delta
        c_day += days_per_row
        if d>ord.end_date:
            hasMoreDays = False

    values = {'blockdates': blockdates, 'order_id': order_id, 'patient_name': ord.patient.fio(),
              'mp_order': mp_type_order, 'name': mp.name, 'curcnt': curcnt,'allcnt': cur_omp.times}
    return render_to_response('pansionat/mps.html', MenuRequestContext(request, values))

@login_required
def medical_procedures_schedule_save(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if order_id is None:
            return
        else:
            order = Order.objects.get(id = order_id)
        mp_order = request.POST.get('order')
        mps = MedicalProcedureType.objects.filter(order = mp_order)
        mp = mps[0]

        d = order.start_date-datetime.timedelta(days=(order.start_date.weekday()))
        delta = datetime.timedelta(days=1)
        tdelta = datetime.timedelta(minutes=mp.duration)
        c_day = 0

        while d<=order.end_date:
            t = datetime.datetime.combine(d,mp.start_time)
            finish_datetime = datetime.datetime.combine(d,mp.finish_time)
            slot = 1
            while t<= finish_datetime:
                scheduled = OrderMedicalProcedureSchedule.objects.filter(mp_type = mp, p_date = d, slot= slot)
                orders = []
                already = False
                for omp in scheduled:
                    orders.append(omp.order)
                    if order == omp.order:
                        already = True
                checked = request.POST.get('slot_'+str(c_day)+"_"+str(slot))
                #print str(already)+"/"+str(checked)
                if checked=="True":
                    if not already:
                        omp = OrderMedicalProcedureSchedule(mp_type=mp, p_date=d,slot=slot, order=order)
                        omp.save()
                else:
                    if already:
                        for omp in scheduled:
                            if order == omp.order:
                                omp.delete()
                t += tdelta
                slot +=1
            c_day +=1
            d += delta

        return medical_procedures_schedule(request, order_id, mp_order)
    return ill_history_new(request) #if method is't post then show empty form

@login_required
def medical_procedures(request, order_id):
    ord = Order.objects.get(id = order_id)
    all_mp = MedicalProcedureType.objects.all()
    mps = OrderMedicalProcedure.objects.filter(order = ord)
    choosed = set()
    add_info = {}
    for mp in mps:
        choosed.add(mp.mp_type)
        add_info[mp.mp_type] = (mp.times,mp.add_info)

    order_scheduled = OrderMedicalProcedureSchedule.objects.filter(order = ord, p_date__gte = ord.start_date, p_date__lte = ord.end_date).values('mp_type').annotate(cnt = Count('id'))
    os= dict()
    for o in order_scheduled:
        os[o['mp_type']] = o['cnt']

    choosed_values = {}
    for mp in all_mp:
        value = False
        if mp in choosed:
            value = True
        choosed_values[mp] = (value,add_info.get(mp,""),os.get(mp.id, ""))

    values = {'choosed_values': choosed_values, 'order_id': order_id, 'patient_name': ord.patient.fio()}
    user = request.user
    if user.has_perm('pansionat.add_ordermedicalprocedure'):
        return render_to_response('pansionat/mp.html', MenuRequestContext(request, values))
    else:
        return render_to_response('pansionat/mpreadonly.html', MenuRequestContext(request, values))


def medical_procedures_v2_(request, order_id, nakls):
    ord = Order.objects.get(id=order_id)
    order_scheduled = OrderMedicalProcedureSchedule.objects.filter(order=ord, p_date__gte=ord.start_date,
        p_date__lte=ord.end_date).values('mp_type').annotate(cnt=Count('id'))
    os = fill_order_scheduled(order_scheduled)
    mps = OrderMedicalProcedure.objects.filter(order=ord)
    choosed = list()
    for mp in mps:
        k1 = str(mp.mp_type.id)
        k2 = mp.add_info
        key = k1 + '/' + k2
        choosed.append((mp.mp_type.name, mp.add_info, mp.times, os.get(key, ""), mp.mp_type.id))
    return medical_procedures_v2_common(request, ord, order_id, choosed, nakls, [])


@login_required
def medical_procedures_v2(request, order_id):
    return medical_procedures_v2_(request, order_id,[])


def fill_order_scheduled(order_scheduled):
    os = dict()
    for o in order_scheduled:
        os[o['mp_type'] + '/' + o['add_info']] = o['cnt']
    return os

@login_required
def medical_procedures_v2_common(request, ord, order_id, choosed, nakls, val_ers):

    all_mp = MedicalProcedureType.objects.all()
    m_ai = dict()
    m_ai2 = dict()
    for mp in all_mp:
        l = mp.optional.split(",")
        m_ai[mp.id] = l#map(str, l)
        m_ai2[mp.name] = l

    values = {'choosed': choosed, 'order_id': order_id, 'patient_name': ord.patient.fio(), 'all_mp': all_mp, "mai":m_ai,"mai2":m_ai2,"ves":val_ers, "ns":nakls}
    user = request.user
    if user.has_perm('pansionat.add_ordermedicalprocedure'):
        return render_to_response('pansionat/mp_v2.html', MenuRequestContext(request, values))
    else:
        return render_to_response('pansionat/mpreadonly.html', MenuRequestContext(request, values))

@login_required
def medical_procedures_print(request, order_id):
    ord = Order.objects.get(id = order_id)

    order_scheduled = OrderMedicalProcedureSchedule.objects.filter(order = ord, p_date__gte = ord.start_date, p_date__lte = ord.end_date).order_by('p_date','slot')
    p = []
    for slot in order_scheduled:
        tdelta = datetime.timedelta(minutes=slot.mp_type.duration)
        entry = dict()
        entry['DATE'] = slot.p_date.strftime('%d.%m.%Y')
        mp = OrderMedicalProcedure.objects.filter(order = ord, mp_type=slot.mp_type)
        if len(mp)>0:
            t = datetime.datetime.combine(slot.p_date,slot.mp_type.start_time)
            time = t + (slot.slot-1)*tdelta
            entry['TIME'] = time.strftime('%H:%M')
            add_info = mp[0].add_info
        else:
            add_info = ""
        entry['NAME'] = slot.mp_type.name +" " +add_info
        p.append(entry)

    tel = { 'P': p,
           'FILENAME': 'procedures-'+str(ord.code),
           'PATIENT': ord.patient.fio(),
    }
    template_filename = 'mp.xls'
    return fill_excel_template(template_filename, tel, request)

@login_required
def medical_procedures_print2(request, order_id):
    ord = Order.objects.get(id = order_id)

    order_scheduled = OrderMedicalProcedure.objects.filter(order = ord)
    p = []
    for omp in order_scheduled:
        entry = dict()
        entry['DATE'] = omp.times
        entry['TIME'] = omp.times
        entry['NAME'] = omp.mp_type.name +" " +omp.add_info
        p.append(entry)

    tel = { 'P': p,
            'FILENAME': 'procedures-'+str(ord.code),
            'PATIENT': ord.patient.fio(),
            }
    template_filename = 'mp2.xls'
    return fill_excel_template(template_filename, tel, request)

@login_required
def schedule_print(request):
#def schedule_print(request, mp_type_id, year, month, day):
    mp_type_id = int(request.POST.get("mp_type",""))
    dt = request.POST.get("start_date","")
    dtv = dt.split(".")
    year = int(dtv[2])
    month = int(dtv[1])
    day = int(dtv[0])
    p_date = datetime.date(year, month, day)

    order_scheduled = OrderMedicalProcedureSchedule.objects.filter(p_date = p_date, mp_type = mp_type_id).order_by('slot')
    p = []
    for slot in order_scheduled:
        tdelta = datetime.timedelta(minutes=slot.mp_type.duration)
        entry = dict()
        entry['PATIENT'] = slot.order.patient.fio()
        mp = OrderMedicalProcedure.objects.filter(order = slot.order, mp_type=slot.mp_type)
        if len(mp)>0:
            t = datetime.datetime.combine(slot.p_date,slot.mp_type.start_time)
            time = t + (slot.slot-1)*tdelta
            entry['TIME'] = time.strftime('%H:%M')
            add_info = mp[0].add_info
        else:
            add_info = ""
        entry['NAME'] = slot.mp_type.name +" " +add_info
        p.append(entry)

    tel = { 'P': p,
            'DATE': p_date.strftime('%d.%m.%Y'),
           'FILENAME': 'procedures-'+str(mp_type_id)+"-"+p_date.strftime('%d-%m-%Y'),
    }
    template_filename = 'mps.xls'
    return fill_excel_template(template_filename, tel, request)

@login_required
def schedule_print(request):
#def schedule_print(request, mp_type_id, year, month, day):
    p_date = datetime.date(year, month, day)

    order_scheduled = OrderMedicalProcedureSchedule.objects.filter(p_date = p_date, mp_type = mp_type_id).order_by('slot')
    p = []
    for slot in order_scheduled:
        tdelta = datetime.timedelta(minutes=slot.mp_type.duration)
        entry = dict()
        entry['PATIENT'] = slot.order.patient.fio()
        mp = OrderMedicalProcedure.objects.filter(order = slot.order, mp_type=slot.mp_type)
        if len(mp)>0:
            t = datetime.datetime.combine(slot.p_date,slot.mp_type.start_time)
            time = t + (slot.slot-1)*tdelta
            entry['TIME'] = time.strftime('%H:%M')
            add_info = mp[0].add_info
        else:
            add_info = ""
        entry['NAME'] = slot.mp_type.name +" " +add_info
        p.append(entry)

    tel = { 'P': p,
            'DATE': p_date.strftime('%d.%m.%Y'),
            'FILENAME': 'procedures-'+str(mp_type_id)+"-"+p_date.strftime('%d-%m-%Y'),
            }
    template_filename = 'mps.xls'
    return fill_excel_template(template_filename, tel, request)

@login_required
@permission_required('pansionat.add_orderdiet', login_url='/forbidden/')
def diets_print(request):
    dt = request.POST.get("start_date","")
    dtv = dt.split(".")
    year = int(dtv[2])
    month = int(dtv[1])
    day = int(dtv[0])
    p_date = datetime.date(year, month, day)

    orders = Order.objects.filter(start_date__lte = p_date, end_date__gte = p_date)
    d = dict()

    for order in orders:
        ods = OrderDiet.objects.filter(order = order)
        if len(ods)>0:
            od = ods[0]
            d[od.diet] = d.get(od.diet,0)+1

    p = []
    for key, value in d.items():
        entry = dict()
        entry['DIETNAME'] = key.name
        entry['VALUE'] = value
        p.append(entry)

    tel = { 'P': p,
            'DATE': p_date.strftime('%d.%m.%Y'),
           'FILENAME': 'diets-'+p_date.strftime('%d-%m-%Y'),
    }
    template_filename = 'diets.xls'
    return fill_excel_template(template_filename, tel, request)

@login_required
@permission_required('pansionat.add_ordermedicalprocedure', login_url='/forbidden/')
def mp_save(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if order_id is None:
            return
        else:
            order = Order.objects.get(id = order_id)

        mp_all = MedicalProcedureType.objects.all()
        checked = {}
        times = {}
        add_info = {}
        for f in mp_all:
            checked[f] = request.POST.get('add_field_'+str(f.order),'')
            times[f] = request.POST.get('times_field_'+str(f.order),'')
            add_info[f] = request.POST.get('id_addinfo_field_'+str(f.order),'')
            objects = OrderMedicalProcedure.objects.filter(order = order, mp_type = f)
            was_checked = len(objects) != 0
            if checked[f]:
                if not was_checked:
                    t = times[f]
                    if t == "":
                        delt = order.end_date - order.start_date
                        t = delt.days+1
                    omp = OrderMedicalProcedure(order = order, mp_type = f, times = t, add_info=add_info[f])
                    omp.save()
                else:
                    if times[f]!=objects[0].times or add_info[f]!=objects[0].add_info:
                        objects[0].times = times[f]
                        objects[0].add_info = add_info[f]
                        objects[0].save()
            else:
                if was_checked:
                    objects[0].delete()

        return medical_procedures(request, order_id)
    return ill_history_new(request) #if method is't post then show empty form

@login_required
@permission_required('pansionat.add_ordermedicalprocedure', login_url='/forbidden/')
def mp_save2(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if order_id is None:
            return
        else:
            order = Order.objects.get(id = order_id)

        ch = dict()
        val_er = list()
        for k,v in request.POST.items():
            if k.startswith('id_n_'):
                s = k.split('id_n_')
                idx = s[1]
                name = v
                add_info = request.POST.get('id_a_'+idx)
                count = request.POST.get('id_c_'+idx)
                mpts = MedicalProcedureType.objects.filter(name = name)
                ch[name+u"/"+add_info] = (name,add_info,count,mpts)
                if not len(mpts):
                    val_er.append(u'Не найдено медицинской процедуры '+name)

        if len(val_er):
            ord = order
            order_scheduled = OrderMedicalProcedureSchedule.objects.filter(order = ord, p_date__gte = ord.start_date, p_date__lte = ord.end_date).values('mp_type').annotate(cnt = Count('id'))
            os = dict()
            for o in order_scheduled:
                os[o['name'] + '/' + o['add_info']] = o['cnt']

            choosed = list()
            for key,(name,add_info,count,mpts) in ch.items():
                choosed.append((name, add_info, count,os.get(key,""),0))
            return medical_procedures_v2_common(request, ord, order_id, choosed,[], val_er)

        omps = OrderMedicalProcedure.objects.filter(order = order)

        balance = list()

        for omp in omps:
            key = omp.mp_type.name + u'/' + omp.add_info
            if ch.has_key(key):
                n,a,cnt,mpts = ch.pop(key)
                c = int(cnt)
                if omp.times!=c:
                    balance.append((omp.mp_type, omp.add_info, c - omp.times))
                    omp.times = cnt
                    omp.save()
            else:
                balance.append((omp.mp_type, omp.add_info,  -omp.times))
                omp.delete()

        for k,(n,a,c,mpts) in ch.items():
            omp = OrderMedicalProcedure(order = order, mp_type = mpts[0], add_info = a, times = c)
            balance.append((omp.mp_type, omp.add_info, c))
            omp.save()


        nakls = list()
        if request.POST.get("galka"):
            idx = 0
            if len(balance):
                nakl = createNakladnaya(order_id)
                nakl.save()
                #val_er.append((u"Создана накладная. <a href=\\order\\"+order_id+u"\\docs\\"+str(nakl.id)+u"\\>открыть</a>")
                nakls.append((u"Создана накладная.", order_id,  nakl.id))
                for mp_type,add_info,times in balance:
                    idx += 1
                    di = getOrCreateDocItem(mp_type.name + " " +add_info)
                    #TODO calculate price
                    price = 0
                    odi = OrderDocumentItem(line = idx, order_document = nakl, doc_item = di, quantity = times, price = price)
                    odi.save()

        return medical_procedures_v2_(request, order_id, nakls)
    return ill_history_new(request) #if method is't post then show empty form

@login_required
def ill_history_edit(request, order_id):
    ord = Order.objects.get(id = order_id)
    ill_historys = IllHistory.objects.filter(order = ord)
    values = {}
    if len(ill_historys)>0:
        ill_history = ill_historys[0]
        values['ill_history_id'] = ill_history.id
    else:
        ill_history = IllHistory(order = ord)
    additional_fields = IllHistoryFieldType.objects.all()
    ill_history_form = IllHistoryForm(instance=ill_history)
    ill_history_form.additional_fields = additional_fields
    ill_history_form.add_fields_values = {}
    for f in additional_fields:
        fv = IllHistoryFieldValue.objects.filter(ill_history = ill_history, ill_history_field = f)
        if len(fv)>0:
            ill_history_form.add_fields_values[f] = fv[0].value
        else:
            ill_history_form.add_fields_values[f] = ""

    values['ill_history_form'] = ill_history_form
    values['order_id'] = order_id
    values['patient_name'] = ord.patient.fio()
    return render_to_response('pansionat/illhistory.html', MenuRequestContext(request, values))

@login_required
def ill_history_doctor(request, order_id):
    ord = Order.objects.get(id = order_id)
    ill_historys = IllHistory.objects.filter(order = ord)
    values = {}
    if len(ill_historys)>0:
        ill_history = ill_historys[0]
        values['ill_history_id'] = ill_history.id
        doctor_name = ill_history.doctor.__unicode__()
    else:
        ill_history = IllHistory(order = ord)
        doctor_name = ""

    doctor_role = Role.objects.get(name = "Врач")

    employers = getEmployersByRoleAndDate(doctor_role, ord.start_date)

    doctors_capacity = []
    for emp in employers:
        capacity = IllHistory.objects.filter(order__start_date = ord.start_date, doctor = emp).count()
        doctors_capacity.append((emp, capacity))

    values['doctors_capacity'] = doctors_capacity
    values['doctor_name'] = doctor_name
    values['order_id'] = order_id
    values['patient_name'] = ord.patient.fio()
    return render_to_response('pansionat/doctor.html', MenuRequestContext(request, values))

@login_required
def ill_history_doctor_save1(request, order_id, doctor_id):
    return ill_history_doctor_save(request, order_id, doctor_id, False)

@login_required
def ill_history_doctor_save2(request, order_id, doctor_id):
    return ill_history_doctor_save(request, order_id, doctor_id, True)

@login_required
def ill_history_doctor_save(request, order_id, doctor_id, doc):
    ord = Order.objects.get(id = order_id)
    ill_historys = IllHistory.objects.filter(order = ord)
    doctor = Employer.objects.get(id = doctor_id)
    if len(ill_historys)>0:
        ill_history = ill_historys[0]
        ill_history.doctor = doctor
    else:
        ill_history = IllHistory(order = ord, doctor = doctor)

    ill_history.save()

    if doc:
        return rmdoc(request, ord.start_date.year, ord.start_date.month, ord.start_date.day)
    else:
        return rmregtoday(request)


@login_required
@permission_required('pansionat.add_orderdiet', login_url='/forbidden/')
def orderdiet(request, order_id):
    ord = Order.objects.get(id = order_id)
    orderdiets = OrderDiet.objects.filter(order = ord)
    values = {}
    if len(orderdiets)>0:
        orderdiet = orderdiets[0]
        values['orderdiet_id'] = orderdiet.id
        values['diet_type'] = orderdiet.diet.id
#    else:
#        orderdiet = OrderDiet(order = ord)

    values['order_id'] = order_id
    values['patient_name'] = ord.patient.fio()
    diets = Diet.objects.all()
    diet_ext = []
    for diet in diets:
        s = ""
        for dietitem in diet.dietitems_set.filter(start_date__lte = ord.start_date, end_date__gte = ord.start_date):
            if s=="":
                s = dietitem.item.name
            else:
                s += ',' + dietitem.item.name
        diet_ext.append((diet, s))
    values['types'] = diet_ext
    return render_to_response('pansionat/diet.html', MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_orderdiet', login_url='/forbidden/')
def orderdiet_save(request):
    if request.method == 'POST':
        orderdiet_id = request.POST.get('orderdiet_id')
        if orderdiet_id is None:
            orderdiet = OrderDiet(order = Order.objects.get(id = request.POST.get('id_order_id')))
        else:
            orderdiet = OrderDiet.objects.get(id = orderdiet_id)

        diet_type = request.POST.get('diet_type')
        if diet_type != "":
            diet_type = int(diet_type)
            diet = Diet.objects.get(id = diet_type)
            orderdiet.diet = diet
            orderdiet.save()
            orderdiet_id = orderdiet.id

        values = {'order_id': orderdiet.order.id, 'orderdiet_id': orderdiet_id,
                  'patient_name': orderdiet.order.patient.fio(), 'types': Diet.objects.all(), 'diet_type': diet_type}
        return render_to_response('pansionat/diet.html', MenuRequestContext(request, values))
    return ill_history_new(request) #if method is't post then show empty form

@login_required
def ill_history_new(request):
    ill_history_form = IllHistoryForm()
    values = {'ill_history_form' : ill_history_form}
    return render_to_response('pansionat/illhistory.html', MenuRequestContext(request, values))

@login_required
def ill_history_save(request):
    if request.method == 'POST':
        ill_history_id = request.POST.get('ill_history_id')
        if ill_history_id is None:
            ill_history = IllHistory(order = Order.objects.get(id = request.POST.get('id_order_id')))
        else:
            ill_history = IllHistory.objects.get(id = ill_history_id)

        ill_history_form = IllHistoryForm(request.POST, instance = ill_history)

        additional_fields = IllHistoryFieldType.objects.all()
        ill_history_form.additional_fields = additional_fields
        ill_history_form.add_fields_values = {}
        for f in additional_fields:
            ill_history_form.add_fields_values[f] = request.POST.get('add_field_'+str(f.group.order)+'_'+str(f.order),'')

        if ill_history_form.is_valid():
            ill_history = ill_history_form.save()
            for f in additional_fields:
                fv = IllHistoryFieldValue.objects.filter(ill_history = ill_history, ill_history_field = f)
                value = ill_history_form.add_fields_values[f]
                if len(fv)>0:
                    fv[0].value = value
                    fv[0].save()
                else:
                    fv = IllHistoryFieldValue(ill_history = ill_history, ill_history_field = f, value = value)
                    fv.save()
                    
            ill_history_id = ill_history.id

        values = {'ill_history_form' : ill_history_form, 'order_id':ill_history.order.id, 'ill_history_id' : ill_history_id}
        return render_to_response('pansionat/illhistory.html', MenuRequestContext(request, values))
    return ill_history_new(request) #if method is't post then show empty form

def dellist(l):
    for o in l:
        o.delete()

@login_required
def clear(request):
    dellist(OrderMedicalProcedureSchedule.objects.all())
    dellist(OrderMedicalProcedure.objects.all())
    dellist(MedicalProcedureType.objects.all())
    dellist(IllHistoryFieldValue.objects.all())
    dellist(IllHistory.objects.all())
    dellist(Occupied.objects.all())
    dellist(OrderDiet.objects.all())
    dellist(OrderDay.objects.all())
    dellist(Order.objects.all())
    dellist(Room.objects.all())
    dellist(RoomType.objects.all())
    dellist(RoomBook.objects.all())
    dellist(Book.objects.all())
    dellist(IllHistoryFieldTypeGroup.objects.all())
    dellist(IllHistoryFieldType.objects.all())
    dellist(Patient.objects.all())
    dellist(Customer.objects.all())
    dellist(EmployerRoleHistory.objects.all())
    dellist(Employer.objects.all())
    dellist(Role.objects.all())
    dellist(Diet.objects.all())
    dellist(Item.objects.all())
    dellist(ItemPiece.objects.all())
    dellist(Piece.objects.all())
    dellist(DietItems.objects.all())
    dellist(OrderType.objects.all())

@login_required
def br(request):
    res = import_bron('soon.xls')
    values = {"res":res}
    return render_to_response('pansionat/importorder.html', MenuRequestContext(request, values))

@login_required
def init(request):
    clear(request)
    import_ordertypes()
    import_rooms()
    import_proc()
    import_bron('soon.xls')
    #columns1 = {"n1":0,"n2":2,"d1":6,"put":9,"fio":11,"d":12,"cv":13,"price":17,"c":20,"dr":22,"pd":24,"address":26,"room":28}
    #columns2 = {"n1":0,"n2":2,"d1":6,"put":9,"fio":11,"d":12,"cv":13,"price":16,"c":20,"dr":22,"pd":24,"address":26,"room":28}
    #columns = [columns1, columns2]
    #row_set = set([849])
    #inithistory("201105.xls",columns, row_set)
    columns = [{"n1":0,"n2":1,"d1":2,"put":5,"fio":6,"d":7,"cv":8,"price":9,"c":11,"dr":12,"pd":13,"address":14,"room":15}]
    inithistory("201110.xls",columns,set())
    columns = [{"n1":0,"put":1,"fio":2,"d":3,"cv":4,"price":5,"days":6,"days2":8}]
    #initfuckinghistory("201201.xls",columns,set(),datetime.date(2012,1,1),datetime.date(2012,1,31))
    #initfuckinghistory("201202.xls",columns,set(),datetime.date(2012,2,1),datetime.date(2012,2,29))
    list = RoomType.objects.all()
    if not len(list):
        initroomtypes()
    #order_list = Order.objects.all()
    #if not len(order_list):
    #    initbase(1)
    initroles()
    t = loader.get_template('pansionat/index.html')
    c = MenuRequestContext(request, {
    })
    #list = MedicalProcedureType.objects.all()
    #if not len(list):
    #    initp()
    list = Diet.objects.all()
    if not len(list):
        initdiet()
    return HttpResponse(t.render(c))


def prepare_rmreg_data(orders):
    l = []
    i = 0
    for order in orders:
        i += 1
        innermap = dict()
        innermap['NUMBER'] = i
        innermap['NUMBERYEAR'] = order.code
        innermap['ID'] = order.id
        innermap['AMOUNT'] = order.price
        innermap['DATEIN'] = order.start_date.strftime('%d.%m.%Y')
        innermap['DATEOUT'] = order.end_date.strftime('%d.%m.%Y')
        innermap['SROK'] = order.start_date.strftime('%d.%m.%Y') + ' - ' + order.end_date.strftime('%d.%m.%Y')
        innermap['ORDERNUMBER'] = order.putevka
        innermap['PUTEVKA'] = order.putevka
        if not order.directive is None:
            innermap['WHOM'] = order.directive.shortname
        else:
            innermap['WHOM'] = ''
        innermap['TIME'] = order.start_date.strftime('%d.%m.%Y')
        if not order.customer is None:
            innermap['WORK'] = order.customer.name
        else:
            innermap['WORK'] = ''
        if order.patient is None:
            innermap['FIO'] = ""
            innermap['PID'] = ""
            innermap['WHOIS'] = ""
            innermap['BIRTHDATE'] = ""
            innermap['PASSPORT'] = ""
            innermap['ADDRESS'] = ""
        else:
            innermap['FIO'] = order.patient.__unicode__()
            innermap['PID'] = order.patient.id
            innermap['WHOIS'] = order.patient.grade
            innermap['BIRTHDATE'] = str(order.patient.birth_date)
            innermap['PASSPORT'] = order.patient.passport_number + ' ' + order.patient.passport_whom
            if order.patient.phone is None:
                innermap['ADDRESS'] = order.patient.address
            else:
                innermap['ADDRESS'] = order.patient.address + ' ' + order.patient.phone
        innermap['ROOM'] = order.room.name
        l.append(innermap)
    return l

def prepare_rmdoc_data(dt):
    orders = Order.objects.filter(start_date=dt)
    m = dict()
    mx = 0
    l_e = False
    e_l = []
    doctor_role = Role.objects.get(name = "Врач")
    employers = getEmployersByRoleAndDate(doctor_role, dt)
    l_k = ["Не указан"]
    for emp in employers:
        m[emp] = []
        l_k.append(emp)

    for order in orders:
        ihs = IllHistory.objects.filter(order = order)
        if len(ihs)>0:
            ih = ihs[0]
            d = ih.doctor
            if m.has_key(d):
                ih_l = m.get(d)
            else:
                ih_l = []
                m[d] = ih_l
                l_k.append(d)
        else:
            if not l_e:
                m["Не указан"] = e_l
            ih_l = e_l

        ih_l.append(order)
        cur = len(ih_l)
        if cur>mx:
            mx = cur

    l_v = []
#    for k in m.iterkeys():
#        l_k.append(k)

    for i in xrange(0,mx):
        l2= []
        for j in xrange(0,len(l_k)):
            l3 = m.get(l_k[j],[])
            if len(l3)>i:
                l2.append(m.get(l_k[j])[i])
            else:
                l2.append(None)
        l_v.append(l2)
    return l_k,l_v

def prepare_reestr_data(month, year):
    intyear = int(year)
    intmonth = int(month)
    orders = Order.objects.filter(start_date__year=intyear, start_date__month=intmonth).order_by("start_date","code")
    template_filename = 'registrydiary.xls'
    map = {'MONTH': monthlabel(intmonth) + ' ' + str(intyear) + ' год',
           'TITLE': 'Журнал регистрации отдыхающих',
           'FILENAME': 'reestr-' + year + '-' + month}
    l = prepare_rmreg_data(orders)
    map['T'] = l
    return map, template_filename


@login_required
def reestr(request, year, month):
    map, template_filename = prepare_reestr_data(month, year)
    return render_to_response('pansionat/reports/reestr.html', MenuRequestContext(request, map))

@login_required
def reestrxls(request, year, month):
    map, template_filename = prepare_reestr_data(month, year)
    return fill_excel_template(template_filename, map, request)


def clearBookDays(instance):
    ods = OrderDay.objects.filter(book=instance)
    ods.delete()
    rbs = RoomBook.objects.filter(book=instance)
    rbs.delete()

@login_required
def book_save(request):
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        instance = None
        if instance_id is None:
            form = BookEditForm(request.POST)
        else:
            instance = Book.objects.get(id = instance_id)
            form = BookEditForm(request.POST, instance = instance)

        if form.is_valid():
            if not instance is None:
                clearBookDays(instance)

            instance = form.save()
            rooms = form.cleaned_data["rooms"]
            for r_name in rooms.split(","):
                room = Room.objects.get(name=upper(r_name))
                rb = RoomBook(room =room, book = instance)
                rb.save()
                fillBookDays(instance, room)
            return  redirect('/rmregbook/')
        else:
            values = {'form' : form, 'instance_id' : instance_id}
            return render_to_response('pansionat/book_edit.html', MenuRequestContext(request, values))
    return patient_new(request) #if method is't post then show empty form

def booklist(books, request):
    l = []
    i = 0
    for book in books:
        i += 1
        innermap = dict()
        innermap['NUMBER'] = i
        innermap['STATUS'] = book.status
        innermap['ID'] = book.id
        innermap['NAME'] = book.name
        innermap['PHONE'] = book.phone
        innermap['DESC'] = book.description
        innermap['DATEIN'] = book.start_date.strftime('%d.%m.%Y')
        innermap['DATEOUT'] = book.end_date.strftime('%d.%m.%Y')
        roombooks = book.roombook_set.all()
        q = ""
        for s in roombooks:
            q += s.room.name + " "
        innermap['ROOMS'] = q
        l.append(innermap)
    map = dict()
    map['T'] = l
    dt = datetime.date.today()
    td = datetime.timedelta(days=1)
    pday = dt - td
    nday = dt + td
    map["pday"] = str(pday)
    map["nday"] = str(nday)
    return render_to_response('pansionat/rmregbook.html', MenuRequestContext(request, map))


@login_required
def rmregbook(request):
    books = Book.objects.filter(status = 0).order_by("start_date")
    return booklist(books, request)

@login_required
def rmregbookold(request):
    books = Book.objects.filter(status = -1).order_by("start_date")
    return booklist(books, request)

@login_required
def rmreg(request, year, month, day):
    dt = datetime.date(int(year),int(month),int(day))
    orders = Order.objects.filter(start_date=dt)
    l = prepare_rmreg_data(orders)
    map = dict()
    map['T'] = l
    td = datetime.timedelta(days=1)
    pday = dt - td
    nday = dt + td
    map["pday"] = str(pday)
    map["nday"] = str(nday)
    return render_to_response('pansionat/reports/rmreg.html', MenuRequestContext(request, map))

@login_required
def rmregtoday(request):
    td = datetime.date.today()
    return rmreg(request, td.year, td.month, td.day )

@login_required
def rmdoc(request, year, month, day):
    dt = datetime.date(int(year),int(month),int(day))
    l_k,l_v = prepare_rmdoc_data(dt)
    map = dict()
    map['doctors'] = l_k
    map['patients'] = l_v
    td = datetime.timedelta(days=1)
    pday = dt - td
    nday = dt + td
    map["pday"] = str(pday)
    map["nday"] = str(nday)
    return render_to_response('pansionat/rmdoc.html', MenuRequestContext(request, map))

@login_required
def rmdoctoday(request):
    td = datetime.date.today()
    return rmdoc(request, td.year, td.month, td.day )

@login_required
def moves(request, year, month):
    intyear = int(year)
    intmonth = int(month)
    fd = nextmonthfirstday(intyear, intmonth)
    orders = Order.objects.filter(start_date__year=intyear).values('customer__name').annotate(cnt=Count('customer__name'),sm=Sum('price'))
    template_filename = 'moves.xls'
    map = {'MONTH': monthlabel(intmonth)+' '+str(intyear)+' год',
           'M':monthlabel(intmonth),
           'MNEXT':monthlabel(fd.month),
           'FILENAME': 'moves-'+year+'-'+month,
           'MARKETING': gavnetso.getEmployerByRoleNameAndDate('Маркетинг',datetime.date(intyear, intmonth,1)).__unicode__()}
    l = []
    i = 0
    for order in orders:
        i += 1
        innermap = dict()
        innermap['IDX'] = i
        innermap['NAME'] = order['customer__name']
        innermap['QTY'] = order['cnt']
        innermap['M'] = order['sm']
        innermap['MNEXT'] = order['sm']
        l.append(innermap)

    map['T'] = l
    return fill_excel_template(template_filename, map, request)


def calc_bm(fd, order):
    duration = order.end_date - order.start_date
    if order.end_date < fd:
        days_value = duration.days + 1
        daysn_value = 0
        summc_value = order.price
        summn_value = 0
    else:
        dd = order.end_date - fd
        days = duration.days - dd.days
        days_value = days
        daysn_value = dd.days + 1
        summc_value = days * order.price / (duration.days + 1)
        summn_value = (dd.days + 1) * order.price / (duration.days + 1)
    return days_value, daysn_value, summc_value, summn_value

@login_required
def mov(request, year, month):
    intyear = int(year)
    intmonth = int(month)
    fd = nextmonthfirstday(intyear, intmonth)
    orders = Order.objects.filter(start_date__year=intyear, start_date__month=intmonth).order_by("start_date","code")
    template_filename = 'reestrz.xls'
    map = {'MONTH': monthlabel(intmonth)+' '+str(intyear),
           'MONTHC':monthlabel(intmonth),
           'MONTHN':monthlabel(fd.month),
           'FILENAME': 'moves-'+year+'-'+month,
           'MARKETING': gavnetso.getEmployerByRoleNameAndDate('Маркетинг',datetime.date(intyear, intmonth,1)).__unicode__()}
    l = []
    i = 0
    s1 = s2 = s3 = s4 =0
    for order in orders:
        i += 1
        innermap = dict()
        innermap['IDX'] = i
        innermap['PUTEVKA'] = order.putevka
        innermap['FIO'] = order.patient.fio()
        innermap['D'] = order.patient.grade
        innermap['KEM'] = order.directive.__unicode__()
        innermap['SUMM'] = order.price
        days_value, daysn_value, summc_value, summn_value = calc_bm(fd, order)

        innermap['DAYS'] = days_value
        innermap['DAYSN'] = daysn_value
        innermap['SUMMC'] = summc_value
        innermap['SUMMN'] = summn_value
        s1 += days_value
        s2 += summc_value
        s3 += daysn_value
        s4 += summn_value

        l.append(innermap)

    map['T'] = l
    return fill_excel_template(template_filename, map, request)

tp_map = {
    "1":('ХЗ,СЗ',"hzsz",HzSzCondition()),
    "2":('Прочие',"else",ElseCondition()),
    "3":('Реабилитация',"reab",RCondition()),
    "4":('Пенза проф',"penzaprof",PPCondition()),
    "5":('Самара проф',"samaraprof",SPCondition()),
    "6":('Пенза фсс',"penzafss",PFCondition()),
}

tp2_map = {
    1:('ООО Санаторий Хопровские Зори',"hz",HzCondition()),
    2:('ОАО Сельская здравница',"sz",SzCondition()),
    3:('Прочие организации',"else",ElseCondition()),
    4:('Приобретено(Больницы) Реабилитация',"reab",RCondition()),
    5:('Пенза проф',"penzaprof",PPCondition()),
    6:('Самара проф',"samaraprof",SPCondition()),
    7:('Пенза фсс',"penzafss",PFCondition()),
}

@login_required
def movinfo(request, year, month):
    intyear = int(year)
    intmonth = int(month)
    fd = nextmonthfirstday(intyear, intmonth)
    orders = Order.objects.filter(start_date__year=intyear, start_date__month=intmonth).order_by("code")
    template_filename = 'info.xls'
    map = {'MONTH': monthlabel(intmonth)+' '+str(intyear),
           'MONTHC':monthlabel(intmonth),
           'MONTHN':monthlabel(fd.month),
           'FILENAME': 'moves-info-'+year+'-'+month,
           'MARKETING': gavnetso.getEmployerByRoleNameAndDate('Маркетинг',datetime.date(intyear, intmonth,1)).__unicode__()}
    l = []
    res = list()
    for i in xrange(1,8):
        res.append((0,0,0))
    for order in orders:
        days_value, daysn_value, summc_value, summn_value = calc_bm(fd, order)
        flag = False
        for idx in xrange(1,8):
            if tp2_map[idx][2].process(order):
                if flag:
                    print "Duplicated type of order:"+str(order.code)
                flag = True
                if order.price>0:
                    qty, summc, summn = res[idx-1]
                    res[idx-1] = (qty+1, summc+summc_value,summn+summn_value)


    i = 0
    s1 = s2 = s3 = 0
    for line in res:
        i += 1
        innermap = dict()
        innermap['IDX'] = i
        innermap['NAME'] = tp2_map[i][0]
        innermap['QTY'] = line[0]
        innermap['SUMMC'] = line[1]
        innermap['SUMMN'] = line[2]
        s1 += line[0]
        s2 += line[1]
        s3 += line[2]

        l.append(innermap)

    innermap = dict()
    innermap['IDX'] = ""
    innermap['NAME'] = "Итого"
    innermap['QTY'] = s1
    innermap['SUMMC'] = s2
    innermap['SUMMN'] = s3

    l.append(innermap)

    map['T'] = l
    return fill_excel_template(template_filename, map, request)

def prepare_anal_data(month, year):
    intyear = int(year)
    intmonth = int(month)
    fd = nextmonthfirstday(intyear, intmonth)
    orders = Order.objects.filter(start_date__year=intyear, start_date__month=intmonth).order_by("code")
    template_filename = 'analiz.xls'
    map = {'MONTH': monthlabel(intmonth) + ' ' + str(intyear),
           'MONTHC': monthlabel(intmonth),
           'MONTHN': monthlabel(fd.month),
           'FILENAME': 'moves-analiz-' + year + '-' + month,
           'MARKETING': gavnetso.getEmployerByRoleNameAndDate('Маркетинг',
                                                              datetime.date(intyear, intmonth, 1)).__unicode__()}
    l = []
    res = list()
    idx_dict = dict()
    for order in orders:
        #это ебаная хуйня на случай необходимости удальить все заказы за месяц
        #order.delete()
        days_value, daysn_value, summc_value, summn_value = calc_bm(fd, order)
        key = upper(order.directive.name)
        idx = idx_dict.get(key, -1)
        if idx == -1:
            idx = len(res)
            idx_dict[key] = idx
            res.append((key, 0, 0, 0, 0, 0, 0, 0))
        name, qty, qtyp, summ, qtyc, summc, qtyn, summn = res[idx]
        if summc_value > 0:
            qtyp_c = 1
        else:
            qtyp_c = 0
        res[idx] = (
            name, qty + 1, qtyp + qtyp_c, summ + order.price, qtyc + days_value, summc + summc_value, qtyn + daysn_value
            ,
            summn + summn_value)
    i = 0
    s1 = s2 = s3 = s4 = s5 = s6 = s7 = 0
    for line in res:
        i += 1
        innermap = dict()
        innermap['IDX'] = i
        innermap['NAME'] = line[0]
        innermap['QTY'] = line[1]
        innermap['QTYP'] = line[2]
        innermap['SUMM'] = line[3]
        innermap['QTYC'] = line[4]
        innermap['SUMMC'] = line[5]
        innermap['QTYN'] = line[6]
        innermap['SUMMN'] = line[7]
        s1 += line[1]
        s2 += line[2]
        s3 += line[3]
        s4 += line[4]
        s5 += line[5]
        s6 += line[6]
        s7 += line[7]

        l.append(innermap)
    innermap = dict()
    innermap['IDX'] = ""
    innermap['NAME'] = "Итого"
    innermap['QTY'] = s1
    innermap['QTYP'] = s2
    innermap['SUMM'] = s3
    innermap['QTYC'] = s4
    innermap['SUMMC'] = s5
    innermap['QTYN'] = s6
    innermap['SUMMN'] = s7
    l.append(innermap)
    map['T'] = l
    return map, template_filename


@login_required
def movanal(request, year, month):
    map, template_filename = prepare_anal_data(month, year)
    return render_to_response('pansionat/reports/anal.html', MenuRequestContext(request, map))

@login_required
def movanalxls(request, year, month):
    map, template_filename = prepare_anal_data(month, year)
    return fill_excel_template(template_filename, map, request)

@login_required
def movtp(request, year, month,tp):
    (title,filetitle,condition) = tp_map[tp]
    intyear = int(year)
    intmonth = int(month)
    fd = nextmonthfirstday(intyear, intmonth)
    orders = Order.objects.filter(start_date__year=intyear, start_date__month=intmonth).order_by("start_date","code")
    template_filename = 'reestrzd.xls'
    map = {'MONTH': monthlabel(intmonth)+' '+str(intyear),
           'MONTHC':monthlabel(intmonth),
           'MONTHN':monthlabel(fd.month),
           'TITLE':title,
           'FILENAME': 'moves-'+tp+'-'+year+'-'+month+"-"+filetitle,
           'MARKETING': gavnetso.getEmployerByRoleNameAndDate('Маркетинг',datetime.date(intyear, intmonth,1)).__unicode__()}
    l = []
    i = 0
    c_set = set()
    s1 = 0
    s2 = 0
    s3 = 0
    s4 = 0
    for order in orders:
        if condition.process(order):
            i += 1
            innermap = dict()
            innermap['IDX'] = i
            innermap['PUTEVKA'] = order.putevka
            innermap['FIO'] = order.patient.fio()
            innermap['D'] = order.patient.grade
            innermap['KEM'] = order.directive.__unicode__()
            innermap['SUMM'] = order.price
            srok = str(order.start_date)+'-'+str(order.end_date)
            innermap['SROK'] = srok
            days_value, daysn_value, summc_value, summn_value = calc_bm(fd, order)

            innermap['DAYS'] = days_value
            innermap['DAYSN'] = daysn_value
            innermap['SUMMC'] = summc_value
            innermap['SUMMN'] = summn_value
            s1 += days_value
            s2 += summc_value
            s3 += daysn_value
            s4 += summn_value
            
            l.append(innermap)
            c_set.add(upper(order.directive.name))

    innermap = dict()
    innermap['FIO'] = 'Итого'
    innermap['DAYS'] = s1
    innermap['DAYSN'] = s3
    innermap['SUMMC'] = s2
    innermap['SUMMN'] = s4
    l.append(innermap)

    tps = list()

    for c_name in c_set:
        i = 0
        s1 = 0
        s2 = 0
        s3 = 0
        s4 = 0
        cl = list()
        innermap = dict()
        innermap['FIO'] = c_name
        cl.append(innermap)

        for order in orders:
            if upper(order.directive.name)==c_name and condition.process(order):
                i += 1
                innermap = dict()
                innermap['IDX'] = i
                innermap['PUTEVKA'] = order.putevka
                innermap['FIO'] = order.patient.fio()
                innermap['D'] = order.patient.grade
                innermap['KEM'] = order.directive.__unicode__()
                innermap['SUMM'] = order.price
                srok = str(order.start_date)+'-'+str(order.end_date)
                innermap['SROK'] = srok
                days_value, daysn_value, summc_value, summn_value = calc_bm(fd, order)

                innermap['DAYS'] = days_value
                innermap['DAYSN'] = daysn_value
                innermap['SUMMC'] = summc_value
                innermap['SUMMN'] = summn_value
                s1 += days_value
                s2 += summc_value
                s3 += daysn_value
                s4 += summn_value
                cl.append(innermap)

        innermap = dict()
        innermap['FIO'] = u'Итого по '+c_name
        innermap['DAYS'] = s1
        innermap['DAYSN'] = s3
        innermap['SUMMC'] = s2
        innermap['SUMMN'] = s4
        cl.append(innermap)
        tps.append((c_name,cl))

    map['T'] = l
    return fill_excel_template_with_many_tp(template_filename, map, tps)

@login_required
def nakl(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'torg12_0.xls'
    fullname = str('ООО санаторий "Хопровские зори"')
    vendor = str('КПП 581701001 ')+ fullname + str(' Пензенская обл., п.Колышлей, ул.Лесная 1а')
    if order.patient.address is None:
        client  = order.patient.fio()
    else:
        client  = order.patient.fio()+','+order.patient.address
    delt = order.end_date - order.start_date
    days = delt.days + 1
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    gb = gavnetso.getEmployerByRoleNameAndDate('Главный бухгалтер',order.start_date).__unicode__()
    kassir = gavnetso.getEmployerByRoleNameAndDate('Кассир',order.start_date).__unicode__()
    tovar = str('Пут. сан.-кур. на ')+str(days)+str(' дней c ')+str(order.start_date)+str(' по ')+str(order.end_date) + str('№ ')+ str(order.code)
    price = order.price
    rub = numeral.rubles(float(price), True)
    tel = {'PORTRAIT':False, 'NUMPAGES':1, 'PIZDEZ': fullname, 'NUMBER': order.code,
           'FILENAME': 'nakladnaya-'+str(order.code),
           'CLIENT': client, 'VENDOR': vendor,
           'DIRECTOR': dir,
           'GBUH': gb,
           'KASSIR': kassir,
           'SP': rub,
           'DATE':order.start_date.strftime('%d.%m.%Y'), 'QTYSUM':1, 'AMOUNTSUM':order.price, 'AMOUNTNDSSUM':order.price, 'ALLAMOUNTSUM':order.price,
           'TOVAR': [{'ROWINDEX':1,'NAME':tovar,'QTY':1,'PRICE':order.price,'AMOUNT':order.price,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':order.price}]}
    return fill_excel_template(template_filename, tel, request)

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def ill_history(request, order_id):
    order = Order.objects.get(id=order_id)
    template_filename = 'history.xls'
    if order.patient.birth_date:
        delt = datetime.date.today() - order.patient.birth_date
        years = int (delt.days / 365.25)
    else:
        years = ""
    srok = 'c '+str(order.start_date)+' по '+str(order.end_date)
    ill_historys = IllHistory.objects.filter(order = order)
    if len(ill_historys)>0:
        ill_history = ill_historys[0]
    else:
        ill_history = IllHistory(order = order)
    ill_history_fields = IllHistoryFieldValue.objects.filter(ill_history = ill_history)
    ill_history_records = IllHistoryRecord.objects.filter(ill_history = ill_history).order_by('datetime')
    #first_diagnose = ill_history.first_diagnose
    #pref = u'С каким диагнозом прибыл: '
    #first_diagnose =  pref + first_diagnose
    #main_diagnose =  u'Диагноз санатория а) основной: ' + ill_history.main_diagnose
    #secondary_diagnose = u'б) сопутствующего заболевания: ' + ill_history.secondary_diagnose
    #conditions =  u'Условия труда и быта больного: ' + ill_history.conditions
    tel = { 'NUMBER': order.code,
           'FILENAME': 'ill_history-'+str(order.code),
           'SURNAME': order.patient.family, 'NAME': order.patient.name,
           'SNAME': order.patient.sname,
           'WHOIS': order.patient.profession,
           'WHOARE': order.patient.grade,
           'CLIENT': order.customer.name,
           'ONANIST': order.patient.marriage,
           'ADDRESS': order.patient.address,
           'AGE': years,
           'SROK':srok,
    }
    return fill_excel_template_s_gavnom(template_filename, tel, ill_history_fields, ill_history_records)

@login_required
def ill_history_head(request, order_id):
    order = Order.objects.get(id=order_id)
    template_filename = 'history_br4.xls'
    if not order.patient.birth_date is None:
        delt = datetime.date.today() - order.patient.birth_date
        years = int (delt.days / 365.25)
    else:
        years = ""
    srok = 'c '+str(order.start_date)+' по '+str(order.end_date)
    if order.customer is None:
        client = "-"
    else:
        client = order.customer.name

    ill_historys = IllHistory.objects.filter(order = order)
    values = {}
    if len(ill_historys)>0:
        ill_history = ill_historys[0]
    else:
        ill_history = IllHistory(order = order)
        ill_history.save()

    doctor = ill_history.doctor
    if doctor:
        cabinets = EmployerCabinet.objects.filter(employer = doctor)
        if len(cabinets):
            cabinet_name = cabinets[0].cabinet_name
        else:
            cabinet_name = ""
    else:
        cabinet_name = ""

    tel = { 'NUMBER': order.putevka,
           'FILENAME': 'ill_history-'+str(order.code),
           'ROOM': order.room.name,
           'CABINET': cabinet_name,
           'SURNAME': order.patient.family, 'NAME': order.patient.name,
           'SNAME': order.patient.sname,
           'WHOIS': order.patient.profession,
           'WHOARE': order.patient.grade,
           'CLIENT': client,
           'ONANIST': order.patient.get_marriage_display(),
           'ADDRESS': order.patient.address,
           'AGE': years,
           'SROK':srok,
           'DATEIN':str(order.start_date),
    }
    return fill_excel_template(template_filename, tel, request)

@login_required
def rootik(request, order_id):
    order = Order.objects.get(id=order_id)
    template_filename = 'rootik.xls'
    tel = {'FIO': order.patient.fio(), 'ROOM': order.room.name,
           'DATEIN': str(order.start_date) }
    return fill_excel_template(template_filename, tel, request)

@login_required
def pko(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'prih_order1.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    client  = order.patient.fio()
    gb = gavnetso.getEmployerByRoleNameAndDate('Главный бухгалтер',order.start_date).__unicode__()
    kassir = gavnetso.getEmployerByRoleNameAndDate('Кассир',order.start_date).__unicode__()
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = { 'NUMPAGES':1,'FULLNAME': fullname, 'NUMBER': order.code,
           'FILENAME': 'pko-'+str(order.code),
           'CLIENT': client,
           'GBUH': gb,
           'KASSIR': kassir,
           'PRICE': order.price,
           'DATE':order.start_date.strftime('%d.%m.%Y'),
           'DESCRIPTION':tovar}
    return fill_excel_template(template_filename, tel, request)

@login_required
def rko(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'rko.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    client  = order.patient.fio()
    gb = gavnetso.getEmployerByRoleNameAndDate('Главный бухгалтер',order.start_date).__unicode__()
    kassir = gavnetso.getEmployerByRoleNameAndDate('Кассир',order.start_date).__unicode__()
    director = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    delt = order.end_date - order.start_date
    days = delt.days + 1
    rub = numeral.rubles(float(order.price), True)
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = { 'NUMPAGES':1,'FULLNAME': fullname, 'NUMBER': order.code,
            'FILENAME': 'rko-'+str(order.code),
            'CLIENT': client,
            'GBUH': gb,
            'DIRECTOR':director,
            'SUMMP':rub,
            'KASSIR': kassir,
            'PRICE': order.price,
            'DATE':order.start_date.strftime('%d.%m.%Y'),
            'DESCRIPTION':tovar}
    return fill_excel_template(template_filename, tel, request)

@login_required
def delbook(request, roombook_id):
    roombook = RoomBook.objects.get(id=roombook_id)
    roombook.delete()
    return redirect('/rooms/')

@login_required
def delorder(request, order_id):
    ord = Order.objects.get(id=order_id)
#    clearOrderDays(ord)
#    ord.delete()
    return redirect('/rooms/')

@login_required
def zayava(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'zayava.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    clientaddress = order.patient.address
    clientio = order.patient.name + ' ' + order.patient.sname
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tel = {'FULLNAME': fullname, 'CODE': order.putevka,
           'FILENAME': 'zayavlenie-'+str(order.code),
           'ROOM': order.room.name,
           'CLIENTFAMILY': order.patient.family,
           'CLIENTIO': clientio,
           'CLIENTADDRESS': clientaddress,
           'DIRECTOR': dir,
           'AMOUNT': order.price,
           'DAYS': days,
           'STARTDATE': str(order.start_date),
           'ENDDATE': str(order.end_date),
           'DATE':order.start_date, 'QTYSUM':1, 'AMOUNTSUM':order.price, 'AMOUNTNDSSUM':order.price, 'ALLAMOUNTSUM':order.price}
    return fill_excel_template(template_filename, tel, request)

@login_required
def schetfactura(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'sch_fakt1.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    saleaddress = 'Пензенская обл., п.Колышлей, ул.Лесная 1а'
    vendor = fullname + ' ' + saleaddress
    if order.patient.address:
        a = order.patient.address
    else:
        a = ""
    client  = order.patient.fio()+a
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    gb = gavnetso.getEmployerByRoleNameAndDate('Главный бухгалтер',order.start_date).__unicode__()
    kassir = gavnetso.getEmployerByRoleNameAndDate('Кассир',order.start_date).__unicode__()
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = {'PORTRAIT':False, 'NUMPAGES':1,'SALER': fullname, 'NUMBER': order.code,
           'FILENAME': 'schetfaktura-'+str(order.code),
           'CLIENT': order.patient.fio(), 'CLIENTADDRESS': order.patient.address,
           'CLIENTALL': client, 'VENDOR': vendor,
           'DIRECTOR': dir,
           'GBUH': gb,
           'KASSIR': kassir,
           'INN': '5817000430 / 581701001',
           'SALEADDRESS': saleaddress,
           'DATE':order.start_date, 'QTYSUM':1, 'AMOUNTSUM':order.price, 'AMOUNTNDSSUM':order.price, 'ALLAMOUNTSUM':order.price,
           'TOVAR': [{'ROWINDEX':1,'NAME':tovar,'QTY':1,'PRICE':order.price,'AMOUNT':order.price,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':order.price}]}
    return fill_excel_template(template_filename, tel, request)

@login_required
def xt(request):
    tel = {'PIZDEZ': 'HZ', 'NUMBER': 1236, 'DATE':'26.07.11', 'QTYSUM':3, 'AMOUNTSUM':17810, 'AMOUNTNDSSUM':17810, 'ALLAMOUNTSUM':17810,
           'TOVAR': [{'ROWINDEX':1,'NAME':'TOVAR1','QTY':1,'PRICE':17810,'AMOUNT':17810,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':17810},
                   {'ROWINDEX':2,'NAME':'TOVAR2','QTY':2,'PRICE':17810,'AMOUNT':17810,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':17810}]}
    template_filename = '/Users/rpanov/Downloads/tov_nakl1.xls'
    return fill_excel_template(template_filename, tel, request)

class FilterForm(forms.Form):
    start_date = forms.DateField(label = 'Дата въезда', input_formats = ('%d.%m.%Y',))
    end_date = forms.DateField(label = 'Дата выезда', input_formats  = ('%d.%m.%Y',))
    room_type = forms.ChoiceField()
    book_type = forms.ChoiceField()
	
def strptime(str_date, str_format):
    return datetime.datetime(*(time.strptime(str_date, str_format)[0:6]))

@login_required
def rooms(request):
    clear_rooms_session(request.session)
    start_date = datetime.date.today()
    end_date = datetime.date.today()
    book_type = 'All'
    room_type = None
               
    if request.method == 'POST':
        start_date = strptime(request.POST['start_date'],\
                     '%d.%m.%Y')
        end_date = strptime(request.POST['end_date'],\
                    '%d.%m.%Y')
        book_type = request.POST['book_type']
        if request.POST['room_type'] != '':
            room_type = int(request.POST['room_type'])

    book_list = room_with_orders(start_date, end_date, room_type, book_type)  
    types = RoomType.objects.all()
    values = {'book_list': book_list, 'types': types,\
              'start_date' : start_date.strftime('%d.%m.%Y'),\
              'end_date' : end_date.strftime('%d.%m.%Y'),\
              'room_type' : room_type,
              'book_type' : book_type,
              'msg' : int(request.GET.get('msg',0)),
              'user' : request.user}
    values.update(csrf(request))
    if 'patient_id' in request.GET:
        patient_id = request.GET['patient_id']
        patient = Patient.objects.get(id=patient_id)
        values['patient'] = patient
    return render_to_response('pansionat/rooms.html', MenuRequestContext(request, values))

def room_with_orders(start_date, end_date, room_type, room_book):

    if not room_type is None:
        room_list = Room.objects.filter(room_type__id = room_type)
    else:
#        room_list = Room.objects.filter(disabled=True)
        room_list = Room.objects.all()

    ordered_rooms = [] 

    for room in room_list:
        (orders, booked, max, ignore) = room_availability(room, start_date, end_date)

        if room_book == 'Booked':
            append = room.room_type.places <= max
        elif room_book == 'NotBooked':
            append = room.room_type.places > max
        elif room_book == 'Empty':
            append = max == 0
        else:
            append = True
        if append:
            ordered_rooms.append((room, orders, booked, len(orders)>0 ,len(booked)>0, max))

    return ordered_rooms

class BookForm(forms.Form):
    start_date = forms.DateField(label = 'Дата въезда', input_formats = ('%d.%m.%Y',))
    end_date = forms.DateField(label = 'Дата выезда', input_formats  = ('%d.%m.%Y',))
    name = forms.CharField(label = 'Имя', max_length = 65535)
    phone = forms.CharField(label = 'Телефон', max_length = 11)
    description = forms.CharField(label = 'Описание', max_length = 65535)
    is_type = forms.BooleanField(label = "Забронировать по типу комнаты", required = False)

#TODO: use django form with multiselect field
@login_required
def book_handler(request):
    # Add handler here
    room_list = request.POST.getlist('rooms')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    patient_id = request.POST.get('patient_id')

    # if rooms haven't selected then we don't add it
    rooms = room_handler(room_list)
    if not rooms is None:
        request.session['rooms'] = rooms

    if (not start_date is None) and (start_date != ''):
        request.session['start_date'] = start_date

    if (not end_date is None) and (end_date != ''):
        request.session['end_date'] = end_date
    if (not patient_id is None) and (patient_id != ''):
        request.session['patient_id'] = patient_id
    
    if (request.POST['is_book']) == 'true':
        return redirect('/bookit')
    return redirect('/order')

@login_required
def orders_room_book(request, room_id):
    room_list = [room_id]

    rooms = room_handler(room_list)
    if not rooms is None:
        request.session['rooms'] = rooms

    td = datetime.date.today().strftime('%d.%m.%Y')
    request.session['start_date'] = td
    request.session['end_date'] = td

    return redirect('/order')

def clear_rooms_session(session):
    if 'rooms' in session:
        del session['rooms']
    if 'start_date' in session:
        del session['start_date']
    if 'end_date' in session:
        del session['end_date']
    if 'patient_id' in session:
        del session['patient_id']

def room_handler(rooms):
    if rooms:#  Check if rooms isn't empty
        query = None
        for room in rooms:
            if not query is None:
                query |= Q(id = room)
            else:
                query = Q(id = room)
        return Room.objects.filter(query)
    return None

@login_required
def bookit(request):
    form = BookForm(initial = {'start_date' : request.session['start_date'],\
                'end_date' : request.session['end_date']})
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            #TODO: use ModelFrom instead of simple form
            book = Book()
            book.status = 0
            book.start_date = form.cleaned_data['start_date']
            book.end_date = form.cleaned_data['end_date']
            book.name = form.cleaned_data['name']
            book.phone = form.cleaned_data['phone']
            book.description = form.cleaned_data['description']
            book.save()
            if not form.cleaned_data['is_type']:
                for room in request.session['rooms']:
                    fillBookDays(book, room)
#                    room_book = RoomBook()
#                    room_book.room = room
#                    room_book.book = book
#                    room_book.save()
            else:
                #TODO: handle room type booking 
                pass
            return redirect('/rooms')
    values = {'rooms' : request.session['rooms'], 'book_form' : form, 'user':request.user}
    values.update(csrf(request))
    return render_to_response('pansionat/bookit.html', values)

@login_required
def mpreport(request):
    types = MedicalProcedureType.objects.all().order_by('order')
    values = {'types' : types }
    return render_to_response('pansionat/mpreport.html', MenuRequestContext(request, values))

@login_required
def dietday(request):
    form = DietForm()
    values = {"form":form}
    return render_to_response('pansionat/dietday.html', MenuRequestContext(request, values))

@login_required
def dietdaychoose(request):
    form = DietForm(request.POST)
    if form.is_valid():
        start_date = form.cleaned_data['report_date']
        day_of_week = start_date.weekday()+1
        dis = DietItems.objects.filter(day_of_week = day_of_week)
#        res = []
#        for di in dis:
        values = {"dietitems":dis}
        return render_to_response('pansionat/dietdaychoose.html', MenuRequestContext(request, values))
    else:
        values = {"form":form}
        return render_to_response('pansionat/dietday.html', MenuRequestContext(request, values))

@login_required
def dietdayreport(request):
    post = request.POST
    res = []
    for key,value in post.items():
        ak = key.split("_")
        if len(ak)>1:
            id = int(ak[len(ak)-1])
            qty = int(value)
            di = DietItems.objects.get(id = id)
            res.append((id,qty,di))
#        for itempiece in di.item.itempiece_set:
#        print key
#        print value
#        res = []
    tel = {}
    tel["filename"] = "porcionnik"
    return fill_excel_template_porcii("porcii.xls",tel,res)
#        for di in dis:
#        values = {"dietitems":dis}
#        return render_to_response('pansionat/dietdaychoose.html', MenuRequestContext(request, values))


@login_required
def diets(request):
    values = { 'start_date': datetime.date.today().strftime('%d.%m.%Y') }
    return render_to_response('pansionat/diets.html', MenuRequestContext(request, values))

class OrderForm(ModelForm):
    class Meta:
        model = Order
#        widgets = {
#            'customer': TextInput(),
#        }
        exclude = ('directive','customer','patient', 'room','order_type')

class BookEditForm(ModelForm):
    rooms = CharField(label = 'Комнаты')
    class Meta:
        model = Book
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 3}),
        }
        additional_fields = { 'rooms': CharField() }
        exclude = ('status')
    def clean_rooms(self):
        data = self.cleaned_data['rooms']
        rooms = data.split(',')
        for room in rooms:
            r_name = upper(room)
            rs = Room.objects.filter(name = r_name)
            if not len(rs):
                raise forms.ValidationError(u"Не найдена комната " + r_name)
        return data

class PatientForm(ModelForm):
    class Meta:
        model = Patient
        widgets = {
            'address': Textarea(attrs={'cols': 80, 'rows': 3}),
        }
    def clean_family(self):
        data = self.cleaned_data['family']
        data = data.strip().capitalize()
        return data
    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.strip().capitalize()
        return data
    def clean_sname(self):
        data = self.cleaned_data['sname']
        data = data.strip().capitalize()
        return data
    def clean_passport_number(self):
        data = self.cleaned_data['passport_number']
        matchObj = re.match( '\d\d\s\d\d\s\d\d\d\d\d\d$', data, flags = 0)
        if not data=='-' and not matchObj:
            raise forms.ValidationError("Поле должно быть вида XX XX XXXXXX или -")
        return data

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        widgets = {
            'address': Textarea(attrs={'cols': 80, 'rows': 3}),
        }
    def clean_inn(self):
        data = self.cleaned_data['inn']
        matchObj = re.match( '[0-9]*$', data, flags = 0)
        if not matchObj:
            raise forms.ValidationError("В ИНН должны быть только цифры")
        return data
    def clean_bank(self):
        data = self.cleaned_data['bank']
        matchObj = re.match( '[0-9]*$', data, flags = 0)
        if not matchObj:
            raise forms.ValidationError("В банковском счете должны быть только цифры")
        return data

class RecordForm(ModelForm):
    class Meta:
        model = IllHistoryRecord
        exclude = ('ill_history')
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 20}),
        }

class IllHistoryForm(ModelForm):
    field_groups = {}
    additional_fields = {}
    add_fields_values = {}
    class Meta:
        model = IllHistory
        exclude = ('order')
        widgets = {
            'first_diagnose': Textarea(attrs={'cols': 80, 'rows': 20}),
            'main_diagnose': Textarea(attrs={'cols': 80, 'rows': 20}),
            'secondary_diagnose': Textarea(attrs={'cols': 80, 'rows': 20}),
            'conditions': Textarea(attrs={'cols': 80, 'rows': 20}),
        }


def clearOrderDays(order):
    ods = OrderDay.objects.filter(order = order)
    for od in ods:
        od.delete()

def order(request):
    if request.session.has_key('rooms'):
        if len(request.session['rooms']) == 1:
            rooms = request.session['rooms']
        else:
            request.session['book_message'] = 'Вы можите заселить только в одну комнату'
            return redirect('/rooms?msg=1')
    else:
        request.session['book_message'] = 'Вы должны выбрать комнату для заселения'
        return redirect('/rooms?msg=2')

    start_date = strptime(request.session['start_date'],'%d.%m.%Y')
    end_date = strptime(request.session['end_date'],'%d.%m.%Y')
    period = strptime(request.session['end_date'],'%d.%m.%Y') - strptime(request.session['start_date'],'%d.%m.%Y')
    price = rooms[0].room_type.price * (period.days + 1)
    room = rooms[0]
    (orders, booked, max, ignore) = room_availability(room, start_date, end_date)

    pl = room.room_type.places - max

    code = Order.objects.filter(start_date__year = start_date.year).aggregate(Max("code"))

    mcode = code['code__max']

    if mcode is None:
        mcode = 0

    order_form = OrderForm(initial={'start_date' : request.session['start_date'],\
                                    'end_date' : request.session['end_date'],\
                                    'price_p': price,
                                    'code': mcode+1})
    cus_error = None
    dir_error = None
    cus = ''
    dir = ''
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        patient_form = None
        patient = None
        if 'patient_id' in request.session:
            patient_id = request.session['patient_id']
            patient = Patient.objects.get(id=patient_id)
        else:
            patient_form = PatientForm(request.POST)

        cus = request.POST.get("customer","")
        customer = None
#        if cus!="":
        cs = Customer.objects.filter(name = cus)
        if not len(cs):
            if request.POST.has_key("c_add"):
                customer = Customer(name = cus,shortname = cus)
                customer.save()
            else:
                cus_error = "Выберите корректный вариант. Вашего варианта нет среди допустимых значений."
        else:
            customer = cs[0]
        dir = order_form.data.get("directive","")
        directive = None
#        if dir!="":
        cs = Customer.objects.filter(name = dir)
        if not len(cs):
            if request.POST.has_key("d_add"):
                directive = Customer(name = dir,shortname = dir)
                directive.save()
            else:
                dir_error = "Выберите корректный вариант. Вашего варианта нет среди допустимых значений."
        else:
            directive = cs[0]

        if order_form.is_valid() and cus_error is None and dir_error is None:
            if not patient_form is None and patient_form.is_valid():
                patient = patient_form.save()

            if not patient is None:
                order = order_form.save(commit = False)
                order.customer = customer
                order.directive = directive
                order.patient = patient
                order.room = rooms[0] # Get first element because len of array should be 1
                order.save()
                fillOrderDays(order)
                return redirect('/rmreg')

    values = {'order_form': order_form, 'cus':cus, 'dir':dir, 'rooms': rooms, user: request.user, 'pr': int(rooms[0].room_type.price), 'pl': int(pl)}
    values.update(csrf(request))
    if 'patient_id' in request.session:
        patient_id = request.session['patient_id']
        patient = Patient.objects.get(id=patient_id)
        values['patient'] = patient
    else:    
        patient_form = PatientForm()
        values['patient_form'] = patient_form

    c_list = fill_cust_list()

    values["customers"] = c_list
    values["cus_error"] = cus_error
    values["dir_error"] = dir_error

    return render_to_response('pansionat/order.html', MenuRequestContext(request, values))
