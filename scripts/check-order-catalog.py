"""Read-only regression checks for the orders catalog's Initializer contracts."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'masterdata' / 'configuration'
GROUPS = ['orders.csv', 'lab_samples.csv', 'procedure_sections.csv', 'radiology_order_sections.csv']


def read(relative):
    with (ROOT / relative).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert all(None not in row for row in rows), f'Misaligned CSV: {relative}'
        return reader.fieldnames, rows


for name in GROUPS:
    headers, rows = read('concepts/' + name)
    assert 'Members' not in headers, (
        f'{name}: a blank Members column erases relationships owned by conceptsets '
        '(Initializer 2.7.0 NestedConceptLineProcessor)'
    )
    assert all(row.get('Fully specified name:en') for row in rows), name

_, root_members = read('conceptsets/all_orderables_set.csv')
assert [r['Member'] for r in root_members] == ['Lab Samples', 'Radiology Orders', 'Procedure Orders']
_, procedures = read('conceptsets/procedure_orders_set.csv')
assert any(r['Member'] == 'bb718d23-92ed-4159-bd34-3f641a17a26b' for r in procedures), (
    'Use the configured Biopsy category UUID; SNOMED-CT:86273004 resolves to two concepts in .225'
)
assert not any(r['Member'] == 'SNOMED-CT:86273004' for r in procedures)
_, radiology = read('conceptsets/radiology_order_section_mapping.csv')
assert not any(r['Concept'] == '163958AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' and
               r['Member'] in ['163958AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'SNOMED-CT:44491008']
               for r in radiology), 'Fluoroscopy must not contain itself'
print('PASS: four concept files preserve set membership; root groups, Biopsy UUID and Fluoroscopy hierarchy validated.')
