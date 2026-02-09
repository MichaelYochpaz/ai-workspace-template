# Temporary files

AI agents frequently produce transient artifacts during work - design documents, investigation logs, intermediate outputs, and other files that don't belong in version control. The workspace provides a dedicated `.tmp/` directory for this, with a helper script that keeps it organized.

## How it works

The `.tmp/` directory is git-ignored (except for its `README.md` and `.gitkeep`). Agents create task-specific subdirectories to isolate artifacts from different tasks, preventing the directory from becoming a dumping ground of mixed files.

The generated `AGENTS.md` instructs agents to use this directory and follow the naming conventions below.

## Creating a task directory

A helper script creates task-specific subdirectories:

```bash
uv run .ai-workspace/scripts/mktmpdir.py [name]
```

The script outputs the created path. If a named directory already exists, it returns the existing path.

### Naming strategy

The `name` argument controls how the directory is named:

1. **Work item ID (preferred)** - The canonical identifier from the tracking system

    ```bash
    uv run .ai-workspace/scripts/mktmpdir.py JIRA-123
    uv run .ai-workspace/scripts/mktmpdir.py gh-issue-456
    uv run .ai-workspace/scripts/mktmpdir.py pr-789
    ```

2. **Descriptive name** - A name derived from the task, when no work item ID exists

    ```bash
    uv run .ai-workspace/scripts/mktmpdir.py fix-api-timeout-retry-logic
    ```

    Distinguishing details help - `fix-api-timeout-retry-logic` rather than `api-fix`.

3. **Random (default)** - When the name is omitted, for exploratory or throwaway work

    ```bash
    uv run .ai-workspace/scripts/mktmpdir.py
    # Creates: .tmp/20260208-a3f7
    ```

    Generates a `YYYYMMDD-xxxx` directory (date + random hex).

## Subtask coordination

When an agent delegates work to subtasks, passing the directory path keeps all related artifacts together:

- **Delegating subtasks** - The `.tmp/` subdirectory path is passed so subtask output lands in the same place
- **Coordinating multiple subtasks** - A shared subdirectory is created before delegating, and its path is passed to all subtasks
