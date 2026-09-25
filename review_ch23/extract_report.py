from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import json, re

source = Path(r'D:\DATN\CNTT_2022606983_LeDucThuan_BaoCao.docx')
out = Path(__file__).parent
doc = Document(source)
blocks = []
for i, el in enumerate(doc.element.body.iterchildren()):
    if el.tag.endswith('}p'):
        p = Paragraph(el, doc)
        text = p.text
        imgs = len(el.xpath('.//w:drawing'))
        math = [''.join(x.itertext()) for x in el.xpath('.//m:oMath')]
        blocks.append({'id': i, 'kind': 'paragraph', 'style': p.style.name, 'text':text, 'images': imgs, 'math':math})
    elif el.tag.endswith('}tbl'):
        t = Table(el, doc)
        blocks.append({'id': i, 'kind':'table', 'rows':[[c.text for c in r.cells] for r in t.rows]})
(out/'blocks.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
lines=[]
for b in blocks:
    if b['kind']=='paragraph':
        if b['text'].strip() or b['images'] or b['math']:
            lines.append(f"[{b['id']:04d}] ({b['style']}) {b['text']}" + (f" [IMAGES {b['images']}]" if b['images'] else '') + (f" [MATH {b['math']}]" if b['math'] else ''))
    else:
        lines.append(f"[{b['id']:04d}] TABLE\n"+'\n'.join(' | '.join(row) for row in b['rows']))
(out/'report_all.txt').write_text('\n'.join(lines),encoding='utf-8')
for b in blocks:
    if b['kind']=='paragraph' and (b['style'].startswith('Heading') or re.match(r'^(CHƯƠNG|Chương|[234]\.\d)',b['text'])):
        print(f"[{b['id']:04d}] ({b['style']}) {b['text']}")
print('TOTAL BLOCKS',len(blocks))
