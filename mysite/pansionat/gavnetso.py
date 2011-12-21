# coding: utf-8
import datetime
import decimal
import re
from string import lower, upper, strip
from django.db import connection
from django.db.models.query_utils import Q
from xlrd import open_workbook
from mysite import settings
from mysite.pansionat.models import Patient, Customer, Order, Occupied, Room, RoomType, EmployerRoleHistory, Role, Employer, IllHistoryFieldTypeGroup, IllHistoryFieldType, MedicalProcedureType, OrderMedicalProcedure, OrderMedicalProcedureSchedule, RoomBook, Book, Diet, Item, DietItems, OrderDay, MedicalProcedureTypePrice, OrderType, Piece, ItemPiece

def nextmonthfirstday(year, month):
    if month==12:
        newmonth = 1
        newyear = year + 1
    else:
        newmonth = month + 1
        newyear = year
    return datetime.date(int(newyear), int(newmonth), 1)

def initfromfile(filename):
    rb = open_workbook(settings.STATIC_ROOT + '/xls/' + filename,formatting_info=True)
    rsh = rb.sheet_by_index(0)
    for rrowx in xrange(rsh.nrows):
        i = 0
        for col in xrange(rsh.ncols):
            v = rsh.cell_value(rrowx,col)
            print str(rrowx)+":"+str(col)+unicode(v)


def add_lead_zeros(putevka, req_length):
    while len(putevka) < req_length:
        putevka = "0" + putevka
    return putevka


def up_low_case(fios):
    if len(fios)>1:
        return upper(fios[0]) + lower(fios[1:])
    else:
        return upper(fios)

def import_bron(filename):
    rb = open_workbook(settings.STATIC_ROOT + '/xls/' + filename,formatting_info=True)
    rsh = rb.sheet_by_index(0)

    for rrowx in xrange(rsh.nrows):
        v = rsh.cell_value(rrowx, 1)
        if v != "":
            s_date = rsh.cell_value(rrowx,1)
            e_date = rsh.cell_value(rrowx,2)
            s_date = datetime.date(year = 1899, month = 12, day=30)+datetime.timedelta(days=s_date)
            e_date = datetime.date(year = 1899, month = 12, day=30)+datetime.timedelta(days=e_date)
            name = up_low_case(rsh.cell_value(rrowx,7))
            phone = up_low_case(unicode(rsh.cell_value(rrowx,8)))
            description = up_low_case(rsh.cell_value(rrowx,4))
            book = Book(start_date = s_date, end_date = e_date, name = name, phone = phone, description = description)
            book.save()

def import_diets(filename):
    rb = open_workbook(settings.STATIC_ROOT + '/xls/' + filename,formatting_info=True)
    rsh = rb.sheet_by_index(0)

    res = []

    d2  = Diet.objects.filter(name = 'Диета №2 (легкая)')
    diet = d2[0]
    
    last = None
    for rrowx in xrange(rsh.nrows):
        v = rsh.cell_value(rrowx, 0)
        if v != "":
            line = [("Блюдо","")]
            bl_name = rsh.cell_value(rrowx,0)
            bls = Item.objects.filter(name = bl_name)
            line.append((bl_name,""))
            w = rsh.cell_value(rrowx,1)
            line.append((w,""))
            dw = rsh.cell_value(rrowx,2)
            line.append((dw,""))
            pp = rsh.cell_value(rrowx,3)
            line.append((pp,""))
            if not len(bls):
                bl = Item(name = bl_name, weight = float2int(w))
                bl.save()
                last = bl
                di = DietItems(diet = diet, item = bl,day_of_week = float2int(dw), eating = float2int(pp),
                          start_date = datetime.date(2001,1,1), end_date = datetime.date(2020,1,1))
                di.save()
            else:
                last = bls[0]

            res.append(line)
        else:
            line = [("Ингридиент","")]
            it = strip(rsh.cell_value(rrowx,1))
            line.append((it,""))
            w = rsh.cell_value(rrowx,2)
            line.append((w,""))
            ps = Piece.objects.filter(name = it)
            if not len(ps):
                p = Piece(name = it)
                p.save()
            else:
                p = ps[0]
            ip = ItemPiece(item = last, piece = p,weight = float2int(w))
            ip.save()
            res.append(line)
    return res

