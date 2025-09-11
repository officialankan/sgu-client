# 🚀 Release Process Guide

## Overview
This repository uses a gitflow-lite workflow with automated releases. The release process leverages PR templates to create structured, professional release notes.

## Release Workflow

### 1. Development Phase
- Create feature branches from `dev`
- Make your changes and test thoroughly
- Create PR to merge feature branch → `dev`
- After review and testing, merge to `dev`

### 2. Release Preparation
When ready to release accumulated changes from `dev`:

1. **Create release PR using the template**:
   ```
   https://github.com/officialankan/sgu-client/compare/main...dev?template=release.md
   ```

2. **Fill out the release template**:
   - Update version in the title and install command
   - Complete sections: Added, Fixed, Changed
   - Remember: **Your PR description becomes the GitHub release notes**

3. **Version bump**:
   - Update version in `pyproject.toml` 
   - Commit this change to the `dev` branch

### 3. Release Execution
1. **Create the PR**: Use the template URL above
2. **Review**: Get approval for the release PR
3. **Merge**: When merged to `main`, the GitHub Action automatically:
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
- **Added**: New features and enhancements
- **Fixed**: Bug fixes and resolved issues  
- **Changed**: Modifications to existing features

## Best Practices

### Writing Release Notes
- **Be specific**: Instead of "Fixed bugs", write "Fixed authentication timeout in ObservedGroundwaterLevelClient"
- **Use user-friendly language**: Avoid technical jargon where possible
- **Keep it concise**: Focus on what users need to know

### Version Strategy
- **Semantic Versioning**: Use semver (major.minor.patch)
- **Breaking changes**: Increment major version
- **New features**: Increment minor version  
- **Bug fixes**: Increment patch version

### Testing Before Release
- [ ] All CI tests pass
- [ ] Manual testing of key features
- [ ] Integration tests with SGU API
- [ ] Test with both required and optional dependencies

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
