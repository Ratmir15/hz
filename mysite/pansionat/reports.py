# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django import forms
from django.template import loader
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import Order
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

class MedicalPriceForm(forms.Form):
    report_date = forms.DateField(required=True, label='Дата формирования')

class LeavingReport():

    def process(self, form):
        cleaned_report_date = form.cleaned_data['report_date']
        orders = Order.objects.filter(end_date = cleaned_report_date)
        d = []
        for order in orders:
            d.append({'FIO':order.patient.fio(), 'ROOM':order.room.name})
        z = {'REPORTDATE': str(cleaned_report_date)}
        return z,d


report_map = {"1":('Список заезжающих',EnteringForm,'simplereport.xls',EnteringReport()),
              "2":('Список съезжающих',LeavingForm,'simplereport.xls',LeavingReport()),
              "3":('Прайс-лист',MedicalPriceForm,'simplereport.xls',MedicalPriceReport()),
}

@login_required
def processreport(request, tp):
    report_metadata = report_map[tp]
    form = report_metadata[1](request.POST)

    if form.is_valid():
        md = report_metadata[3].process(form)
        tel = {'TITLE': report_metadata[0],
               'P': md[1]}
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

