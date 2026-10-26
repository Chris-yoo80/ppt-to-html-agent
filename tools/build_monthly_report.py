"""Build repeatable fictional monthly sales presentations and source workbooks."""
import argparse
import html
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'examples/monthly-report'
sys.path.insert(0,str(ROOT/'skills/ppt-to-html/scripts'))
from build_deck import build

CHANNELS=('Online','Marketplace','Partner')

def load_month(month):
    path=SOURCE/f'{month}.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('fictional') is not True or data.get('month')!=month:raise ValueError('Monthly source must be explicitly fictional and match its filename')
    rows=data.get('rows')
    if not isinstance(rows,list) or len(rows)!=12:raise ValueError('Expected four weeks by three channels')
    seen=set()
    for row in rows:
        key=(row.get('week'),row.get('channel'))
        if key in seen or row.get('channel') not in CHANNELS:raise ValueError('Invalid or duplicate week/channel row')
        seen.add(key)
        for metric in ('orders','revenue'):
            if type(row.get(metric)) is not int or row[metric]<0:raise ValueError(f'Invalid {metric}')
    if len({r['week'] for r in rows})!=4 or {r['channel'] for r in rows}!=set(CHANNELS):raise ValueError('The source must cover four weeks and all three channels')
    return data

def totals(rows):
    orders=sum(r['orders'] for r in rows); revenue=sum(r['revenue'] for r in rows)
    return {'orders':orders,'revenue':revenue,'aov':revenue/orders if orders else None}

def deck_for(data, language):
    en=language=='en'; rows=data['rows']; total=totals(rows)
    by_channel={c:totals([r for r in rows if r['channel']==c]) for c in CHANNELS}
    weeks=sorted({r['week'] for r in rows})
    by_week={w:totals([r for r in rows if r['week']==w]) for w in weeks}
    source=f"{data['month']}.xlsx / Sales!A1:D13"
    money=lambda value:f"KRW {value/1_000_000:,.1f}M" if en else f"{value/10_000:,.1f}만원"
    title=f"Fictional monthly sales · {data['month']}" if en else f"가상 월간 매출 · {data['month']}"
    deck={'title':title,'language':language,'settings':{'width':1600,'height':900,'font':'system','motion':'key','playback':'both','end':'stop'},'scenes':[
      {'id':'title','eyebrow':'MONTHLY SALES / FICTIONAL' if en else '월간 매출 / 가상 데이터','title':title,'lead':'The same reviewed structure can be regenerated with next month’s source.' if en else '검토한 발표 구조를 유지하고 다음 달 원본으로 다시 생성합니다.','layout':'cards','motion':'none','items':[{'label':'Period' if en else '기간','value':data['month'],'body':'Four weekly periods.' if en else '4개 주간 기간입니다.'},{'label':'Source range' if en else '원본 범위','value':'Sales!A1:D13','body':'12 fictional source rows.' if en else '가상 원본 12개 행입니다.'}],'message':'Original fictional data; no company or customer information.' if en else '새로 만든 가상 데이터이며 회사·고객 정보가 없습니다.','source':source,'duration':7},
      {'id':'summary','eyebrow':'01 / EXECUTIVE SUMMARY','title':'Monthly result' if en else '월간 결과 요약','lead':'Revenue, orders and average order value use the complete monthly scope.' if en else '매출·주문·평균 주문금액은 월 전체 범위를 사용합니다.','layout':'compare','motion':'none','items':[{'label':'Revenue' if en else '매출','value':money(total['revenue']),'body':f"{total['revenue']:,} KRW"},{'label':'Orders' if en else '주문','value':f"{total['orders']:,}",'body':'Count; all channels.' if en else '건수·전체 채널입니다.'},{'label':'Average order value' if en else '평균 주문금액','value':money(total['aov']),'body':'Revenue ÷ orders; ratio of sums.' if en else '매출 ÷ 주문; 합계의 비율입니다.'}],'message':'Aggregate raw values first; round only for display.' if en else '원본 값을 먼저 합산하고 표시할 때만 반올림합니다.','source':source,'duration':8},
      {'id':'channels','eyebrow':'02 / CHANNEL MIX','title':'Revenue by channel' if en else '채널별 매출 구성','lead':'Every channel uses the same monthly filter.' if en else '모든 채널에 같은 월간 필터를 적용합니다.','layout':'compare','motion':'planes','items':[{'label':c,'value':money(by_channel[c]['revenue']),'body':(f"{by_channel[c]['orders']:,} orders · {by_channel[c]['revenue']/total['revenue']*100:.1f}% of revenue" if en else f"주문 {by_channel[c]['orders']:,}건 · 매출 비중 {by_channel[c]['revenue']/total['revenue']*100:.1f}%") } for c in CHANNELS],'message':'Channel shares use total monthly revenue as the denominator.' if en else '채널 비중의 분모는 월 전체 매출입니다.','source':source,'duration':8},
      {'id':'timeline','eyebrow':'03 / WEEKLY TIMELINE','title':'Weekly revenue flow' if en else '주간 매출 흐름','lead':'The timeline keeps the same four-step structure every month.' if en else '매월 같은 4단계 타임라인 구조를 유지합니다.','layout':'compare','motion':'lines','motion_caption':'Weekly sequence' if en else '주간 흐름','items':[{'label':w,'value':money(by_week[w]['revenue']),'body':(f"{by_week[w]['orders']:,} orders" if en else f"주문 {by_week[w]['orders']:,}건") } for w in weeks],'message':'Week labels come directly from the source file.' if en else '주차 표기는 원본 파일 값을 그대로 사용합니다.','source':source,'duration':8},
      {'id':'conclusion','eyebrow':'04 / CONCLUSION','title':'What to carry into next month' if en else '다음 달에도 유지할 기준','lead':'Keep definitions and the presentation structure stable; replace only the reviewed source.' if en else '지표 정의와 발표 구조를 유지하고 검토한 원본만 교체합니다.','layout':'flow','motion':'lines','items':[{'label':'Replace source' if en else '원본 교체','body':'Add the new month JSON and workbook.' if en else '새 월 JSON과 엑셀을 추가합니다.'},{'label':'Rebuild' if en else '재생성','body':'Run the same build command.' if en else '같은 생성 명령을 실행합니다.'},{'label':'Verify' if en else '검수','body':'Check units, denominator, filters, rounding and provenance.' if en else '단위·분모·필터·반올림·출처를 확인합니다.'}],'message':'Do not carry forward stale totals from the prior month.' if en else '지난달 합계를 다음 달에 그대로 남기지 않습니다.','source':source,'duration':8}
    ]}
    return deck

