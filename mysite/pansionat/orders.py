# coding: utf-8
import datetime
from string import upper
from django.contrib.auth.decorators import permission_required, login_required
from django.core import serializers
from django.db import connection
from django.forms import forms
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import loader
from mysite import settings
from mysite.pansionat.gavnetso import test_file, import_diets
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import OrderDay, Order, Room, Customer, Patient, PutevkaD

__author__ = 'rpanov'

class OrderEditForm(ModelForm):
    class Meta:
        model = Order
#        widgets = {
#            'customer': TextInput(),
#        }
        exclude = ('directive','customer','patient', 'room','order_type')

@login_required
def order_json(request, order_id):
    response = HttpResponse()
    order = Order.objects.filter(id = order_id)
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(order, ensure_ascii=False, stream=response)
    return response

def fill_cust_list():
    customers = Customer.objects.all()
    c_list = set()
    for customer in customers:
        c_list.add(upper(customer.name))
    return c_list

def ordertr(item):
    item["start_date"] = item["start_date"].strftime('%Y.%m.%d')
    item["end_date"] = item["end_date"].strftime('%Y.%m.%d')
    return item

def return_orders_list(occupied_list, request, msg):
    t = loader.get_template('pansionat/orders.html')
    c = MenuRequestContext(request, {
        'diet_en': request.user.has_perm('pansionat.add_orderdiet'),
        'occupied_list': map(ordertr, occupied_list),
        "msg": msg
        })
    resp = HttpResponse(t.render(c))
    #qs = connection.queries
    #for q in qs:
    #    print q
    return resp

@login_required
def search(request):
    fv = request.POST.get('field_value')
    orders = []
    msg = ""
    if request.POST.has_key('family_search'):
        orders = Order.objects.filter(patient__family__contains=fv).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
        msg  = u"Поиск по фамилии: "+fv
    if request.POST.has_key('family_search'):
        _orders = Order.objects.all().values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
        orders = []
        for order in _orders:
            if order["patient_family"].contains(fv):
                orders.append(order)
        msg  = u"Поиск по фамилии: "+fv
    if request.POST.has_key('family_search2'):
        orders = Order.objects.filter(patient__family__contains=fv).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
        msg  = u"Поиск по фамилии: "+fv
    if request.POST.has_key('pn_search'):
        orders = Order.objects.filter(patient__passport_number__contains=fv).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
        msg  = u"Поиск по номеру паспорта: "+fv
    if request.POST.has_key('code_search'):
        orders = Order.objects.filter(code__contains=fv).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
        msg  = u"Поиск по коду: "+fv
    if request.POST.has_key('putevka_search'):
        orders = Order.objects.filter(putevka__contains=fv).values("id","code","putevka","room__name","patient__family","patient__name","patient__sname","start_date","end_date","customer__name","price").order_by("id")
        msg  = u"Поиск по путевке: "+fv

    if not len(orders):
        return return_orders_list(orders, request, msg)
    else:
        if len(orders)==1:
            return order_edit(request, orders[0]["id"])
        else:
            return return_orders_list(orders, request, msg)

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def order_edit(request, order_id):
    order = Order.objects.get(id = order_id)
    form = OrderEditForm(instance = order)
    order_days = OrderDay.objects.filter(order = order).order_by("busydate")
    values = {"id":order.id,"form":form}
    places = get_order_places(order)
    c_list = fill_cust_list()
    p_list = Patient.objects.all().order_by("family","name","sname")
    r_list = Room.objects.filter(disabled=False).order_by("name")

    values["customers"] = c_list
    values["patients"] = p_list
    values["allrooms"] = r_list
    values["order_days"] = get_order_days_with_availability(order_days, places)
    if not order.customer is None:
        values["cus"] = order.customer.name
    else:
        values["cus"] = ""
    if not order.customer is None:
        values["cus"] = order.customer.name
    else:
        values["cus"] = ""
    if not order.directive is None:
        values["dir"] = order.directive.name
    else:
        values["dir"] = ""
    if not order.patient is None:
        values["pat"] = order.patient.fio()
    else:
        values["pat"] = ""
    if not order.room is None:
        values["rm"] = order.room.name
    else:
        values["rm"] = ""
    return render_to_response('pansionat/order_edit.html', MenuRequestContext(request, values))

