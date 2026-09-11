from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# Institutional infrastructure / project-finance presentation palette.
NAVY_DARK = '17365D'
NAVY = '1F4E78'
LIGHT_BLUE = 'D9EAF7'
VERY_LIGHT_BLUE = 'EEF5FB'
LIGHT_GRAY = 'F2F2F2'
DARK_GRAY = '595959'
WHITE = 'FFFFFF'
BLACK = '000000'
INPUT_BLUE = '0000FF'
LINK_GREEN = '008000'
PASS_GREEN = '548235'
PASS_FILL = 'E2F0D9'
WARN_AMBER = 'BF9000'
WARN_FILL = 'FFF2CC'
FAIL_RED = 'C00000'
FAIL_FILL = 'F4CCCC'
BORDER = 'BFBFBF'

THIN = Side(style='thin', color=BORDER)
MEDIUM_BLUE = Side(style='medium', color=NAVY)

FMT_NUM2 = '#,##0.00;[Red](#,##0.00);-'
FMT_INT = '#,##0;[Red](#,##0);-'
FMT_PCT = '0.0%'
FMT_MULT = '0.00x'


def solid(color: str) -> PatternFill:
    return PatternFill('solid', fgColor=color)


def clear_cell(cell):
    cell.value = None
    cell.fill = PatternFill(fill_type=None)
    cell.font = Font(name='Arial', color=BLACK, size=9)
    cell.border = Border()
    cell.alignment = Alignment()
    cell.number_format = 'General'


def box(cell, *, bg=WHITE, color=BLACK, bold=False, size=9, align='left', wrap=False):
    cell.fill = solid(bg)
    cell.font = Font(name='Arial', color=color, bold=bold, size=size)
    cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
    cell.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def label(cell, text: str):
    cell.value = text
    box(cell, bg=VERY_LIGHT_BLUE, color=DARK_GRAY, bold=True, wrap=True)


def linked_value(cell, formula: str, fmt: str | None = None, align='right'):
    cell.value = formula
    box(cell, bg=WHITE, color=LINK_GREEN, bold=True, size=11, align=align, wrap=True)
    if fmt:
        cell.number_format = fmt


def section(ws, row: int, title: str, end_col: int = 14):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=end_col)
    for col in range(1, end_col + 1):
        ws.cell(row, col).fill = solid(NAVY)
    c = ws.cell(row, 1)
    c.value = title
    c.font = Font(name='Arial', color=WHITE, bold=True, size=10)
    c.alignment = Alignment(vertical='center')
    ws.row_dimensions[row].height = 20


def add_status_rules(ws, rng: str, anchor: str):
    ws.conditional_formatting.add(
        rng,
        FormulaRule(
            formula=[f'OR({anchor}="PASS",{anchor}="SELECTED",{anchor}="YES",{anchor}="ABOVE HURDLE")'],
            fill=solid(PASS_FILL), font=Font(name='Arial', color=PASS_GREEN, bold=True),
        ),
    )
    ws.conditional_formatting.add(
        rng,
        FormulaRule(
            formula=[f'OR({anchor}="FAIL",{anchor}="REJECT",{anchor}="NO",{anchor}="BELOW HURDLE",{anchor}="BREACH")'],
            fill=solid(FAIL_FILL), font=Font(name='Arial', color=FAIL_RED, bold=True),
        ),
    )
    ws.conditional_formatting.add(
        rng,
        FormulaRule(
            formula=[f'OR({anchor}="CONDITIONAL",{anchor}="INVEST WITH CONDITIONS",{anchor}="RENEGOTIATE")'],
            fill=solid(WARN_FILL), font=Font(name='Arial', color=WARN_AMBER, bold=True),
        ),
    )


def lookup_formula(sheet: str, return_col: str, key_col: str = 'A', rows='2:21') -> str:
    start, end = rows.split(':')
    return f'=INDEX(\'{sheet}\'!${return_col}${start}:${return_col}${end},MATCH($B$5,\'{sheet}\'!${key_col}${start}:${key_col}${end},0))'


