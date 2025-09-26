# 🚀 Release v[VERSION]

<!-- This PR description will become the GitHub release notes when merged to main -->

## Release Checklist
- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `src/sgu_client/__init__.py` (`__version__`)
- [ ] `uv.lock` updated with `uv sync`
- [ ] Version consistency test passes: `uv run pytest tests/test_version.py -v`
- [ ] All files committed to dev branch
- [ ] Replace `[VERSION]` placeholders in this template

## Added

## Fixed

## Changed

---

**Install:**
```bash
uv add sgu-client==[VERSION]
```