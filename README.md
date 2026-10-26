# Discovery5AndroidUpgrade

Custom software for the aftermarket Android screen in a **2019 Land Rover Discovery 5 (L462)**.

## Goal

Keep wireless CarPlay's picture and touch controls on the Android screen while **music, calls, the factory microphone, and steering-wheel track controls use the iPhone's direct connection to Land Rover Discovery Bluetooth**. Fix the receiver behavior that takes audio back to `localhost` during connection or later transitions.

Selecting **USB** in the original Land Rover system currently restores music but loses the factory mic and steering-wheel track controls. The iPhone remains wireless. The complete observed behavior is in [screen specs](docs/screen-specs.md).

Also build a simpler Android home screen: **CarPlay first, Land Rover system second**, with unnecessary built-in shortcuts removed from the main view and a modern Land Rover-inspired appearance.

Preserve the owner's working automatic switch to the factory camera view when selecting reverse. Investigate an Android 15 upgrade separately from the launcher/receiver: the real board, compatible firmware, vendor integration, and recovery path must first be identified.

## Development direction

- **Native Kotlin** for new Android components; inspect existing Java/native code as needed. Flutter projects are references, not dependencies.
- **Python 3.9+ standard library + ADB** for the first host-side inventory/capture tool.
- Reuse the Mac's installed Android SDK, ADB, and JDK. Build with the Gradle wrapper when an Android module is introduced; avoid adding Flutter or an emulator workflow.
- Evaluate a replacement open-source receiver as well as the installed ZLINK implementation. The leading migration candidate is **F-e-n-y-x/CarLink**, distinct from the adapter-dependent **lvalen91/carlink**.

## Start here

1. [Screen specs](docs/screen-specs.md): device identity, observed failure, and missing information.
2. [Implementation plan](docs/implementation-plan.md): first coding task and vehicle acceptance criteria.
3. [Research](docs/research-findings.md): relevant source-code leads and their limits.
4. [Backlog](docs/backlog.md): prioritized remaining work, evidence required to close it, and open scope questions.

## Code now available

- [`tools/grab_apps.py`](tools/grab_apps.py): inventory and copy installed APKs through an existing ADB connection, with explicit target selection, hashes, and a capture manifest. Run `python3 tools/grab_apps.py --help` for usage.
- [`tests/test_grab_apps.py`](tests/test_grab_apps.py): mocked-ADB tests; run `python3 -m unittest discover -s tests -v`.
- Six upstream source references are pinned in [`upstreams.lock.json`](upstreams.lock.json). Third-party clones are not bundled. `carlink-direct` is the leading receiver candidate; Bluetooth, hardware and authentication compatibility remain unverified.

The official ZJINNOVA pages did not expose a public ZLINK source repository. None of these clones is official ZLINK source. Clone/inspect does not require Flutter or installing the upstream build toolchains.

## Status

**Paused at the owner's request on 2026-10-25.** The temporary installer download server is closed. Resume with the recorded connection findings and the inspection alternative below; no automatic follow-up is scheduled.

As of **2026-10-25**, the host-side APK grabber passes seven mocked-ADB tests, and six external source references are pinned for review. ADB and the Android SDK are installed on the Mac. The owner has read out Android 11/build information and opened Developer options, but no standard Wireless debugging entry was found. No ADB connection or capture has occurred; no Android app, OS port, or vehicle fix has been built or tested.

This public snapshot contains sanitized research and project-owned tooling. Private history, personal/company instructions, raw photographs, device/network identifiers, captures, credentials and third-party binaries are excluded. A public source repository does not constitute a public product launch.