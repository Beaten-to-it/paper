import base64
import binascii
import hashlib
import json
import posixpath
import struct
import sys
import zlib
from pathlib import Path, PurePosixPath
from urllib.error import URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen


class CatalogError(ValueError):
    pass


PAGES_FILE_LIMIT = 50 * 1024 * 1024
RELEASE_PATH_PREFIX = "/Beaten-to-it/paper/releases/download/"
ALLOWED_STORAGE = {"none", "pages", "release"}
RIGHTS_AWARE_STORAGE = ALLOWED_STORAGE | {"external", "protected"}
ALLOWED_STATUS = {"complete", "missing", "in_progress", "not_applicable", "withheld"}
ALLOWED_ACCESS = {"public", "official_link_plus_password_encrypted", "public_plus_password_encrypted"}
ALLOWED_EXTERNAL_HOSTS = {"dash.harvard.edu", "doi.org", "pubsonline.informs.org"}
ALLOWED_KINDS = {"paper", "research-design"}
RIGHTS_PROFILES = {
    "kemell-2025": {
        "rights": {"license": "CC-BY-4.0", "redistribution": "allowed", "translation_publication": "allowed_with_attribution", "source_url": "https://doi.org/10.1016/j.infsof.2025.107805", "checked_at": "2026-08-11"},
    },
    "neumann-2026": {
        "rights": {"license": "CC-BY-4.0", "redistribution": "allowed", "translation_publication": "allowed_with_attribution", "source_url": "https://doi.org/10.1007/978-3-032-22375-3_18", "checked_at": "2026-08-11"},
    },
    "golgeci-2025": {
        "rights": {"license": "CC-BY-4.0", "redistribution": "allowed", "translation_publication": "allowed_with_attribution", "source_url": "https://doi.org/10.1016/j.hrmr.2024.101075", "checked_at": "2026-08-11"},
    },
    "battilana-casciaro-2012": {
        "rights": {"license": "author-manuscript-policy", "redistribution": "restricted", "translation_publication": "restricted", "source_url": "https://dash.harvard.edu/handle/1/9544459", "checked_at": "2026-08-11"},
        "official_source_url": "https://doi.org/10.5465/amj.2009.0891",
        "protected": {"source_paper": "protected/bc2012-source.enc", "korean_version": "protected/bc2012-korean-full.enc"},
    },
    "battilana-casciaro-2013": {
        "rights": {"license": "all-rights-reserved", "redistribution": "restricted", "translation_publication": "restricted", "source_url": "https://pubsonline.informs.org/authorportal/rights-permissions", "checked_at": "2026-08-11"},
        "official_source_url": "https://doi.org/10.1287/mnsc.1120.1583",
        "protected": {"source_paper": "protected/bc2013-source.enc", "korean_version": "protected/bc2013-korean-full.enc"},
    },
}
ALLOWED_PROTECTED_FILENAMES = {
    "bc2012-source.enc",
    "bc2012-korean-full.enc",
    "bc2013-source.enc",
    "bc2013-korean-full.enc",
}
PAPER_SLOT_TYPES = {
    "source_paper",
    "korean_version",
    "analysis",
    "notebooklm_prompt",
    "notebooklm_run",
    "audio",
    "slides",
    "slide_pdf",
    "infographic",
    "model_contribution",
}
PAGES_EXTENSIONS = {
    "analysis": {".md"},
    "construct_dictionary": {".md"},
    "infographic": {".png"},
    "korean_version": {".md"},
    "model_contribution": {".md"},
    "model_diagram": {".png"},
    "notebooklm_prompt": {".md"},
    "notebooklm_run": {".md"},
    "pilot_protocol": {".md"},
    "proposition_traceability": {".md"},
    "research_design": {".md"},
    "research_model": {".md"},
    "research_synthesis": {".md"},
}
RELEASE_EXTENSIONS = {
    "audio": {".m4a", ".mp3", ".wav"},
    "slide_pdf": {".pdf"},
    "slides": {".pptx"},
    "spreadsheet": {".csv", ".tsv", ".xls", ".xlsx"},
    "source_paper": {".pdf"},
    "korean_version": {".pdf"},
}
PUBLIC_SITE_FILES = {
    ".nojekyll",
    "assets/app.js",
    "assets/protected-crypto.js",
    "assets/protected-viewer.js",
    "assets/styles.css",
    "assets/viewer.js",
    "data/catalog.json",
    "favicon.svg",
    "index.html",
    "protected-viewer.html",
    "viewer.html",
}
RELEASE_V1 = "https://github.com/Beaten-to-it/paper/releases/download/artifacts-2026-08-11-v1/"
RELEASE_V2 = "https://github.com/Beaten-to-it/paper/releases/download/artifacts-2026-08-11-v2/"
RELEASE_V3 = "https://github.com/Beaten-to-it/paper/releases/download/artifacts-2026-08-12-v3/"
EXPECTED_GROUP_IDENTITIES = {
    "kemell-2025": ("paper", 2025, "Still just personal assistants?", "Kemell, Saarikallio, Nguyen-Duc, & Abrahamsson (2025) · Information and Software Technology 186, 107805"),
    "neumann-2026": ("paper", 2026, "Between Policy and Practice", "Neumann et al. (2026) · Between Policy and Practice: GenAI Adoption in Agile Software Development Teams"),
    "golgeci-2025": ("paper", 2025, "Confronting and alleviating AI resistance in the workplace", "Golgeci, Ritala, Arslan, McKenna, & Ali (2025) · Human Resource Management Review 35, 101075"),
    "battilana-casciaro-2012": ("paper", 2012, "Change Agents, Networks, and Institutions", "Battilana & Casciaro (2012) · Academy of Management Journal 55(2)"),
    "battilana-casciaro-2013": ("paper", 2013, "Overcoming Resistance to Organizational Change", "Battilana & Casciaro (2013) · Management Science 59(4), 819-836"),
    "research-design": ("research-design", 2026, "연구 종합과 설계", "Doctoral research design · updated 2026-08-12"),
}
EXPECTED_ARTIFACT_BINDINGS = {
    "kemell-2025": {
        "kemell-2025-source": ("source_paper", "release", RELEASE_V2 + "Kemell-et-al-2025-Still-just-personal-assistants.pdf"),
        "kemell-2025-korean": ("korean_version", "release", RELEASE_V2 + "Kemell-2025-Korean-unofficial-translation.pdf"),
        "kemell-analysis": ("analysis", "pages", "downloads/kemell-2025/analysis.md"),
        "kemell-prompt": ("notebooklm_prompt", "pages", "downloads/kemell-2025/notebooklm-prompts.md"),
        "kemell-run": ("notebooklm_run", "pages", "downloads/kemell-2025/notebooklm-run.md"),
        "kemell-audio": ("audio", "release", RELEASE_V1 + "Kemell-2025-Korean-deep-dive.m4a"),
        "kemell-slides": ("slides", "release", RELEASE_V1 + "Kemell-2025-seminar-deck.pptx"),
        "kemell-slide-pdf": ("slide_pdf", "release", RELEASE_V1 + "Kemell-2025-seminar-deck.pdf"),
        "kemell-infographic": ("infographic", "pages", "downloads/kemell-2025/infographic.png"),
        "kemell-2025-model-contribution": ("model_contribution", "pages", "downloads/kemell-2025/model-v0.3-contribution.md"),
    },
    "neumann-2026": {
        "neumann-2026-source": ("source_paper", "release", RELEASE_V2 + "Neumann-et-al-2026-Between-policy-and-practice.pdf"),
        "neumann-2026-korean": ("korean_version", "release", RELEASE_V2 + "Neumann-2026-Korean-unofficial-translation.pdf"),
        "neumann-analysis": ("analysis", "pages", "downloads/neumann-2026/analysis.md"),
        "neumann-prompt": ("notebooklm_prompt", "pages", "downloads/neumann-2026/notebooklm-prompts.md"),
        "neumann-run": ("notebooklm_run", "pages", "downloads/neumann-2026/notebooklm-run.md"),
        "neumann-audio": ("audio", "release", RELEASE_V1 + "Neumann-2026-Korean-deep-dive.m4a"),
        "neumann-slides": ("slides", "release", RELEASE_V1 + "Neumann-2026-NotebookLM-seminar-deck.pptx"),
        "neumann-slide-pdf": ("slide_pdf", "release", RELEASE_V1 + "Neumann-2026-NotebookLM-seminar-deck.pdf"),
        "neumann-infographic": ("infographic", "pages", "downloads/neumann-2026/infographic.png"),
        "neumann-2026-model-contribution": ("model_contribution", "pages", "downloads/neumann-2026/model-v0.3-contribution.md"),
    },
    "golgeci-2025": {
        "golgeci-2025-source": ("source_paper", "release", RELEASE_V2 + "Golgeci-et-al-2025-AI-resistance-process-framework.pdf"),
        "golgeci-2025-korean": ("korean_version", "release", RELEASE_V2 + "Golgeci-2025-Korean-unofficial-translation.pdf"),
        "golgeci-analysis": ("analysis", "pages", "downloads/golgeci-2025/analysis.md"),
        "golgeci-prompt": ("notebooklm_prompt", "pages", "downloads/golgeci-2025/notebooklm-prompts.md"),
        "golgeci-run": ("notebooklm_run", "pages", "downloads/golgeci-2025/notebooklm-run.md"),
        "golgeci-audio": ("audio", "release", RELEASE_V2 + "Golgeci-2025-NotebookLM-audio-overview.m4a"),
        "golgeci-slides": ("slides", "release", RELEASE_V2 + "Golgeci-2025-NotebookLM-seminar-deck.pptx"),
        "golgeci-slide-pdf": ("slide_pdf", "release", RELEASE_V2 + "Golgeci-2025-NotebookLM-seminar-deck.pdf"),
        "golgeci-infographic": ("infographic", "pages", "downloads/golgeci-2025/infographic.png"),
        "golgeci-2025-model-contribution": ("model_contribution", "pages", "downloads/golgeci-2025/model-v0.3-contribution.md"),
    },
    "battilana-casciaro-2012": {
        "bc2012-source": ("source_paper", "external", "https://doi.org/10.5465/amj.2009.0891"),
        "bc2012-korean": ("korean_version", "pages", "downloads/battilana-casciaro-2012/korean-study-guide.md"),
        "bc2012-analysis": ("analysis", "pages", "downloads/battilana-casciaro-2012/analysis.md"),
        "bc2012-prompt": ("notebooklm_prompt", "pages", "downloads/battilana-casciaro-2012/notebooklm-prompts.md"),
        "bc2012-run": ("notebooklm_run", "pages", "downloads/battilana-casciaro-2012/notebooklm-run.md"),
        "bc2012-audio": ("audio", "release", RELEASE_V2 + "Battilana-Casciaro-2012-NotebookLM-audio-overview.m4a"),
        "bc2012-slides": ("slides", "release", RELEASE_V2 + "Battilana-Casciaro-2012-NotebookLM-seminar-deck.pptx"),
        "bc2012-slide-pdf": ("slide_pdf", "release", RELEASE_V2 + "Battilana-Casciaro-2012-NotebookLM-seminar-deck.pdf"),
        "bc2012-infographic": ("infographic", "pages", "downloads/battilana-casciaro-2012/infographic.png"),
        "battilana-casciaro-2012-model-contribution": ("model_contribution", "pages", "downloads/battilana-casciaro-2012/model-v0.3-contribution.md"),
    },
    "battilana-casciaro-2013": {
        "bc2013-source": ("source_paper", "external", "https://doi.org/10.1287/mnsc.1120.1583"),
        "bc2013-korean": ("korean_version", "pages", "downloads/battilana-casciaro-2013/korean-study-guide.md"),
        "bc2013-analysis": ("analysis", "pages", "downloads/battilana-casciaro-2013/analysis.md"),
        "bc2013-prompt": ("notebooklm_prompt", "pages", "downloads/battilana-casciaro-2013/notebooklm-prompts.md"),
        "bc2013-run": ("notebooklm_run", "pages", "downloads/battilana-casciaro-2013/notebooklm-run.md"),
        "bc2013-audio": ("audio", "release", RELEASE_V2 + "Battilana-Casciaro-2013-NotebookLM-audio-overview.m4a"),
        "bc2013-slides": ("slides", "release", RELEASE_V2 + "Battilana-Casciaro-2013-NotebookLM-seminar-deck.pptx"),
        "bc2013-slide-pdf": ("slide_pdf", "release", RELEASE_V2 + "Battilana-Casciaro-2013-NotebookLM-seminar-deck.pdf"),
        "bc2013-infographic": ("infographic", "pages", "downloads/battilana-casciaro-2013/infographic.png"),
        "battilana-casciaro-2013-model-contribution": ("model_contribution", "pages", "downloads/battilana-casciaro-2013/model-v0.3-contribution.md"),
    },
    "research-design": {
        "four-paper-bridge": ("research_synthesis", "pages", "downloads/research-design/four-paper-theory-bridge.md"),
        "literature-map": ("research_design", "pages", "downloads/research-design/literature-map.md"),
        "core-matrix": ("research_design", "pages", "downloads/research-design/core-paper-matrix-research-model-interview-guide.md"),
        "literature-map-xlsx": ("spreadsheet", "release", RELEASE_V1 + "AI-transformation-change-agent-literature-map-2026-08-10.xlsx"),
        "research-model-v03": ("research_model", "pages", "downloads/research-design/research-model-v0.3.md"),
        "construct-dictionary-v03": ("construct_dictionary", "pages", "downloads/research-design/construct-dictionary-v0.3.md"),
        "proposition-traceability-v03": ("proposition_traceability", "pages", "downloads/research-design/proposition-traceability-v0.3.md"),
        "pilot-protocol-v03": ("pilot_protocol", "pages", "downloads/research-design/pilot-protocol-and-codingbook-v0.3.md"),
        "research-model-v03-diagram": ("model_diagram", "pages", "downloads/research-design/research-model-v0.3.png"),
        "research-model-v03-workbook": ("spreadsheet", "release", RELEASE_V3 + "SW-AI-change-agent-research-model-v0.3-workbook.xlsx"),
        "research-model-v03-slides": ("slides", "release", RELEASE_V3 + "SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx"),
        "research-model-v03-slide-pdf": ("slide_pdf", "release", RELEASE_V3 + "SW-AI-change-agent-research-model-v0.3-advisor-deck.pdf"),
    },
}


