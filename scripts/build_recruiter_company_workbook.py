from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

NAVY_DARK = '0B1F33'
NAVY = '17365D'
SLATE = '44546A'
LIGHT_GRAY = 'F2F2F2'
VERY_LIGHT = 'F8F9FB'
WHITE = 'FFFFFF'
BLACK = '000000'
INPUT_BLUE = '0000FF'
PASS_GREEN = '548235'
PASS_FILL = 'E2F0D9'
WARN_AMBER = 'BF9000'
WARN_FILL = 'FFF2CC'
FAIL_RED = 'C00000'
FAIL_FILL = 'F4CCCC'
BORDER = 'D9D9D9'

THIN = Side(style='thin', color=BORDER)


def solid(color: str) -> PatternFill:
    return PatternFill('solid', fgColor=color)


def box(cell, *, bg=WHITE, color=BLACK, bold=False, size=10, align='left', wrap=False):
    cell.fill = solid(bg)
    cell.font = Font(name='Aptos', color=color, bold=bold, size=size)
    cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
    cell.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def label(cell, text: str):
    cell.value = text
    box(cell, bg=LIGHT_GRAY, color=SLATE, bold=True, wrap=True)


def value(cell, formula: str, fmt: str | None = None, align='right'):
    cell.value = formula
    box(cell, bg=WHITE, color=BLACK, bold=True, size=12, align=align, wrap=True)
    if fmt:
        cell.number_format = fmt


def section(ws, row: int, title: str):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=12)
    for col in range(1, 13):
        ws.cell(row, col).fill = solid(NAVY)
    c = ws.cell(row, 1)
    c.value = title
    c.font = Font(name='Aptos Display', color=WHITE, bold=True, size=11)
    c.alignment = Alignment(vertical='center')
    ws.row_dimensions[row].height = 22


def add_status_rules(ws, rng: str, anchor: str):
    ws.conditional_formatting.add(
        rng,
        FormulaRule(
            formula=[f'OR({anchor}="PASS",{anchor}="SELECTED")'],
            fill=solid(PASS_FILL), font=Font(color=PASS_GREEN, bold=True),
        ),
    )
    ws.conditional_formatting.add(
        rng,
        FormulaRule(
            formula=[f'OR({anchor}="FAIL",{anchor}="REJECT",{anchor}="BELOW HURDLE")'],
            fill=solid(FAIL_FILL), font=Font(color=FAIL_RED, bold=True),
        ),
    )
    ws.conditional_formatting.add(
        rng,
        FormulaRule(
            formula=[f'OR({anchor}="CONDITIONAL",{anchor}="INVEST WITH CONDITIONS",{anchor}="RENEGOTIATE")'],
            fill=solid(WARN_FILL), font=Font(color=WARN_AMBER, bold=True),
        ),
    )


def lookup_formula(sheet: str, return_col: str, key_col: str = 'A', rows='2:21') -> str:
    start, end = rows.split(':')
    return f'=INDEX(\'{sheet}\'!${return_col}${start}:${return_col}${end},MATCH($B$5,\'{sheet}\'!${key_col}${start}:${key_col}${end},0))'


