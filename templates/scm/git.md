# git.md

# Git Best Practices & Tips

## Core Best Practices

### 1. Commit Messages
- **Use conventional commits:** `type(scope): description`
- **Keep first line under 50 characters**
- **Use imperative mood:** "Add feature" not "Added feature"
- **Include issue references:** `fix: resolve login bug (#123)`

### 2. Branch Management
- **Use descriptive branch names:** `feature/user-authentication`, `fix/memory-leak`
- **Keep branches focused:** One feature/fix per branch
- **Delete merged branches:** Clean up after merging
- **Use branch protection rules** on main/master

### 3. Commit Hygiene
- **Commit early and often** with logical chunks
- **Never commit secrets** or sensitive data
- **Use `.gitignore`** for build artifacts and IDE files
- **Squash commits** before merging to keep history clean

### 4. Collaboration
- **Pull before push:** Always sync with remote first
- **Use pull requests/merge requests** for code review
- **Rebase feature branches** to maintain linear history
- **Tag releases** with semantic versioning

## Specific Git Usage Instructions
**IMPORTANT**
- As all commits are signed, do not do a git commit directly.
  Instead, prepare the commit message, and ask me to do so
- **NEVER** `checkout` or `restore` files from git to revert recent changes that you have made. What is in git may not be up to date as other changes that have been made, and these commands also risk overwriting other files as a side-effect, destroying many hours of development work.
- When you come to a logical place where a feature or sub-feature has been completed, ask the user whether they wish to commit.
- Before commit, all the relevant checks must be done in preparation:
  - All tests must be passing
  - All lint and type checking must be passing
  - Code has been formatted according to the required standard

## Essential Commands & Tips

### Quick Fixes
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Amend last commit message
git commit --amend -m "New message"

# Unstage files
git reset HEAD <file>

# Discard local changes
git checkout -- <file>
```

### Branch Operations
```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Switch branches
git switch main

# Delete local branch
git branch -d feature-name

# Delete remote branch
git push origin --delete feature-name
```

### History & Information
```bash
# View commit history (one line)
git log --oneline

# Show changes in last commit
git show

# Find who changed a line
git blame <file>

# Search commit messages
git log --grep="keyword"
```

### Stashing
```bash
# Stash current changes
git stash

# Apply last stash
git stash pop

# List all stashes
git stash list

# Apply specific stash
git stash apply stash@{2}
```

## Advanced Tips

### 5. Rebase vs Merge
- **Use rebase** for feature branches to maintain clean history
- **Use merge** for integrating completed features
- **Never rebase shared/public branches**

### 6. Interactive Rebase
```bash
# Clean up last 3 commits
git rebase -i HEAD~3

# Squash, reword, or reorder commits
# Use 'squash' to combine commits
```

### 7. Cherry-picking
```bash
# Apply specific commit to current branch
git cherry-pick <commit-hash>

# Cherry-pick without committing
git cherry-pick -n <commit-hash>
```

### 8. Aliases for Efficiency
```bash
# Set up useful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
```

## FAQ Solutions

### "I committed to the wrong branch"
```bash
# Move last commit to correct branch
git checkout correct-branch
git cherry-pick wrong-branch
git checkout wrong-branch
git reset --hard HEAD~1
```

### "I need to change the last commit"
```bash
# Add more changes to last commit
git add .
git commit --amend --no-edit
```

### "I want to see what changed"
```bash
# Compare working directory to last commit
git diff HEAD

# Compare staged changes
git diff --cached

# Compare two branches
git diff main..feature-branch
```

### "I accidentally deleted a file"
```bash
# Restore file from last commit
git checkout HEAD -- <file>

# Find when file was deleted
git log --oneline --follow -- <file>
```

## Security & Cleanup

### 9. Remove Sensitive Data
```bash
# Remove file from entire history (use with caution)
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch <file>' \
--prune-empty --tag-name-filter cat -- --all
```

### 10. Repository Maintenance
```bash
# Clean up unreachable objects
git gc --prune=now

# Verify repository integrity
git fsck

# Show repository size
git count-objects -vH
```

## Configuration Essentials

### 11. Global Setup
```bash
# Set identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default editor
git config --global core.editor "code --wait"

# Enable colour output
git config --global color.ui auto
```

### 12. Ignore Patterns
**Common `.gitignore` entries:**
```
# Dependencies
node_modules/
__pycache__/
*.pyc

# Build outputs
dist/
build/
*.o
*.exe

# IDE files
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db

# Environment files
.env
.env.local
```

Remember: **Git is a tool for collaboration and history tracking. Keep commits atomic, meaningful, and your history clean.**