def import_proc():
    rb = open_workbook(settings.STATIC_ROOT + '/xls/mproc.xls',formatting_info=True)
    rsh = rb.sheet_by_index(0)

    for rrowx in xrange(rsh.nrows):
        v = rsh.cell_value(rrowx, 0)
        name = v
        price = rsh.cell_value(rrowx,1)
        pra = price.split('-')
        if len(pra)>1:
            price = decimal.Decimal(pra[0]+'.'+pra[1])
        else:
            price = decimal.Decimal(pra[0])
        add_info = rsh.cell_value(rrowx,2)
        mpts = MedicalProcedureType.objects.filter(name = name)
        if not len(mpts):
            mpt = MedicalProcedureType(name = name, order = 0, capacity = 1, duration =30,
                                   start_time = datetime.time(hour = 8, minute = 30),
                                   finish_time = datetime.time(hour = 17, minute = 30),
                                   optional = add_info)
        else:
            mpt = mpts[0]
            mpt.optional += ','+add_info
        mpt.save()
        mpts = MedicalProcedureTypePrice(mpt = mpt, price = price, date_applied = datetime.date(year=2010,month=12,day=31),add_info=add_info)
        mpts.save()

def import_ordertypes():
    ots = OrderType.objects.all()
    if not len(ots):
        ot = OrderType(name = 'Ульяновск проф',price = 0)
        ot.save()
        ot = OrderType(name = 'Самара проф',price = 35154)
        ot.save()
        ot = OrderType(name = 'Пенза проф',price = 0)
        ot.save()
        ot = OrderType(name = 'Пенза фсс',price = 14850)
        ot.save()
        ot = OrderType(name = 'Реабилитация',price = '21607.92')
        ot.save()
        ot = OrderType(name = 'Наличка',price = 0)
        ot.save()
        ot = OrderType(name = 'Командировочные',price = 0)
        ot.save()

def float2int(strdata):
    arr = str(strdata).split(".")
    if len(arr)>1:
        strdata = arr[0]
    return int(strdata)

def test_file(filename, flag):
    rb = open_workbook(filename,formatting_info=True)
    rsh = rb.sheet_by_index(0)

    res = []

    order_type = None
    order_type_r = OrderType.objects.filter(name = 'Реабилитация')[0]

    for rrowx in xrange(rsh.nrows):
        if rrowx>4:
            data = rsh.cell_value(rrowx,1)
            row_info = []
            strdata = unicode(data)
            if strdata!="":
                #matchObj = re.match( '([0-9]*)[\.0]?$', strdata, flags = 0)
                do_import = True
                r = False
                strdata = strip(strdata)
                if not strdata[0] in ('0','1','2','3'):
                    r = True
                    order_type = order_type_r
                    strdata = strdata[1:]
                arr = strdata.split(".")
                if len(arr)>1:
                    strdata = strip(arr[0])
                os = Order.objects.filter(code = int(strdata))
                duplicated = False
                if not len(os):
                    row_info.append((int(strdata),""))
                else:
                    do_import = False
                    duplicated = True
                    row_info.append((int(strdata),"duplicated"))
                v = rsh.cell_value(rrowx,2)
                start_date = datetime.date(year = 1899, month = 12, day=30)+datetime.timedelta(days=v)
                if not duplicated or os[0].start_date!=start_date:
                    row_info.append((start_date,""))
                else:
                    row_info.append(("",""))
                v = rsh.cell_value(rrowx,3)
                end_date = datetime.date(year = 1899, month = 12, day=30)+datetime.timedelta(days=v)
                if not duplicated or os[0].end_date!=end_date:
                    row_info.append((end_date,""))
                else:
                    row_info.append(("",""))
                putevka = rsh.cell_value(rrowx,4)
                putevkas = str(putevka).split('.')
                if len(putevkas)>1:
                    putevka = putevkas[0]
                putevka = add_lead_zeros(putevka, 6)
                if not duplicated or os[0].putevka!=putevka:
                    row_info.append((putevka,""))
                else:
                    row_info.append(("",""))
                v = rsh.cell_value(rrowx,5)
                fios = v.split(" ")
                family = up_low_case(fios[0])
                name = up_low_case(fios[1])
                if len(fios)>2:
                    sname = up_low_case(fios[2])
                else:
                    sname = ""
                if not duplicated or os[0].patient.family!=family:
                    row_info.append((family,""))
                else:
                    row_info.append(("",""))
                if not duplicated or os[0].patient.name!=name:
                    row_info.append((name,""))
                else:
                    row_info.append(("",""))
                if not duplicated or os[0].patient.sname!=sname:
                    row_info.append((sname,""))
                else:
                    row_info.append(("",""))
                grade = rsh.cell_value(rrowx,6)
                v = rsh.cell_value(rrowx,7)
                cs = Customer.objects.filter(Q(name = v,shortname = v))
                if len(cs)>0:
                    if not duplicated or os[0].directive.name!=v:
                        row_info.append((v,""))
                    else:
                        row_info.append(("",""))
                    directive = cs[0]
                else:
