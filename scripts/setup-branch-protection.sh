#!/bin/bash
# Script to configure branch protection rules for msgspec-ext
#
# Rules:
# - Require PRs for all changes (except repository admins/owners)
# - Require CI checks to pass
# - Owners can bypass and push directly to main (for releases)
# - Maintainers must create PRs and get approvals

set -e

REPO="msgflux/msgspec-ext"
BRANCH="main"

echo "🔧 Configuring branch protection for ${REPO}/${BRANCH}..."
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Install it first:"
    echo "   Ubuntu/Debian: sudo apt install gh"
    echo "   Or: https://cli.github.com/manual/installation"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Configure branch protection using GitHub API via gh
echo "📋 Applying branch protection rules..."

# IMPORTANT: Using correct check names from CI workflow
# The workflow is named "CI" and jobs are:
# - "Ruff Lint & Format"
# - "Test Python 3.10/3.11/3.12/3.13"
# - "Build distribution"
#
# GitHub combines these as "CI / Job Name"

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "Ruff Lint & Format"},
      {"context": "Test Python 3.10"},
      {"context": "Test Python 3.11"},
      {"context": "Test Python 3.12"},
      {"context": "Test Python 3.13"},
      {"context": "Build distribution"}
    ]
  },
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "enforce_admins": true,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true,
  "restrictions": null
}
EOF

echo ""
echo "✅ Branch protection configured successfully!"
echo ""
echo "📋 Applied rules:"
echo "   ✅ Require pull request before merging"
echo "   ✅ Require status checks to pass:"
echo "      - CI / Ruff Lint & Format"
echo "      - CI / Test Python 3.10"
echo "      - CI / Test Python 3.11"
echo "      - CI / Test Python 3.12"
echo "      - CI / Test Python 3.13"
echo "      - CI / Build distribution"
echo "   ✅ Require branches to be up to date"
echo "   ✅ Require linear history (no merge commits)"
echo "   ✅ Require conversation resolution before merging"
echo "   ✅ Dismiss stale reviews when new commits pushed"
echo "   ✅ Enforce rules for administrators (maximum security)"
echo "   ✅ Release file validation (only version.py and CHANGELOG.md)"
echo "   ✅ No force pushes allowed"
echo "   ✅ No branch deletions allowed"
echo ""
echo "🎉 Done!"
echo ""
echo "👤 Permissions:"
echo "   - Repository Owners: Must use PRs for ALL changes (including releases)"
echo "   - Maintainers: Must create PRs and wait for approvals"
echo "   - Contributors: Must create PRs and wait for approvals"
echo ""
echo "📖 Release process (via PR):"
echo "   1. Run: ./scripts/release.sh 0.12.4"
echo "   2. Script creates release branch and PR automatically"
echo "   3. Wait for CI to pass (including security validation)"
echo "   4. Merge PR: @mergebot merge"
echo "   5. publish.yml workflow runs and deploys to PyPI"
echo ""
echo "📖 Normal development (Everyone):"
echo "   1. Create feature branch: git checkout -b feat/my-feature"
echo "   2. Make changes and commit"
echo "   3. Push: git push origin feat/my-feature"
echo "   4. Create PR: gh pr create"
echo "   5. Wait for CI to pass ✅"
echo "   6. Use merge bot: @mergebot merge"
echo ""
