# Open-source due diligence — research inputs, not vendored code

We reviewed publicly available READMEs/protocol specifications/licence files on 2026-10-31. **No third-party project source code has been copied into the SuperScreen repository.** MIT and Apache licenses allow reuse with their notices; GPLv3 source may not be silently incorporated into a permissively licensed product. Review every dependency and binary redistributable separately.

| Project | Repository | Observed license | Approach |
|---|---|---|---|
| Extendo | https://github.com/Hafij-BGE/Second-monitor | MIT (checked root LICENSE) | Primary reference for Windows/Android UX, transport, reconnection, TLS, and Android decoding. If code is later incorporated, preserve copyright notices and THIRD_PARTY_NOTICES. |
| DDisplay | https://github.com/VedantJJA/DDisplay | README claims MIT; root LICENSE not found at check | Reference protocol architecture only until legal file verification; do not copy without checking licence details. |
| Virtual Display Driver | https://github.com/VirtualDrivers/Virtual-Display-Driver | MIT (checked root LICENSE) | Optional Windows IDD integration candidate; prefer signed releases, users must explicitly install and have recovery path. |
| Apollo | https://github.com/ClassicOldSong/Apollo | GPL-3.0 (checked root LICENSE) | Architectural reference only; no GPL code imported into MIT project. |
| Artemis/Moonlight Android | https://github.com/ClassicOldSong/moonlight-android | Root licence location unconfirmed | Architectural reference only; no source imported. |

Specific design lessons from [Extendo protocol v4](https://github.com/Hafij-BGE/Second-monitor/blob/main/docs/protocol.md): one transport-neutral stream protocol, TLS with pinned host identity, explicit local discovery packets, H.264 with timestamps, resize messages, touch/control backchannel and timebound pairing approval.

Specific design lessons from [DDisplay protocol draft](https://github.com/VedantJJA/DDisplay/blob/main/protocol/SPEC.md): well-specified handshake, codec negotiation, separate control/media message framing, negotiated size, and forward-compatible protocol versioning.

We deliberately implemented an independent simple Python prototype rather than claiming protocol compatibility with either upstream project. High-performance media and IDD require separate integration and licensing tests.
