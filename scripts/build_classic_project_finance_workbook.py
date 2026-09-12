from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

PURPLE = '666699'
NAVY = '000066'
BLUE = '003399'
LIGHT_BLUE = '99CCFF'
CYAN = 'CCFFFF'
YELLOW = 'FFFF99'
GREEN = 'CCFFCC'
PALE_GREEN = 'E2F0D9'
ORANGE = 'FFCC99'
GREY = 'D9D9D9'
DARK_GREY = '808080'
WHITE = 'FFFFFF'
BLACK = '000000'
LINK_GREEN = '008000'
INPUT_BLUE = '0000FF'
RED = 'C00000'
BORDER = '7F7F7F'

THIN = Side(style='thin', color=BORDER)
MEDIUM = Side(style='medium', color=BLACK)
DOUBLE = Side(style='double', color=BLACK)

FMT_BN = '#,##0.00;[Red](#,##0.00);-'
FMT_NUM = '#,##0.00;[Red](#,##0.00);-'
FMT_INT = '#,##0;[Red](#,##0);-'
FMT_PCT = '0.0%'
FMT_PCT2 = '0.00%'
FMT_MULT = '0.00x'

CLASSIC_SHEETS = [
    '00_Title_Page', '01_Dashboard', '02_Model_Log', '03_Input_Scenarios',
    '04_Construction_Workings', '05_Project_Workings', '06_Financing_Workings',
    '07_Cashflow_Waterfall', '08_Coverage_Returns', '09_Sensitivity',
    '10_IC_Decision', '11_Model_Checks',
]


def fill(color):
    return PatternFill('solid', fgColor=color)


def set_font(cell, color=BLACK, bold=False, size=9, italic=False):
    cell.font = Font(name='Arial', color=color, bold=bold, size=size, italic=italic)


def border_all(cell, side=THIN):
    cell.border = Border(left=side, right=side, top=side, bottom=side)


def style_cell(cell, *, bg=None, color=BLACK, bold=False, size=9, align='left', fmt=None, wrap=False, border=False):
    if bg:
        cell.fill = fill(bg)
    set_font(cell, color=color, bold=bold, size=size)
    cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
    if fmt:
        cell.number_format = fmt
    if border:
        border_all(cell)


def section(ws, row, title, end_col):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=end_col)
    c = ws.cell(row, 1, title)
    for col in range(1, end_col + 1):
        ws.cell(row, col).fill = fill(BLUE)
    set_font(c, WHITE, True, 9)
    c.alignment = Alignment(vertical='center')
    ws.row_dimensions[row].height = 18


def banner(ws, title, subtitle, end_col):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=end_col)
    ws['A1'] = title
    ws['A2'] = subtitle
    for row in (1, 2):
        for col in range(1, end_col + 1):
            ws.cell(row, col).fill = fill(PURPLE)
    set_font(ws['A1'], WHITE, True, 11)
    set_font(ws['A2'], WHITE, False, 9)
    ws.row_dimensions[1].height = 20
    ws.row_dimensions[2].height = 18


def label(cell, text, bg=LIGHT_BLUE):
    cell.value = text
    style_cell(cell, bg=bg, color=NAVY, bold=True, border=True, wrap=True)


def formula(cell, fx, fmt=None, bg=WHITE, color=LINK_GREEN, bold=False, align='right'):
    cell.value = fx
    style_cell(cell, bg=bg, color=color, bold=bold, fmt=fmt, align=align, border=True)


def hardcode(cell, value, fmt=None, bg=YELLOW, align='right'):
    cell.value = value
    style_cell(cell, bg=bg, color=INPUT_BLUE, bold=True, fmt=fmt, align=align, border=True)


def configure(ws, freeze='A4'):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = freeze
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and c.font.name is None:
                set_font(c)


def project_formula(sheet, value_col, key_col='A', key='$B$4', first=2, last=1000):
    return f'=INDEX(\'{sheet}\'!${value_col}${first}:${value_col}${last},MATCH({key},\'{sheet}\'!${key_col}${first}:${key_col}${last},0))'


def dashboard_formula(sheet, value_col, key_col='A', first=2, last=1000):
    return project_formula(sheet, value_col, key_col=key_col, key='$B$3', first=first, last=last)


def add_status_rules(ws, rng, anchor):
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR({anchor}="PASS",{anchor}="MATCH",{anchor}=TRUE)'], fill=fill(PALE_GREEN), font=Font(name='Arial', color='006100', bold=True)))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR({anchor}="FAIL",{anchor}="BREACH",{anchor}="REVIEW",{anchor}="REJECT")'], fill=fill('FFC7CE'), font=Font(name='Arial', color='9C0006', bold=True)))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR({anchor}="CONDITIONAL",{anchor}="INVEST_WITH_CONDITIONS",{anchor}="RENEGOTIATE")'], fill=fill(YELLOW), font=Font(name='Arial', color='9C6500', bold=True)))


def build_title(wb):
    ws = wb.create_sheet('00_Title_Page', 0)
    ws.sheet_view.showGridLines = False
    for col, width in {'A':4, 'B':18, 'C':22, 'D':22, 'E':22, 'F':22, 'G':22, 'H':18}.items():
        ws.column_dimensions[col].width = width
    ws.merge_cells('B3:H5')
    ws['B3'] = 'VIETGREEN C&I SOLAR — PROJECT FINANCE MODEL'
    ws['B3'].fill = fill(PURPLE)
    set_font(ws['B3'], WHITE, True, 20)
    ws['B3'].alignment = Alignment(vertical='center', wrap_text=True)
    ws.merge_cells('B7:H8')
    ws['B7'] = 'Classic infrastructure-model presentation | Construction → Operations → Financing → Coverage → Returns → Sensitivity → Investment Committee'
    style_cell(ws['B7'], bg=LIGHT_BLUE, color=NAVY, bold=True, size=11, wrap=True)
    section(ws, 11, 'MODEL DETAILS', 8)
    details = [
        ('B12', 'Model Purpose', 'D12', 'Recruiter / underwriting review'),
        ('B13', 'Reporting Currency', 'D13', 'VND'),
        ('B14', 'Base Project', 'D14', 'VG-001'),
        ('B15', 'Project Life', 'D15', '15 years'),
        ('B16', 'Debt Tenor', 'D16', '10 years'),
        ('B17', 'Presentation Update', 'D17', '12-Sep-2026'),
    ]
    for lc, lt, vc, vv in details:
        label(ws[lc], lt)
        ws.merge_cells(start_row=ws[vc].row, start_column=ws[vc].column, end_row=ws[vc].row, end_column=8)
        ws[vc] = vv
        style_cell(ws[vc], bg=WHITE, color=BLACK, bold=True, border=True)
    ws.merge_cells('B20:H23')
    ws['B20'] = 'Model convention: blue font = hardcodes / user inputs; green font = cross-sheet links; black font = formulas; yellow fill = key assumptions / attention; grey = financing and reserve mechanics; cyan = subtotals and key outputs.'
    style_cell(ws['B20'], bg=GREY, color=BLACK, wrap=True, border=True)


