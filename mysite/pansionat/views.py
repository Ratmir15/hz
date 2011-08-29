# Create your views here.
# coding: utf-8
from django.db.models.aggregates import Count, Sum

from django.template import Context, loader
from pansionat.models import Patient
from pansionat.models import RoomType
from pansionat.models import Room
from pansionat.models import Book
from pansionat.models import RoomBook
from pansionat.models import Order
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect 
import logging
from mysite.pansionat import gavnetso
from pytils import numeral
from mysite.pansionat.gavnetso import monthlabel, nextmonthfirstday, init, initroles
import datetime
import time
from django import forms
from django.forms import ModelForm
from django.core.context_processors import csrf
from django.db.models import Q
from django.forms.models import inlineformset_factory

from django.db import connection
from mysite.pansionat.xltemplates import fill_excel_template


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def index(request):
	patients_list = Patient.objects.all()
	t = loader.get_template('pansionat/index.html')
	c = Context({
	'patients_list': patients_list,
	})
	return HttpResponse(t.render(c))

def patients(request):
	patients_list = Patient.objects.all()
	t = loader.get_template('pansionat/patients.html')
	c = Context({
	'patients_list': patients_list,
	})
	return HttpResponse(t.render(c))

def orders(request):
    occupied_list = Order.objects.all()
    t = loader.get_template('pansionat/orders.html')
    c = Context({
    'occupied_list': occupied_list,
    })
    return HttpResponse(t.render(c))

def orders_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    occupied_list = Order.objects.filter(patient = patient)
    t = loader.get_template('pansionat/orders.html')
    c = Context({
    'occupied_list': occupied_list,
    })
    return HttpResponse(t.render(c))

def reports(request):
    t_list = Order.objects.dates('start_date','month', order='DESC')
    t = loader.get_template('pansionat/reports.html')
    c = Context({
    't_list': t_list,
    })
    return HttpResponse(t.render(c))

def detail(request, patient_id):
    patient = Patient.objects.get(id = patient_id)
    t = loader.get_template('pansionat/patient.html')
    c = Context({
    'patient': patient,
    })
    return HttpResponse(t.render(c))

def reestr(request, year, month):
    #init(1)
    #initroles()
    intyear = int(year)
    intmonth = int(month)
    orders = Order.objects.filter(start_date__year=intyear, start_date__month=intmonth)
    template_filename = 'registrydiary.xls'
    map = {'MONTH': monthlabel(intmonth)+' '+str(intyear)+' год',
           'FILENAME': 'reestr-'+year+'-'+month}
    l = []
    i = 0
    for order in orders:
        i += 1
        innermap = dict()
        innermap['NUMBER'] = i
        innermap['NUMBERYEAR'] = i
        innermap['FIO'] = order.patient.__unicode__()
        innermap['AMOUNT'] = order.price
        innermap['DATEIN'] = str(order.start_date)
        innermap['DATEOUT'] = str(order.end_date)
        innermap['SROK'] = str(order.start_date)+' - '+str(order.end_date)
        innermap['ORDERNUMBER'] = order.code
        innermap['WHOIS'] = order.patient.grade
        innermap['WHOM'] = order.directive.name
        innermap['TIME'] = str(order.start_date)
        innermap['WORK'] = order.customer.name
        innermap['BIRTHDATE'] = str(order.patient.birth_date)
        innermap['PASSPORT'] = order.patient.passport_number+' '+order.patient.passport_whom
        innermap['ADDRESS'] = order.patient.address
        innermap['ROOM'] = order.room.name
        l.append(innermap)

    map['T'] = l
    return fill_excel_template(template_filename, map)


def moves(request, year, month):
    init(0)
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
    #print len(occupieds)
    #print connection.queries
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
    return fill_excel_template(template_filename, map)