def validate_metadata(artifact: dict, schema_version: int) -> None:
    storage = artifact["storage"]
    status = artifact["status"]
    allowed_storage = RIGHTS_AWARE_STORAGE if schema_version >= 2 else ALLOWED_STORAGE
    if storage not in allowed_storage:
        raise CatalogError(f"unsupported storage: {storage}")
    if status not in ALLOWED_STATUS:
        raise CatalogError(f"unsupported status: {status}")

    if status == "complete":
        if storage not in {"pages", "release", "external"}:
            raise CatalogError("complete artifacts require public storage")
        if not isinstance(artifact["href"], str) or not artifact["href"]:
            raise CatalogError("complete artifacts require href")
        if storage == "external":
            if artifact["size_bytes"] != 0 or artifact["sha256"]:
                raise CatalogError("external artifacts must not claim local size or hash")
        else:
            if isinstance(artifact["size_bytes"], bool) or not isinstance(artifact["size_bytes"], int) or artifact["size_bytes"] <= 0:
                raise CatalogError("complete artifacts require a positive integer size_bytes")
            sha256 = artifact["sha256"]
            if not isinstance(sha256, str) or len(sha256) != 64 or any(character not in "0123456789abcdefABCDEF" for character in sha256):
                raise CatalogError("complete artifacts require a hexadecimal sha256")
    elif storage != "none" or artifact["href"] or artifact["size_bytes"] != 0 or artifact["sha256"]:
        raise CatalogError("non-complete artifacts must not expose public files")