#                    do_import = False
                    if flag:
                        customer = Customer(name = v,shortname =v)
                        customer.save()
                    row_info.append((v,"Клиент не найден"))
                v = rsh.cell_value(rrowx,8)
                if v=="-" or v==u"нет":
                    price=0
                else:
                    pr = str(v)
                    prs = pr.split(',')
                    if len(prs)>1:
                        pr = prs[0]+'.'+prs[1]
                    if not len(str(pr)):
                        pr = 0
                    price = decimal.Decimal(pr)
                if not duplicated or os[0].price!=price:
                    row_info.append((price,""))
                    if duplicated and do_import:
                        os[0].price = price
                        os[0].save()
                else:
                    row_info.append(("",""))
#                v = rsh.cell_value(rrowx,9)
#                s_date = datetime.date(year = 1899, month = 12, day=30)+datetime.timedelta(days=v)
#                row_info.append((s_date,""))
                v = rsh.cell_value(rrowx,10)
                cs = Customer.objects.filter(Q(name = v,shortname = v))
                if len(cs)>0:
                    if not duplicated or os[0].customer.name!=v:
                        row_info.append((v,""))
                    else:
                        row_info.append(("",""))
                    customer = cs[0]
                else:
                    #do_import = False
                    if flag:
                        customer = Customer(name = v,shortname =v)
                        customer.save()
                    row_info.append((v,"Клиент не найден"))
                v = rsh.cell_value(rrowx,11)
                if v!='':
                    try:
                        birth_date = datetime.date(year = 1899, month = 12, day=30)+datetime.timedelta(days=v)
                        row_info.append((birth_date,""))
                    except TypeError:
                        birth_date = None
                        row_info.append((birth_date,"Incorrect date format!"))
                else:
                    birth_date = None
                    row_info.append((birth_date,""))
                address = rsh.cell_value(rrowx,13)
                v = rsh.cell_value(rrowx,12)
                s1 = v[:12]
                s2 = v[13:]
                if s1!="":
                    ps = Patient.objects.filter(passport_number = s1)
                    if len(os)>0:
                        if os[0].patient.passport_number!=s1:
                            row_info.append((os[0].patient.passport_number,"Несоответствие заказов!!!"))
                else:
                    ps = Patient.objects.filter(family = family, name = name, sname = sname)
                if len(ps)>0:
                    row_info.append((s1,"Пациент найден"))
                    patient = ps[0]
                    if not duplicated or patient.address!=address:
                        row_info.append((address,""))
                    else:
                        row_info.append(("",""))
                    if not duplicated or patient.grade!=grade:
                        row_info.append((grade,""))
                    else:
                        row_info.append(("",""))
                else:
                    row_info.append((s1,"Пациент не найден"))
                    if flag:
                        if s1=="":
                            s1 = family+name
                        patient = Patient(family = family,
                                          name = name,
                                          sname = sname,
                                          birth_date = birth_date,
                                          grade = grade,
                                          profession = grade,
                                          passport_number = s1,
                                          passport_whom = s2,
                                          address = address
                        )
                        patient.save()
                    row_info.append((grade,""))
                    row_info.append((address,""))
                row_info.append((s2,""))
                v = rsh.cell_value(rrowx,14)
                v = upper(v)
                rooms = Room.objects.filter(name = v)
                if len(rooms)>0:
                    if not duplicated or os[0].room.name!=v:
                        row_info.append((v,""))
                    else:
                        row_info.append(("",""))
                    room = rooms[0]
                else:
                    do_import = False
                    row_info.append((v,"Комната не найден"))
                res.append(row_info)
                if flag and do_import:
                    order = Order(
                        code = int(strdata),
                        putevka = putevka,
                        patient = patient,
                        customer = customer,
                        room = room,
                        directive = directive,
                        start_date = start_date,
                        end_date = end_date,
                        price = price,
                        is_with_child = False,
                        payd_by_patient = False,
                        reab = r,
                        order_type = order_type
                    )
                    order.save()
                    fillOrderDays(order)

    return res

