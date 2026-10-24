"""Build the English landing page from the shared Korean markup."""
from pathlib import Path
import re
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
TRANSLATIONS='''PPT → HTML Agent · 설명은 내 속도로|PPT → HTML Agent · Explain at your own pace
본문으로 이동|Skip to content
이야기는 움직이고.|Motion you can pause.
설명은 내 속도로.|A story you can explain.
영상처럼 이어서 보여주고,|Let the story play,
설명할 순간에는 멈추세요.|then pause when it is time to explain.
PPT의 내용을 읽고 흐름을 설계해,|Read your slides. Shape the narrative.
직접 조작하는 HTML 발표로 만드는 에이전트 스킬.|An agent skill for interactive HTML presentations.
모션 데모 보기|Explore the motion
내 발표 설정하기 →|Set up your presentation →
Claude Code · Codex 가상 예제 검증 / 실제 자료별 확인 필요|Claude Code and Codex fictional fixture checked / verify your own files
배송 · 마케팅 · 창고. 지금 움직여보세요.|Delivery. Marketing. Warehousing. In motion.
각 24초 · 주제 선택|24 seconds each · choose a story
재생하거나, 단계별로 설명하거나.|Play the flow or explain it chapter by chapter.
크게 열기 ↗|Open full size ↗
3가지 시나리오 · 각 24초 · 재생 / 정지 / 구간 탐색|3 stories · 24 seconds each · play / pause / seek
HTML 내려받기 ↓|Download HTML ↓
경로가 정리되는 순간|When routes fall into place
주문 → 권역 → 경로 → 운행. 교차하던 선이 세 차량의 동선으로 바뀝니다.|Orders → regions → routes → delivery. Tangled lines become three vehicle routes.
관심이 전환으로 이어질 때|From attention to conversion
인지 → 관심 → 구매 → 재방문. 고객 여정과 리텐션의 연결을 흐름으로 보여줍니다.|Reach → engagement → purchase → return. Follow the journey into a retention loop.
창고가 움직이는 방식|How a warehouse moves
입고 → 적치 → 피킹 → 출고. 입체 랙과 이동하는 상자로 운영 순서를 설명합니다.|Receiving → storage → picking → shipping. Isometric racks and moving parcels explain the flow.
모두 새로 작성한 가상 시나리오입니다. 실제 최적화·캠페인·시설 성능이나 자동 PPT 변환 결과가 아닙니다. 이 페이지는 자료를 업로드하거나 AI에 전송하지 않습니다.|These are original fictional scenarios, not measured optimization, campaign or facility results, or automatic PPT conversions. This page does not upload your files or send them to AI.
영상처럼 연속 재생|Continuous motion
단계 선택·타임라인 탐색|Chapter controls and seeking
오프라인 단일 HTML|One offline HTML file
디자인보다 먼저,|Before the design,
무엇을 설명할지 정합니다.|decide what to explain.
AI가 만드는 과정에도 기준이 필요하니까.|AI authoring needs a clear process, too.
확인 가능한 절차를 스킬로 묶었습니다.|The skill makes that process explicit.
PPT의 내용과 표, 메모를 읽고 원문 근거를 정리합니다.|Read slide text, tables and notes, and preserve the source evidence.
핵심 메시지와 설명 순서, 적합한 모션을 제안합니다.|Propose the message, narrative order and meaningful motion.
검토한 구성을 단계별 HTML 발표로 제작합니다.|Build the reviewed outline into a step-by-step HTML presentation.
수치·화면 넘침·단계 진행을 점검하고 수정합니다.|Check figures, overflow and navigation, then refine.
가상 예제로 두 CLI의 변환·수정을 확인했습니다. 마케팅 보충 HTML의 실제 Edge 조작도 검증했습니다. 상세 범위와 한계는 검증 기록을 확인하세요.|Fictional conversion and revision checked in both CLIs. Marketing supporting HTML was exercised in Edge. See the verification record for scope and limits.
첫 질문부터, 내 발표에 맞게.|Start with the right questions.
설정을 고르면 시작 요청문을 만들어드립니다.|Choose your settings to create a starting prompt.
설치한 AI 환경에 PPT와 함께 전달하세요.|Use it with your PPT in the AI environment where you installed the skill.
01 · 발표 목적과 청중|01 · Purpose and audience
02 · 발표 시간|02 · Presentation length
03 · 화면 비율과 크기|03 · Aspect ratio and size
04 · 글꼴|04 · Typeface
05 · 움직임의 빈도|05 · Motion frequency
06 · 발표 진행 방식|06 · Playback mode
07 · 점·선·면 모션|07 · Point, line and plane motion
5분|5 minutes
10분|10 minutes
15분|15 minutes
20분|20 minutes
시스템 한글 sans-serif|System sans-serif
시스템 한글 serif|System serif
지정 글꼴 사용 — 파일·사용 조건 별도 전달|Custom font — provide files and usage terms
핵심 설명 화면에만|Key explanatory scenes only
움직임 없이 정적으로|Static, without motion
대부분의 화면에|Most scenes
수동 기본 + 자동 재생 선택 / 마지막에 정지|Manual by default, optional autoplay / stop at end
클릭·키보드 수동 진행만 / 마지막에 정지|Click and keyboard only / stop at end
자동 재생 / 마지막에 정지|Autoplay / stop at end
적합한 장면과 표현 방식을 먼저 제안해주세요|Suggest suitable scenes and visual treatments first
내가 지정하는 장면에만 넣어주세요|Only in scenes I specify
사용하지 않겠습니다|Do not use it
입력 내용은 저장하거나 서버로 전송하지 않습니다. 글꼴·비율 등 설정은 제작 후 화면 검증이 필요합니다.|Your input is not stored or sent to a server. Fonts, sizing and other settings need visual checks after authoring.
요청문 복사|Copy prompt
현재 브라우저 안에서만 생성됩니다.|Generated only in this browser.
당신이 쓰는 AI에서|Continue in the AI
이어서 시작하세요.|you already use.
스킬과 도구는 개인·내부 업무에 무료입니다.|The skill and tools are free for personal and internal business use.
AI 구독료·API 사용료는 사용하는 서비스의 조건을 따릅니다.|AI subscriptions and API fees follow your provider’s terms.
GitHub에서 설치하기|Install from GitHub
저장소의 |See 
에서 Claude Code·Codex별 설치 경로와 실행 예시를 확인하세요. 가상 예제의 두 CLI 흐름을 확인했으며, 실제 자료는 별도 검증이 필요합니다.| in the repository for Claude Code and Codex installation paths and examples. The fictional CLI fixture was checked; verify your own source files separately.
스킬 ZIP 내려받기 ↓|Download skill ZIP ↓
GitHub에서 코드 보기 ↗|View source on GitHub ↗
몇 가지, 분명하게.|A few things to know.
이 페이지에서 바로 PPT를 변환하나요?|Does this website convert PPT files?
아니요. 이곳은 소개·예제 체험·시작 요청문 생성 페이지입니다. 실제 변환은 스킬을 설치한 AI 환경에서 수행합니다.|This website introduces the project, plays examples and builds a starting prompt. Conversion happens in your AI environment with the skill installed.
원본 PPT와 똑같은 배치를 복원하나요?|Does it reproduce the original slide layout?
내용을 바탕으로 설명 구조와 화면을 재설계합니다. 원본 배치의 완전 복원은 지원하지 않습니다. 기본 추출기는 PPTX의 텍스트·표·메모를 읽으며 이미지 OCR과 차트 데이터 해석은 포함하지 않습니다.|It redesigns the narrative and screens around your content. Pixel-perfect reconstruction is not supported. The basic extractor reads PPTX text, tables and notes; image OCR and chart-data interpretation are not included.
동영상 파일도 만들 수 있나요?|Can it export video files?
첫 버전은 HTML 안의 점·선·면 모션 그래픽에 집중합니다. MP4 영상 파일 출력은 후속 기능입니다.|The first version focuses on point, line and plane motion inside HTML. MP4 export is deferred.
어떤 내용이 GitHub에 공개되나요?|What is published on GitHub?
일반적인 제작 지침과 코드, 새로 작성한 가상 예제만 공개합니다. 사용자의 실제 PPT·메모·내장 자료는 공개 예제로 자동 전환하지 않습니다.|Only general authoring instructions, code and original fictional examples are published. Your actual slides, notes and embedded materials do not automatically become public examples.
개인·내부 업무 무료 / 도구의 유료 제공은 별도 허가|Free for personal and internal use / paid tool offerings need permission
EARLY PREVIEW · 개인·내부 업무 무료|EARLY PREVIEW · FREE FOR INTERNAL USE
예: 동아리 활동 소개 / 신입 회원|Example: project introduction / new team members
발표 시작 설정|Presentation setup
생성된 시작 요청문|Generated starting prompt
메인 메뉴|Main navigation
PPT to HTML Agent 홈|PPT to HTML Agent home
배송 경로·마케팅 퍼널·입체 창고 운영의 연속 모션 데모|Continuous delivery, marketing and warehouse motion demos
개인·회사 내부 업무에 무료로 사용할 수 있는 소스 공개 발표 에이전트 스킬. 점·선·면 HTML 데모를 체험하고 시작 요청문을 만들어보세요. 도구 재판매·외부 생성 서비스 사업은 별도 허가가 필요합니다.|A source-available presentation agent skill, free for personal and internal business use. Explore interactive HTML motion demos and create your starting prompt. Tool resale and external generation services require permission.'''

