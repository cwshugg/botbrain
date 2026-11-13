#!/usr/bin/env python3
"""Install Copilot instructions using only Python 3.10+."""

import argparse
import os
import stat
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

# Discover the payload relative to this standalone checkout.
ROOT = Path(__file__).absolute().parent


def check_path(path: Path, directory: bool = False) -> None:
    """Reject traversal, links, special files, and non-directory ancestors."""
    if ".." in path.parts:
        raise ValueError(f"Parent traversal is not allowed: {path}")
    for item in (*reversed(path.parents), path):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError(f"Linked path is not allowed: {item}")
        is_directory = item != path or directory
        if is_directory and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"Expected a directory: {item}")
        if not is_directory and (
            not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
        ):
            raise ValueError(f"Expected an unlinked regular file: {item}")


def instruction_files(directory: Path) -> Iterator[Path]:
    """Yield every instruction support file in deterministic path order."""
    check_path(directory, directory=True)
    for path in sorted(directory.iterdir()):
        check_path(path, directory=path.is_dir())
        if path.is_dir():
            yield from instruction_files(path)
        else:
            yield path


def install(destination: Path, overwrite: bool = True) -> tuple[int, int]:
    """Preflight all paths, then copy individual files, never directories."""
    destination = destination.expanduser().absolute()
    check_path(destination, directory=True)
    if destination.is_relative_to(ROOT) or ROOT.is_relative_to(destination):
        raise ValueError("Destination must not overlap the source checkout.")
    pending = []
    unchanged = 0
    for source in instruction_files(ROOT / "instructions"):
        content = source.read_bytes()
        target = destination / source.relative_to(ROOT)
        check_path(target)
        if target.is_file():
            if target.read_bytes() == content:
                unchanged += 1
                print(f"Unchanged: {source} -> {target}")
                continue
            if not overwrite:
                raise ValueError(
                    f"Conflict: {target}; omit --no-overwrite to replace "
                    "this file."
                )
        pending.append((source, target, content))

    for source, target, content in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        check_path(target)
        if not overwrite:
            # Exclusive creation also protects files created after preflight.
            with target.open("xb") as stream:
                stream.write(content)
        else:
            # Replace this file without truncating existing contents on error.
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(
                    dir=target.parent, delete=False
                ) as stream:
                    temporary = Path(stream.name)
                    stream.write(content)
                os.replace(temporary, target)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        print(f"Copied: {source} -> {target}")
    return len(pending), unchanged


def main() -> int:
    """Expose help, a short installation result, and actionable failures."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Installs every file under instructions/, preserving "
            "subdirectories. "
            "Differing files are replaced by default; identical files are left "
            "untouched. Never follows links. Use trusted local directories; "
            "concurrent installs are unsupported."
        ),
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / ".copilot",
        metavar="DIR",
        help="Copilot user directory (default: ~/.copilot)",
    )
    parser.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="fail on differing existing payload files instead of replacing",
    )
    args = parser.parse_args()
    try:
        copied, unchanged = install(args.destination, args.overwrite)
    except (OSError, ValueError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 1
    print(f"Installed instructions: {copied} copied, {unchanged} unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
