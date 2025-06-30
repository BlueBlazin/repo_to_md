#!/usr/bin/env python3
"""repo_to_md.py
=================

Convert selected repository files into a **single, portable Markdown** document
that you can paste into an AI chat, share with reviewers, or archive for later.

Key features
------------
* **Glob‑style include patterns** (positional) and repeatable `‑x/‑‑exclude` patterns.
* Optional `‑B/‑‑base‑dir` so you never have to type long paths.
* **Alphabetical output** – files are bundled *by filename* (case‑insensitive)
  for easy, predictable diffs.
* Each added file is announced on *stderr* (`Adding …`) so you can confirm the
  selection without polluting Markdown.
* Rich `‑h/‑‑help` via **Click**.

Quick examples
--------------
```bash
# Bundle all Rust sources plus README into repo.md (alphabetical by basename)
repo_to_md src/**/*.rs README.md -o repo.md

# Different directory, trim noisy examples, list processed files
repo_to_md "src/**/*.rs" -B ~/projects/gizmo -x src/bin/** > bundle.md
```

Markdown format
---------------
Each file appears as an HTML comment + fenced code‑block. The language tag is
inferred from the extension via `_EXTENSION_TO_LANGUAGE` (extend it as you
wish).

```markdown
<!-- path/to/file.ext -->
```<lang>
<contents>
```
```
"""

import glob
import sys
from pathlib import Path
from typing import Iterable, List, Set

import click

# ---------------------------------------------------------------------------
# File‑handling helpers
# ---------------------------------------------------------------------------

_EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".rs": "rust",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".go": "go",
    ".sh": "bash",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".html": "html",
    ".css": "css",
    ".md": "markdown",
}


def _detect_language(path: Path) -> str:
    """Return a Markdown language tag for *path* (empty if unknown)."""
    return _EXTENSION_TO_LANGUAGE.get(path.suffix.lower(), "")


def _resolve_pattern(pattern: str, base_dir: Path) -> str:
    """Return absolute glob pattern anchored at *base_dir* if *pattern* is relative."""
    p = Path(pattern)
    return str(p if p.is_absolute() else base_dir / pattern)


def _glob_files(patterns: Iterable[str], base_dir: Path) -> Set[Path]:
    """Expand *patterns* into a set of absolute file paths."""
    files: Set[Path] = set()
    for pattern in patterns:
        for match in glob.glob(_resolve_pattern(pattern, base_dir), recursive=True):
            path = Path(match)
            if path.is_file():
                files.add(path.resolve())
    return files


def _sort_files(files: Set[Path]) -> List[Path]:
    """Return *files* as a list sorted alphabetically by filename (case‑insensitive)."""
    return sorted(files, key=lambda p: (p.name.lower(), str(p)))


def _build_markdown(files: Iterable[Path], base_dir: Path) -> str:
    """Return concatenated Markdown for *files* (already sorted as desired)."""
    sections: List[str] = []
    for path in files:
        lang = _detect_language(path)
        try:
            rel = path.relative_to(base_dir)
        except ValueError:
            rel = path
        sections.extend(
            [
                f"<!-- {rel} -->",
                f"```{lang}" if lang else "```",
                path.read_text(encoding="utf-8", errors="replace"),
                "```\n",
            ]
        )
    return "\n".join(sections).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Click CLI definition
# ---------------------------------------------------------------------------

_CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 100,
}


@click.command(context_settings=_CONTEXT_SETTINGS)
@click.argument("include", nargs=-1, required=True, metavar="PATTERN...")
@click.option(
    "--exclude",
    "exclude_",
    "-x",
    multiple=True,
    metavar="PATTERN",
    help="Glob patterns to remove *after* inclusion (repeatable)",
)
@click.option(
    "--base-dir",
    "-B",
    default=Path.cwd,
    show_default="current directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Directory against which patterns are evaluated",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    metavar="FILE",
    help="Write Markdown to FILE instead of stdout",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress file list on stderr",
)
def cli(
    include: tuple[str, ...],
    exclude_: tuple[str, ...],
    base_dir: Path,
    output: Path | None,
    quiet: bool,
) -> None:  # noqa: D401
    """Bundle repository files into one Markdown document.

    INCLUDE takes one or more shell‑style glob patterns (`"src/**/*.rs"`). Wrap
    them in quotes if your shell would expand them. Use `‑x/‑‑exclude` to drop
    matches. Output is alphabetised by **basename** for readability.
    """

    base_dir = base_dir.expanduser().resolve()
    if not base_dir.is_dir():
        raise click.BadParameter(f"Base directory '{base_dir}' is not a directory.")

    include_files = _glob_files(include, base_dir)
    exclude_files = _glob_files(exclude_, base_dir)
    final_files = include_files - exclude_files

    if not final_files:
        raise click.ClickException("No files matched after applying exclusions.")

    sorted_files = _sort_files(final_files)

    if not quiet:
        for path in sorted_files:
            try:
                rel = path.relative_to(base_dir)
            except ValueError:
                rel = path
            click.echo(f"Adding {rel}", err=True)

    markdown = _build_markdown(sorted_files, base_dir)

    if output:
        output.write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown)


# ---------------------------------------------------------------------------
# Entry‑point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
