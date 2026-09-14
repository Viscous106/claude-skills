# claude-skills

Personal [Claude Code](https://code.claude.com) skills, agents and slash
commands, packaged as a plugin marketplace.

## Install

```
/plugin marketplace add Viscous106/claude-skills
/plugin install viscous-skills@viscous
```

Run both from inside Claude Code. The first command registers the
marketplace, the second installs the plugin from it.

## What's in it

| Component | Location |
|---|---|
| Skills | `plugins/viscous-skills/skills/<name>/SKILL.md` |
| Agents | `plugins/viscous-skills/agents/<name>.md` |
| Slash commands | `plugins/viscous-skills/commands/<name>.md` |

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
clone — git drops empty directories otherwise.

## Adding a skill

Create `plugins/viscous-skills/skills/<skill-name>/SKILL.md`:

```markdown
---
name: skill-name
description: When Claude should reach for this skill.
---

Instructions go here.
```

Always set `name` explicitly. Marketplace installs place plugins in
version-named directories, so the directory-name fallback is not stable.
Write `description` as a trigger condition ("Use when…") rather than a
summary — it is the only thing the model sees when deciding whether to load
the skill.

The bundled `new-skill` skill walks through this.

## Using it without the marketplace

Installing from the marketplace copies the plugin into a version-pinned cache
directory, which is fine for using these skills but awkward for editing them —
changes are lost on the next update.

To work on them instead, clone the repo anywhere and point Claude Code's
personal skills directory at it:

```bash
git clone git@github.com:Viscous106/claude-skills.git ~/Viscous/claude-skills

ln -sfn ~/Viscous/claude-skills/plugins/viscous-skills/skills   ~/.config/claude/skills
ln -sfn ~/Viscous/claude-skills/plugins/viscous-skills/agents   ~/.config/claude/agents
ln -sfn ~/Viscous/claude-skills/plugins/viscous-skills/commands ~/.config/claude/commands
```

Use `~/.claude/` instead of `~/.config/claude/` unless `CLAUDE_CONFIG_DIR`
says otherwise. Edits then take effect in the next session with no install
step. Skills loaded this way are invoked as `/<name>`, not
`/viscous-skills:<name>`.

## License

MIT — see [LICENSE](LICENSE).
