# coding: utf-8
import datetime
from django.db import connection
from mysite.pansionat.models import Patient, Customer, Order, Occupied, Room, RoomType, EmployerRoleHistory, Role, Employer, IllHistoryFieldTypeGroup, IllHistoryFieldType, MedicalProcedureType, OrderMedicalProcedure, OrderMedicalProcedureSchedule, RoomBook, Book

def nextmonthfirstday(year, month):
    if month==12:
        newmonth = 1
        newyear = year + 1
    else:
        newmonth = month + 1
        newyear = year
    return datetime.date(int(newyear), int(newmonth), 1)

def initbase(doit):
    if not doit:
        return
    ihftg1 = IllHistoryFieldTypeGroup(description = 'Общие поля', order = 0)
    ihftg1.save()
    ihftg2 = IllHistoryFieldTypeGroup(description = 'Данные объективного исследования', order = 1)
    ihftg2.save()
    ihftg3 = IllHistoryFieldTypeGroup(description = 'Органы дыхания', order = 2)
    ihftg3.save()
    ihftg4 = IllHistoryFieldTypeGroup(description = 'Сердечно-сосудистая система', order = 3)
    ihftg4.save()

    ihft1 = IllHistoryFieldType(description = 'С каким диагнозом прибыл', lines = 3, defval ='',\
                                order = 0, group = ihftg1)
    ihft1.save()
    ihft2 = IllHistoryFieldType(description = 'Диагноз санатория, а) основной', lines = 3, defval ='',\
                                order = 1, group = ihftg1)
    ihft2.save()
    ihft3 = IllHistoryFieldType(description = 'б) сопутствующего заболевания', lines = 3, defval ='',\
                                order = 2, group = ihftg1)
    ihft3.save()
    ihft4 = IllHistoryFieldType(description = 'Условия труда и быта больного', lines = 6, defval ='',\
                                order = 3, group = ihftg1)
    ihft4.save()
    ihft5 = IllHistoryFieldType(description = 'Жалобы больного', lines = 8, defval ='',\
                                order = 4, group = ihftg1)
    ihft5.save()
    ihft6 = IllHistoryFieldType(description = 'Общий анамнез', lines = 5, defval ='',\
                                order = 5, group = ihftg1)
    ihft6.save()
    ihft7 = IllHistoryFieldType(description = 'Начало и развитие настоящего заболевания', lines = 5, defval ='',\
                                order = 6, group = ihftg1)
    ihft7.save()

    ihft = IllHistoryFieldType(description = 'Состояние удовлетворительное', lines = 1, defval ='',\
                                order = 0, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Телосложение', lines = 1, defval ='правильное,неправильное',\
                                order = 1, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = '', lines = 1, defval ='Астеник, нормастеник, гиперстеник',\
                                order = 2, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Питание', lines = 1, defval ='удовлетворительное, повышенное, пониженное',\
                                order = 3, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Кожные покровы', lines = 2, defval ='нормальной окраски, бледные, гиперемированы, желтушные',\
                                order = 4, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Щитовидная железа', lines = 1, defval ='увеличена, не увеличена',\
                                order = 5, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Региональные лимфатические железы-шейные, подмышечные, паховые', lines = 3, defval ='не увеличены, увеличены, мягкие, уплотненные',\
                                order = 6, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'при пальпации', lines = 1, defval ='безболезненные, болезненные',\
                                order = 7, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Косто-мышечная система', lines = 1, defval ='без видимых изменений',\
                                order = 8, group = ihftg2)
    ihft.save()




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
    c1 = Customer(name = 'Кожвендиспансер', inn = 1)
    c1.save()
    c2 = Customer(name = 'Администрация окт. р-на', inn = 2)
    c2.save()
    c3 = Customer(name = 'Администрация каржиманского c/c', inn = 3)
    c3.save()
    c4 = Customer(name = 'МОУ СОШ№35', inn = 4)
    c4.save()
    c5 = Customer(name = 'Атмис-сахар', inn = 5)
    c5.save()
    c6 = Customer(name = 'ХЗ', inn = 6)
    c6.save()
    c7 = Customer(name = 'ЦРБ', inn = 7)
    c7.save()
    r = Room.objects.get(name = '12А')
    o1 = Order(room = r, code = '1290', start_date=datetime.date(2011,10,11),end_date=datetime.date(2011,10,17), patient = p1, customer = c1, directive = c5, price = 12345)
    o1.save()
    r = Room.objects.get(name = '12А')
    o1 = Order(room = r, code = '1291', start_date=datetime.date(2011,10,11),end_date=datetime.date(2011,10,24), patient = p2, customer = c2, directive = c5, price = 12000)
    o1.save()
    r = Room.objects.get(name = '12Б')
    o1 = Order(room = r, code = '1292', start_date=datetime.date(2011,10,11),end_date=datetime.date(2011,10,17), patient = p3, customer = c1, directive = c5, price = 15000)
    o1.save()
    book = Book(start_date=datetime.date(2011,10,11),end_date=datetime.date(2011,10,17),name='Аяцков',phone='5551234',description='вряд ли')
    book.save()
    r = Room.objects.get(name = '13Б')
    rb = RoomBook(book = book, room = r)
    rb.save()
    r1 = Room.objects.get(name = '1СК')
    r2 = Room.objects.get(name = '1Д')
    r3 = Room.objects.get(name = '33Б')
    r4 = Room.objects.get(name = '2Д')
    o1 = Order(room = r1, code = '1266', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p1, customer = c1, directive = c5, price = 12345)
    o1.save()
    o2 = Order(room = r2,code = '1267', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p2, customer = c2, directive = c5, price = 11000)
    o2.save()
    o3 = Order(room = r3, code = '1268', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p3, customer = c3, directive = c6, price = 19000)
    o3.save()
    o4 = Order(room = r4, code = '1269', start_date=datetime.date(2007,7,4),end_date=datetime.date(2007,7,15), patient = p4, customer = c4, directive = c6, price = 12000)
    o4.save()
    oc1 = Occupied(order = o1, room = r1, start_date=datetime.date(2007,7,1),end_date=datetime.date(2007,7,15), description = 'первый')
    oc1.save()
    oc2 = Occupied(order = o2, room = r2, start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), description = 'второй')
    oc2.save()
    oc3 = Occupied(order = o3, room = r3, start_date=datetime.date(2007,7,3),end_date=datetime.date(2007,7,15), description = 'третий')
    oc3.save()
    oc4 = Occupied(order = o4, room = r4, start_date=datetime.date(2007,7,4),end_date=datetime.date(2007,7,15), description = 'четвертый')
    oc4.save()

