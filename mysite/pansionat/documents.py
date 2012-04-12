# coding: utf-8
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.aggregates import Max
from django.shortcuts import render_to_response
from mysite.pansionat import gavnetso
from mysite.pansionat.alog import log_message
import mysite.pansionat.gavnetso
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import Order, OrderDay, Patient, Room, OrderDocument, DOC_TYPE, OrderDocumentItem, DocItem
from mysite.pansionat.orders import OrderEditForm, get_order_places, fill_cust_list
from mysite.pansionat.xltemplates import fill_excel_template
from pytils import numeral
import pytils.numeral

__author__ = 'YC14RP1'

@login_required
@permission_required('pansionat.add_orderdocument', login_url='/forbidden/')
def docs(request, order_id):
    order = Order.objects.get(id = order_id)
    ds = order.orderdocument_set.order_by('-dt')
    values = {"id":order.id,"docs":ds}
    return render_to_response('pansionat/docs.html', MenuRequestContext(request, values))

@login_required
def n(request, n):
    dis = n.orderdocumentitem_set.order_by('line')
    items = []
    for di in dis:
        items.append((di.line, di.doc_item.name, di.quantity, di.price))
    values = {"title":n.title(), "doc_id":n.id, "code":n.code, "dt":n.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

@login_required
def s(request, s):
    dis = s.orderdocumentitem_set.order_by('line')
    items = []
    for di in dis:
        items.append((di.line, di.doc_item.name, di.quantity, di.price))
    values = {"title":s.title(), "doc_id":s.id, "code":s.code, "dt":s.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

@login_required
def p(request, p):
    dis = p.orderdocumentitem_set.order_by('line')
    items = []
    for di in dis:
        items.append((di.line, di.doc_item.name, di.quantity, di.price))
    values = {"title":p.title(), "doc_id":p.id, "code":p.code, "dt":p.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

@login_required
def r(request, r):
    dis = r.orderdocumentitem_set.order_by('line')
    items = []
    for di in dis:
        items.append((di.line, di.doc_item.name, di.quantity, di.price))
    values = {"title":r.title(), "doc_id":r.id, "code":r.code, "dt":r.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

#@login_required
def createDocument(order_id, doc_type):
    ord = Order.objects.get(id=order_id)
    dt = datetime.now()
    code = OrderDocument.objects.filter(dt__year=dt.year, doc_type=doc_type).aggregate(Max("code"))
    mcode = code['code__max']
    if mcode is None:
        mcode = 0
    od = OrderDocument(ord=ord, dt=dt, doc_type=doc_type, code=mcode + 1,status = 0)
    return od

@login_required
def new_nakl(request, order_id):
    od = createDocument(order_id, "N")
    od.save()
    return open_doc(request, order_id, od.id)

@login_required
def new_sf(request, order_id):
    od = createDocument(order_id, "S")
    od.save()
    return open_doc(request, order_id, od.id)

@login_required
def new_p(request, order_id):
    od = createDocument(order_id, "P")
    od.save()
    return open_doc(request, order_id, od.id)

@login_required
def new_r(request, order_id):
    od = createDocument(order_id, "R")
    od.save()
    return open_doc(request, order_id, od.id)

def getOrCreateDocItem(name):
    dis = DocItem.objects.filter(name = name)
    if len(dis):
        return dis[0]
    else:
        di = DocItem(name = name)
        di.save()
        return di

@login_required
def docs_save(request, doc_id):
    doc = OrderDocument.objects.get(id = doc_id)
    items = []
    d_items = []
    val_er = []
    more = True
    cnt = 0
    while more:
        cnt += 1
        n = request.POST.get('id_di_'+str(cnt),'')
        q = request.POST.get('id_q_'+str(cnt),'')
        p = request.POST.get('id_p_'+str(cnt),'')
        if n=='':
            more = False
        else:
            items.append((cnt,n,q,p))
            dis = DocItem.objects.filter(name = n)
            if not len(dis):
                val_er.append(u'Не найдено товара '+n)
            else:
                d_items.append((cnt, dis[0],q, p))

    if len(val_er):
        values = {"title":doc.title(),"dis":items,"ves":val_er,"doc_id":doc.id,"docitems":DocItem.objects.all()}
        return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))
    else:
        for line, item, quantity, price in d_items:
            ods = OrderDocumentItem.objects.filter(order_document=doc, line = line)
            if len(ods):
                od = ods[0]
                od.doc_item = item
                od.quantity = quantity
                od.price = price
                od.save()
            else:
                odi = OrderDocumentItem(line = line, doc_item = item, quantity = quantity, price = price)
                odi.save()
        doc.orderdocumentitem_set.filter(line__gt = len(d_items)).delete()
    return open_doc(request, doc.ord.id, doc.id)

@login_required
def rmkassa(request):
    ods = OrderDocument.objects.filter(status=0).order_by("dt")
    map = dict()
    map['ods'] = ods
    return render_to_response('pansionat/rmkassa.html', MenuRequestContext(request, map))

@login_required
def rmkassadone(request):
    ods = OrderDocument.objects.filter(status=2).order_by("dt")[:100]
    map = dict()
    map['ods'] = ods
    return render_to_response('pansionat/rmkassa.html', MenuRequestContext(request, map))

@login_required
def rmkassacanceled(request):
    ods = OrderDocument.objects.filter(status=1).order_by("dt")[:100]
    map = dict()
    map['ods'] = ods
    return render_to_response('pansionat/rmkassa.html', MenuRequestContext(request, map))

@login_required
@permission_required('pansionat.delete_orderdocument', login_url='/forbidden/')
def done_doc(request, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    od.status = 2
    od.save()
    log_message(request, "Проведено")
    return rmkassa(request)

@login_required
@permission_required('pansionat.delete_orderdocument', login_url='/forbidden/')
def cancel_doc(request, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    od.status = 1
    od.save()
    log_message(request, "Отменено")
    return rmkassa(request)

@login_required
def print_doc(request, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    order = od.ord #.orderOrder.objects.get(id=od.id)
    #delt = order.end_date - order.start_date
    #days = delt.days + 1
    idx = 0
    t = list()
    for dti in od.orderdocumentitem_set.all().order_by("line"):
        idx += 1
        tovar = dti.doc_item.name
        t.append({'ROWINDEX': idx, 'NAME': tovar, 'QTY': dti.quantity, 'PRICE': dti.price, 'AMOUNT': dti.amount(), 'PNDS': 0,
          'AMOUNTNDS': '-', 'ALLAMOUNT': dti.amount()})
    order_price = od.all_amount()
    order_date = order.start_date.strftime('%d.%m.%Y')
    return generateNakl(order, order_date, order_price, request, t)

@login_required
@permission_required('pansionat.add_orderdocument', login_url='/forbidden/')
def open_doc(request, order_id, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    if od.doc_type=="N":
        return n(request, od)
    if od.doc_type=="S":
        return s(request, od)
    if od.doc_type=="P":
        return p(request, od)
    if od.doc_type=="R":
        return r(request, od)
    ds = order.orderdocument_set.order_by('-date')
    values = {"id":order.id,"docs":ds}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))


def generateNakl(order, order_date, order_price, request, t):
    template_filename = 'torg12_0.xls'
    fullname = str('ООО санаторий "Хопровские зори"')
    vendor = str('КПП 581701001 ') + fullname + str(' Пензенская обл., п.Колышлей, ул.Лесная 1а')
    if order.patient.address is None:
        client = order.patient.fio()
    else:
        client = order.patient.fio() + ',' + order.patient.address
    dir = gavnetso.getEmployerByRoleNameAndDate('Директор', order.start_date).__unicode__()
    gb = gavnetso.getEmployerByRoleNameAndDate('Главный бухгалтер', order.start_date).__unicode__()
    kassir = gavnetso.getEmployerByRoleNameAndDate('Кассир', order.start_date).__unicode__()
    rub = numeral.rubles(float(order_price), True)
    tel = {'PORTRAIT': False, 'NUMPAGES': 1, 'PIZDEZ': fullname, 'NUMBER': order.code,
           'FILENAME': 'nakladnaya-' + str(order.code),
           'CLIENT': client, 'VENDOR': vendor,
           'DIRECTOR': dir,
           'GBUH': gb,
           'KASSIR': kassir,
           'SP': rub,
           'DATE': order_date,
           'QTYSUM': 1,
           'AMOUNTSUM': order_price,
           'AMOUNTNDSSUM': order_price, 'ALLAMOUNTSUM': order_price,
           'TOVAR': t}
    return fill_excel_template(template_filename, tel, request)