def validate_type_and_extension(artifact: dict, storage: str, suffix: str) -> None:
    allowed = PAGES_EXTENSIONS if storage == "pages" else RELEASE_EXTENSIONS
    if artifact["type"] not in allowed or suffix.lower() not in allowed[artifact["type"]]:
        raise CatalogError(f"invalid {storage} artifact type or extension: {artifact['href']}")


def validate_release_url(artifact: dict, release_assets: dict[str, dict] | None = None) -> None:
    href = artifact["href"]
    url = urlparse(href)
    decoded_path = unquote(url.path)
    canonical_path = posixpath.normpath(decoded_path)
    if (
        url.scheme != "https"
        or url.netloc != "github.com"
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
        or "\\" in decoded_path
        or decoded_path != canonical_path
        or not decoded_path.startswith(RELEASE_PATH_PREFIX)
    ):
        raise CatalogError(f"unsafe release url: {href}")

    release_parts = PurePosixPath(decoded_path[len(RELEASE_PATH_PREFIX):]).parts
    if len(release_parts) != 2 or any(part in {"", ".", ".."} for part in release_parts):
        raise CatalogError(f"unsafe release url: {href}")
    validate_type_and_extension(artifact, "release", PurePosixPath(decoded_path).suffix)
    if release_assets is not None:
        published = release_assets.get(href)
        if (
            not isinstance(published, dict)
            or published.get("size_bytes") != artifact["size_bytes"]
            or str(published.get("sha256", "")).lower() != artifact["sha256"].lower()
        ):
            raise CatalogError(f"release asset metadata mismatch: {href}")