def build_dashboard(wb):
    ws = wb.create_sheet('01_Dashboard', 1)
    banner(ws, 'VIETGREEN PROJECT FINANCE MODEL | DASHBOARD', 'Selected-project executive outputs and decision summary', 14)
    label(ws['A3'], 'Selected Project')
    hardcode(ws['B3'], 'VG-001', align='center')
    dv = DataValidation(type='list', formula1='"' + ','.join(f'VG-{i:03d}' for i in range(1, 21)) + '"')
    ws.add_data_validation(dv); dv.add(ws['B3'])
    label(ws['D3'], 'Base Year'); hardcode(ws['E3'], 2026, fmt='0', align='center')
    label(ws['G3'], 'Units'); ws['H3'] = 'VND bn / x / %'; style_cell(ws['H3'], bg=WHITE, bold=True, border=True)

    section(ws, 5, 'KEY MODEL OUTPUTS', 14)
    metrics = [
        ('A6','B6','Installed Capacity (MWp)', dashboard_formula('18_Portfolio','D'), FMT_NUM),
        ('D6','E6','Project Cost (VND bn)', "=INDEX('07_CAPEX_Construction'!$N$2:$N$1000,MATCH($B$3,'07_CAPEX_Construction'!$A$2:$A$1000,0))/1000000000", FMT_BN),
        ('G6','H6','Standalone Debt (VND bn)', dashboard_formula('18_Portfolio','E'), FMT_BN),
        ('J6','K6','Minimum DSCR', dashboard_formula('14_Coverage','B'), FMT_MULT),
        ('A8','B8','LLCR', dashboard_formula('14_Coverage','C'), FMT_MULT),
        ('D8','E8','PLCR', dashboard_formula('14_Coverage','D'), FMT_MULT),
        ('G8','H8','Project NPV (VND bn)', '=' + dashboard_formula('15_Returns_Discount','E')[1:] + '/1000000000', FMT_BN),
        ('J8','K8','Equity NPV (VND bn)', '=' + dashboard_formula('15_Returns_Discount','D')[1:] + '/1000000000', FMT_BN),
    ]
    for lc, vc, txt, fx, fmt in metrics:
        label(ws[lc], txt); formula(ws[vc], fx, fmt, bg=CYAN, bold=True)
    label(ws['M6'], 'Sponsor Status'); formula(ws['N6'], dashboard_formula('19_IC_Bankability','B'), align='center', bold=True)
    label(ws['M8'], 'Lender Status'); formula(ws['N8'], dashboard_formula('19_IC_Bankability','C'), align='center', bold=True)
    add_status_rules(ws, 'N6', 'N6'); add_status_rules(ws, 'N8', 'N8')

    section(ws, 11, 'FINANCING & CREDIT METRICS', 14)
    debt = [
        ('A12','B12','All-in Debt Rate', dashboard_formula('11_Debt_Terms','G',key_col='B'), FMT_PCT2),
        ('D12','E12','Leverage Cap', dashboard_formula('11_Debt_Terms','M',key_col='B'), FMT_PCT),
        ('G12','H12','Debt Tenor', dashboard_formula('11_Debt_Terms','N',key_col='B'), '0'),
        ('J12','K12','Covenant DSCR', dashboard_formula('11_Debt_Terms','J',key_col='B'), FMT_MULT),
        ('A14','B14','Lock-up DSCR', dashboard_formula('11_Debt_Terms','K',key_col='B'), FMT_MULT),
        ('D14','E14','DSRA Months', dashboard_formula('11_Debt_Terms','O',key_col='B'), '0'),
        ('G14','H14','DSCR Headroom', '=K6-K12', FMT_MULT),
        ('J14','K14','Coverage Status', dashboard_formula('14_Coverage','J'), '@'),
    ]
    for lc, vc, txt, fx, fmt in debt:
        label(ws[lc], txt); formula(ws[vc], fx, fmt, bg=YELLOW if vc in {'B12','E12','H12','K12','B14','E14'} else CYAN, bold=True)
    add_status_rules(ws, 'K14', 'K14')

    section(ws, 17, 'DOWNSIDE REVIEW', 14)
    headers = ['Scenario','CFADS Factor','CAPEX Factor','Interest Rate','Minimum DSCR','Credit Flag']
    for i,h in enumerate(headers,1):
        c=ws.cell(18,i,h); style_cell(c,bg=ORANGE,bold=True,border=True,align='center')
    scenario_rows = ['BASE_SPONSOR','P90_ENERGY','CAPEX_OVERRUN','COD_DELAY','INTEREST_RATE_SHOCK','FX_CRAWL','FX_ONE_OFF','DSO_DELAY','OFFTAKER_PARTIAL_NONPAYMENT','OFFTAKER_DEFAULT_TERMINATION','SITE_CONTINUITY_EVENT','COMBINED_DOWNSIDE','PORTFOLIO_COMMON_FACTOR_DOWNSIDE']
    for idx,sid in enumerate(scenario_rows,19):
        ws.cell(idx,1,sid); style_cell(ws.cell(idx,1), bg=LIGHT_BLUE, color=LINK_GREEN, bold=True, border=True)
        for col, src in [(2,'C'),(3,'D'),(4,'F'),(5,'P')]:
            formula(ws.cell(idx,col), f'=INDEX(\'17_Scenarios_Sensitivity\'!${src}$2:${src}$14,MATCH($A{idx},\'17_Scenarios_Sensitivity\'!$A$2:$A$14,0))', FMT_PCT if col in (2,3) else FMT_PCT2 if col==4 else FMT_MULT, bg=YELLOW if col<5 else CYAN, bold=col==5)
        ws.cell(idx,6, f'=IF(E{idx}<1.20,"BREACH","PASS")'); style_cell(ws.cell(idx,6), bg=WHITE, bold=True, border=True, align='center'); add_status_rules(ws, f'F{idx}', f'F{idx}')
    ws.conditional_formatting.add('A19:F19', FormulaRule(formula=['$A19="BASE_SPONSOR"'], fill=fill(PALE_GREEN), font=Font(name='Arial', color='006100', bold=True)))

    section(ws, 34, 'INVESTMENT COMMITTEE SUMMARY', 14)
    decision = [
        ('A35','B35','Binding Issue', dashboard_formula('19_IC_Bankability','D')),
        ('A37','B37','Recommended Action', dashboard_formula('19_IC_Bankability','E')),
        ('A39','B39','Final Classification', dashboard_formula('19_IC_Bankability','I')),
    ]
    for lc,vc,txt,fx in decision:
        label(ws[lc],txt); ws.merge_cells(start_row=ws[vc].row,start_column=2,end_row=ws[vc].row,end_column=14); formula(ws[vc],fx,align='left',bold=True)
    add_status_rules(ws, 'B39:N39', 'B39')
    for col,w in {'A':36,'B':16,'C':3,'D':24,'E':16,'F':16,'G':24,'H':16,'I':3,'J':24,'K':16,'L':3,'M':24,'N':18}.items(): ws.column_dimensions[col].width=w
    configure(ws,'A5')


