## ADDED Requirements

### Requirement: Branch Strategy
The project SHALL use a branch-based workflow for managing releases.

#### Scenario: Main branch for development
- **WHEN** developers commit changes
- **THEN** changes go to `main` branch
- **AND** `main` contains latest development code

#### Scenario: Release branches for stable versions
- **WHEN** preparing a release
- **THEN** create a branch named `release/vX.Y.Z`
- **AND** only bug fixes are committed to release branch
- **AND** release branch is merged to main after release

#### Scenario: Feature branches for experimental work
- **WHEN** working on experimental features
- **THEN** create feature branch from `main`
- **AND** test locally before merging
- **AND** merge to `main` via pull request

### Requirement: Version Numbering
The project SHALL follow Semantic Versioning 2.0.0 for all releases.

#### Scenario: Major version for breaking changes
- **WHEN** making breaking changes (API, workflow changes)
- **THEN** increment major version (X.0.0)
- **AND** document migration guide
- **AND** update CHANGELOG with BREAKING label

#### Scenario: Minor version for new features
- **WHEN** adding new features (backward compatible)
- **THEN** increment minor version (X.Y.0)
- **AND** document new features in CHANGELOG

#### Scenario: Patch version for bug fixes
- **WHEN** fixing bugs without adding features
- **THEN** increment patch version (X.Y.Z)
- **AND** document fixes in CHANGELOG

### Requirement: Local Testing Before Release
The project SHALL require local testing in actual ComfyUI environment before publishing any release.

#### Scenario: Test installation from local directory
- **WHEN** preparing a release
- **THEN** install node in ComfyUI from local directory
- **AND** test all major features work
- **AND** verify workflow examples function correctly
- **AND** check error messages are clear

#### Scenario: Test with target ComfyUI version
- **WHEN** testing a release
- **THEN** test on minimum supported ComfyUI version
- **AND** test on latest ComfyUI version
- **AND** document any version-specific issues

### Requirement: Git Tagging
The project SHALL create annotated git tags for all releases.

#### Scenario: Create release tag
- **WHEN** publishing a release
- **THEN** create annotated tag named `vX.Y.Z`
- **AND** tag message includes release notes summary
- **AND** tag is pushed to remote repository
- **AND** tag points to release commit

#### Scenario: Tag naming convention
- **WHEN** creating tags
- **THEN** use format `vX.Y.Z` (with 'v' prefix)
- **AND** match version in pyproject.toml exactly
- **AND** ensure tag is annotated (not lightweight)

### Requirement: ComfyUI Registry Publishing
The project SHALL publish to ComfyUI Registry only after successful local testing and git tagging.

#### Scenario: Publish to registry
- **WHEN** all local tests pass
- **THEN** ensure git tag exists for version
- **AND** ensure CHANGELOG is updated
- **AND** push tag to GitHub
- **AND** ComfyUI Manager will auto-detect the new version
- **AND** verify listing appears in ComfyUI Manager

#### Scenario: Registry update timing
- **WHEN** publishing to registry
- **THEN** publish within 24 hours of git tag creation
- **AND** monitor for user-reported issues first 48 hours
- **AND** be prepared to publish hotfix if critical bugs found

### Requirement: Rollback Procedure
The project SHALL have a defined procedure for rolling back problematic releases.

#### Scenario: Hotfix for critical bugs
- **WHEN** critical bug is found in released version
- **THEN** create hotfix branch from release tag
- **AND** fix bug with minimal changes
- **AND** increment patch version
- **AND** test thoroughly in ComfyUI
- **AND** publish hotfix within 24 hours

#### Scenario: Yanking broken releases
- **WHEN** release has breaking bugs that can't be quickly fixed
- **THEN** document issue in CHANGELOG
- **AND** recommend users downgrade to previous version
- **AND** provide clear migration instructions
- **AND** publish fixed version as soon as possible

### Requirement: Release Checklist
The project SHALL maintain a pre-release checklist to ensure quality.

#### Scenario: Pre-release verification
- **WHEN** preparing to release
- **THEN** verify all of:
  - Version updated in pyproject.toml
  - CHANGELOG updated with release notes
  - All tests passing
  - Local ComfyUI testing completed
  - Documentation updated
  - Git tag created
  - No untracked files in repository
- **AND** only proceed if all checks pass

#### Scenario: Post-release verification
- **WHEN** release is published
- **THEN** verify:
  - Tag is visible on GitHub
  - ComfyUI Manager shows new version
  - Installation instructions work
  - Example workflows load correctly
- **AND** monitor issue tracker for problems

### Requirement: Development vs Release Workflow
The project SHALL distinguish between development commits and release publishing.

#### Scenario: Continuous development
- **WHEN** developing features
- **THEN** commit to `main` branch frequently
- **AND** no need to publish every commit
- **AND** maintain working state in `main`

#### Scenario: Release publishing
- **WHEN** ready to publish to users
- **THEN** create release branch
- **AND** update version and changelog
- **AND** perform full testing cycle
- **AND** create git tag
- **AND** publish to ComfyUI Registry
- **AND** announce release if major changes

### Requirement: Testing Requirements Per Release Type
The project SHALL define different testing requirements based on release type.

#### Scenario: Major version testing
- **WHEN** releasing major version (breaking changes)
- **THEN** test all workflows from scratch
- **AND** test migration from previous version
- **AND** update all documentation
- **AND** provide migration guide
- **AND** test with multiple ComfyUI versions

#### Scenario: Minor version testing
- **WHEN** releasing minor version (new features)
- **THEN** test new features thoroughly
- **AND** regression test existing features
- **AND** update relevant documentation
- **AND** test with latest ComfyUI version

#### Scenario: Patch version testing
- **WHEN** releasing patch version (bug fixes)
- **THEN** test that bug is fixed
- **AND** basic smoke test of major features
- **AND** document fix in CHANGELOG
- **AND** can skip extensive testing if fix is isolated
