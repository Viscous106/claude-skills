---
name: new-skill
description: Use when adding a new skill, agent, or slash command to the claude-skills repo — places the file correctly and gets the frontmatter right.
---

# Adding a component to claude-skills

## Where the file goes

Paths are relative to the repo root.

| Component | Path | Loaded as |
|---|---|---|
| Skill | `plugins/viscous-skills/skills/<name>/SKILL.md` | model-invoked skill |
| Agent | `plugins/viscous-skills/agents/<name>.md` | subagent type |
| Command | `plugins/viscous-skills/commands/<name>.md` | `/<name>` |

A skill may also carry supporting files in its own directory — `reference.md`
for detail the model loads only when needed, `scripts/` for anything
executable.

## Skill frontmatter

```markdown
---
name: kebab-case-name
description: When Claude should reach for this skill, phrased as a trigger.
---
```

`name` is required and must be set explicitly. Marketplace installs place
plugins in version-named directories, so the fallback to the directory name is
not stable across updates.

`description` is the only part of a skill the model sees when deciding whether
to load it. Write it as a trigger condition — "Use when the user is X" —
rather than a summary of the contents.

Optional: `model` pins a model for the skill, and
`disable-model-invocation: true` restricts it to explicit invocation by name.

## After writing

1. Confirm it loads in a **fresh** session — the skill list is built at
   startup, so an already-running session will not see it.
2. Commit it.
3. Bump `version` in `.claude-plugin/plugin.json` only when publishing a
   change that marketplace users should pick up.

## If the repo is symlinked into `~/.config/claude`

Write to the repo path rather than through the symlink. Same inode either way,
but the repo path keeps `git status` honest. See `nix-setup.md` for that
arrangement.
