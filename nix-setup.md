# NixOS / home-manager setup

How this repo is wired on my machine, instead of installing it as a plugin.

The goal is a live-editable skills directory: writing a `SKILL.md` should take
effect in the next Claude Code session with no rebuild and no `flake.lock`
bump. A plugin install cannot do that — it copies into a versioned cache — and
neither can a flake input, because the store is read-only. So the repo is
cloned to a persistent path and symlinked out-of-store.

## Where things live

Claude Code config is split across two repos by shareability:

| Repo | Holds |
|---|---|
| [iUseNixBtw](https://github.com/Viscous106/iUseNixBtw) | `CLAUDE.md`, `settings.json`, hooks, statusline helpers — machine-specific |
| this repo | skills, agents, commands — portable and shareable |

`CLAUDE_CONFIG_DIR` is set to `~/.config/claude` in `home/modules/zsh.nix`, so
that — not `~/.claude` — is where the symlinks go.

## Clone

`/persist` is root-owned and home-manager activation runs as the user, so the
clone is a manual bootstrap step:

```bash
sudo mkdir -p /persist/claude-skills && sudo chown $USER:users /persist/claude-skills
git clone git@github.com:Viscous106/claude-skills.git /persist/claude-skills
```

## Wiring — `home/modules/extras.nix`

```nix
xdg.configFile."claude/skills".source = config.lib.file.mkOutOfStoreSymlink
  "/persist/claude-skills/plugins/viscous-skills/skills";
xdg.configFile."claude/agents".source = config.lib.file.mkOutOfStoreSymlink
  "/persist/claude-skills/plugins/viscous-skills/agents";
xdg.configFile."claude/commands".source = config.lib.file.mkOutOfStoreSymlink
  "/persist/claude-skills/plugins/viscous-skills/commands";
```

`mkOutOfStoreSymlink`, not a store copy — a store path would be read-only and
would need a rebuild for every edit.

Only these three directories plus the static config in the other repo are
symlinked. The rest of `~/.config/claude` — `projects/`, `sessions/`,
`plugins/`, `history.jsonl`, the caches — is live runtime state and must stay
as real files.

## Bootstrap warning — `home/viscous.nix`

Activation cannot create the clone, so it warns instead of failing the switch:

```nix
home.activation.checkClaudeSkills = config.lib.dag.entryAfter [ "writeBoundary" ] ''
  if [ ! -d /persist/claude-skills/plugins/viscous-skills/skills ]; then
    echo "Warning: /persist/claude-skills is missing — Claude Code skills/agents/commands will be dangling symlinks."
    echo "  Bootstrap with:"
    echo "    sudo mkdir -p /persist/claude-skills && sudo chown $USER:users /persist/claude-skills"
    echo "    git clone git@github.com:Viscous106/claude-skills.git /persist/claude-skills"
  fi
'';
```

Until the clone exists the three symlinks dangle, which Claude Code tolerates
— it just finds no skills.

## Apply

```bash
sudo nixos-rebuild switch --flake /persist/nixos-config#laptop
```

Then verify the symlinks resolve into the repo rather than into the store:

```bash
for d in skills agents commands; do readlink -f ~/.config/claude/$d; done
```

Each should print a `/persist/claude-skills/...` path.

## Plugins are not covered by this

`settings.json` in the other repo tracks `enabledPlugins`, but the installed
plugin cache under `~/.config/claude/plugins/` is runtime state and is not in
git. After a fresh install Claude Code starts with plugins enabled but absent;
reinstall them with `/plugin install`. Deliberately manual — plugin installs
hit the network, and a failed fetch should not be able to wedge a
`nixos-rebuild switch`.
