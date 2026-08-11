import {decryptContainer, parseContainer} from "./protected-crypto.js";

const protectedPathPattern = /^protected\/[a-z0-9][a-z0-9-]*\.enc$/;
const sha256Pattern = /^[a-fA-F0-9]{64}$/;
const maxEncryptedBytes = 50 * 1024 * 1024;
const protectedAccessModes = new Set([
  "official_link_plus_password_encrypted",
  "public_plus_password_encrypted",
]);
const protectedMetadataFields = [
  "href",
  "size_bytes",
  "sha256",
  "container_version",
  "algorithm",
  "kdf",
  "iterations",
];

function validateProtectedMetadata(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("invalid protected artifact metadata");
  }
  const fields = Object.keys(value).sort();
  const expectedFields = [...protectedMetadataFields].sort();
  if (fields.length !== expectedFields.length || fields.some((field, index) => field !== expectedFields[index])) {
    throw new Error("invalid protected artifact metadata");
  }
  if (typeof value.href !== "string" || !protectedPathPattern.test(value.href)) {
    throw new Error("invalid protected artifact path");
  }
  if (!Number.isSafeInteger(value.size_bytes) || value.size_bytes <= 0 || value.size_bytes > maxEncryptedBytes) {
    throw new Error("invalid protected artifact size");
  }
  if (typeof value.sha256 !== "string" || !sha256Pattern.test(value.sha256)) {
    throw new Error("invalid protected artifact hash");
  }
  if (
    value.container_version !== 1
    || value.algorithm !== "AES-256-GCM"
    || value.kdf !== "PBKDF2-HMAC-SHA-256"
    || !Number.isSafeInteger(value.iterations)
    || value.iterations < 600_000
    || value.iterations > 2_000_000
  ) {
    throw new Error("invalid protected encryption metadata");
  }
  return {...value};
}

function bytesToHex(bytes) {
  return [...bytes].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function verifyEncryptedPayload(bytes, declaredMetadata) {
  if (!(bytes instanceof Uint8Array)) {
    throw new Error("encrypted payload must be bytes");
  }
  const expected = validateProtectedMetadata(declaredMetadata);
  if (bytes.length !== expected.size_bytes) {
    throw new Error("encrypted payload size mismatch");
  }
  const digest = new Uint8Array(await globalThis.crypto.subtle.digest("SHA-256", bytes));
  if (bytesToHex(digest) !== expected.sha256.toLowerCase()) {
    throw new Error("encrypted payload integrity mismatch");
  }
  let serialized;
  try {
    serialized = new TextDecoder("utf-8", {fatal: true}).decode(bytes);
  } catch (error) {
    throw new Error("encrypted payload is not UTF-8", {cause: error});
  }
  const container = parseContainer(serialized);
  if (
    container.version !== expected.container_version
    || container.algorithm !== expected.algorithm
    || container.kdf !== expected.kdf
    || container.iterations !== expected.iterations
  ) {
    throw new Error("encrypted payload metadata mismatch");
  }
  return container;
}

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
  const expected = validateProtectedMetadata(artifact.protected);
  return {href: expected.href, title: String(artifact.title || "비공개 PDF"), expected};
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
  let activeRequest = null;
  let unlockVersion = 0;

  const relock = () => {
    unlockVersion += 1;
    activeRequest?.abort();
    activeRequest = null;
    passwordInput.value = "";
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
    const password = passwordInput.value;
    relock();
    const attempt = unlockVersion;
    const request = new AbortController();
    activeRequest = request;
    submitButton.disabled = true;
    status.textContent = "암호화된 PDF를 확인하는 중입니다…";
    let plaintext;
    try {
      const response = await fetch(artifact.href, {cache: "no-store", signal: request.signal});
      if (!response.ok) throw new Error("encrypted artifact request failed");
      const contentLength = Number(response.headers.get("content-length"));
      if (Number.isFinite(contentLength) && contentLength > maxEncryptedBytes) {
        throw new Error("encrypted artifact is too large");
      }
      const encoded = new Uint8Array(await response.arrayBuffer());
      const container = await verifyEncryptedPayload(encoded, artifact.expected);
      plaintext = await decryptContainer(container, password);
      if (attempt !== unlockVersion) return;
      if (!startsWithPdfMagic(plaintext)) throw new Error("invalid PDF");
      activeUrl = URL.createObjectURL(new Blob([plaintext], {type: "application/pdf"}));
      frame.src = activeUrl;
      frame.hidden = false;
      relockButton.hidden = false;
      status.textContent = "이 탭을 닫거나 새로고침하면 다시 잠깁니다.";
    } catch {
      if (attempt !== unlockVersion) return;
      relock();
      status.textContent = "비밀번호 또는 암호화 파일이 올바르지 않습니다.";
    } finally {
      passwordInput.value = "";
      plaintext?.fill(0);
      if (activeRequest === request) activeRequest = null;
      submitButton.disabled = false;
    }
  });
}

if (typeof document !== "undefined") {
  start();
}
