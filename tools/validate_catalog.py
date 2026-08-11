import hashlib
import json
import posixpath
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse


class CatalogError(ValueError):
    pass


PAGES_FILE_LIMIT = 50 * 1024 * 1024
RELEASE_PATH_PREFIX = "/Beaten-to-it/paper/releases/download/"
ALLOWED_STORAGE = {"none", "pages", "release"}
RIGHTS_AWARE_STORAGE = ALLOWED_STORAGE | {"external", "protected"}
ALLOWED_STATUS = {"complete", "missing", "in_progress", "not_applicable", "withheld"}
ALLOWED_ACCESS = {"public", "official_link_plus_password_encrypted", "public_plus_password_encrypted"}
ALLOWED_EXTERNAL_HOSTS = {"dash.harvard.edu", "doi.org", "pubsonline.informs.org"}
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
}
PAGES_EXTENSIONS = {
    "analysis": {".md"},
    "infographic": {".jpeg", ".jpg", ".png", ".webp"},
    "korean_version": {".md"},
    "notebooklm_prompt": {".md"},
    "notebooklm_run": {".md"},
    "research_design": {".md"},
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
    "assets/styles.css",
    "assets/viewer.js",
    "data/catalog.json",
    "favicon.svg",
    "index.html",
    "viewer.html",
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


def validate_release_url(artifact: dict) -> None:
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
    ):
        raise CatalogError("invalid protected encryption metadata")
    if isinstance(metadata["size_bytes"], bool) or not isinstance(metadata["size_bytes"], int) or metadata["size_bytes"] <= 0:
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
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_hash.lower() != expected_hash.lower():
        raise CatalogError(f"protected sha256 mismatch: {href}")
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


def validate_paper_contract(paper: dict) -> None:
    if paper["kind"] != "paper":
        return
    validate_rights(paper)
    artifacts = paper["artifacts"]
    if len(artifacts) != len(PAPER_SLOT_TYPES) or {artifact["type"] for artifact in artifacts} != PAPER_SLOT_TYPES:
        raise CatalogError("paper artifacts must satisfy the nine-slot contract")
    if any(artifact.get("status") != "complete" for artifact in artifacts):
        raise CatalogError("rights-aware paper artifacts must all be complete")
    for artifact in artifacts:
        if artifact.get("access") not in ALLOWED_ACCESS:
            raise CatalogError("invalid artifact access")
        if artifact["access"] == "public" and "protected" in artifact:
            raise CatalogError("public artifacts must not declare protected content")
        if artifact["access"] != "public" and "protected" not in artifact:
            raise CatalogError("password-encrypted access requires protected metadata")
    source = next(artifact for artifact in artifacts if artifact["type"] == "source_paper")
    korean = next(artifact for artifact in artifacts if artifact["type"] == "korean_version")
    if paper["rights"]["redistribution"] == "restricted" and source["storage"] in {"pages", "release"}:
        raise CatalogError("rights do not allow public redistribution")
    if (
        paper["rights"]["translation_publication"] == "restricted"
        and korean.get("translation_kind") == "full_unofficial"
        and korean["storage"] in {"pages", "release"}
    ):
        raise CatalogError("rights do not allow public full translation")


def validate_public_inventory(public_root: Path, declared_pages: set[str]) -> None:
    allowed_files = PUBLIC_SITE_FILES | declared_pages
    for path in public_root.rglob("*"):
        if path.is_symlink():
            raise CatalogError(f"public symlinks are not allowed: {path.relative_to(public_root).as_posix()}")
        if path.is_file():
            relative_path = path.relative_to(public_root).as_posix()
            if relative_path not in allowed_files:
                raise CatalogError(f"undeclared public file: {relative_path}")


def validate(catalog: dict, public_root: Path) -> tuple[int, int]:
    papers = catalog["papers"]
    schema_version = catalog.get("version", 1)
    if isinstance(schema_version, bool) or not isinstance(schema_version, int) or schema_version < 1:
        raise CatalogError("invalid catalog version")
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
                actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual_hash.lower() != artifact["sha256"].lower():
                    raise CatalogError(f"sha256 mismatch: {href}")
                declared_pages.add(href_path.as_posix())
            if artifact["storage"] == "release":
                validate_release_url(artifact)
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
        paper_count, artifact_count = validate(catalog, public_root)
        print(f"valid catalog: {paper_count} papers, {artifact_count} artifacts")
        return 0
    except (CatalogError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
