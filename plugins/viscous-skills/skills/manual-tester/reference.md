# manual-tester reference: heuristics, taxonomy, recipes

Load this when planning charters or when a session runs dry. SKILL.md has the rules; this has the material.

Sources of the ideas (secondary write-ups; the originals are James and Jonathan Bach's session-based test management
and the Rapid Software Testing heuristics at satisfice.com):
[SFDIPOT heuristic (Tessl)](https://tessl.io/registry/testland/sfdpot-exploratory-heuristic),
[charter template (Tessl)](https://tessl.io/registry/testland/exploratory-testing/1.0.6/files/references/charter-template.md),
[session sheet and metrics (Tessl)](https://tessl.io/registry/testland/exploratory-testing/1.0.6/files/references/session-sheet-and-metrics.md),
[running a session (Eurostar)](https://huddle.eurostarsoftwaretesting.com/session-based-test-management-part-3-session-based-exploratory-testing/),
[heuristics cheatsheet (QASkills)](https://qaskills.sh/blog/exploratory-testing-heuristics-cheatsheet),
[dogfood QA skill (hermes-agent)](https://claudemarketplaces.com/skills/nousresearch/hermes-agent/dogfood),
plus Playwright's own bundled `playwright-cli` and `playwright-trace` skills.

## 1. Charters (what to investigate; the how is your judgment)

A charter is a mission, not a test case. Pattern: **Explore `<area>` with `<resource / technique / data>` to discover
`<information or risk>`**.

Examples:
- Explore **sign-in** with **expired, reused and mistyped email codes** to discover whether failure states leak, loop or lock.
- Explore **the New-run form** with **empty, huge, unicode and double-submitted input** to discover validation gaps.
- Explore **every /app route** with **a dead network and 500s injected** to discover missing error states.

Time-box each charter (30-60 min of real time for a small site; shorter is fine). One charter, one note block in the
tracker. Stop when the charter is answered or the box ends, not when ideas run out; write the leftover ideas down as new
charters.

## 2. What to vary: SFDIPOT (James Bach's product checklist)

Walk these when choosing charters, so coverage is deliberate instead of whatever you noticed first.

| | Ask |
|---|---|
| **S**tructure | What is it made of? Routes, components, services, third-party scripts, build artefacts, config. |
| **F**unction | What does it do? Every feature, error handler, calculation, state change, background job. |
| **D**ata | What does it process? Valid / invalid / boundary / empty / huge / unicode / emoji / RTL / duplicate / stale. |
| **I**nterfaces | What does it touch? UI, API, URL params, deep links, OAuth redirects, email, wallets, webhooks, file upload. |
| **P**latform | What does it depend on? Browser, viewport, OS, locale/timezone, network speed, extensions, cookies on or off. |
| **O**perations | How is it really used? New vs returning user, first run, interrupted flow, two tabs, back button, long idle. |
| **T**ime | When does it matter? Timeouts, expiry (codes, sessions), ordering, race conditions, rapid repeats, clock changes. |

## 3. How to know something is wrong: oracles (HICCUPPS)

A bug is a mismatch with an expectation. Name the expectation in the issue ("Oracle:" field). Common oracles:
**H**istory (it used to / the demo does), **I**mage (brand and tone), **C**omparable products, **C**laims (README,
docs, marketing, the paper/PRD, UI copy), **U**ser expectations, **P**roduct (consistent with itself: same thing, same
look and behaviour everywhere), **P**urpose, **S**tatutes and standards (a11y, privacy, HTTP semantics).
Claims are the strongest oracle on a product like Mergit: UI copy says "leaves the choice for later" or "No sample
numbers"; check it.

## 4. Fault-injection recipes (Playwright)

Use these on every core flow; they find the bugs happy-path clicking never will.

```js
await ctx.setOffline(true);                                   // dead network mid-flow
await page.route("**/v0/plans", r => r.fulfill({ status: 500, body: '{"detail":"boom"}' }));   // server error
await page.route("**/v0/**", r => r.fulfill({ status: 401, body: '{"detail":"not signed in"}' })); // session expiry
await page.route("**/v0/**", async r => { await new Promise(s => setTimeout(s, 8000)); r.continue(); }); // slow API
await page.route("**/*.{png,jpg,mp4}", r => r.abort());       // missing media
await page.evaluate(() => localStorage.clear());               // lost client state
```

Also: double-click submit; submit then immediately reload; browser back/forward through a flow; open the same flow in two
tabs; paste 10k characters; `<script>alert(1)</script>` and `' OR 1=1 --` as text (observe encoding only, see rule 7);
leading/trailing spaces; emoji; right-to-left text; a second language/locale; zoom 200%; keyboard-only run.

## 5. Issue taxonomy (tag each issue)

`functional` · `ux` (confusing, dead end, no feedback) · `content` (wrong or stale copy, typos, claims that are not true)
· `visual` (layout, overflow, contrast, dark mode) · `a11y` · `performance` · `console/network` (errors, failed calls)
· `security-passive` · `data` (wrong numbers, wrong state) · `compat` (viewport, browser) · `flaky` (cannot repeat).

Severity: **High** blocks a core flow, loses data or money, or is a security issue. **Med** a feature is broken or wrong
and there is a workaround. **Low** cosmetic, noisy, edge case. Add **Check** for "suspected, not confirmed" and keep it
out of the severity counts.

## 6. Passive security and trust checks (observe only)

On the user's own site, without attacking anything:
- Response headers on the HTML and an API call: `Content-Security-Policy`, `X-Content-Type-Options`,
  `Referrer-Policy`, `Strict-Transport-Security`, CORS `Access-Control-Allow-Origin` (is it `*` on credentialed routes?).
- Session cookie flags: `HttpOnly`, `Secure`, `SameSite`. Anything auth-like in localStorage is worth a note
  (here `mergit-session` is in localStorage: record what is in it, not its value).
- Secrets or tokens visible in the bundle, console, URLs or error bodies. Stack traces or internal hostnames in
  errors.
- Mixed content, third-party scripts, source maps shipped to production.
- Protected routes while signed out; another user's id in a URL (only with the user's own two accounts).
Record findings as `security-passive`, severity per above, with the exact header or value observed.

## 7. Session notes and the PROOF debrief

At the end of each charter add a short block to the tracker:

```
### Session S-03: <charter>   (started 14:05, 40 min, signed in as <role>)
Past: what I did.   Results: what I found (ISS ids) and what passed.   Obstacles: what blocked or slowed me.
Outlook: what is still unexplored / next charters.   Feelings: where the product felt fragile or confusing.
```

"Feelings" matters: a flow that technically works but felt confusing is a real `ux` finding even with no error.

## 8. Evidence and post-mortems

- Prefer an **accessibility snapshot** (`page.accessibility`/`ariaSnapshot()`) over a screenshot to record what is on the
  page; keep screenshots for visual bugs.
- **Trace** each charter so a failure can be replayed later:
  `await ctx.tracing.start({ screenshots: true, snapshots: true });` ... `await ctx.tracing.stop({ path: "evidence/S-03.trace.zip" });`
  Then post-mortem without a browser: `npx playwright trace open <zip>`, `trace actions --errors-only`,
  `trace requests --failed`, `trace console --errors-only`, `trace snapshot <id>`. (`npx playwright` resolves from the
  project's `node_modules`; version 1.64 here.)
- **Video** for hard-to-describe interaction bugs: context option `recordVideo: { dir }`.
- `playwright-cli` (separate package, **not installed here**; check with `which playwright-cli`) adds `show --annotate`
  (the user draws on the live page and you receive the annotated screenshot and notes), `video-chapter`,
  `state-save`/`state-load` for auth reuse and `route`. If it is missing, do the same with `playwright-core` scripts.
- Save sign-in once with `ctx.storageState({ path })` into the profile dir, not the project, so later sessions skip the
  login (and never commit it).
