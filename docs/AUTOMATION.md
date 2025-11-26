# Automation Guide

This document describes all automated workflows configured for msgspec-ext.

## 🤖 Configured Automations

### 1. **Dependabot** - Dependency Updates

**File**: `.github/dependabot.yml`

**What it does**:
- Automatically checks for dependency updates weekly (Mondays at 9am UTC)
- Creates PRs for Python dependencies and GitHub Actions
- Groups OpenTelemetry packages together
- Groups dev dependencies by type (minor/patch)

**Labels**: `dependencies`, `python`, `github-actions`

**Configuration**:
- Max 10 PRs for Python deps
- Max 5 PRs for GitHub Actions
- Auto-labeled with `automerge` for automated merging

---

### 2. **Pre-commit Auto-update** - Hook Updates

**File**: `.github/workflows/pre-commit-autoupdate.yml`

**What it does**:
- Runs `pre-commit autoupdate` weekly (Mondays at 9am UTC)
- Creates PR with updated hook versions
- Automatically labeled with `automerge`

**Triggers**:
- Schedule: Weekly (Mondays)
- Manual: `workflow_dispatch`

---

### 3. **Merge Bot** - Command-based PR Merging

**File**: `.github/workflows/merge-bot.yml`

**What it does**:
- Merges PRs via comment commands (PyTorch-style)
- Updates PR branches with latest changes from base branch
- Waits up to 10 minutes for CI checks to pass
- Checks user permissions (write/admin only)
- Uses squash merge
- Deletes branch after merge
- Interactive feedback with emoji reactions

**Commands**:

**Merge Commands**:
- `@mergebot merge`
- `@merge-bot merge`
- `/merge`
- `merge`

**Update Commands** (new in v1.0.0):
- `@mergebot update`
- `@merge-bot update`
- `/update`
- `update`

#### How to Use the Merge Bot

**Option 1: Mention the bot**
```
@mergebot merge
```
or
```
@merge-bot merge
```

**Option 2: Simple command**
```
/merge
```
or simply:
```
merge
```

**What happens when you merge:**
1. Bot reacts with 🚀 - Shows it's processing
2. **Checks permissions** - Only collaborators with write/admin can merge
3. **Checks if PR is ready** - Can't be draft, can't have conflicts
4. **Waits for checks** - Waits up to 10 minutes for CI, tests, CodeQL, etc.
5. **Merges PR** - Uses squash merge
6. **Deletes branch** - Removes branch automatically
7. Bot reacts with 👍 - Confirms success

**Update Command Usage:**

Use `/update` or `@mergebot update` to update your PR branch with the latest changes from the base branch (usually `main`). This is useful when your PR is behind the base branch.

**What happens when you update:**
1. Bot reacts with 👀 - Shows it's processing
2. **Checks permissions** - Only collaborators with write/admin can update
3. **Merges base branch** - Merges latest changes from base into PR branch
4. **Pushes changes** - Automatically pushes to your PR branch
5. **Comments with status** - Confirms success or failure
6. Bot reacts with 👍 (success) or 👎 (failure)

**Example:**
```
# PR is behind main branch

# You comment:
/update

# Bot merges main into your PR branch
# Bot comments: "✅ Branch updated successfully by @username!"
```

**Requirements:**
- ✅ You must have **write** or **admin** access to the repo
- ✅ PR cannot be a draft (for merge)
- ✅ PR cannot have conflicts (for merge)
- ✅ All checks must pass (or bot waits up to 10 min for merge)

**Error Messages:**

**❌ No permission**
```
❌ @user you don't have permission to merge/update PRs.
Only collaborators with write access can use these commands.
```
**Solution**: Ask a maintainer.

**❌ PR is draft**
```
❌ Cannot merge: PR is still a draft.
Please mark it as ready for review first.
```
**Solution**: Click "Ready for review" on the PR.

**❌ Conflicts**
```
❌ Cannot merge: PR has conflicts or is not mergeable.
Please resolve conflicts first.
```
**Solution**: Resolve conflicts manually.

**❌ Checks failed**
```
❌ Cannot merge: The following checks failed:
- ❌ Ruff Lint & Format
- ❌ Test Python 3.10
Please fix the issues and try again.
```
**Solution**: Fix errors and push again.

**❌ Update conflicts**
```
❌ Failed to update branch with latest changes from `main`.

This usually means there are merge conflicts that need to be resolved manually.
```
**Solution**: Merge main locally and resolve conflicts.

**⏱️ Timeout**
```
⏱️ Timeout waiting for checks to complete (waited 10 minutes).
You can try the merge command again once checks complete.
```
**Solution**: Wait for checks to complete and try again.

**Security:**
- 🔒 Only collaborators with **write access** can use commands
- 🔒 Respects branch protection rules
- 🔒 Waits for all required checks
- 🔒 Cannot merge PRs with conflicts
- 🔒 Cannot merge drafts

---

### 4. **Stale Bot** - Issue/PR Cleanup

**File**: `.github/workflows/stale.yml`

**What it does**:
- Marks issues as stale after 60 days of inactivity
- Closes stale issues after 7 days
- Marks PRs as stale after 30 days
- Closes stale PRs after 14 days
- Removes stale label when updated

**Exempt labels**: `keep-open`, `bug`, `security`, `enhancement`, `help-wanted`, `in-progress`, `work-in-progress`

**Triggers**:
- Schedule: Daily at midnight UTC
- Manual: `workflow_dispatch`