def fetch_release_asset_index(catalog: dict) -> dict[str, dict]:
    tags: set[str] = set()
    for paper in catalog["papers"]:
        for artifact in paper["artifacts"]:
            if artifact.get("status") == "complete" and artifact.get("storage") == "release":
                path = unquote(urlparse(artifact["href"]).path)
                relative = path[len(RELEASE_PATH_PREFIX):]
                parts = PurePosixPath(relative).parts
                if len(parts) == 2:
                    tags.add(parts[0])
    assets: dict[str, dict] = {}
    for tag in tags:
        api_url = f"https://api.github.com/repos/Beaten-to-it/paper/releases/tags/{quote(tag, safe='')}"
        request = Request(api_url, headers={"Accept": "application/vnd.github+json", "User-Agent": "paper-catalog-validator"})
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        for item in payload.get("assets", []):
            digest = item.get("digest")
            if not isinstance(digest, str) or not digest.startswith("sha256:"):
                continue
            assets[item["browser_download_url"]] = {
                "size_bytes": item["size"],
                "sha256": digest.removeprefix("sha256:"),
            }
    return assets


def validate_external_url(artifact: dict) -> None:
    href = artifact["href"]
    url = urlparse(href)
    decoded_path = unquote(url.path)
    if (
        url.scheme != "https"
        or url.hostname not in ALLOWED_EXTERNAL_HOSTS
        or url.username is not None
        or url.password is not None
        or url.fragment
        or "\\" in decoded_path
        or ".." in PurePosixPath(decoded_path).parts
        or artifact["type"] != "source_paper"
    ):
        raise CatalogError(f"unsafe external url: {href}")


