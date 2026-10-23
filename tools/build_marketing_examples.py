"""Build the fictional marketing supplement and its bilingual presentation wrappers."""
import copy
import html
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/ppt-to-html/scripts'))
from build_analysis import build as analysis
from build_deck import build as presentation

def backup(config, english):
    title='Backup: source & calculations' if english else '백업: 원본과 계산 근거'
    rows=''.join('<tr>'+''.join('<td>'+html.escape(str(r[k]))+'</td>' for k in ['week','channel','region','spend','impressions','clicks','orders','revenue'])+'</tr>' for r in config['records'])
    note='Original fictional Excel: Campaign!A1:H25. 24 rows. ROAS = SUM(revenue) / SUM(spend). Conversion = SUM(orders) / SUM(clicks). Zero denominators are unavailable. This is reviewed supporting HTML; the original workbook is not attached.' if english else '신규 가상 엑셀 Campaign!A1:H25, 24개 행. ROAS = 매출 합계 / 광고비 합계. 전환율 = 구매 합계 / 클릭 합계. 분모가 0이면 계산하지 않습니다. 검토한 보충 HTML이며 원본 엑셀은 첨부하지 않았습니다.'
    license_text=html.escape((ROOT/'LICENSE').read_text(encoding='utf8'))
    return '<!doctype html><html lang="'+('en' if english else 'ko')+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>body{font:14px/1.7 system-ui,sans-serif;color:#243d30;max-width:1100px;margin:30px auto;padding:20px}table{border-collapse:collapse;width:100%;font-size:12px}td,th{padding:7px;border-bottom:1px solid #ddd;text-align:left}div{overflow:auto}button{padding:12px}pre{white-space:pre-wrap}@media print{@page{size:A4 landscape;margin:12mm}button,details{display:none}body{margin:0;padding:0}div{overflow:visible}tr{break-inside:avoid}thead{display:table-header-group}}</style><h1>'+title+'</h1><p>'+note+'</p><button onclick="window.print()">'+('Print / PDF' if english else '인쇄 / PDF')+'</button><div><table><thead><tr>'+''.join('<th>'+v+'</th>' for v in ['Week','Channel','Region','Spend (KRW)','Impressions','Clicks','Orders','Revenue (KRW)'])+'</tr></thead><tbody>'+rows+'</tbody></table></div><details><summary>License</summary><pre>'+license_text+'</pre></details></html>'

def outputs():
    config=json.loads((ROOT/'examples/marketing-analysis/data.json').read_text(encoding='utf8'))
    spend=sum(r['spend'] for r in config['records']);revenue=sum(r['revenue'] for r in config['records']);clicks=sum(r['clicks'] for r in config['records']);orders=sum(r['orders'] for r in config['records'])
    result={}
    for language in ['ko','en']:
        english=language=='en';localized=copy.deepcopy(config);localized['language']=language
        if english:localized['title']='Fictional campaign analysis'
        suffix='.en' if english else ''
        supplement=analysis(localized)
        result[f'docs/marketing-analysis{suffix}.html']=supplement
        deck={'title':'Campaign review' if english else '가상 캠페인 성과 검토','language':language,'settings':{'width':1600,'height':900,'font':'system','motion':'key','playback':'both','end':'stop'},'scenes':[
            {'id':'scope','title':'Campaign scope' if english else '캠페인 분석 범위','lead':'Open Additional resources to explore the supporting HTML.' if english else '아래 추가 자료를 열어 마케팅 분석 HTML을 조작할 수 있습니다.','layout':'cards','motion':'none','items':[{'label':'Fictional data' if english else '새 가상 데이터','body':'24 records across four weeks, three channels and two markets.' if english else '4주, 3개 채널, 2개 시장의 가상 기록 24개입니다.'},{'label':'Supporting analysis' if english else '보충 분석','body':'Controls and slicers on the left, visual results on the right.' if english else '왼쪽 조정값·슬라이서, 오른쪽 수치·차트로 근거를 확인합니다.'}],'message':'Original fictional data, not measured campaign performance.' if english else '실측 성과가 아닌 신규 가상 캠페인입니다.','source':'Campaign!A1:H25','duration':8},
            {'id':'results','title':'Source campaign totals' if english else '원본 캠페인 집계','layout':'compare','motion':'none','items':[{'label':'Ad spend (KRW)' if english else '광고비 (원)','value':f'{spend:,}','body':'Sum of source spend.' if english else '전체 광고비 합계입니다.'},{'label':'Revenue (KRW)' if english else '매출 (원)','value':f'{revenue:,}','body':'Sum of source revenue.' if english else '전체 매출 합계입니다.'},{'label':'ROAS','value':f'{revenue/spend:.2f}×','body':'Total revenue / total ad spend.' if english else '매출 합계 ÷ 광고비 합계입니다.'},{'label':'Conversion' if english else '구매 전환율','value':f'{orders/clicks*100:.2f}%','body':f'{orders:,} / {clicks:,} '+('purchases / clicks' if english else '구매 ÷ 클릭')}],'message':'Do not average individual-row rates.' if english else '행별 비율의 단순 평균을 사용하지 않습니다.','source':'Campaign!D2:H25','duration':8},
            {'id':'interpretation','title':'Explore the evidence' if english else '근거를 확인하는 순서','layout':'flow','motion':'lines','motion_caption':'Illustrative review sequence' if english else '분석 순서를 설명하는 개념도','items':[{'label':'Filter' if english else '범위 선택','body':'Choose the period, channel and market.' if english else '기간·채널·시장을 좁혀 같은 범위를 비교합니다.'},{'label':'Compare' if english else '성과 비교','body':'Read the trend, funnel and weighted channel metrics.' if english else '추이·전환 흐름·채널별 집계 지표를 확인합니다.'},{'label':'Extend' if english else '필요 시 확장','body':'Add detail or a separately labeled hypothetical scenario.' if english else '상세표나 별도로 표시한 가정 시나리오를 추가합니다.'}],'message':'Close supporting analysis to return to the same presentation step.' if english else '추가 자료를 닫으면 같은 발표 단계로 돌아옵니다.','source':'Original fictional example' if english else '새 가상 예제','duration':8}
        ]}
        result[f'examples/marketing-analysis/presentation.{language}.json']=json.dumps(deck,ensure_ascii=False,indent=2)+'\n'
        deck['supplements']=[{'id':'campaign','label':'Marketing analysis' if english else '마케팅 분석','html':supplement}]
        backup_html=backup(config,english)
        result[f'docs/marketing-backup{suffix}.html']=backup_html
        for guide_language in [language,'ko' if english else 'en']:
            guide=ROOT/f'docs/guide.{guide_language}.html'
            if guide.exists():deck['supplements'].append({'id':'guide-'+guide_language,'label':'User guide (EN)' if guide_language=='en' else '사용설명서 (KO)','html':guide.read_text(encoding='utf8')})
        deck['supplements'].append({'id':'backup','label':'Backup: source & calculations' if english else '백업: 원본과 계산 근거','html':backup_html})
        result[f'docs/marketing-presentation{suffix}.html']=presentation(deck)
    return result

if __name__=='__main__':
    for filename,content in outputs().items():
        (ROOT/filename).write_text(content,encoding='utf8',newline='\n')
    print('Built bilingual presentation + supporting HTML examples.')
