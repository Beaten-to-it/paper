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
ALLOWED_STATUS = {"complete", "missing", "in_progress", "not_applicable", "withheld"}
PAGES_EXTENSIONS = {
    "analysis": {".md"},
    "infographic": {".jpeg", ".jpg", ".png", ".webp"},
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


def validate_metadata(artifact: dict) -> None:
    storage = artifact["storage"]
    status = artifact["status"]
    if storage not in ALLOWED_STORAGE:
        raise CatalogError(f"unsupported storage: {storage}")
    if status not in ALLOWED_STATUS:
        raise CatalogError(f"unsupported status: {status}")

    if status == "complete":
        if storage not in {"pages", "release"}:
            raise CatalogError("complete artifacts require public storage")
        if not isinstance(artifact["href"], str) or not artifact["href"]:
            raise CatalogError("complete artifacts require href")
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
    root = public_root.resolve()
    declared_pages: set[str] = set()
    for paper in papers:
        for artifact in paper["artifacts"]:
            validate_metadata(artifact)
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
