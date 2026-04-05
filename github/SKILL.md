---
name: github
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries. Use when the user asks about GitHub issues, pull requests, workflows, or wants to interact with GitHub repositories from the command line — including tasks like check CI status, create PR, list issues, or query the GitHub API."
---

# GitHub Skill

Use the `gh` CLI to interact with GitHub. Always specify `--repo owner/repo` when not in a git directory, or use URLs directly.

## Pull Requests

### Creating

```bash
# Create PR from current branch
gh pr create --title "Add feature" --body "Description of changes"

# Create draft PR
gh pr create --title "WIP: feature" --body "Still working on this" --draft

# Create with reviewers and labels
gh pr create --title "Fix bug" --body "Fixes #42" --reviewer user1,user2 --label bug,urgent

# Create with base branch (default: main)
gh pr create --title "Feature" --body "..." --base develop

# Create using heredoc for multi-line body
gh pr create --title "Feature" --body "$(cat <<'EOF'
## Summary
- Added new endpoint
- Updated tests

## Test plan
- [ ] Unit tests pass
- [ ] Manual QA
EOF
)"
```

### Viewing and Listing

```bash
# List open PRs
gh pr list --repo owner/repo

# List PRs by author
gh pr list --author @me

# List PRs with label
gh pr list --label "needs-review"

# View PR details
gh pr view 55 --repo owner/repo

# View PR diff
gh pr diff 55 --repo owner/repo

# Check out a PR locally
gh pr checkout 55
```

### Reviewing and Commenting

```bash
# Approve a PR
gh pr review 55 --approve

# Request changes
gh pr review 55 --request-changes --body "Please fix the error handling"

# Add a comment
gh pr comment 55 --body "Looks good, just one question about the caching layer"

# View review comments
gh api repos/owner/repo/pulls/55/comments
```

### Merging

```bash
# Merge (default strategy)
gh pr merge 55

# Squash merge
gh pr merge 55 --squash

# Rebase merge
gh pr merge 55 --rebase

# Merge and delete branch
gh pr merge 55 --squash --delete-branch

# Auto-merge when checks pass
gh pr merge 55 --auto --squash
```

### CI Status and Debugging

Check CI status on a PR:
```bash
gh pr checks 55 --repo owner/repo
```

List recent workflow runs:
```bash
gh run list --repo owner/repo --limit 10
```

View a run and see which steps failed:
```bash
gh run view <run-id> --repo owner/repo
```

View logs for failed steps only:
```bash
gh run view <run-id> --repo owner/repo --log-failed
```

#### Debugging a CI Failure

Follow this sequence to investigate a failing CI run:

1. **Check PR status** — identify which checks are failing:
   ```bash
   gh pr checks 55 --repo owner/repo
   ```
2. **List recent runs** — find the relevant run ID:
   ```bash
   gh run list --repo owner/repo --limit 10
   ```
3. **View the failed run** — see which jobs and steps failed:
   ```bash
   gh run view <run-id> --repo owner/repo
   ```
4. **Fetch failure logs** — get the detailed output for failed steps:
   ```bash
   gh run view <run-id> --repo owner/repo --log-failed
   ```

## Issues

### Creating

```bash
# Create with title and body
gh issue create --title "Bug: crash on launch" --body "Steps to reproduce..."

# Create with labels and assignee
gh issue create --title "Add dark mode" --label enhancement,ui --assignee @me

# Create from template (if repo has issue templates)
gh issue create --template "bug_report.md"
```

### Listing and Searching

```bash
# List open issues
gh issue list --repo owner/repo

# Filter by label
gh issue list --label bug

# Filter by assignee
gh issue list --assignee @me

# Search across repos
gh issue list --search "memory leak language:swift"

# List with state
gh issue list --state closed --limit 20
```

### Managing

```bash
# View issue details
gh issue view 42

# Close an issue
gh issue close 42

# Close with comment
gh issue close 42 --comment "Fixed in #55"

# Reopen
gh issue reopen 42

# Add labels
gh issue edit 42 --add-label "priority:high"

# Remove labels
gh issue edit 42 --remove-label "needs-triage"

# Assign
gh issue edit 42 --add-assignee user1

# Add a comment
gh issue comment 42 --body "Reproduced on iOS 18.2"

# Pin an issue
gh issue pin 42
```

## Releases

### Creating

```bash
# Create release from tag
gh release create v1.0.0 --title "v1.0.0" --notes "First stable release"

# Create draft release
gh release create v1.1.0 --title "v1.1.0" --draft --notes "Release candidate"

# Auto-generate notes from commits
gh release create v1.2.0 --generate-notes

# Auto-generate notes with previous tag reference
gh release create v1.2.0 --generate-notes --notes-start-tag v1.1.0

# Create pre-release
gh release create v2.0.0-beta.1 --prerelease --title "v2.0.0 Beta 1" --notes "Beta release"

# Create release with assets
gh release create v1.0.0 ./build/app.zip ./build/app.dmg --title "v1.0.0"
```

### Managing Assets

```bash
# Upload assets to existing release
gh release upload v1.0.0 ./build/app.zip ./build/checksum.txt

# Download assets
gh release download v1.0.0 --dir ./downloads

# Download specific asset by pattern
gh release download v1.0.0 --pattern "*.dmg"
```

### Listing and Viewing

```bash
# List releases
gh release list --repo owner/repo

# View release details
gh release view v1.0.0

# View latest release
gh release view --repo owner/repo
```

### Editing and Deleting

```bash
# Edit release notes
gh release edit v1.0.0 --notes "Updated release notes"

# Promote draft to published
gh release edit v1.0.0 --draft=false

# Delete release
gh release delete v1.0.0
```

## Gists

### Creating

```bash
# Create public gist from file
gh gist create script.py --public

# Create private gist (default)
gh gist create config.json

# Create with description
gh gist create snippet.swift --desc "Core Data migration helper"

# Create from multiple files
gh gist create file1.py file2.py file3.py

# Create from stdin
echo "hello world" | gh gist create --filename greeting.txt
```

### Managing

```bash
# List your gists
gh gist list

# View gist contents
gh gist view <gist-id>

# Edit a gist
gh gist edit <gist-id>

# Add file to existing gist
gh gist edit <gist-id> --add newfile.md

# Delete a gist
gh gist delete <gist-id>

# Clone gist as repo
gh gist clone <gist-id>
```

## API for Advanced Queries

The `gh api` command is useful for accessing data not available through other subcommands.

Get PR with specific fields:
```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

Paginate large result sets:
```bash
gh api repos/owner/repo/issues --paginate --jq '.[].title'
```

POST request (e.g., add a label):
```bash
gh api repos/owner/repo/issues/42/labels --method POST --input - <<< '["bug"]'
```

## JSON Output

Most commands support `--json` for structured output. Use `--jq` to filter:

```bash
# Issue list as formatted lines
gh issue list --json number,title --jq '.[] | "\(.number): \(.title)"'

# PR authors for open PRs
gh pr list --json author --jq '.[].author.login' | sort -u

# Checks that failed
gh pr checks 55 --json name,state --jq '.[] | select(.state != "SUCCESS")'
```