def build_model_log(wb):
    ws=wb.create_sheet('02_Model_Log',2)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | MODEL LOG','Version control and reviewer notes',10)
    headers=['Date','Version','Owner','Description','Scope','Status']
    for i,h in enumerate(headers,1): style_cell(ws.cell(5,i,h),bg=ORANGE,bold=True,border=True,align='center')
    rows=[
        ['12-Sep-2026','v1.2','Analyst','Classic project-finance presentation and expanded cell highlighting','Presentation / formula views','CURRENT'],
        ['12-Sep-2026','v1.1','Analyst','Added debt, waterfall, returns and sensitivity working sheets','Financial modeling','SUPERSEDED'],
        ['11-Sep-2026','v1.0','Analyst','Institutional recruiter workbook','Baseline presentation','SUPERSEDED'],
    ]
    for r,row in enumerate(rows,6):
        for c,v in enumerate(row,1): ws.cell(r,c,v); style_cell(ws.cell(r,c),bg=GREEN if r==6 else WHITE,bold=(r==6),border=True,wrap=True)
    for col,w in {'A':16,'B':12,'C':16,'D':64,'E':30,'F':18}.items(): ws.column_dimensions[col].width=w
    configure(ws,'A5')


def build_input_scenarios(wb):
    ws=wb.create_sheet('03_Input_Scenarios',3)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | INPUT SCENARIOS','Scenario controls and registered downside parameters',20)
    label(ws['A4'],'Selected Project'); formula(ws['B4'],"='01_Dashboard'!$B$3",align='center',bold=True)
    section(ws,6,'SCENARIO MATRIX',20)
    scenarios=['BASE_SPONSOR','P90_ENERGY','CAPEX_OVERRUN','COD_DELAY','INTEREST_RATE_SHOCK','FX_ONE_OFF','DSO_DELAY','COMBINED_DOWNSIDE']
    for i,s in enumerate(scenarios,8): ws.cell(7,i,s); style_cell(ws.cell(7,i),bg=NAVY,color=WHITE,bold=True,border=True,align='center',wrap=True)
    rows=[('Energy Case','B','@'),('CFADS Factor','C',FMT_PCT),('CAPEX Factor','D',FMT_PCT),('COD Delay (years)','E','0'),('Interest Rate','F',FMT_PCT2),('FX Depreciation','G',FMT_PCT),('DSO Days','H','0'),('Site Event Factor','J',FMT_PCT),('Common Factor','K',FMT_PCT)]
    for rr,(name,col,fmt) in enumerate(rows,9):
        label(ws.cell(rr,1),name)
        for i in range(8,16): formula(ws.cell(rr,i),f'=INDEX(\'17_Scenarios_Sensitivity\'!${col}$2:${col}$14,MATCH({ws.cell(7,i).coordinate},\'17_Scenarios_Sensitivity\'!$A$2:$A$14,0))',fmt,bg=YELLOW)
    section(ws,21,'OPTIMISATION / FINANCING INPUTS',20)
    finance=[('Reference Rate','E',FMT_PCT2),('Spread','F','0 "bps"'),('All-in Rate','G',FMT_PCT2),('Sizing DSCR','H',FMT_MULT),('Sculpting DSCR','I',FMT_MULT),('Covenant DSCR','J',FMT_MULT),('Lock-up DSCR','K',FMT_MULT),('LLCR Floor','L',FMT_MULT),('Leverage Cap','M',FMT_PCT),('Debt Tenor','N','0'),('DSRA Months','O','0')]
    for r,(name,col,fmt) in enumerate(finance,22): label(ws.cell(r,1),name); formula(ws.cell(r,2),project_formula('11_Debt_Terms',col,key_col='B'),fmt,bg=YELLOW,bold=True)
    ws.column_dimensions['A'].width=32; ws.column_dimensions['B'].width=14
    for c in range(8,16): ws.column_dimensions[ws.cell(1,c).column_letter].width=16
    configure(ws,'A7')


def build_construction(wb):
    ws=wb.create_sheet('04_Construction_Workings',4)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | CONSTRUCTION WORKINGS','Monthly capital expenditure, Value Added Tax (VAT) and Interest During Construction (IDC)',20)
    label(ws['A4'],'Selected Project'); formula(ws['B4'],"='01_Dashboard'!$B$3",align='center',bold=True)
    section(ws,6,'MONTHLY CONSTRUCTION SCHEDULE',20)
    ws['A7']='Construction Month'; style_cell(ws['A7'],bg=PURPLE,color=WHITE,bold=True,border=True)
    for i in range(12):
        c=8+i; ws.cell(7,c,i+1); style_cell(ws.cell(7,c),bg=PURPLE,color=WHITE,bold=True,border=True,align='right')
    rows=[('Construction Share','C',FMT_PCT,YELLOW),('Gross CAPEX','D',FMT_BN,WHITE),('Net CAPEX','E',FMT_BN,WHITE),('VAT','F',FMT_BN,WHITE),('IDC','G',FMT_BN,GREY),('Cumulative CAPEX','H',FMT_BN,CYAN),('Cumulative IDC','I',FMT_BN,GREY)]
    for rr,(name,col,fmt,bg) in enumerate(rows,9):
        label(ws.cell(rr,1),name)
        for i in range(12):
            cc=8+i; fx=f'=SUMIFS(\'07_CAPEX_Construction\'!${col}:${col},\'07_CAPEX_Construction\'!$A:$A,$B$4,\'07_CAPEX_Construction\'!$B:$B,{i+1})/1000000000' if fmt==FMT_BN else f'=SUMIFS(\'07_CAPEX_Construction\'!${col}:${col},\'07_CAPEX_Construction\'!$A:$A,$B$4,\'07_CAPEX_Construction\'!$B:$B,{i+1})'
            formula(ws.cell(rr,cc),fx,fmt,bg=bg,bold=name.startswith('Cumulative'))
    section(ws,18,'SOURCES & USES SUMMARY',20)
    summary=[('Gross Construction CAPEX','=' + project_formula('07_CAPEX_Construction','J')[1:] + '/1000000000'),('Net Construction CAPEX','=' + project_formula('07_CAPEX_Construction','K')[1:] + '/1000000000'),('VAT','=' + project_formula('07_CAPEX_Construction','L')[1:] + '/1000000000'),('Interest During Construction (IDC)',"=SUM(H13:S13)"),('Total Uses','=' + project_formula('07_CAPEX_Construction','N')[1:] + '/1000000000')]
    for r,(name,fx) in enumerate(summary,19): label(ws.cell(r,1),name); formula(ws.cell(r,5),fx,FMT_BN,bg=CYAN if r==23 else WHITE,bold=r==23)
    ws.column_dimensions['A'].width=34
    for c in range(8,20): ws.column_dimensions[ws.cell(1,c).column_letter].width=12
    configure(ws,'A7')


