# Paper Lab

SW 조직의 AI 전환과 변화주도자 네트워크를 연구하는 박사과정 논문 분석·NotebookLM 산출물 허브입니다.

- 공개 사이트: https://beaten-to-it.github.io/paper/
- 대용량 산출물: GitHub Releases
- 사이트 콘텐츠: `site/`

## 공개 원칙

- CC BY 4.0 세 편은 출처·라이선스·변경 고지를 포함한 원문과 비공식 전문 번역을 공개합니다.
- 권리 제한 두 편은 공식 원문 링크와 전문 번역이 아닌 한국어 학습가이드를 공개합니다.
- 권리 제한 원문과 개인 학습용 전문 번역 네 파일은 브라우저에서만 복호화되는 암호문으로 제공합니다. 평문은 저장소와 Release에 올리지 않습니다.
- 분석, NotebookLM 실행기록, 음성, 발표자료와 인포그래픽은 학습·연구설계 자료이며 동료심사 논문을 대체하지 않습니다.
- 회사 기밀, 개인정보, 비공개 NotebookLM 주소와 임시 QA 파일은 공개하지 않습니다.

## 카탈로그 구조

- 논문 5편은 각각 `원문 / 한국어본 / 분석 / NotebookLM 프롬프트 / 실행기록 / 음성 / PPT / 슬라이드 PDF / 인포그래픽 / 연구모형 기여`의 10개 슬롯을 가집니다.
- 연구설계 그룹의 12개 산출물을 더해 6개 그룹, 총 62개 완료 항목을 `site/data/catalog.json`에서 관리합니다.
- 대용량 공개 파일은 `artifacts-2026-08-11-v1`, `artifacts-2026-08-11-v2` 또는 `artifacts-2026-08-12-v3` GitHub Release에, Markdown·PNG·암호문은 Pages에 둡니다.

## 검증

```powershell
python -m unittest discover -s tests -v
node --test tests/protected_crypto.test.mjs
python tools/validate_catalog.py site/data/catalog.json site
```
