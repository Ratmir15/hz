# coding: utf-8
from datetime import timedelta

from django.http import HttpResponse
from xlrd import open_workbook

import re
import xlwt
from xlwt.Style import easyxf
from mysite import settings

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

def fill_excel_template(template_filename, tel):
    w = prepare_excel_template(template_filename, tel)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    filename = tel.get('FILENAME','report')
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.xls'
    w.save(response)
    return response

def fill_excel_template_s_gavnom(template_filename, tel, fields, records):
    w = prepare_excel_template(template_filename, tel)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    filename = tel.get('FILENAME','report')
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.xls'
    maxr = tel['max_row']
    wtsheet = w.get_sheet(0)
    for field in fields:
        maxr += 2
        wtsheet.write_merge(maxr-1, maxr, 0, 8, field.ill_history_field.description+": "+ field.value, easyxf('align: wrap on'))
    maxr += 1
    wtsheet.write_merge(
        maxr, maxr,
        0, 8,
        'Записи истории болезни')
    for record in records:
        maxr += 2
        wtsheet.write(maxr-1, 0, record.datetime.strftime('%d.%m.%Y'))
        wtsheet.write_merge(maxr-1, maxr, 1, 8, record.text, easyxf('align: wrap on'))
    w.save(response)
    return response

def fill_excel_template_with_many_tp(template_filename, tel, tps):
    w = prepare_excel_template(template_filename, tel)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    filename = tel.get('FILENAME','report')
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.xls'
    maxr = tel['max_row']
    wtsheet = w.get_sheet(0)
    cols = ['IDX','PUTEVKA','FIO','D','KEM','SUMM','SROK','DAYS','SUMMC','DAYSN','SUMMN']
    for tp in tps:
        maxr += 3
        wtsheet.write_merge(maxr-2, maxr, 0, 10, tp[0], easyxf('align: wrap on;border: left no_line, right no_line'))
        for record in tp[1]:
            maxr += 1
            i = 0
            for col in cols:
                wtsheet.write(maxr-1, i, record.get(col,""),easyxf('align: wrap on; border: top thin, left thin, bottom thin, right thin'))
                i += 1
    w.save(response)
    return response