def write_xlsx(data, path):
    rows=[['Week','Channel','Orders','Revenue (KRW)']]+[[r['week'],r['channel'],r['orders'],r['revenue']] for r in data['rows']]
    def cell(col,row,value):
        ref=f'{col}{row}'
        if isinstance(value,int):return f'<c r="{ref}"><v>{value}</v></c>'
        return f'<c r="{ref}" t="inlineStr"><is><t>{html.escape(value)}</t></is></c>'
    sheet=''.join(f'<row r="{i}">'+''.join(cell(chr(65+j),i,v) for j,v in enumerate(values))+'</row>' for i,values in enumerate(rows,1))
    files={'[Content_Types].xml':'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
      '_rels/.rels':'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
      'xl/workbook.xml':'<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Sales" sheetId="1" r:id="rId1"/></sheets></workbook>',
      'xl/_rels/workbook.xml.rels':'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
      'xl/worksheets/sheet1.xml':f'<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{sheet}</sheetData></worksheet>'}
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,content in files.items():archive.writestr(name,content)

def build_month(month):
    data=load_month(month); write_xlsx(data,SOURCE/f'{month}.xlsx')
    outputs=[]
    for language in ('ko','en'):
        deck=deck_for(data,language); suffix='.en' if language=='en' else ''
        deck_path=SOURCE/f'presentation-{month}{suffix}.json'
        deck_path.write_text(json.dumps(deck,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        output=ROOT/f'docs/monthly-report-{month}{suffix}.html'
        output.write_text(build(deck),encoding='utf-8',newline='\n'); outputs.append(output)
    return outputs

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--month',action='append');args=parser.parse_args()
    months=args.month or sorted(p.stem for p in SOURCE.glob('20??-??.json'))
    for month in months:
        for output in build_month(month):print(f'Built {output.relative_to(ROOT)}')
