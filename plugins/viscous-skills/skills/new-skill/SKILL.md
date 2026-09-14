---
name: new-skill
description: Use when adding a new personal skill, agent, or slash command to the claude-skills repo — scaffolds the file in the right place with correct frontmatter.
---

# Adding a component to claude-skills

The repo is cloned at `/persist/claude-skills` and symlinked into
`~/.config/claude/{skills,agents,commands}` by `home/modules/extras.nix` in
the `iUseNixBtw` flake. Edits are live — there is no rebuild step.

## Where the file goes

| Component | Path | Loaded as |
|---|---|---|
| Skill | `plugins/viscous-skills/skills/<name>/SKILL.md` | model-invoked skill |
| Agent | `plugins/viscous-skills/agents/<name>.md` | subagent type |
| Command | `plugins/viscous-skills/commands/<name>.md` | `/<name>` |

Write to the repo path, not through the `~/.config/claude` symlink — same
inode either way, but the repo path keeps `git status` obvious.

## Skill frontmatter

```markdown
---
name: kebab-case-name
description: When Claude should reach for this skill, phrased as a trigger.
---
```

`name` is required and must be set explicitly — marketplace installs use
version-named directories, so the directory-name fallback is unstable.

`description` is the only thing the model sees when deciding whether to load
the skill. Write it as a trigger condition ("Use when…"), not a summary.

Optional: `model` to pin a model, `disable-model-invocation: true` for a
skill only ever invoked by name.

## After writing

1. Check it loads in a fresh session — the skill list is built at startup.
2. Commit in `/persist/claude-skills` (the user runs all git commands).
3. Bump `version` in `.claude-plugin/plugin.json` only when publishing a
   change others consume via the marketplace.
