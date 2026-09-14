# claude-skills

Personal [Claude Code](https://code.claude.com) skills, agents and slash
commands. This repo is consumed two different ways from the same files.

## For me (NixOS, live-editable)

`home/modules/extras.nix` in [iUseNixBtw](https://github.com/Viscous106/iUseNixBtw)
symlinks the component directories straight into `~/.config/claude`:

| Symlink | Target |
|---|---|
| `~/.config/claude/skills` | `plugins/viscous-skills/skills` |
| `~/.config/claude/agents` | `plugins/viscous-skills/agents` |
| `~/.config/claude/commands` | `plugins/viscous-skills/commands` |

They are `mkOutOfStoreSymlink`s, so edits land immediately — no rebuild, no
`flake.lock` bump. The repo is cloned to `/persist/claude-skills`.

## For everyone else (plugin marketplace)

```
/plugin marketplace add Viscous106/claude-skills
/plugin install viscous-skills@viscous
```

## Adding a skill

```
plugins/viscous-skills/skills/<skill-name>/SKILL.md
```

with frontmatter:

```markdown
---
name: skill-name
description: When Claude should reach for this skill.
---
```

Always set `name` explicitly. Marketplace installs place plugins in
version-named directories, so the directory-name fallback is not stable.

Agents go in `agents/<name>.md`, slash commands in `commands/<name>.md`.

## Layout

```
.claude-plugin/marketplace.json     # marketplace manifest
plugins/viscous-skills/
├── .claude-plugin/plugin.json      # plugin manifest
├── skills/<name>/SKILL.md
├── agents/<name>.md
└── commands/<name>.md
```

The `.gitkeep` files keep the three component directories present in a fresh
clone; without them git would drop the empty dirs and the symlinks above
would dangle.
