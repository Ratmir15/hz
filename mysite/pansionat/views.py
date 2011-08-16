# Create your views here.
# coding: utf-8
from datetime import date
import datetime
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
from django_excel_templates import *
from xlutils.copy import copy
from xlrd import open_workbook
import re
import logging
from xlwt import *
from mysite.pansionat.models import Order, Customer, Occupied
import datetime
from django import forms
from django.core.context_processors import csrf
from django.db.models import Q

from django.db import connection


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

import xlwt

def get_xlwt_style_list(rdbook):
    wt_style_list = []
    for rdxf in rdbook.xf_list:
        wtxf = xlwt.Style.XFStyle()
        #
        # number format
        #
        wtxf.num_format_str = rdbook.format_map[rdxf.format_key].format_str
        #
        # font
        #
        wtf = wtxf.font
        rdf = rdbook.font_list[rdxf.font_index]
        wtf.height = rdf.height
        wtf.italic = rdf.italic
        wtf.struck_out = rdf.struck_out
        wtf.outline = rdf.outline
        wtf.shadow = rdf.outline
        wtf.colour_index = rdf.colour_index
        wtf.bold = rdf.bold #### This attribute is redundant, should be driven by weight
        wtf._weight = rdf.weight #### Why "private"?
        wtf.escapement = rdf.escapement
        wtf.underline = rdf.underline_type ####
        # wtf.???? = rdf.underline #### redundant attribute, set on the fly when writing
        wtf.family = rdf.family
        wtf.charset = rdf.character_set
        wtf.name = rdf.name
        #
        # protection
        #
        wtp = wtxf.protection
        rdp = rdxf.protection
        wtp.cell_locked = rdp.cell_locked
        wtp.formula_hidden = rdp.formula_hidden
        #
        # border(s) (rename ????)
        #
        wtb = wtxf.borders
        rdb = rdxf.border
        wtb.left   = rdb.left_line_style
        wtb.right  = rdb.right_line_style
        wtb.top    = rdb.top_line_style
        wtb.bottom = rdb.bottom_line_style
        wtb.diag   = rdb.diag_line_style
        wtb.left_colour   = rdb.left_colour_index
        wtb.right_colour  = rdb.right_colour_index
        wtb.top_colour    = rdb.top_colour_index
        wtb.bottom_colour = rdb.bottom_colour_index
        wtb.diag_colour   = rdb.diag_colour_index
        wtb.need_diag1 = rdb.diag_down
        wtb.need_diag2 = rdb.diag_up
        #
        # background / pattern (rename???)
        #
        wtpat = wtxf.pattern
        rdbg = rdxf.background
        wtpat.pattern = rdbg.fill_pattern
        wtpat.pattern_fore_colour = rdbg.pattern_colour_index
        wtpat.pattern_back_colour = rdbg.background_colour_index
        #
        # alignment
        #
        wta = wtxf.alignment
        rda = rdxf.alignment
        wta.horz = rda.hor_align
        wta.vert = rda.vert_align
        wta.dire = rda.text_direction
        # wta.orie # orientation doesn't occur in BIFF8! Superceded by rotation ("rota").
        wta.rota = rda.rotation
        wta.wrap = rda.text_wrapped
        wta.shri = rda.shrink_to_fit
        wta.inde = rda.indent_level
        # wta.merg = ????
        #
        wt_style_list.append(wtxf)
    return wt_style_list


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

#def bookit(request):
#    room_list = Room.objects.all()
#    now = datetime.datetime.now()
#    book_list= [(room, room.occupied_set.filter(start_date__gte = now))
#                for room in room_list]
#
#    print book_list
#    print connection.queries
#    return render_to_response('pansionat/bookit.html', {'book_list': book_list})