def build_project_workings(wb):
    ws=wb.create_sheet('05_Project_Workings',5)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | PROJECT WORKINGS','Operating cash flow and Cash Flow Available for Debt Service (CFADS)',23)
    label(ws['A4'],'Selected Project'); formula(ws['B4'],"='01_Dashboard'!$B$3",align='center',bold=True)
    section(ws,6,'OPERATING TIMELINE',23)
    ws['A7']='Year Number'; style_cell(ws['A7'],bg=PURPLE,color=WHITE,bold=True,border=True)
    for i in range(16): c=8+i; ws.cell(7,c,i); style_cell(ws.cell(7,c),bg=PURPLE,color=WHITE,bold=True,border=True,align='right')
    rows=[('Revenue','C',FMT_BN,WHITE),('Operating Expenditure (OPEX)','D',FMT_BN,WHITE),('EBITDA',None,FMT_BN,CYAN),('Depreciation','E',FMT_BN,WHITE),('Taxable Income','F',FMT_BN,WHITE),('Cash Tax','I',FMT_BN,WHITE),('Working Capital','J',FMT_BN,YELLOW),('Change in Working Capital','K',FMT_BN,YELLOW),('Major Maintenance','Q',FMT_BN,YELLOW),('Terminal Release','S',FMT_BN,WHITE),('CFADS','U',FMT_BN,CYAN),('Sources / Uses Check','X',FMT_BN,WHITE)]
    for rr,(name,col,fmt,bg) in enumerate(rows,10):
        label(ws.cell(rr,1),name)
        for i in range(16):
            cc=8+i; fx=f'={ws.cell(rr-2,cc).coordinate}-{ws.cell(rr-1,cc).coordinate}' if name=='EBITDA' else f'=SUMIFS(\'09_Project_CF_CFADS\'!${col}:${col},\'09_Project_CF_CFADS\'!$A:$A,$B$4,\'09_Project_CF_CFADS\'!$B:$B,{i})/1000000000'
            formula(ws.cell(rr,cc),fx,fmt,bg=bg,bold=name in {'EBITDA','CFADS'})
    for r in [12,20]:
        for c in range(1,24): ws.cell(r,c).border=Border(top=MEDIUM,bottom=THIN)
    for c in range(1,24): ws.cell(20,c).border=Border(top=MEDIUM,bottom=DOUBLE)
    ws.column_dimensions['A'].width=38
    for c in range(8,24): ws.column_dimensions[ws.cell(1,c).column_letter].width=11
    configure(ws,'A7')


def build_financing(wb):
    ws=wb.create_sheet('06_Financing_Workings',6)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | FINANCING WORKINGS','Senior debt schedule sculpted to target Debt Service Coverage Ratio (DSCR)',18)
    label(ws['A4'],'Selected Project'); formula(ws['B4'],"='01_Dashboard'!$B$3",align='center',bold=True)
    section(ws,6,'SENIOR DEBT TERMS',18)
    terms=[('Standalone Debt Capacity',project_formula('18_Portfolio','E'),FMT_BN),('Reference Rate',project_formula('11_Debt_Terms','E',key_col='B'),FMT_PCT2),('Credit Spread',project_formula('11_Debt_Terms','F',key_col='B'),'0 "bps"'),('All-in Debt Rate',project_formula('11_Debt_Terms','G',key_col='B'),FMT_PCT2),('Target DSCR',project_formula('11_Debt_Terms','I',key_col='B'),FMT_MULT),('Covenant DSCR',project_formula('11_Debt_Terms','J',key_col='B'),FMT_MULT),('Lock-up DSCR',project_formula('11_Debt_Terms','K',key_col='B'),FMT_MULT),('Debt Tenor',project_formula('11_Debt_Terms','N',key_col='B'),'0'),('DSRA Months',project_formula('11_Debt_Terms','O',key_col='B'),'0')]
    for r,(name,fx,fmt) in enumerate(terms,7): label(ws.cell(r,1),name); formula(ws.cell(r,5),fx,fmt,bg=YELLOW,bold=True)
    section(ws,18,'SENIOR DEBT REPAYMENT SCHEDULE',18)
    ws['A19']='Year Number'; style_cell(ws['A19'],bg=PURPLE,color=WHITE,bold=True,border=True)
    for i in range(10): c=8+i; ws.cell(19,c,i+1); style_cell(ws.cell(19,c),bg=PURPLE,color=WHITE,bold=True,border=True,align='right')
    names=['CFADS','Opening Debt','Interest Expense','Target Debt Service','Principal Repayment','Closing Debt','Actual DSCR','Debt Roll-forward Check','Coverage Status']
    for r,name in enumerate(names,21): label(ws.cell(r,1),name)
    for i in range(10):
        c=8+i; col=ws.cell(1,c).column_letter; pcol=ws.cell(1,9+i).column_letter
        formula(ws.cell(21,c),f"='05_Project_Workings'!{pcol}20",FMT_BN)
        formula(ws.cell(22,c),'=$E$7' if i==0 else f'={ws.cell(26,c-1).coordinate}',FMT_BN,bg=GREY,color=BLACK)
        formula(ws.cell(23,c),f'={col}22*$E$10',FMT_BN,bg=GREY,color=BLACK)
        formula(ws.cell(24,c),f'=MIN({col}21/$E$11,{col}22+{col}23)',FMT_BN,bg=GREY,color=BLACK)
        formula(ws.cell(25,c),f'=MAX(0,MIN({col}22,{col}24-{col}23))',FMT_BN,bg=GREY,color=BLACK)
        formula(ws.cell(26,c),f'=MAX(0,{col}22-{col}25)',FMT_BN,bg=CYAN,color=BLACK,bold=True)
        formula(ws.cell(27,c),f'=IF({col}24=0,"",{col}21/{col}24)',FMT_MULT,bg=YELLOW,color=BLACK,bold=True)
        formula(ws.cell(28,c),f'={col}22-{col}25-{col}26',FMT_BN,color=BLACK)
        formula(ws.cell(29,c),f'=IF({col}27<$E$12,"BREACH","PASS")',bg=WHITE,color=BLACK,bold=True,align='center'); add_status_rules(ws,f'{col}29',f'{col}29')
    section(ws,32,'FINANCING CHECKS',18)
    checks=[('Opening Facility','=H22',FMT_BN),('Final Closing Debt','=Q26',FMT_BN),('Minimum Actual DSCR','=MIN(H27:Q27)',FMT_MULT),('Debt Roll-forward Balance','=SUM(H28:Q28)',FMT_BN),('Schedule Check','=IF(AND(ABS(Q26)<0.01,ABS(SUM(H28:Q28))<0.01),"PASS","REVIEW")','@')]
    for r,(name,fx,fmt) in enumerate(checks,33): label(ws.cell(r,1),name); formula(ws.cell(r,5),fx,fmt,bg=CYAN if r in (35,37) else WHITE,bold=True)
    add_status_rules(ws,'E37','E37')
    ws.column_dimensions['A'].width=36
    for c in range(8,18): ws.column_dimensions[ws.cell(1,c).column_letter].width=12
    chart=LineChart(); chart.title='Senior Debt Amortisation'; chart.y_axis.title='VND bn'; chart.x_axis.title='Year'; chart.add_data(Reference(ws,min_col=8,max_col=17,min_row=26,max_row=26),from_rows=True,titles_from_data=False); chart.set_categories(Reference(ws,min_col=8,max_col=17,min_row=19,max_row=19)); chart.height=7; chart.width=14; ws.add_chart(chart,'A40')
    configure(ws,'A19')


