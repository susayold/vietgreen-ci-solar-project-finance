"""Build the V5 workbook on the ephemeral CI runner."""
from pathlib import Path
import csv,json
from openpyxl import Workbook
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"outputs"; ART=ROOT/"artifacts"/"v5_model"
def read(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.reader(f))
def main():
    ART.mkdir(parents=True,exist_ok=True); wb=Workbook(); wb.remove(wb.active)
    specs=[("00_Control",ROOT/"release"/"V5_BUILD_STATUS.json"),("01_Project_Facts",ROOT/"data"/"public"/"project_master_real.csv"),("02_Assumptions",ROOT/"data"/"public"/"project_assumption_overlay.csv"),("03_Sources",ROOT/"evidence"/"GLOBAL_SOURCE_REGISTER.csv"),("04_Benchmarks",ROOT/"evidence"/"COUNTRY_BENCHMARK_PACKS.csv"),("05_Economics",OUT/"v5_project_economics.csv"),("06_Debt",OUT/"v5_debt_schedule.csv"),("07_Scenarios",OUT/"v5_scenarios.csv"),("08_Portfolio",OUT/"v5_portfolio_summary.json"),("09_Reconciliation",OUT/"v5_reconciliation.csv")]
    for name,path in specs:
        ws=wb.create_sheet(name)
        data=[[("key","value")]] if path.suffix==".json" else read(path)
        if path.suffix==".json":
            data=[["key","value"]]+[[k,json.dumps(v,ensure_ascii=False)] for k,v in json.loads(path.read_text(encoding="utf-8")).items()]
        for row in data:ws.append(row)
        ws.freeze_panes="A2";ws.auto_filter.ref=ws.dimensions
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width=min(max(max(len(str(x.value or "")) for x in col)+2,10),48)
    wb.save(ART/"vietgreen_v5_model.xlsx");print(f"built={ART/'vietgreen_v5_model.xlsx'}")
if __name__=="__main__":main()