def rebuild_control(ws):
    for merged in list(ws.merged_cells.ranges):
        ws.unmerge_cells(str(merged))
    ws.conditional_formatting = type(ws.conditional_formatting)()
    ws.data_validations.dataValidation = []

    for row in ws.iter_rows(min_row=1, max_row=max(ws.max_row, 60), min_col=1, max_col=14):
        for cell in row:
            clear_cell(cell)

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = 'A6'

    # Cover / dashboard title.
    ws.merge_cells('A1:N2')
    for row in range(1, 3):
        ws.row_dimensions[row].height = 24
        for col in range(1, 15):
            ws.cell(row, col).fill = solid(NAVY_DARK)
    ws['A1'] = 'VIETGREEN C&I SOLAR | PROJECT FINANCE MODEL'
    ws['A1'].font = Font(name='Arial', color=WHITE, bold=True, size=17)
    ws['A1'].alignment = Alignment(vertical='center')

    ws.merge_cells('A3:N3')
    ws['A3'] = 'Executive review dashboard | Commercial & Industrial Solar | Base case, financing, downside and investment decision'
    ws['A3'].font = Font(name='Arial', color=DARK_GRAY, italic=True, size=9)
    ws.row_dimensions[3].height = 18

    # Model details / project selector.
    section(ws, 4, 'MODEL DETAILS')
    details = [
        ('A5', 'Selected Project', 'B5', 'VG-001'),
        ('D5', 'Model Revision', 'E5', 'V5.1.3'),
        ('G5', 'Presentation Update', 'H5', '12-Sep-2026'),
        ('J5', 'Reporting Currency', 'K5', 'VND'),
        ('M5', 'Model Status', 'N5', 'Screening / Underwriting'),
    ]
    for lc, text, vc, val in details:
        label(ws[lc], text)
        ws[vc] = val
        box(ws[vc], bg=WHITE, color=INPUT_BLUE, bold=True, align='center')
    ws['B5'].fill = solid(WARN_FILL)
    dv = DataValidation(type='list', formula1='"' + ','.join(f'VG-{i:03d}' for i in range(1, 21)) + '"')
    ws.add_data_validation(dv)
    dv.add(ws['B5'])

    # Executive outputs.
    section(ws, 8, 'EXECUTIVE OUTPUTS')
    outputs = [
        ('A9','B9','Installed Capacity (MWp)', lookup_formula('18_Portfolio', 'D'), FMT_NUM2),
        ('D9','E9','P50 Generation (GWh)', lookup_formula('05_Solar_Energy', 'C') + '/1000000', FMT_NUM2),
        ('G9','H9','Project Cost (VND bn)', '=INDEX(\'07_CAPEX_Construction\'!$N$2:$N$999,MATCH($B$5,\'07_CAPEX_Construction\'!$A$2:$A$999,0))/1000000000', FMT_NUM2),
        ('J9','K9','Year-1 CFADS (VND bn)', '=SUMIFS(\'09_Project_CF_CFADS\'!$U:$U,\'09_Project_CF_CFADS\'!$A:$A,$B$5,\'09_Project_CF_CFADS\'!$B:$B,1)/1000000000', FMT_NUM2),
        ('A11','B11','Project NPV (VND bn)', lookup_formula('15_Returns_Discount', 'E') + '/1000000000', FMT_NUM2),
        ('D11','E11','Equity NPV (VND bn)', lookup_formula('15_Returns_Discount', 'D') + '/1000000000', FMT_NUM2),
        ('G11','H11','Debt Capacity (VND bn)', lookup_formula('18_Portfolio', 'E'), FMT_NUM2),
        ('J11','K11','Return Status', '=SUBSTITUTE(' + lookup_formula('15_Returns_Discount', 'I').lstrip('=') + ',"_"," ")', '@'),
    ]
    for lc, vc, text, formula, fmt in outputs:
        label(ws[lc], text)
        linked_value(ws[vc], formula, fmt)
    label(ws['M9'], 'Sponsor')
    linked_value(ws['N9'], lookup_formula('19_IC_Bankability', 'B'), '@', 'center')
    label(ws['M11'], 'Lender')
    linked_value(ws['N11'], lookup_formula('19_IC_Bankability', 'C'), '@', 'center')
    add_status_rules(ws, 'K11', 'K11')
    add_status_rules(ws, 'N9', 'N9')
    add_status_rules(ws, 'N11', 'N11')

    # Financing and credit coverage.
    section(ws, 14, 'FINANCING & CREDIT METRICS')
    debt = [
        ('A15','B15','Leverage Cap', lookup_formula('11_Debt_Terms', 'M', key_col='B'), FMT_PCT),
        ('D15','E15','All-in Debt Rate', lookup_formula('11_Debt_Terms', 'G', key_col='B'), FMT_PCT),
        ('G15','H15','Debt Tenor (years)', lookup_formula('11_Debt_Terms', 'N', key_col='B'), '0'),
        ('J15','K15','Minimum DSCR', lookup_formula('14_Coverage', 'B'), FMT_MULT),
        ('A17','B17','Covenant DSCR', lookup_formula('11_Debt_Terms', 'J', key_col='B'), FMT_MULT),
        ('D17','E17','DSCR Headroom', '=' + lookup_formula('14_Coverage', 'B').lstrip('=') + '-' + lookup_formula('11_Debt_Terms', 'J', key_col='B').lstrip('='), FMT_MULT),
        ('G17','H17','Loan Life Coverage Ratio (LLCR)', lookup_formula('14_Coverage', 'C'), FMT_MULT),
        ('J17','K17','Project Life Coverage Ratio (PLCR)', lookup_formula('14_Coverage', 'D'), FMT_MULT),
    ]
    for lc, vc, text, formula, fmt in debt:
        label(ws[lc], text)
        linked_value(ws[vc], formula, fmt)
    label(ws['M15'], 'Coverage')
    ws['N15'] = '=IF(AND(K15>=B17,H17>=INDEX(\'11_Debt_Terms\'!$L$2:$L$21,MATCH($B$5,\'11_Debt_Terms\'!$B$2:$B$21,0))),K17>=INDEX(\'01_Assumptions\'!$D$2:$D$30,MATCH("ASM-PLCR",\'01_Assumptions\'!$A$2:$A$30,0))),"PASS","REVIEW")'
    box(ws['N15'], bg=WHITE, color=BLACK, bold=True, align='center')
    add_status_rules(ws, 'N15', 'N15')

    # Downside review.
    section(ws, 20, 'DOWNSIDE REVIEW')
    for cell, text in [('A21','Scenario'), ('B21','Portfolio DSCR'), ('D21','Headroom vs 1.20x'), ('E21','Status')]:
        label(ws[cell], text)
    scenarios = [
        ('BASE_SPONSOR','Base Case'),
        ('P90_ENERGY','P90 Energy'),
        ('INTEREST_RATE_SHOCK','Interest Rate Shock'),
        ('FX_ONE_OFF','Foreign Exchange One-off Shock'),
        ('DSO_DELAY','Days Sales Outstanding Delay'),
        ('COD_DELAY','Commercial Operation Date Delay'),
        ('COMBINED_DOWNSIDE','Combined Downside'),
    ]
    for r, (scenario_id, text) in enumerate(scenarios, 22):
        ws.cell(r, 1, text); box(ws.cell(r, 1))
        ws.cell(r, 2, f'=INDEX(\'17_Scenarios_Sensitivity\'!$M$2:$M$14,MATCH("{scenario_id}",\'17_Scenarios_Sensitivity\'!$A$2:$A$14,0))'); box(ws.cell(r, 2), align='right'); ws.cell(r, 2).number_format = FMT_MULT
        ws.cell(r, 4, f'=IF(B{r}="","",B{r}-1.20)'); box(ws.cell(r, 4), align='right'); ws.cell(r, 4).number_format = FMT_MULT
        ws.cell(r, 5, f'=IF(OR(B{r}="",B{r}<1.20),"BREACH","PASS")'); box(ws.cell(r, 5), bold=True, align='center')
        add_status_rules(ws, f'E{r}', f'E{r}')
        ws.row_dimensions[r].height = 18

    ws.merge_cells('G21:N28')
    ws['G21'] = (
        'Reviewer interpretation\n\n'
        'The base financing structure is stress-tested without automatically resizing debt under downside cases. '
        'A Debt Service Coverage Ratio (DSCR) below 1.20x is treated as a covenant breach reference. '
        'This tests whether the original financing remains serviceable under adverse operating and market conditions.'
    )
    box(ws['G21'], bg=LIGHT_GRAY, color=DARK_GRAY, wrap=True)
    ws['G21'].alignment = Alignment(vertical='top', wrap_text=True)
    for r in range(21, 29):
        ws.row_dimensions[r].height = 20 if r > 21 else 26

    # Decision and conditions.
    section(ws, 31, 'INVESTMENT DECISION & CONDITIONS')
    decision = [
        ('A32','B32','Sponsor Status', lookup_formula('19_IC_Bankability', 'B')),
        ('D32','E32','Lender Status', lookup_formula('19_IC_Bankability', 'C')),
        ('G32','H32','Final Classification', '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'I').lstrip('=') + ',"_"," ")'),
        ('J32','K32','Selected in Portfolio?', '=IF(' + lookup_formula('18_Portfolio', 'C').lstrip('=') + '=TRUE,"YES","NO")'),
    ]
    for lc, vc, text, formula in decision:
        label(ws[lc], text)
        linked_value(ws[vc], formula, '@', 'center')
        add_status_rules(ws, vc, vc)
    label(ws['A34'], 'Binding Issue')
    ws.merge_cells('B34:F34')
    linked_value(ws['B34'], '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'D').lstrip('=') + ',"_"," ")', '@', 'left')
    label(ws['G34'], 'Recommended Action')
    ws.merge_cells('H34:N34')
    linked_value(ws['H34'], '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'E').lstrip('=') + ',"_"," ")', '@', 'left')

    # Workbook map.
    section(ws, 37, 'WORKBOOK MAP')
    map_rows = [
        ('Inputs & Evidence', '01_Assumptions | 02_Evidence_Regulatory | 03_Project_Pipeline | 04_Offtakers_Credit_Site'),
        ('Technical & Commercial', '05_Solar_Energy | 06_Load_PPA | 07_CAPEX_Construction | 08_OPEX'),
        ('Cash Flow & Financing', '09_Project_CF_CFADS | 10_Portfolio_CFADS | 11_Debt_Terms | 12_Debt_Sculpting | 13_Reserves_Waterfall'),
        ('Coverage & Returns', '14_Coverage | 15_Returns_Discount | 16_FX_Financing'),
        ('Risk & Decision', '17_Scenarios_Sensitivity | 18_Portfolio | 19_IC_Bankability'),
        ('Validation & QA', '20_External_Validation | 21_QA_Audit | 22_Model_Log'),
    ]
    for r, (group, tabs) in enumerate(map_rows, 38):
        ws.cell(r, 1, group); box(ws.cell(r, 1), bg=LIGHT_BLUE, color=NAVY_DARK, bold=True, align='center')
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=14)
        ws.cell(r, 2, tabs); box(ws.cell(r, 2), bg=WHITE, color=DARK_GRAY, wrap=True)

    # Professional modeling conventions, not a skills showcase.
    section(ws, 46, 'MODEL CONVENTIONS')
    ws.merge_cells('A47:N49')
    ws['A47'] = (
        'Blue font = hardcoded assumption / user-editable input  |  Green font = link from another worksheet  |  '
        'Black font = calculation  |  Red font = external workbook link (if any).  '
        'Zeros display as “-”; negative values display in red parentheses.  '
        'Transaction-specific items that are not evidenced are treated as diligence requirements, not confirmed facts.'
    )
    box(ws['A47'], bg=LIGHT_GRAY, color=DARK_GRAY, wrap=True)
    ws['A47'].alignment = Alignment(vertical='top', wrap_text=True)

    for col, width in {
        1:30, 2:16, 3:3, 4:20, 5:14, 6:3, 7:27, 8:18, 9:3, 10:24, 11:17, 12:3, 13:18, 14:20
    }.items():
        ws.column_dimensions[get_column_letter(col)].width = width


