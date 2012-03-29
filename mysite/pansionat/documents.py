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
        items.append((di.line, di.docitem.name, di.qty, di.price))
    values = {"doc_id":n.id, "code":n.code, "dt":n.dt_cool(), "dis":items}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))

@login_required
def new_nakl(request, order_id):
    ord = Order.objects.get(id = order_id)
    dt = datetime.now()
    code = OrderDocument.objects.filter(dt__year = dt.year, doc_type = "N").aggregate(Max("code"))
    mcode = code['code__max']

    if mcode is None:
        mcode = 0
    od = OrderDocument(ord = ord, dt = dt,doc_type = "N", code = mcode + 1)
    od.save()
    return open_doc(request, order_id, od.id)

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
@permission_required('pansionat.add_orderdocument', login_url='/forbidden/')
def open_doc(request, order_id, doc_id):
    od = OrderDocument.objects.get(id = doc_id)
    if od.doc_type=="N":
        return n(request, od)
    ds = order.orderdocument_set.order_by('-date')
    values = {"id":order.id,"docs":ds}
    return render_to_response('pansionat/nakl.html', MenuRequestContext(request, values))
