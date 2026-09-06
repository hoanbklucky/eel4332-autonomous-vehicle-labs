# Updating the Course Repository

Use these steps to get the newest course files without losing your own work. Run all commands in a **WSL/Ubuntu Terminal**.

## 1. Go to Your Local Course Repository

If you cloned the repository in the recommended location, run:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
```

**Command breakdown:** `cd` changes the current directory, and `~` represents your Ubuntu home directory.

Here, `~` means your Ubuntu home directory, such as `/home/your_username`. If you cloned the repository somewhere else, change the command to that location.

## 2. Check for Local Changes

```bash
git status --short
```

**Command breakdown:** `git status` compares your working files with the current commit; `--short` uses a compact one-line format for each changed file.

This command compares your working files with your most recent local commit:

- **No output** means the tracked files are unchanged. Continue to Step 3.
- **Listed files** mean you have local changes or new files. Follow Step 4 before pulling.

## 3. Update a Clean Repository

When `git status --short` prints nothing, run:

```bash
git pull --rebase
```

**Command breakdown:** `git pull` downloads and integrates changes from the configured remote branch. `--rebase` reapplies your local commits after the downloaded commits, avoiding an unnecessary merge commit.

Git will either report `Already up to date.` or download and apply newer course files. Pulling updates does **not** submit your lab work.

## 4. Protect Local Work Before Updating

First, make a backup copy of any important work outside the repository. Then temporarily store both tracked and untracked changes:

```bash
git stash push --include-untracked -m "My work before course update"
git pull --rebase
git stash pop
```

**Command breakdown:** `git stash push` temporarily stores tracked and untracked changes; `-m` labels that saved state. After `git pull --rebase` updates the repository, `git stash pop` reapplies the stored work.

`git stash` sets your unfinished changes aside, `git pull --rebase` updates the course files, and `git stash pop` reapplies your changes.

## If Git Reports a Conflict

A conflict means both you and the course update changed the same part of a file. Your work is not automatically lost.

1. Run `git status` to identify the conflicted files.
2. Open each file in VS Code and use the Merge Editor, or resolve the sections marked with `<<<<<<<`, `=======`, and `>>>>>>>`.
3. Save the resolved file and run `git add path/to/file`.
4. If Git says a rebase is in progress, run `git rebase --continue`. If the conflict appeared after `git stash pop`, do not run `git rebase --continue`; resolve and stage the files normally.

If you are unsure how to resolve a conflict, stop and ask the instructor or teaching assistant. Do not use `git reset --hard`, force a pull, or delete and clone the repository again; those actions can discard your work. If a pull rebase is still in progress and you need to return to the state before the pull, run:

```bash
git rebase --abort
```

**Command breakdown:** `git rebase --abort` cancels an in-progress rebase and restores the repository to its state before that rebase began. It does not resolve a conflict caused only by `git stash pop`.
