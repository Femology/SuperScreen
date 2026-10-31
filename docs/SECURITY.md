# Security model and limitations

## Phase 1 is not suitable for public networks

The prototype carries screen images and a bearer token over HTTP/WebSocket with no TLS. A hotspot participant, hostile local network, or compromised device can potentially intercept the traffic or use a token. Use **only your personally controlled phone hotspot**, with a strong WPA2/WPA3 hotspot password, and avoid sensitive windows while testing. Do not forward TCP 8765 to the internet. The first version has no remote mouse, keyboard or shell control.

Pairing is restricted to five invalid attempts per IP per minute, uses a single-use six-digit code and issues a random 32-byte viewer token. Tokens are saved as SHA-256 digests on Windows and as a local browser session credential on Android. Browser storage is not hardware protected. Token rotation/revocation is currently available through the Python PairingManager API; a user-facing revoke button is planned.

**This is explicitly a prototype**. Do not mistake a pairing code on HTTP for end-to-end authenticated encryption.

## Phase 2 security requirements
- TLS 1.3 or suitable mutually authenticated encrypted transport for all control/video traffic.
- Device identity, certificate pinning and simple key revocation UI.
- Manual first-pair confirmation on the PC or explicit USB trust bootstrap.
- Restrict inbound Windows firewall rule to the trusted hotspot profile/address; do not open Public network profile.
- Bound frame sizes and capture limits, and fuzz input messages.
- Opt-in remote input; rate limits on commands; allowlist of possible messages.
- Do not capture Windows UAC secure desktop, login or other protected surfaces unless explicitly implemented and tested within OS-supported interfaces.
- Preserve clear third-party licence notices and pinned dependency audits.

## Vulnerability reporting

Until a private reporting channel is established, open a minimal GitHub issue without attaching tokens, passwords or captured screenshots. Do not publicly paste secret keys.
