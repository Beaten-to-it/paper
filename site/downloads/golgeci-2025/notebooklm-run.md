# NotebookLM 실행 기록: Golgeci et al. (2025)

- 실행일: 2026-08-11
- 언어와 형식: 한국어 Deep Dive 오디오, Presenter Slides, 인포그래픽
- 소스 수: 1개
- 단일 소스: *Confronting and alleviating AI resistance in the workplace: A process framework*
- 소스 격리: 다른 논문이나 웹 자료를 추가하지 않은 별도 노트북에서 생성

## 생성 산출물과 무결성

| 종류 | 공개 파일 | 크기(byte) | SHA-256 |
|---|---|---:|---|
| 한국어 심층 오디오 | `Golgeci-2025-NotebookLM-audio-overview.m4a` | 27,407,638 | `0952b92a20b1f184ac3bea8101654d44cbf9441b1084cc3ddb9274f14feed714` |
| 세미나 PPTX | `Golgeci-2025-NotebookLM-seminar-deck.pptx` | 13,674,991 | `6e445d67d02f640895366a0074434a85fdd37885130e692674664312e49f3f53` |
| 세미나 PDF | `Golgeci-2025-NotebookLM-seminar-deck.pdf` | 11,610,088 | `30c7ffb8230a7f41e5399bd6d524870f5f6b54f2dcb5be6e090e2b607ff42234` |
| 인포그래픽 | `infographic.png` | 4,523,233 | `9eb39378e432c80607331a05048226e9c37ebc88e77642bbea84d5b7b8f9b749` |

## 검증

- 오디오는 AAC, 44.1 kHz, 2채널, 851.568617초이며 `ffprobe` 확인과 전체 디코딩을 통과했다.
- PPTX 12장과 PDF 12쪽의 장수가 일치하고, 오버플로 검사와 전체 슬라이드 렌더 육안 검토를 통과했다.
- 2,752 × 1,536px 인포그래픽을 원본 해상도로 검토했다.
- 논문의 경로는 실증 결과가 아닌 개념적 명제이며, 공식 리더와 비공식 AI 챔피언 역할은 후속 연구 가설이라는 경계를 확인했다.

이 기록은 재현성과 파일 확인을 위한 공개 메타데이터다. 개인 NotebookLM 주소와 로컬 작업 경로는 공개하지 않는다.