def reset_control(ws):
    for merged in list(ws.merged_cells.ranges):
        ws.unmerge_cells(str(merged))
    ws.conditional_formatting = type(ws.conditional_formatting)()
    ws.data_validations.dataValidation = []

    for row in ws.iter_rows(min_row=1, max_row=max(ws.max_row, 70), min_col=1, max_col=12):
        for c in row:
            c.value = None
            c.fill = PatternFill(fill_type=None)
            c.font = Font(name='Aptos', color=BLACK, size=10)
            c.border = Border()
            c.alignment = Alignment()
            c.number_format = 'General'

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = 'A8'

    ws.merge_cells('A1:L2')
    for row in range(1, 3):
        ws.row_dimensions[row].height = 24
        for col in range(1, 13):
            ws.cell(row, col).fill = solid(NAVY_DARK)
    ws['A1'] = 'VIETGREEN C&I SOLAR | PROJECT FINANCE INVESTMENT SUMMARY'
    ws['A1'].font = Font(name='Aptos Display', color=WHITE, bold=True, size=18)
    ws['A1'].alignment = Alignment(vertical='center')

    ws.merge_cells('A3:L3')
    ws['A3'] = 'Base-case screening and underwriting view | Formula-driven recruiter workbook | VND unless stated otherwise'
    ws['A3'].font = Font(name='Aptos', color=SLATE, italic=True, size=10)
    ws.row_dimensions[3].height = 20

    label(ws['A5'], 'Selected Project')
    ws['B5'] = 'VG-001'
    box(ws['B5'], bg=WARN_FILL, color=INPUT_BLUE, bold=True, align='center')
    dv = DataValidation(type='list', formula1='"' + ','.join(f'VG-{i:03d}' for i in range(1, 21)) + '"')
    ws.add_data_validation(dv)
    dv.add(ws['B5'])

    label(ws['D5'], 'Sponsor Status')
    value(ws['E5'], lookup_formula('19_IC_Bankability', 'B'), align='center')
    label(ws['G5'], 'Lender Status')
    value(ws['H5'], lookup_formula('19_IC_Bankability', 'C'), align='center')
    label(ws['J5'], 'Final Classification')
    ws.merge_cells('K5:L5')
    value(ws['K5'], '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'I').lstrip('=') + ',"_"," ")', align='center')
    add_status_rules(ws, 'E5', 'E5')
    add_status_rules(ws, 'H5', 'H5')
    add_status_rules(ws, 'K5:L5', 'K5')

    ws.merge_cells('A7:B7'); ws['A7'] = 'Current Recommendation'
    ws.merge_cells('C7:H7'); ws['C7'] = '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'E').lstrip('=') + ',"_"," ")'
    ws.merge_cells('I7:J7'); ws['I7'] = 'Key Binding Issue'
    ws.merge_cells('K7:L7'); ws['K7'] = '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'D').lstrip('=') + ',"_"," ")'
    for rg in ('A7:B7', 'I7:J7'):
        for row in ws[rg]:
            for c in row:
                c.fill = solid(NAVY)
                c.font = Font(name='Aptos', color=WHITE, bold=True)
                c.alignment = Alignment(vertical='center')
    for rg in ('C7:H7', 'K7:L7'):
        for row in ws[rg]:
            for c in row:
                box(c, bg=VERY_LIGHT, bold=True, wrap=True)

    section(ws, 10, '1. Investment Snapshot')
    snapshot = [
        ('A11','B11','Capacity (MWp)', lookup_formula('18_Portfolio', 'D'), '#,##0.00'),
        ('D11','E11','P50 Generation (GWh)', lookup_formula('05_Solar_Energy', 'C') + '/1000000', '#,##0.00'),
        ('G11','H11','Project Cost (VND bn)', '=INDEX(\'07_CAPEX_Construction\'!$N$2:$N$999,MATCH($B$5,\'07_CAPEX_Construction\'!$A$2:$A$999,0))/1000000000', '#,##0.00;[Red](#,##0.00);-'),
        ('J11','K11','Year-1 CFADS (VND bn)', '=SUMIFS(\'09_Project_CF_CFADS\'!$U:$U,\'09_Project_CF_CFADS\'!$A:$A,$B$5,\'09_Project_CF_CFADS\'!$B:$B,1)/1000000000', '#,##0.00;[Red](#,##0.00);-'),
        ('A12','B12','Annual Load (GWh)', lookup_formula('06_Load_PPA', 'C') + '/1000000', '#,##0.00'),
        ('D12','E12','Self-Consumption', lookup_formula('06_Load_PPA', 'G'), '0.0%'),
        ('G12','H12','Solar Share of Load', lookup_formula('06_Load_PPA', 'H'), '0.0%'),
        ('J12','K12','Year-1 Revenue (VND bn)', '=SUMIFS(\'09_Project_CF_CFADS\'!$C:$C,\'09_Project_CF_CFADS\'!$A:$A,$B$5,\'09_Project_CF_CFADS\'!$B:$B,1)/1000000000', '#,##0.00;[Red](#,##0.00);-'),
    ]
    for lc, vc, text, formula, fmt in snapshot:
        label(ws[lc], text); value(ws[vc], formula, fmt)
    ws.merge_cells('L11:L12')
    ws['L11'] = 'Details: tabs 05–10'
    ws['L11'].font = Font(name='Aptos', color=SLATE, italic=True, size=9)
    ws['L11'].alignment = Alignment(wrap_text=True, vertical='center')

    section(ws, 15, '2. Returns & Value')
    returns = [
        ('A16','B16','Project NPV (VND bn)', lookup_formula('15_Returns_Discount', 'E') + '/1000000000', '#,##0.00;[Red](#,##0.00);-'),
        ('D16','E16','Equity NPV (VND bn)', lookup_formula('15_Returns_Discount', 'D') + '/1000000000', '#,##0.00;[Red](#,##0.00);-'),
        ('G16','H16','Discount Rate', lookup_formula('15_Returns_Discount', 'C'), '0.0%'),
        ('J16','K16','Return Status', '=SUBSTITUTE(' + lookup_formula('15_Returns_Discount', 'I').lstrip('=') + ',"_"," ")', '@'),
    ]
    for lc, vc, text, formula, fmt in returns:
        label(ws[lc], text); value(ws[vc], formula, fmt)
    ws.conditional_formatting.add('K16', FormulaRule(formula=['K16="BELOW HURDLE"'], fill=solid(FAIL_FILL), font=Font(color=FAIL_RED,bold=True)))
    ws.conditional_formatting.add('K16', FormulaRule(formula=['K16="ABOVE HURDLE"'], fill=solid(PASS_FILL), font=Font(color=PASS_GREEN,bold=True)))
    ws['L16'] = 'Detail: tab 15'; ws['L16'].font = Font(name='Aptos', color=SLATE, italic=True, size=9)

    section(ws, 19, '3. Debt & Credit Coverage')
    debt = [
        ('A20','B20','Debt Capacity (VND bn)', lookup_formula('18_Portfolio', 'E'), '#,##0.00;[Red](#,##0.00);-'),
        ('D20','E20','Leverage Cap', lookup_formula('11_Debt_Terms', 'M', key_col='B'), '0.0%'),
        ('G20','H20','All-in Debt Rate', lookup_formula('11_Debt_Terms', 'G', key_col='B'), '0.0%'),
        ('J20','K20','Debt Tenor (years)', lookup_formula('11_Debt_Terms', 'N', key_col='B'), '0'),
        ('A21','B21','Minimum DSCR', lookup_formula('14_Coverage', 'B'), '0.00x'),
        ('D21','E21','Covenant DSCR', lookup_formula('11_Debt_Terms', 'J', key_col='B'), '0.00x'),
        ('G21','H21','LLCR', lookup_formula('14_Coverage', 'C'), '0.00x'),
        ('J21','K21','PLCR', lookup_formula('14_Coverage', 'D'), '0.00x'),
    ]
    for lc, vc, text, formula, fmt in debt:
        label(ws[lc], text); value(ws[vc], formula, fmt)
    ws.merge_cells('L20:L21')
    ws['L20'] = 'Details: tabs 11–14'
    ws['L20'].font = Font(name='Aptos', color=SLATE, italic=True, size=9)
    ws['L20'].alignment = Alignment(wrap_text=True, vertical='center')

    section(ws, 24, '4. Downside & Scenario Review')
    for cell, text in [('A25','Scenario'),('B25','Portfolio DSCR'),('D25','Headroom vs 1.20x'),('E25','Status')]:
        label(ws[cell], text)
    scenarios = [
        ('BASE_SPONSOR','Base Case'), ('P90_ENERGY','P90 Energy'),
        ('INTEREST_RATE_SHOCK','Interest Rate Shock'), ('FX_ONE_OFF','FX One-off Shock'),
        ('DSO_DELAY','DSO Delay'), ('COD_DELAY','COD Delay'), ('COMBINED_DOWNSIDE','Combined Downside'),
    ]
    for r, (scenario_id, text) in enumerate(scenarios, 26):
        ws.cell(r, 1, text); box(ws.cell(r, 1))
        ws.cell(r, 2, f'=INDEX(\'17_Scenarios_Sensitivity\'!$M$2:$M$14,MATCH("{scenario_id}",\'17_Scenarios_Sensitivity\'!$A$2:$A$14,0))'); box(ws.cell(r, 2)); ws.cell(r, 2).number_format = '0.00x'
        ws.cell(r, 4, f'=IF(B{r}="","",B{r}-1.20)'); box(ws.cell(r, 4)); ws.cell(r, 4).number_format = '0.00x'
        ws.cell(r, 5, f'=IF(OR(B{r}="",B{r}<1.20),"BREACH","PASS")'); box(ws.cell(r, 5), bold=True)
        ws.conditional_formatting.add(f'E{r}', FormulaRule(formula=[f'E{r}="BREACH"'], fill=solid(FAIL_FILL), font=Font(color=FAIL_RED,bold=True)))
        ws.conditional_formatting.add(f'E{r}', FormulaRule(formula=[f'E{r}="PASS"'], font=Font(color=PASS_GREEN,bold=True)))
    ws.merge_cells('F25:L32')
    ws['F25'] = ('Downside interpretation\n\nThe base financing case is compared with operating, market and execution stresses. '
                 'Coverage below the 1.20x covenant reference is flagged as a breach. Debt is not automatically resized under stress, '
                 'so the review shows whether base-case financing remains serviceable.')
    box(ws['F25'], bg=VERY_LIGHT, color=SLATE, wrap=True)
    ws['F25'].alignment = Alignment(vertical='top', wrap_text=True)

    section(ws, 35, '5. Investment Decision & Key Conditions')
    label(ws['A36'], 'Sponsor Status'); value(ws['B36'], lookup_formula('19_IC_Bankability', 'B'), '@')
    label(ws['D36'], 'Lender Status'); value(ws['E36'], lookup_formula('19_IC_Bankability', 'C'), '@')
    label(ws['G36'], 'Final Classification'); ws.merge_cells('H36:L36'); value(ws['H36'], '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'I').lstrip('=') + ',"_"," ")', '@', 'center')
    label(ws['A37'], 'Selected in Portfolio?'); value(ws['B37'], '=IF(' + lookup_formula('18_Portfolio', 'C').lstrip('=') + '=TRUE,"YES","NO")', '@')
    label(ws['D37'], 'Pooled Debt (VND bn)'); value(ws['E37'], lookup_formula('18_Portfolio', 'G'), '#,##0.00;[Red](#,##0.00);-')
    label(ws['G37'], 'Pooled Equity (VND bn)'); value(ws['H37'], lookup_formula('18_Portfolio', 'H'), '#,##0.00;[Red](#,##0.00);-')
    label(ws['A38'], 'Binding Issue'); ws.merge_cells('B38:F38'); value(ws['B38'], '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'D').lstrip('=') + ',"_"," ")', '@', 'left')
    label(ws['G38'], 'Recommended Action'); ws.merge_cells('H38:L38'); value(ws['H38'], '=SUBSTITUTE(' + lookup_formula('19_IC_Bankability', 'E').lstrip('=') + ',"_"," ")', '@', 'left')
    add_status_rules(ws, 'B36', 'B36'); add_status_rules(ws, 'E36', 'E36'); add_status_rules(ws, 'H36:L36', 'H36')

    section(ws, 41, '6. Review Notes')
    ws.merge_cells('A42:L46')
    ws['A42'] = ('• Public-data / synthetic reconstruction for screening and underwriting analysis; not a live transaction approval.\n'
                 '• Reference tariff assumptions are not executed PPAs; modeled debt terms are not actual lender commitments.\n'
                 '• A live decision would require executed PPA, measured customer load, lender term sheet, independent technical validation and final legal / tax diligence.\n'
                 '• Detailed operating, financing, scenario and QA calculations remain available in the underlying tabs.')
    box(ws['A42'], bg=VERY_LIGHT, color=SLATE, wrap=True)
    ws['A42'].alignment = Alignment(vertical='top', wrap_text=True)

    for col, width in {1:22,2:15,3:3,4:22,5:15,6:3,7:22,8:15,9:3,10:22,11:16,12:18}.items():
        ws.column_dimensions[get_column_letter(col)].width = width


