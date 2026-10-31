# apiKeysKaJugad: reference

Facts about provider headers below are from memory of provider docs. Verify against the provider's current docs
before relying on them, and say so in the README you write.

## Data model

```
Key   { index: usize, secret: String (never logged), state: Ok | Cooling{until} | Dead, last_used: Instant }
Pool  { keys: VecDeque<Key> }          // back = top (next to use); front = bottom
```

`index` is the key's position in the file at start-up and never changes. Logs and `status` use it.

## Picking and rotating

```
fn acquire(now) -> Result<KeyHandle, AllLimited{next_at}>
    # scan from the back (top) towards the front
    for key in pool.back_to_front():
        if key.state == Dead:                continue
        if key.state == Cooling{until} and until > now: continue
        if key.state == Cooling{until} and until <= now: key.state = Ok
        return handle(key)               # leave it in place: LIFO keeps using it until it fails
    return AllLimited{ next_at: min(until of every Cooling key) }   # None if every key is Dead

fn on_rate_limited(handle, retry_after, now)
    key = pool.remove(handle)
    key.state = Cooling{ until: now + clamp(retry_after or DEFAULT_COOLDOWN, MIN, MAX) }
    pool.push_front(key)                 # "popped and appended again": goes to the bottom

fn on_auth_failed(handle)               # 401 / 403
    key.state = Dead; log(index)         # stays out for the life of the process
```

Lock the pool only for these small operations. Never hold the lock across a network call. Concurrent requests all use
the current top key until it is limited; each request that gets a 429 rotates on its own. A key already rotated by
another request must not be rotated twice: compare the handle's generation before applying `on_rate_limited`.

## Request flow

```
for attempt in 0..max_attempts (default: number of keys + 1):
    key = acquire(now)   or return 429/503 with Retry-After = next_at - now and a JSON error body
    resp = forward(request_copy, key)
    match resp.status:
        2xx/4xx other than 401/403/429 -> return it (it is the provider's real answer)
        429                            -> on_rate_limited(key, retry_after(resp)); continue
        401 | 403                      -> on_auth_failed(key); continue
        5xx / transport error          -> backoff, retry the SAME key up to a small cap, then return the error
return the last response, or AllLimited
```

## Reading the limit from the response

- `Retry-After` (seconds) on a 429 sets the cooldown. A daily-quota 429 may carry a very large value: clamp to a
  configured maximum, and do not trust a missing or zero value (use the default).
- If the provider sends remaining-capacity headers on successful responses (for example `x-ratelimit-remaining-tokens`
  and `x-ratelimit-reset-tokens`), you may rotate early when remaining capacity is about to run out. This is an
  optimisation; the 429 path must work without it.
- A 429 can mean requests-per-minute or tokens-per-day. Both are handled the same way; only the cooldown differs.

## Config (example)

```toml
[server]
listen = "127.0.0.1:8787"
token_file = "proxy-token.txt"          # callers send: Authorization: Bearer <this>

[[provider]]
name = "groq"
base_url = "https://api.groq.com/openai/v1"
keys_file = "groq-keys.txt"             # one key per line, chmod 600, gitignored
default_cooldown_s = 60
max_cooldown_s = 86400
max_attempts = 0                        # 0 = number of keys + 1
state_file = "keyrelay-state.json"      # optional: cooldowns survive a restart
```

Route by prefix (`/groq/v1/...`) when several providers are configured; with one provider the plain `/v1/...` path
works.

## Errors the proxy returns itself

All as JSON `{"error": {"type": ..., "message": ...}}`:

- all keys limited: HTTP 429 with `Retry-After`, message names how many keys and when the first is usable;
- every key dead: HTTP 503, message says to replace the keys;
- missing or wrong proxy token: HTTP 401.

Never include any part of a key in an error body.

## Tests (write them first)

Use a stub provider (a small local server) so no real key or network is needed.

1. **LIFO order:** with keys [a, b, c], the first request uses c, the next also c while it is healthy.
2. **429 rotates:** c returns 429 with Retry-After 30; the same request succeeds on b; c is now at the bottom, cooling.
3. **Cooldown applies:** while c cools, requests use b; after the cooldown they use whichever key is on top and
   usable.
4. **Skip cooling keys:** a pool where every key but one is cooling always yields the one that is not.
5. **All limited:** every key 429; the response is 429 with `Retry-After` equal to the soonest cooldown end.
6. **Dead key:** a 401 sets the key aside, the request retries on the next key, and the dead key is never used again.
7. **All dead:** returns 503.
8. **Missing Retry-After / zero / huge:** default, default, and clamped-to-max respectively.
9. **5xx:** retried on the same key with backoff, not rotated.
10. **No secrets in logs:** run a rotation with a recognisable fake key, capture all log output and the error bodies,
    assert the fake key text is absent.
11. **Concurrency:** many parallel requests while the top key starts returning 429; no panic, no key lost or
    duplicated, and the pool length is unchanged at the end.
12. **Pool of one:** a single key works, and when it is limited the error is the all-limited one.
13. **Proxy token:** a request without the token is rejected before any provider call is made.
14. **Body replay:** a request with a body that needs a retry sends the identical body to the second key.
15. **Streaming:** a 429 before the first byte is retried on the next key; a failure after streaming starts is passed
    through unchanged.

## What to report when done

Say exactly what was tested (stub provider, which of the tests above) and what was not (a real provider, real
streaming, long soak). Do not call it production-ready.