#        if v != "":
#            n = rsh.cell_value(rrowx,columns["n2"])
#            ns = unicode(n).split(" ")
#            reab = False
#            if len(ns)>1:
#                n = ns[0]
#                if ns[1]=="Р":
#                    reab = True
#            code = int(n)
#            putevka = str(rsh.cell_value(rrowx,columns["put"]))
#            putevkas = putevka.split('.')
#            if len(putevkas)>1:
#                putevka = putevkas[0]
#            putevka = add_lead_zeros(putevka, 6)
#            rhi = mc_map.get(rrowx,rrowx)
#            pdall = unicode(rsh.cell_value(rrowx,columns["pd"]))
#            cr = rrowx
#            while cr<rhi-1:
#                cr +=1
#                pdall = pdall + " "+unicode(rsh.cell_value(cr,columns["pd"]))
#            pdd = pdall.split(" ")
#            try:
#                pd0 = str(int(round(float(pdd[0]))))
#                pd1 = str(int(round(float(pdd[1]))))
#                pd2 = str(int(round(float(pdd[2]))))
#                q = True
#            except UnicodeEncodeError:
#                q = False
#
#            if q:
#                pd0 = add_lead_zeros(pd0, 2)
#                pd1 = add_lead_zeros(pd1, 2)
#                pd2 = add_lead_zeros(pd2, 6)
#                pn = pd0+" "+pd1+" "+pd2
#                cnt = 3
#                pv = pdd[cnt]
#                while cnt<len(pdd)-1:
#                    cnt += 1
#                    pv = pv + " "+ pdd[cnt]
#                fio = rsh.cell_value(rrowx,columns["fio"])
#                cr = rrowx
#                while cr<rhi-1:
#                    cr +=1
#                    fio = fio + " "+unicode(rsh.cell_value(cr,columns["fio"]))
#                fios = fio.split(" ")
#                if len(fios)==3:
#                    family,name, sname = fio.split(" ")
#                else:
#                    family = up_low_case(fios[0])
#                    name = up_low_case(fios[1])
#                    sname = up_low_case(fios[2])
#                objs = Patient.objects.filter(passport_number = pn)
#                if len(objs)>0:
#                    p = objs[0]
#                else:
#                    p = Patient(family = family,name = name, sname = sname, passport_number = pn, passport_whom = pv)
#                    p.save()
#                c_name = rsh.cell_value(rrowx,columns["c"])
#                objs = Customer.objects.filter(name = c_name)
#                if len(objs)>0:
#                    cust = objs[0]
#                else:
#                    cust = Customer(name=c_name, shortname = c_name)
#                    cust.save()
#                roomname = rsh.cell_value(rrowx,columns["room"])
#                objs = Room.objects.filter(name = roomname)
#                if len(objs)>0:
#                    room = objs[0]
#                else:
#                    #print unicode(rrowx)+":"+unicode(roomname)
#                    room = Room(name=roomname, room_type = rt1)
#                    room.save()
#                dirname = rsh.cell_value(rrowx,columns["cv"])
#                objs = Customer.objects.filter(shortname = dirname)
#                if len(objs)>0:
#                    dir = objs[0]
#                else:
#                    dir = Customer(name=dirname, shortname = dirname)
#                    dir.save()
#
#                dts = unicode(rsh.cell_value(rrowx,columns["d1"]))
#                cr = rrowx
#                while cr<rhi-1:
#                    cr +=1
#                    dts = dts + " "+unicode(rsh.cell_value(cr,columns["d1"]))
#                dtss = dts.split(" ")
#
#                dts = dtss[0].split(".")
#                dtf = dtss[2].split(".")
#                start_date = datetime.date(day=int(dts[0]),month=int(dts[1]),year=2011)
#                end_date = datetime.date(day=int(dtf[0]),month=int(dtf[1]),year=2011)
#                pr = str(rsh.cell_value(rrowx,columns["price"]))
#                prs = pr.split(',')
#                if len(prs)>1:
#                    pr = prs[0]+'.'+prs[1]
#                if not len(str(pr)):
#                    pr = 0
#                price = decimal.Decimal(pr)
#                order = Order(code = code, putevka = putevka, patient = p, customer = cust,
#                              room = room, directive = dir, start_date = start_date, end_date = end_date,
#                              price = price, reab = reab)
#                order.save()
#                fillOrderDays(order)
                # TODO WTF is_with_child = models.BooleanField(verbose_name = 'Мать и дитя')
                # TODO WTF payd_by_patient = models.BooleanField(verbose_name = 'Оплачивается пациентом')

