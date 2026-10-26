# Project backlog

Updated **2026-10-25**. Hands-on vehicle work is **paused at the owner's request**. This backlog records future work; it does not schedule an automatic restart.

## Work to resume

| Priority | ID and work | Evidence needed to close |
| --- | --- | --- |
| P0 | **D5-001 — Identify the actual hardware and obtain inspection access** | Establish actual Android API, board/SoC, ABI and privileges; preserve readable launcher, ZLINK and integration APKs with hashes. Use verified ADB access or App Manager No-root inspection/export. Record that the first capture is after the reported reset/restart. |
| P0 | **D5-002 — Trace factory switching and preserve cameras** | Identify the manual OEM-switch operation and reverse-trigger ownership. Vehicle tests show factory camera priority from Home and CarPlay, and document behavior leaving reverse. Use those findings to simplify switching; physical-button support remains conditional on verified input and controller behavior. |
| P1 | **D5-003 — Build our own native Kotlin launcher** | CarPlay first, Land Rover system second, Settings secondary; verified receiver launch and OEM-switch bindings. Home/Back, restart behavior and camera interruptions pass on the installed screen. Automatic CarPlay startup is not assumed. |
| P1 | **D5-004 — Adapt a receiver we can modify and fix audio ownership** | Evaluate CarLink/DiPlay hardware and authentication compatibility. Wireless CarPlay retains direct iPhone-to-factory-Bluetooth music, calls, microphone and wheel controls across calls, Siri, navigation and reconnects without manual output selection. Record connection latency and phone-heating observations separately from routing acceptance. |
| P1 | **D5-005 — Diagnose power-off behavior and battery drain** | Identify relevant ACC/controller, Android sleep/wakelock and wiring behavior. Measure shutdown timing and current draw, then verify vehicle sleep/wake physically. An Android sleep message alone does not close this issue. |
| P2, conditional | **D5-006 — Assess an Android 15 port** | Identify a compatible board-specific build or establish generic-image compatibility, required vendor interfaces, original firmware and a usable recovery route before flashing. Boot success and full vehicle acceptance remain separate. |

Detailed sequencing and acceptance scenarios: [implementation plan](implementation-plan.md). Current identifiers and observations: [screen specs](screen-specs.md).

## Work already recorded

- [Research findings](research-findings.md) preserve source links, receiver/code leads, USB-role findings, related-owner reports, uncertainty and compatibility limits. No exact-unit ADB procedure or complete vehicle fix is verified.
- The host-side [APK grabber](../tools/grab_apps.py) has seven recorded passing mocked-ADB tests; no real device capture has occurred.
- Six upstream source references are pinned in [upstreams.lock.json](../upstreams.lock.json). Clones are not bundled; these are references, not proven compatible applications.
- Raw photos, network-attempt records and third-party installers are excluded. A checked App Manager 4.1.1 installer was prepared privately; head-unit installation remains unconfirmed and the temporary download server is closed.

## Confirmed scope and publication

- **Launcher:** the owner confirmed that the requested future work is our own Android launcher. A separate public product launch has not been requested.
- **Source publication:** this repository contains a sanitized snapshot of the research and project-owned tooling. Private history, personal/company instructions, device evidence and third-party binaries are excluded.
