# Wireshark display filters (Member 4)

Capture interface: **Adapter for loopback traffic capture** (Npcap, Windows) / `lo` (Linux) / `Loopback: lo0` (macOS).
Capture filter (optional): `tcp port 5000`

| Purpose | Display filter |
|---|---|
| All lab HTTP traffic | `tcp.port == 5000 && http` |
| Requests only | `http.request` |
| Responses only | `http.response` |
| 404 responses | `http.response.code == 404` |
| 401 responses | `http.response.code == 401` |
| 429 responses (rate limit ON) | `http.response.code == 429` |
| Login attempts | `http.request.method == "POST" && http.request.uri contains "login"` |
| Repeated test endpoint | `http.request.uri == "/api/test"` |
| Specific client | `ip.src == 127.0.0.1` |
| TCP handshakes | `tcp.flags.syn == 1` |
| Time between requests | add column `frame.time_delta_displayed` |

Useful columns: `frame.number`, `frame.time_relative`, `ip.src`, `ip.dst`, `tcp.srcport`, `http.request.method`, `http.request.uri`, `http.response.code`.
Tip: Statistics > Conversations / HTTP > Requests, and right-click > Follow > HTTP Stream.

## Observations (fill with REAL packet numbers from your captures)

| # | Observation | Filter | Frames | Comment |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