def style_generic_headers(wb):
    for name in wb.sheetnames:
        if name in {'00_Control', '12_Debt_Sculpting'}:
            continue
        ws = wb[name]
        ws.sheet_view.showGridLines = False
        if ws.max_row < 1:
            continue
        for cell in ws[1]:
            cell.fill = solid(NAVY)
            cell.font = Font(name='Aptos', color=WHITE, bold=True, size=10)
            cell.alignment = Alignment(vertical='center', wrap_text=True)
        ws.row_dimensions[1].height = max(ws.row_dimensions[1].height or 15, 24)

    if '11_Debt_Terms' in wb.sheetnames:
        ws = wb['11_Debt_Terms']
        for r in range(2, min(ws.max_row, 21) + 1):
            for c in (5, 6, *range(8, 17)):
                ws.cell(r, c).font = Font(name='Aptos', color=INPUT_BLUE)
            ws.cell(r, 7).font = Font(name='Aptos', color=BLACK, bold=True)
    if '17_Scenarios_Sensitivity' in wb.sheetnames:
        ws = wb['17_Scenarios_Sensitivity']
        for r in range(2, min(ws.max_row, 14) + 1):
            for c in range(3, 12):
                ws.cell(r, c).font = Font(name='Aptos', color=INPUT_BLUE)


