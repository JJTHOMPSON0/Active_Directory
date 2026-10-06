#!/usr/bin/env python3

from pathlib import Path
from urllib.parse import unquote
import re
import shutil
import sys

# --------------------------------------------------
# Configuration
# --------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
DOCS_DIR = REPO_ROOT / "active_directory"

SOURCE_ZMEDIA = Path("/home/mew2/Documents/Obsidian-Vault/ZMEDIA")
REPO_ZMEDIA = REPO_ROOT / "ZMEDIA"

# --------------------------------------------------
# Find image references containing ZMEDIA
# --------------------------------------------------

# Matches things like:
# ![](../../../ZMEDIA/Pasted%20image%2020261006211024.png)
# ![description](../../../ZMEDIA/foo.png)
ZMEDIA_PATTERN = re.compile(
    r'!\[[^\]]*\]\(([^)]*ZMEDIA/[^)]*)\)'
)

referenced_images = set()
reference_locations = []

print(f"Repository : {REPO_ROOT}")
print(f"Source     : {SOURCE_ZMEDIA}")
print(f"Destination: {REPO_ZMEDIA}")
print()

if not SOURCE_ZMEDIA.is_dir():
    print(f"ERROR: Source ZMEDIA does not exist:")
    print(f"       {SOURCE_ZMEDIA}")
    sys.exit(1)

# --------------------------------------------------
# Scan all Markdown files
# --------------------------------------------------

for md_file in DOCS_DIR.rglob("*.md"):
    try:
        text = md_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"WARNING: Could not read {md_file}")
        continue

    for match in ZMEDIA_PATTERN.finditer(text):
        ref = match.group(1)

        # Remove optional angle brackets
        ref = ref.strip().strip("<>")

        # We only need the part after ZMEDIA/
        marker = "ZMEDIA/"
        image_name = ref.split(marker, 1)[1]

        # Decode %20 etc.
        image_name = unquote(image_name)

        # Ignore query/fragment if present
        image_name = image_name.split("?", 1)[0]
        image_name = image_name.split("#", 1)[0]

        referenced_images.add(image_name)

        reference_locations.append(
            (md_file.relative_to(REPO_ROOT), image_name)
        )

# --------------------------------------------------
# Report references
# --------------------------------------------------

print(f"Markdown files scanned : {len(list(DOCS_DIR.rglob('*.md')))}")
print(f"Unique ZMEDIA images   : {len(referenced_images)}")
print()

if not referenced_images:
    print("No ZMEDIA references found.")
    sys.exit(0)

# --------------------------------------------------
# Find/copy referenced images
# --------------------------------------------------

missing = []
copied = []
already_present = []

REPO_ZMEDIA.mkdir(parents=True, exist_ok=True)

for image_name in sorted(referenced_images):

    source = SOURCE_ZMEDIA / image_name
    destination = REPO_ZMEDIA / image_name

    # Security/sanity check: don't allow ../ paths
    try:
        source.relative_to(SOURCE_ZMEDIA)
        destination.relative_to(REPO_ZMEDIA)
    except ValueError:
        print(f"WARNING: Unsafe path skipped: {image_name}")
        missing.append(image_name)
        continue

    if not source.is_file():
        missing.append(image_name)
        continue

    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        # Don't overwrite an identical file unnecessarily
        if destination.stat().st_size == source.stat().st_size:
            already_present.append(image_name)
            continue

    shutil.copy2(source, destination)
    copied.append(image_name)

# --------------------------------------------------
# Report missing images
# --------------------------------------------------

print("RESULT")
print("======")

print(f"Copied          : {len(copied)}")
print(f"Already present : {len(already_present)}")
print(f"Missing         : {len(missing)}")
print()

if copied:
    print("Copied images:")
    for x in copied:
        print(f"  + {x}")
    print()

if missing:
    print("MISSING FROM OBSIDIAN ZMEDIA:")
    for x in missing:
        print(f"  ! {x}")
    print()

# --------------------------------------------------
# Optional pruning
# --------------------------------------------------

print("NOTE:")
print("This script does NOT delete anything from either ZMEDIA.")
print("It only copies images referenced by your Markdown files.")
print()

if missing:
    print("Some referenced images could not be found in the source ZMEDIA.")
    sys.exit(2)

print("ZMEDIA sync completed successfully.")
