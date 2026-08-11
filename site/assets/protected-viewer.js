import {decryptContainer} from "./protected-crypto.js";

const protectedPathPattern = /^protected\/[a-z0-9][a-z0-9-]*\.enc$/;
const protectedAccessModes = new Set([
  "official_link_plus_password_encrypted",
  "public_plus_password_encrypted",
]);

export function resolveProtectedArtifact(catalog, artifactId) {
  if (typeof artifactId !== "string" || !/^[a-z0-9][a-z0-9-]*$/.test(artifactId)) {
    throw new Error("protected artifact is not available");
  }
  const papers = Array.isArray(catalog?.papers) ? catalog.papers : [];
  const matches = papers
    .flatMap((paper) => Array.isArray(paper?.artifacts) ? paper.artifacts : [])
    .filter((artifact) => artifact?.id === artifactId);
  if (matches.length !== 1) {
    throw new Error("protected artifact is not available");
  }
  const artifact = matches[0];
  if (
    artifact.status !== "complete"
    || !protectedAccessModes.has(artifact.access)
    || !["source_paper", "korean_version"].includes(artifact.type)
  ) {
    throw new Error("invalid protected access declaration");
  }
  const href = artifact.protected?.href;
  if (typeof href !== "string" || !protectedPathPattern.test(href)) {
    throw new Error("invalid protected artifact path");
  }
  return {href, title: String(artifact.title || "비공개 PDF")};
}

function startsWithPdfMagic(bytes) {
  return bytes.length >= 5
    && bytes[0] === 0x25
    && bytes[1] === 0x50
    && bytes[2] === 0x44
    && bytes[3] === 0x46
    && bytes[4] === 0x2d;
}

function start() {
  const form = document.querySelector("#unlock-form");
  const passwordInput = document.querySelector("#private-password");
  const submitButton = document.querySelector("#unlock-button");
  const relockButton = document.querySelector("#relock-button");
  const status = document.querySelector("#protected-status");
  const title = document.querySelector("#protected-title");
  const frame = document.querySelector("#protected-frame");
  const artifactId = new URLSearchParams(location.search).get("id") || "";
  let artifact;
  let activeUrl = null;

  const relock = () => {
    frame.hidden = true;
    frame.removeAttribute("src");
    if (activeUrl) {
      URL.revokeObjectURL(activeUrl);
      activeUrl = null;
    }
    relockButton.hidden = true;
  };

  addEventListener("pagehide", relock);
  relockButton.addEventListener("click", () => {
    relock();
    status.textContent = "다시 열려면 비밀번호를 입력하세요.";
    passwordInput.focus();
  });

  fetch("data/catalog.json", {cache: "no-store"})
    .then((response) => {
      if (!response.ok) throw new Error("catalog request failed");
      return response.json();
    })
    .then((catalog) => {
      artifact = resolveProtectedArtifact(catalog, artifactId);
      title.textContent = artifact.title;
      status.textContent = "비밀번호는 이 브라우저 탭의 복호화에만 사용됩니다.";
      form.hidden = false;
      passwordInput.focus();
    })
    .catch(() => {
      status.textContent = "요청한 비공개 자료를 확인할 수 없습니다.";
    });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!artifact) return;
    relock();
    submitButton.disabled = true;
    status.textContent = "암호화된 PDF를 확인하는 중입니다…";
    let plaintext;
    try {
      const response = await fetch(artifact.href, {cache: "no-store"});
      if (!response.ok) throw new Error("encrypted artifact request failed");
      const serialized = await response.text();
      plaintext = await decryptContainer(serialized, passwordInput.value);
      if (!startsWithPdfMagic(plaintext)) throw new Error("invalid PDF");
      activeUrl = URL.createObjectURL(new Blob([plaintext], {type: "application/pdf"}));
      frame.src = activeUrl;
      frame.hidden = false;
      relockButton.hidden = false;
      status.textContent = "이 탭을 닫거나 새로고침하면 다시 잠깁니다.";
    } catch {
      relock();
      status.textContent = "비밀번호 또는 암호화 파일이 올바르지 않습니다.";
    } finally {
      passwordInput.value = "";
      plaintext?.fill(0);
      submitButton.disabled = false;
    }
  });
}

if (typeof document !== "undefined") {
  start();
}
