#!/bin/bash
# Configure repository labels for msgspec-ext

set -e

REPO="msgflux/msgspec-ext"

echo "🏷️  Configuring labels for ${REPO}..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found"
    exit 1
fi

# Function to create or update label
create_or_update_label() {
    local name="$1"
    local description="$2"
    local color="$3"

    if gh label create "$name" --repo "$REPO" --description "$description" --color "$color" 2>/dev/null; then
        echo "  ✅ Created: $name"
    else
        gh label edit "$name" --repo "$REPO" --description "$description" --color "$color" 2>/dev/null
        echo "  ✅ Updated: $name"
    fi
}

echo "📋 Creating type labels..."
create_or_update_label "feat" "New feature" "0e8a16"
create_or_update_label "fix" "Bug fix" "d73a4a"
create_or_update_label "docs" "Documentation" "0075ca"
create_or_update_label "chore" "Maintenance" "fef2c0"
create_or_update_label "test" "Testing" "bfe5bf"
create_or_update_label "refactor" "Code refactoring" "fbca04"
create_or_update_label "perf" "Performance improvement" "c5def5"
create_or_update_label "ci" "CI/CD changes" "1d76db"

echo "📋 Creating status labels..."
create_or_update_label "release" "Release PR" "0e8a16"
create_or_update_label "automerge" "Auto-merge enabled" "ededed"
create_or_update_label "urgent" "Urgent/hotfix" "b60205"
create_or_update_label "dependencies" "Dependency updates" "0366d6"

echo "📋 Creating size labels..."
create_or_update_label "size/XS" "Extra small PR" "3CBF00"
create_or_update_label "size/S" "Small PR" "5D9801"
create_or_update_label "size/M" "Medium PR" "7F7203"
create_or_update_label "size/L" "Large PR" "A14C05"
create_or_update_label "size/XL" "Extra large PR" "C32607"

echo "✅ Labels configured successfully!"