def build_waterfall(wb):
    ws=wb.create_sheet('07_Cashflow_Waterfall',7)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | CASHFLOW WATERFALL','CFADS, senior debt service, Debt Service Reserve Account (DSRA), cash trap and equity distributions',23)
    label(ws['A4'],'Selected Project'); formula(ws['B4'],"='01_Dashboard'!$B$3",align='center',bold=True)
    section(ws,6,'PROJECT CASH WATERFALL',23)
    ws['A7']='Year Number'; style_cell(ws['A7'],bg=PURPLE,color=WHITE,bold=True,border=True)
    for i in range(15): c=8+i; ws.cell(7,c,i+1); style_cell(ws.cell(7,c),bg=PURPLE,color=WHITE,bold=True,border=True,align='right')
    names=['CFADS','Senior Debt Service','Cash Available Before Reserves','DSRA Opening Balance','DSRA Target','DSRA Funding','DSRA Release','DSRA Closing Balance','Lock-up DSCR','Cash Trap','Equity Distribution','Waterfall Check']; rowmap={name:9+i for i,name in enumerate(names)}
    for name,r in rowmap.items(): label(ws.cell(r,1),name)
    for i in range(15):
        c=8+i; col=ws.cell(1,c).column_letter; pcol=ws.cell(1,9+i).column_letter
        formula(ws.cell(rowmap['CFADS'],c),f"='05_Project_Workings'!{pcol}20",FMT_BN)
        if i<10: fcol=ws.cell(1,8+i).column_letter; formula(ws.cell(rowmap['Senior Debt Service'],c),f"='06_Financing_Workings'!{fcol}24",FMT_BN)
        else: ws.cell(rowmap['Senior Debt Service'],c,0); style_cell(ws.cell(rowmap['Senior Debt Service'],c),bg=WHITE,fmt=FMT_BN,border=True,align='right')
        formula(ws.cell(rowmap['Cash Available Before Reserves'],c),f'={col}{rowmap["CFADS"]}-{col}{rowmap["Senior Debt Service"]}',FMT_BN,bg=YELLOW,color=BLACK,bold=True)
        if i==0: ws.cell(rowmap['DSRA Opening Balance'],c,0); style_cell(ws.cell(rowmap['DSRA Opening Balance'],c),bg=GREY,fmt=FMT_BN,border=True,align='right')
        else: formula(ws.cell(rowmap['DSRA Opening Balance'],c),f'={ws.cell(rowmap["DSRA Closing Balance"],c-1).coordinate}',FMT_BN,bg=GREY,color=BLACK)
        if i<10: formula(ws.cell(rowmap['DSRA Target'],c),f'={col}{rowmap["Senior Debt Service"]}*\'06_Financing_Workings\'!$E$15/12',FMT_BN,bg=GREY,color=BLACK)
        else: ws.cell(rowmap['DSRA Target'],c,0); style_cell(ws.cell(rowmap['DSRA Target'],c),bg=GREY,fmt=FMT_BN,border=True,align='right')
        formula(ws.cell(rowmap['DSRA Funding'],c),f'=MAX(0,{col}{rowmap["DSRA Target"]}-{col}{rowmap["DSRA Opening Balance"]})',FMT_BN,bg=GREY,color=BLACK)
        if i==9: formula(ws.cell(rowmap['DSRA Release'],c),f'={col}{rowmap["DSRA Opening Balance"]}+{col}{rowmap["DSRA Funding"]}',FMT_BN,bg=GREY,color=BLACK)
        else: ws.cell(rowmap['DSRA Release'],c,0); style_cell(ws.cell(rowmap['DSRA Release'],c),bg=GREY,fmt=FMT_BN,border=True,align='right')
        formula(ws.cell(rowmap['DSRA Closing Balance'],c),f'=MAX(0,{col}{rowmap["DSRA Opening Balance"]}+{col}{rowmap["DSRA Funding"]}-{col}{rowmap["DSRA Release"]})',FMT_BN,bg=GREY,color=BLACK)
        formula(ws.cell(rowmap['Lock-up DSCR'],c),"='06_Financing_Workings'!$E$13",FMT_MULT,bg=YELLOW,color=BLACK)
        if i<10: fcol=ws.cell(1,8+i).column_letter; formula(ws.cell(rowmap['Cash Trap'],c),f'=IF(\'06_Financing_Workings\'!{fcol}27<{col}{rowmap["Lock-up DSCR"]},MAX(0,{col}{rowmap["Cash Available Before Reserves"]}),0)',FMT_BN,bg=YELLOW,color=BLACK)
        else: ws.cell(rowmap['Cash Trap'],c,0); style_cell(ws.cell(rowmap['Cash Trap'],c),bg=YELLOW,fmt=FMT_BN,border=True,align='right')
        formula(ws.cell(rowmap['Equity Distribution'],c),f'=MAX(0,{col}{rowmap["Cash Available Before Reserves"]}+{col}{rowmap["DSRA Release"]}-{col}{rowmap["Cash Trap"]})',FMT_BN,bg=CYAN,color=BLACK,bold=True)
        formula(ws.cell(rowmap['Waterfall Check'],c),f'={col}{rowmap["CFADS"]}-{col}{rowmap["Senior Debt Service"]}+{col}{rowmap["DSRA Release"]}-{col}{rowmap["Cash Trap"]}-{col}{rowmap["Equity Distribution"]}',FMT_BN,color=BLACK,bold=True)
    ws.column_dimensions['A'].width=36
    for c in range(8,23): ws.column_dimensions[ws.cell(1,c).column_letter].width=11
    configure(ws,'A7')


