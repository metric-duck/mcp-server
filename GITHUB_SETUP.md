# GitHub Repository Setup Guide

This guide walks you through configuring the GitHub repository after pushing code.

## Prerequisites

- GitHub repository created at `https://github.com/metric-duck/mcp-server`
- Code pushed to `main` branch
- PyPI account created (for publishing)

---

## 1. Repository Settings

### General Settings

1. Navigate to **Settings** → **General**
2. Configure:
   - **Description:** "Model Context Protocol server for MetricDuck API - AI-native financial data access"
   - **Website:** `https://metricduck.com`
   - **Topics:** `mcp`, `model-context-protocol`, `financial-data`, `sec`, `edgar`, `ai`, `claude`, `python`
   - **Features:**
     - ✅ Issues
     - ✅ Discussions (optional - for community support)
     - ❌ Projects (not needed yet)
     - ❌ Wiki (use docs/ folder instead)

### Branch Protection Rules

1. Navigate to **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Branch name pattern: `main`
4. Enable:
   - ✅ **Require a pull request before merging**
     - Required approvals: 1
     - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Status checks required:
       - `test (3.10)`
       - `test (3.11)`
       - `test (3.12)`
       - `lint`
       - `security`
   - ✅ **Require conversation resolution before merging**
   - ✅ **Do not allow bypassing the above settings** (unless you're sole maintainer)
5. Click **Create**

---

## 2. Secrets Configuration

### PyPI Publishing Secret

1. **Get PyPI API Token:**
   - Go to https://pypi.org/manage/account/token/
   - Create token with scope: "Entire account" (initially)
   - After first publish, create project-specific token for `metricduck-mcp`
   - Copy token (starts with `pypi-`)

2. **Add to GitHub:**
   - Navigate to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-AgE...` (paste your token)
   - Click **Add secret**

### Codecov Token (Optional but Recommended)

1. **Get Codecov Token:**
   - Go to https://codecov.io/
   - Sign in with GitHub
   - Add repository: `metric-duck/mcp-server`
   - Copy repository upload token

2. **Add to GitHub:**
   - Navigate to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `CODECOV_TOKEN`
   - Value: (paste token)
   - Click **Add secret**

---

## 3. GitHub Actions Configuration

### Enable Actions

1. Navigate to **Settings** → **Actions** → **General**
2. Under **Actions permissions:**
   - ✅ Allow all actions and reusable workflows
3. Under **Workflow permissions:**
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests
4. Click **Save**

### Verify Workflows

1. Navigate to **Actions** tab
2. You should see two workflows:
   - **CI** - Runs on every push/PR
   - **Publish to PyPI** - Runs on releases

3. Push a commit to trigger CI:
   ```bash
   cd C:\github\metric-duck\mcp-server
   git add .
   git commit -m "chore: add CI/CD workflows"
   git push
   ```

4. Check **Actions** tab - CI workflow should start automatically

---

## 4. Team and Access Management

### Create Team (if organization)

1. Navigate to organization → **Teams**
2. Create team: `mcp-maintainers`
3. Add members
4. Set repository access:
   - Repository: `metric-duck/mcp-server`
   - Role: **Maintain** or **Admin**

### Collaborator Access (if personal repo)

1. Navigate to **Settings** → **Collaborators**
2. Add collaborators with **Maintain** or **Write** access
3. Update `.github/CODEOWNERS` with their GitHub usernames

---

## 5. Release Configuration

### Create First Release

1. Update version in `pyproject.toml` (e.g., `0.3.0`)
2. Commit and push changes
3. Create git tag:
   ```bash
   git tag -a v0.3.0 -m "Release v0.3.0 - Initial public release"
   git push origin v0.3.0
   ```
4. Navigate to **Releases** → **Draft a new release**
5. Fill in:
   - **Tag:** `v0.3.0` (select existing tag)
   - **Title:** `v0.3.0 - Initial Public Release`
   - **Description:**
     ```markdown
     ## Features
     - 🔍 Smart company search with fuzzy matching
     - 📊 Company overview with 50+ financial metrics
     - 📈 Income statement (multi-period)
     - 💰 Balance sheet (multi-period)
     - 💵 Cash flow statement (multi-period)

     ## Installation
     ```bash
     pip install metricduck-mcp
     ```

     ## Documentation
     See [README.md](https://github.com/metric-duck/mcp-server#readme) for setup instructions.
     ```
6. Click **Publish release**
7. Check **Actions** tab - PyPI publish workflow should start

---

## 6. Security Configuration

### Enable Dependabot

1. Navigate to **Settings** → **Security** → **Code security and analysis**
2. Enable:
   - ✅ **Dependency graph** (should be enabled by default)
   - ✅ **Dependabot alerts**
   - ✅ **Dependabot security updates**
   - ✅ **Dependabot version updates** (optional - creates PRs for dep updates)

### Configure Dependabot Updates (Optional)

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "metric-duck/mcp-maintainers"
    labels:
      - "dependencies"
      - "automated"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    reviewers:
      - "metric-duck/mcp-maintainers"
    labels:
      - "dependencies"
      - "ci"
```

### Enable Secret Scanning

1. Navigate to **Settings** → **Security** → **Code security and analysis**
2. Enable:
   - ✅ **Secret scanning** (requires public repo or GitHub Advanced Security)
   - ✅ **Push protection** (prevents accidental secret commits)

---

## 7. Pre-commit Hooks Setup (Local Development)

Install pre-commit hooks for contributors:

```bash
cd C:\github\metric-duck\mcp-server

# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

## 8. Badges for README (Optional)

Add status badges to `README.md`:

```markdown
[![CI](https://github.com/metric-duck/mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/metric-duck/mcp-server/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/metricduck-mcp.svg)](https://badge.fury.io/py/metricduck-mcp)
[![Python Versions](https://img.shields.io/pypi/pyversions/metricduck-mcp.svg)](https://pypi.org/project/metricduck-mcp/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/metric-duck/mcp-server/blob/main/LICENSE)
```

---

## 9. Anthropic MCP Directory Submission

After repository is live and PyPI package is published:

1. Visit https://github.com/anthropics/mcp-directory
2. Fork the repository
3. Add entry to `servers.json`:
   ```json
   {
     "name": "metricduck",
     "displayName": "MetricDuck Financial Data",
     "description": "Access comprehensive financial data from SEC filings with 50+ metrics for 6,500+ companies. Includes company search, financial statements, and fundamental analysis.",
     "author": "MetricDuck Team",
     "sourceUrl": "https://github.com/metric-duck/mcp-server",
     "homepage": "https://metricduck.com",
     "license": "MIT",
     "categories": ["finance", "data", "analytics"],
     "install": {
       "pip": "metricduck-mcp"
     },
     "authentication": {
       "type": "oauth2",
       "authUrl": "https://metricduck.com/mcp/auth",
       "documentation": "https://metricduck.com/docs/mcp/authentication"
     }
   }
   ```
4. Create pull request
5. Wait for Anthropic team review (typically 1-2 weeks)

---

## 10. Post-Setup Verification

### Checklist

- [ ] CI workflow runs successfully on push
- [ ] Security workflow runs without critical vulnerabilities
- [ ] Branch protection prevents direct pushes to `main`
- [ ] PyPI secret configured (test with a pre-release if possible)
- [ ] Pre-commit hooks work locally
- [ ] Issue templates appear when creating new issues
- [ ] PR template appears when creating pull requests
- [ ] Release workflow tested (optional: create v0.3.0-rc1 pre-release)

### Test Commands

```bash
# Clone fresh to test
cd /tmp
git clone https://github.com/metric-duck/mcp-server.git
cd mcp-server

# Test installation
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .[dev]

# Run tests
pytest

# Test pre-commit
pre-commit run --all-files
```

---

## Troubleshooting

### CI Failing

**Check:**
- Python version compatibility (3.10, 3.11, 3.12)
- Missing dependencies in `pyproject.toml`
- Test fixtures in `tests/` directory

**Fix:**
```bash
# Run tests locally
pytest -v

# Check coverage
pytest --cov=metricduck_mcp --cov-report=term
```

### PyPI Publishing Fails

**Common Issues:**
- Token not configured: Add `PYPI_API_TOKEN` secret
- Version already exists: Bump version in `pyproject.toml`
- Tag mismatch: Ensure git tag matches package version

**Fix:**
```bash
# Check current version
python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# Create matching tag
git tag v0.3.0
git push origin v0.3.0
```

### Security Scan False Positives

**Review findings:**
1. Navigate to **Security** → **Code scanning**
2. Review each alert
3. Dismiss false positives with reason
4. Fix real vulnerabilities

---

## Support

**Issues?**
- Email: support@metricduck.com
- GitHub Issues: https://github.com/metric-duck/mcp-server/issues

---

**Last Updated:** 2025-01-XX
