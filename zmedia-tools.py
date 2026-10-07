#!/usr/bin/env python3
"""
Sync Markdown notes from Obsidian into the Active_Directory repo.

SOURCE OF TRUTH
---------------
For every repo Markdown note that has a matching Obsidian note, the Obsidian
note is authoritative. The repo note is replaced with the Obsidian note's
content, preserving its text and exact image order.

LOCAL IMAGES
------------
Local Obsidian image embeds are resolved from the master:
    /home/mew2/Documents/Obsidian-Vault/ZMEDIA

They are copied into:
    <repo>/ZMEDIA

and converted to repo-relative Markdown image links, e.g.:
    ![](../../ZMEDIA/Pasted%20image%2020261006210736.png)

Remote image URLs are left unchanged.

SAFETY
------
- Never modifies the Obsidian vault.
- Never deletes files from repo/ZMEDIA.
- Does not touch repo-only Markdown files such as README.md/SUMMARY.md.
- If a source image is missing or ambiguous, that note is NOT replaced.
- Matching is by exact repo-relative path first, then by unique filename.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, unquote

REPO_ROOT = Path(__file__).resolve().parent
OBSIDIAN_ROOT = Path("/home/mew2/Documents/Obsidian-Vault")
SOURCE_ZMEDIA = OBSIDIAN_ROOT / "ZMEDIA"
REPO_ZMEDIA = REPO_ROOT / "ZMEDIA"

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
    ".bmp", ".tif", ".tiff", ".avif"
}

# Standard Markdown image: ![alt](target)
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]*)\)")

# Obsidian wiki image: ![[file.png]] or ![[file.png|300]]
WIKI_IMAGE_RE = re.compile(r"!\[\[([^\]]+)\]\]")


def is_remote(value: str) -> bool:
    value = value.strip().lower()
    return value.startswith(("http://", "https://", "data:", "//"))


def clean_markdown_target(raw: str) -> str:
    """Extract the URL/path portion from a Markdown image target."""
    raw = raw.strip()

    # Markdown destination may be written as <path with spaces>.
    if raw.startswith("<") and ">" in raw:
        raw = raw[1:raw.index(">")]
    else:
        # Optional title: path "title" or path 'title'. For our image names,
        # taking the first token is sufficient when the path itself has no
        # unescaped spaces. Obsidian screenshots are handled by wiki syntax or
        # URL-decoding below.
        m = re.match(r"^(\S+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?$", raw)
        if m:
            raw = m.group(1)

    raw = raw.split("#", 1)[0].split("?", 1)[0]
    return unquote(raw).strip()


def clean_wiki_target(raw: str) -> str:
    """Extract the filename from an Obsidian wiki image embed."""
    raw = raw.strip()
    # ![[image.png|300]] / ![[image.png|alt text]]
    target = raw.split("|", 1)[0].strip()
    return unquote(target).strip()


def is_local_image_target(target: str) -> bool:
    if not target or is_remote(target):
        return False
    return Path(target.split("#", 1)[0]).suffix.lower() in IMAGE_EXTENSIONS


def normalize_source_ref(target: str) -> str | None:
    """Normalize an image path to a path relative to the master ZMEDIA."""
    target = target.replace("\\", "/").strip()
    if not target or is_remote(target):
        return None

    # Handle vault/repo-style references containing ZMEDIA.
    if "/ZMEDIA/" in target:
        target = target.split("/ZMEDIA/", 1)[1]
    elif target.startswith("ZMEDIA/"):
        target = target[len("ZMEDIA/"):]

    while target.startswith("./"):
        target = target[2:]
    target = target.lstrip("/")

    return target or None


def iter_image_tokens(text: str):
    """Yield image token matches in document order."""
    matches = []
    matches.extend((m.start(), m.end(), "md", m) for m in MD_IMAGE_RE.finditer(text))
    matches.extend((m.start(), m.end(), "wiki", m) for m in WIKI_IMAGE_RE.finditer(text))
    matches.sort(key=lambda x: x[0])
    return matches


def token_source_ref(kind: str, match: re.Match) -> str | None:
    if kind == "wiki":
        target = clean_wiki_target(match.group(1))
    else:
        target = clean_markdown_target(match.group(1))

    if not is_local_image_target(target):
        return None
    return normalize_source_ref(target)


def repo_markdown_files() -> list[Path]:
    return sorted(
        p for p in REPO_ROOT.rglob("*.md")
        if ".git" not in p.parts and ".obsidian" not in p.parts
    )


def source_markdown_index():
    if not OBSIDIAN_ROOT.is_dir():
        raise SystemExit(f"ERROR: Obsidian vault does not exist: {OBSIDIAN_ROOT}")

    by_rel: dict[str, Path] = {}
    by_name: dict[str, list[Path]] = {}

    for p in OBSIDIAN_ROOT.rglob("*.md"):
        if ".obsidian" in p.parts:
            continue
        rel = p.relative_to(OBSIDIAN_ROOT).as_posix()
        by_rel[rel] = p
        by_name.setdefault(p.name, []).append(p)

    return by_rel, by_name


def find_source_note(repo_md: Path, by_rel, by_name):
    """Find the Obsidian note corresponding to a repo note."""
    rel = repo_md.relative_to(REPO_ROOT).as_posix()

    # Best case: identical path below the two roots.
    if rel in by_rel:
        return by_rel[rel], None

    # Existing workflow may copy notes from a different Obsidian folder while
    # retaining the same filename. Only use filename matching when unique.
    candidates = by_name.get(repo_md.name, [])
    if len(candidates) == 1:
        return candidates[0], None
    if len(candidates) > 1:
        return None, f"multiple Obsidian notes named {repo_md.name}"
    return None, "no Obsidian source note found"


def source_zmedia_index():
    if not SOURCE_ZMEDIA.is_dir():
        raise SystemExit(f"ERROR: source ZMEDIA does not exist: {SOURCE_ZMEDIA}")

    by_rel: dict[str, Path] = {}
    by_name: dict[str, list[Path]] = {}

    for p in SOURCE_ZMEDIA.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(SOURCE_ZMEDIA).as_posix()
        by_rel[rel] = p
        by_name.setdefault(p.name, []).append(p)

    return by_rel, by_name


def resolve_source_image(ref: str, by_rel, by_name):
    ref = ref.replace("\\", "/").lstrip("/")

    if ref in by_rel:
        return by_rel[ref], None

    candidates = by_name.get(Path(ref).name, [])
    if len(candidates) == 1:
        return candidates[0], None
    if len(candidates) > 1:
        return None, f"ambiguous filename: {Path(ref).name}"
    return None, f"not found in Obsidian ZMEDIA: {ref}"


def repo_image_url(repo_md: Path, source_image: Path) -> str:
    """Return a URL-encoded path from the repo note to repo/ZMEDIA."""
    rel_img = source_image.relative_to(SOURCE_ZMEDIA).as_posix()
    note_dir = repo_md.parent.relative_to(REPO_ROOT)
    prefix = "../" * len(note_dir.parts)

    # Keep common filename punctuation readable, but encode spaces and other
    # characters GitHub/GitBook URLs need encoded.
    encoded = "/".join(
        quote(part, safe="()[]'!,-._~")
        for part in rel_img.split("/")
    )
    return f"{prefix}ZMEDIA/{encoded}"


def collect_source_images(source_text: str):
    """Return unique local image refs in exact document order."""
    refs = []
    for _, _, kind, match in iter_image_tokens(source_text):
        ref = token_source_ref(kind, match)
        if ref:
            refs.append(ref)
    return refs


def rewrite_source_note(source_text: str, repo_md: Path, resolved: dict[str, Path]) -> str:
    """
    Copy the source note's text exactly, except:
      - local Markdown image targets become repo-relative ZMEDIA links
      - local Obsidian wiki image embeds become Markdown image links
      - remote images and all non-image text remain unchanged
    """
    pieces = []
    pos = 0

    for start, end, kind, match in iter_image_tokens(source_text):
        pieces.append(source_text[pos:start])
        token = match.group(0)
        ref = token_source_ref(kind, match)

        if ref and ref in resolved:
            pieces.append(f"![]({repo_image_url(repo_md, resolved[ref])})")
        else:
            # This should only be reached for remote images/non-local embeds;
            # unresolved local images are blocked before this function runs.
            pieces.append(token)
        pos = end

    pieces.append(source_text[pos:])
    return "".join(pieces)


def copy_required_images(source_refs, z_by_rel, z_by_name):
    """Resolve and copy all source images. Returns resolved/missing/ambiguous."""
    resolved: dict[str, Path] = {}
    missing = []
    ambiguous = []

    for ref in dict.fromkeys(source_refs):
        src, err = resolve_source_image(ref, z_by_rel, z_by_name)
        if src is None:
            if err and err.startswith("ambiguous"):
                ambiguous.append((ref, err))
            else:
                missing.append((ref, err))
            continue

        resolved[ref] = src

    # Do not partially replace a note. First resolve everything; only then copy.
    copied = []
    already = []

    if not missing and not ambiguous:
        for src in resolved.values():
            dest = REPO_ZMEDIA / src.relative_to(SOURCE_ZMEDIA)
            dest.parent.mkdir(parents=True, exist_ok=True)

            if dest.exists() and dest.stat().st_size == src.stat().st_size:
                already.append(str(dest.relative_to(REPO_ZMEDIA)))
            else:
                shutil.copy2(src, dest)
                copied.append(str(dest.relative_to(REPO_ZMEDIA)))

    return resolved, copied, already, missing, ambiguous


def sync():
    repo_files = repo_markdown_files()
    source_by_rel, source_by_name = source_markdown_index()
    z_by_rel, z_by_name = source_zmedia_index()
    REPO_ZMEDIA.mkdir(parents=True, exist_ok=True)

    source_notes_used = 0
    local_refs = 0
    copied = []
    already = []
    rewritten = []
    missing = []
    ambiguous = []
    skipped = []

    for repo_md in repo_files:
        source_note, source_error = find_source_note(
            repo_md, source_by_rel, source_by_name
        )

        if source_note is None:
            # Repo-only files are normal. Don't replace them.
            continue

        source_notes_used += 1
        source_text = source_note.read_text(encoding="utf-8", errors="strict")
        source_refs = collect_source_images(source_text)
        local_refs += len(source_refs)

        resolved, copied_now, already_now, missing_now, ambiguous_now = copy_required_images(
            source_refs, z_by_rel, z_by_name
        )

        if missing_now or ambiguous_now:
            skipped.append((repo_md, source_note, missing_now, ambiguous_now))
            missing.extend((repo_md, ref, err) for ref, err in missing_now)
            ambiguous.extend((repo_md, ref, err) for ref, err in ambiguous_now)
            continue

        new_text = rewrite_source_note(source_text, repo_md, resolved)
        old_text = repo_md.read_text(encoding="utf-8", errors="strict")

        copied.extend(copied_now)
        already.extend(already_now)

        if new_text != old_text:
            repo_md.write_text(new_text, encoding="utf-8")
            rewritten.append(repo_md)

    print(f"Repository : {REPO_ROOT}")
    print(f"Obsidian   : {OBSIDIAN_ROOT}")
    print(f"Source     : {SOURCE_ZMEDIA}")
    print(f"Destination: {REPO_ZMEDIA}\n")
    print(f"Markdown files scanned       : {len(repo_files)}")
    print(f"Obsidian source notes found  : {source_notes_used}")
    print(f"Local image references found : {local_refs}\n")

    print("SYNC RESULT")
    print("===========")
    print(f"Copied                      : {len(set(copied))}")
    print(f"Already present             : {len(set(already))}")
    print(f"Missing from source ZMEDIA  : {len(missing)}")
    print(f"Ambiguous source images     : {len(ambiguous)}")
    print(f"Markdown files rewritten     : {len(rewritten)}")

    if rewritten:
        print("\nREPLACED FROM OBSIDIAN:")
        for p in rewritten:
            print(f"  * {p.relative_to(REPO_ROOT)}")

    if missing or ambiguous:
        print("\nNOTES NOT REPLACED:")
        for repo_md, source_note, missing_now, ambiguous_now in skipped:
            print(f"  ! {repo_md.relative_to(REPO_ROOT)}")
            print(f"    source: {source_note.relative_to(OBSIDIAN_ROOT)}")
            for ref, err in missing_now:
                print(f"    missing: {ref} ({err})")
            for ref, err in ambiguous_now:
                print(f"    ambiguous: {ref} ({err})")

    print()
    if missing or ambiguous:
        print("Sync stopped with unresolved source images; affected notes were left unchanged.")
        return 2

    print("Sync completed successfully.")
    return 0


def audit():
    repo_files = repo_markdown_files()
    source_by_rel, source_by_name = source_markdown_index()
    z_by_rel, z_by_name = source_zmedia_index()

    source_count = 0
    total = 0
    resolvable = 0
    missing = []
    ambiguous = []

    for repo_md in repo_files:
        source_note, _ = find_source_note(repo_md, source_by_rel, source_by_name)
        if source_note is None:
            continue

        source_count += 1
        text = source_note.read_text(encoding="utf-8", errors="strict")
        refs = collect_source_images(text)
        total += len(refs)

        for ref in refs:
            src, err = resolve_source_image(ref, z_by_rel, z_by_name)
            if src:
                resolvable += 1
            elif err and err.startswith("ambiguous"):
                ambiguous.append((repo_md, ref, err))
            else:
                missing.append((repo_md, ref, err))

    print(f"Markdown files scanned       : {len(repo_files)}")
    print(f"Obsidian source notes found  : {source_count}")
    print(f"Local image references found : {total}")
    print(f"Resolvable                   : {resolvable}")
    print(f"Missing from source ZMEDIA   : {len(missing)}")
    print(f"Ambiguous source images      : {len(ambiguous)}")

    if missing:
        print("\nMISSING:")
        for repo_md, ref, err in missing:
            print(f"  ! {repo_md.relative_to(REPO_ROOT)}: {ref} ({err})")
    if ambiguous:
        print("\nAMBIGUOUS:")
        for repo_md, ref, err in ambiguous:
            print(f"  ! {repo_md.relative_to(REPO_ROOT)}: {ref} ({err})")

    return 2 if missing or ambiguous else 0


def main():
    parser = argparse.ArgumentParser(
        description="Replace repo notes from matching Obsidian notes and sync local images."
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Check that all local images used by matching Obsidian notes resolve in ZMEDIA.",
    )
    args = parser.parse_args()
    raise SystemExit(audit() if args.audit else sync())


if __name__ == "__main__":
    main()