def write_and_clone_cell(wtsheet, merged_cell_top_left_map, value, style, rdrowx, rdcolx, wtrowx, wtcolx,nrows_to_clone):
    if nrows_to_clone > 1:
        #print 'Клонирование ячейки '+str(rdrowx)+'/'+str(rdcolx)+'/'+str(wtrowx)+'/'+str(wtcolx)+':'+str(nrows_to_clone)
        for j in xrange(nrows_to_clone):
            write_cell(wtsheet, merged_cell_top_left_map, value, style, rdrowx, rdcolx, wtrowx + j, wtcolx)
    else:
        write_cell(wtsheet, merged_cell_top_left_map, value, style, rdrowx, rdcolx, wtrowx, wtcolx)

def write_cell(wtsheet, merged_cell_top_left_map, value, style, rdrowx, rdcolx, wtrowx, wtcolx):
    rdcoords2d = (rdrowx, rdcolx)
    if rdcoords2d in merged_cell_top_left_map:
    # The cell is the governing cell of a group of
    # merged cells.
        rlo, rhi, clo, chi = merged_cell_top_left_map[rdcoords2d]
        wtsheet.write_merge(
            wtrowx, wtrowx + rhi - rlo - 1,
            wtcolx, wtcolx + chi - clo - 1,
            value, style)
    else:
        wtsheet.write(wtrowx, wtcolx, value, style)

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
    sd = datetime.date(intyear , intmonth , 1)
    fd = nextmonthfirstday(intyear, intmonth)
    print intyear
    print intmonth
    occupieds = Occupied.objects.filter(start_date__year=intyear, start_date__month=intmonth)
    template_filename = '/Users/rpanov/Downloads/registrydiary.xls'
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
    template_filename = '/Users/rpanov/Downloads/moves.xls'
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
    template_filename = '/Users/rpanov/Downloads/tov_nakl1.xls'
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
    template_filename = '/Users/rpanov/Downloads/prih_order1.xls'
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
    template_filename = '/Users/rpanov/Downloads/zayava.xls'
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
    template_filename = '/Users/rpanov/Downloads/sch_fakt1.xls'
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
    #       {'ROWINDEX':1,'NAME':'TOVAR1','QTY':1,'PRICE':order.price,'AMOUNT':order.price,
    #                 'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':order.price}]}
    return fill_excel_template(template_filename, tel)

