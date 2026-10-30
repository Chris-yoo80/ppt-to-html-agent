# 스킬 설치와 사용

한국어 · [English](install.md)

초기 버전입니다. Claude Code·Codex CLI에서 가상 5장 PPT의 입력·생성·수정 과정을 확인했습니다. 마케팅 보충 HTML과 상위 발표는 Edge에서도 확인했으며, 범위와 한계는 [브라우저 검증 기록](browser-verification-2026-10-23.md)에 있습니다. 이 도구들은 AI API에 연결하지 않습니다. 실제 에이전트 실행에는 사용 중인 AI 환경과 해당 구독료·사용료가 적용됩니다.

HTML 사용설명서: [한국어 HTML](https://chris-yoo80.github.io/ppt-to-html-agent/guide.ko.html) / [English HTML](https://chris-yoo80.github.io/ppt-to-html-agent/guide.en.html). 마케팅 발표 예제 안의 추가 자료로도 들어 있습니다.

사용 조건은 프로젝트 전용 [Community License 1.0](../LICENSE)을 따릅니다. 개인·비상업·회사 내부 사용은 무료입니다. 도구 판매나 외부 생성·변환 서비스 사업은 별도 서면 허가가 필요합니다. 완성한 발표물은 발표물 예외 조항의 목적 범위에서 고지를 유지한 채 공유할 수 있습니다. MIT·OSI 승인 오픈소스가 아닌 소스 공개 패키지입니다. [사용 조건 자세히](license.ko.md)

## 시작 전에 준비할 것

- **Claude Code 또는 Codex**가 설치되고 로그인되어 있어야 합니다. 이 패키지는 두 도구를 설치하거나 로그인해 주지 않습니다. 일반 ChatGPT·Claude 웹 채팅에서는 이 로컬 스킬을 실행할 수 없습니다.
- **Python 3.10 이상**이 필요합니다. 터미널에서 확인하세요.

  | 운영체제 | 확인 명령 | 명령에서 쓸 이름 |
  |---|---|---|
  | Windows | `python --version` (또는 `py --version`) | `python` 또는 `py` |
  | macOS / 리눅스 | `python3 --version` | `python3` |

  명령을 찾을 수 없다고 나오면 [python.org](https://www.python.org/downloads/)에서 설치합니다. 이 저장소의 예시는 `python`으로 적혀 있으니 macOS·리눅스에서는 `python3`으로 바꿔 입력하세요.
- Node.js는 개발용 검사에만 필요합니다.

## 1. 스킬 받기

[스킬 ZIP](https://chris-yoo80.github.io/ppt-to-html-agent/downloads/ppt-to-html.zip)을 내려받거나 이 저장소를 복제합니다. 어느 쪽이든 `ppt-to-html` 폴더 전체가 필요합니다. `SKILL.md`, `scripts/`, `assets/`, `references/`를 따로 떼지 마세요.

## 가장 쉬운 방법: AI에게 설치 맡기기

ZIP을 아무 곳(예: 다운로드 폴더)에 풀고, Claude Code 또는 Codex에서 **내 프로젝트 폴더**를 연 뒤 이렇게 요청합니다.

```text
다운로드 폴더의 ppt-to-html 폴더를 이 프로젝트의 Claude Code 스킬로 설치해줘.
최종 위치가 .claude/skills/ppt-to-html/SKILL.md가 되게 하고, 한 단계 더 깊으면 안 돼.
설치 후 경로를 확인하고 스킬 호출 방법을 알려줘.
```

Codex는 "Codex 스킬"과 `.agents/skills/ppt-to-html/SKILL.md`로 바꿔 요청합니다. 모든 프로젝트에서 쓰려면 `~/.claude/skills` 또는 `~/.agents/skills`에 설치해 달라고 하세요. 폴더 생성·파일 복사 권한을 물어볼 수 있습니다. 끝나면 [4. 설치 확인하기](#4-설치-확인하기)로 확인합니다.

아무 폴더에 둔 `SKILL.md`를 "읽고 적용해줘"라고 해도 동작할 수 있습니다. 하지만 새 대화마다 다시 말해야 하고, `/ppt-to-html`·`$ppt-to-html` 호출을 쓸 수 없으며, 참고 문서를 건너뛸 수 있습니다. 설치하는 편이 더 안정적입니다.

직접 복사하고 싶다면 아래 2~4단계를 따르세요.

## 2. 설치 위치 고르기

| 도구 | 이 프로젝트에서만 (내 프로젝트 폴더 안) | 모든 프로젝트에서 (내 사용자 폴더) | 호출 |
|---|---|---|---|
| Claude Code | `.claude/skills/ppt-to-html/` | `~/.claude/skills/ppt-to-html/` | `/ppt-to-html` |
| Codex | `.agents/skills/ppt-to-html/` | `~/.agents/skills/ppt-to-html/` | `$ppt-to-html` |

`~`는 사용자 폴더입니다. Windows는 `C:\Users\<이름>`, macOS는 `/Users/<이름>`, 리눅스는 `/home/<이름>`입니다. "내 프로젝트 폴더"는 PPT·엑셀 작업을 하는 폴더이며, 이 저장소가 아닙니다.

**최종 위치는 항상 `.../skills/ppt-to-html/SKILL.md`여야 합니다.** `SKILL.md`가 한 단계 더 깊으면 인식되지 않습니다.

## 3a. ZIP으로 설치하기 (터미널 없이)

1. 위 표의 설치 위치를 엽니다. `.claude`, `.agents`처럼 점(.)으로 시작하는 폴더는 기본적으로 숨겨져 있습니다.
   - **Windows:** 파일 탐색기 → 보기 → 표시 → 숨긴 항목을 켭니다. 폴더가 없으면 새로 만듭니다.
   - **macOS:** Finder에서 `Cmd+Shift+.`을 누르면 숨김 폴더가 보입니다. Finder가 점으로 시작하는 이름을 거부하면 아래 3b의 터미널 명령을 사용하세요.
2. ZIP을 풉니다. 안에는 `ppt-to-html/` 폴더 하나가 있습니다.
   - **Windows 주의:** "압축 풀기"는 ZIP 이름으로 폴더를 하나 더 만들어 `skills\ppt-to-html\ppt-to-html\SKILL.md`가 됩니다. 대상 경로를 `skills` 폴더 자체로 지정하거나, 푼 뒤 안쪽 `ppt-to-html` 폴더를 한 단계 위로 옮기세요.
3. `SKILL.md`가 `skills/ppt-to-html/` 바로 안에 있는지 확인합니다.

## 3b. 터미널로 설치하기

**내 프로젝트 폴더**에서 실행합니다(이 프로젝트에서만 사용). `<download>`는 압축을 푼 `ppt-to-html` 폴더가 들어 있는 위치로 바꾸고, 저장소를 복제했다면 `<복제한 위치>/skills`로 바꿉니다.

Claude Code, PowerShell:

```powershell
New-Item -ItemType Directory -Force .claude/skills | Out-Null
Copy-Item -Recurse <download>/ppt-to-html .claude/skills/
```

Claude Code, macOS / 리눅스:

```sh
mkdir -p .claude/skills
cp -R <download>/ppt-to-html .claude/skills/
```

Codex는 같은 명령에서 `.claude/skills`를 `.agents/skills`로 바꿉니다.

모든 프로젝트에서 쓰려면 `.claude/skills`를 `~/.claude/skills`(Claude Code) 또는 `~/.agents/skills`(Codex)로 바꿉니다. PowerShell에서는 `$HOME/.claude/skills` 또는 `$HOME/.agents/skills`로 씁니다.

## 4. 설치 확인하기

1. Claude Code 또는 Codex에서 내 프로젝트 폴더를 엽니다. 이미 실행 중이었다면 다시 시작합니다.
2. Claude Code는 `/`, Codex는 `$`(또는 `/skills`)를 입력해 목록에 `ppt-to-html`이 보이는지 확인합니다.
3. 보이지 않으면 경로가 `skills/ppt-to-html/SKILL.md`로 끝나는지(위 Windows 주의 참고), 설치한 폴더를 열었는지 확인합니다.

## 업데이트·삭제

업데이트할 때는 기존 `ppt-to-html` 스킬 폴더를 지우고 새 폴더를 설치합니다. 기존 폴더 위에 덮어쓰면 새 버전에서 삭제된 파일이 남습니다. 삭제하려면 `skills/` 안의 `ppt-to-html` 폴더를 지우면 됩니다.

## 첫 요청

내 프로젝트 폴더에 접근 가능한 `.pptx`나 `.xlsx`를 넣고 다음과 같이 요청합니다.

```text
ppt-to-html 스킬로 첨부한 PPT를 HTML 발표로 만들어줘.
먼저 목적·청중·시간·화면 크기·글꼴·모션 빈도·재생 방식·점선면 그래픽 설정을 물어봐줘.
전체 제작 전에 목차와 대표 장면 하나를 먼저 보여줘.
원본의 수치와 의미는 유지하고, MP4 출력은 필요 없어.
```

구버전 `.ppt`와 암호가 설정된 파일은 지원하지 않습니다. 소개 사이트의 설정 양식으로 이 요청문을 내 설정에 맞게 만들 수도 있습니다. 양식은 PPT를 업로드하거나 AI 서비스에 연결하지 않습니다.

## AI 없이 도구만 실행해 보기

이 저장소를 복제한 폴더에서 실행합니다(macOS·리눅스는 `python3`).

```sh
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output output/library.html
```

결과 HTML을 허용된 브라우저에서 엽니다. 플레이어와 스타일이 파일 안에 들어 있고 외부 글꼴·스크립트가 필요 없습니다. 화면의 화살표나 키보드 화살표, Home, End, A(자동 재생 사용 시)로 조작합니다. 기본 설정에서는 마지막 단계에서 멈춥니다. 브라우저나 삽입 환경 정책에 따라 전체 화면이 제한될 수 있습니다.

접근 가능한 PPTX에서 내용을 추출하려면:

```sh
python skills/ppt-to-html/scripts/extract_pptx.py private-inputs/input.pptx --output work/source.json
```

이 명령은 텍스트·표·메모·미디어 목록을 추출합니다. 발표 구성은 만들지 않습니다. 추출한 내용을 에이전트에게 해석하게 하고, 가능하면 원본 슬라이드를 함께 확인한 뒤 장면 JSON을 작성하게 하세요.

## 개인정보와 공개

비공개 원본, 추출한 메모, 고객용 결과물은 공개 저장소에 올리지 마세요. `private-inputs/`, `work/`, `output/`은 무시되는 편의 폴더일 뿐이며 `.gitignore`가 내용 검토를 대신하지 않습니다. 커밋 전에 파일 목록을 직접 확인하고, 업무 자료가 있는 상위 폴더에서 저장소를 만들지 마세요.

다른 ChatGPT·Claude 환경은 설치·실행 방식이 다를 수 있습니다. 검증하지 않은 환경의 호환성은 보장하지 않습니다.
