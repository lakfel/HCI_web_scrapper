#!/bin/bash

# Remove .env from git history
git filter-branch --force --index-filter \
	"git rm --cached --ignore-unmatch HCIScrapy/.env" \
	--prune-empty --tag-name-filter cat -- --all

# Remove the old refs
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# Cleanup and garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push to remote (BE CAREFUL WITH THIS)
git push origin --force --all