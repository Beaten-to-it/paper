import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


class CatalogError(ValueError):
    pass


PAGES_FILE_LIMIT = 50 * 1024 * 1024
RELEASE_PATH_PREFIX = "/Beaten-to-it/paper/releases/download/"


def validate(catalog: dict, public_root: Path) -> tuple[int, int]:
    papers = catalog["papers"]
    for paper in papers:
        for artifact in paper["artifacts"]:
            if artifact["type"] == "source_paper_pdf":
                raise CatalogError("source_paper_pdf is not public")
            if artifact["storage"] == "pages" and artifact["size_bytes"] > PAGES_FILE_LIMIT:
                raise CatalogError("files over 50 MiB must use release storage")
            if artifact["storage"] == "pages":
                root = public_root.resolve()
                path = (root / artifact["href"]).resolve()
                try:
                    path.relative_to(root)
                except ValueError as error:
                    raise CatalogError(f"unsafe pages path: {artifact['href']}") from error
                if not path.is_file():
                    raise CatalogError(f"missing pages file: {artifact['href']}")
                if path.stat().st_size != artifact["size_bytes"]:
                    raise CatalogError(f"size mismatch: {artifact['href']}")
                actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual_hash.lower() != artifact["sha256"].lower():
                    raise CatalogError(f"sha256 mismatch: {artifact['href']}")
            if artifact["storage"] == "release":
                url = urlparse(artifact["href"])
                if (
                    url.scheme != "https"
                    or url.netloc != "github.com"
                    or not url.path.startswith(RELEASE_PATH_PREFIX)
                ):
                    raise CatalogError(f"unsafe release url: {artifact['href']}")
    return len(papers), sum(len(paper["artifacts"]) for paper in papers)


def main() -> int:
    try:
        catalog_path = Path(sys.argv[1])
        public_root = Path(sys.argv[2])
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        paper_count, artifact_count = validate(catalog, public_root)
        print(f"valid catalog: {paper_count} papers, {artifact_count} artifacts")
        return 0
    except (CatalogError, KeyError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
