from pathlib import Path
import json
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

out=Path(__file__).parent
pdf=PdfReader(out/'report.pdf')
rows=[]
(out/'pages').mkdir(exist_ok=True)
for i,p in enumerate(pdf.pages):
    txt=p.extract_text()
    rows.append({'page':i+1,'text':txt})
    print(f'PAGE {i+1} chars={len(txt)} END={txt[-45:]!r}')
(out/'pdf_pages.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'pdf_text.txt').write_text('\n\n'.join(f'===== PDF PAGE {r["page"]} =====\n{r["text"]}' for r in rows),encoding='utf-8')
images=convert_from_path(out/'report.pdf',dpi=95,poppler_path=r'C:\Users\84378\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin',thread_count=4)
for i,im in enumerate(images): im.save(out/'pages'/f'page-{i+1:02d}.png')
for start in range(0,len(pdf.pages),12):
    sheet=Image.new('RGB',(4*300,3*445),'#c0c0c0');draw=ImageDraw.Draw(sheet)
    for j in range(start,min(start+12,len(pdf.pages))):
        im=Image.open(out/'pages'/f'page-{j+1:02d}.png').convert('RGB');im.thumbnail((290,415))
        x=(j-start)%4*300+5;y=(j-start)//4*445+25
        sheet.paste(im,(x,y));draw.text((x,y-20),f'PDF page {j+1}',fill='black')
    sheet.save(out/f'contact-{start+1:02d}.jpg')