def style_table(ws, *, body_blue=False, widths=None, row_height=36):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = 'A2'
    for cell in ws[1]:
        cell.fill = solid(NAVY)
        cell.font = Font(name='Arial', color=WHITE, bold=True, size=8)
        cell.alignment = Alignment(vertical='center', wrap_text=True)
    ws.row_dimensions[1].height = row_height
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name='Arial', color=INPUT_BLUE if body_blue else BLACK, size=8)
            cell.alignment = Alignment(vertical='center')
    if widths:
        for col_range, width in widths:
            for col in col_range.split(':'):
                ws.column_dimensions[col].width = width


def style_supporting_sheets(wb):
    configs = {
        '02_Evidence_Regulatory': (True, [('A',14),('B',20),('C',20),('D',18),('E',18),('F',18),('G',24),('H',24),('I',24),('J',18),('K',18),('L',18),('M',18),('N',18),('O',18),('P',18)]),
        '03_Project_Pipeline': (True, [('A',14),('B',24)]),
        '04_Offtakers_Credit_Site': (True, [('A',14),('B',24)]),
        '05_Solar_Energy': (False, [('A',13),('B',24)]),
        '06_Load_PPA': (False, [('A',13),('B',16)]),
        '07_CAPEX_Construction': (False, [('A',13),('B',14),('C',14)]),
        '08_OPEX': (False, [('A',13),('B',9)]),
        '09_Project_CF_CFADS': (False, [('A',13),('B',9)]),
        '10_Portfolio_CFADS': (False, [('A',10)]),
        '13_Reserves_Waterfall': (False, [('A',13),('B',9)]),
        '14_Coverage': (False, [('A',13)]),
        '15_Returns_Discount': (False, [('A',13)]),
        '16_FX_Financing': (False, [('A',13),('B',20)]),
        '18_Portfolio': (False, [('A',13),('B',24)]),
        '20_External_Validation': (False, [('A',14),('B',20),('C',28)]),
        '21_QA_Audit': (False, [('A',18),('B',12),('C',24),('D',48)]),
    }
    for name, (blue, widths) in configs.items():
        if name in wb.sheetnames:
            style_table(wb[name], body_blue=blue, widths=widths, row_height=40)

    # Assumption register: separate hardcodes from governance columns.
    if '01_Assumptions' in wb.sheetnames:
        ws = wb['01_Assumptions']
        style_table(ws, body_blue=False, widths=[('A',18),('B',14),('C',30),('D',14)], row_height=40)
        for row in ws.iter_rows(min_row=2):
            row[3].font = Font(name='Arial', color=INPUT_BLUE, size=8)  # value
            if len(row) > 8:
                row[8].font = Font(name='Arial', color=INPUT_BLUE, size=8)  # scenario / sensitivity
        ws.conditional_formatting.add(
            'D2:D40',
            FormulaRule(formula=['$Q2="HIGH"'], fill=solid(WARN_FILL), font=Font(name='Arial', color=INPUT_BLUE, bold=True)),
        )

    # Debt terms: financing inputs in blue, calculated all-in rate in black.
    if '11_Debt_Terms' in wb.sheetnames:
        ws = wb['11_Debt_Terms']
        style_table(ws, body_blue=False, widths=[('A',14),('B',18),('C',16),('D',16)], row_height=40)
        for r in range(2, ws.max_row + 1):
            for c in (5, 6, *range(8, min(ws.max_column, 16) + 1)):
                ws.cell(r, c).font = Font(name='Arial', color=INPUT_BLUE, size=8)
            if ws.max_column >= 7:
                ws.cell(r, 7).font = Font(name='Arial', color=BLACK, bold=True, size=8)

    # Scenario drivers are editable assumptions; result columns remain calculations.
    if '17_Scenarios_Sensitivity' in wb.sheetnames:
        ws = wb['17_Scenarios_Sensitivity']
        style_table(ws, body_blue=False, widths=[('A',28),('B',16)], row_height=42)
        for r in range(2, ws.max_row + 1):
            for c in range(3, min(11, ws.max_column) + 1):
                ws.cell(r, c).font = Font(name='Arial', color=INPUT_BLUE, size=8)
        for r in range(2, ws.max_row + 1):
            if ws.max_column >= 13:
                ws.cell(r, 13).number_format = FMT_MULT
            if ws.max_column >= 16:
                ws.cell(r, 16).number_format = FMT_MULT

    # Decision and QA statuses.
    if '19_IC_Bankability' in wb.sheetnames:
        ws = wb['19_IC_Bankability']
        style_table(ws, body_blue=False, widths=[('A',14),('B',16),('C',16),('D',32),('E',26)], row_height=42)
        ws.conditional_formatting.add('B2:C99', FormulaRule(formula=['B2="PASS"'], fill=solid(PASS_FILL), font=Font(color=PASS_GREEN,bold=True)))
        ws.conditional_formatting.add('B2:C99', FormulaRule(formula=['B2="FAIL"'], fill=solid(FAIL_FILL), font=Font(color=FAIL_RED,bold=True)))
        ws.conditional_formatting.add('B2:C99', FormulaRule(formula=['B2="CONDITIONAL"'], fill=solid(WARN_FILL), font=Font(color=WARN_AMBER,bold=True)))
    if '21_QA_Audit' in wb.sheetnames:
        ws = wb['21_QA_Audit']
        ws.conditional_formatting.add('B2:B99', FormulaRule(formula=['B2="PASS"'], fill=solid(PASS_FILL), font=Font(color=PASS_GREEN,bold=True)))
        ws.conditional_formatting.add('B2:B99', FormulaRule(formula=['B2<>"PASS"'], fill=solid(FAIL_FILL), font=Font(color=FAIL_RED,bold=True)))


