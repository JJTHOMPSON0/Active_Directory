#!/usr/bin/env python3

from pathlib import Path
from urllib.parse import unquote
import argparse
import re
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parent
DOCS_DIR = REPO_ROOT / "active_directory"
SOURCE_ZMEDIA = Path("/home/mew2/Documents/Obsidian-Vault/ZMEDIA")
REPO_ZMEDIA = REPO_ROOT / "ZMEDIA"
BACKUP_ZMEDIA = REPO_ROOT.parent / "Active_Directory-ZMEDIA-unused-backup"

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tif", ".tiff"
}

MD_IMAGE_RE = re.compile(r'!\[[^\]]*\]\(([^)]*)\)')
WIKI_IMAGE_RE = re.compile(r'!\[\[([^\]]+)\]\]')


def clean_ref(raw: str) -> str:
    """Decode a Markdown/Obsidian image target into a useful path/name."""
    raw = raw.strip().strip("<>")
    raw = raw.split("?", 1)[0].split("#", 1)[0]
    return unquote(raw)


def extract_refs(md_file: Path):
    """Yield referenced ZMEDIA paths/names from one Markdown file."""
    text = md_file.read_text(encoding="utf-8", errors="ignore")

    # Standard Markdown images: ![alt](path/to/ZMEDIA/file.png)
    for match in MD_IMAGE_RE.finditer(text):
        target = clean_ref(match.group(1))

        # Remove optional Markdown title after the destination.
        # This is only used when the target contains ZMEDIA.
        if "ZMEDIA/" in target:
            target = target.split("ZMEDIA/", 1)[1].strip()
            if target:
                yield target

    # Obsidian image embeds: ![[file.png]] or ![[path/file.png|300]]
    for match in WIKI_IMAGE_RE.finditer(text):
        target = clean_ref(match.group(1))
        target = target.split("|", 1)[0].strip()

        if "ZMEDIA/" in target:
            target = target.split("ZMEDIA/", 1)[1].strip()

        if target:
            yield target


def collect_references():
    """
    Collect references from every Markdown file.

    For wiki embeds without ZMEDIA/ (e.g. ![[Pasted image.png]]),
    the basename is used. This makes the cleanup safer for Obsidian-style
    references as well as the existing GitHub-style references.
    """
    refs = set()
    md_count = 0

    if not DOCS_DIR.is_dir():
        print(f"ERROR: Markdown directory not found: {DOCS_DIR}")
        sys.exit(1)

    for md_file in DOCS_DIR.rglob("*.md"):
        md_count += 1
        text = md_file.read_text(encoding="utf-8", errors="ignore")

        for match in MD_IMAGE_RE.finditer(text):
            target = clean_ref(match.group(1))
            if "ZMEDIA/" in target:
                refs.add(target.split("ZMEDIA/", 1)[1].strip())

        for match in WIKI_IMAGE_RE.finditer(text):
            target = clean_ref(match.group(1))
            target = target.split("|", 1)[0].strip()
            if "ZMEDIA/" in target:
                target = target.split("ZMEDIA/", 1)[1].strip()
            elif Path(target).suffix.lower() in IMAGE_EXTENSIONS:
                # Obsidian commonly stores a bare filename.
                refs.add(Path(target).name)
                continue

            if target:
                refs.add(target)

    return refs, md_count


def index_files(root: Path):
    by_rel = {}
    by_name = {}

    if not root.is_dir():
        return by_rel, by_name

    for p in root.rglob("*"):
        if not p.is_file():
            continue

        rel = str(p.relative_to(root))
        by_rel[rel] = p
        by_name.setdefault(p.name, []).append(p)

    return by_rel, by_name


def resolve_source(ref: str, source_rel, source_by_name):
    """Resolve a reference to one source file."""
    ref = str(Path(ref))

    if ref in source_rel:
        return source_rel[ref], None

    # Most Obsidian ZMEDIA folders are flat; basename fallback handles
    # references that contain relative path differences.
    candidates = source_by_name.get(Path(ref).name, [])
    if len(candidates) == 1:
        return candidates[0], None
    if len(candidates) > 1:
        return None, f"ambiguous source filename: {Path(ref).name}"
    return None, "not found in source ZMEDIA"


