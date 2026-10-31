# Roadmap and test gates

**Vision:** A native Windows/Android second-screen product with a beautiful UI, hotspot-first offline networking, secure pairing, one-tap reconnection, input control, real extend, USB fallback and broken-screen rescue. Passing one gate does not imply another is implemented.

## Phase 0 — Baseline and safety
- [x] Create repository, OSS evaluation, architecture and test framework.
- [x] Separate mirroring from virtual-monitor support.
- [ ] Baseline test on the damaged HP, external LG display and Android phone. Document which GPU, Windows build and phone model were used.
- **Gate:** reversible setup; no external-monitor loss.

## Phase 1 — Hotspot browser mirror
- [x] Windows capture pipeline; authenticated WebSocket; browser viewer.
- [x] User-selected monitor, FPS counter and local reconnect attempt.
- [x] Auth, network, JPEG and server unit tests.
- [ ] Real Windows/Android hardware acceptance test.
- **Gate:** phone hotspot ON, laptop autojoins saved network; no second handset; phone displays TV/Windows output; keyboard and mouse still work; no mobile data required.

## Phase 2 — Native Android
- [ ] Compose UI, MediaCodec renderer, remembered pairing, foreground streaming service.
- [ ] Data safety, screen power, background behavior, orientation handling.
- **Gate:** 30 minutes streaming; rotate; background and return; recover from hotspot disconnect.

## Phase 3 — Windows capture and encoding
- [ ] DXGI Desktop Duplication (or Windows Graphics Capture) and hardware H.264 encoder.
- [ ] Frame pacing, delta updates, backpressure, capture restart.
- **Gate:** benchmark 720p/1080p at 30/60 FPS on supported hardware; report latency, frame drops, CPU and RAM.

## Phase 4 — Real extended display
- [ ] Evaluate approved signed virtual display driver with explicit admin approval.
- [ ] Accurate monitor identity, extend/duplicate mode, per-device display layout.
- [ ] Detect lost display, restore previous arrangement, rollback/recovery.
- **Gate:** exactly one new Windows monitor enumerates, can move a window onto it, unplug returns window to safe monitor; test 20 reconnections.

## Phase 5 — Broken-screen rescue
- [ ] Make phone-accessible display primary only after authentication.
- [ ] Desktop/window recovery even when internal LCD is physically damaged.
- [ ] Login-screen behavior documented with actual Windows tests; no unsupported promise.
- **Gate:** power off, boot, sign in, reconnect without TV on supported devices; if not possible, explicit fallback.

## Phase 6 — Control + transport
- [ ] Touch, drag, scroll, right-click and keyboard; opt-in input permission.
- [ ] USB ADB/USB tether transport fallback; local hotspot transport selection.
- [ ] TLS 1.3, pinned device identity, revocation, replay protection.
- **Gate:** transport switching, input accuracy, permission revocation, threat-model tests.

## Phase 7 — Release
- [ ] Signed Windows installer/uninstaller, Android release APK, CI matrix and GPU lab testing.
- [ ] WCAG-minded UI accessibility, documentation and benchmarks.
- **Gate:** zero outstanding critical vulnerabilities; support matrix, automated install/uninstall and rollback tests.

## Performance target, not result

Start with reliable 720p/30 FPS native video, then target 1080p/60 FPS with hardware acceleration. Report measured median and p95 end-to-end latency. Performance claims must be tied to real device logs.
