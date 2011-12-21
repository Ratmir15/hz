# coding: utf-8
import datetime
from string import upper
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django import forms
from django.template import loader
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import Order, OrderType, OrderDay, OrderMedicalProcedure, Room
from mysite.pansionat.orders import room_availability
from mysite.pansionat.proc import MedicalPriceReport
from mysite.pansionat.xltemplates import fill_excel_template, fill_excel_template_net

__author__ = 'rpanov'


class EnteringForm(forms.Form):
    report_date = forms.DateField(required=True, label='Дата заезда')

class DietForm(forms.Form):
    report_date = forms.DateField(required=True, label='Дата формирования меню')

class DateFilterForm(forms.Form):
    start_date = forms.DateField(required=True, label='С')
    end_date = forms.DateField(required=True, label='по')

class EnteringReport():

    def process(self, form):
        cleaned_report_date = form.cleaned_data['report_date']
        orders = Order.objects.filter(start_date = cleaned_report_date)
        d = []
        for order in orders:
            d.append({'FIO':order.patient.fio(), 'ROOM':order.room.name})
        z = {'REPORTDATE': str(cleaned_report_date)}
        return z,d

class LeavingForm(forms.Form):
    report_date = forms.DateField(required=True, label='Дата отъезда')

class LeavingForm2(forms.Form):
    report_date = forms.DateField(required=True, label='Дата отъезда')
    order_type = forms.ModelChoiceField(OrderType.objects.all(), label = 'Тип путевки')

class MedicalPriceForm(forms.Form):
    report_date = forms.DateField(required=True, label='Дата формирования')

class LivingForm(forms.Form):
    report_date = forms.DateField(required=True, label='Дата формирования')
    order_type = forms.ChoiceField([("1","СЗ/ХЗ"),("2","Прочие"),("3","Реабилитация"),("4","Пенза проф"),("5","Самара проф"),("6","Пенза фсс")], label = 'Тип путевки')
    summ_type = forms.ChoiceField([("1","Общая сумма"),("2","Сумма за день")], label = 'Тип вывода')

class LeavingReport():

    def process(self, form):
        cleaned_report_date = form.cleaned_data['report_date']
        orders = Order.objects.filter(end_date = cleaned_report_date)
        d = []
        for order in orders:
            d.append({'FIO':order.patient.fio(), 'ROOM':order.room.name})
        z = {'REPORTDATE': str(cleaned_report_date)}
        return z,d

class LeavingReport2():

    def process(self, form):
        cleaned_report_date = form.cleaned_data['report_date']
        order_type = form.cleaned_data['order_type']
        orders = Order.objects.filter(end_date = cleaned_report_date, order_type = order_type)
        d = []
        for order in orders:
            d.append({'FIO':order.patient.fio(), 'ROOM':order.room.name})
        z = {'REPORTDATE': str(cleaned_report_date)}
        return z,d


class HzCondition():

    def process(self, order):
        n_list = [u'САНАТОРИЙ ХОПРОВСКИЕ ЗОРИ']
        return upper(order.directive.name) in n_list

class SzCondition():

    def process(self, order):
        n_list = [u'СЕЛЬСКАЯ ЗДРАВНИЦА']
        return upper(order.directive.name) in n_list

class HzSzCondition():

    def process(self, order):
        n_list = [u'СЕЛЬСКАЯ ЗДРАВНИЦА',u'САНАТОРИЙ ХОПРОВСКИЕ ЗОРИ']
        return upper(order.directive.name) in n_list

class PPCondition():

    def process(self, order):
        n_list = [u'ПЕНЗА ПРОФ']
        return upper(order.directive.name) in n_list

class SPCondition():

    def process(self, order):
        n_list = [u'САМАРА ПРОФ']
        return upper(order.directive.name) in n_list

class PFCondition():

    def process(self, order):
        n_list = [u'ПЕНЗА ФСС']
        return upper(order.directive.name) in n_list

class RCondition():

    def process(self, order):
        p_list = [26400,21607.92]
        n_list = [u'САНАТОРИЙ ХОПРОВСКИЕ ЗОРИ',u'СЕЛЬСКАЯ ЗДРАВНИЦА',u'ПЕНЗА ФСС',u'САМАРА ПРОФ',u'ПЕНЗА ПРОФ']
        return (not upper(order.directive.name) in n_list) and (order.price==26400 or (order.price>21607 and order.price<21608))

class ElseCondition():

    def process(self, order):
        b = order.price==26400 or (order.price>21607 and order.price<21608)
        n_list = [u'САНАТОРИЙ ХОПРОВСКИЕ ЗОРИ',u'СЕЛЬСКАЯ ЗДРАВНИЦА',u'ПЕНЗА ФСС',u'САМАРА ПРОФ',u'ПЕНЗА ПРОФ']
        return not b and (not upper(order.directive.name) in n_list)

tp_map = {
    "1":('ХЗ,СЗ',"hzsz",HzSzCondition()),
    "2":('Прочие',"else",ElseCondition()),
    "3":('Реабилитация',"reab",RCondition()),
    "4":('Пенза проф',"penzaprof",PPCondition()),
    "5":('Самара проф',"samaraprof",SPCondition()),
    "6":('Пенза фсс',"penzafss",PFCondition()),
}

