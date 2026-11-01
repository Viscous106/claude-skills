---
name: manual-tester
description: Use when the user asks you to manually test, QA, click through or smoke-test a website or web app in a real browser (e.g. "test mergit.site", "go through every page", "check if everything works") and to keep track of what is broken. Drives a visible Chrome with Playwright on Hyprland workspace 5 so it never disturbs the user, asks the user for help only where a human is needed (login, OAuth, email codes, wallets), and writes a fix-ready issue tracker with evidence, debug detail and a suspected cause.
---

# manual-tester: test like a person, track like an engineer

The goal is two things: exercise the product the way a user would, and leave behind a tracker good enough that someone
(or a later session) can fix every problem **without re-running the test**.

## Rules

1. **Isolation.** All test browsers open on **Hyprland workspace 5**, silently. Never switch the user's workspace, never
   move, focus or close windows you did not create. Use a dedicated Chrome profile, never the user's real one.
2. **Track as you go.** Update the tracker the moment something fails, not at the end. Every issue needs the debug
   detail and a reason (see Tracker).
3. **Ask for help at human-only steps**, using `AskUserQuestion` or a plain message: logins, OAuth consent, email or SMS
   codes, captchas, wallet popups, payments. Say exactly what you need and what you will do after. Do not guess
   credentials, read secrets from disk, or work around auth.
4. **Never assert what you did not observe.** If a check was skipped or was inconclusive, record it as such.
5. **No fixes during the run** unless the user asks. Test, record, move on. Fixing comes after.
6. **Git is read-only** for you (user's global rule). Print commands for the user to run.

## Setup

### 1. Launch Chrome on workspace 5

Use `scripts/launch-chrome.sh <start-url>`. It starts a visible Chrome with a throwaway profile and a CDP port on
workspace 5 and prints the CDP URL. Details it relies on (all verified on this machine):

- Hyprland here uses the **Lua dispatcher**; the old `[workspace 5 silent]` rule syntax is rejected. The working form is
  `hyprctl dispatch 'hl.dsp.exec_cmd("<cmd>", { workspace = "5 silent" })'`.
- `HYPRLAND_INSTANCE_SIGNATURE` is not set inside the tool shell; derive it with `ls $XDG_RUNTIME_DIR/hypr | head -1`.
- Verify placement with `hyprctl clients -j` (class `google-chrome`, workspace id 5). Do not assume.

### 2. Sandbox

Chrome cannot start inside the Bash sandbox (`socket() ... Operation not permitted`, no Wayland access), so these
commands need `dangerouslyDisableSandbox: true`. That is expected and covered by the task: use it **only** for the
launch and the Playwright scripts, run everything else sandboxed, and tell the user once why. Without the sandbox the
network is open, so keep every script pointed at the target site only.

### 3. Drive it with Playwright

Use `playwright-core` from the project's `node_modules` (find with `find . -name playwright-core -maxdepth 4`) and
attach with `chromium.connectOverCDP("http://localhost:<port>")`. Reusing one browser across scripts is what lets the
user log in once by hand and have you continue in the same session. Scripts live in the scratchpad, not the project.

Run headed with `slowMo` ~100 ms so the user can watch.

## What to test (adapt to the product)

Work through these one by one, announcing each area before you start it:

1. **Every route** (from the router source or sitemap): status, `<title>`, an `h1`, no blank screen, no uncaught error.
   Also an unknown URL, and a deep link opened cold (refresh on a nested route).
2. **Console and network on every page**: `console.error/warning`, `pageerror`, failed requests, any HTTP >= 400.
   Separate expected noise (e.g. 401 while signed out) from real faults, but record both.
3. **Every link and button**: where does it go, does it work, are in-page `#anchors` real, do external links resolve.
4. **Forms**: empty submit, invalid input, valid input, double-click submit, error and success states.
5. **Auth** (with the user): each sign-in method, wrong or expired code, sign-out, session persistence on reload,
   protected routes while signed out.
6. **Core flows** end to end, then repeat once with bad input or a mid-flow reload.
7. **Responsive**: 390, 768, 1024, 1440. Look for horizontal scroll (`scrollWidth > clientWidth`), clipped or
   overlapping content, unreachable nav.
8. **Theme and state**: dark mode toggle, persistence after reload, no flash of wrong theme.
9. **Media**: video and images load, play, have alt text.
10. **Quick a11y**: keyboard tab order reaches the main actions, visible focus, labels on icon buttons.

Take a screenshot of every page and of every failure. Read the screenshots; do not assume a 200 means it looks right.

## Tracker

Keep **one file**, created at the start, in the project under `testing/<target>-<YYYY-MM-DD>/ISSUES.md`, with screenshots
and logs in `testing/<target>-<YYYY-MM-DD>/evidence/`. (Create the directory; tell the user it is untracked so they can
commit it.) Update it after every finding.

```markdown
# <target> test run, <date>
Env: <url>, Chrome <version>, viewport(s), signed in as <role or "signed out">
Scope tested / not yet tested: <lists>

## Issues
### ISS-001 [High|Med|Low] <short title>  (status: open)
- **Where:** <route>, <component or file if known>
- **Steps to reproduce:** 1. ... 2. ... 3. ...
- **Expected:** ...
- **Actual:** ...
- **Debug detail:** <exact console error, failing request URL + status + response body snippet, DOM/selector
  observed, viewport, timestamp>
- **Evidence:** evidence/ISS-001.png, evidence/ISS-001.log
- **Suspected cause:** <your reasoning, with file:line when you checked the source. Mark as "hypothesis" unless
  verified>
- **Suggested fix:** <one or two lines>
- **Needs user input:** <anything blocking a fix, or "no">

## Passed
- <check>: <what was observed>

## Skipped / inconclusive
- <check>: <why>

## Questions for the user
```

Severity: **High** = blocks a core flow, loses data or money, security issue. **Med** = feature broken or wrong with a
workaround. **Low** = cosmetic, noisy, or edge-case.

An issue without steps, evidence and a reason is not finished. If you could not find the cause, say so and list what you
ruled out, so the fixer does not repeat it.

## Finishing

1. Close the browser you launched: `kill` the pid `launch-chrome.sh` printed, and nothing else. Do not `pkill -f` or
   `pgrep -f | xargs kill` from a Bash call: the pattern matches the tool's own shell command line and kills it (exit
   144) before it kills Chrome. If you must search by pattern, use `ps -eo pid,args | grep "[p]attern"`. Then confirm with `hyprctl clients -j` that nothing of yours is
   left on workspace 5.
2. Print a summary: counts by severity, the top issues in priority order, what was skipped and why.
3. Print the git commands for the user to commit `testing/` if they want it kept. Do not run them.