def validate_protected(artifact: dict, root: Path, declared_pages: set[str]) -> None:
    metadata = artifact["protected"]
    required = {"href", "size_bytes", "sha256", "container_version", "algorithm", "kdf", "iterations"}
    if set(metadata) != required:
        raise CatalogError("invalid protected metadata")
    href = metadata["href"]
    href_path = PurePosixPath(href)
    if (
        not isinstance(href, str)
        or "\\" in href
        or href_path.is_absolute()
        or len(href_path.parts) != 2
        or href_path.parts[0] != "protected"
        or ".." in href_path.parts
        or href_path.name not in ALLOWED_PROTECTED_FILENAMES
    ):
        raise CatalogError(f"unsafe protected path: {href}")
    if (
        metadata["container_version"] != 1
        or metadata["algorithm"] != "AES-256-GCM"
        or metadata["kdf"] != "PBKDF2-HMAC-SHA-256"
        or isinstance(metadata["iterations"], bool)
        or not isinstance(metadata["iterations"], int)
        or metadata["iterations"] < 600_000
        or metadata["iterations"] > 2_000_000
    ):
        raise CatalogError("invalid protected encryption metadata")
    if (
        isinstance(metadata["size_bytes"], bool)
        or not isinstance(metadata["size_bytes"], int)
        or metadata["size_bytes"] <= 0
        or metadata["size_bytes"] > PAGES_FILE_LIMIT
    ):
        raise CatalogError("protected artifacts require a positive integer size_bytes")
    expected_hash = metadata["sha256"]
    if not isinstance(expected_hash, str) or len(expected_hash) != 64 or any(character not in "0123456789abcdefABCDEF" for character in expected_hash):
        raise CatalogError("protected artifacts require a hexadecimal sha256")
    path = (root / Path(*href_path.parts)).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise CatalogError(f"unsafe protected path: {href}") from error
    if not path.is_file():
        raise CatalogError(f"missing protected file: {href}")
    if path.stat().st_size != metadata["size_bytes"]:
        raise CatalogError(f"protected size mismatch: {href}")
    payload = path.read_bytes()
    actual_hash = hashlib.sha256(payload).hexdigest()
    if actual_hash.lower() != expected_hash.lower():
        raise CatalogError(f"protected sha256 mismatch: {href}")
    try:
        container = json.loads(payload.decode("utf-8"))
        if set(container) != {"version", "algorithm", "kdf", "iterations", "salt", "iv", "ciphertext"}:
            raise ValueError("unexpected container fields")
        if (
            container["version"] != metadata["container_version"]
            or container["algorithm"] != metadata["algorithm"]
            or container["kdf"] != metadata["kdf"]
            or container["iterations"] != metadata["iterations"]
        ):
            raise ValueError("container metadata mismatch")
        salt = base64.b64decode(container["salt"], validate=True)
        iv = base64.b64decode(container["iv"], validate=True)
        ciphertext = base64.b64decode(container["ciphertext"], validate=True)
        if len(salt) != 16 or len(iv) != 12 or len(ciphertext) < 17:
            raise ValueError("invalid encrypted payload lengths")
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError, binascii.Error) as error:
        raise CatalogError(f"invalid encrypted container: {href}") from error
    declared_pages.add(href_path.as_posix())


