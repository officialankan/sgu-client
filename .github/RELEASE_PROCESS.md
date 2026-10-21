# 🚀 Release Process Guide

## Overview
This repository uses a gitflow-lite workflow with automated releases. The release process leverages PR templates to create structured, professional release notes.

`main` is the default branch, so **an issue closes when its change is released**, not when it merges into `dev`. GitHub only acts on closing keywords (`Closes #N`, `Fixes #N`) that reach the default branch: in the description of a PR merged into `main`, or in a commit message that lands on `main`. The release PR lists every issue it ships as `Closes #N`, and merging it closes them all.

## Release Workflow

### 1. Development Phase
- Create feature branches from `dev`
- Make your changes and test thoroughly
- Create PR to merge feature branch → `dev`. GitHub suggests `main` as the base, because it is the default branch: change it to `dev` (`gh pr create --base dev`). A check fails any PR into `main` that doesn't come from `dev`
- Name the issue in the PR description (`Closes #N`) and in commit messages as usual. It doesn't close anything yet; it closes the issue when the change reaches `main`
- After review and testing, merge to `dev`
- Feature PRs never change the version. They add their notes, including breaking changes, under `[Unreleased]` in `CHANGELOG.md`

### 2. Release
When ready to release accumulated changes from `dev`:

1. **Pick the version**: see [Version Strategy](#version-strategy).

2. **Create the release PR `dev` → `main`** with the template:
   ```
   https://github.com/officialankan/sgu-client/compare/main...dev?template=release.md
   ```
   **Fill out the template**. **Your PR description becomes the GitHub release notes**:
   - Replace `[VERSION]` in the title and install command
   - **Summary**: a short before/after of the change users will notice most
   - **Added / Fixed / Changed / ⚠️ Breaking Changes**: copy them from the changelog, citing the issue and the PR for each entry (e.g. `(#49, #52)`)
   - **Closes**: one `Closes #N` line for every issue the release ships. These close when the PR is merged
   - **Merge Danger**: every release is a one-way door, because a PyPI version can't be uploaded again (a mistake means a new patch release). Describe the blast radius for users who upgrade, e.g. code that breaks because of a breaking change

3. **Commit the version bump directly to `dev`** as `chore: release vX.Y.Z`. It is the one change that goes into `dev` without a PR, so it needs an account allowed to bypass `dev`'s branch protection. The release PR picks it up and CI runs again. The bump changes:
   - `version` in `pyproject.toml`
   - `__version__` in `src/sgu_client/__init__.py`
   - `release` in `docs/source/conf.py`
   - `uv.lock`: run `uv lock` so the `sgu-client` entry matches
   - `CHANGELOG.md`: rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`, add a fresh empty `[Unreleased]` above it, and add anything merged without a changelog entry

   Before pushing, run the checks with the optional dependencies installed: `uv sync --all-extras --all-groups`, then `uv run pytest`, `uv run ruff check`, `uv run ruff format --check` and `uv run ty check`.

4. **Try the TestPyPI build**: CI publishes `X.Y.Z.devN` to TestPyPI on the PR and comments the install command.

5. **Merge**: Merging closes every issue listed under **Closes**. When merged to `main`, the GitHub Action automatically:
   - Publishes to PyPI
   - Creates GitHub release with your PR description as release notes
   - Attaches distribution files

## Template Usage

### Quick Template Access
For this repository:
```
https://github.com/officialankan/sgu-client/compare/main...dev?template=release.md
```

### Template Sections
- **Summary**: The headline change, shown as a before/after
- **Added**: New features and enhancements
- **Fixed**: Bug fixes and resolved issues  
- **Changed**: Modifications to existing features
- **⚠️ Breaking Changes**: Anything that can break code using the package
- **Closes**: The issues the release ships, closed on merge
- **Merge Danger**: Whether the merge can be undone, and who is affected

## Best Practices

### Writing Release Notes
- **Be specific**: Instead of "Fixed bugs", write "Fixed authentication timeout in ObservedGroundwaterLevelClient"
- **Use user-friendly language**: Avoid technical jargon where possible
- **Keep it concise**: Focus on what users need to know

### Version Strategy
- **Semantic Versioning**: Use semver (major.minor.patch)
- **Breaking changes**: Increment major version. Before 1.0, increment the minor version instead (e.g. 0.5.0 → 0.6.0)
- **New features**: Increment minor version  
- **Bug fixes**: Increment patch version
- **Nothing computes the version for you**: CI publishes whatever `pyproject.toml` says, so merging without a bump fails on PyPI

### Testing Before Release
- [ ] All CI tests pass
- [ ] Manual testing of key features
- [ ] Integration tests with SGU API
- [ ] Test with both required and optional dependencies (`uv sync --all-extras --all-groups`; without `--all-extras` pandas is missing and tests fail)

## Automation Details

### How It Works
1. **PR Template**: Provides structure for release notes
2. **Merge Detection**: GitHub Action detects merge to `main`
3. **PR Extraction**: Finds the original PR that was merged
4. **Release Creation**: Uses PR body as release notes
5. **PyPI Publishing**: Automatically publishes the new version

### Fallback Behavior
If PR information cannot be extracted, the workflow falls back to a generic release message with installation instructions.

## Troubleshooting

### Template Not Loading
- Ensure you're using the correct template URL
- Check that `.github/pull_request_template/release.md` exists
- Verify branch names (`main` and `dev`) in the URL

### Release Notes Not Applied
- Ensure the merge commit includes PR information
- Check GitHub Action logs for PR extraction errors
- Verify the PR body contains content (not just template placeholders)

### Manual Release
If automatic release fails, you can create a manual release:
1. Go to GitHub Releases
2. Create new release with appropriate tag (v1.2.3)
3. Use the merged PR description as release notes
4. Attach distribution files from PyPI
