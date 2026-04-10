---
name: git-workflow
description: Enforce branch-first development, conventional branch naming, structured PRs, and mandatory human review for this repository.
compatibility: opencode
---

# Git Workflow Skill

Use this skill for any code or documentation change in this repository.

## Goals

- Keep all changes isolated on branches.
- Use consistent branch naming based on Conventional Commit types.
- Use a consistent pull request structure.
- Require human review before merge.

## Rules

1. Never commit directly to `main`.
2. Always create a branch for every change, including docs, chores, and fixes.
3. Branch names must start with a Conventional Commit type.
4. If an issue ID exists, place it after the type and before the short branch slug.
5. Pull requests must use the repository PR template.
6. Pull requests must not be auto-merged. Human review is mandatory before merge.

## Branch Naming

Use one of these formats:

- Without issue ID: `<type>/<short-slug>`
- With issue ID: `<type>/<issue-id>-<short-slug>`

Allowed `<type>` values:

- `feat`
- `fix`
- `docs`
- `chore`
- `refactor`
- `test`
- `ci`
- `build`
- `perf`
- `style`
- `revert`

Examples:

- `feat/add-release-health-check`
- `fix/142-correct-publish-tag`
- `docs/98-improve-readme-install-steps`

## Pull Request Process

1. Open a PR from your branch to `main`.
2. Fill out all sections in the PR template, especially:
   - Changes
   - Validation
3. Request at least one human reviewer.
4. Do not enable auto-merge.
5. Merge only after review approval and passing checks.

## Agent Behavior

When acting as an AI agent in this repository:

- If currently on `main`, create a branch before making edits.
- If branch name does not match this skill, rename or create a compliant branch.
- If an issue ID is provided by the user, include it in branch naming.
- When opening or updating a PR, follow the PR template exactly.
- If auto-merge is enabled on a PR, disable it and note the reason.