def main():
    page=(ROOT/'docs/index.html').read_text(encoding='utf-8')
    pairs=[line.split('|',1) for line in TRANSLATIONS.splitlines()]
    # Match all original strings in one pass so translations cannot translate each other.
    mapping=dict(pairs)
    mapping.update({'발표 안에서, 근거까지 열어보세요.':'Open the evidence inside your presentation.','마케팅 분석을 추가 HTML로 함께 담았습니다.':'Marketing analysis, included as supporting HTML.','왼쪽 조정값·슬라이서, 오른쪽 수치·차트.':'Controls and slicers on the left. Visual results on the right.','기초 설정부터 시작하고, 필요한 분석을 추가하세요.':'Start with the basics, then add the analysis you need.','실제 브라우저에서 확인한 마케팅 분석 화면: 왼쪽 필터와 오른쪽 성과 차트':'Marketing analysis verified in a real browser: left-side filters and right-side performance charts','발표 + 추가 자료 체험 ↗':'Try the presentation + resources ↗','국문 사용설명서 ↗':'English user guide ↗','분석 HTML만 열기 ↗':'Open supporting HTML only ↗','신규 가상 캠페인 24개 기록입니다. 실제 성과나 임의의 엑셀 자동 변환을 뜻하지 않습니다. 추가 자료를 닫으면 같은 발표 단계로 돌아옵니다.':'24 original fictional campaign records, not measured results or arbitrary Excel conversion. Close the supporting material to return to the same presentation step.'})
    mapping.update({'도움이 되셨나요? ⭐ Star 주시겠어요?': 'Finding this useful? Give it a ⭐', '여러분의 Star는 다음 업데이트를 만드는 힘이 됩니다.': 'Your star encourages the next update.', '⭐ GitHub에 Star 남기기 ↗': '⭐ Star on GitHub ↗', 'GitHub에서 로그인 후 저장소 상단의 Star를 눌러주세요. 응원은 선택이며 다운로드는 바로 가능합니다.': 'Sign in on GitHub and click Star at the top of the repository. Stars are optional; downloads are available right away.'})
    mapping.update({'엑셀과 PPT를 HTML로.': 'Excel &amp; PPT to HTML.', '영상처럼 생동감 있게.': 'Bring your data to life.', '엑셀 분석과 PPT 발표를 HTML로 구성해,': 'Turn Excel analysis and PPT presentations into HTML.', '차트·슬라이서·영상 같은 모션까지 담는 에이전트 스킬.': 'Charts, slicers and video-like motion in one agent skill.', 'Excel and PPT to HTML Motion Agent 홈': 'Excel and PPT to HTML Motion Agent home', '엑셀 분석과 PPT 발표를 인터랙티브 HTML로 만드는 에이전트 스킬. 차트·슬라이서·영상 같은 HTML 모션을 지원하며, MP4 저장은 후속 기능입니다. 개인·내부 업무에 무료입니다.': 'An agent skill for interactive HTML from Excel analysis and PPT presentations, with charts, slicers and video-like HTML motion. MP4 export is deferred. Free for personal and internal use.'})
    page=re.sub('|'.join(re.escape(k) for k in sorted(mapping,key=len,reverse=True)),lambda m:mapping[m[0]],page)
    page=page.replace('lang="ko"','lang="en"').replace('demo.html','demo.en.html').replace('href="index.en.html" lang="en"','href="index.html" lang="ko"').replace('English</a>','한국어</a>')
    page=page.replace('lang="ko" hreflang="en"','lang="ko" hreflang="ko"').replace('href="license.html"','href="license.en.html"')
    page=page.replace('marketing-presentation.html','marketing-presentation.en.html').replace('marketing-analysis.html','marketing-analysis.en.html').replace('guide.ko.html','guide.en.html')
    (ROOT/'docs/index.en.html').write_text(page,encoding='utf-8',newline='\n')
    config=json.loads((ROOT/'examples/motion-stories/stories.json').read_text(encoding='utf-8'))
    config['language']='en'
    stories=[
        ('Delivery routes','Complex routes become one clear flow.','Orders gather, regions take shape, and vehicles start moving.',['Collect orders','Group regions','Connect routes','Follow deliveries'],'Fictional coordinates and predefined routes. Not an optimization engine or measured road performance.'),
        ('Marketing funnel','When attention becomes conversion.','Follow the flow from channels to engagement, purchase and return visits.',['Reach people','Build interest','Create conversions','Bring people back'],'All counts and conversion rates are fictional. Moving dots are visual symbols, not customer counts.'),
        ('Warehouse flow','From receiving to shipping, in one view.','Watch parcels move, racks fill, and orders leave the warehouse.',['Receive and inspect','Sort and store','Pick orders','Pack and ship'],'An original fictional warehouse. Not a real facility layout, operating condition or throughput claim.')
    ]
    for story,values in zip(config['stories'],stories):
        for key,value in zip(('label','title','lead','phases','note'),values):story[key]=value
    (ROOT/'examples/motion-stories/stories.en.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    sys.path.insert(0,str(ROOT/'skills/ppt-to-html/scripts'))
    from build_motion_demo import build
    (ROOT/'docs/demo.en.html').write_text(build(config),encoding='utf-8',newline='\n')

if __name__=='__main__':main()