def initroomtypes():
    rt1 = RoomType(name = 'Двухместный номер блочный повышенной комфортности',\
                   description = 'телевизор, холодильник, душевая кабина, кондиционер',\
                   places = 2, price = 1310, price_alone = 2120)
    rt1.save()
    rt2 = RoomType(name = 'Двухместный номер стандартный',\
                   description = 'телевизор, холодильник',\
                   places = 2, price = 1370, price_alone = 2230)
    rt2.save()
    rt3 = RoomType(name = 'Двухместный номер 1 категории',\
                   description = 'телевизор, холодильник, душевая кабина',\
                   places = 2, price = 1580, price_alone = 2650)
    rt3.save()
    rt4 = RoomType(name = 'Двухместный номер повышенной комфортности',\
                   description = 'телевизор, холодильник, кондиционер',\
                   places = 2, price = 1730, price_alone = 2960)
    rt4.save()
    rt5 = RoomType(name = 'Двухкомнатный номер «Люкс»',\
                   description = 'телевизор, холодильник, душевая кабина, кондиционер',\
                   places = 2, price = 2000, price_alone = 4000)
    rt5.save()
    rt6 = RoomType(name = 'Двухкомнатный номер «Люкс»',\
                   description = 'телевизор, холодильник, душевая кабина',\
                   places = 2, price = 1750, price_alone = 3500)
    rt6.save()
    rt7 = RoomType(name = 'Домики (двухместный номер)',\
                   description = 'телевизор, холодильник',\
                   places = 2, price = 1050, price_alone = 1600)
    rt7.save()
    rt7 = RoomType(name = 'Домики (трехместный номер)',\
                   description = 'телевизор, холодильник',\
                   places = 3, price = 950, price_alone = 0)
    rt7.save()
    rt1list = ['1СК','12А','12Б','13А','13Б','14А','14Б',\
                 '15А','15Б','16','17А','17Б',\
                 '19А','19Б','20А','20Б','21А','21Б',\
                 '22А','22Б','23А','23Б','24А','24Б',\
                 '25А','25Б','26А','26Б','27А','27Б',\
                 '28А','28Б','28В']
    for name in rt1list:
        r1 = Room(name=name,room_type=rt1)
        r1.save()
    rt5list = ['18','29','31','32']
    for name in rt5list:
        r1 = Room(name=name,room_type=rt5)
        r1.save()
    r2 = Room(name='1Д',room_type=rt2)
    r2.save()
    r3 = Room(name='33Б',room_type=rt2)
    r3.save()
    r4 = Room(name='3НК',room_type=rt1)
    r4.save()
    r1 = Room(name='2СК',room_type=rt1)
    r1.save()
    r2 = Room(name='2Д',room_type=rt2)
    r2.save()
    r3 = Room(name='433Б',room_type=rt3)
    r3.save()
    r4 = Room(name='2НК',room_type=rt3)
    r4.save()