def restyle_debt_sculpting(ws):
    ws.sheet_view.showGridLines = False
    for row in ws['A1:J2']:
        for c in row:
            c.fill = solid(NAVY_DARK)
    for c in ws[6]:
        c.fill = solid(NAVY)
        c.font = Font(name='Aptos', color=WHITE, bold=True)
        c.alignment = Alignment(vertical='center', wrap_text=True)

    if 'A19:J19' not in [str(rng) for rng in ws.merged_cells.ranges]:
        ws.merge_cells('A19:J19')
    ws['A19'] = 'DEBT SCULPTING CONTROL CHECKS'
    ws['A19'].fill = solid(LIGHT_GRAY)
    ws['A19'].font = Font(name='Aptos', color=NAVY, bold=True)
    checks = [
        ('Opening Facility (VND bn)', '=F4', 'Opening debt used in the sculpted schedule', '#,##0.00;[Red](#,##0.00);-'),
        ('Final Closing Debt (VND bn)', '=H16', 'Should amortize to zero by maturity', '#,##0.00;[Red](#,##0.00);-'),
        ('Minimum Actual DSCR', '=MIN(I7:I16)', 'Lowest annual coverage in the sculpted schedule', '0.00x'),
        ('Schedule Balance Check', '=IF(COUNTIF(J7:J16,"REVIEW")=0,"PASS","REVIEW")', 'Opening − principal − closing balance control', '@'),
    ]
    for r, (name, formula, note, fmt) in enumerate(checks, 20):
        ws.cell(r, 1, name); ws.cell(r, 2, formula); ws.cell(r, 3, note)
        box(ws.cell(r, 1), color=SLATE, bold=True, wrap=True)
        box(ws.cell(r, 2), bold=True, wrap=True); ws.cell(r, 2).number_format = fmt
        box(ws.cell(r, 3), color=SLATE, wrap=True)
    ws.column_dimensions['A'].width = 24
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 34


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit('usage: build_recruiter_company_workbook.py INPUT_XLSX [OUTPUT_XLSX]')
    source = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) == 3 else source.with_name('vietgreen_company_style.xlsx')
    output.parent.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(source)
    required = {'00_Control', '12_Debt_Sculpting', '19_IC_Bankability', '18_Portfolio'}
    missing = required.difference(wb.sheetnames)
    if missing:
        raise SystemExit(f'missing expected workbook sheets: {sorted(missing)}')

    reset_control(wb['00_Control'])
    style_generic_headers(wb)
    restyle_debt_sculpting(wb['12_Debt_Sculpting'])
    wb.save(output)
    print(f'Company-style recruiter workbook: {output}')


if __name__ == '__main__':
    main()