def add_model_log(wb):
    if '22_Model_Log' in wb.sheetnames:
        del wb['22_Model_Log']
    ws = wb.create_sheet('22_Model_Log')
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = 'A11'
    ws.merge_cells('A1:H2')
    for row in ws['A1:H2']:
        for cell in row:
            cell.fill = solid(NAVY_DARK)
    ws['A1'] = 'MODEL LOG | VERSION CONTROL & REVIEW RECORD'
    ws['A1'].font = Font(name='Arial', color=WHITE, bold=True, size=15)
    ws['A1'].alignment = Alignment(vertical='center')

    details = [
        ('Model', 'VietGreen C&I Solar Project Finance'),
        ('Purpose', 'Recruiter-facing screening / underwriting model'),
        ('Current Revision', 'V5.1.3 / presentation refresh 12-Sep-2026'),
        ('Reporting Currency', 'VND'),
        ('Governance', 'Public-data reconstruction; transaction evidence limitations explicitly disclosed'),
    ]
    for r, (k, v) in enumerate(details, 4):
        label(ws.cell(r, 1), k)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
        ws.cell(r, 2, v); box(ws.cell(r, 2), color=DARK_GRAY, wrap=True)

    ws.merge_cells('A10:H10')
    ws['A10'] = 'CHANGE LOG'
    ws['A10'].fill = solid(NAVY)
    ws['A10'].font = Font(name='Arial', color=WHITE, bold=True, size=10)
    headers = ['Revision','Date','Change Type','Area','Description','Prepared By','Review Status','Notes']
    for c, text in enumerate(headers, 1):
        ws.cell(11, c, text)
        box(ws.cell(11, c), bg=LIGHT_BLUE, color=NAVY_DARK, bold=True, wrap=True)
    rows = [
        ['V5.1.3','31-Aug-2026','Model release','Core model','Verified operating, debt, coverage and scenario release','VietGreen','Released','Deterministic core release'],
        ['P1','10-Sep-2026','Presentation','Recruiter workbook','Added recruiter-facing presentation and website workbook distribution','VietGreen','Reviewed','Core workbook retained separately'],
        ['P2','12-Sep-2026','Presentation','Workbook style','Reformatted to institutional infrastructure-model presentation standard','VietGreen','Reviewed','Restrained navy / blue / gray style; professional model conventions'],
    ]
    for r, values in enumerate(rows, 12):
        for c, val in enumerate(values, 1):
            ws.cell(r, c, val)
            box(ws.cell(r, c), color=DARK_GRAY, wrap=True)

    ws.merge_cells('A17:H17')
    ws['A17'] = 'REVIEW PRINCIPLES'
    ws['A17'].fill = solid(NAVY)
    ws['A17'].font = Font(name='Arial', color=WHITE, bold=True, size=10)
    ws.merge_cells('A18:H22')
    ws['A18'] = (
        '1. Inputs, calculations and outputs are visually distinguished.\n'
        '2. Cash Flow Available for Debt Service (CFADS), Debt Service Coverage Ratio (DSCR), Loan Life Coverage Ratio (LLCR) and Project Life Coverage Ratio (PLCR) remain traceable to supporting schedules.\n'
        '3. Transaction-specific items such as an executed Power Purchase Agreement (PPA), lender term sheet and independent technical due diligence are not represented as confirmed where evidence is unavailable.\n'
        '4. Checks and reconciliation items remain visible for reviewer inspection.'
    )
    box(ws['A18'], bg=LIGHT_GRAY, color=DARK_GRAY, wrap=True)
    ws['A18'].alignment = Alignment(vertical='top', wrap_text=True)

    widths = [16,14,18,20,48,16,16,36]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[11].height = 30


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit('usage: build_recruiter_company_workbook.py INPUT_XLSX [OUTPUT_XLSX]')
    source = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) == 3 else source.with_name('vietgreen_company_style.xlsx')
    output.parent.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(source)
    required = {'00_Control','01_Assumptions','11_Debt_Terms','17_Scenarios_Sensitivity','18_Portfolio','19_IC_Bankability'}
    missing = required.difference(wb.sheetnames)
    if missing:
        raise SystemExit(f'missing expected workbook sheets: {sorted(missing)}')

    rebuild_control(wb['00_Control'])
    style_supporting_sheets(wb)
    add_model_log(wb)
    wb.save(output)
    print(f'Institutional-style recruiter workbook: {output}')


if __name__ == '__main__':
    main()