def build_coverage_returns(wb):
    ws=wb.create_sheet('08_Coverage_Returns',8)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | COVERAGE & RETURNS','Credit coverage and sponsor returns for the selected project',23)
    label(ws['A4'],'Selected Project'); formula(ws['B4'],"='01_Dashboard'!$B$3",align='center',bold=True)
    section(ws,6,'CREDIT COVERAGE',23)
    metrics=[('Minimum DSCR',project_formula('14_Coverage','B'),FMT_MULT),('Covenant DSCR',project_formula('11_Debt_Terms','J',key_col='B'),FMT_MULT),('DSCR Headroom','=B7-B8',FMT_MULT),('LLCR',project_formula('14_Coverage','C'),FMT_MULT),('PLCR',project_formula('14_Coverage','D'),FMT_MULT),('DSRA Target (VND bn)','=' + project_formula('14_Coverage','E')[1:] + '/1000000000',FMT_BN)]
    for r,(name,fx,fmt) in enumerate(metrics,7): label(ws.cell(r,1),name); formula(ws.cell(r,2),fx,fmt,bg=CYAN,bold=True)
    ws.conditional_formatting.add('B9', CellIsRule(operator='lessThan', formula=['0'], fill=fill('FFC7CE')))
    section(ws,15,'PROJECT & EQUITY RETURNS',23)
    returns=[('Project Cost (VND bn)',"='01_Dashboard'!$E$6",FMT_BN),('Equity Required (VND bn)','=' + project_formula('15_Returns_Discount','B')[1:] + '/1000000000',FMT_BN),('Discount Rate',project_formula('15_Returns_Discount','C'),FMT_PCT2),('Project NPV (VND bn)','=' + project_formula('15_Returns_Discount','E')[1:] + '/1000000000',FMT_BN),('Equity NPV (VND bn)','=' + project_formula('15_Returns_Discount','D')[1:] + '/1000000000',FMT_BN)]
    for r,(name,fx,fmt) in enumerate(returns,16): label(ws.cell(r,1),name); formula(ws.cell(r,2),fx,fmt,bg=YELLOW,bold=True)
    ws['A23']='Year'; ws['A24']='Project Cash Flow'; ws['A25']='Equity Cash Flow'
    for r in (23,24,25): style_cell(ws.cell(r,1),bg=PURPLE,color=WHITE,bold=True,border=True)
    for i in range(16):
        c=8+i; ws.cell(23,c,i); style_cell(ws.cell(23,c),bg=PURPLE,color=WHITE,bold=True,border=True,align='right')
        if i==0: formula(ws.cell(24,c),'=-$B$16',FMT_BN,bg=WHITE,color=BLACK); formula(ws.cell(25,c),'=-$B$17',FMT_BN,bg=WHITE,color=BLACK)
        else:
            pcol=ws.cell(1,8+i).column_letter; wcol=ws.cell(1,7+i).column_letter
            formula(ws.cell(24,c),f"='05_Project_Workings'!{pcol}20",FMT_BN)
            formula(ws.cell(25,c),f"='07_Cashflow_Waterfall'!{wcol}19",FMT_BN)
    label(ws['A28'],'Project IRR',bg=CYAN); formula(ws['B28'],'=IFERROR(IRR(H24:W24),"n.m.")',FMT_PCT2,bg=CYAN,color=BLACK,bold=True)
    label(ws['A29'],'Equity IRR',bg=CYAN); formula(ws['B29'],'=IFERROR(IRR(H25:W25),"n.m.")',FMT_PCT2,bg=CYAN,color=BLACK,bold=True)
    ws['D7']='Year'; ws['E7']='Actual DSCR'; ws['F7']='Covenant'
    for c in range(4,7): style_cell(ws.cell(7,c),bg=ORANGE,bold=True,border=True,align='center')
    for i in range(10):
        r=8+i; ws.cell(r,4,i+1); formula(ws.cell(r,5),f"='06_Financing_Workings'!{ws.cell(1,8+i).column_letter}27",FMT_MULT); formula(ws.cell(r,6),'=$B$8',FMT_MULT)
    chart=LineChart(); chart.title='Annual DSCR vs Covenant'; chart.add_data(Reference(ws,min_col=5,max_col=6,min_row=7,max_row=17),titles_from_data=True); chart.set_categories(Reference(ws,min_col=4,min_row=8,max_row=17)); chart.height=7; chart.width=14; ws.add_chart(chart,'H6')
    ws.column_dimensions['A'].width=34; ws.column_dimensions['B'].width=16
    for c in range(8,24): ws.column_dimensions[chr(64+c)].width=11
    configure(ws,'A4')


def build_sensitivity(wb):
    ws=wb.create_sheet('09_Sensitivity',9)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | SENSITIVITY ANALYSIS','Two-dimensional project NPV sensitivity and registered downside outcomes',22)
    label(ws['A4'],'Discount Rate'); formula(ws['B4'],"='08_Coverage_Returns'!$B$18",FMT_PCT2,bg=YELLOW,bold=True)
    section(ws,6,'TWO-DIMENSIONAL PROJECT NPV SENSITIVITY',22)
    shocks=[-0.15,-0.10,-0.05,0,0.05,0.10,0.15]
    ws['G8']='CAPEX \\ CFADS'; style_cell(ws['G8'],bg=YELLOW,color=NAVY,bold=True,border=True,align='center')
    for i,x in enumerate(shocks,8): ws.cell(8,i,x); style_cell(ws.cell(8,i),bg=YELLOW,color=NAVY,bold=True,fmt=FMT_PCT,border=True,align='center')
    for i,x in enumerate(shocks,9):
        ws.cell(i,7,x); style_cell(ws.cell(i,7),bg=YELLOW,color=NAVY,bold=True,fmt=FMT_PCT,border=True)
        for j in range(8,15):
            col=ws.cell(1,j).column_letter
            formula(ws.cell(i,j),f"=NPV($B$4,'05_Project_Workings'!$I$20:$W$20)*(1+{col}$8)-'08_Coverage_Returns'!$B$16*(1+$G{i})",FMT_BN,bg=WHITE,color=BLACK)
    ws.conditional_formatting.add_color_scale('H9:N15',start_type='min',start_color='F8696B',mid_type='percentile',mid_value=50,mid_color='FFEB84',end_type='max',end_color='63BE7B')
    section(ws,18,'REGISTERED DOWNSIDE RESULTS',22)
    headers=['Scenario','CFADS Factor','CAPEX Factor','Interest Rate','Minimum DSCR','Credit Flag']
    for i,h in enumerate(headers,1): style_cell(ws.cell(19,i,h),bg=ORANGE,bold=True,border=True,align='center')
    scenarios=['BASE_SPONSOR','P90_ENERGY','CAPEX_OVERRUN','COD_DELAY','INTEREST_RATE_SHOCK','FX_CRAWL','FX_ONE_OFF','DSO_DELAY','OFFTAKER_PARTIAL_NONPAYMENT','OFFTAKER_DEFAULT_TERMINATION','SITE_CONTINUITY_EVENT','COMBINED_DOWNSIDE','PORTFOLIO_COMMON_FACTOR_DOWNSIDE']
    for r,sid in enumerate(scenarios,20):
        ws.cell(r,1,sid); style_cell(ws.cell(r,1),bg=LIGHT_BLUE,color=LINK_GREEN,bold=True,border=True,wrap=True)
        for c,src,fmt in [(2,'C',FMT_PCT),(3,'D',FMT_PCT),(4,'F',FMT_PCT2),(5,'P',FMT_MULT)]: formula(ws.cell(r,c),f'=INDEX(\'17_Scenarios_Sensitivity\'!${src}$2:${src}$14,MATCH($A{r},\'17_Scenarios_Sensitivity\'!$A$2:$A$14,0))',fmt,bg=YELLOW if c<5 else CYAN,bold=c==5)
        ws.cell(r,6,f'=IF(E{r}<1.20,"BREACH","PASS")'); style_cell(ws.cell(r,6),bg=WHITE,bold=True,border=True,align='center'); add_status_rules(ws,f'F{r}',f'F{r}')
    ws.conditional_formatting.add('A20:F20',FormulaRule(formula=['$A20="BASE_SPONSOR"'],fill=fill(PALE_GREEN),font=Font(name='Arial',color='006100',bold=True)))
    ws.column_dimensions['A'].width=38
    for c in range(2,7): ws.column_dimensions[ws.cell(1,c).column_letter].width=16
    for c in range(8,15): ws.column_dimensions[ws.cell(1,c).column_letter].width=13
    configure(ws,'A6')


