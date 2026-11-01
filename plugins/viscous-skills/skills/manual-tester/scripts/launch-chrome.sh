#!/usr/bin/env bash
# Launch a visible Chrome on Hyprland workspace 5 (silently, so the user's view never changes),
# with a throwaway profile and a CDP port for Playwright's connectOverCDP.
# Run outside the Bash sandbox (Chrome cannot start inside it).
#
# usage: launch-chrome.sh <start-url> [port] [profile-dir]
set -euo pipefail

url="${1:?usage: launch-chrome.sh <start-url> [port] [profile-dir]}"
port="${2:-9222}"
profile="${3:-$(mktemp -d)}"
workspace=5

# Not set inside the tool shell; take the running instance.
export HYPRLAND_INSTANCE_SIGNATURE="${HYPRLAND_INSTANCE_SIGNATURE:-$(ls "$XDG_RUNTIME_DIR/hypr" | head -1)}"

before="$(hyprctl activeworkspace -j | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')"

# Hyprland's Lua dispatcher: the old "[workspace 5 silent]" rule syntax is rejected.
hyprctl dispatch "hl.dsp.exec_cmd(\"google-chrome --user-data-dir=$profile --remote-debugging-port=$port --no-first-run --no-default-browser-check $url\", { workspace = \"$workspace silent\" })" >/dev/null

for _ in $(seq 1 30); do
  curl -s "localhost:$port/json/version" >/dev/null && break
  sleep 1
done
curl -s "localhost:$port/json/version" >/dev/null || { echo "Chrome did not come up on :$port" >&2; exit 1; }

after="$(hyprctl activeworkspace -j | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')"
[ "$before" = "$after" ] || echo "WARNING: active workspace changed ($before -> $after)" >&2

# The user may have their own Chrome open: find OUR window by the process that owns our profile, and wait for it to
# map (CDP comes up before the window does).
pid="$(pgrep -f -- "--user-data-dir=$profile .*--remote-debugging-port=$port" | head -1 || true)"
[ -n "$pid" ] || pid="$(pgrep -f -- "--user-data-dir=$profile" | head -1)"
placed=""
for _ in $(seq 1 20); do
  placed="$(hyprctl clients -j | PID="$pid" python3 -c '
import json,os,sys
for c in json.load(sys.stdin):
    if c["pid"] == int(os.environ["PID"]):
        print(c["workspace"]["id"]); break')"
  [ -n "$placed" ] && break
  sleep 0.5
done

echo "CDP:     http://localhost:$port"
echo "profile: $profile"
echo "pid:     $pid   (kill this pid to close the test browser)"
echo "window:  workspace ${placed:-NOT FOUND} (expected $workspace)"
[ "$placed" = "$workspace" ] || { echo "WARNING: test window is not on workspace $workspace" >&2; exit 2; }
