#!/usr/bin/env python3
"""Measure meaningful code/config changes in a Git diff."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys


CODE_EXTENSIONS = {
    ".astro", ".c", ".cc", ".clj", ".cljs", ".cmake", ".coffee", ".cpp",
    ".cs", ".css", ".cue", ".dart", ".ex", ".exs", ".fs", ".fsx", ".go",
    ".graphql", ".gql", ".h", ".hbs", ".hh", ".hpp", ".html", ".java",
    ".js", ".json", ".json5", ".jsx", ".kt", ".kts", ".less", ".lua",
    ".m", ".mm", ".php", ".pl", ".proto", ".py", ".rb", ".rs", ".sass",
    ".scala", ".scss", ".sh", ".sql", ".svelte", ".swift", ".tf", ".toml",
    ".ts", ".tsx", ".vue", ".xml", ".yaml", ".yml", ".zig",
}
CONFIG_NAMES = {
    ".babelrc", ".browserslistrc", ".dockerignore", ".editorconfig", ".env.example",
    ".eslintignore", ".eslintrc", ".gitattributes", ".gitignore", ".npmrc",
    ".prettierignore", ".prettierrc", "CMakeLists.txt", "Dockerfile", "Gemfile",
    "Makefile", "Procfile", "Rakefile", "Vagrantfile",
}
LOCK_NAMES = {
    "bun.lock", "bun.lockb", "Cargo.lock", "composer.lock", "flake.lock",
    "Gemfile.lock", "package-lock.json", "pnpm-lock.yaml", "poetry.lock",
    "uv.lock", "yarn.lock",
}
DOC_EXTENSIONS = {".adoc", ".md", ".mdx", ".rst", ".rtf", ".txt"}
EXCLUDED_DIRS = {
    "__fixtures__", "__snapshots__", "__tests__", "coverage", "dist", "docs",
    "fixtures", "generated", "snapshots", "test", "tests", "vendor",
}


def is_meaningful(path_text: str) -> bool:
    path = PurePosixPath(path_text)
    lower_parts = {part.lower() for part in path.parts[:-1]}
    name = path.name
    lower_name = name.lower()
    if name in LOCK_NAMES or lower_name.endswith((".lock", ".snap")):
        return False
    if path.suffix.lower() in DOC_EXTENSIONS or lower_parts & EXCLUDED_DIRS:
        return False
    if any(token in lower_name for token in (".test.", ".tests.", ".spec.", "_test.", "_tests.")):
        return False
    return name in CONFIG_NAMES or path.suffix.lower() in CODE_EXTENSIONS


def diff_args(scope: str) -> list[str]:
    base = ["git", "diff", "--numstat", "-z", "--no-renames"]
    if scope == "staged":
        return [*base, "--cached"]
    if scope == "both":
        return [*base, "HEAD"]
    return base


def run_git(args: list[str]) -> bytes:
    result = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(result.returncode)
    return result.stdout


def untracked_files() -> list[dict[str, object]]:
    output = run_git(["git", "ls-files", "--others", "--exclude-standard", "-z"])
    files: list[dict[str, object]] = []
    for raw_path in output.split(b"\0"):
        if not raw_path:
            continue
        path_text = raw_path.decode("utf-8", errors="surrogateescape")
        path = Path(path_text)
        data = path.read_bytes() if path.is_file() and not path.is_symlink() else b""
        binary = b"\0" in data
        added = 0 if binary else len(data.splitlines())
        files.append({
            "path": path_text,
            "lines_changed": added,
            "additions": added,
            "deletions": 0,
            "binary": binary,
            "meaningful": is_meaningful(path_text),
            "untracked": True,
        })
    return files


def collect(scope: str) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    for record in run_git(diff_args(scope)).split(b"\0"):
        if not record:
            continue
        fields = record.decode("utf-8", errors="surrogateescape").split("\t", 2)
        if len(fields) != 3:
            continue
        added_text, deleted_text, path = fields
        binary = added_text == "-" or deleted_text == "-"
        added = 0 if binary else int(added_text)
        deleted = 0 if binary else int(deleted_text)
        files.append({
            "path": path,
            "lines_changed": added + deleted,
            "additions": added,
            "deletions": deleted,
            "binary": binary,
            "meaningful": is_meaningful(path),
            "untracked": False,
        })
    if scope in {"unstaged", "both"}:
        files.extend(untracked_files())
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("unstaged", "staged", "both"), default="both")
    args = parser.parse_args()
    files = collect(args.scope)
    meaningful = [item for item in files if item["meaningful"]]
    json.dump({
        "scope": args.scope,
        "meaningful_files": len(meaningful),
        "total_lines_changed": sum(int(item["lines_changed"]) for item in meaningful),
        "max_lines_changed_per_file": max((int(item["lines_changed"]) for item in meaningful), default=0),
        "files": meaningful,
        "all_changed_files": len(files),
    }, sys.stdout, indent=2)
    sys.stdout.write(os.linesep)


if __name__ == "__main__":
    main()