def nakl(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'tov_nakl1.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    vendor = 'КПП 581701001 '+ fullname + ' Пензенская обл., п.Колышлей, ул.Лесная 1а'
    client  = order.patient.fio()+','+order.patient.address
    delt = order.end_date - order.start_date
    days = delt.days + 1
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    gb = gavnetso.getEmployerByRoleNameAndDate('Главный бухгалтер',order.start_date).__unicode__()
    kassir = gavnetso.getEmployerByRoleNameAndDate('Кассир',order.start_date).__unicode__()
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = {'PIZDEZ': fullname, 'NUMBER': order.code,
           'FILENAME': 'nakladnaya-'+order.code,
           'CLIENT': client, 'VENDOR': vendor,
           'DIRECTOR': dir,
           'GBUH': gb,
           'KASSIR': kassir,
           'SP': numeral.rubles(order.price, True),
           'DATE':order.start_date, 'QTYSUM':1, 'AMOUNTSUM':order.price, 'AMOUNTNDSSUM':order.price, 'ALLAMOUNTSUM':order.price,
           'TOVAR': [{'ROWINDEX':1,'NAME':tovar,'QTY':1,'PRICE':order.price,'AMOUNT':order.price,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':order.price}]}
    return fill_excel_template(template_filename, tel)

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
    tel = {'FULLNAME': fullname, 'NUMBER': order.code,
           'FILENAME': 'pko-'+order.code,
           'CLIENT': client,
           'GBUH': gb,
           'KASSIR': kassir,
           'PRICE': order.price,
           'DATE':order.start_date,
           'DESCRIPTION':tovar}
    return fill_excel_template(template_filename, tel)

def zayava(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'zayava.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    clientaddress = order.patient.address
    clientio = order.patient.name + ' ' + order.patient.sname
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tel = {'FULLNAME': fullname, 'CODE': order.code,
           'FILENAME': 'zayavlenie-'+order.code,
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
    return fill_excel_template(template_filename, tel)

def schetfactura(request, occupied_id):
    order = Order.objects.get(id=occupied_id)
    template_filename = 'sch_fakt1.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    saleaddress = 'Пензенская обл., п.Колышлей, ул.Лесная 1а'
    vendor = fullname + ' ' + saleaddress
    client  = order.patient.fio()+','+order.patient.address
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    gb = gavnetso.getEmployerByRoleNameAndDate('Главный бухгалтер',order.start_date).__unicode__()
    kassir = gavnetso.getEmployerByRoleNameAndDate('Кассир',order.start_date).__unicode__()
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = {'SALER': fullname, 'NUMBER': order.code,
           'FILENAME': 'schetfaktura-'+order.code,
           'CLIENT': order.patient.fio(), 'CLIENTADDRESS': order.patient.address,
           'CLIENTALL': client, 'VENDOR': vendor,
           'DIRECTOR': dir,
           'GBUH': gb,
           'KASSIR': kassir,
           'INN': '5817000430',
           'SALEADDRESS': saleaddress,
           'DATE':order.start_date, 'QTYSUM':1, 'AMOUNTSUM':order.price, 'AMOUNTNDSSUM':order.price, 'ALLAMOUNTSUM':order.price,
           'TOVAR': [{'ROWINDEX':1,'NAME':tovar,'QTY':1,'PRICE':order.price,'AMOUNT':order.price,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':order.price}]}
    return fill_excel_template(template_filename, tel)

def xt(request):
    tel = {'PIZDEZ': 'HZ', 'NUMBER': 1236, 'DATE':'26.07.11', 'QTYSUM':3, 'AMOUNTSUM':17810, 'AMOUNTNDSSUM':17810, 'ALLAMOUNTSUM':17810,
           'TOVAR': [{'ROWINDEX':1,'NAME':'TOVAR1','QTY':1,'PRICE':17810,'AMOUNT':17810,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':17810},
                   {'ROWINDEX':2,'NAME':'TOVAR2','QTY':2,'PRICE':17810,'AMOUNT':17810,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':17810}]}
    template_filename = '/Users/rpanov/Downloads/tov_nakl1.xls'
    return fill_excel_template(template_filename, tel)

class FilterForm(forms.Form):
    start_date = forms.DateField(label = 'Дата въезда', input_formats = ('%d.%m.%Y',))
    end_date = forms.DateField(label = 'Дата выезда', input_formats  = ('%d.%m.%Y',))
    room_type = forms.ChoiceField()
    book_type = forms.ChoiceField()
	
def strptime(str_date, str_format):
    return datetime.datetime(*(time.strptime(str_date, str_format)[0:6]))

def rooms(request):
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
            room_type = request.POST['room_type']

    book_list = room_with_orders(start_date, end_date, room_type, book_type)  
    types = RoomType.objects.all()
    values = {'book_list': book_list, 'types': types,\
              'start_date' : start_date.strftime('%d.%m.%Y'),\
              'end_date' : end_date.strftime('%d.%m.%Y'),\
              'room_type' : room_type}
    values.update(csrf(request))
#    print connection.queries
    return render_to_response('pansionat/rooms.html', values)

def room_with_orders(start_date, end_date, room_type, room_book):
    room_list = None
    
    if not room_type is None:
        room_list = Room.objects.filter(room_type__name = room_type) 
    else:
        room_list = Room.objects.all()

    ordered_rooms = [] 

    for room in room_list:
        order_rooms = room.order_set.filter(start_date__lte = start_date,\
                        end_date__gte = end_date)
        booked_rooms = room.roombook_set.filter(book__start_date__lte = start_date,\
                        book__end_date__gte = end_date)
        ordered_rooms.append((room, order_rooms, booked_rooms))

    return ordered_rooms

class BookForm(forms.Form):
    start_date = forms.DateField(label = 'Дата въезда', input_formats = ('%d.%m.%Y',))
    end_date = forms.DateField(label = 'Дата выезда', input_formats  = ('%d.%m.%Y',))
    name = forms.CharField(label = 'Имя', max_length = 65535)
    phone = forms.CharField(label = 'Телефон', max_length = 11)
    description = forms.CharField(label = 'Описание', max_length = 65535)
    is_type = forms.BooleanField(label = "Забронировать по типу комнаты", required = False)

#TODO: use django form with multiselect field
def book_handler(request):
    # Add handler here
    room_list = request.POST.getlist('rooms')
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    # if rooms haven't selected then we don't add it
    rooms = room_handler(room_list)
    if not rooms is None:
        request.session['rooms'] = rooms

    if (not start_date is None) and (start_date != ''):
        request.session['start_date'] = start_date

    if (not end_date is None) and (end_date != ''):
        request.session['end_date'] = end_date
    
    if (request.POST['is_book']) == 'true':
        return redirect('/bookit')
    return redirect('/order')

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

def bookit(request):
    form = BookForm(initial = {'start_date' : request.session['start_date'],\
                'end_date' : request.session['end_date']})
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            #TODO: use ModelFrom instead of simple form
            book = Book()
            book.start_date = form.cleaned_data['start_date']
            book.end_date = form.cleaned_data['end_date']
            book.name = form.cleaned_data['name']
            book.phone = form.cleaned_data['phone']
            book.description = form.cleaned_data['description']
            book.save()
            if not form.cleaned_data['is_type']:
                for room in request.session['rooms']:
                    room_book = RoomBook()
                    room_book.room = room
                    room_book.book = book
                    room_book.save()
            else:
                #TODO: handle room type booking 
                pass
            return redirect('/rooms')
    values = {'rooms' : request.session['rooms'], 'book_form' : form}
    values.update(csrf(request))
    return render_to_response('pansionat/bookit.html', values)

class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ('patient', 'room')

class PatientForm(ModelForm):
    class Meta:
        model = Patient

def order(request):
    if request.session.has_key('rooms'):
        if len(request.session['rooms']) == 1:
            rooms = request.session['rooms']
        else:
            request.session['book_message'] = 'Вы можите заселить только в одну комнату'
            return redirect('/rooms')
    else:
        request.session['book_message'] = 'Вы должны выбрать комнату для заселения'
        return redirect('/rooms')

    period = strptime(request.session['end_date'],'%d.%m.%Y') - strptime(request.session['start_date'],'%d.%m.%Y')
    price = rooms[0].room_type.price * (period.days + 1)
    
    order_form = OrderForm(initial={'start_date' : request.session['start_date'],\
                                    'end_date' : request.session['end_date'],\
                                    'price': price})
    patient_form = PatientForm()
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        patient_form = PatientForm(request.POST)
        if order_form.is_valid() and patient_form.is_valid():
            patient = patient_form.save()
            order = order_form.save(commit = False)
            order.patient = patient
            order.room = rooms[0] # Get first element because len of array should be 1
            order.save()
            return redirect('/rooms')

    values = {'order_form': order_form, 'patient_form' : patient_form,\
                'rooms': rooms}
    values.update(csrf(request))
    return render_to_response('pansionat/order.html', values)
