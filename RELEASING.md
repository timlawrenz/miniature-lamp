# Release Guide

This document describes the release process for DINO Upscale ComfyUI node.

## Overview

We follow a structured release process with local testing before publishing to ComfyUI Registry. The process ensures quality and gives users confidence in updates.

## Branch Strategy

### Main Branch (`main`)
- Contains latest development code
- Should always be in working state
- Commits go here during active development
- No need to publish every commit

### Release Branches (`release/vX.Y.Z`)
- Created when preparing a release
- Only bug fixes committed here
- Merged back to `main` after release
- Deleted after successful release

### Feature Branches
- For experimental or risky work
- Branch from `main`
- Test thoroughly before merging
- Merge via pull request

## Version Numbering

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **Major (X.0.0)**: Breaking changes
  - API changes requiring user workflow updates
  - Removed functionality
  - Changes to node inputs/outputs
  - Example: v1.x → v2.0.0 (removed FLUX)

- **Minor (X.Y.0)**: New features (backward compatible)
  - New functionality that doesn't break existing workflows
  - New optional parameters
  - Example: v1.0.x → v1.1.0 (added ComfyUI sampler)

- **Patch (X.Y.Z)**: Bug fixes
  - Fixes that don't add features
  - Performance improvements
  - Documentation updates
  - Example: v2.0.0 → v2.0.1 (fix VAE encoding)

## Release Process

### 1. Pre-Release Checklist

Before starting a release:

- [ ] All features complete and tested
- [ ] CHANGELOG.md updated with release notes
- [ ] Documentation reflects new version
- [ ] No critical bugs in issue tracker
- [ ] Ready to support users with questions

### 2. Update Version

```bash
# Edit pyproject.toml
version = "X.Y.Z"

# Verify it's correct
grep "version" pyproject.toml
```

### 3. Update CHANGELOG

Add new version section at the top of `CHANGELOG.md`:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature descriptions

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes

### BREAKING (if major version)
- Breaking changes with migration guide
```

### 4. Local Testing (CRITICAL)

This is the most important step. You MUST test in actual ComfyUI before releasing.

#### Installation Test

```bash
# In ComfyUI custom_nodes directory
cd /path/to/ComfyUI/custom_nodes/

# If already installed, remove old version
rm -rf comfyui-dino-upscale

# Clone your local changes
cp -r /path/to/miniature-lamp comfyui-dino-upscale
cd comfyui-dino-upscale

# Install dependencies
pip install -r requirements.txt

# Restart ComfyUI
```

#### Testing Checklist

Test ALL of the following:

- [ ] Node appears in ComfyUI menu (image → upscaling → DINO Upscale)
- [ ] Can load external MODEL + VAE
- [ ] Upscaling with SD 1.5 model works
- [ ] Upscaling with SDXL model works
- [ ] Upscaling with FLUX model works (if available)
- [ ] DINO feature extraction works
- [ ] Progress bar updates correctly
- [ ] Stop button works
- [ ] Error messages are clear and helpful
- [ ] Example workflows (if any) load and run
- [ ] Memory usage is acceptable
- [ ] No Python errors in console

#### Test Different Scenarios

- Small images (< 512x512)
- Medium images (512-1024)
- Large images (> 1024, tests tiling)
- Different scale factors (1.5x, 2x, 3x)
- Different denoise values (0.1, 0.3, 0.5)
- With DINO enabled and disabled

#### Version-Specific Testing

- **Major version**: Test migration from previous major version
- **Minor version**: Test new features + existing features still work
- **Patch version**: Test bug fix + smoke test major features

### 5. Commit and Create Release Branch (Optional)

For major/minor releases, consider using a release branch:

```bash
# Create release branch
git checkout -b release/vX.Y.Z

# Commit version changes
git add pyproject.toml CHANGELOG.md
git commit -m "Prepare release vX.Y.Z"

# Push to remote
git push origin release/vX.Y.Z
```

For patch releases, you can work directly on `main`.

### 6. Create Git Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release vX.Y.Z

Summary of changes:
- Feature 1
- Feature 2
- Fix for issue #123
"

# Verify tag
git tag -n5 vX.Y.Z

# Push tag to GitHub
git push origin vX.Y.Z
```

**IMPORTANT**: The tag name MUST match the version in `pyproject.toml` exactly!

