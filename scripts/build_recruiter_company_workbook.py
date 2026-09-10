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

thin = Side(style='thin', color=BORDER)


def fill(hex_color: str) -> PatternFill:
    return PatternFill('solid', fgColor=hex_color)


def box(cell, *, bg=WHITE, color=BLACK, bold=False, size=10, align='left', wrap=False):
    cell.fill = fill(bg)
    cell.font = Font(name='Aptos', color=color, bold=bold, size=size)
    cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap)
    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)


def label(cell, text):
    cell.value = text
    box(cell, bg=LIGHT_GRAY, color=SLATE, bold=True, wrap=True)


def value(cell, formula, number_format=None, align='right'):
    cell.value = formula
    box(cell, bg=WHITE, color=BLACK, bold=True, size=12, align=align, wrap=True)
    if number_format:
        cell.number_format = number_format


def section(ws, row: int, title: str):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=12)
    c = ws.cell(row, 1, title)
    c.fill = fill(NAVY)
    c.font = Font(name='Aptos Display', color=WHITE, bold=True, size=11)
    c.alignment = Alignment(horizontal='left', vertical='center')
    ws.row_dimensions[row].height = 22
    for col in range(2, 13):
        ws.cell(row, col).fill = fill(NAVY)


def add_status_rules(ws, rng: str, anchor: str):
    ws.conditional_formatting.add(
        rng,
        FormulaRule(formula=[f'OR({anchor}="PASS",{anchor}="SELECTED")'],
                    fill=fill(PASS_FILL), font=Font(color=PASS_GREEN, bold=True)),
    )
    ws.conditional_formatting.add(
        rng,
        FormulaRule(formula=[f'OR({anchor}="FAIL",{anchor}="REJECT",{anchor}="BELOW HURDLE")'],
                    fill=fill(FAIL_FILL), font=Font(color=FAIL_RED, bold=True)),
    )
    ws.conditional_formatting.add(
        rng,
        FormulaRule(formula=[f'OR({anchor}="CONDITIONAL",{anchor}="INVEST WITH CONDITIONS",{anchor}="RENEGOTIATE")'],
                    fill=fill(WARN_FILL), font=Font(color=WARN_AMBER, bold=True)),
    )