def build_ic(wb):
    ws=wb.create_sheet('10_IC_Decision',10)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | INVESTMENT COMMITTEE (IC) & BANKABILITY','Decision framework separating sponsor, lender and diligence views',14)
    label(ws['A4'],'Selected Project'); formula(ws['B4'],"='01_Dashboard'!$B$3",align='center',bold=True)
    section(ws,6,'PROJECT IDENTIFICATION',14)
    info=[('Capacity (MWp)',project_formula('18_Portfolio','D'),FMT_NUM),('Industry',project_formula('18_Portfolio','O'),'@'),('Region',project_formula('18_Portfolio','P'),'@'),('Eligible Shortlist?',project_formula('18_Portfolio','B'),'@'),('Selected Portfolio?',project_formula('18_Portfolio','C'),'@')]
    for r,(name,fx,fmt) in enumerate(info,7): label(ws.cell(r,1),name); formula(ws.cell(r,4),fx,fmt,bg=CYAN,bold=True,align='left' if fmt=='@' else 'right')
    section(ws,14,'SPONSOR / LENDER DECISION',14)
    dec=[('Sponsor Status','B'),('Lender Status','C'),('Binding Issue','D'),('Recommended Action','E'),('Condition 1','F'),('Condition 2','G'),('Condition 3','H'),('Final Classification','I'),('Formula Check','K')]
    for r,(name,col) in enumerate(dec,15):
        label(ws.cell(r,1),name); ws.merge_cells(start_row=r,start_column=4,end_row=r,end_column=14); formula(ws.cell(r,4),project_formula('19_IC_Bankability',col),align='left',bold=name in {'Sponsor Status','Lender Status','Recommended Action','Final Classification','Formula Check'})
        if name in {'Sponsor Status','Lender Status','Final Classification','Formula Check'}: add_status_rules(ws,f'D{r}:N{r}',f'D{r}')
    section(ws,27,'KEY FINANCIAL OUTPUTS',14)
    metrics=[('Project NPV (VND bn)',"='08_Coverage_Returns'!$B$19",FMT_BN),('Equity NPV (VND bn)',"='08_Coverage_Returns'!$B$20",FMT_BN),('Project IRR',"='08_Coverage_Returns'!$B$28",FMT_PCT2),('Equity IRR',"='08_Coverage_Returns'!$B$29",FMT_PCT2),('Minimum DSCR',"='08_Coverage_Returns'!$B$7",FMT_MULT),('LLCR',"='08_Coverage_Returns'!$B$10",FMT_MULT),('PLCR',"='08_Coverage_Returns'!$B$11",FMT_MULT)]
    for r,(name,fx,fmt) in enumerate(metrics,28): label(ws.cell(r,1),name,bg=CYAN); formula(ws.cell(r,4),fx,fmt,bg=CYAN,bold=True)
    ws.column_dimensions['A'].width=34
    for c in range(4,15): ws.column_dimensions[ws.cell(1,c).column_letter].width=14
    configure(ws,'A4')


def build_checks(wb):
    ws=wb.create_sheet('11_Model_Checks',11)
    banner(ws,'VIETGREEN PROJECT FINANCE MODEL | MODEL CHECKS','Integrated model checks and validation register',8)
    section(ws,5,'INTEGRATED FINANCIAL MODEL CHECKS',8)
    headers=['Check','Status','Actual','Purpose']
    for i,h in enumerate(headers,1): style_cell(ws.cell(6,i,h),bg=ORANGE,bold=True,border=True,align='center')
    checks=[
        ('Construction total uses reconcile','=IF(ABS(\'04_Construction_Workings\'!E23-\'01_Dashboard\'!E6)<0.01,"PASS","REVIEW")',"='04_Construction_Workings'!E23",'Construction schedule total uses tie to dashboard project cost'),
        ('Project sources / uses reconcile','=IF(MAX(MAX(\'05_Project_Workings\'!H21:W21),-MIN(\'05_Project_Workings\'!H21:W21))<0.01,"PASS","REVIEW")','=MAX(MAX(\'05_Project_Workings\'!H21:W21),-MIN(\'05_Project_Workings\'!H21:W21))','Annual operating source/use check'),
        ('Debt schedule closes',"='06_Financing_Workings'!$E$37","='06_Financing_Workings'!$E$34",'Senior debt fully amortises and roll-forward balances'),
        ('Waterfall balances','=IF(MAX(MAX(\'07_Cashflow_Waterfall\'!H20:V20),-MIN(\'07_Cashflow_Waterfall\'!H20:V20))<0.01,"PASS","REVIEW")','=MAX(MAX(\'07_Cashflow_Waterfall\'!H20:V20),-MIN(\'07_Cashflow_Waterfall\'!H20:V20))','Cash waterfall closes in every period'),
        ('Coverage above covenant','=IF(\'08_Coverage_Returns\'!$B$7>=\'08_Coverage_Returns\'!$B$8,"PASS","REVIEW")',"='08_Coverage_Returns'!$B$9",'Minimum DSCR compared with covenant'),
    ]
    for r,(name,status,actual,purpose) in enumerate(checks,7):
        ws.cell(r,1,name); style_cell(ws.cell(r,1),bg=LIGHT_BLUE,color=NAVY,bold=True,border=True,wrap=True)
        formula(ws.cell(r,2),status,bg=WHITE,color=BLACK,bold=True,align='center'); add_status_rules(ws,f'B{r}',f'B{r}')
        formula(ws.cell(r,3),actual,FMT_BN if r!=11 else FMT_MULT,bg=WHITE,color=BLACK)
        ws.cell(r,4,purpose); style_cell(ws.cell(r,4),bg=GREY,border=True,wrap=True)
    section(ws,14,'SOURCE MODEL VALIDATION STATUS',8)
    ws['A15']='Native Workbook QA'; ws['B15']='See 21_QA_Audit and validation outputs'; ws.merge_cells('B15:H15')
    style_cell(ws['A15'],bg=LIGHT_BLUE,color=NAVY,bold=True,border=True); style_cell(ws['B15'],bg=WHITE,color=LINK_GREEN,bold=True,border=True)
    ws.column_dimensions['A'].width=36; ws.column_dimensions['B'].width=16; ws.column_dimensions['C'].width=18; ws.column_dimensions['D'].width=62
    configure(ws,'A6')


