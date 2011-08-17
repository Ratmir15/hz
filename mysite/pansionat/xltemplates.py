# coding: utf-8

from django.http import HttpResponse
from xlrd import open_workbook

import re
import xlwt
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
                                print ymargin
                        if not rrowx in cloned_rows:
                            ymargin -= 1
                            print ymargin
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

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    filename = tel.get('FILENAME','report')
    response['Content-Disposition'] = 'attachment; filename=' + filename + '.xls'
    w.save(response)
    return response