def reset_control(ws):
    for merged in list(ws.merged_cells.ranges):
        ws.unmerge_cells(str(merged))
    ws.conditional_formatting = type(ws.conditional_formatting)()

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
    ws['A1'] = 'VIETGREEN C&I SOLAR | PROJECT FINANCE INVESTMENT SUMMARY'
    ws['A1'].fill = fill(NAVY_DARK)
    ws['A1'].font = Font(name='Aptos Display', color=WHITE, bold=True, size=18)
    ws['A1'].alignment = Alignment(horizontal='left', vertical='center')
    for row in range(1, 3):
        ws.row_dimensions[row].height = 24
        for col in range(1, 13):
            ws.cell(row, col).fill = fill(NAVY_DARK)

    ws.merge_cells('A3:L3')
    ws['A3'] = 'Base-case screening and underwriting view | Public-data reconstruction | VND unless stated otherwise'
    ws['A3'].font = Font(name='Aptos', color=SLATE, italic=True, size=10)
    ws['A3'].alignment = Alignment(vertical='center')
    ws.row_dimensions[3].height = 20

    label(ws['A5'], 'Selected Project')
    ws.data_validations.dataValidation = []
    ws['B5'] = 'VG-001'
    box(ws['B5'], bg=WARN_FILL, color=INPUT_BLUE, bold=True, align='center')
    dv = DataValidation(type='list', formula1='"' + ','.join(f'VG-{i:03d}' for i in range(1, 21)) + '"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(ws['B5'])

    label(ws['D5'], 'Sponsor Status')
    value(ws['E5'], '=INDEX(\'19_IC_Bankability\'!$B$6:$B$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0))', align='center')
    label(ws['G5'], 'Lender Status')
    value(ws['H5'], '=INDEX(\'19_IC_Bankability\'!$C$6:$C$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0))', align='center')
    label(ws['J5'], 'Final Classification')
    ws.merge_cells('K5:L5')
    value(ws['K5'], '=SUBSTITUTE(INDEX(\'19_IC_Bankability\'!$I$6:$I$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0)),"_"," ")', align='center')
    add_status_rules(ws, 'E5', 'E5')
    add_status_rules(ws, 'H5', 'H5')
    add_status_rules(ws, 'K5:L5', 'K5')

    ws.merge_cells('A7:B7'); ws['A7'] = 'Current Recommendation'
    ws.merge_cells('C7:H7'); ws['C7'] = '=SUBSTITUTE(INDEX(\'19_IC_Bankability\'!$E$6:$E$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0)),"_"," ")'
    ws.merge_cells('I7:J7'); ws['I7'] = 'Key Binding Issue'
    ws.merge_cells('K7:L7'); ws['K7'] = '=SUBSTITUTE(INDEX(\'19_IC_Bankability\'!$D$6:$D$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0)),"_"," ")'
    for rg in ('A7:B7', 'I7:J7'):
        for row in ws[rg]:
            for c in row:
                c.fill = fill(NAVY); c.font = Font(name='Aptos', color=WHITE, bold=True)
                c.alignment = Alignment(vertical='center')
    for rg in ('C7:H7', 'K7:L7'):
        for row in ws[rg]:
            for c in row:
                box(c, bg=VERY_LIGHT, color=BLACK, bold=True, wrap=True)

    section(ws, 10, '1. Investment Snapshot')
    metrics = [
        ('A11','B11','Capacity (MWp)', '=INDEX(\'18_Portfolio\'!$D$2:$D$21,MATCH($B$5,\'18_Portfolio\'!$A$2:$A$21,0))', '#,##0.00'),
        ('D11','E11','P50 Generation (GWh)', '=INDEX(\'05_Solar_Energy\'!$C$2:$C$21,MATCH($B$5,\'05_Solar_Energy\'!$A$2:$A$21,0))/1000000', '#,##0.00'),
        ('G11','H11','Project Cost (VND bn)', '=INDEX(\'07_CAPEX_Construction\'!$N$2:$N$999,MATCH($B$5,\'07_CAPEX_Construction\'!$A$2:$A$999,0))/1000000000', '#,##0.00;[Red](#,##0.00);-'),
        ('J11','K11','Year-1 CFADS (VND bn)', '=\'09_Project_CF_CFADS\'!D15', '#,##0.00;[Red](#,##0.00);-'),
        ('A12','B12','Annual Load (GWh)', '=INDEX(\'06_Load_PPA\'!$C$2:$C$21,MATCH($B$5,\'06_Load_PPA\'!$A$2:$A$21,0))/1000000', '#,##0.00'),
        ('D12','E12','Self-Consumption', '=INDEX(\'06_Load_PPA\'!$G$2:$G$21,MATCH($B$5,\'06_Load_PPA\'!$A$2:$A$21,0))', '0.0%'),
        ('G12','H12','Solar Share of Load', '=INDEX(\'06_Load_PPA\'!$H$2:$H$21,MATCH($B$5,\'06_Load_PPA\'!$A$2:$A$21,0))', '0.0%'),
        ('J12','K12','Year-1 Revenue (VND bn)', '=\'09_Project_CF_CFADS\'!D7', '#,##0.00;[Red](#,##0.00);-'),
    ]
    for lc, vc, txt, f, fmt in metrics:
        label(ws[lc], txt); value(ws[vc], f, fmt)
    ws.merge_cells('L11:L12'); ws['L11'] = 'Details: tabs 05–10'
    ws['L11'].font = Font(name='Aptos', color=SLATE, italic=True, size=9)
    ws['L11'].alignment = Alignment(wrap_text=True, vertical='center')

    section(ws, 15, '2. Returns & Value')
    ret = [
        ('A16','B16','Project NPV (VND bn)', '=\'15_Returns_Discount\'!E7', '#,##0.00;[Red](#,##0.00);-'),
        ('D16','E16','Equity NPV (VND bn)', '=\'15_Returns_Discount\'!G7', '#,##0.00;[Red](#,##0.00);-'),
        ('G16','H16','Discount Rate', '=\'15_Returns_Discount\'!C7', '0.0%'),
        ('J16','K16','Return Status', '=\'15_Returns_Discount\'!K7', '@'),
    ]
    for lc, vc, txt, f, fmt in ret:
        label(ws[lc], txt); value(ws[vc], f, fmt)
    ws.conditional_formatting.add('K16', FormulaRule(formula=['K16="BELOW HURDLE"'], fill=fill(FAIL_FILL), font=Font(color=FAIL_RED,bold=True)))
    ws.conditional_formatting.add('K16', FormulaRule(formula=['K16="ABOVE HURDLE"'], fill=fill(PASS_FILL), font=Font(color=PASS_GREEN,bold=True)))
    ws['L16'] = 'Detail: tab 15'; ws['L16'].font = Font(name='Aptos', color=SLATE, italic=True, size=9)

    section(ws, 19, '3. Debt & Credit Coverage')
    debt = [
        ('A20','B20','Debt Capacity (VND bn)', '=INDEX(\'18_Portfolio\'!$E$2:$E$21,MATCH($B$5,\'18_Portfolio\'!$A$2:$A$21,0))', '#,##0.00;[Red](#,##0.00);-'),
        ('D20','E20','Leverage Cap', '=INDEX(\'11_Debt_Terms\'!$M$6:$M$25,MATCH($B$5,\'11_Debt_Terms\'!$B$6:$B$25,0))', '0.0%'),
        ('G20','H20','All-in Debt Rate', '=INDEX(\'11_Debt_Terms\'!$G$6:$G$25,MATCH($B$5,\'11_Debt_Terms\'!$B$6:$B$25,0))', '0.0%'),
        ('J20','K20','Debt Tenor (years)', '=INDEX(\'11_Debt_Terms\'!$N$6:$N$25,MATCH($B$5,\'11_Debt_Terms\'!$B$6:$B$25,0))', '0'),
        ('A21','B21','Minimum DSCR', '=\'14_Coverage\'!A7', '0.00x'),
        ('D21','E21','Covenant DSCR', '=\'14_Coverage\'!C7', '0.00x'),
        ('G21','H21','LLCR', '=\'14_Coverage\'!A10', '0.00x'),
        ('J21','K21','PLCR', '=\'14_Coverage\'!G10', '0.00x'),
    ]
    for lc, vc, txt, f, fmt in debt:
        label(ws[lc], txt); value(ws[vc], f, fmt)
    ws.merge_cells('L20:L21'); ws['L20'] = 'Details: tabs 11–14'
    ws['L20'].font = Font(name='Aptos', color=SLATE, italic=True, size=9)
    ws['L20'].alignment = Alignment(wrap_text=True, vertical='center')

    section(ws, 24, '4. Downside & Scenario Review')
    headers = [('A25','Scenario'),('B25','Portfolio DSCR'),('D25','Headroom vs 1.20x'),('E25','Status')]
    for cell, txt in headers: label(ws[cell], txt)
    scenarios = [
        ('BASE_SPONSOR','Base Case'),('P90_ENERGY','P90 Energy'),('INTEREST_RATE_SHOCK','Interest Rate Shock'),
        ('FX_ONE_OFF','FX One-off Shock'),('DSO_DELAY','DSO Delay'),('COD_DELAY','COD Delay'),('COMBINED_DOWNSIDE','Combined Downside')
    ]
    for r,(sid,txt) in enumerate(scenarios, start=26):
        ws.cell(r,1,txt); box(ws.cell(r,1))
        ws.cell(r,2, f'=INDEX(\'17_Scenarios_Sensitivity\'!$M$6:$M$18,MATCH("{sid}",\'17_Scenarios_Sensitivity\'!$A$6:$A$18,0))'); box(ws.cell(r,2)); ws.cell(r,2).number_format='0.00x'
        ws.cell(r,4, f'=IF(B{r}="","",B{r}-1.20)'); box(ws.cell(r,4)); ws.cell(r,4).number_format='0.00x'
        ws.cell(r,5, f'=IF(OR(B{r}="",B{r}<1.20),"BREACH","PASS")'); box(ws.cell(r,5), bold=True)
        ws.conditional_formatting.add(f'E{r}', FormulaRule(formula=[f'E{r}="BREACH"'], fill=fill(FAIL_FILL), font=Font(color=FAIL_RED,bold=True)))
        ws.conditional_formatting.add(f'E{r}', FormulaRule(formula=[f'E{r}="PASS"'], font=Font(color=PASS_GREEN,bold=True)))
    ws.merge_cells('F25:L32')
    ws['F25'] = ('Downside interpretation\n\nThe base financing case is compared with key operating, market and execution stresses. '
                 'Coverage below the 1.20x covenant reference is flagged as a breach. Debt is not automatically resized under stress, '
                 'so the schedule tests whether base-case financing remains serviceable.')
    box(ws['F25'], bg=VERY_LIGHT, color=SLATE, wrap=True); ws['F25'].alignment = Alignment(vertical='top', wrap_text=True)

    section(ws, 35, '5. Investment Decision & Key Conditions')
    label(ws['A36'], 'Sponsor Status'); value(ws['B36'], '=INDEX(\'19_IC_Bankability\'!$B$6:$B$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0))', '@')
    label(ws['D36'], 'Lender Status'); value(ws['E36'], '=INDEX(\'19_IC_Bankability\'!$C$6:$C$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0))', '@')
    label(ws['G36'], 'Final Classification'); ws.merge_cells('H36:L36'); value(ws['H36'], '=SUBSTITUTE(INDEX(\'19_IC_Bankability\'!$I$6:$I$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0)),"_"," ")', '@', align='center')
    label(ws['A37'], 'Selected in Portfolio?'); value(ws['B37'], '=IF(INDEX(\'18_Portfolio\'!$C$2:$C$21,MATCH($B$5,\'18_Portfolio\'!$A$2:$A$21,0))=TRUE,"YES","NO")', '@')
    label(ws['D37'], 'Pooled Debt (VND bn)'); value(ws['E37'], '=INDEX(\'18_Portfolio\'!$G$2:$G$21,MATCH($B$5,\'18_Portfolio\'!$A$2:$A$21,0))', '#,##0.00;[Red](#,##0.00);-')
    label(ws['G37'], 'Pooled Equity (VND bn)'); value(ws['H37'], '=INDEX(\'18_Portfolio\'!$H$2:$H$21,MATCH($B$5,\'18_Portfolio\'!$A$2:$A$21,0))', '#,##0.00;[Red](#,##0.00);-')
    label(ws['A38'], 'Binding Issue'); ws.merge_cells('B38:F38'); value(ws['B38'], '=SUBSTITUTE(INDEX(\'19_IC_Bankability\'!$D$6:$D$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0)),"_"," ")', '@', align='left')
    label(ws['G38'], 'Recommended Action'); ws.merge_cells('H38:L38'); value(ws['H38'], '=SUBSTITUTE(INDEX(\'19_IC_Bankability\'!$E$6:$E$25,MATCH($B$5,\'19_IC_Bankability\'!$A$6:$A$25,0)),"_"," ")', '@', align='left')
    add_status_rules(ws, 'B36', 'B36'); add_status_rules(ws, 'E36', 'E36'); add_status_rules(ws, 'H36:L36', 'H36')

    section(ws, 41, '6. Review Notes')
    ws.merge_cells('A42:L46')
    ws['A42'] = ('• Public-data reconstruction for screening / underwriting analysis; not a live transaction approval.\n'
                 '• Reference tariff assumptions are not executed PPAs; modeled debt terms are not actual lender commitments.\n'
                 '• A live decision would require executed PPA, measured customer load, lender term sheet, independent technical validation and final legal / tax diligence.\n'
                 '• Detailed operating, financing, scenario and QA calculations remain available in the underlying tabs.')
    box(ws['A42'], bg=VERY_LIGHT, color=SLATE, wrap=True); ws['A42'].alignment = Alignment(vertical='top', wrap_text=True)

    widths = {1:22,2:15,3:3,4:22,5:15,6:3,7:22,8:15,9:3,10:22,11:16,12:18}
    for col,w in widths.items(): ws.column_dimensions[get_column_letter(col)].width = w


def professional_restyle(wb):
    title_ranges = {
        '01_Assumptions':'A1:S2','09_Project_CF_CFADS':'A1:M2','11_Debt_Terms':'A1:P2',
        '12_Debt_Sculpting':'A1:J2','14_Coverage':'A1:J2','15_Returns_Discount':'A1:W2',
        '17_Scenarios_Sensitivity':'A1:U2','19_IC_Bankability':'A1:K2'
    }
    for name,rng in title_ranges.items():
        if name not in wb.sheetnames: continue
        ws=wb[name]; ws.sheet_view.showGridLines=False
        for row in ws[rng]:
            for c in row: c.fill=fill(NAVY_DARK)

    headers = {
        '02_Evidence_Regulatory':'A1:P1','03_Project_Pipeline':'A1:AH1','04_Offtakers_Credit_Site':'A1:J1',
        '05_Solar_Energy':'A1:Q1','06_Load_PPA':'A1:T1','07_CAPEX_Construction':'A1:P1','08_OPEX':'A1:X1',
        '10_Portfolio_CFADS':'A1:H1','13_Reserves_Waterfall':'A1:M1','16_FX_Financing':'A1:G1',
        '18_Portfolio':'A1:Q1','20_External_Validation':'A1:K1','21_QA_Audit':'A1:D1'
    }
    for name,rng in headers.items():
        if name not in wb.sheetnames: continue
        ws=wb[name]; ws.sheet_view.showGridLines=False
        for row in ws[rng]:
            for c in row:
                c.fill=fill(NAVY); c.font=Font(name='Aptos',color=WHITE,bold=True); c.alignment=Alignment(wrap_text=True,vertical='center')

    if '01_Assumptions' in wb.sheetnames:
        ws=wb['01_Assumptions']
        for c in ws['D'][5:34]: c.font=Font(name='Aptos',color=INPUT_BLUE)

    if '11_Debt_Terms' in wb.sheetnames:
        ws=wb['11_Debt_Terms']
        for row in range(6,26):
            for col in range(5,7): ws.cell(row,col).font=Font(name='Aptos',color=INPUT_BLUE)
            ws.cell(row,7).font=Font(name='Aptos',color=BLACK,bold=True)
            for col in range(8,17): ws.cell(row,col).font=Font(name='Aptos',color=INPUT_BLUE)

    if '17_Scenarios_Sensitivity' in wb.sheetnames:
        ws=wb['17_Scenarios_Sensitivity']
        for row in range(6,19):
            for col in range(3,12): ws.cell(row,col).font=Font(name='Aptos',color=INPUT_BLUE)
            for col in list(range(1,3))+list(range(12,22)): ws.cell(row,col).font=Font(name='Aptos',color=BLACK)

    if '09_Project_CF_CFADS' in wb.sheetnames:
        ws=wb['09_Project_CF_CFADS']
        ws.merge_cells('A19:M19'); ws['A19']='MODEL CONTROL CHECKS'
        ws['A19'].fill=fill(LIGHT_GRAY); ws['A19'].font=Font(name='Aptos',color=NAVY,bold=True)
        controls=[
            ('CFADS Reconciliation','=IF(ABS(SUM(C16:M16))<0.01,"PASS","REVIEW")','Calculated CFADS agrees to the preserved source output'),
            ('Selected Project','=B4','Controlled centrally from 00_Control'),
            ('Review Years','=COUNT(C6:M6)','Years 0–10 displayed in the review bridge'),
            ('Source Rows','=COUNTIF($A$31:$A$350,$B$4)','Raw project rows available for the selected project'),
        ]
        for r,(a,b,c) in enumerate(controls,20):
            ws.cell(r,1,a); ws.cell(r,2,b); ws.cell(r,3,c)
            for col in range(1,4): box(ws.cell(r,col), bg=WHITE, color=SLATE if col!=2 else BLACK, bold=(col<3), wrap=True)

    if '12_Debt_Sculpting' in wb.sheetnames:
        ws=wb['12_Debt_Sculpting']
        ws.merge_cells('A19:J19'); ws['A19']='DEBT SCULPTING CONTROL CHECKS'
        ws['A19'].fill=fill(LIGHT_GRAY); ws['A19'].font=Font(name='Aptos',color=NAVY,bold=True)
        controls=[
            ('Opening Facility (VND bn)','=F4','Opening debt used in the sculpted schedule','#,##0.00;[Red](#,##0.00);-'),
            ('Final Closing Debt (VND bn)','=H16','Should amortize to zero by maturity','#,##0.00;[Red](#,##0.00);-'),
            ('Minimum Actual DSCR','=MIN(I7:I16)','Lowest annual coverage in the sculpted schedule','0.00x'),
            ('Schedule Balance Check','=IF(COUNTIF(J7:J16,"REVIEW")=0,"PASS","REVIEW")','Confirms opening − principal − closing = 0 for all years','@'),
        ]
        for r,(a,b,c,fmt) in enumerate(controls,20):
            ws.cell(r,1,a); ws.cell(r,2,b); ws.cell(r,3,c); ws.cell(r,2).number_format=fmt
            for col in range(1,4): box(ws.cell(r,col), bg=WHITE, color=SLATE if col!=2 else BLACK, bold=(col<3), wrap=True)
        ws.column_dimensions['A'].width=24; ws.column_dimensions['B'].width=18; ws.column_dimensions['C'].width=34
        for r in range(7,17):
            ws.cell(r,9).fill=fill(WHITE); ws.cell(r,10).fill=fill(WHITE)

    if '15_Returns_Discount' in wb.sheetnames:
        ws=wb['15_Returns_Discount']
        ws['A9']='DISCOUNTED CASH FLOW SUPPORT — review calculation'
        ws['A9'].fill=fill(LIGHT_GRAY); ws['A9'].font=Font(name='Aptos',color=NAVY,bold=True)
        ws['M1']='SUPPORTING RETURN CALCULATION'


def main():
    if len(sys.argv) not in (2,3):
        raise SystemExit('usage: build_recruiter_company_workbook.py INPUT_XLSX [OUTPUT_XLSX]')
    src=Path(sys.argv[1])
    dst=Path(sys.argv[2]) if len(sys.argv)==3 else src.with_name('vietgreen_company_style.xlsx')
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb=load_workbook(src)
    reset_control(wb['00_Control'])
    professional_restyle(wb)
    wb.save(dst)
    print(f'Company-style recruiter workbook: {dst}')


if __name__ == '__main__':
    main()
