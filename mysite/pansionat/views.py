# Create your views here.
# coding: utf-8
from django.db.models.aggregates import Count, Sum

from django.template import Context, loader
from pansionat.models import Patient
from pansionat.models import RoomType
from pansionat.models import Room
from pansionat.models import Book
from pansionat.models import RoomBook
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect 
import logging
from mysite.pansionat import gavnetso
from pytils import numeral
from mysite.pansionat.gavnetso import monthlabel, nextmonthfirstday, init, initroles
from mysite.pansionat.models import Occupied, Role
import datetime
from django import forms
from django.core.context_processors import csrf
from django.db.models import Q

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

def orders(request):
    occupied_list = Occupied.objects.all()
    t = loader.get_template('pansionat/orders.html')
    c = Context({
    'occupied_list': occupied_list,
    })
    return HttpResponse(t.render(c))

def reports(request):
    t_list = Occupied.objects.dates('start_date','month', order='DESC')
    t = loader.get_template('pansionat/reports.html')
    c = Context({
    't_list': t_list,
    })
    return HttpResponse(t.render(c))

def detail(request, patient_id):
    return HttpResponse("You're looking at patient %s." % patient_id)

def reestr(request, year, month):
    init(0)
    #initroles()
    intyear = int(year)
    intmonth = int(month)
    occupieds = Occupied.objects.filter(start_date__year=intyear, start_date__month=intmonth)
    template_filename = 'registrydiary.xls'
    map = {'MONTH': monthlabel(intmonth)+' '+str(intyear)+' год',
           'FILENAME': 'reestr-'+year+'-'+month}
    l = []
    i = 0
    print len(occupieds)
    for occupied in occupieds:
        order = occupied.order
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
        innermap['ROOM'] = occupied.room.name
        l.append(innermap)

    map['T'] = l
    return fill_excel_template(template_filename, map)


def moves(request, year, month):
    init(0)
    intyear = int(year)
    intmonth = int(month)
    fd = nextmonthfirstday(intyear, intmonth)
    occupieds = Occupied.objects.filter(start_date__year=intyear).values('order__customer__name').annotate(cnt=Count('order__customer__name'),sm=Sum('order__price'))
    template_filename = 'moves.xls'
    map = {'MONTH': monthlabel(intmonth)+' '+str(intyear)+' год',
           'M':monthlabel(intmonth),
           'MNEXT':monthlabel(fd.month),
           'FILENAME': 'moves-'+year+'-'+month,
           'MARKETING': gavnetso.getEmployerByRoleNameAndDate('Маркетинг',datetime.date(intyear, intmonth,1)).__unicode__()}
    l = []
    i = 0
    print len(occupieds)
    print connection.queries
    for occupied in occupieds:
        i += 1
        print occupied
        innermap = dict()
        innermap['IDX'] = i
        innermap['NAME'] = occupied['order__customer__name']
        innermap['QTY'] = occupied['cnt']
        innermap['M'] = occupied['sm']
        innermap['MNEXT'] = occupied['sm']
        l.append(innermap)

    map['T'] = l
    return fill_excel_template(template_filename, map)


def nakl(request, occupied_id):
    occupied = Occupied.objects.get(id=occupied_id)
    order = occupied.order
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
    occupied = Occupied.objects.get(id=occupied_id)
    order = occupied.order
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
    occupied = Occupied.objects.get(id=occupied_id)
    order = occupied.order
    template_filename = 'zayava.xls'
    fullname = 'ООО санаторий "Хопровские зори"'
    clientaddress = order.patient.address
    clientio = order.patient.name + ' ' + order.patient.sname
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор',order.start_date).__unicode__()
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tel = {'FULLNAME': fullname, 'CODE': order.code,
           'FILENAME': 'zayavlenie-'+order.code,
           'ROOM': occupied.room.name,
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
    occupied = Occupied.objects.get(id=occupied_id)
    order = occupied.order
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

	
def rooms(request):
    now = datetime.datetime.now()
    book_list = room_with_occupied(now, now)  
    types = RoomType.objects.all()
    values = {'book_list': book_list, 'types': types}
    values.update(csrf(request))
#    print connection.queries
    return render_to_response('pansionat/rooms.html', values)

def room_with_occupied(start_date, end_date):
#    print dir(Room) 
    room_list = Room.objects.all()
    return [(room, room.occupied_set.filter(start_date__lte = start_date,\
                end_date__gte = end_date),\
                room.roombook_set.filter(book__start_date__lte = start_date,\
                book__end_date__gte = end_date))
                for room in room_list]

class BookForm(forms.Form):
    start_date = forms.DateField(label = 'Start Date', input_formats = ('%d.%m.%Y',))
    end_date = forms.DateField(label = 'End date', input_formats  = ('%d.%m.%Y',))
    name = forms.CharField(label = 'Name', max_length = 65535)
    phone = forms.CharField(label = 'Phone', max_length = 11)
    description = forms.CharField(label = 'Description', max_length = 65535)
    is_type = forms.BooleanField(label = "Book by category", required = False)

#TODO: use django form with multiselect field
def bookit(request):
    # Add handler here
    rooms = request.POST.getlist('rooms')
    query = None
    for room in rooms:
        if not query is None:
            query |= Q(id = room)
        else:
            query = Q(id = room)
    book_form = BookForm()
    request.session['rooms'] = Room.objects.filter(query) 
    values = {'rooms' : request.session['rooms'], 'book_form' : book_form}
    values.update(csrf(request))

    return render_to_response('pansionat/bookit.html', values)

def bookit_save(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
#        print dir(form)
        print form.is_valid()
        print form.errors
#TODO: add form validation
 #       if form.is_valid():
            #TODO: use ModelFrom instead of simple form
        book = Book()
        book.start_date = form.cleaned_data['start_date']
        book.end_date = form.cleaned_data['end_date']
        book.name = form.cleaned_data['name']
        book.phone = form.cleaned_data['phone']
        book.description = form.cleaned_data['description']
        book.save()
        #TODO: handle type flag
        for room in request.session['rooms']:
            room_book = RoomBook()
            room_book.room = room
            room_book.book = book
            room_book.save()
#        else:
#            values = {'rooms' : request.session['rooms'], 'book_form' : form}
#            return render_to_response('pansionat/bookit.html', values)
    # anyway redirect to rooms
    return redirect('/rooms')            