def import_rooms():
    rb = open_workbook(settings.STATIC_ROOT + '/xls/rooms.xls',formatting_info=True)
    rsh = rb.sheet_by_index(0)

    for rrowx in xrange(rsh.nrows):
        v = rsh.cell_value(rrowx, 0)
        name = upper(unicode(v))
        t_name = rsh.cell_value(rrowx, 1).capitalize()
        price_s = rsh.cell_value(rrowx,2)
        price = decimal.Decimal(str(price_s))
        places = int(rsh.cell_value(rrowx,3))

        roomtypes = RoomType.objects.filter(name = t_name)
        if not len(roomtypes):
            rt = RoomType(name = t_name, places = places, price = price, price_alone = price)
            rt.save()
        else:
            rt = roomtypes[0]
        room = Room(name = name, room_type = rt)
        room.save()

def inithistory(filename, input_columns, row_set):
    rt1 = RoomType(name = 'Двухместный номер блочный повышенной комфортности',
                   description = 'телевизор, холодильник, душевая кабина, кондиционер',
                   places = 2, price = 1310, price_alone = 2120)
    rt1.save()
    rb = open_workbook(settings.STATIC_ROOT + '/xls/' + filename,formatting_info=True)
    rsh = rb.sheet_by_index(0)

    mc_map = {}
    for crange in rsh.merged_cells:
        rlo, rhi, clo, chi = crange
        if not clo:
            mc_map[rlo] = rhi

    columns = input_columns[0]

    for rrowx in xrange(rsh.nrows):
        if rrowx in row_set:
            columns = input_columns[1]
        v = rsh.cell_value(rrowx,columns["n1"])
        if v != "":
            n = rsh.cell_value(rrowx,columns["n2"])
            ns = unicode(n).split(" ")
            reab = False
            if len(ns)>1:
                n = ns[0]
                if ns[1]=="Р":
                    reab = True
            code = int(n)
            putevka = str(rsh.cell_value(rrowx,columns["put"]))
            putevkas = putevka.split('.')
            if len(putevkas)>1:
                putevka = putevkas[0]
            putevka = add_lead_zeros(putevka, 6)
            rhi = mc_map.get(rrowx,rrowx)
            pdall = unicode(rsh.cell_value(rrowx,columns["pd"]))
            cr = rrowx
            while cr<rhi-1:
                cr +=1
                pdall = pdall + " "+unicode(rsh.cell_value(cr,columns["pd"]))
            pdd = pdall.split(" ")
            try:
                pd0 = str(int(round(float(pdd[0]))))
                pd1 = str(int(round(float(pdd[1]))))
                pd2 = str(int(round(float(pdd[2]))))
                q = True
            except UnicodeEncodeError:
                q = False

            if q:
                pd0 = add_lead_zeros(pd0, 2)
                pd1 = add_lead_zeros(pd1, 2)
                pd2 = add_lead_zeros(pd2, 6)
                pn = pd0+" "+pd1+" "+pd2
                cnt = 3
                pv = pdd[cnt]
                while cnt<len(pdd)-1:
                    cnt += 1
                    pv = pv + " "+ pdd[cnt]
                fio = rsh.cell_value(rrowx,columns["fio"])
                cr = rrowx
                while cr<rhi-1:
                    cr +=1
                    fio = fio + " "+unicode(rsh.cell_value(cr,columns["fio"]))
                fios = fio.split(" ")
                if len(fios)==3:
                    family,name, sname = fio.split(" ")
                else:
                    family = up_low_case(fios[0])
                    name = up_low_case(fios[1])
                    sname = up_low_case(fios[2])
                objs = Patient.objects.filter(passport_number = pn)
                if len(objs)>0:
                    p = objs[0]
                else:
                    p = Patient(family = family,name = name, sname = sname, passport_number = pn, passport_whom = pv)
                    p.save()
                c_name = rsh.cell_value(rrowx,columns["c"])
                objs = Customer.objects.filter(name = c_name)
                if len(objs)>0:
                    cust = objs[0]
                else:
                    cust = Customer(name=c_name, shortname = c_name)
                    cust.save()
                roomname = rsh.cell_value(rrowx,columns["room"])
                objs = Room.objects.filter(name = roomname)
                if len(objs)>0:
                    room = objs[0]
                else:
                    #print unicode(rrowx)+":"+unicode(roomname)
                    room = Room(name=roomname, room_type = rt1)
                    room.save()
                dirname = rsh.cell_value(rrowx,columns["cv"])
                objs = Customer.objects.filter(shortname = dirname)
                if len(objs)>0:
                    dir = objs[0]
                else:
                    dir = Customer(name=dirname, shortname = dirname)
                    dir.save()

                dts = unicode(rsh.cell_value(rrowx,columns["d1"]))
                cr = rrowx
                while cr<rhi-1:
                    cr +=1
                    dts = dts + " "+unicode(rsh.cell_value(cr,columns["d1"]))
                dtss = dts.split(" ")

                dts = dtss[0].split(".")
                dtf = dtss[2].split(".")
                start_date = datetime.date(day=int(dts[0]),month=int(dts[1]),year=2011)
                end_date = datetime.date(day=int(dtf[0]),month=int(dtf[1]),year=2011)
                pr = str(rsh.cell_value(rrowx,columns["price"]))
                prs = pr.split(',')
                if len(prs)>1:
                    pr = prs[0]+'.'+prs[1]
                if not len(str(pr)):
                    pr = 0
                price = decimal.Decimal(pr)
                order = Order(code = code, putevka = putevka, patient = p, customer = cust,
                              room = room, directive = dir, start_date = start_date, end_date = end_date,
                              price = price, reab = reab)
                order.save()
                fillOrderDays(order)
                # TODO WTF is_with_child = models.BooleanField(verbose_name = 'Мать и дитя')
                # TODO WTF payd_by_patient = models.BooleanField(verbose_name = 'Оплачивается пациентом')


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

    ihft1 = IllHistoryFieldType(description = 'С каким диагнозом прибыл', lines = 3, defval ='',
                                order = 0, group = ihftg1)
    ihft1.save()
    ihft2 = IllHistoryFieldType(description = 'Диагноз санатория, а) основной', lines = 3, defval ='',
                                order = 1, group = ihftg1)
    ihft2.save()
    ihft3 = IllHistoryFieldType(description = 'б) сопутствующего заболевания', lines = 3, defval ='',
                                order = 2, group = ihftg1)
    ihft3.save()
    ihft4 = IllHistoryFieldType(description = 'Условия труда и быта больного', lines = 6, defval ='',
                                order = 3, group = ihftg1)
    ihft4.save()
    ihft5 = IllHistoryFieldType(description = 'Жалобы больного', lines = 8, defval ='',
                                order = 4, group = ihftg1)
    ihft5.save()
    ihft6 = IllHistoryFieldType(description = 'Общий анамнез', lines = 5, defval ='',
                                order = 5, group = ihftg1)
    ihft6.save()
    ihft7 = IllHistoryFieldType(description = 'Начало и развитие настоящего заболевания', lines = 5, defval ='',
                                order = 6, group = ihftg1)
    ihft7.save()

    ihft = IllHistoryFieldType(description = 'Состояние удовлетворительное', lines = 1, defval ='',
                               order = 0, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Телосложение', lines = 1, defval ='правильное,неправильное',
                               order = 1, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = '', lines = 1, defval ='Астеник, нормастеник, гиперстеник',
                               order = 2, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Питание', lines = 1, defval ='удовлетворительное, повышенное, пониженное',
                               order = 3, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Кожные покровы', lines = 2, defval ='нормальной окраски, бледные, гиперемированы, желтушные',
                               order = 4, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Щитовидная железа', lines = 1, defval ='увеличена, не увеличена',
                               order = 5, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Региональные лимфатические железы-шейные, подмышечные, паховые', lines = 3, defval ='не увеличены, увеличены, мягкие, уплотненные',
                               order = 6, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'при пальпации', lines = 1, defval ='безболезненные, болезненные',
                               order = 7, group = ihftg2)
    ihft.save()
    ihft = IllHistoryFieldType(description = 'Косто-мышечная система', lines = 1, defval ='без видимых изменений',
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
    p5 = Patient(family = 'Хуртин',name = 'Олег', sname = 'Ольгович',
                 birth_date=datetime.date(1963,2,15),grade='Программист',
                 passport_whom = 'ОВД ШЕМЫШЕЙКА',passport_number='56 07 736142',
                 address = 'ШЕМЫШ.Р-Н С.МАЧКАССЫ УЛ.МОЛОДЕЖНАЯ 5. 28-1-34Д.Т.')
    p5.save()
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
    o1 = Order(room = r, code = '1290', start_date=datetime.date(2011,10,18),end_date=datetime.date(2011,10,24), patient = p1, customer = c1, directive = c5, price = 12345)
    o1.save()
    fillOrderDays(o1)
    r = Room.objects.get(name = '12А')
    o1 = Order(room = r, code = '1291', start_date=datetime.date(2011,10,18),end_date=datetime.date(2011,10,31), patient = p2, customer = c2, directive = c5, price = 12000)
    o1.save()
    fillOrderDays(o1)
    r = Room.objects.get(name = '12Б')
    for i in xrange(18,25):
        o1 = Order(room = r, code = '1292'+str(i), start_date=datetime.date(2011,10,i),end_date=datetime.date(2011,10,i), patient = p3, customer = c1, directive = c5, price = 15000)
        o1.save()
        fillOrderDays(o1)
    r = Room.objects.get(name = '14А')
    o1 = Order(room = r, code = '1515', start_date=datetime.date(2011,10,18),end_date=datetime.date(2011,10,24), patient = p5, customer = c1, directive = c5, price = 15000, is_with_child = True)
    o1.save()
    fillOrderDays(o1)
    book = Book(start_date=datetime.date(2011,10,18),end_date=datetime.date(2011,10,24),name='Аяцков',phone='5551234',description='вряд ли')
    book.save()
    r = Room.objects.get(name = '13Б')
    fillBookDays(book, r)
    r1 = Room.objects.get(name = '1СК')
    r2 = Room.objects.get(name = '1Д')
    r3 = Room.objects.get(name = '33Б')
    r4 = Room.objects.get(name = '2Д')
    o1 = Order(room = r1, code = '1266', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p1, customer = c1, directive = c5, price = 12345)
    o1.save()
    fillOrderDays(o1)
    o2 = Order(room = r2,code = '1267', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p2, customer = c2, directive = c5, price = 11000)
    o2.save()
    fillOrderDays(o2)
    o3 = Order(room = r3, code = '1268', start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), patient = p3, customer = c3, directive = c6, price = 19000)
    o3.save()
    fillOrderDays(o3)
    o4 = Order(room = r4, code = '1269', start_date=datetime.date(2007,7,4),end_date=datetime.date(2007,7,15), patient = p4, customer = c4, directive = c6, price = 12000)
    o4.save()
    fillOrderDays(o4)
    oc1 = Occupied(order = o1, room = r1, start_date=datetime.date(2007,7,1),end_date=datetime.date(2007,7,15), description = 'первый')
    oc1.save()
    oc2 = Occupied(order = o2, room = r2, start_date=datetime.date(2007,7,2),end_date=datetime.date(2007,7,15), description = 'второй')
    oc2.save()
    oc3 = Occupied(order = o3, room = r3, start_date=datetime.date(2007,7,3),end_date=datetime.date(2007,7,15), description = 'третий')
    oc3.save()
    oc4 = Occupied(order = o4, room = r4, start_date=datetime.date(2007,7,4),end_date=datetime.date(2007,7,15), description = 'четвертый')
    oc4.save()

