---
name: api-keys-ka-jugad
description: Use when the user asks for an API key rotator, a key pool, "apiKeysKaJugad", or a way to use many API keys for one provider (rotate on rate limit, always use a key that still has capacity). Builds a small standalone OpenAI-compatible proxy that any project points its base URL at. Not Mergit-specific.
---

# apiKeysKaJugad: a key rotator you can reuse in any project

Build one small local proxy, not a per-language library. Projects set their provider base URL to the proxy and send a
dummy key; the proxy swaps in a real key and rotates when one is spent.

Details, pseudocode and the full test list are in [reference.md](reference.md). Read it before writing code.

## Say these three things first (before building)

State them plainly. Do not skip them because the user "just wants it built".

1. **Limits may be per organization, not per key.** For some providers (Groq, as recalled from its docs: verify the
   current docs) the rate limit applies to the whole account/org, so many keys from one account share one limit and
   rotation gains nothing. It only helps with keys from separate accounts.
2. **Terms of service.** Using many separate accounts' free keys to get around limits may breach the provider's terms.
   Tell the user to read them. It is their decision; do not refuse, do not lecture.
3. **There is no "credits left" to query** on most free tiers. The tool can only learn a key is spent from a 429, and
   from `x-ratelimit-remaining-*` style headers where the provider sends them. It reacts; it cannot know in advance.

## Ask only what you cannot default

- **Language.** Default Rust (axum + reqwest, one binary to drop anywhere) if the user has a Rust stack; otherwise
  Python (FastAPI + httpx) or Go. Offer, then proceed with the default if they have no preference.
- **Provider(s).** Design for any OpenAI-compatible provider from the start (config lists providers); start with the
  one the user names.

## Behaviour to build (this is the user's spec; keep it exactly)

- Keys form an ordered list. The **top** key is the last one; use it until it fails (LIFO), so keys are spent one at a
  time.
- On **429**: pop that key, append it to the **bottom**, set its **cooldown** from `Retry-After` (fall back to a
  configured default), and **retry the same request immediately on the next usable key**.
- On **401/403**: the key is revoked or invalid. Set it aside for the life of the process and log it **by index**.
- A key in cooldown is **skipped**, so callers always get a key that has capacity.
- **All keys limited**: return a clear error with the soonest time any key becomes usable; never hang.
- **5xx and network errors**: retry on the same key with backoff; they are not quota problems.
- A single key must work (a pool of one).

## Proxy rules

- Forward `/v1/*` (and the provider's equivalent) to the provider with the chosen key set in `Authorization`.
- Buffer the request body so it can be replayed on a retry.
- **Streaming**: retry only before the first response byte is sent. A mid-stream failure cannot be recovered; pass it
  through.
- The proxy must not be an open relay: require a caller token (`Authorization: Bearer <proxy token>`), and bind to
  `127.0.0.1` by default.

## Security (non-negotiable)

- Keys live in a file (one per line, `chmod 600`) or env, never in the repo. The user builds the file; **never ask the
  user to paste keys into the chat, and never print them in commands you write.** Add the file's path to
  `.gitignore`.
- Never log a key or any fragment of one. Log the key's **index** (and, if useful, a short hash of it).
- `status` output shows index, state (ok, cooling, dead) and when a key is next usable. No secrets.

## Deliverables

- The proxy, a config example (`keyrelay.example.toml`), and a README with: run command, how to point a project at it,
  the three caveats above, and a `docker`/`systemd` snippet.
- CLI commands: `serve`, `status`, `check` (one cheap authenticated call per key; report valid, dead or limited).
- Optional: persist cooldowns to a file so a restart does not re-hit spent keys.

## Tests that must exist (guards that fire, not only the happy path)

See [reference.md](reference.md) for the list. At minimum: LIFO order; a 429 rotates and applies the cooldown; a
cooling key is skipped; all-limited returns the right error and the soonest time; a 401 sets the key aside; no key text
in any log; concurrent requests do not corrupt the pool.

## Verify before claiming it works

Run the test suite, then run the proxy against a stub provider that returns 429 for the first N keys and show the
request succeeds on key N+1 and that `status` reflects it. Say what was not tested (real provider, streaming).