### 7. Merge to Main (if using release branch)

```bash
# Switch to main
git checkout main

# Merge release branch
git merge release/vX.Y.Z

# Push to remote
git push origin main

# Delete release branch
git branch -d release/vX.Y.Z
git push origin --delete release/vX.Y.Z
```

### 8. Publish to ComfyUI Registry

ComfyUI Registry automatically detects new tags on GitHub.

1. **Wait for registry update** (usually within 1 hour)
2. **Verify in ComfyUI Manager**:
   - Open ComfyUI Manager
   - Search for "DINO Upscale"
   - Check that new version appears
3. **Test installation from registry**:
   - Uninstall local copy
   - Install via ComfyUI Manager
   - Verify it works

### 9. Post-Release

- [ ] Announce release (if major version) on GitHub discussions or relevant forums
- [ ] Monitor GitHub issues for bug reports
- [ ] Be prepared to release hotfix if critical bugs found
- [ ] Update project documentation if needed

## Hotfix Process

If a critical bug is found in a release:

### 1. Create Hotfix Branch

```bash
# Branch from the problematic release tag
git checkout -b hotfix/vX.Y.Z+1 vX.Y.Z

# Or if tag doesn't exist, from main
git checkout -b hotfix/vX.Y.Z+1 main
```

### 2. Fix the Bug

- Make minimal changes to fix the issue
- Don't add new features
- Test thoroughly in ComfyUI

### 3. Increment Patch Version

```bash
# Update pyproject.toml
version = "X.Y.Z+1"

# Update CHANGELOG.md
## [X.Y.Z+1] - YYYY-MM-DD

### Fixed
- Critical bug description and fix
```

### 4. Release Hotfix

Follow the normal release process from step 5 (Create Git Tag).

**Timeline**: Try to release hotfix within 24 hours of discovering critical bug.

## Testing Requirements Summary

| Release Type | Testing Level | Time Expected |
|-------------|---------------|---------------|
| Major | Full testing + migration testing | 2-4 hours |
| Minor | Feature testing + regression testing | 1-2 hours |
| Patch | Bug fix verification + smoke test | 30 min - 1 hour |

## Version History

Current version: **2.0.0**

Recent releases:
- v2.0.0 (2024-11-03): Removed FLUX, fully model-agnostic
- v1.1.0 (2024-11-03): Added ComfyUI native sampler support
- v1.0.2 (2024-11-03): Renamed to DINO Upscale
- v1.0.1 (2024-11-02): Initial ComfyUI Registry release

## FAQs

### When should I publish a release?

Publish when:
- You've completed a feature you want users to have
- You've fixed important bugs
- You have changes that improve the user experience
- It's been a while since last release and you have useful changes

Don't publish:
- Every single commit
- Unfinished features
- Untested changes
- Breaking changes without migration guide

### How often should I release?

There's no fixed schedule. Release when you have meaningful changes:
- Bug fixes: As soon as tested
- Minor features: When complete and tested
- Major changes: When thoroughly tested and documented

### What if I forgot to update CHANGELOG?

You can fix it:
1. Update CHANGELOG.md
2. Commit the change
3. Move the tag: `git tag -f vX.Y.Z`
4. Force push: `git push origin vX.Y.Z --force`

Only do this immediately after release, before users have installed!

### What if tests fail after I pushed the tag?

If you catch it quickly:
1. Delete the tag: `git push origin --delete vX.Y.Z`
2. Fix the issue
3. Create new tag with same version
4. Push again

If users already installed:
1. Leave tag as-is
2. Fix the bug
3. Release hotfix version (X.Y.Z+1)
4. Document issue in CHANGELOG

### How do I test with different ComfyUI versions?

Use separate ComfyUI installations or Docker:
```bash
# Clone ComfyUI at specific version
git clone https://github.com/comfyanonymous/ComfyUI.git ComfyUI-v0.3.67
cd ComfyUI-v0.3.67
git checkout v0.3.67
```

## Getting Help

- **Questions**: Open GitHub issue with "question" label
- **Bugs**: Open GitHub issue with "bug" label  
- **Release issues**: Contact maintainer directly

## See Also

- [CHANGELOG.md](CHANGELOG.md) - Version history
- [MIGRATION_v2.md](MIGRATION_v2.md) - v2.0 migration guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
