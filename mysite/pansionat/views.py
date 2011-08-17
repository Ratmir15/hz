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
from mysite import settings
from mysite.pansionat.models import Order, Customer, Occupied
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
    logger.error('trying to render order  '+ str(occupied_list))
    t = loader.get_template('pansionat/orders.html')
    c = Context({
    'occupied_list': occupied_list,
    })
    return HttpResponse(t.render(c))

def reports(request):
    t_list = Occupied.objects.dates('start_date','month', order='DESC')
    logger.error('trying to render order  '+ str(t_list))
    t = loader.get_template('pansionat/reports.html')
    c = Context({
    't_list': t_list,
    })
    return HttpResponse(t.render(c))

def detail(request, patient_id):
    return HttpResponse("You're looking at patient %s." % patient_id)

def nextmonthfirstday(year, month):
    if month==12:
        newmonth = 1
        newyear = year + 1
    else:
        newmonth = month + 1
        newyear = year
    return datetime.date(int(newyear), int(newmonth), 1)

def init(doit):
    if not doit:
        return
    p1 = Patient(family = 'Харитонова',name = 'Ульяна', sname = 'Яковлевна',
                birth_date=datetime.date(1964,8,21),grade='Доярка',
                passport_whom = 'ОВД ОКТ Р-НА',passport_number='63 04 658348',
                address = 'г. Пенза, ул. Кулибина 61-39')
    p1.save()
    p2 = Patient(family = 'Ленин',name = 'Владимир', sname = 'Ильич',
                birth_date=datetime.date(1870,4,22),grade='Лидер',
                passport_whom = 'ОВД ФРУНЗ Р-НА',passport_number='63 04 611148',
                address = 'г. Пенза, ул. Маяковского 61-39')
    p2.save()
    p3 = Patient(family = 'Комарова',name = 'Ирина', sname = 'Викторовна',
                birth_date=datetime.date(1964,8,21),grade='Зав сект',
                passport_whom = 'ОВД ОКТ Р-НА',passport_number='56 09 876408',
                address = 'Г.ПЕНЗА УЛ.КУЛИБИНА 11-39 71-55-45')
    p3.save()
    p4 = Patient(family = 'Бурмистрова',name = 'Валентина', sname = 'Ивановна',
                birth_date=datetime.date(1963,2,15),grade='Бухгалтер',
                passport_whom = 'ОВД ШЕМЫШЕЙКА',passport_number='56 07 736141',
                address = 'ШЕМЫШ.Р-Н С.МАЧКАССЫ УЛ.МОЛОДЕЖНАЯ 5. 28-1-34Д.Т.')
    p4.save()
    c1 = Customer(name = 'Кожвендиспансер')
    c1.save()
    c2 = Customer(name = 'Администрация окт. р-на')
    c2.save()
    c3 = Customer(name = 'Администрация каржиманского c/c')
    c3.save()
    c4 = Customer(name = 'МОУ СОШ№35')
    c4.save()
    c5 = Customer(name = 'Атмис-сахар')
    c5.save()
    c6 = Customer(name = 'ХЗ')
    c6.save()
    c7 = Customer(name = 'ЦРБ')
    c7.save()
    o1 = Order(code = '1266', start_date=datetime.date(2007,7,1),end_date=datetime.date(2007,7,15), patient = p1, customer = c1, directive = c5, price = 12345)
    o1.save()
    o2 = Order(code = '1267', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p2, customer = c2, directive = c5, price = 11000)
    o2.save()
    o3 = Order(code = '1268', start_date=datetime.date(2007,7,3),end_date=datetime.date(2007,7,15), patient = p3, customer = c3, directive = c6, price = 19000)
    o3.save()
    o4 = Order(code = '1269', start_date=datetime.date(2007,7,4),end_date=datetime.date(2007,7,15), patient = p4, customer = c4, directive = c6, price = 12000)
    o4.save()
    rt1 = RoomType(name = 'Люкс', places = 2, price=2000)
    rt1.save()
    rt2 = RoomType(name = 'Полулюкс', places = 3, price=1500)
    rt2.save()
    r1 = Room(name='1СК',room_type=rt1)
    r1.save()
    r2 = Room(name='1Д',room_type=rt2)
    r2.save()
    r3 = Room(name='33Б',room_type=rt2)
    r3.save()
    r4 = Room(name='3НК',room_type=rt1)
    r4.save()
    oc1 = Occupied(order = o1, room = r1, start_date=datetime.date(2007,7,1),end_date=datetime.date(2007,7,15), description = 'первый')
    oc1.save()
    oc2 = Occupied(order = o2, room = r2, start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), description = 'второй')
    oc2.save()
    oc3 = Occupied(order = o3, room = r3, start_date=datetime.date(2007,7,3),end_date=datetime.date(2007,7,15), description = 'третий')
    oc3.save()
    oc4 = Occupied(order = o4, room = r4, start_date=datetime.date(2007,7,4),end_date=datetime.date(2007,7,15), description = 'четвертый')
    oc4.save()

def monthlabel(month):
    if month==1:
        return 'Январь'
    if month==2:
        return 'Февраль'
    if month==3:
        return 'Март'
    if month==4:
        return 'Апрель'
    if month==5:
        return 'Май'
    if month==6:
        return 'Июнь'
    if month==7:
        return 'Июль'
    if month==8:
        return 'Август'
    if month==9:
        return 'Сентябрь'
    if month==10:
        return 'Октябрь'
    if month==11:
        return 'Ноябрь'
    if month==12:
        return 'Декабрь'
    return 'Ну типа this should never accured'



def reestr(request, year, month):
    init(0)
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
           'MARKETING': 'Зитев С.А.'}
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
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = {'PIZDEZ': fullname, 'NUMBER': order.code,
           'FILENAME': 'nakladnaya-'+order.code,
           'CLIENT': client, 'VENDOR': vendor,
           'DIRECTOR': 'Киселев В.И.',
           'GBUH': 'Абрамова Н.Г.',
           'KASSIR': 'Кузьмина В.В.',
           'SP': order.price,
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
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = {'FULLNAME': fullname, 'NUMBER': order.code,
           'FILENAME': 'pko-'+order.code,
           'CLIENT': client,
           'GBUH': 'Абрамова Н.Г.',
           'KASSIR': 'Кузьмина В.В.',
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
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tel = {'FULLNAME': fullname, 'CODE': order.code,
           'FILENAME': 'zayavlenie-'+order.code,
           'ROOM': occupied.room.name,
           'CLIENTFAMILY': order.patient.family,
           'CLIENTIO': clientio,
           'CLIENTADDRESS': clientaddress,
           'DIRECTOR': 'Киселев В.И.',
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
    delt = order.end_date - order.start_date
    days = delt.days + 1
    tovar = 'Пут. сан.-кур. на '+str(days)+' дней c '+str(order.start_date)+' по '+str(order.end_date) + '№ '+ str(order.code)
    tel = {'SALER': fullname, 'NUMBER': order.code,
           'FILENAME': 'schetfaktura-'+order.code,
           'CLIENT': order.patient.fio(), 'CLIENTADDRESS': order.patient.address,
           'CLIENTALL': client, 'VENDOR': vendor,
           'DIRECTOR': 'Киселев В.И.',
           'GBUH': 'Абрамова Н.Г.',
           'KASSIR': 'Кузьмина В.В.',
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
