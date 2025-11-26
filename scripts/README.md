# Scripts

Automation scripts for msgspec-ext repository management.

## Release Automation

Automated script to bump version, update changelog, and create release PR.

### Prerequisites

1. **Be on main branch** with clean working directory
2. **Have GitHub CLI authenticated** (`gh auth login`)
3. **Have PyPI trusted publishing configured** (already done)

### Usage

```bash
# Create release PR for version 0.12.4
./scripts/release.sh 0.12.4

# Create release PR for version 1.0.0
./scripts/release.sh 1.0.0
```

### What It Does

1. **Validates environment:**
   - Checks you're on main branch
   - Ensures working directory is clean
   - Pulls latest changes

2. **Validates version:**
   - Must be in X.Y.Z format
   - Must be greater than current version

3. **Updates files:**
   - `src/msgspec_ext/version.py` - Sets `__version__`
   - `CHANGELOG.md` - Adds release section with date

4. **Security validation:**
   - Verifies ONLY `version.py` and `CHANGELOG.md` were modified
   - Aborts if any other files changed

5. **Creates release branch:**
   - Branch name: `release/v0.12.4`
   - Commits changes with detailed message

6. **Creates Pull Request:**
   - Title: "Release v0.12.4"
   - Labels: `release`, `automerge`
   - Includes release notes and merge instructions

7. **Merge the PR manually** (important!):
   ```bash
   # Wait for all CI checks to pass, then:
   gh pr merge <number> --squash --delete-branch
   # Or use GitHub UI: "Squash and merge"
   ```

   **⚠️ Note**: Release PRs must be merged **manually** (not via merge bot) to trigger the `publish.yml` workflow. This is due to GitHub Actions security limitations with `GITHUB_TOKEN`.

8. **After PR is merged:**
   - `publish.yml` workflow triggers automatically
   - Package is built and validated
   - Git tag `v0.12.4` is created
   - Package is published to PyPI
   - GitHub Release is created

### Example Session

```bash
$ ./scripts/release.sh 0.12.4
🚀 msgspec-ext Release Automation

📥 Pulling latest changes...
Already up to date.
📦 Current version: 0.12.3
🎯 Releasing version: 0.12.3 → 0.12.4

📝 Updating files...
   → src/msgspec_ext/version.py
   → CHANGELOG.md

🔒 Security validation...
✅ Security validation passed
   Only version.py and CHANGELOG.md were modified

🌿 Creating release branch: release/v0.12.4
💾 Committing changes...
📤 Pushing release branch...
🔀 Creating pull request...

✅ Release PR created successfully!

📋 Next steps:
   1. Review the PR: https://github.com/msgflux/msgspec-ext/pull/42
   2. Wait for CI checks to pass (including security validation)
   3. Merge using: @mergebot merge
   4. After merge, publish.yml will deploy to PyPI automatically

🔗 Quick links:
   PR: https://github.com/msgflux/msgspec-ext/pull/42
   CI: https://github.com/msgflux/msgspec-ext/actions

⚠️  Note: The release will NOT be published until the PR is merged
```

### Security Features

🔒 **Multi-layer security validation:**

1. **Clean working directory check**
   - Script refuses to run if there are uncommitted changes
   - Prevents accidental/malicious code injection during releases

2. **File modification validation**
   - After updating files, script verifies ONLY these were modified:
     - `src/msgspec_ext/version.py`
     - `CHANGELOG.md`
   - If ANY other file is modified, release is ABORTED
   - Protects against script compromise or malfunction

3. **Version validation**
   - New version must be greater than current version
   - Prevents accidental downgrades

4. **Branch protection with enforce_admins=true**
   - Even owners must use PRs - no direct push to main
   - Required CI checks must pass before merge
   - All changes logged in git history with clear audit trail

5. **GitHub Actions validation**
   - Server-side validation runs automatically on release PRs
   - Cannot be bypassed by modifying local script
   - Ensures integrity even if local environment is compromised

**Why this matters:**
- Prevents supply chain attacks
- Ensures releases are exactly what they claim to be
- Provides audit trail of all changes
- Protects package integrity on PyPI
- PR-based releases make it clear who initiated each release

### Notes

- ✅ **Everyone uses PRs** - Including repository owners for maximum security
- ✅ **Multi-layer security validation** - Both local and server-side
- ✅ **Automatic rollback** on any error or security violation
- ✅ **Clear audit trail** - Every release has a PR showing exactly what changed
- ⚠️  **PyPI releases are permanent** - can't delete/overwrite versions