def validate_rights(paper: dict) -> None:
    rights = paper["rights"]
    required = {"license", "redistribution", "translation_publication", "source_url", "checked_at"}
    if set(rights) != required:
        raise CatalogError("invalid rights metadata")
    if rights["redistribution"] not in {"allowed", "restricted"}:
        raise CatalogError("invalid redistribution right")
    if rights["translation_publication"] not in {"allowed_with_attribution", "restricted"}:
        raise CatalogError("invalid translation publication right")
    source_url = urlparse(rights["source_url"])
    if source_url.scheme != "https" or not source_url.hostname:
        raise CatalogError("invalid rights source url")
    profile = RIGHTS_PROFILES.get(paper["slug"])
    if profile is None or rights != profile["rights"]:
        raise CatalogError("rights metadata does not match approved paper profile")


def validate_paper_contract(paper: dict) -> None:
    kind = paper["kind"]
    if kind not in ALLOWED_KINDS:
        raise CatalogError(f"unsupported paper kind: {kind}")
    if kind != "paper":
        return
    validate_rights(paper)
    artifacts = paper["artifacts"]
    if len(artifacts) != len(PAPER_SLOT_TYPES) or {artifact["type"] for artifact in artifacts} != PAPER_SLOT_TYPES:
        raise CatalogError("paper artifacts must satisfy the ten-slot contract")
    if any(artifact.get("status") != "complete" for artifact in artifacts):
        raise CatalogError("rights-aware paper artifacts must all be complete")
    for artifact in artifacts:
        if artifact.get("access") not in ALLOWED_ACCESS:
            raise CatalogError("invalid artifact access")
        if artifact["access"] == "public" and "protected" in artifact:
            raise CatalogError("public artifacts must not declare protected content")
        if artifact["access"] != "public" and "protected" not in artifact:
            raise CatalogError("password-encrypted access requires protected metadata")
        if artifact["type"] not in {"source_paper", "korean_version"} and (
            artifact["access"] != "public" or "protected" in artifact
        ):
            raise CatalogError("only source and Korean version may declare protected access")
    source = next(artifact for artifact in artifacts if artifact["type"] == "source_paper")
    korean = next(artifact for artifact in artifacts if artifact["type"] == "korean_version")
    profile = RIGHTS_PROFILES[paper["slug"]]
    if paper["rights"]["redistribution"] == "restricted":
        if not (
            source["storage"] == "external"
            and source["access"] == "official_link_plus_password_encrypted"
            and "protected" in source
        ):
            raise CatalogError("restricted source requires official link and encrypted companion")
        if source["href"] != profile["official_source_url"]:
            raise CatalogError("official source does not match approved paper profile")
    elif source["storage"] != "release" or source["access"] != "public" or "protected" in source:
        raise CatalogError("redistributable source must use public release storage")
    if paper["rights"]["translation_publication"] == "restricted":
        if not (
            korean["storage"] == "pages"
            and korean["access"] == "public_plus_password_encrypted"
            and korean.get("translation_kind") == "detailed_study_guide"
            and "protected" in korean
        ):
            raise CatalogError("restricted translation requires public study guide and encrypted companion")
    elif not (
        korean["storage"] == "release"
        and korean["access"] == "public"
        and korean.get("translation_kind") == "full_unofficial"
        and "protected" not in korean
    ):
        raise CatalogError("public translation must use attributed full unofficial release")
    for artifact in (source, korean):
        if "protected" in artifact and artifact["protected"]["href"] != profile["protected"][artifact["type"]]:
            raise CatalogError("protected companion does not match paper slot")