def fill_excel_template_porcii(template_filename, tel, res):
    w = prepare_excel_template(template_filename, tel)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    filename = tel.get('FILENAME','report')
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.xls'
    maxr = tel['max_row']
    top_row = maxr
    maxr += 1
    wtsheet = w.get_sheet(0)
    pieces = set()
    pieces_indexes = dict()
    di_pi = dict()
    wtsheet.write_merge(top_row,top_row+1, 0,0,"Продукты\nБлюда", easyxf('align: wrap on, horiz center, vert center; border: top thick, left thick, bottom thin, right thin'))
    wtsheet.write_merge(top_row,top_row+1, 1,1,"Кол-во", easyxf('align: wrap on, horiz center, vert center, rota 90; border: top thick, left thin, bottom thin, right thin'))
    wtsheet.write_merge(top_row,top_row+1, 2,2,"Выход", easyxf('align: wrap on, horiz center, vert center, rota 90; border: top thick, left thin, bottom thin, right thin'))
    wtsheet.write_merge(top_row,top_row, 3,3,"", easyxf('align: wrap on, horiz center, vert center; border: top thick, left thin, bottom thin, right thin'))
    wtsheet.write_merge(top_row+1,top_row+1, 3,3,"", easyxf('align: wrap on, horiz center, vert center; border: top thin, left thin, bottom thin, right thin'))

    for id,qty,di in res:
        for itempiece in di.item.itempiece_set.all():
            if not itempiece.piece in pieces:
                pieces.add(itempiece.piece)
                pieces_indexes[itempiece.piece]=(len(pieces),0)
                wtsheet.write_merge(top_row,top_row, 2+2*len(pieces)-1,2+2*len(pieces),itempiece.piece.name, easyxf('align: wrap on, horiz center, vert center; border: top thick, left thick, bottom thin, right thick'))
                wtsheet.write_merge(top_row+1,top_row+1,2+2*len(pieces)-1,2+2*len(pieces)-1, 'норма', easyxf('align: wrap on; alignment:rota 90; border: top thin, left thick, bottom thin, right thin'))
                wtsheet.write_merge(top_row+1,top_row+1,2+2*len(pieces),2+2*len(pieces), 'кол-во', easyxf('align: wrap on; alignment:rota 90; border: top thin, left thin, bottom thin, right thick'))
                col = wtsheet.col(1+2*len(pieces))
                col.width = 850
                col = wtsheet.col(2+2*len(pieces))
                col.width = 850
            (idx,total) = pieces_indexes[itempiece.piece]
            l = di_pi.get(di,dict())
            l[idx] = itempiece.weight
            di_pi[di] = l
            pieces_indexes[itempiece.piece] = (idx,total+qty*itempiece.weight)

    simple = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thin, bottom thin, right thin')
    left = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thick, bottom thin, right thin')
    right = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thin, bottom thin, right thick')
    bottom = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thin, bottom thick, right thin')

    for id,qty,di in res:
        maxr += 1
        wtsheet.write_merge(maxr, maxr, 0, 0, di.item.name, easyxf('align: wrap on; border: top thin, left thick, bottom thin, right thin'))
        wtsheet.write_merge(maxr, maxr, 1, 1, qty, easyxf('align: wrap on; border: top thin, left thin, bottom thin, right thin'))
        wtsheet.write_merge(maxr, maxr, 2, 2, di.item.weight, easyxf('align: wrap on; border: top thin, left thin, bottom thin, right thin'))
        wtsheet.write_merge(maxr, maxr, 3, 3, 0, easyxf('align: wrap on; border: top thin, left thin, bottom thin, right thin'))
        row = wtsheet.row(maxr)
        row.height=500
        row.height_mismatch = True

        d = di_pi.get(di,dict())

        cnt = len(pieces)+1

        for i in xrange(1,cnt):
            weight = d.get(i,0)
            if weight>0:
                wtsheet.write_merge(maxr, maxr, 1+2*i, 1+2*i, weight, left)
                wtsheet.write_merge(maxr, maxr, 2+2*i, 2+2*i, qty, right)
            else:
                wtsheet.write_merge(maxr, maxr, 1+2*i, 1+2*i, "", left)
                wtsheet.write_merge(maxr, maxr, 2+2*i, 2+2*i, "", right)
                

#    for id,qty,di in res:
#        maxr += 1
#        wtsheet.write_merge(maxr, maxr, 0, 0, di.item.name, easyxf('align: wrap on'))
#        wtsheet.write_merge(maxr, maxr, 1, 1, qty, easyxf('align: wrap on'))
#        wtsheet.write_merge(maxr, maxr, 2, 2, di.item.weight, easyxf('align: wrap on'))
#        for itempiece in di.item.itempiece_set.all():
#            if not itempiece.piece in pieces:
#                pieces.add(itempiece.piece)
#                pieces_indexes[itempiece.piece]=(len(pieces),0)
#                wtsheet.write_merge(top_row,top_row, 3+2*len(pieces)-1,3+2*len(pieces),itempiece.piece.name, easyxf('align: wrap on, horiz center, vert center'))
#                wtsheet.write_merge(top_row+1,top_row+1,3+2*len(pieces)-1,3+2*len(pieces)-1, 'норма', easyxf('align: wrap on; alignment:rota 90'))
#                wtsheet.write_merge(top_row+1,top_row+1,3+2*len(pieces),3+2*len(pieces), 'кол-во', easyxf('align: wrap on; alignment:rota 90'))
#                col = wtsheet.col(2+2*len(pieces))
#                col.width = 900
#                col = wtsheet.col(3+2*len(pieces))
#                col.width = 900
#            (idx,total) = pieces_indexes[itempiece.piece]
#            pieces_indexes[itempiece.piece] = (idx,total+qty*itempiece.weight)
#            wtsheet.write_merge(maxr, maxr, 2+2*idx, 2+2*idx, itempiece.weight, easyxf('align: wrap on; font:name Arial, height 160'))
#            wtsheet.write_merge(maxr, maxr, 3+2*idx, 3+2*idx, qty, easyxf('align: wrap on; font:name Arial, height 160'))
#            row = wtsheet.row(maxr)
#            row.height=500
#            row.height_mismatch = True

    maxr += 1
    wtsheet.write_merge(maxr, maxr, 0,0, 'Итого продуктов', easyxf('align: wrap on; font:name Arial, height 240; border: top thin, left thick, bottom thick, right thin'))
    wtsheet.write_merge(maxr, maxr, 1,1, '', bottom)
    wtsheet.write_merge(maxr, maxr, 2,2, '', bottom)
    wtsheet.write_merge(maxr, maxr, 3,3, '', bottom)

    for key,value in pieces_indexes.items():
        wtsheet.write_merge(maxr, maxr, 1+2*value[0], 2+2*value[0], value[1], easyxf('align: wrap on; font:name Arial, height 220; border: top thin, left thick, bottom thick, right thick'))

    row = wtsheet.row(top_row)
    row.height=1500
    row.height_mismatch = True
    row = wtsheet.row(top_row+1)
    row.height=1000
    row.height_mismatch = True
    row = wtsheet.row(maxr)
    row.height=400
    row.height_mismatch = True

    w.save(response)
    return response

