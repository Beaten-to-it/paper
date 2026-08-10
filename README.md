# Paper Lab

SW 조직의 AI 전환과 변화주도자 네트워크를 연구하는 박사과정 논문 분석·NotebookLM 산출물 허브입니다.

- 공개 사이트: https://beaten-to-it.github.io/paper/
- 대용량 산출물: GitHub Releases
- 사이트 콘텐츠: `site/`

## 공개 원칙

- 자체 작성한 분석, 연구설계, 프롬프트, 슬라이드, 음성, 인포그래픽만 공개합니다.
- 제3자 논문 원문 PDF, 회사 기밀, 개인정보, 임시 파일은 공개하지 않습니다.
- 아직 만들지 않은 산출물은 숨기지 않고 `미생성`으로 표시합니다.

## 검증

```powershell
python -m unittest discover -s tests -v
python tools/validate_catalog.py site/data/catalog.json site
```