def xt(request):
    tel = {'PIZDEZ': 'HZ', 'NUMBER': 1236, 'DATE':'26.07.11', 'QTYSUM':3, 'AMOUNTSUM':17810, 'AMOUNTNDSSUM':17810, 'ALLAMOUNTSUM':17810,
           'TOVAR': [{'ROWINDEX':1,'NAME':'TOVAR1','QTY':1,'PRICE':17810,'AMOUNT':17810,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':17810},
                   {'ROWINDEX':2,'NAME':'TOVAR2','QTY':2,'PRICE':17810,'AMOUNT':17810,
                      'PNDS':0,'AMOUNTNDS':'-','ALLAMOUNT':17810}]}
    template_filename = '/Users/rpanov/Downloads/tov_nakl1.xls'
    return fill_excel_template(template_filename, tel)

def fill_excel_template(template_filename, tel):
    rb = open_workbook(template_filename,formatting_info=True)
    rsh = rb.sheet_by_index(0)
    w = xlwt.Workbook(encoding="utf-8", style_compression=2)
    wtsheet = w.add_sheet('Shit', cell_overwrite_ok=True)
    rdsheet = rsh
    #
    # MERGEDCELLS
    #
    mc_map = {}
    mc_nfa = set()
    for crange in rdsheet.merged_cells:
        rlo, rhi, clo, chi = crange
        mc_map[(rlo, clo)] = crange
        for rowx in xrange(rlo, rhi):
            for colx in xrange(clo, chi):
                mc_nfa.add((rowx, colx))

    #self.merged_cell_top_left_map = mc_map
    #self.merged_cell_already_set = mc_nfa
    if not rdsheet.formatting_info:
        return
    #
    # default column width: STANDARDWIDTH, DEFCOLWIDTH
    #
    if rdsheet.standardwidth is not None:
        # STANDARDWIDTH is expressed in units of 1/256 of a
        # character-width, but DEFCOLWIDTH is expressed in units of
        # character-width; we lose precision by rounding to
        # the higher whole number of characters.
        #### XXXX TODO: implement STANDARDWIDTH record in xlwt.
        wtsheet.col_default_width = \
            (rdsheet.standardwidth + 255) // 256
    elif rdsheet.defcolwidth is not None:
        wtsheet.col_default_width = rdsheet.defcolwidth
    #
    # WINDOW2
    #
    wtsheet.show_formulas = rdsheet.show_formulas
    wtsheet.show_grid = rdsheet.show_grid_lines
    wtsheet.show_headers = rdsheet.show_sheet_headers
    wtsheet.panes_frozen = rdsheet.panes_are_frozen
    wtsheet.show_zero_values = rdsheet.show_zero_values
    wtsheet.auto_colour_grid = rdsheet.automatic_grid_line_colour
    wtsheet.cols_right_to_left = rdsheet.columns_from_right_to_left
    wtsheet.show_outline = rdsheet.show_outline_symbols
    wtsheet.remove_splits = rdsheet.remove_splits_if_pane_freeze_is_removed
    wtsheet.selected = rdsheet.sheet_selected
    # xlrd doesn't read WINDOW1 records, so we have to make a best
    # guess at which the active sheet should be:
    # (at a guess, only one sheet should be marked as visible)
   # if not self.sheet_visible and rdsheet.sheet_visible:
   #     self.wtbook.active_sheet = self.wtsheet_index
    wtsheet.sheet_visible = 1
    #self.wtsheet_index +=1

    wtsheet.page_preview = rdsheet.show_in_page_break_preview
    wtsheet.first_visible_row = rdsheet.first_visible_rowx
    wtsheet.first_visible_col = rdsheet.first_visible_colx
    wtsheet.grid_colour = rdsheet.gridline_colour_index
    wtsheet.preview_magn = rdsheet.cached_page_break_preview_mag_factor
    wtsheet.normal_magn = rdsheet.cached_normal_view_mag_factor
    #
    # DEFAULTROWHEIGHT
    #
    wtsheet.row_default_height =          rdsheet.default_row_height
    wtsheet.row_default_height_mismatch = rdsheet.default_row_height_mismatch
    wtsheet.row_default_hidden =          rdsheet.default_row_hidden
    wtsheet.row_default_space_above =     rdsheet.default_additional_space_above
    wtsheet.row_default_space_below =     rdsheet.default_additional_space_below

    res = re.compile("\{\{\{([A-Za-z]*)\.?([A-Za-z]*)\}\}\}")
    style_list = get_xlwt_style_list(rb)
    ymargin = 0
    wtcols = set()
    for wtcolx in xrange(rsh.ncols):
        rdcolx = wtcolx
        if wtcolx not in wtcols and rdcolx in rsh.colinfo_map:
            rdcol = rsh.colinfo_map[rdcolx]
            wtcol = wtsheet.col(wtcolx)
            wtcol.width = rdcol.width
            #wtcol.set_style(self.style_list[rdcol.xf_index])
            wtcol.hidden = rdcol.hidden
            wtcol.level = rdcol.outline_level
            wtcol.collapsed = rdcol.collapsed
            wtcols.add(wtcolx)


    cloned_rows = set()

    for rrowx in xrange(rsh.nrows):
        i = 0
        for col in xrange(rsh.ncols):
            v = rsh.cell_value(rrowx,col)
            st = rsh.cell_xf_index(rrowx,col)
            style=style_list[rsh.cell_xf_index(rrowx, col)]
            if isinstance(v, str) or isinstance(v,unicode):
                list = res.findall(v)
                if len(list)>0:
                    match = list[0]
                    #logger.error('found '+str(list) + ' in '+v)
                    if len(match[1]) > 0:
                        mainkey=match[0]
                        secondkey = match[1]
                        vl = tel.get(mainkey,'')
                        #logger.error('trying to write '+ str(vl))
                        i = 0
                        for zx in vl:
                            value = zx.get(secondkey,'')
                            write_cell(wtsheet, mc_map, value, style, rrowx, col, rrowx + i, col)
                            i += 1
                            if not rrowx in cloned_rows:
                                ymargin += 1
                                print ymargin
                        if not rrowx in cloned_rows:
                            ymargin -= 1
                            print ymargin
                            for k in xrange(col-1):
                                #print 'Копирование ячейки '+str(k)
                                write_and_clone_cell(wtsheet, mc_map, rsh.cell_value(rrox,k), style_list[rsh.cell_xf_index(rrowx,k)], rrowx, k, rrowx , k, i)
                        cloned_rows.add(rrowx)
                        #print 'Клонирована строка '+str(rrowx)
                    else:
                        key = match[0]
                        value = tel.get(key,'')
                        write_and_clone_cell(wtsheet, mc_map, value, style, rrowx, col, rrowx + ymargin, col, i)
                else:
                    #print 'Копирование ячейки 1 '+str(i)
                    if i>0:
                        ym = ymargin - i + 1
                    else:
                        ym = ymargin
                    write_and_clone_cell(wtsheet, mc_map, v, style, rrowx, col, rrowx + ym, col, i)
            else:
                #print 'Копирование ячейки 2'+str(i)
                write_and_clone_cell(wtsheet, mc_map, v, style, rrowx, col, rrowx + ymargin, col, i)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    filename = tel.get('FILENAME','report')
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.xls'
    w.save(response)
    return response


def test(request, test_id):
    report = ExcelReport()
    report.addSheet("TestBasic")
    testobj = Patient.objects.all()
    #    report.addQuerySet(testobj, REPORT_HORZ, addheader=True)
    report.addSheet("TestStyle")
    style = ExcelStyle()
    style.set_alignment(horz=3, wrap=1)
    style.set_font(font_color='000000', bold=True, italic=True)
    style.set_border(border_color='000000', border_style=5)
    style.set_pattern(pattern_color='339933', pattern=1)
    formatter = ExcelFormatter()
    formatter.addBodyStyle(style=style)
    report.addFormatter(formatter)
    report.addQuerySet(testobj, orientation=REPORT_HORZ, addheader=True)
    #    report.addSheet("TestStyle2")
#    headerstyle = ExcelStyle(font_color='00FF00', shadow=True, underline=True,
#    		      		 pattern_color='000000', pattern=1, border_style=5,
#				 border_color='FFFFFF')
#    col_style = ExcelStyle(font_color='FFFFFF')
#    formatter.addHeaderStyle(headerstyle)
#    formatter.addColumnStyle('column_name', style=col_style)
#    report.addQuerySet(testobj, REPORT_HORZ, True)
#    report.addSheet("ModifyStyle")
#    style.set_font(font_color='000000', bold=False, underline=True)
#    style.set_border(border_color='330099', border_style=6)
#    style.set_pattern(pattern_color='FFFFFF', pattern=1)
#    col_style.set_pattern(pattern_color='FFFF33', pattern=1)
#    formatter.setWidth('column1_name, column2_name', width=600)
#    report.addQuerySet(testobj, REPORT_HORZ, True)
    response = HttpResponse(report.writeReport(), mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=foo.xls'
    return response

	
def rooms(request):
    now = datetime.datetime.now()
    book_list = room_with_occupied(now, now)  
    types = RoomType.objects.all()
    values = {'book_list': book_list, 'types': types}
    values.update(csrf(request))
#    print connection.queries
    return render_to_response('pansionat/rooms.html', values)

def room_with_occupied(start_date, end_date): 
    room_list = Room.objects.all()
    return [(room, room.occupied_set.filter(start_date__lte = start_date,\
                end_date__gte = end_date))
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
        print dir(form)
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