def _support_header_row(ws):
    """Find the first real table header without disturbing presentation sheets."""
    max_scan_col = min(ws.max_column, 60)
    for r in range(1, min(ws.max_row, 8) + 1):
        populated = sum(1 for c in range(1, max_scan_col + 1) if ws.cell(r, c).value not in (None, ''))
        if populated >= 3:
            return r
    return None


def _status_fill(cell):
    text = str(cell.value).strip().upper() if cell.value is not None else ''
    if text in {'PASS', 'MATCH', 'TRUE', 'YES', 'SELECTED', 'CURRENT'}:
        cell.fill = fill(PALE_GREEN)
        set_font(cell, color='006100', bold=True)
    elif text in {'FAIL', 'BREACH', 'REVIEW', 'REJECT', 'FALSE', 'NO'}:
        cell.fill = fill('FFC7CE')
        set_font(cell, color='9C0006', bold=True)
    elif text in {'CONDITIONAL', 'INVEST_WITH_CONDITIONS', 'RENEGOTIATE', 'WATCH', 'PENDING'}:
        cell.fill = fill(YELLOW)
        set_font(cell, color='9C6500', bold=True)


def polish_support_sheets(wb):
    """Apply a consistent institutional style to the native/support tabs.

    Classic presentation tabs remain untouched. Pure table tabs get dark-blue
    headers, subtle row banding, filters, status highlighting and readable
    widths. Existing bespoke analytical tabs keep their body formatting.
    """
    for ws in wb.worksheets:
        if ws.title in CLASSIC_SHEETS:
            continue
        ws.sheet_view.showGridLines = False
        try:
            ws.sheet_properties.tabColor = BLUE
        except Exception:
            pass

        header_row = _support_header_row(ws)
        if header_row is None:
            continue
        max_col = ws.max_column

        for c in range(1, max_col + 1):
            cell = ws.cell(header_row, c)
            if cell.value in (None, ''):
                continue
            style_cell(cell, bg=BLUE, color=WHITE, bold=True, align='center', wrap=True, border=True)
        ws.row_dimensions[header_row].height = max(ws.row_dimensions[header_row].height or 15, 28)

        if header_row == 1:
            ws.freeze_panes = 'A2'
            try:
                ws.auto_filter.ref = f'A1:{get_column_letter(max_col)}{ws.max_row}'
            except Exception:
                pass

            header_text = {c: str(ws.cell(1, c).value or '').strip().lower() for c in range(1, max_col + 1)}
            status_cols = {
                c for c, h in header_text.items()
                if any(k in h for k in ('status', 'flag', 'selected', 'eligible', 'check'))
            }
            for r in range(2, ws.max_row + 1):
                has_data = any(ws.cell(r, c).value not in (None, '') for c in range(1, max_col + 1))
                if not has_data:
                    continue
                for c in range(1, max_col + 1):
                    cell = ws.cell(r, c)
                    if cell.value in (None, ''):
                        continue
                    if cell.fill is None or cell.fill.fill_type is None:
                        cell.fill = fill('F4F8FC' if r % 2 == 0 else WHITE)
                    value = cell.value
                    if isinstance(value, str) and value.startswith('='):
                        set_font(cell, color=LINK_GREEN if '!' in value else BLACK, size=9)
                    else:
                        set_font(cell, color=BLACK, size=9)
                    cell.alignment = Alignment(
                        horizontal='right' if isinstance(value, (int, float)) and not isinstance(value, bool) else 'left',
                        vertical='center',
                        wrap_text=isinstance(value, str) and len(value) > 28,
                    )
                    cell.border = Border(bottom=THIN)
                    if c in status_cols:
                        _status_fill(cell)

            for c in range(1, max_col + 1):
                letter = get_column_letter(c)
                h = header_text.get(c, '')
                sample = [ws.cell(r, c).value for r in range(1, min(ws.max_row, 60) + 1)]
                max_len = max((len(str(v)) for v in sample if v not in (None, '')), default=8)
                cap = 42 if any(k in h for k in ('detail', 'source', 'url', 'name', 'action', 'condition', 'note')) else 24
                ws.column_dimensions[letter].width = min(max(max_len + 2, 10), cap)
        elif ws.freeze_panes is None:
            ws.freeze_panes = f'A{header_row + 1}'


def build(source: Path, target: Path):
    wb=load_workbook(source)
    for name in CLASSIC_SHEETS:
        if name in wb.sheetnames:
            del wb[name]
    build_title(wb)
    build_dashboard(wb)
    build_model_log(wb)
    build_input_scenarios(wb)
    build_construction(wb)
    build_project_workings(wb)
    build_financing(wb)
    build_waterfall(wb)
    build_coverage_returns(wb)
    build_sensitivity(wb)
    build_ic(wb)
    build_checks(wb)
    for i,name in enumerate(CLASSIC_SHEETS):
        wb._sheets.insert(i, wb._sheets.pop(wb._sheets.index(wb[name])))
    polish_support_sheets(wb)
    try:
        wb.calculation.fullCalcOnLoad = True
        wb.calculation.forceFullCalc = True
        wb.calculation.calcMode = 'auto'
    except Exception:
        pass
    target.parent.mkdir(parents=True, exist_ok=True)
    wb.save(target)


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: build_classic_project_finance_workbook.py SOURCE.xlsx TARGET.xlsx')
    build(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == '__main__':
    main()
