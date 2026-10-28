"""Create a declared design-reference manifest without fetching or copying a source."""
import argparse
import json
from pathlib import Path

CATALOG=Path(__file__).resolve().parent.parent/'assets/reference-presets.json'
ALLOWED_REUSE=('inspiration','layout','code')

def catalog():
    data=json.loads(CATALOG.read_text(encoding='utf-8'))
    if data.get('version')!=1 or not isinstance(data.get('presets'),dict):raise ValueError('Invalid reference preset catalog')
    return data

def manifest(preset,source,source_kind,apply,reuse,license_id=None,license_url=None,inspected=False):
    presets=catalog()['presets']
    if preset not in presets:raise ValueError(f'Unknown preset: {preset}')
    if reuse not in ALLOWED_REUSE:raise ValueError('reuse must be inspiration, layout or code')
    if reuse=='code' and (not license_id or not license_url):raise ValueError('Code reuse requires --license and --license-url')
    requested=[value.strip() for value in apply.split(',') if value.strip()]
    if not requested:raise ValueError('At least one applied element is required')
    if not source.strip():raise ValueError('A source or preset declaration is required')
    selected=presets[preset]
    permission={'status':'verified declaration' if reuse=='code' else 'visual inspiration only',
                'license':license_id if reuse=='code' else None,
                'licenseUrl':license_url if reuse=='code' else None,
                'needsReview':reuse=='code'}
    return {'version':1,'mode':'reference-design','preset':preset,'presetLabel':selected['label'],
            'source':{'value':source,'kind':source_kind,'inspected':bool(inspected)},
            'reuse':reuse,'apply':requested,'presetRules':selected['apply'],'exclude':selected['exclude'],
            'tokens':selected['tokens'],'references':selected['references'],'permission':permission,
            'runtimeDependencies':[],'offlineSingleFile':True,
            'note':'Preset rules are newly authored abstractions. No third-party code, assets, branding or example data are bundled.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list',action='store_true');parser.add_argument('--preset',choices=tuple(catalog()['presets']))
    parser.add_argument('--source');parser.add_argument('--source-kind',choices=('url','repository','html','image','named-style','preset'),default='preset')
    parser.add_argument('--apply',default='mood,color,typography,layout,cards,charts,motion')
    parser.add_argument('--reuse',choices=ALLOWED_REUSE,default='inspiration');parser.add_argument('--license');parser.add_argument('--license-url')
    parser.add_argument('--inspected',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.list:
        print(json.dumps(catalog(),ensure_ascii=False,indent=2));return
    if not args.preset or not args.source or not args.output:parser.error('--preset, --source and --output are required unless --list is used')
    try:result=manifest(args.preset,args.source,args.source_kind,args.apply,args.reuse,args.license,args.license_url,args.inspected)
    except ValueError as error:parser.error(str(error))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Wrote design-reference manifest: {args.output}')

if __name__=='__main__':main()