def validate_catalog_identity(catalog: dict) -> None:
    papers = catalog["papers"]
    slugs = [paper.get("slug") for paper in papers]
    if len(slugs) != len(EXPECTED_GROUP_IDENTITIES) or set(slugs) != set(EXPECTED_GROUP_IDENTITIES):
        raise CatalogError("canonical catalog identity mismatch: expected six unique groups")

    global_artifact_ids: set[str] = set()
    for paper in papers:
        slug = paper["slug"]
        expected_identity = EXPECTED_GROUP_IDENTITIES[slug]
        actual_identity = (paper.get("kind"), paper.get("year"), paper.get("title"), paper.get("citation"))
        if actual_identity != expected_identity:
            raise CatalogError(f"canonical catalog identity mismatch: {slug}")

        artifacts = paper.get("artifacts")
        if not isinstance(artifacts, list):
            raise CatalogError(f"canonical catalog identity mismatch: {slug} artifacts")
        artifact_ids = [artifact.get("id") for artifact in artifacts]
        expected_bindings = EXPECTED_ARTIFACT_BINDINGS[slug]
        if (
            len(artifact_ids) != len(expected_bindings)
            or set(artifact_ids) != set(expected_bindings)
            or len(set(artifact_ids)) != len(artifact_ids)
        ):
            raise CatalogError(f"canonical catalog identity mismatch: {slug} artifact ids")
        for artifact in artifacts:
            artifact_id = artifact["id"]
            if artifact_id in global_artifact_ids:
                raise CatalogError(f"canonical catalog identity mismatch: duplicate artifact id {artifact_id}")
            global_artifact_ids.add(artifact_id)
            actual_binding = (artifact.get("type"), artifact.get("storage"), artifact.get("href"))
            if actual_binding != expected_bindings[artifact_id] or artifact.get("status") != "complete":
                raise CatalogError(f"canonical catalog identity mismatch: {artifact_id}")

    if len(global_artifact_ids) != 62:
        raise CatalogError("canonical catalog identity mismatch: expected 62 unique artifacts")


