# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django import forms
from django.template import loader
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import Order, OrderType, OrderDay
from mysite.pansionat.proc import MedicalPriceReport
from mysite.pansionat.xltemplates import fill_excel_template

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
    order_type = forms.ModelChoiceField(OrderType.objects.all(), label = 'Тип путевки')

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


class LivingReport():

    def process(self, form):
        cleaned_report_date = form.cleaned_data['report_date']
        order_type = form.cleaned_data['order_type']
        list = OrderDay.objects.filter(busydate = cleaned_report_date,
            order__order_type = order_type).order_by("order__code")
        d = []
        i = 0
        for obj in list:
            order = obj.order
            i += 1
            innermap = dict()
            innermap['NUMBER'] = i
            innermap['NUMBERYEAR'] = order.code
            innermap['FIO'] = order.patient.__unicode__()
            innermap['AMOUNT'] = order.price
            innermap['DATEIN'] = str(order.start_date)
            innermap['DATEOUT'] = str(order.end_date)
            innermap['SROK'] = str(order.start_date)+' - '+str(order.end_date)
            innermap['ORDERNUMBER'] = order.putevka
            innermap['WHOIS'] = order.patient.grade
            innermap['WHOM'] = order.directive.name
            innermap['TIME'] = str(order.start_date)
            innermap['WORK'] = order.customer.name
            innermap['BIRTHDATE'] = str(order.patient.birth_date)
            innermap['PASSPORT'] = order.patient.passport_number+' '+order.patient.passport_whom
            innermap['ADDRESS'] = order.patient.address
            innermap['ROOM'] = order.room.name
            d.append(innermap)
        title = "Список заселенных"
        month  = ""#order_type.__unicode__()
        z = {'TITLE': title+". "+str(cleaned_report_date),'MONTH':month, 'REPORTDATE': str(cleaned_report_date)}
        return z,d

report_map = {"1":('Список заезжающих',EnteringForm,'simplereport.xls',EnteringReport()),
              "2":('Список съезжающих',LeavingForm,'simplereport.xls',LeavingReport()),
              "3":('Прайс-лист',MedicalPriceForm,'simplereport.xls',MedicalPriceReport()),
              "4":('Отчет по заселенным',LivingForm,'registrydiary.xls',LivingReport()),
              "5":('Список съезжающих с учетом типа путевки)',LeavingForm2,'simplereport.xls',LeavingReport2()),
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

