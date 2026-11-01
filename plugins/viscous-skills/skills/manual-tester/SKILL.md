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
7. **Passive only on security.** Observe headers, cookies, bundles and error bodies on the user's own site. Do not
   brute-force, fuzz auth, hammer endpoints, test other people's accounts, or send payloads beyond harmless text. The
   only email you request a code for is one the user gave you; never type a code the user did not give you.
8. **Reproduce before you log.** Re-run a failure once (ideally fresh state) and record how often it happened (3/3, 1/3).
   If you cannot repeat it, log it as `flaky` with what you saw, not as a confirmed bug.
9. **Name the oracle.** Every issue says which expectation it violates (UI copy, docs, the demo, the PRD or paper, a
   standard, consistency with another screen). "Looks wrong" is not an issue.
10. **Do not trust a green status.** A 200 and no console errors say nothing about whether the page is right. Look at the
    screenshot or accessibility snapshot of every page you claim passed.

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

Run headed with `slowMo` ~100 ms so the user can watch. Reuse one Chrome profile (a dedicated dir, never the user's) so
a login done once by hand survives relaunches. `playwright-cli` is an optional extra (annotate-on-page feedback, video
chapters) and may not be installed: check `which playwright-cli` and fall back to `playwright-core` scripts.

## How to run it: charters, not a flat checklist

Work in short, named **sessions**, each with a charter: *Explore `<area>` with `<technique/data>` to discover `<risk>`*.
Plan the charters up front from the **SFDIPOT** checklist (Structure, Function, Data, Interfaces, Platform, Operations,
Time) so coverage is deliberate, tell the user the list, then run them one at a time. Per session:

1. Announce the charter. Start a Playwright **trace** for it (`ctx.tracing.start`) so any failure can be replayed.
2. Test, mixing happy path, edge data, and **fault injection** (offline, injected 500/401, slow API, double submit,
   reload mid-flow, two tabs; recipes in [reference.md](reference.md)).
3. Log issues immediately; stop the trace into `evidence/<session>.trace.zip`.
4. Close with the short **PROOF** debrief (Past, Results, Obstacles, Outlook, Feelings) in the tracker. "It felt
   confusing" is a valid `ux` finding even with no error.
5. Leftover ideas become new charters, not scope creep inside the current one.

Read [reference.md](reference.md) before planning: SFDIPOT, oracles (HICCUPPS), fault-injection recipes, issue taxonomy,
passive security checks and the evidence/post-mortem commands (`npx playwright trace ...`).

## Baseline coverage (adapt to the product)

Whatever the charters, make sure these have been covered by the end, announcing each area before you start it:

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
10. **Quick a11y**: keyboard tab order reaches the main actions, visible focus, labels on icon buttons, Escape closes
    dialogs, focus returns after a dialog, headings in order.
11. **First-run vs returning user**: a fresh account, then the same account after reload, sign-out and sign-in. State that
    lives only in memory shows up here.
12. **Claims vs reality**: every promise in UI copy, marketing and docs ("start free", "no wallet needed", "nothing is
    paid until you approve") gets tried and confirmed or logged as `content`.
13. **Passive security** (see rule 7 and reference.md section 6): headers, cookie flags, what sits in localStorage,
    secrets in the bundle or errors, protected routes when signed out.

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
### ISS-001 [High|Med|Low] <short title>  (status: open)   tags: functional|ux|content|visual|a11y|performance|console/network|security-passive|data|compat|flaky
- **Where:** <route>, <component or file if known>
- **Found in session:** S-03 (<charter>)   **Frequency:** 3/3   **Affects:** <who / which state, e.g. new accounts only>
- **Steps to reproduce:** 1. ... 2. ... 3. ... (start state: signed out / fresh account / viewport)
- **Expected:** ...   **Oracle:** <which expectation: UI copy "...", PRD/paper section, demo behaviour, standard>
- **Actual:** ...
- **Impact / workaround:** <what the user loses; how to get around it, or "none">
- **Debug detail:** <exact console error, failing request URL + status + response body snippet, DOM/selector
  observed, viewport, timestamp>
- **Evidence:** evidence/ISS-001.png, evidence/ISS-001.log
- **Suspected cause:** <your reasoning, with file:line when you checked the source. Mark as "hypothesis" unless
  verified>
- **Suggested fix:** <one or two lines>
- **How to verify the fix:** <the exact steps/assertion that proves it is fixed; ideally a Playwright snippet or e2e
  test name that would have caught it>
- **Needs user input:** <anything blocking a fix, or "no">

## Sessions
(one PROOF block per charter, see reference.md section 7)

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
2. Print a summary: counts by severity (excluding `Check`/`flaky`), the top issues in priority order, coverage by
   SFDIPOT dimension (what was and was not touched), what was skipped and why, and a **fix order** that groups issues by
   shared cause (one change that closes several). Offer to turn the "How to verify the fix" lines into e2e tests.
3. Print the git commands for the user to commit `testing/` if they want it kept. Do not run them.