def initroomtypes():
    rt1 = RoomType(name = 'Двухместный номер блочный повышенной комфортности',
                   description = 'телевизор, холодильник, душевая кабина, кондиционер',
                   places = 2, price = 1310, price_alone = 2120)
    rt1.save()
    rt2 = RoomType(name = 'Двухместный номер стандартный',
                   description = 'телевизор, холодильник',
                   places = 2, price = 1370, price_alone = 2230)
    rt2.save()
    rt3 = RoomType(name = 'Двухместный номер 1 категории',
                   description = 'телевизор, холодильник, душевая кабина',
                   places = 2, price = 1580, price_alone = 2650)
    rt3.save()
    rt4 = RoomType(name = 'Двухместный номер повышенной комфортности',
                   description = 'телевизор, холодильник, кондиционер',
                   places = 2, price = 1730, price_alone = 2960)
    rt4.save()
    rt5 = RoomType(name = 'Двухкомнатный номер «Люкс»',
                   description = 'телевизор, холодильник, душевая кабина, кондиционер',
                   places = 2, price = 2000, price_alone = 4000)
    rt5.save()
    rt6 = RoomType(name = 'Двухкомнатный номер «Люкс»',
                   description = 'телевизор, холодильник, душевая кабина',
                   places = 2, price = 1750, price_alone = 3500)
    rt6.save()
    rt7 = RoomType(name = 'Домики (двухместный номер)',
                   description = 'телевизор, холодильник',
                   places = 2, price = 1050, price_alone = 1600)
    rt7.save()
    rt7 = RoomType(name = 'Домики (трехместный номер)',
                   description = 'телевизор, холодильник',
                   places = 3, price = 950, price_alone = 0)
    rt7.save()
    rt1list = ['1СК','12А','12Б','13А','13Б','14А','14Б',
               '15А','15Б','16','17А','17Б',
               '19А','19Б','20А','20Б','21А','21Б',
               '22А','22Б','23А','23Б','24А','24Б',
               '25А','25Б','26А','26Б','27А','27Б',
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

def fillOrderDays(order):
    date = order.start_date
    delta = datetime.timedelta(days=1)
    while date<= order.end_date:
        orderDay = OrderDay(order = order, busydate = date, room = order.room)
        orderDay.save()
        date += delta

def fillBookDays(book, room):
    date = book.start_date
    delta = datetime.timedelta(days=1)
    while date<= book.end_date:
        orderDay = OrderDay(book = book, busydate = date, room = room)
        orderDay.save()
        date += delta

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

def initdiet():
    d1  = Diet(name = 'Диета №1 (вегетерианская)')
    d1.save()
    d2  = Diet(name = 'Диета №2 (легкая)')
    d2.save()
    d3  = Diet(name = 'Диета №3 (питательная)')
    d3.save()
    i1 = Item(name = 'Рис с овощами',weight = 100)
    i1.save()
    i2 = Item(name = 'Макароны по флотски',weight = 100)
    i2.save()
    i3 = Item(name = 'Спагетти с сосиской',weight = 100)
    i3.save()
    i4 = Item(name = 'Суп грибной',weight = 100)
    i4.save()
    i5 = Item(name = 'Лапша куриная',weight = 100)
    i5.save()
    i6 = Item(name = 'Щи',weight = 100)
    i6.save()
    di = DietItems(diet = d1, item = i1,day_of_week=2,eating = 1, start_date = datetime.date(2007,7,1), end_date = datetime.date(2015,7,1))
    di.save()
    di = DietItems(diet = d2, item = i2,day_of_week=2,eating = 1, start_date = datetime.date(2007,7,1), end_date = datetime.date(2015,7,1))
    di.save()
    di = DietItems(diet = d3, item = i3,day_of_week=2,eating = 1, start_date = datetime.date(2007,7,1), end_date = datetime.date(2015,7,1))
    di.save()
    di = DietItems(diet = d1, item = i4,day_of_week=2,eating = 1, start_date = datetime.date(2007,7,1), end_date = datetime.date(2015,7,1))
    di.save()
    di = DietItems(diet = d2, item = i5,day_of_week=2,eating = 1, start_date = datetime.date(2007,7,1), end_date = datetime.date(2015,7,1))
    di.save()
    di = DietItems(diet = d3, item = i6,day_of_week=2,eating = 1, start_date = datetime.date(2007,7,1), end_date = datetime.date(2015,7,1))
    di.save()

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