def is_valid_png(payload: bytes) -> bool:
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    offset = 8
    chunk_index = 0
    width = height = bit_depth = color_type = None
    idat_parts: list[bytes] = []
    saw_iend = False
    while offset + 12 <= len(payload):
        length = struct.unpack(">I", payload[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(payload):
            return False
        chunk_type = payload[offset + 4:offset + 8]
        chunk_data = payload[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack(">I", payload[offset + 8 + length:end])[0]
        if zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF != expected_crc:
            return False
        if chunk_index == 0:
            if chunk_type != b"IHDR" or length != 13:
                return False
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", chunk_data)
            if width <= 0 or height <= 0 or compression != 0 or filter_method != 0 or interlace != 0:
                return False
            valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
            if color_type not in valid_depths or bit_depth not in valid_depths[color_type]:
                return False
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            if length != 0 or end != len(payload):
                return False
            saw_iend = True
            break
        offset = end
        chunk_index += 1
    if not saw_iend or not idat_parts or None in {width, height, bit_depth, color_type}:
        return False
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    row_bytes = (width * channels * bit_depth + 7) // 8
    expected_size = height * (row_bytes + 1)
    if expected_size <= 0 or expected_size > 200 * 1024 * 1024:
        return False
    try:
        decompressor = zlib.decompressobj()
        decoded = decompressor.decompress(b"".join(idat_parts), expected_size + 1)
        decoded += decompressor.flush()
    except zlib.error:
        return False
    if len(decoded) != expected_size or not decompressor.eof or decompressor.unused_data:
        return False
    return all(decoded[row_start] <= 4 for row_start in range(0, expected_size, row_bytes + 1))


def looks_like_pdf(payload: bytes) -> bool:
    return payload.find(b"%PDF-") >= 0


def validate_page_content(artifact: dict, payload: bytes) -> None:
    if looks_like_pdf(payload):
        raise CatalogError(f"page content does not match declared type: {artifact['href']}")
    if artifact["type"] in {"infographic", "model_diagram"} and not is_valid_png(payload):
        raise CatalogError(f"page content does not match declared type: {artifact['href']}")
    if artifact["type"] not in {"infographic", "model_diagram"}:
        try:
            payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise CatalogError(f"page content does not match declared type: {artifact['href']}") from error


def validate_public_inventory(public_root: Path, declared_pages: set[str]) -> None:
    allowed_files = PUBLIC_SITE_FILES | declared_pages
    for path in public_root.rglob("*"):
        if path.is_symlink():
            raise CatalogError(f"public symlinks are not allowed: {path.relative_to(public_root).as_posix()}")
        if path.is_file():
            relative_path = path.relative_to(public_root).as_posix()
            if relative_path not in allowed_files:
                raise CatalogError(f"undeclared public file: {relative_path}")


def validate(
    catalog: dict,
    public_root: Path,
    release_assets: dict[str, dict] | None = None,
    enforce_identity: bool = True,
) -> tuple[int, int]:
    papers = catalog["papers"]
    schema_version = catalog.get("version", 1)
    if isinstance(schema_version, bool) or not isinstance(schema_version, int) or schema_version < 1:
        raise CatalogError("invalid catalog version")
    if enforce_identity and schema_version != 3:
        raise CatalogError("canonical catalog identity mismatch: expected version 3")
    if schema_version >= 2 and release_assets is None and any(
        artifact.get("status") == "complete" and artifact.get("storage") == "release"
        for paper in papers
        for artifact in paper["artifacts"]
    ):
        raise CatalogError("release asset index is required for rights-aware catalogs")
    if enforce_identity:
        validate_catalog_identity(catalog)
    root = public_root.resolve()
    declared_pages: set[str] = set()
    for paper in papers:
        if schema_version >= 2:
            validate_paper_contract(paper)
        for artifact in paper["artifacts"]:
            validate_metadata(artifact, schema_version)
            if artifact["type"] == "source_paper_pdf":
                raise CatalogError("source_paper_pdf is not public")
            if artifact["status"] != "complete":
                continue
            if artifact["storage"] == "pages" and artifact["size_bytes"] > PAGES_FILE_LIMIT:
                raise CatalogError("files over 50 MiB must use release storage")
            if artifact["storage"] == "pages":
                href = artifact["href"]
                href_path = PurePosixPath(href)
                if "\\" in href or href_path.is_absolute() or not href_path.parts or href_path.parts[0] != "downloads" or ".." in href_path.parts:
                    raise CatalogError(f"unsafe pages path: {href}")
                validate_type_and_extension(artifact, "pages", href_path.suffix)
                path = (root / Path(*href_path.parts)).resolve()
                try:
                    path.relative_to(root)
                except ValueError as error:
                    raise CatalogError(f"unsafe pages path: {href}") from error
                if not path.is_file():
                    raise CatalogError(f"missing pages file: {href}")
                if path.stat().st_size != artifact["size_bytes"]:
                    raise CatalogError(f"size mismatch: {href}")
                payload = path.read_bytes()
                validate_page_content(artifact, payload)
                actual_hash = hashlib.sha256(payload).hexdigest()
                if actual_hash.lower() != artifact["sha256"].lower():
                    raise CatalogError(f"sha256 mismatch: {href}")
                declared_pages.add(href_path.as_posix())
            if artifact["storage"] == "release":
                validate_release_url(artifact, release_assets if schema_version >= 2 else None)
            if artifact["storage"] == "external":
                validate_external_url(artifact)
            if schema_version >= 2 and "protected" in artifact:
                validate_protected(artifact, root, declared_pages)
    validate_public_inventory(root, declared_pages)
    return len(papers), sum(len(paper["artifacts"]) for paper in papers)


def main() -> int:
    try:
        catalog_path = Path(sys.argv[1])
        public_root = Path(sys.argv[2])
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        release_assets = fetch_release_asset_index(catalog) if catalog.get("version", 1) >= 2 else None
        paper_count, artifact_count = validate(catalog, public_root, release_assets)
        print(f"valid catalog: {paper_count} papers, {artifact_count} artifacts")
        return 0
    except (CatalogError, KeyError, TypeError, AttributeError, json.JSONDecodeError, URLError, TimeoutError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
