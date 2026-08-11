# NotebookLM 실행 기록: Battilana & Casciaro (2012)

- 실행일: 2026-08-11
- 언어와 형식: 한국어 Deep Dive 오디오, Presenter Slides, 인포그래픽
- 소스 수: 1개
- 단일 소스: *Change Agents, Networks, and Institutions: A Contingency Theory of Organizational Change*
- 소스 격리: 다른 논문이나 웹 자료를 추가하지 않은 별도 노트북에서 생성

## 생성 산출물과 무결성

| 종류 | 공개 파일 | 크기(byte) | SHA-256 |
|---|---|---:|---|
| 한국어 심층 오디오 | `Battilana-Casciaro-2012-NotebookLM-audio-overview.m4a` | 37,208,529 | `281e6b0cd85bf675ca07d2e77da3cc4e50e9b22ff453b4faa5d1295ba7c57360` |
| 세미나 PPTX | `Battilana-Casciaro-2012-NotebookLM-seminar-deck.pptx` | 13,981,762 | `a420144a568b7ee5129def8b45229cc3de262bfd246fb0ac6b0f1f41907c9e11` |
| 세미나 PDF | `Battilana-Casciaro-2012-NotebookLM-seminar-deck.pdf` | 1,714,312 | `e22743a8f5aeb77d1e41c35b7826a9267986e2cc427c8f2bcd321e12bf6544ff` |
| 인포그래픽 | `infographic.png` | 4,299,982 | `2f2ddfc4b642642bedc38d28c6be9fc68b4844eacaf711fee291f562e66dd3a9` |

## 검증과 교정

- 오디오는 AAC, 44.1 kHz, 2채널, 1,156.098322초이며 `ffprobe` 확인과 전체 디코딩을 통과했다.
- 최종 PPTX 12장과 PDF 12쪽의 장수가 일치하고, 오버플로 검사와 전체 슬라이드 렌더 육안 검토를 통과했다.
- NotebookLM 표지에 남았던 `[Title]`, `[Subtitle]` 자리표시자를 제거한 교정본을 게시 대상으로 확정했다.
- 2,752 × 1,536px 인포그래픽은 원본 해상도에서 네트워크 폐쇄성과 변화 괴리도의 상황적합 관계가 과도하게 단정되지 않는지 확인했다.

이 기록은 재현성과 파일 확인을 위한 공개 메타데이터다. 개인 NotebookLM 주소와 로컬 작업 경로는 공개하지 않는다.
