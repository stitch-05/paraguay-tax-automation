---
name: release-notes-generator
description: Automatically generate and update RELEASE_NOTES.md from git commits, categorizing major/interesting changes into Features and Bugs with rewritten readable messages, organized by month with GitHub links.
---

# Release Notes Generator Skill

## When to use

Use this skill whenever asked to:

- Update release notes
- Generate release notes from commits
- Create changelog from git history
- Summarize recent changes for release

## Instructions

Follow these exact steps to generate release notes:

1. **Fetch recent commits**: Use git log to get commits. Focus on unpushed or recent changes.

   ```
   git log --pretty=format:"%H %ai %s" --all
   ```

   Prioritize **major and interesting commits only** - ignore minor fixes, formatting changes, dependency updates, or trivial commits.

2. **Classify commits by date and type**:
   - Group commits by **month and year** (e.g., January 2026, November 2025)
   - Within each month, separate into **Features** and **Bug Fixes**
   - **Features**: New functionality, UI improvements, performance enhancements, new APIs/commands.
   - **Bug Fixes**: Fixes for errors, crashes, incorrect behavior, regressions.

3. **Rewrite messages**: Original commit messages may be poor. Rewrite each into 1 clear, readable sentence starting with an action verb (e.g., "Added user authentication flow" instead of "auth stuff").

4. **Format RELEASE_NOTES.md**:
   - Top-level: `# Release Notes`
   - Month headers: `## Month Year` (e.g., `## January 2026`)
   - Section headers: `### Features` and `### Bug Fixes`
   - Each entry format: `- [`<commit-hash-short>`](github-link): Description`
   - Use commit's short hash (8 chars) as clickable link to GitHub commit.
   - Within each month: Features first, then Bug Fixes.
   - Months in reverse chronological order (newest first).
   - Separate each month section with `---`
   - Append new entries to existing file if it exists; do not overwrite old notes.

5. **GitHub links**:
   - Format: `https://github.com/<owner>/<repo>/commit/<full-commit-hash>`
   - Get repo URL from: `git config --get remote.origin.url`

## Example Output Structure

```
# Release Notes

## January 2026

### Features

- [`abc1234`](https://github.com/owner/repo/commit/abc1234567890123456789012345678901234567): Added support for real-time notifications in the dashboard.
- [`def5678`](https://github.com/owner/repo/commit/def5678901234567890123456789012345678901): Implemented dark mode toggle with local storage persistence.

### Bug Fixes

- [`ghi9012`](https://github.com/owner/repo/commit/ghi9012345678901234567890123456789012345): Fixed login crash when email contains special characters.

---

## December 2025

### Features

- [`jkl3456`](https://github.com/owner/repo/commit/jkl3456789012345678901234567890123456789): Added user profile customization options.
```

## Execution Steps

1. Run `git log --pretty=format:"%H %ai %s" --all` to list commits with dates.
2. Get repository URL: `git config --get remote.origin.url`
3. Filter to 5-10 major ones per month.
4. Group by month, categorize as Features or Bug Fixes, and rewrite messages.
5. Check if `RELEASE_NOTES.md` exists: if yes, read it and insert new month sections in chronological order; if no, create new.
6. Format each entry with clickable commit hash links.
7. Write the file and commit with message like "docs: update release notes from recent commits".

## Tips

- Be selective: Only 30-50% of commits qualify as "major/interesting".
- Readable: Use single sentences, preferring action verbs at the start.
- No duplicates: Check existing RELEASE_NOTES.md before adding.
- Chronological: Newest months at the top, oldest at the bottom.
- Month grouping: Combine all changes from the same month into one section.