def sync():
    refs, md_count = collect_references()
    source_rel, source_by_name = index_files(SOURCE_ZMEDIA)

    REPO_ZMEDIA.mkdir(parents=True, exist_ok=True)

    copied = []
    already = []
    missing = []
    ambiguous = []

    for ref in sorted(refs):
        source, error = resolve_source(ref, source_rel, source_by_name)

        if source is None:
            if error and error.startswith("ambiguous"):
                ambiguous.append((ref, error))
            else:
                missing.append(ref)
            continue

        # Preserve the reference's relative path in the repo when possible.
        destination = REPO_ZMEDIA / ref
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists() and destination.stat().st_size == source.stat().st_size:
            already.append(ref)
            continue

        shutil.copy2(source, destination)
        copied.append(ref)

    print(f"Repository : {REPO_ROOT}")
    print(f"Source     : {SOURCE_ZMEDIA}")
    print(f"Destination: {REPO_ZMEDIA}")
    print()
    print(f"Markdown files scanned : {md_count}")
    print(f"Unique images referenced: {len(refs)}")
    print()
    print("SYNC RESULT")
    print("===========")
    print(f"Copied          : {len(copied)}")
    print(f"Already present : {len(already)}")
    print(f"Missing         : {len(missing)}")
    print(f"Ambiguous       : {len(ambiguous)}")
    print()

    if missing:
        print("MISSING FROM OBSIDIAN ZMEDIA:")
        for x in missing:
            print(f"  ! {x}")
        print()

    if ambiguous:
        print("AMBIGUOUS SOURCE FILES:")
        for x, err in ambiguous:
            print(f"  ! {x} ({err})")
        print()

    if missing or ambiguous:
        return 2

    print("Sync completed successfully.")
    return 0


def cleanup(apply=False):
    """
    Find repo ZMEDIA files that aren't referenced.

    Without --apply: dry-run only.
    With --apply: move unused files OUTSIDE the Git repo to BACKUP_ZMEDIA.
    """
    refs, md_count = collect_references()
    repo_rel, _ = index_files(REPO_ZMEDIA)

    # References can be exact relative paths or bare filenames.
    used = set()
    used_names = set()

    for ref in refs:
        used.add(ref.replace("\\", "/"))
        used_names.add(Path(ref).name)

    unused = []
    for rel, path in repo_rel.items():
        normalized = rel.replace("\\", "/")
        if normalized not in used and path.name not in used_names:
            unused.append(path)

    print(f"Repository ZMEDIA files : {len(repo_rel)}")
    print(f"Markdown files scanned  : {md_count}")
    print(f"Referenced images       : {len(refs)}")
    print(f"Unused images           : {len(unused)}")
    print()

    if not unused:
        print("Nothing to clean.")
        return 0

    if not apply:
        print("DRY RUN — nothing has been moved or deleted.")
        print()
        print("First 30 unused files:")
        for path in unused[:30]:
            print(f"  - {path.relative_to(REPO_ZMEDIA)}")

        if len(unused) > 30:
            print(f"  ... and {len(unused) - 30} more")

        print()
        print("If the count looks correct, run:")
        print("  ./zmedia-tools.py --cleanup --apply")
        return 0

    # Backup is outside the Git repo.
    BACKUP_ZMEDIA.mkdir(parents=True, exist_ok=True)

    moved = 0
    for source in unused:
        rel = source.relative_to(REPO_ZMEDIA)
        destination = BACKUP_ZMEDIA / rel
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Never overwrite an existing backup.
        if destination.exists():
            print(f"SKIP (backup exists): {rel}")
            continue

        shutil.move(str(source), str(destination))
        moved += 1

    print(f"Moved {moved} unused images to:")
    print(f"  {BACKUP_ZMEDIA}")
    print()
    print("Nothing in the original Obsidian ZMEDIA was touched.")
    print("Nothing was permanently deleted.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Sync only referenced Obsidian ZMEDIA images into this Git repo."
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Show unused repo ZMEDIA files (dry-run by default).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="With --cleanup, move unused files outside the repo.",
    )
    args = parser.parse_args()

    if args.apply and not args.cleanup:
        parser.error("--apply requires --cleanup")

    if args.cleanup:
        raise SystemExit(cleanup(apply=args.apply))

    raise SystemExit(sync())


if __name__ == "__main__":
    main()
