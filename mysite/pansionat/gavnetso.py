# coding: utf-8
import datetime
from django.db import connection
from mysite.pansionat.models import Patient, Customer, Order, Occupied, Room, RoomType, EmployerRoleHistory, Role, Employer

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
    o1 = Order(room = r1, code = '1266', start_date=datetime.date(2007,7,1),end_date=datetime.date(2007,7,15), patient = p1, customer = c1, directive = c5, price = 12345)
    o1.save()
    o2 = Order(room = r2,code = '1267', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p2, customer = c2, directive = c5, price = 11000)
    o2.save()
    o3 = Order(room = r3, code = '1268', start_date=datetime.date(2007,7,3),end_date=datetime.date(2007,7,15), patient = p3, customer = c3, directive = c6, price = 19000)
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