class FileForm(forms.Form):
    data = forms.FileField(required=True, label='Данные')

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def test_orders(request):
    values = {"form":FileForm(),"action":"testfile"}
    return render_to_response('pansionat/import_orders.html', MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def import_orders(request):
    values = {"form":FileForm(),"action":"importfile"}
    return render_to_response('pansionat/import_orders.html', MenuRequestContext(request, values))


def handle_upload_file(file_data):
    destination = open(settings.STATIC_ROOT+'/tmp.xls','wb+')
    for chunk in file_data.chunks():
        destination.write(chunk)
    destination.close()

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def import_file(request):
    form = FileForm(request.POST, request.FILES)
    if form.is_valid():
        handle_upload_file(request.FILES['data'])
        res = test_file(settings.STATIC_ROOT+'/tmp.xls', True)
    values = {"res":res}
    return render_to_response('pansionat/importorder.html', MenuRequestContext(request, values))


@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def testfile(request):
    form = FileForm(request.POST, request.FILES)
    if form.is_valid():
        handle_upload_file(request.FILES['data'])
        res = test_file(settings.STATIC_ROOT+'/tmp.xls', False)
    values = {"res":res}
    return render_to_response('pansionat/importorder.html', MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def importdiet(request):
    res = import_diets('dietitems.xls')
    values = {"res":res}
    return render_to_response('pansionat/importorder.html', MenuRequestContext(request, values))

@login_required
def putevkas(request):
    l = PutevkaD.objects.all()
    t = loader.get_template('pansionat/putevkas.html')
    c = MenuRequestContext(request, {
        'l': l,
    })
    resp = HttpResponse(t.render(c))
    return resp

class PutevkaForm(ModelForm):
    class Meta:
        model = PutevkaD

@login_required
def putevka_edit(request, instance_id):
    instance = PutevkaD.objects.get(id = instance_id)
    form = PutevkaForm(instance=instance)
    values = {'form' : form,\
                'instance_id' : instance_id}
    return render_to_response('pansionat/putevka_edit.html', MenuRequestContext(request, values))

@login_required
def putevka_new(request):
    instance = PutevkaD()
    form = PutevkaForm(instance=instance)
    values = {'form' : form,\
                'instance_id' : ""}
    return render_to_response('pansionat/putevka_edit.html', MenuRequestContext(request, values))

@login_required
def putevkas_save(request):
    if request.method == 'POST':
        instance_id = request.POST.get('instance_id')
        instance = None
        if instance_id is None:
            form = PutevkaForm(request.POST)
        else:
            instance = PutevkaD.objects.get(id = instance_id)
            form = PutevkaForm(request.POST, instance = instance)

        if form.is_valid():
            instance = form.save()
            return  redirect('/putevkas/')
        else:
            values = {'form' : form, 'instance_id' : instance_id}
            return render_to_response('pansionat/putevka_edit.html', MenuRequestContext(request, values))
    return putevka_new(request) #if method is't post then show empty form

@login_required
def net(request):
    d = datetime.date.today()
    td = d + datetime.timedelta(days=60)
    return mainnet(request, d, td, False, 8,'pansionat/net.html')

@login_required
def netp(request):
    d = datetime.date.today()
    td = d
    return mainnet(request, d, td, True, 5,'pansionat/net.html')

@login_required
def netpprint(request):
    d = datetime.date.today()
    td = d
    return mainnet(request, d, td, True, 5,'pansionat/netprint.html')

@login_required
def mainnet(request, d, td, show_p, columns, tmpl):
#    rooms = Room.objects.filter(disabled=False).values("name","order_day__set","room_type__places","room_place__id").order_by("name")
    rooms = Room.objects.filter(disabled=False).order_by("room_place__id","name")
    res = []
    i = 0
    j = 0
    max_row = len(rooms)/columns
    for room in rooms:
        if not i:
            q = []
            res.append(q)
        orders, booked, max , by_dates = room_availability(room,d,td)
        choosedkey = None
        lastkey = None
        dateslist = sorted(by_dates.iteritems())
        txt = "<table>"
        for key,value in dateslist:
            lastkey = key
            txt += "<tr><td>"+key.strftime('%d.%m')+"</td><td>"+str(value)+"</td></tr>"
            if value<room.room_type.places and choosedkey is None:
                choosedkey = key
#                print key
#                print value
        txt += "</table>"
        if show_p:
            ar = []
            for order in orders:
                ar.append((order.family(),order.end_date_cool_and_short()))
            q.append((room, "", txt, ar))
        else:
            if choosedkey is None:
                if lastkey is None:
                    dt = ''
                else:
                    dt = (lastkey+ datetime.timedelta(days=1)).strftime('%d.%m')
            else:
                dt = choosedkey.strftime('%d.%m')
            q.append((room, dt, txt, None))
        i +=1
        if i==max_row:
            i = 0
            j += 1
    res_t = []
    for i in xrange(0,max_row):
        q = []
        for j in xrange(0,len(res)):
            if len(res[j])>i:
                q.append(res[j][i])
        res_t.append(q)
    values = {"res" : res_t}
    return render_to_response(tmpl, MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def order_save(request):
    if request.POST.has_key('recalc'):
        id = request.POST.get('id')
        order = Order.objects.get(id = id)
        recalc_order_days(order)
        return redirect('/order/'+str(id))
    if request.POST.has_key('del'):
        id = request.POST.get('id')
        order = Order.objects.get(id = id)
        orders = Order.objects.filter(start_date__year=order.start_date.year, code__gt= order.code)
        if len(orders)==0 and request.user.has_perm('pansionat.delete_order'):
            order.delete()
            return redirect('/orders')
        else:
            return redirect('/order/'+str(id))

    cus_error = None
    dir_error = None
    pat_error = None
    rm_error = None
    cus = ''
    dir = ''
    pat = ''
    rm = ''
    if request.method == 'POST':
        id = request.POST.get('id')
        if id is None:
            order_form = OrderEditForm(request.POST)
        else:
            instance = Order.objects.get(id = id)
            order_form = OrderEditForm(request.POST, instance = instance)

        cus = request.POST.get("customer","")
        customer = None
        #if cus!="":
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
        rm = order_form.data.get("room","")
        room = None
        if rm!="":
            rms = Room.objects.filter(name = rm, disabled = False)
            if not len(rms):
                rm_error = "Выберите корректный вариант. Вашего варианта нет среди допустимых значений."
            else:
                room = rms[0]
        pat = order_form.data.get("patient","")
        patient = None
        if pat!="":
            fio = pat.split(" ")
            family = fio[0]
            if len(fio)>1:
                name = fio[1]
            else:
                name = ""
            if len(fio)>2:
                sname = fio[2]
            else:
                sname = ""
            pt = Patient.objects.filter(family = family, name = name, sname = sname)
            if not len(pt):
                pat_error = "Выберите корректный вариант. Вашего варианта нет среди допустимых значений."
            else:
                patient = pt[0]


        if order_form.is_valid() and cus_error is None and dir_error is None and pat_error is None and rm_error is None:
            #todo check available
            instance = order_form.save(commit=False)
            instance.directive = directive
            instance.customer = customer
            instance.room = room
            instance.patient = patient
            instance.save()

            fill_order_days(instance)
            order_form = OrderEditForm(instance = instance)
            values = {'form' : order_form, 'id' : instance.id}
        else:
            values = {'form' : order_form, 'id' : id}
        values["cus"] = cus
        values["dir"] = dir
        values["rm"] = rm
        values["pat"] = pat
        values["cus_error"] = cus_error
        values["dir_error"] = dir_error
        values["pat_error"] = pat_error
        values["rm_error"] = rm_error
        c_list = fill_cust_list()
        p_list = Patient.objects.all().order_by("family","name","sname")
        r_list = Room.objects.filter(disabled=False).order_by("name")

        values["customers"] = c_list
        values["patients"] = p_list
        values["allrooms"] = r_list
        order_days = OrderDay.objects.filter(order = instance).order_by("busydate")
        places = get_order_places(instance)
        values["order_days"] = get_order_days_with_availability(order_days, places)
        print_q()
        return render_to_response('pansionat/order_edit.html', MenuRequestContext(request, values))


def print_q():
    qs = connection.queries
    for q in qs:
        print q

def get_order_places(order):
    if order.is_with_child:
        return 2
    return 1

def get_order_days_with_availability(od_list, places):
    res = []
    for od in od_list:
        orders, booked, max , by_dates = room_availability(od.room, od.busydate, od.busydate)
        res.append((od, od.room.room_type.places - max + places))
    return res


def fill_order_days(order):
    date = order.start_date
    delta = datetime.timedelta(days=1)
    while date<= order.end_date and order.start_date<=order.end_date:
        ods = OrderDay.objects.filter(order = order, busydate = date)
        if not len(ods):
            orderDay = OrderDay(order = order, busydate = date, room = order.room)
            orderDay.save()
        date += delta
    ods = OrderDay.objects.filter(order = order).exclude(busydate__range = (order.start_date, order.end_date))
    for od in ods:
        od.delete()

def recalc_order_days(order):
    ods = OrderDay.objects.filter(order = order)
    for od in ods:
        od.delete()
    fill_order_days(order)

def room_availability(room, start_date, end_date):
    if start_date==end_date:
        order_rooms = room.orderday_set.filter(busydate = start_date).order_by('busydate')
    else:
        order_rooms = room.orderday_set.filter(busydate__range = (start_date, end_date)).order_by('busydate')

    cnt = 0
    orders = set()
    booked = set()
    cd = ""
    l_cnt = 0
    max = 0
    by_dates = {}
    for ord_days in order_rooms:
        if ord_days.order is None:
            booked.add(ord_days.book)
        else:
            orders.add(ord_days.order)
        if cd != ord_days.busydate:
            if cd!="":
                by_dates[cd] = l_cnt
            l_cnt = 0
            cd = ord_days.busydate

        if ord_days.is_with_child:
            cnt += 2
            l_cnt += 2
        else:
            cnt += 1
            l_cnt += 1
        if max < l_cnt:
            max = l_cnt
        by_dates[cd] = l_cnt
    return orders, booked, max , by_dates


