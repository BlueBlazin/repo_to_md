# Repo to Markdown

Convert repo code + other files into a single markdown.

Provide multiple glob patterns to include any number of files from the repo. Pass multiple exclude patterns for precise control.

Repo-to-md will convert all it into a single, annotated markdown file with all files included in alphabetically sorted order.

## Installation

```sh
uv build --wheel
uv tool install dict/*.whl

repo-to-md --help
```

## Usage

```
Usage: main.py [OPTIONS] PATTERN...

  Bundle repository files into one Markdown document.

  INCLUDE takes one or more shell‑style glob patterns (`"src/**/*.rs"`). Wrap
  them in quotes if your shell would expand them. Use `‑x/‑‑exclude` to drop
  matches. Output is alphabetised by **basename** for readability.

Options:
  -x, --exclude PATTERN     Glob patterns to remove *after* inclusion
                            (repeatable)
  -B, --base-dir DIRECTORY  Directory against which patterns are evaluated
                            [default: (current directory)]
  -o, --output FILE         Write Markdown to FILE instead of stdout
  -q, --quiet               Suppress file list on stderr
  -h, --help                Show this message and exit.
```
