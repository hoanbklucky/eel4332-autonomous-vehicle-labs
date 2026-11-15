# Fork, Open, Update, and Save Your Work

Use **Ubuntu/WSL**, including VS Code's integrated terminal connected to WSL. Your course repository and `~/turtlebot3_ws` are separate; fork only the course repository.

## 1. Fork and clone (new students)

On [the instructor repository](https://github.com/hoanbklucky/eel4332-autonomous-vehicle-labs), click **Fork → Create fork** under your own GitHub account. Keep the repository name. Then replace `YOUR_USERNAME` below with your actual GitHub username:

```bash
mkdir -p ~/courses
cd ~/courses
git clone https://github.com/YOUR_USERNAME/eel4332-autonomous-vehicle-labs.git
cd eel4332-autonomous-vehicle-labs
git remote add upstream https://github.com/hoanbklucky/eel4332-autonomous-vehicle-labs.git
git remote -v
code .
```

| Remote | Repository | Purpose |
|---|---|---|
| `origin` | Your fork | Push your code/results |
| `upstream` | Instructor repository | Receive course updates |

Confirm **WSL: Ubuntu** in VS Code. Wait for any VS Code Server update; it updates editor support, not course files. Use **Terminal → New Terminal** for commands.

## 2. Already cloned the instructor repository?

Keep your files and history; do not delete or re-clone. First create your fork on GitHub, then inspect:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git remote -v
git status
```

If `origin` currently points to the instructor repository and `upstream` does not exist, run these commands after replacing `YOUR_USERNAME`:

```bash
git remote rename origin upstream
git remote add origin https://github.com/YOUR_USERNAME/eel4332-autonomous-vehicle-labs.git
git fetch origin
git remote -v
```

If either remote already exists, inspect it first. Use `git remote set-url REMOTE URL` only to correct that remote's URL; do not add duplicates. Changing remotes does not alter local files or commits.

If the current branch is `main` and you intend to keep student work there, its next successful `git push -u origin main` sets tracking to your fork. Check **both fetch and push URLs** before pushing.

## 3. Save your edits to your fork

Save editor buffers, check your branch with `git branch --show-current`, and review:

```bash
git status
git diff
```

Stage only your intended source, answers, configuration, maps, and small results using VS Code's **+** controls, or `git add path/to/file` with actual paths. Do not commit bags, environments, or ROS build/install/log directories. Then:

```bash
git commit -m "Complete lab work"
git push -u origin main
```

These instructions assume student work is on `main`; if you use a different branch, push that branch explicitly. Authenticate with your GitHub account using supported HTTPS credentials (a personal access token/credential manager) or an SSH key; your account password is not a Git HTTPS password. Never commit credentials.

In VS Code, **Commit** saves locally; **Push** uploads to your fork after tracking is configured. **Sync Changes** pulls/pushes the tracked fork branch; it does not fetch new instructor commits from `upstream`.

Pushing backs up work. Submit the fork link/commit through the instructor's specified submission channel; no pull request to the instructor repository is required.

## 4. Receive instructor updates without losing your commits

Save and commit your work first, then ensure `git status --short` prints nothing and `git branch --show-current` reports `main`. Run:

```bash
git fetch upstream
git merge --no-edit upstream/main
```

This keeps student commits and merges instructor updates; `--ff-only` is not suitable once both sides have new commits. After a successful merge:

```bash
git push -u origin main
```

If the push is rejected because your fork has newer commits, run `git fetch origin`, merge `origin/main`, resolve any conflicts, and push again. Do not force-push.

VS Code's ordinary **Pull** reads the tracked fork, not the instructor repository. Use the integrated-terminal commands above for course updates.

## 5. Conflicts or unfinished work

A merge conflict means both sides edited the same section. Use `git status` and VS Code's Merge Editor to combine the changes, stage each resolved file, then finish with `git commit` and push. If unsure, ask the instructor/TA. `git merge --abort` cancels an in-progress merge.

If you cannot commit unfinished work yet, back up important files outside the repository, then run `git stash push --include-untracked -m "Before course update"`. Confirm a stash was created. Fetch/merge upstream as above. **Only after the merge succeeds**, run `git stash apply`; review/resolve changes, then commit and push. The stash remains as a backup until you deliberately remove it. Ignored files are not included.

Do not use `git reset --hard`, `git clean -fdx`, or VS Code **Discard Changes** as a routine update method; they can remove student work.

## 6. Verify

Run `git log -1 --oneline` and reopen the README. New folders include `lab04_slam`, `lab05_navigation`, and `final_project_simulation`. Old untracked files may remain after updates; review rather than delete blindly. Git updates files, not installed ROS/Python packages.

Official references: [Fork a repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo), [Syncing a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork), [VS Code in WSL](https://code.visualstudio.com/docs/remote/wsl).
