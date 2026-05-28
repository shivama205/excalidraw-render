# Releasing `excalidraw-render`

This is the runbook for publishing a new version to PyPI.

## Prerequisites (one-time)

1. PyPI account: https://pypi.org/account/register/
2. Optional: TestPyPI account (a separate registration): https://test.pypi.org/account/register/
3. Generate a PyPI API token scoped to this project:
   - https://pypi.org/manage/account/token/
   - Scope: "Project: excalidraw-render" (after the first release; before that, scope it more broadly and re-scope later)
4. Save the token securely. Suggested: `~/.pypirc` with `[pypi]` and `[testpypi]` sections, or use `keyring`.
   ```ini
   # ~/.pypirc — chmod 600
   [pypi]
     username = __token__
     password = pypi-...

   [testpypi]
     repository = https://test.pypi.org/legacy/
     username = __token__
     password = pypi-...
   ```

## Release procedure

```bash
cd ~/Projects/Hobby/excalidraw-render

# 1. Sanity: clean tree, tests green
git status                      # no uncommitted changes
.venv/bin/pytest -q             # all tests pass
.venv/bin/ruff check src tests  # clean
.venv/bin/mypy src              # clean

# 2. Bump version in src/excalidraw_render/_version.py
#    Also update CHANGELOG.md: move [Unreleased] section to [vX.Y.Z] - YYYY-MM-DD

# 3. Commit the version bump
git add src/excalidraw_render/_version.py CHANGELOG.md
git commit -m "release: vX.Y.Z"
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin main --follow-tags

# 4. Clean any previous build artifacts
rm -rf dist/ build/ *.egg-info

# 5. Build wheel + sdist
.venv/bin/python -m build

# 6. Validate
.venv/bin/twine check dist/*

# 7. (Optional but recommended for the first release) upload to TestPyPI first
.venv/bin/twine upload --repository testpypi dist/*

# Verify in a clean venv:
python -m venv /tmp/verify-test-pypi
/tmp/verify-test-pypi/bin/pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ excalidraw-render
/tmp/verify-test-pypi/bin/excalidraw-render --help

# 8. Upload to real PyPI
.venv/bin/twine upload dist/*

# 9. Create a GitHub release tied to the tag
gh release create vX.Y.Z dist/* \
  --title "vX.Y.Z" \
  --notes-file CHANGELOG.md \
  --repo shivama205/excalidraw-render
```

## Version scheme

Semver:
- `0.1.0` — first public release. Anything ≥ 0.1.0 is considered usable.
- `0.2.0` — first feature-release after 0.1.0. (Backlog: roughness, terminal, markdown subcommand, etc.)
- `0.x.y` — `x` minor bumps for features; `y` patches for bugfixes.
- Pre-1.0: API may break between minor versions; CHANGELOG.md flags any breakage.
- `1.0.0` — API stabilized. After this, semver is strict.

Pre-release suffixes (`a1`, `b1`, `rc1`) and dev releases (`.dev0`) are allowed for testing on TestPyPI without burning version numbers on real PyPI.

## After every release

- Update CHANGELOG.md: open a new `[Unreleased]` section above the released one.
- Bump version to the next `.dev0` (e.g. after releasing `0.1.0`, set `_version.py` to `0.2.0.dev0`).
- Commit and push.
