# Repositories

The workspace aggregates your projects as git submodules under the `repositories/` directory.

For AI tools with [hook support](index.md#session-hooks), each submodule's git state is automatically reported to the agent at session start.

## The submodule model

Git submodules are pinned to specific commits. When someone clones the workspace, they get the exact versions that were last committed. During daily work, you work with the latest code inside each submodule - the pinned commits just serve as a baseline for cloning and CI.

The workspace periodically updates these pins to keep them reasonably current. This should be done as a **dedicated action**, not as a side effect of other work - otherwise unrelated submodule reference changes end up polluting your commits.

## Adding repositories

```bash
git submodule add <repository-url> repositories/<name>
```

### Tracking a different branch

By default, submodules track `main`. To track a different branch, set `branch` in `.gitmodules`:

```ini
[submodule "repositories/backend"]
    path = repositories/backend
    url = git@github.com:org/repository.git
    branch = develop
```

Then update:

```bash
git submodule update --remote repositories/backend
```

## Repository status reporting

!!! info "Requires hook support"

    Automatic status reporting only works with AI tools that support [session hooks](../development/session-hooks.md).

    Other tools can still use the workspace, but won't receive automatic repo status context.

At session start, the session-start script checks each submodule's git state and injects it into the agent's context:

```xml
<repository-status>
<repo path="repositories/backend"
      branch="main"
      default-branch="main"
      uncommitted-changes="false"
      behind="0" />
<repo path="repositories/frontend"
      branch="feature/new-ui"
      default-branch="main"
      uncommitted-changes="true"
      behind="3" />
</repository-status>
```

### Status fields

`path`
:   Submodule path relative to workspace root

`branch`
:   Current branch (or `detached @ <sha>` for detached HEAD)

`default-branch`
:   Auto-detected default branch (see [detection logic](#default-branch-detection) below)

`uncommitted-changes`
:   Whether there are staged, unstaged, or untracked changes

`behind`
:   Commits behind the remote tracking branch (`unknown` if offline)

With this, agents can warn about uncommitted changes, suggest pulling when behind, and understand which branch they're working on.

!!! warning "Point-in-time snapshot"

    Repository status is captured once at session start and cached for the session's lifetime. It may become stale if repo state changes during the session — for example, if branches are switched externally, another agent modifies the workspace, or the session runs long enough for remote refs to diverge.

    Agents are instructed to verify repo state with git commands before branch switches or destructive operations. See [Session Hooks — Limitations](development/session-hooks.md#limitations) for more details.

## Default branch detection

The default branch for each submodule is auto-detected at session start using a waterfall strategy:

1. **Git remote HEAD ref** -- `git symbolic-ref refs/remotes/origin/HEAD` (accurate when present, but often missing in submodules)
2. **`.gitmodules` branch field** -- per-submodule `branch` setting (the recommended way to configure non-standard defaults)
3. **Heuristic** -- checks if `origin/main` or `origin/master` exists as a local remote ref
4. **Fallback** -- defaults to `main` with a warning printed to stderr

If a submodule uses a non-standard default branch (e.g., `develop`, `trunk`), set the `branch` field in `.gitmodules` for that submodule. This ensures correct detection regardless of the local git state.

## Configuration

```toml
[repositories]
include_workspace_root = false
```

`include_workspace_root`
:   **Default:** `false` - Also report status for the workspace root repo itself

## Commit and push workflow

When making changes inside a submodule, **always push the submodule before the parent**. If the parent is pushed first, other users (and CI) will have submodule references pointing to commits that don't exist on the remote yet.

??? example "Example workflow"

    ```bash
    # 1. Commit and push inside the submodule
    cd repositories/backend
    git add . && git commit -m "Your changes"
    git push

    # 2. Return to workspace root and commit the updated reference
    cd ../..
    git add repositories/backend
    git commit -m "Update backend submodule"
    git push
    ```

## Updating pinned commits

To update submodule pins to the latest remote commits:

```bash
git submodule update --remote --recursive
```

This changes the pinned commit references in the parent repo. Commit and push these changes as a **standalone commit** - don't mix them with unrelated work.

!!! tip

    This is a good candidate for a periodic automated job (e.g., a scheduled CI workflow that opens a PR with updated submodule pins).

## Other useful commands

```bash
# Initialize submodules after cloning (checks out pinned commits)
git submodule update --init --recursive

# Check current repository status (same output agents see at session start)
uv run .ai-workspace/scripts/session-start.py
```

??? note "Troubleshooting"

    - **Commits in detached HEAD** - Run `git checkout -b <branch>` inside the submodule, then `git push -u origin <branch>`
    - **Forgot to push submodule before parent** - Just push the submodule now; the parent reference is already correct
    - **Submodule update fails with conflicts** - Reset and retry: `git submodule foreach --recursive git reset --hard && git submodule update --init --recursive`
    - **Status shows "unknown" for behind count** - No network connection or no remote tracking branch; run `git fetch` inside the submodule