class LivingReport():

    def process(self, form):
        cleaned_report_date = form.cleaned_data['report_date']
        cleaned_summ_type = form.cleaned_data['summ_type']
        title, title_eng, condition = tp_map[form.cleaned_data['order_type']]
        list = OrderDay.objects.filter(busydate = cleaned_report_date).order_by("order__code")
        d = []
        i = 0
        for obj in list:
            order = obj.order
            if condition.process(order):
                i += 1
                innermap = dict()
                innermap['NUMBER'] = i
                innermap['ID'] = order.id
                innermap['NUMBERYEAR'] = order.code
                innermap['FIO'] = order.patient.__unicode__()
                if cleaned_summ_type=="2":
                    dif = order.end_date - order.start_date
                    price = order.price/(dif.days+1)
                else:
                    price = order.price
                innermap['AMOUNT'] = price
                innermap['DATEIN'] = str(order.start_date)
                innermap['DATEOUT'] = str(order.end_date)
                innermap['SROK'] = str(order.start_date)+' - '+str(order.end_date)
                innermap['ORDERNUMBER'] = order.putevka
                innermap['WHOIS'] = order.patient.grade
                innermap['WHOM'] = order.directive.name
                innermap['TIME'] = str(order.start_date)
                if order.customer is None:
                    innermap['WORK'] = ""
                else:
                    innermap['WORK'] = order.customer.name
                innermap['BIRTHDATE'] = str(order.patient.birth_date)
                innermap['PASSPORT'] = order.patient.passport_number+' '+order.patient.passport_whom
                innermap['ADDRESS'] = order.patient.address
                innermap['ROOM'] = order.room.name
                d.append(innermap)
        title = "Список заселенных "+title
        month  = ""#order_type.__unicode__()
        z = {'TITLE': title+". "+str(cleaned_report_date),'MONTH':month, 'REPORTDATE': str(cleaned_report_date)}
        return z,d

report_map = {"1":('Список заезжающих',EnteringForm,'simplereport.xls',EnteringReport(),""),
              "2":('Список съезжающих',LeavingForm,'simplereport.xls',LeavingReport(),""),
              "3":('Прайс-лист',MedicalPriceForm,'simplereport.xls',MedicalPriceReport(),""),
              "4":('Отчет по заселенным',LivingForm,'registrydiary.xls',LivingReport(),'pansionat/reports/rmreg.html'),
              "5":('Список съезжающих с учетом типа путевки)',LeavingForm2,'simplereport.xls',LeavingReport2(),'pansionat/reports/rmreg.html'),
}

@login_required
def processreport(request, tp):
    report_metadata = report_map[tp]
    form = report_metadata[1](request.POST)

    if form.is_valid():
        md = report_metadata[3].process(form)
        tel = {'TITLE': report_metadata[0],
               'T': md[1]}
        for (key,value) in md[0].items():
            tel[key] = str(value)

        if request.POST.has_key("s2") and report_metadata[4]!="":
            return render_to_response(report_metadata[4], MenuRequestContext(request, tel))
        else:
            return fill_excel_template(report_metadata[2], tel)
    else:
        values = {"tp": tp, "metadata": report_metadata}
        return render_to_response('pansionat/report.html', MenuRequestContext(request, values))

@login_required
def report(request, tp):
    report_metadata = report_map[tp]
    values = {"tp": tp, "metadata": report_metadata}
    return render_to_response('pansionat/report.html', MenuRequestContext(request, values))

@login_required
def reports(request):
    t_list = Order.objects.dates('start_date','month', order='DESC')
    t = loader.get_template('pansionat/reports.html')
    c = MenuRequestContext(request,{
    't_list': t_list,
    })
    return HttpResponse(t.render(c))

@login_required
def netreport(request):
    values = {}
    return render_to_response('pansionat/netreport.html', MenuRequestContext(request, values))


def get_date(dt):
    dtv = dt.split(".")
    year = int(dtv[2])
    month = int(dtv[1])
    day = int(dtv[0])
    p_date = datetime.date(year, month, day)
    return p_date


@login_required
def zreport(request):
    values = {}
    return render_to_response('pansionat/zreport.html', MenuRequestContext(request, values))

@login_required
def netprint(request):
    d = get_date(request.POST.get("start_date",""))
    td = get_date(request.POST.get("end_date",""))
    rooms = Room.objects.filter(disabled=False).order_by("room_place__id","name")
    res = []
    for room in rooms:
        orders, booked, max , by_dates = room_availability(room,d,td)
        allinfo = []
        for order in orders:
            allinfo.append((order.patient.family, order.start_date, order.end_date))
        for book in booked:
            allinfo.append((book.name, book.start_date, book.end_date))

        allinfo = sorted(allinfo)

        row_info = []

        for name,start_date,end_date in allinfo:
            flag = False
            for i in xrange(len(row_info)):
                last_date,busy_array = row_info[i]
                #            for last_date,busy_array in row_info:
                if start_date>last_date:
                    busy_array.append((name,start_date,end_date))
                    row_info[i] = (end_date, busy_array)
                    flag = True
            if not flag:
                busy_array = [(name, start_date, end_date)]
                row_info.append((end_date,busy_array))

        res.append((room, row_info))

    tel = { 'RES': res,
            'STARTDATE': d,
            'ENDDATE': td,
            'FILENAME': 'NET-'+d.strftime('%d-%m-%Y'),
            }
    template_filename = 'simplereport.xls'
    return fill_excel_template_net(template_filename, d, td, res, tel)

@login_required
def zprint(request):
    dt = request.POST.get("start_date","")
    dtv = dt.split(".")
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
    return fill_excel_template(template_filename, tel)