---

### 5. **Label Automation** - Auto-labeling

**Files**:
- `.github/workflows/labeler.yml`
- `.github/labeler.yml`

**What it does**:
- **File-based labeling**: Labels based on changed files (sdk, core, tests, docs, ci, dependencies, examples)
- **Size labeling**: Adds size labels (XS/S/M/L/XL) based on line changes
- **Title-based labeling**: Detects conventional commit prefixes (feat, fix, docs, etc.)
- **Keyword detection**: Detects breaking changes, security issues

**Labels added automatically**:
- `sdk`, `core`, `tests`, `documentation`, `ci`, `dependencies`, `examples`
- `size/XS`, `size/S`, `size/M`, `size/L`, `size/XL`
- `enhancement`, `bug`, `maintenance`, `refactor`, `performance`
- `breaking-change`, `security`

---

### 6. **CodeQL Security Scanning**

**File**: `.github/workflows/codeql.yml`

**What it does**:
- Scans Python code for security vulnerabilities
- Runs on pushes to main, PRs, and weekly schedule
- Uses `security-extended` queries for comprehensive checking
- Reports findings in Security tab

**Triggers**:
- Push to main
- Pull requests
- Schedule: Weekly (Mondays at 3am UTC)

**Results**: View in GitHub Security tab

---

### 7. **Release Drafter** - Draft Release Notes

**Files**:
- `.github/workflows/release-drafter.yml`
- `.github/release-drafter.yml`

**What it does**:
- Automatically drafts release notes based on merged PRs
- Categorizes changes by type (Features, Bug Fixes, Docs, etc.)
- Suggests version bump (major/minor/patch) based on labels
- Lists contributors

**Categories**:
- 🚀 Features (`enhancement`, `feat`)
- 🐛 Bug Fixes (`bug`, `fix`)
- 📚 Documentation (`documentation`, `docs`)
- 🧪 Tests (`tests`, `test`)
- ⚡ Performance (`performance`, `perf`)
- 🔧 Maintenance (`maintenance`, `chore`)
- 🔐 Security (`security`)
- 📦 Dependencies (`dependencies`)

**View**: Check GitHub Releases page for draft

---

### 8. **Changelog Generator** - Auto-update CHANGELOG

**File**: `.github/workflows/changelog.yml`

**What it does**:
- Automatically updates CHANGELOG.md when PRs are merged
- Adds entry under appropriate section (Added/Fixed/Changed/etc.)
- Includes PR title and number
- Commits directly to main

**Sections**:
- Added (features)
- Fixed (bug fixes)
- Changed (modifications)
- Security (security fixes)
- Deprecated
- Removed

**Triggers**: When PR is closed and merged to main

---

## 🎯 Workflow Summary

| Workflow | Trigger | Frequency | Auto-action |
|----------|---------|-----------|-------------|
| Dependabot | Schedule | Weekly (Mon 9am) | Creates PRs |
| Pre-commit update | Schedule | Weekly (Mon 9am) | Creates PRs |
| Merge Bot | PR comment | On command | Merges PRs |
| Stale bot | Schedule | Daily | Closes stale items |
| Labeler | PR open/update | On PR | Adds labels |
| CodeQL | Push/PR/Schedule | Weekly (Mon 3am) | Security scan |
| Release Drafter | Push to main | On push | Drafts release |
| Changelog | PR merged | On merge | Updates CHANGELOG |

---

## 🏷️ Important Labels

- `keep-open` - Prevents stale bot from closing
- `dependencies` - Dependency updates
- `breaking-change` - Triggers major version bump
- `security` - Security-related changes
- `size/XS`, `size/S`, `size/M`, `size/L`, `size/XL` - PR size indicators

---

## 🚀 Usage Examples

### Merge a PR with bot
```bash
# Comment on PR:
@mergebot merge
# or
/merge
```

### Prevent stale bot from closing
```bash
gh issue edit <issue-number> --add-label "keep-open"
```

### Trigger pre-commit update manually
```bash
gh workflow run pre-commit-autoupdate.yml
```

---

## 📊 Monitoring

- **CI Status**: Check Actions tab for workflow runs
- **Security**: Check Security tab for CodeQL findings
- **Dependencies**: Check Pull Requests for Dependabot updates
- **Release Notes**: Check Releases page for draft release notes

---

## ⚙️ Configuration Files

All automation configurations are in `.github/`:

```
.github/
├── dependabot.yml              # Dependency updates
├── labeler.yml                 # File-based labeling rules
├── release-drafter.yml         # Release notes configuration
└── workflows/
    ├── merge-bot.yml           # Merge bot (command-based)
    ├── changelog.yml           # Changelog updates
    ├── codeql.yml              # Security scanning
    ├── labeler.yml             # Label automation
    ├── pre-commit-autoupdate.yml  # Pre-commit updates
    ├── release-drafter.yml     # Release drafter
    └── stale.yml               # Stale bot
```

---

## 🔧 Customization

To customize automations, edit the respective configuration files and commit changes. Most workflows support manual triggers via `workflow_dispatch`.

---

## 📝 Best Practices

1. **Use conventional commits** for automatic changelog updates
2. **Use merge bot commands** to merge PRs after CI passes
3. **Use `keep-open` label** for long-running issues/PRs
4. **Review Dependabot PRs** before merging (check breaking changes)
5. **Check CodeQL findings** regularly in Security tab
