"""Build the optional campaign-analysis supplemental HTML from reviewed records.

The host prepares records from an authorized workbook; this is not an arbitrary
Excel formula interpreter. All sample records are fictional.
"""
import argparse
import html
import json
import math
from pathlib import Path
from unit_audit import audit_checks

ASSETS=Path(__file__).resolve().parent.parent/'assets'

def metric_metadata(config):
    """Describe actual starter calculations, not an automatic workbook audit."""
    return {
        'version': 1, 'source': config['source'],
        'sourceUnits': {'spend': 'KRW', 'revenue': 'KRW', 'impressions': 'count', 'clicks': 'count', 'orders': 'count'},
        'rates': {
            'roas': {'numerator': 'revenue', 'denominator': 'spend', 'unit': 'x', 'displayMultiplier': 1},
            'cvr': {'numerator': 'orders', 'denominator': 'clicks', 'unit': '%', 'displayMultiplier': 100},
            'ctr': {'numerator': 'clicks', 'denominator': 'impressions', 'unit': '%', 'displayMultiplier': 100},
            'aov': {'numerator': 'revenue', 'denominator': 'orders', 'unit': 'KRW', 'displayMultiplier': 1},
        },
        'aggregation': 'ratio_of_sums_within_same_filtered_group', 'zeroDenominator': 'unavailable',
        'scope': {'dimensions': ['week', 'channel', 'region'],
                  'values': {key: sorted({r[key] for r in config['records']}) for key in ['week', 'channel', 'region']},
                  'filters': 'AND across dimensions; OR within selected channels',
                  'channelComparison': 'numerator and denominator restricted to each selected channel'},
        'display': {
            'ko': {'moneyThreshold': 10000, 'moneyDivisor': 10000, 'moneyUnit': '만원', 'moneyMaxDecimals': 1, 'trendDivisor': 10000, 'trendMaxDecimals': 1},
            'en': {'moneyThreshold': 1000000, 'moneyDivisor': 1000000, 'moneyUnit': 'KRW millions', 'moneyMaxDecimals': 2, 'trendDivisor': 1000000, 'trendMaxDecimals': 1},
            'belowThreshold': {'unit': 'KRW', 'divisor': 1, 'maxDecimals': 0},
            'rateMaxDecimals': 2, 'countsMaxDecimals': 0,
        },
        'rounding': 'aggregate unrounded source values; round for display only; displayed parts may not sum to displayed total',
        'sourceReview': 'requires comparison with the authorized workbook; metadata alone is not a passed audit',
    }


def build(config):
    if not isinstance(config,dict) or not isinstance(config.get('title'),str):raise ValueError('A title is required')
    if type(config.get('fictional')) is not bool:raise ValueError('Declare fictional as true or false')
    if config.get('currency','KRW')!='KRW':raise ValueError('This starter uses KRW; adapt and test formatting for other currencies')
    if config.get('language','ko') not in ('ko','en'):raise ValueError('language must be ko or en')
    if not isinstance(config.get('source'),str) or not config['source'].strip():raise ValueError('A reviewed source reference is required')
    if 'brief' in config:
        allowed={'purpose':['compare','budget','funnel'],'focus':['return','conversion'],'screen':['responsive','presentation'],'font':['sans','serif'],'share':['view','source']}
        if not isinstance(config['brief'],dict) or any(config['brief'].get(k) not in values for k,values in allowed.items()):raise ValueError('Provide complete, supported brief settings')
    records=config.get('records')
    if not isinstance(records,list) or not 1<=len(records)<=10000:raise ValueError('1–10,000 records required')
    for record in records:
        for key in ['week','channel','region']:
            if not isinstance(record.get(key),str) or not record[key].strip():raise ValueError(f'Missing dimension: {key}')
        for key in ['spend','impressions','clicks','orders','revenue']:
            value=record.get(key)
            if type(value) not in (int,float) or not math.isfinite(value) or value<0:raise ValueError(f'Invalid metric: {key}')
        if record['orders']>record['clicks'] or record['clicks']>record['impressions']:raise ValueError('Inconsistent funnel counts')
    page=(ASSETS/'analysis-template.html').read_text(encoding='utf8')
    metadata=metric_metadata(config)
    if 'metricMetadata' in config and config['metricMetadata']!=metadata:
        raise ValueError('metricMetadata conflicts with the starter calculations; adapt and test the model before changing definitions')
    payload={**config,'metricMetadata':metadata}
    if 'unitChecks' in config:
        payload['unitAudit']=audit_checks(config['unitChecks'])
    else:
        payload.pop('unitAudit',None) # Do not retain an unsubstantiated caller-supplied pass.
    data=json.dumps(payload,ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    legal=(ASSETS.parent/'LICENSE').read_text(encoding='utf8').replace('--','- -')
    page=page.replace('<body>','<body><template id="analysis-license"><pre>'+html.escape('Copyright (c) 2026 Chris-yoo80. Embedded runtime. Presentation Output Exception applies.\n'+legal)+'</pre></template>',1)
    return '<!-- Copyright (c) 2026 Chris-yoo80. Presentation Output Exception applies.\n'+legal+'\n-->\n'+page.replace('__TITLE__',html.escape(config['title'])).replace('__CSS__',(ASSETS/'analysis.css').read_text(encoding='utf8')).replace('__DATA__',data).replace('__MODEL__',(ASSETS/'analysis-model.js').read_text(encoding='utf8')).replace('__UI__',(ASSETS/'analysis-ui.js').read_text(encoding='utf8'))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--language',choices=['ko','en']);args=parser.parse_args()
    try:
        config=json.loads(args.input.read_text(encoding='utf-8-sig'))
        if args.language:config['language']=args.language
        result=build(config);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(result,encoding='utf8',newline='\n')
    except (ValueError,OSError) as error:parser.exit(1,f'Build failed: {error}\n')
    print(f'Built supplemental campaign analysis: {args.output}')