### Troubleshooting

**"Error: Must be on main branch"**
```bash
git checkout main
```

**"Error: Working directory is not clean"**
```bash
git status
git stash  # or commit changes
```

**"Error creating PR" or "gh: command not found"**
- Install GitHub CLI: `sudo apt install gh` or https://cli.github.com
- Authenticate: `gh auth login`

**"CI checks failing on release PR"**
- Check GitHub Actions: https://github.com/msgflux/msgspec-ext/actions
- Common issues:
  - Security validation failed (unexpected files modified)
  - Version downgrade detected
  - Test failures

**"Workflow failed: version downgrade detected"**
- Check CHANGELOG.md wasn't manually edited
- Ensure version.py has correct current version

---

## Setup Branch Protection

Automatically configure branch protection rules for the `main` branch using GitHub best practices.

### Prerequisites

1. **Install GitHub CLI:**
   ```bash
   # Ubuntu/Debian
   sudo apt install gh

   # macOS
   brew install gh

   # Or download from: https://cli.github.com/
   ```

2. **Authenticate:**
   ```bash
   gh auth login
   # Follow prompts to authenticate with GitHub
   ```

### Usage

```bash
cd /home/vilson-neto/Documents/msg-projects/msgspec-ext
./scripts/setup-branch-protection.sh
```

### What It Configures

The script applies these **best practices** from major OSS projects (PyTorch, TensorFlow, etc.):

#### ✅ Pull Request Requirements
- **Require PR before merging** - No direct pushes to main (enforced for everyone)
- **Require approvals: 0** - You can self-merge, but must create PR first
- **Dismiss stale reviews** - New commits invalidate old approvals
- **Enforce for admins: true** - Even repository owners must follow all rules

#### ✅ Status Checks (CI/CD)
- **Require checks to pass** - All tests must pass before merge
- **Required checks** (using correct workflow names):
  - `CI / Ruff Lint & Format` - Code linting and formatting
  - `CI / Test Python 3.10` - Test suite on Python 3.10
  - `CI / Test Python 3.11` - Test suite on Python 3.11
  - `CI / Test Python 3.12` - Test suite on Python 3.12
  - `CI / Test Python 3.13` - Test suite on Python 3.13
  - `CI / Build distribution` - Package build
- **Require branches up-to-date** - Must rebase on latest main

#### ✅ History & Safety
- **Require linear history** - No merge commits, cleaner git log
- **Require conversation resolution** - All PR comments must be resolved
- **✅ Enforce for admins: true** - Even owners must use PRs (maximum security)
- **No force pushes** - Prevents accidental history rewrite
- **No deletions** - Prevents accidental branch deletion

#### 👤 Permissions
- **Repository Owners:** Must create PRs for ALL changes (including releases)
- **Maintainers:** Must create PRs and wait for approvals
- **Contributors:** Must create PRs and wait for approvals

### After Running

You'll see output like:
```
✅ Branch protection configured successfully!

📋 Applied rules:
   ✅ Require pull request before merging
   ✅ Require status checks to pass (test, lint, build)
   ✅ Require branches to be up to date
   ✅ Require linear history (no merge commits)
   ...
```

### Verify Configuration

Visit: https://github.com/msgflux/msgspec-ext/settings/branches

You should see:
- Branch name pattern: `main`
- Branch protection rules: ✅ Active
- Status checks: `test`, `lint`, `build`

### Customizing Rules

To customize branch protection rules, edit the JSON input in `setup-branch-protection.sh`:

```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1  // Require 1 approval
  },
  "enforce_admins": false  // Allow admin bypass (not recommended)
}
```

### Troubleshooting

#### "gh: command not found"
Install GitHub CLI: https://cli.github.com/manual/installation

#### "HTTP 403: Resource not accessible by integration"
You need admin access to the repository.

#### "Required status checks not found"
The status checks (`test`, `lint`, `build`) need to run at least once before they can be required. They'll run automatically when CI runs on a PR.

#### Want to temporarily disable protection?
```bash
# Disable (use with caution!)
gh api -X DELETE "/repos/msgflux/msgspec-ext/branches/main/protection"

# Re-enable
./scripts/setup-branch-protection.sh
```

### Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Contributing Guide](../CONTRIBUTING.md) - See development workflow and best practices
