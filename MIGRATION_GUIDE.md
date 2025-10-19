# MCP Server Public Repository Migration Guide

This guide walks you through migrating the MCP server code from the private repository to the public GitHub repository.

## Overview

**From:** `C:\jujusec\mcp-server` (private repo)
**To:** `C:\github\metric-duck\mcp-server` (public repo)
**GitHub URL:** https://github.com/metric-duck/mcp-server

## Pre-Migration Checklist

✅ Security audit completed - no secrets found in source code
✅ GitHub repository created: `github.com/metric-duck/mcp-server`
✅ Local directory created: `C:\github\metric-duck\mcp-server`
✅ Public repo files prepared (LICENSE, .gitignore, README.md, pyproject.toml)

## Files Already in Public Repo

The following files have been created in `C:\github\metric-duck\mcp-server`:

- ✅ `LICENSE` - MIT License
- ✅ `.gitignore` - Comprehensive Python/MCP exclusions
- ✅ `README.md` - Public-ready documentation
- ✅ `pyproject.toml` - Package metadata with GitHub URLs
- ✅ `MIGRATION_GUIDE.md` - This file

## Step-by-Step Migration

### Step 1: Copy Source Code

Copy the following directories from `C:\jujusec\mcp-server` to `C:\github\metric-duck\mcp-server`:

```bash
# Navigate to private repo
cd C:\jujusec\mcp-server

# Copy source code
xcopy /E /I src C:\github\metric-duck\mcp-server\src

# Copy tests
xcopy /E /I tests C:\github\metric-duck\mcp-server\tests

# Copy scripts (optional - for development)
xcopy /E /I scripts C:\github\metric-duck\mcp-server\scripts
```

**Linux/Mac equivalent:**
```bash
cp -r src C:/github/metric-duck/mcp-server/
cp -r tests C:/github/metric-duck/mcp-server/
cp -r scripts C:/github/metric-duck/mcp-server/
```

### Step 2: Copy Additional Files

```bash
# Copy .env.example (safe template)
copy .env.example C:\github\metric-duck\mcp-server\.env.example

# Copy requirements files
copy requirements.txt C:\github\metric-duck\mcp-server\requirements.txt
copy requirements-dev.txt C:\github\metric-duck\mcp-server\requirements-dev.txt
```

### Step 3: Security Review

Before committing, review these files for any hardcoded secrets:

```bash
cd C:\github\metric-duck\mcp-server

# Check for localhost:8951 references (should only be in .env.example)
findstr /S /I "localhost:8951" *

# Check for internal references
findstr /S /I "jujusec" *

# Check for API keys (should find none)
findstr /S /I "fda_" *
findstr /S /I "md_" *
```

**Expected results:**
- `localhost:8951` - Only in `.env.example` ✅
- `jujusec` - Should find nothing ✅
- API keys - Should find nothing ✅

### Step 4: Initialize Git Repository

```bash
cd C:\github\metric-duck\mcp-server

# Initialize git
git init

# Add .gitignore FIRST (important!)
git add .gitignore
git commit -m "chore: add .gitignore"

# Add LICENSE
git add LICENSE
git commit -m "chore: add MIT license"

# Add documentation
git add README.md MIGRATION_GUIDE.md
git commit -m "docs: add README and migration guide"

# Add package configuration
git add pyproject.toml .env.example requirements*.txt
git commit -m "build: add package configuration"

# Add source code
git add src/
git commit -m "feat: add MCP server implementation"

# Add tests
git add tests/
git commit -m "test: add test suite"

# Add scripts (optional)
git add scripts/
git commit -m "chore: add development scripts"
```

### Step 5: Connect to GitHub

```bash
# Add remote
git remote add origin https://github.com/metric-duck/mcp-server.git

# Verify remote
git remote -v

# Create main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 6: Verify on GitHub

1. Visit https://github.com/metric-duck/mcp-server
2. Check that all files are present
3. Verify README renders correctly
4. Check that LICENSE is detected (should show "MIT License" badge)
5. Review commit history for any sensitive data

### Step 7: Test Installation from GitHub

Test that users can install from the public repo:

```bash
# In a new directory
cd /tmp
python -m venv test-env
source test-env/bin/activate  # or test-env\Scripts\activate on Windows

# Install from GitHub
pip install git+https://github.com/metric-duck/mcp-server.git

# Test
python -m metricduck_mcp --help
```

### Step 8: Update Private Repo References

Update the private repo (`C:\jujusec`) to reference the public repo:

1. ✅ **Already done:** `/ai` page updated to `github.com/metric-duck/mcp-server`
2. Add `mcp-server/` to `.gitignore` in private repo
3. Delete `C:\jujusec\mcp-server` (after confirming public repo works)

```bash
cd C:\jujusec

# Add to .gitignore
echo "mcp-server/" >> .gitignore

# Commit the change
git add .gitignore web/src/app/ai/page.tsx
git commit -m "chore: update MCP server references to public repo"
```

### Step 9: Optional - Publish to PyPI

For easier installation (`pip install metricduck-mcp`):

1. Create PyPI account at https://pypi.org/account/register/
2. Generate API token at https://pypi.org/manage/account/token/
3. Build package:
   ```bash
   cd C:\github\metric-duck\mcp-server
   pip install build twine
   python -m build
   ```
4. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

## Post-Migration Checklist

- [ ] Public repo accessible at https://github.com/metric-duck/mcp-server
- [ ] README renders correctly on GitHub
- [ ] MIT License detected by GitHub
- [ ] Installation from GitHub works (`pip install git+https://github.com/...`)
- [ ] Private repo updated to reference public repo
- [ ] Private repo no longer has `mcp-server/` directory
- [ ] `/ai` page tested with correct GitHub URL
- [ ] (Optional) Published to PyPI for `pip install metricduck-mcp`

## Troubleshooting

### "Git remote already exists"

```bash
git remote remove origin
git remote add origin https://github.com/metric-duck/mcp-server.git
```

### "Permission denied" when pushing

1. Check GitHub authentication (SSH keys or Personal Access Token)
2. Verify repository permissions
3. Try HTTPS instead of SSH

### "Files too large" error

Check if any test fixtures or data files are too large. Move them to `.gitignore` if needed.

### Found secrets in git history

If you accidentally committed secrets:

```bash
# WARNING: This rewrites history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (dangerous - only for new repos)
git push origin --force --all
```

Better: Delete the repo and start fresh with proper .gitignore.

## Support

If you encounter issues during migration:

- **Email:** support@metricduck.com
- **Internal:** Check with dev team
- **GitHub Issues:** https://github.com/metric-duck/mcp-server/issues (for public issues)

## Next Steps

After successful migration:

1. Apply for Anthropic MCP Directory listing
2. Create GitHub Actions workflow for automated testing
3. Set up PyPI publishing workflow
4. Add contribution guidelines (CONTRIBUTING.md)
5. Create issue templates
6. Set up project board for feature tracking

---

**Migration prepared on:** 2025-01-XX
**GitHub Repository:** https://github.com/metric-duck/mcp-server
**License:** MIT
