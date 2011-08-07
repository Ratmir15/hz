# Create your views here.
# coding: utf-8

from django.template import Context, loader
from pansionat.models import Patient
from pansionat.models import Room
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django_excel_templates import *
from xlutils.copy import copy
from xlrd import open_workbook
import re
import logging
from xlwt import *

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

def detail(request, patient_id):
    return HttpResponse("You're looking at patient %s." % patient_id)
	
	
def bookit(request):
    room_list = Room.objects.all()
    return render_to_response('pansionat/bookit.html', {'rooms':room_list})

def xt(request):
#    rb = open_workbook('/Users/rpanov/Documents/w1.xls',formatting_info=True)
    tel = {'PIZDEZ': 'HZ', 'NUMBER': 535, 'TOVAR': [{'NAME':'TOVAR1','QTY':2},{'NAME':'TOVAR2','QTY':3}]}
    rb = open_workbook('/Users/rpanov/Downloads/tov_nakl1.xls',formatting_info=True)
    rsh = rb.sheet_by_index(0)
    w = copy(rb)
    sh = w.get_sheet(0)
    res = re.compile("\{\{\{([A-Za-z]*)\.?([A-Za-z]*)\}\}\}")
    #rb = open_workbook('/Users/rpanov/Downloads/tov_nakl1.xls',formatting_info=True)
    for rrowx in xrange(rsh.nrows):
        #rrowvalues = sh.row_values(rrowx)
        for col in xrange(rsh.ncols):
            v = rsh.cell_value(rrowx,col)
            st = rsh.cell_xf_index(rrowx,col)
            if isinstance(v, str) or isinstance(v,unicode):
                list = res.findall(v)
#                if v.startswith("{{{"):
                if len(list)>0:
                    match = list[0]
                    logger.error('found '+str(list) + ' in '+v)
                    if len(match[1]) > 0:
                        mainkey=match[0]
                        secondkey = match[1]
                        vl = tel[mainkey]
                        logger.error('trying to write '+ str(vl))
                        i = 0
                        for zx in vl:
                            value = zx[secondkey]
                            sh.write(rrowx+i,col,value)
                            i = i + 1
                    else:
                        key = match[0]
                        value = tel[key]
                        logger.error('trying to write '+ str(value))
                        xf = rb.xf_list[st]
                        #style1 = XFStyle()
                        #style1.font  = rb.font_list[xf.font_index]
                        style_list = get_xlwt_style_list(rb)
                        #ws.write(rx, cx, sh.cell_value(rowx=rx, colx=cx), style=style_list[sh.cell_xf_index(rx, cx)])
                        sh.write(rrowx,col,value,style=style_list[rsh.cell_xf_index(rrowx, col)])
                        logger.error('successfully wrote '+ str(value))
#                else:
#                    sh.write(rrowx,col,str(rrowx)+'_'+str(col)+'_zhopa')
#            else:
#                sh.write(rrowx,col,str(type(v)))


    #w.get_sheet(0).write(9,1,"PIZDEZZZZ")
    #w.get_sheet(0).write(8,1,"ZHOPA")
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=report.xls'
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
