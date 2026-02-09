# Tool Discovery

Tool Discovery detects installed CLI tools on your system and tells AI agents about them at session start. Instead of agents guessing what's available, they know which tools exist and how to use them.

!!! info "Requires hook support"

    Tool discovery context is injected via session hooks. See [Session Hooks](../development/session-hooks.md) for which tools are supported and how to add more.

    Other tools can still use the workspace but won't receive automatic tool discovery context.

## How it works

1. **You define tools** in `agent-tools.yaml` at the repository root
2. **At session start**, the script checks each tool's command on the system PATH
3. **Available tools** are injected into the agent's session context
4. **Agents match** tasks to tools based on the provided information

## Defining tools

Tools are defined in `agent-tools.yaml`. Each entry describes a CLI tool:

```yaml
<tool-id>:
  command: <string>        # Required - executable name to check on PATH
  name: <string>           # Optional - display name (defaults to tool ID)
  description: <string>    # Optional - brief description
  when_to_use: |           # Optional - conditions when agents should use this
    - Condition 1
    - Condition 2
  instructions: |          # Optional - usage examples and common commands
    Common commands:
    - command example 1
```

Only `command` is required. Everything else helps agents understand when and how to use the tool.

### Example

```yaml
github:
  command: gh
  name: GitHub CLI
  description: GitHub CLI for repository operations, issues, PRs, and CI/CD.
  when_to_use: |
    - Working with GitHub-hosted repositories
    - Fetching issues, PRs, or checking CI status
    - Creating releases or managing repo settings
  instructions: |
    Common commands:
    - Issues: gh issue list, gh issue view <num>
    - PRs: gh pr list, gh pr create
    - CI: gh run list, gh run view <id>

    Use --json for machine-readable output.
```

## Default tools

The template ships with these definitions:

| ID | Command | Description |
|----|---------|-------------|
| `github` | `gh` | GitHub CLI for repos, issues, PRs, releases, CI/CD |
| `gitlab` | `glab` | GitLab CLI for MRs, issues, pipelines |
| `atlassian` | `acli` | Atlassian CLI for Jira and Confluence |

These can be customized to match your team's toolchain.

## Configuration

In `ai-workspace.toml`:

```toml
[tools]
show_unavailable = false
```

`false` (default)
:   Only tools found on PATH are shown to agents

`true`
:   All defined tools are shown with availability status. Useful when you want agents to know what they *could* use if installed.

## Output format

The session-start script produces XML injected into the agent's context:

```xml
<available-tools>
  <tool id="github">
    <name>GitHub CLI</name>
    <description>GitHub CLI for repository operations...</description>
    <when-to-use>
      - Working with GitHub-hosted repositories
      - Fetching issues, PRs, or checking CI status
    </when-to-use>
    <instructions>
      Common commands:
      - Issues: gh issue list...
    </instructions>
  </tool>
</available-tools>
```

When `show_unavailable = true`, unavailable tools show `available="false"` with no instructions.

## Tips

- **Focused descriptions** work best - brief descriptions help agents quickly identify relevant tools
- **Specific `when_to_use` conditions** improve matching - the more specific, the better agents match tasks to tools
- **`instructions` don't need to be exhaustive** - covering common use cases is enough, since agents can discover more via `--help`
