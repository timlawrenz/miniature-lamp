# ComfyUI Registry Publishing Guide

This guide documents how to officially register and publish this custom node to the ComfyUI Registry (which powers ComfyUI Manager).

**Source**: https://docs.comfy.org/registry/publishing

## Overview

The ComfyUI Registry is the official system for distributing custom nodes. Once published, users can install your node directly through ComfyUI Manager.

## Prerequisites

- [ ] Custom node is working and tested
- [ ] `comfy-cli` installed (`pip install comfy-cli`)
- [ ] GitHub repository is public
- [ ] `LICENSE.txt` file exists in repository

## Step 1: Create a Publisher Account

1. Go to https://registry.comfy.org/
2. Create a publisher account
3. Choose your **Publisher ID** (globally unique, cannot be changed)
   - Example: `@yourpublisher`
   - This will be used in URLs: `https://registry.comfy.org/@yourpublisher/node-name`
4. Note your Publisher ID from your profile page (after the `@` symbol)

## Step 2: Create Registry Publishing API Key

**Important**: This is different from API keys for using paid nodes in workflows.

1. Go to your publisher profile: https://registry.comfy.org/
2. Click on your publisher name
3. Click "Create API Key"
4. Name the key (e.g., "GitHub Actions" or "CLI Publishing")
5. **Save the key securely** - you cannot retrieve it later

## Step 3: Add Metadata to Repository

### Generate pyproject.toml

Run this command in your repository root:

```bash
comfy node init
```

### Example pyproject.toml Structure

```toml
# pyproject.toml
[project]
name = "comfyui-dino-flux-upscale"  # Unique identifier (immutable after creation)
description = "DINO-guided FLUX upscaler for ComfyUI with semantic-aware image enhancement"
version = "1.0.0"  # Must follow semantic versioning
license = { file = "LICENSE.txt" }
dependencies = [
    "torch>=2.0.0",
    "diffusers>=0.25.0",
    "transformers>=4.35.0",
    "accelerate>=0.25.0",
    "pillow>=10.0.0"
]

[project.urls]
Repository = "https://github.com/timlawrenz/miniature-lamp"

[tool.comfy]
PublisherId = "@yourpublisher"  # Your Publisher ID from registry
DisplayName = "DINO FLUX Upscale"  # Display name (can be changed later)
Icon = "https://example.com/icon.png"  # Optional: SVG, PNG, JPG, GIF (max 800x400px)
```

### Key Fields Explained

- **name**: Unique identifier, cannot change after first publish
- **version**: Semantic versioning (MAJOR.MINOR.PATCH)
- **PublisherId**: Your publisher ID from the registry
- **DisplayName**: What users see in ComfyUI Manager
- **Icon**: Optional branding image

### Specifications

See full specification: https://docs.comfy.org/registry/pyproject-toml

## Step 4: Publish to Registry

### Option 1: Manual Publishing with CLI

**First time setup:**

```bash
comfy node publish
```

You'll be prompted for your API key:

```
API Key for publisher '@yourpublisher': ****************************************
```

**Note**: When pasting on Windows with CTRL+V, the key may have `\x16` appended. Use right-click paste instead.

**Success output:**

```
...Version 1.0.0 Published.
See it here: https://registry.comfy.org/@yourpublisher/node-name
```

### Option 2: Automated Publishing with GitHub Actions

**Step 1: Add GitHub Secret**

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Secrets and Variables** → **Actions**
3. Under **Repository secrets**, click **New Repository Secret**
4. Name: `REGISTRY_ACCESS_TOKEN`
5. Value: Your API key from Step 2

**Step 2: Create GitHub Action**

Create file: `.github/workflows/publish_action.yml`

```yaml
name: Publish to Comfy registry
on:
  workflow_dispatch:
  push:
    branches:
      - main  # Change to 'master' if that's your default branch
    paths:
      - "pyproject.toml"

jobs:
  publish-node:
    name: Publish Custom Node to registry
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4
      - name: Publish Custom Node
        uses: Comfy-Org/publish-node-action@main
        with:
          personal_access_token: ${{ secrets.REGISTRY_ACCESS_TOKEN }}
```

**Step 3: Test the Action**

1. Update version in `pyproject.toml` (e.g., `1.0.0` → `1.0.1`)
2. Commit and push to main branch
3. Check **Actions** tab on GitHub to see if it ran successfully
4. Verify on https://registry.comfy.org/

**How it works:**
- Triggers automatically when `pyproject.toml` is modified
- Can also be triggered manually via "workflow_dispatch"

## Version Management

### Semantic Versioning Rules

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Publishing Updates

1. Update version number in `pyproject.toml`
2. Commit changes
3. Push to trigger GitHub Action (or run `comfy node publish` manually)

## Installation by Users

Once published, users can install via ComfyUI Manager:

1. Open ComfyUI
2. Click **Manager** button
3. Search for "DINO FLUX Upscale"
4. Click **Install**
5. Restart ComfyUI

## Troubleshooting

### API Key Issues

- **Problem**: Key has `\x16` appended
- **Solution**: Use right-click paste instead of CTRL+V

### Version Already Exists

- **Problem**: "Version X.X.X already published"
- **Solution**: Increment version number in `pyproject.toml`

### GitHub Action Not Triggering

- **Problem**: Action doesn't run on push
- **Solution**: Check branch name matches (main vs master)

### Missing Dependencies

- **Problem**: Users report missing packages
- **Solution**: Update `dependencies` in `pyproject.toml`

## Pre-Publication Checklist

- [ ] Repository is public on GitHub
- [ ] `LICENSE.txt` file exists
- [ ] `pyproject.toml` is properly configured
- [ ] `README.md` has usage instructions
- [ ] Node has been tested locally in ComfyUI
- [ ] All dependencies are listed
- [ ] Version number follows semantic versioning
- [ ] Publisher account created
- [ ] API key generated and saved securely
- [ ] GitHub secret configured (if using Actions)

## Resources

- **ComfyUI Registry**: https://registry.comfy.org/
- **Publishing Documentation**: https://docs.comfy.org/registry/publishing
- **pyproject.toml Spec**: https://docs.comfy.org/registry/pyproject-toml
- **Video Tutorial**: Available on docs.comfy.org
- **Standards**: https://docs.comfy.org/registry/standards

## Next Steps

After initial publication:

1. Monitor user feedback and issues on GitHub
2. Publish updates regularly with bug fixes and improvements
3. Keep dependencies up to date
4. Update documentation as needed
5. Consider adding example workflows to repository

## Notes

- Publisher ID is **permanent** - choose wisely
- Node name is **immutable** after first publish
- DisplayName and Icon can be changed in updates
- First publication may take a few minutes to appear in registry
- Updates are instant once published