def fill_excel_template_net(template_filename, sd,ed, res, tel):
    w = prepare_excel_template(template_filename, tel)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    filename = tel.get('FILENAME','report')
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.xls'
    maxr = tel['max_row']
    top_row = maxr
    maxr += 1
    wtsheet = w.get_sheet(0)
    pieces = set()
    pieces_indexes = dict()
    di_pi = dict()
    simple = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thin, bottom thin, right thin')
    bad = easyxf('align: wrap on; font:name Arial, height 160, italic 1; border: top thin, left thick, bottom thin, right thin')
    wtsheet.write_merge(top_row,top_row+1, 0,0,"Номер", simple)
    std = sd
    td = timedelta(days=1)
    i = 1
    while std<=ed:
        wtsheet.write_merge(top_row,top_row+1, i,i,std.day, simple)
        std += td
        i +=1

    top_row +=2

    for i in xrange(0,len(res)):
        room, room_info = res[i]
        h = 0
        if len(room_info)>1:
            h = len(room_info)-1
        wtsheet.write_merge(top_row,top_row+h, 0,0,room.name, simple)

        z = 0
        for end_ddd,busy_array in room_info:
            for name, start_date, end_date in busy_array:
                td1 = start_date-sd
                if td1.days<0:
                    td1d = 0
                else:
                    td1d = td1.days
                td2 = end_date-sd
                if z>room.room_type.places:
                    stl = bad
                else:
                    stl = simple
                wtsheet.write_merge(top_row+z,top_row+z, td1d+1,td2.days+1,name, stl)
            z +=1
        top_row += h+1

    left = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thick, bottom thin, right thin')
    right = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thin, bottom thin, right thick')
    bottom = easyxf('align: wrap on; font:name Arial, height 160; border: top thin, left thin, bottom thick, right thin')

    w.save(response)
    return response


def prepare_excel_template(template_filename, tel):
    rb = open_workbook(settings.STATIC_ROOT + '/xls/' + template_filename,formatting_info=True)
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
                                #print ymargin
                        if not rrowx in cloned_rows:
                            ymargin -= 1
                            # print ymargin
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
        if rsh.rowinfo_map.has_key(rrowx):
            #print str(rrowx)+":"+str(rsh.rowinfo_map[rrowx].height)
            wtsheet.row(rrowx + ymargin).height = rsh.rowinfo_map[rrowx].height
            wtsheet.row(rrowx + ymargin).height_mismatch = True

    tel['max_row'] = rsh.nrows + ymargin

    return w