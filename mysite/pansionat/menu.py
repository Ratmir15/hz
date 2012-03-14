# coding: utf-8
from django.template.context import RequestContext

__author__ = 'rpanov'

class MenuItem:
    href = "/"
    label = "default"

def getMenuItems(request):
    user = request.user
    items = []
    if user.has_perm('pansionat.add_patient'):
        i = MenuItem()
        i.href = "/patients/"
        i.label = "Пациенты"
        items.append(i)
        i = MenuItem()
        i.href = "/clients/"
        i.label = "Организации"
        items.append(i)
    if user.has_perm('pansionat.add_order'):
        i = MenuItem()
        i.href = "/rooms/"
        i.label = "Номера"
        items.append(i)
        i = MenuItem()
        i.href = "/rmreg/"
        i.label = "РМР"
        items.append(i)
    if user.has_perm('pansionat.add_medicalproceduretypeprice'):
        i = MenuItem()
        i.href = "/rmdoc/"
        i.label = "РМД"
        items.append(i)
        i = MenuItem()
        i.href = "/mpp/"
        i.label = "Процедуры"
        items.append(i)
    if user.is_authenticated():
        i = MenuItem()
        i.href = "/ordersmenu/"
        i.label = "Путевки"
        items.append(i)
        i = MenuItem()
        i.href = "/reports/"
        i.label = "Отчеты"
        items.append(i)
    return items



class MenuRequestContext(RequestContext):
    def __init__(self, request, dict=None, processors=None, current_app=None, use_l10n=None):
        dict['menu_list'] = getMenuItems(request)
        RequestContext.__init__(self, request, dict, processors, current_app=current_app, use_l10n=use_l10n)
