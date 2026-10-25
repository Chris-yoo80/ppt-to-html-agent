# Excel & PPT → HTML · Motion Agent

**도움이 되셨나요? [⭐ Star 주시겠어요?](https://github.com/Chris-yoo80/ppt-to-html-agent)** 여러분의 응원이 다음 업데이트를 만드는 힘이 됩니다. Star는 선택이며, 바로 내려받아 사용할 수 있습니다.

**엑셀과 PPT를 HTML로, 영상처럼 움직이는 인터랙티브 콘텐츠까지.**

PPT 발표와 검토한 엑셀 분석을 인터랙티브 HTML로 구성하고, 차트·슬라이서·영상 같은 모션을 담는 에이전트 스킬입니다. 모션은 HTML 안에서 재생하며 MP4 저장은 후속 기능입니다. 흐름은 영상처럼 재생하고, 설명할 순간에는 멈추거나 한 단계씩 진행합니다.

**초기 버전입니다.** Claude Code·Codex CLI에서 가상 PPT 입력·변환·수정 과정을 확인했습니다. 실제 Edge에서는 마케팅 보충 HTML의 조작과 발표 복귀를 검증했습니다. 모든 파일·환경의 호환성을 보장하는 것은 아닙니다.

[국문 HTML 사용설명서](https://chris-yoo80.github.io/ppt-to-html-agent/guide.ko.html) · [English HTML guide](https://chris-yoo80.github.io/ppt-to-html-agent/guide.en.html) · [발표 + 추가 자료 체험](https://chris-yoo80.github.io/ppt-to-html-agent/marketing-presentation.en.html)

## 발표 안에 추가 HTML 넣기

**추가 자료**를 누르면 마케팅 분석과 HTML 설명서를 열 수 있습니다. 발표 자동 재생은 멈추고, 닫으면 같은 단계로 돌아옵니다. 분석 설정은 같은 발표 세션에서 자료를 오가거나 다시 열어도 유지됩니다.

초기 질문에서 PDF 필요 범위와 백업자료 배치를 정합니다. **인쇄 / PDF**는 모든 장면과 설명 단계를 펼쳐 미리보기로 보여주며 브라우저 인쇄 창에서 저장합니다. 분석 자료는 현재 필터 기준으로 별도 출력합니다. 백업 HTML은 이름을 지정한 자료 탭에 넣으며 원본 엑셀 첨부는 별도 선택입니다.

![실제 Edge에서 확인한 좌측 조정값·우측 차트의 마케팅 분석 화면](docs/assets/marketing-dashboard.jpg)

처음에는 목적·지표·화면·글꼴·공유 설정을 질문합니다. 왼쪽 기간·채널·시장 슬라이서로 범위를 정하고, 오른쪽 KPI·추이·전환 흐름·채널 비교를 확인합니다. 상세표와 가정 시나리오는 기초 화면을 정한 뒤 추가합니다. HTML 저장은 현재 설정과 필터를 함께 보관합니다.

새로 작성한 가상 캠페인 24개 기록을 사용했습니다. 원본 엑셀은 자동 첨부하지 않습니다. CSV 버튼을 꺼도 HTML에 포함된 분석 데이터가 제거되지는 않습니다. 임의의 엑셀 수식을 자동 변환하는 기능은 아닙니다. [실제 브라우저 검증 기록](docs/browser-verification-2026-10-23.md)을 참고하세요. 저장 파일의 `file://` 재열기는 브라우저 정책상 미검증입니다.

![배송·마케팅·창고의 가상 모션 예제 개념도](docs/assets/motion-preview.svg)

## 대표 데모

| 주제 | 설명 흐름 |
|---|---|
| 배송 경로 | 주문 집결 → 권역 분리 → 사전 구성 경로 연결 → 차량 이동 |
| 마케팅 퍼널 | 인지 → 관심 → 구매 → 재방문 |
| 입체 창고 | 입고·검수 → 분류·적치 → 피킹 → 포장·출고 |

각 24초로 재생되며 일시정지·단계 선택·타임라인 탐색을 지원합니다. 위 이미지는 정적인 개념도이며, 실제 조작은 `docs/index.html`의 갤러리에서 할 수 있습니다. [한국어 데모](https://chris-yoo80.github.io/ppt-to-html-agent/) · [English](https://chris-yoo80.github.io/ppt-to-html-agent/index.en.html)

```text
python skills/ppt-to-html/scripts/build_motion_demo.py examples/motion-stories/stories.json --output output/motion-stories.html
```

예제 파일은 서버·인터넷·AI 키 없이 열립니다. 사용자 PPT를 새로 해석하고 제작하는 에이전트 실행에는 자신의 AI 환경이 필요합니다. 예제는 가상 데이터로 직접 작성했으며 자동 PPT 변환 완료 사례나 실제 최적화 성능을 의미하지 않습니다.

## 무료 공개 방식

- 스킬과 제작 코드를 GitHub에 공개합니다. [프로젝트 전용 Community License 1.0](LICENSE)을 적용합니다.
- 개인·비상업적 활동과 회사 내부 업무 사용·수정은 무료입니다. 도구 재판매·유료 제품 포함·외부 생성 서비스 사업은 별도 서면 허가가 필요합니다.
- 생성한 발표물은 포함된 플레이어와 함께 업무·고객 발표에 공유·전달할 수 있습니다. 저작권·라이선스 고지는 유지해야 합니다. [사용 조건 자세히](docs/license.ko.md)
- MIT·OSI 승인 오픈소스가 아닌 **내부 업무에 무료로 쓸 수 있는 소스 공개 에이전트**입니다. 라이선스는 프로젝트 전용 초안이며 별도 법률 검토는 받지 않았습니다.
- 소개·체험 페이지는 GitHub Pages용 정적 파일입니다.
- 사용자는 자신의 Claude Code·Codex 환경에서 실행합니다. AI 구독료·API 비용은 해당 서비스의 조건을 따릅니다.
- 소개 페이지에는 PPT 업로드나 AI 연결이 없습니다. 입력 설정은 서버로 전송하거나 저장하지 않습니다.
- 회사 자료는 공개 패키지에 포함하지 않습니다. 대표 예제는 새로 작성한 가상 배송 경로·마케팅 퍼널·입체 창고 모션입니다. 도서관 예제는 기본 템플릿으로 남겨둡니다.

## 시작 질문

1. 발표 목적·청중·시간
2. 화면 비율과 기준 크기
3. 글꼴과 디자인 분위기
4. 움직임의 빈도
5. 클릭·키보드·자동 재생 중 진행 방식
6. 점·선·면 모션을 사용할 장면
7. 오프라인 HTML·편집용 소스 등 산출물

기존에 답한 항목은 다시 묻지 않고, '추천 설정으로'라는 한 답으로 기본값을 선택할 수 있습니다. 화면 크기, 움직임의 양과 자동 재생 여부는 각각 다른 설정으로 다룹니다.

## 기능

PPTX 추출기는 장표 순서대로 텍스트·표·메모와 미디어 목록을 읽습니다. 내용 해석과 발표 설계는 호스트 AI가 수행하고, 검토한 장면 구성을 JSON으로 작성합니다. 생성기는 이를 외부 글꼴·스크립트 없이 열리는 단일 HTML로 만듭니다.

HTML 내부의 모션은 점 등장, 선 연결, 면의 전개를 지원합니다. MP4 파일 생성은 다음 버전 범위입니다.

대표 모션 갤러리는 각 24초짜리 배송·마케팅·창고 예제를 제공합니다. 재생·정지, 네 단계 선택, 타임라인 탐색을 지원합니다. 경로와 수치는 가상 데이터이며 실제 최적화 엔진이나 물리 시뮬레이터가 아닙니다.

## 빠른 실행

[환경별 설치 안내](docs/install.md)를 참고하세요. Python 3.10 이상으로 예제 생성기를 단독 실행할 수도 있습니다.

```text
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output output/library.html
```

결과 파일을 허용된 브라우저에서 열고 화면의 화살표로 진행합니다. 예제는 3개 장면·9개 단계이며 마지막에 정지합니다. 입력은 가상 Markdown에서 직접 만든 장면 JSON으로, 실제 PPT 자동 변환 사례는 아닙니다.

모션 데모의 **핵심 정보** 요약에 수치·설명·4단계를 남깁니다. **모션 끄기** 후에도 수동 이동이 가능하고, **인쇄 / PDF**는 세 예제의 전체 요약을 보여줍니다. 발표의 모션 줄이기는 현재 장면의 모든 항목을 표시하고 자동 재생을 멈춥니다. 인쇄에서 돌아오면 원래 주제·시점 또는 단계가 유지됩니다. 저장된 PDF 검증은 별도입니다.

## 수치 검수

단위 검수에는 **길이·면적·부피·질량·시간·속도·에너지/전력·복합/업무 단위**도 포함합니다. 오프라인 검수 도구가 지원 단위의 제공된 환산값을 대조하고, 미지원 단위·차원 불일치·포장 환산 기준 누락은 확인 필요로 남깁니다. 임의의 엑셀을 자동 해석하거나 원화 캠페인 차트를 범용 단위로 바꾸는 기능은 아닙니다. [가상 단위 예제](examples/unit-verification/README.ko.md)를 참고하세요.


수치 검수는 **단위·환산, 분모, 필터·범위, 반올림, 모션 끔·인쇄 정보 유지, 원본 시트·범위**를 대조합니다. 근거 화면에서 정의와 현재 선택 범위를 확인하고, 최종 보고에는 항목별 **통과 / 확인 필요**와 근거를 남깁니다. 메타데이터만으로 원본 일치를 보증하지 않습니다. [수치 검수 결과](docs/verification.ko.md)를 확인하세요.

## 현재 한계

원본 PPT의 배치를 그대로 복원하거나 OCR·차트 워크북·DRM을 처리하지 않습니다. 기본 템플릿은 장면당 짧은 항목 1~4개를 지원합니다. 복잡한 레이아웃·지정 글꼴은 추가 구현과 화면 검증이 필요합니다.

구문·데이터 검사는 실제 화면 검증을 대신하지 않습니다. 브라우저 렌더링, 모든 단계 조작, 다른 비율, 인쇄는 별도 확인 대상입니다. 완전한 다중 페이지 PDF와 MP4 출력은 구현하지 않았습니다.

한국어·영어 소개 페이지와 데모는 GitHub Pages의 `main` / `/docs`로 배포합니다. 영문 페이지는 `python tools/localize_site.py`로 재생성합니다.

## 개발 검사 (Development checks)

```text
python -m unittest discover -s tests -v
node --check skills/ppt-to-html/assets/player.js
node --check docs/site.js
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output docs/library-demo.html
python skills/ppt-to-html/scripts/build_motion_demo.py examples/motion-stories/stories.json --output docs/demo.html
node --test tests/motion.test.cjs
```
