const escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

function inline(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function cells(line) {
  return line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
}

function renderMarkdown(source) {
  const lines = source.replaceAll("\r\n", "\n").split("\n");
  const html = [];
  let inCode = false;
  let code = [];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line.startsWith("```")) {
      if (inCode) {
        html.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
        code = [];
      }
      inCode = !inCode;
      continue;
    }
    if (inCode) {
      code.push(line);
      continue;
    }

    const next = lines[index + 1] || "";
    if (line.includes("|") && /^\s*\|?\s*:?-{3,}/.test(next)) {
      const head = cells(line);
      const rows = [];
      index += 2;
      while (index < lines.length && lines[index].includes("|")) {
        rows.push(cells(lines[index]));
        index += 1;
      }
      index -= 1;
      html.push(`<div class="table-scroll"><table><thead><tr>${head.map((item) => `<th>${inline(item)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((item) => `<td>${inline(item)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      html.push(`<h${level}>${inline(heading[2])}</h${level}>`);
    } else if (/^[-*]\s+/.test(line)) {
      html.push(`<p class="md-list-item">• ${inline(line.replace(/^[-*]\s+/, ""))}</p>`);
    } else if (/^\d+\.\s+/.test(line)) {
      html.push(`<p class="md-list-item">${inline(line)}</p>`);
    } else if (line.startsWith("> ")) {
      html.push(`<blockquote>${inline(line.slice(2))}</blockquote>`);
    } else if (line.trim()) {
      html.push(`<p>${inline(line)}</p>`);
    }
  }
  if (inCode) html.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
  return html.join("\n");
}

async function start() {
  const file = new URLSearchParams(location.search).get("file") || "";
  if (!file.startsWith("downloads/") || !file.endsWith(".md") || file.includes("..")) {
    throw new Error("허용되지 않은 문서 경로입니다.");
  }
  const response = await fetch(file);
  if (!response.ok) throw new Error(`문서 요청 실패 (${response.status})`);
  const source = await response.text();
  const documentNode = document.querySelector("#viewer-document");
  documentNode.innerHTML = renderMarkdown(source);
  documentNode.hidden = false;
  document.querySelector("#viewer-status").hidden = true;
  document.title = `${file.split("/").at(-2)} | Paper Lab`;
}

start().catch((error) => {
  document.querySelector("#viewer-status").textContent = error.message;
});
