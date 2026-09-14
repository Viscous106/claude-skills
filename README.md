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

The component directories are plain files with no build step, so you can also
symlink them straight into `~/.config/claude/{skills,agents,commands}` and
edit them in place. For a declarative NixOS / home-manager version of that,
see [nix-setup.md](nix-setup.md).

## License

MIT — see [LICENSE](LICENSE).
