"""English UI text for the offline motion gallery."""
import re

TEXT={
 '모션 끄기':'Turn motion off','모션 켜기':'Turn motion on',
 '인쇄 / PDF로 저장':'Print / Save as PDF','인쇄 / PDF':'Print / PDF',
 '데모로 돌아가기':'Back to demo',
 '세 예제의 핵심 정보 · A4 가로 · 인쇄 창에서 PDF 저장을 선택하세요.':'Key facts from all three examples · A4 landscape · choose Save as PDF in the print dialog.',
 '모션 예제 선택':'Choose a motion story','가상 업무 흐름 모션 그래픽':'Fictional workflow motion graphic',
 '동영상형 모션 재생 조작':'Motion playback controls','이전 설명 단계':'Previous chapter','다음 설명 단계':'Next chapter',
 '모션 타임라인 탐색':'Seek motion timeline','다시 보기 ↻':'Restart ↻','다시 보기 ↺':'Restart ↺','설명 단계 선택':'Choose a chapter',
 '물류센터':'DEPOT','12곳':'12 stops','가상 배송처':'Fictional delivery stops',
 '가상 좌표의 총 경로 길이 비교':'Total route length on fictional coordinates',
 '인지':'Reach','관심':'Engage','구매':'Buy','재방문':'Return',
 '도달':'Reach','참여':'Engage','전환':'Convert','유지':'Retain',' · 가상 인원':' · fictional people',
 '콘텐츠':'Content','검색':'Search','이메일':'Email','명':' people',
 '가상 캠페인 도달 인원':'Fictional campaign reach','가상 시나리오의 도달 대비 전환율':'Fictional reach-to-purchase rate',
 '입고':'Receive','적치':'Store','피킹':'Pick','출고':'Ship','가상 공정 · 처리 성능을 뜻하지 않음':'Fictional process · not measured throughput',
 '모션 줄임':'Reduced motion','Ⅱ 일시 정지':'Ⅱ Pause','▶ 재생':'▶ Play',
 '${p+1}단계 ${story.phases[p]}, ${Math.floor(time)}초':'Chapter ${p+1}: ${story.phases[p]}, ${Math.floor(time)} seconds',
}

def english(text):
    return re.sub('|'.join(re.escape(k) for k in sorted(TEXT,key=len,reverse=True)),lambda m:TEXT[m[0]],text)
