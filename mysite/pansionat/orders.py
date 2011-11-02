import datetime
from django.contrib.auth.decorators import permission_required, login_required
from django.core import serializers
from django.db import connection
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import OrderDay, Order, Room

__author__ = 'rpanov'

class OrderEditForm(ModelForm):
    class Meta:
        model = Order

@login_required
def order_json(request, order_id):
    response = HttpResponse()
    order = Order.objects.filter(id = order_id)
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(order, ensure_ascii=False, stream=response)
    return response

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def order_edit(request, order_id):
    order = Order.objects.get(id = order_id)
    form = OrderEditForm(instance = order)
    order_days = OrderDay.objects.filter(order = order).order_by("busydate")
    values = {"id":order.id,"form":form}
    places = get_order_places(order)
    values["order_days"] = get_order_days_with_availability(order_days, places)
    return render_to_response('pansionat/order_edit.html', MenuRequestContext(request, values))

@login_required
def net(request):
    d = datetime.date.today()
    td = d + datetime.timedelta(days=60)
    rooms = Room.objects.all().order_by("name")
    res = []
    i = 0
    for room in rooms:
        if not i:
            q = []
            res.append(q)
        orders, booked, max , by_dates = room_availability(room,d,td)
        flag = False
        for key,value in by_dates.items():
            if value<room.room_type.places and not flag:
                q.append((room,key.strftime('%d.%m')))
                flag = True
                print key
                print value
        if not flag:
            q.append((room,''))
        i +=1
        if i==8:
            i = 0
    values = {"res" : res}
    return render_to_response('pansionat/net.html', MenuRequestContext(request, values))

@login_required
@permission_required('pansionat.add_order', login_url='/forbidden/')
def order_save(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if id is None:
            form = OrderEditForm(request.POST)
        else:
            instance = Order.objects.get(id = id)
            form = OrderEditForm(request.POST, instance = instance)

        if form.is_valid():
            #todo check available
            instance = form.save()
            fill_order_days(instance)
            form = OrderEditForm(instance = instance)
            values = {'form' : form, 'id' : instance.id}
        else:
            values = {'form' : form, 'id' : id}
        order_days = OrderDay.objects.filter(order = instance).order_by("busydate")
        places = get_order_places(instance)
        values["order_days"] = get_order_days_with_availability(order_days, places)
        print_q()
        return render_to_response('pansionat/order_edit.html', MenuRequestContext(request, values))
    return None


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


