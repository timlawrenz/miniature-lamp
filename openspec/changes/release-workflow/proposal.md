## Why

Currently there's no defined process for:
- Creating and testing releases locally before publishing
- Managing version branches (stable vs development)
- Publishing to ComfyUI Registry consistently
- Testing changes in actual ComfyUI environments before release

This leads to uncertainty about when/how to publish and risks releasing untested code.

## What Changes

Define a comprehensive release workflow that specifies:
- Branch strategy (main, release branches, feature branches)
- Version numbering and tagging conventions
- Local testing procedures before publishing
- ComfyUI Registry publishing process and timing
- Rollback procedures if issues are found

**BREAKING**: None - this is a new process definition

## Impact

- **Affected specs**: None (new capability)
- **Affected code**: No code changes, only process definition
- **Benefits**: 
  - Clear release process reduces publishing errors
  - Local testing catches issues before users see them
  - Consistent versioning and changelogs
  - Confidence in when/how to publish
