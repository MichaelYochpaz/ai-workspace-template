# Temporary Directory

A git-ignored workspace for AI agents to store transient artifacts, design documents, logs, and intermediate files.

## How It Works

AI agents create task-specific subdirectories at the start of each task to keep artifacts organized. When a task delegates to subtasks, the parent task's directory path is passed along so all related work stays together. This prevents the directory from becoming cluttered with mixed artifacts from unrelated tasks.

The [`.ai-workspace/scripts/mktmpdir.py`](../.ai-workspace/scripts/mktmpdir.py) helper script automates directory creation for agents.

## Version Control

All contents are git-ignored except for this `README.md` and `.gitkeep`.
