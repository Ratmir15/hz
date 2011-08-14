# Create your views here.
# coding: utf-8
from datetime import date
import datetime

from django.template import Context, loader
from pansionat.models import Patient
from pansionat.models import RoomType
from pansionat.models import Room
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django_excel_templates import *
from xlutils.copy import copy
from xlrd import open_workbook
import re
import logging
from xlwt import *
from mysite.pansionat.models import Order, Customer, Occupied
import datetime
from django import forms

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
    orders_list = Order.objects.all()
    logger.error('trying to render order  '+ str(orders_list))
    t = loader.get_template('pansionat/orders.html')
    c = Context({
    'orders_list': orders_list,
    })
    return HttpResponse(t.render(c))


def detail(request, patient_id):
    return HttpResponse("You're looking at patient %s." % patient_id)
	
	
def rooms(request):
    now = datetime.now()
    book_list = room_with_occupied(now, now)  
    types = RoomType.objects.all()
#    print connection.queries
    return render_to_response('pansionat/rooms.html', {'book_list': book_list,\
                        'types': types})

def room_with_occupied(start_date, end_date): 
    room_list = Room.objects.all()
    return [(room, room.occupied_set.filter(start_date__lte = start_date,\
                end_date__gte = end_date))
                for room in room_list]

#class BookForm(forms.Form):
#    start_date = forms.DateTimeField()
#    end_date = forms.DateTimeField()
#    name = forms.CharField(max_length = 65535)
#    phone = forms.CharField(max_length = 11)
#    description = forms.CharFiled(max_lehgth = 65535)

#def bookit(request):
    # Add handler here
#    book_form = BookForm()
#    return render_to_response('pansionat/bookit.html', {
#        'book_form': book_form,
#    })

