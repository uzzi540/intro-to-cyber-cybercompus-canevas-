# Timeline, fact/hypothesis table, risks and recommendations (Member 5)

## Timeline (>= 5 events, use real timestamps from the captures / backend/logs/access.log)
| # | Time | Event | Source (frame / log line) |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

## Fact / hypothesis / verification
| Fact (proved) | Hypothesis | How to verify |
|---|---|---|
| e.g. 40 GET /api/test in 2 s from 127.0.0.1 | Load test, monitoring script, or flooding attempt | Check User-Agent, server log, repeat with rate limit ON, ask the person who ran it |
| e.g. 3 x 401 on /api/login | Forgotten password OR guessing | Look at timing, usernames, later success |

Key point for the defense: **a repeated request alone is not proof of an attack** - volume, intent, authorization, origin and outcome must be considered.

## Risks and recommendations
| Risk | Recommendation | Justification |
|---|---|---|
| Cleartext HTTP exposes credentials/tokens to anyone on the path | Enforce HTTPS (TLS) | Login body and Bearer token are readable in Wireshark |
| Unlimited requests -> resource exhaustion / brute force | Rate limiting (`CC_RATE_LIMIT=on` demo) | Returns 429 + Retry-After |
| No monitoring of failed logins / bursts | Centralized logging + alerting | `backend/logs/access.log` correlates with PCAP |
(Optional) Segmentation: separate web, database and admin networks.
