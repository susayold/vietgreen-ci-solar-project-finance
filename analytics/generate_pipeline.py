from pathlib import Path
import csv

def validate_input_csv(path):
    with Path(path).open(newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    if len(rows)!=20: raise ValueError('expected 20 projects')
    ids={r['project_id'] for r in rows}
    if len(ids)!=20: raise ValueError('duplicate project IDs')
    return rows

if __name__=='__main__':
    validate_input_csv(Path('data/synthetic/project_master.csv')); print('PIPELINE_INPUT_VALID')