def initroles():
    role1 = Role(name = 'Директор')
    role1.save()
    role2 = Role(name = 'Главный бухгалтер')
    role2.save()
    role3 = Role(name = 'Кассир')
    role3.save()
    role4 = Role(name = 'Маркетинг')
    role4.save()
    e1 = Employer(family = 'Зитев',name='С.',sname='А.')
    e1.save()
    e2 = Employer(family = 'Киселев',name='В.',sname='И.')
    e2.save()
    e3 = Employer(family = 'Абрамова',name='Н.',sname='Г.')
    e3.save()
    e4 = Employer(family = 'Кузьмина',name='В.',sname='В.')
    e4.save()
    erh1 = EmployerRoleHistory(employer = e1, role = role4, start_date=datetime.date(2007,1,1),end_date=datetime.date(2015,1,1))
    erh1.save()
    erh2 = EmployerRoleHistory(employer = e2, role = role1, start_date=datetime.date(2007,1,1),end_date=datetime.date(2015,1,1))
    erh2.save()
    erh3 = EmployerRoleHistory(employer = e3, role = role2, start_date=datetime.date(2007,1,1),end_date=datetime.date(2015,1,1))
    erh3.save()
    erh4 = EmployerRoleHistory(employer = e4, role = role3, start_date=datetime.date(2007,1,1),end_date=datetime.date(2015,1,1))
    erh4.save()

def initp():
    mpt  = MedicalProcedureType(name = 'Грязь на область', order = 1, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(16), capacity = 2, optional='Живота,Головы,Ноги')
    mpt.save()
    mpt1  = MedicalProcedureType(name = 'Подводное вытяжение в минеральной воде', order = 2, duration = 45, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt1.save()
    orders = Order.objects.filter(code = '1266')
    ord = orders[0]
    omp = OrderMedicalProcedure(order = ord, mp_type = mpt, times = 10)
    omp.save()
    omp = OrderMedicalProcedure(order = ord, mp_type = mpt1, times = 5)
    omp.save()
    for i in xrange(2,7):
        omps = OrderMedicalProcedureSchedule(order = ord, mp_type = mpt, p_date = datetime.date(2007,7,i), slot = 2)
        omps.save()
        omps = OrderMedicalProcedureSchedule(order = ord, mp_type = mpt1, p_date = datetime.date(2007,7,i), slot = 4)
        omps.save()
    orders = Order.objects.filter(code = '1267')
    ord = orders[0]
    omp = OrderMedicalProcedure(order = ord, mp_type = mpt, times = 10)
    omp.save()
    for i in xrange(2,7):
        omps = OrderMedicalProcedureSchedule(order = ord, mp_type = mpt, p_date = datetime.date(2007,7,i), slot = 3)
        omps.save()
    orders = Order.objects.filter(code = '1268')
    ord = orders[0]
    omp = OrderMedicalProcedure(order = ord, mp_type = mpt, times = 10)
    omp.save()
    for i in xrange(2,7):
        omps = OrderMedicalProcedureSchedule(order = ord, mp_type = mpt, p_date = datetime.date(2007,7,i), slot = i)
        omps.save()

    mpt  = MedicalProcedureType(name = 'Рапные ванный', order = 3, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Подводный душ массаж', order = 4, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Каменистая дорожка', order = 5, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = '4-х камерная ванна', order = 6, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2, optional = "гальваническая, пневмо и гидро массажа")
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Кислородный коктейль', order = 7, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Массаж ручной', order = 8, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2, optional="спины,ШВЗ,пояснично-кресцовой,грудной области,ног,рук,головы")
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Общая магнитотерапия Калибри', order = 9, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Гирудотерапия', order = 10, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'СУВ', order = 11, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Теплолечение озокерит', order = 12, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Ароматерапия', order = 13, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Лазеротерапия', order = 14, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Ингаляции с ', order = 15, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Аэроионотерапия', order = 16, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Механомассаж', order = 17, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2,optional="Ормед,анатомотор,Терамакс")
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Физиопроцедура на область', order = 18, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2, optional="СМТ,ДДТ,дарсонваль,магнит")
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Физиопроцедура на область', order = 19, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2, optional="УВЧ,э/форез,э/стимуляция,у/звук,КВЧ,трансаир,э/сон")
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Вакуумный массаж на область', order = 20, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Вибромассаж н/к, в/к', order = 21, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Прессотерапия', order = 22, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()
    mpt  = MedicalProcedureType(name = 'Озонотерапия', order = 23, duration = 30, start_time=datetime.time(8), finish_time = datetime.time(17), capacity = 2)
    mpt.save()

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

def getEmployerByRoleAndDate(erole, date):
    roles = EmployerRoleHistory.objects.filter(role=erole,start_date__lte=date,end_date__gte=date)
    print len(roles)
    print connection.queries
    for role in roles:
        return role.employer

def getEmployerByRoleNameAndDate(rolename, date):
    return getEmployerByRoleAndDate(Role.objects.get_or_create(name = rolename)[0], date)
