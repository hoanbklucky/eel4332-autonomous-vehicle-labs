# Open and Update the Course Repository

Use your existing clone in **WSL/Ubuntu**. Opening VS Code does not download course updates; pulling does. You do not need to clone again for each lab.

## 1. Open the repository in VS Code

Open an Ubuntu terminal and run:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
code .
```

`cd` enters your local repository; `code .` opens that folder in VS Code. Use your actual path if you cloned elsewhere. If several similarly named folders exist, open the student course repository rather than an instructor or backup copy.

The first launch may display **Installing/Updating VS Code Server** and a download percentage. Wait for it to finish. This updates VS Code's WSL support, not the course repository.

Confirm:

- The lower-left indicator shows **WSL: Ubuntu** (possibly with the distribution version).
- Explorer shows the repository's top-level `README.md` and lab folders.
- **Terminal → New Terminal** opens an Ubuntu shell in this repository.

If the folder opens in Windows mode, use the Command Palette (**Ctrl+Shift+P**) and **WSL: Reopen Folder in WSL**. Install the Microsoft WSL extension if needed.

## 2. Check your copy before updating

Save all open files, then run in the integrated Ubuntu terminal:

```bash
pwd
git remote -v
git branch --show-current
git status --short
```

For a direct clone of the course repository, `origin` should point to:
`https://github.com/hoanbklucky/eel4332-autonomous-vehicle-labs.git`
(the equivalent SSH URL is also valid), and the branch should be `main`.

If your origin is a personal fork or you use a different branch, do not change remotes or switch branches blindly; ask the instructor which upstream workflow to use.

No output from `git status --short` means there are no reported uncommitted changes. Listed files mean you must protect local work using Section 4 first. A clean working tree does not mean your clone is up to date.

## 3. Get the latest version — choose either method

### Method A: VS Code Source Control

For a clean working tree on the course `main` branch:

1. Open **Source Control** (**Ctrl+Shift+G**).
2. If multiple repositories appear, select this course repository.
3. Open the **…** menu and choose **Pull** (it may appear under **Pull, Push**).
4. Wait for completion and review any reported error before continuing.

Use **Pull** to receive instructor updates. **Sync Changes** performs a pull followed by a push and may try to upload your local commits; it is not needed to download course files. **Settings Sync** synchronizes editor settings, not repository contents. Pulling does not submit your lab work.

### Method B: Ubuntu command line

From a clean working tree on the course `main` branch:

```bash
git pull --ff-only origin main
```

`pull` fetches and integrates instructor changes. `--ff-only` updates only when no merge or rebase is needed; it stops if local and remote history diverge. If it stops, ask the instructor/TA for help rather than forcing an update.

For a routine update after checking your copy:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git status --short
```

If nothing is listed, run:

```bash
git pull --ff-only origin main
code .
```

Git reports either `Already up to date.` or a summary of updated files. Opening `code .` alone does not perform this pull.

## 4. Preserve uncommitted student work

Only use this section when `git status --short` lists files. Save editor buffers and back up important code/results outside the repository first. Ignored files such as bags/build outputs are not included by the stash command below.

Run:

```bash
git stash push --include-untracked -m "My work before course update"
```

Confirm Git reports that it saved your changes, then run:

```bash
git pull --ff-only origin main
```

Only after the pull succeeds, restore your work:

```bash
git stash apply
git status
```

`stash apply` restores the saved changes while keeping the stash as a backup. Verify your files before optionally removing that saved stash with `git stash drop`. Do not repeatedly apply the same stash.

If the pull fails, stop before restoring and ask for help; your saved work remains in the stash. Stashing does not resolve diverged committed history.

## 5. Conflicts and update verification

If restoring work reports conflicts, run `git status`, open the affected files in VS Code, and reconcile your work with the course update. Ask the instructor/TA if unsure. The stash remains available after `stash apply`. Do not use **Discard Changes**, `git reset --hard`, or delete your clone to resolve the problem.

After a successful update:

```bash
git log -1 --oneline
ls
```

Check that the current structure includes `lab04_slam/`, `lab05_navigation/`, and `final_project_simulation/`. The older Labs 04–09 are now under `optional_legacy/previous_lab_sequence/`; locally modified/untracked old files may remain and should be reviewed rather than deleted blindly.

Reopen the updated README in VS Code. If an update changes dependencies, follow the relevant setup instructions; Git updates files but does not install ROS packages or Python dependencies.

## Official references

- [VS Code in WSL](https://code.visualstudio.com/docs/remote/wsl)
- [VS Code source control](https://code.visualstudio.com/docs/sourcecontrol/overview)
- [Git pull](https://git-scm.com/docs/git-pull)
