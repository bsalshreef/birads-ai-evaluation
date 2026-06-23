#!/bin/bash
# ============================================================
# push_to_github.sh
# Run this script ONCE after cloning/extracting the zip.
# Replace YOUR_GITHUB_TOKEN with a Personal Access Token
# (Settings → Developer Settings → Personal Access Tokens → Fine-grained)
# with "Contents: Read and Write" permission on the new repo.
# ============================================================

GITHUB_USERNAME="bsalshreef"
REPO_NAME="birads-ai-evaluation"
GITHUB_TOKEN="YOUR_GITHUB_TOKEN"   # <-- paste your PAT here

# Step 1: Create the repository on GitHub
echo "Creating repository on GitHub..."
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"BI-RADS Anchored AI Evaluation Framework for Breast Cancer Screening\",
    \"private\": false,
    \"has_issues\": true,
    \"has_projects\": false,
    \"has_wiki\": false
  }"

echo ""
echo "Repository created: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

# Step 2: Initialise git and push
cd "$(dirname "$0")"
git init
git add .
git commit -m "Initial commit: BI-RADS AI evaluation framework v1.0.0"
git branch -M main
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git push -u origin main

# Step 3: Tag the release
git tag -a v1.0.0 -m "Release v1.0.0 — initial publication version"
git push origin v1.0.0

echo ""
echo "✅ Done! Repository is live at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "Next: Connect Zenodo at https://zenodo.org/account/settings/github/"
