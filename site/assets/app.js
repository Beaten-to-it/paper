const statusLabels = {
  complete: "완료",
  missing: "미생성",
  in_progress: "진행 중",
  not_applicable: "해당 없음",
  withheld: "공개 제외",
};

const typeLabels = {
  source_paper: "원문",
  korean_version: "한국어본",
  analysis: "분석",
  notebooklm_prompt: "NotebookLM 프롬프트",
  notebooklm_run: "NotebookLM 실행기록",
  audio: "음성",
  slides: "PPT",
  slide_pdf: "슬라이드 PDF",
  infographic: "인포그래픽",
  model_contribution: "연구모형 기여",
  model_diagram: "연구모형 다이어그램",
  spreadsheet: "XLSX",
  construct_dictionary: "구성개념 사전",
  pilot_protocol: "파일럿 프로토콜",
  proposition_traceability: "명제 추적성",
  research_design: "연구설계",
  research_model: "연구모형",
  research_synthesis: "연구 종합",
};

const escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

function rightsBadges(paper, artifact) {
  if (!paper.rights) return "";
  const labels = [];
  if (artifact.type === "source_paper") {
    labels.push(paper.rights.redistribution === "allowed" ? "CC BY 4.0" : "공식 원문 링크");
  }
  if (artifact.type === "korean_version") {
    labels.push(artifact.translation_kind === "full_unofficial" ? "비공식 전문 번역" : "전문 번역 아님");
  }
  if (artifact.protected) labels.push("암호 필요");
  return labels.length
    ? `<div class="artifact__badges">${labels.map((label) => `<span class="rights-badge">${escapeHtml(label)}</span>`).join("")}</div>`
    : "";
}

function artifactActions(artifact) {
  if (artifact.status !== "complete") return "";
  const actions = [];
  if (artifact.href?.endsWith(".md")) {
    actions.push(`<a href="viewer.html?file=${encodeURIComponent(artifact.href)}">사이트에서 읽기</a>`);
    actions.push(`<a href="${escapeHtml(artifact.href)}" download>원본 받기</a>`);
  } else if (artifact.storage === "external") {
    actions.push(`<a href="${escapeHtml(artifact.href)}" target="_blank" rel="noopener noreferrer">공식 원문 열기</a>`);
  } else if (artifact.href) {
    actions.push(`<a href="${escapeHtml(artifact.href)}">열기 · 다운로드</a>`);
  }
  if (artifact.protected) {
    actions.push(`<a class="locked-action" href="protected-viewer.html?id=${encodeURIComponent(artifact.id)}">암호 입력 후 열기</a>`);
  }
  return actions.length ? `<div class="artifact__actions">${actions.join("")}</div>` : "";
}

function artifactHtml(artifact, paper) {
  const status = statusLabels[artifact.status] || artifact.status;
  const player = artifact.status === "complete" && artifact.type === "audio"
    ? `<audio controls preload="none" src="${escapeHtml(artifact.href)}"></audio>`
    : "";
  const preview = artifact.status === "complete" && ["infographic", "model_diagram"].includes(artifact.type)
    ? `<a href="${escapeHtml(artifact.href)}"><img class="artifact__preview" src="${escapeHtml(artifact.href)}" alt="${escapeHtml(artifact.title)}" loading="lazy"></a>`
    : "";
  return `<article class="artifact" data-type="${escapeHtml(artifact.type)}">
    <div class="artifact__top">
      <h4>${escapeHtml(typeLabels[artifact.type] || artifact.type)}</h4>
      <span class="status status--${escapeHtml(artifact.status)}">${escapeHtml(status)}</span>
    </div>
    <p>${escapeHtml(artifact.title)}</p>
    ${rightsBadges(paper, artifact)}${preview}${player}${artifactActions(artifact)}
  </article>`;
}

function paperHtml(paper, selectedType) {
  const artifacts = paper.artifacts.filter((artifact) => selectedType === "all" || artifact.type === selectedType);
  if (!artifacts.length) return "";
  return `<article class="paper-card">
    <header class="paper-card__header">
      <div>
        <h3>${escapeHtml(paper.title)}</h3>
        <p class="citation">${escapeHtml(paper.citation)}</p>
        <p class="paper-summary">${escapeHtml(paper.summary)}</p>
      </div>
      <span class="paper-badge">${escapeHtml(paper.kind === "research-design" ? "연구설계" : "논문")}</span>
    </header>
    <div class="artifact-grid">${artifacts.map((artifact) => artifactHtml(artifact, paper)).join("")}</div>
  </article>`;
}

async function start() {
  const response = await fetch("data/catalog.json");
  if (!response.ok) throw new Error(`catalog ${response.status}`);
  const catalog = await response.json();
  const list = document.querySelector("#paper-list");
  const search = document.querySelector("#search-input");
  const filter = document.querySelector("#type-filter");
  document.querySelector("#paper-count").textContent = catalog.papers.length;
  document.querySelector("#artifact-count").textContent = catalog.papers.flatMap((paper) => paper.artifacts).filter((artifact) => artifact.status === "complete").length;
  document.querySelector("#updated-date").textContent = catalog.updated;
  document.querySelector("#loading").hidden = true;

  const types = [...new Set(catalog.papers.flatMap((paper) => paper.artifacts.map((artifact) => artifact.type)))].sort();
  filter.insertAdjacentHTML("beforeend", types.map((type) => `<option value="${escapeHtml(type)}">${escapeHtml(typeLabels[type] || type)}</option>`).join(""));

  const render = () => {
    const query = search.value.trim().toLowerCase();
    const selectedType = filter.value;
    const visible = catalog.papers.filter((paper) => [paper.title, paper.citation, paper.summary].join(" ").toLowerCase().includes(query));
    const html = visible.map((paper) => paperHtml(paper, selectedType)).join("");
    list.innerHTML = html || '<p class="empty">조건에 맞는 산출물이 없습니다.</p>';
  };
  search.addEventListener("input", render);
  filter.addEventListener("change", render);
  render();
}

start().catch((error) => {
  document.querySelector("#loading").textContent = `카탈로그를 불러오지 못했습니다: ${error.message}`;
});
