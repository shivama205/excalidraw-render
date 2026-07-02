#!/usr/bin/env python3
"""Regenerate the Homebrew tap formula's url/sha256 stanzas for a release.

Resolves the actual runtime dependency closure by installing the package
into a throwaway venv, then rewrites the top-level url/sha256 and every
`resource` block in the formula to match. Everything else in the formula
(desc, depends_on, comments, test block) is left untouched.

Usage: sync_homebrew_tap.py <version> <path-to-formula.rb>
"""
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

PACKAGE = "excalidraw-render"
IGNORE = {"pip", "setuptools", "wheel", PACKAGE}


def pypi_sdist(name: str, version: str) -> tuple[str, str]:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json") as r:
        data = json.load(r)
    for f in data["urls"]:
        if f["packagetype"] == "sdist":
            return f["url"], f["digests"]["sha256"]
    raise SystemExit(f"no sdist published for {name}=={version}")


def resolve_closure(version: str) -> dict[str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        venv = Path(tmp) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        pip = venv / "bin" / "pip"
        subprocess.run([str(pip), "install", "--quiet", f"{PACKAGE}=={version}"], check=True)
        out = subprocess.run(
            [str(pip), "list", "--format=freeze"], check=True, capture_output=True, text=True
        ).stdout
    closure = {}
    for line in out.splitlines():
        name, _, ver = line.partition("==")
        if name.lower() not in IGNORE:
            closure[name.lower()] = ver
    return closure


def replace_main(text: str, url: str, sha: str) -> str:
    pattern = re.compile(r'(homepage "[^"]+"\n  url ")[^"]+("\n  sha256 ")[0-9a-f]+(")')
    new_text, n = pattern.subn(lambda m: m.group(1) + url + m.group(2) + sha + m.group(3), text, count=1)
    if n != 1:
        raise SystemExit("failed to patch top-level url/sha256 — formula layout changed?")
    return new_text


def render_resource_block(name: str, url: str, sha: str) -> str:
    return f'  resource "{name}" do\n    url "{url}"\n    sha256 "{sha}"\n  end'


def replace_resources(text: str, closure: dict[str, str]) -> str:
    start = text.index('\n  resource "')
    end = text.index("\n  def install")
    blocks = [render_resource_block(name, *pypi_sdist(name, ver)) for name, ver in sorted(closure.items())]
    middle = "\n\n".join(blocks) + "\n\n"
    return text[: start + 1] + middle + text[end + 1 :]


def main() -> None:
    version, formula_path = sys.argv[1], Path(sys.argv[2])
    text = formula_path.read_text()

    main_url, main_sha = pypi_sdist(PACKAGE, version)
    text = replace_main(text, main_url, main_sha)

    closure = resolve_closure(version)
    text = replace_resources(text, closure)

    formula_path.write_text(text)


if __name__ == "__main__":
    main()
