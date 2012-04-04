# coding: utf-8
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.aggregates import Max
from django.shortcuts import render_to_response
from mysite.pansionat.menu import MenuRequestContext
from mysite.pansionat.models import Order, OrderDay, Patient, Room, OrderDocument, DOC_TYPE, OrderDocumentItem, DocItem
from mysite.pansionat.orders import OrderEditForm, get_order_places, fill_cust_list

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
    values = {"doc_id":n.id, "code":n.code, "dt":n.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

@login_required
def s(request, s):
    dis = s.orderdocumentitem_set.order_by('line')
    items = []
    for di in dis:
        items.append((di.line, di.doc_item.name, di.quantity, di.price))
    values = {"doc_id":s.id, "code":s.code, "dt":s.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

@login_required
def p(request, p):
    dis = p.orderdocumentitem_set.order_by('line')
    items = []
    for di in dis:
        items.append((di.line, di.doc_item.name, di.quantity, di.price))
    values = {"doc_id":p.id, "code":p.code, "dt":p.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

@login_required
def r(request, r):
    dis = r.orderdocumentitem_set.order_by('line')
    items = []
    for di in dis:
        items.append((di.line, di.doc_item.name, di.quantity, di.price))
    values = {"doc_id":r.id, "code":r.code, "dt":r.dt_cool(), "dis":items}
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
def nakl_save(request, doc_id):
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
        items.append((cnt,n,q,p))
        dis = DocItem.objects.filter(name = n)
        if not len(dis):
            val_er.append(u'Не найдено товара '+n)
        else:
            d_items.append((cnt, dis[0],q, p))

    if len(val_er):
        values = {"dis":items,"ves":val_er,"doc_id":doc.id,"docitems":DocItem.objects.all()}
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
@permission_required('pansionat.delete_orderdocument', login_url='/forbidden/')
def done_doc(request, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    od.status = 2
    od.save()
    return rmkassa(request)

@login_required
@permission_required('pansionat.delete_orderdocument', login_url='/forbidden/')
def cancel_doc(request, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    od.status = 1
    od.save()
    return rmkassa(request)

@login_required
def print_doc(request, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    od.status = 1
    od.save()
    return rmkassa(request)

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
