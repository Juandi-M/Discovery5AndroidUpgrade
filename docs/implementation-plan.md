# Implementation plan

Updated **2026-10-25**. Goal and observed routing: [README](../README.md) and [screen specs](screen-specs.md). The host-side APK grabber is implemented and tested with mocked ADB; no device capture or Android implementation has been completed.

Priorities and completion evidence are tracked in the [project backlog](backlog.md); this document retains the engineering sequence and acceptance details.

## Resume point

The owner paused hands-on work on **2026-10-25**. The Mac and screen reached the same Wi-Fi network, but network ADB refused port 5555 and the connected USB cable produced no enumerated peripheral. No ADB session exists. Do not repeat FactorySet guidance or assume selecting MTP solves the USB role problem.

The official **App Manager 4.1.1** installer was checked against its GitHub release digest and its APK signature verified. The installer is not bundled and head-unit installation is unconfirmed. A temporary local download server was stopped. On a future device-testing session, recheck network addresses and use the documented No-root inspection/export route if appropriate. Any first device capture is after the reported reset/restart; no firmware flash or automatic follow-up is scheduled.

## 1. Grab the installed apps and inspect the hardware

[`tools/grab_apps.py`](../tools/grab_apps.py) uses the standard library and the existing ADB installation. It lists devices, requires an explicit target for inspection, records build/package/HOME information, and copies selected installed APKs with hashes and a manifest.

```sh
python3 tools/grab_apps.py --devices
python3 tools/grab_apps.py --serial DEVICE --inventory
python3 tools/grab_apps.py --serial DEVICE --package LAUNCHER_PACKAGE --package ZLINK_PACKAGE
```

Replace `DEVICE` and the package placeholders with observed values. This tool uses an existing ADB connection; it does not enable or connect network debugging. Identify the current Home launcher and actual ZLINK package from inventory before selecting them. APKs are compiled apps; decompilation can reveal implementation details but does not recover the original source project.

Remaining capture work:

- Inspect the head unit's available Android Bluetooth/network APIs and privileges.
- Add targeted audio/vendor-service diagnostics and bounded runtime logs when needed; keep originals under `.local/` and record partial failures.

Real capture requires the car and a supported ADB connection. Try Wi-Fi access first to avoid removing dash trim; supported network debugging and USB roles remain unknown. An APK copy is not a complete firmware rollback backup.

Current transport checks found the screen reachable on Wi-Fi but port 5555 refused ADB; the attached A-to-C cable produced no USB peripheral enumeration on the Mac. No exact-unit connection procedure has been verified. An alternative is **App Manager in No-root mode** on the screen to read device/app metadata and export readable installed APKs before ADB is available. Those APKs can be inspected for actual vendor USB/network controls. This is an inspection path, not a way to bypass ADB authorization or grant system privileges. The first exported state will be after the owner's unexpected reset/restart; preserve that provenance. Sources and limitations are in [transport research](research-findings.md#usbadb-access-investigation).

## 2. Evaluate receiver migration

Start with the locally cloned **F-e-n-y-x/CarLink** (`vendor/carlink-direct`), a native Kotlin receiver for generic Android ARM devices with wired/wireless iPhone CarPlay and a factory-Bluetooth audio setting. Its DiPlay engine changes the receiver's advertised audio capabilities, rather than merely muting playback. Test compatibility before deciding whether to adapt its reusable core into our launcher or run a separate receiver app.

- Verify actual Android API/ABI and access to Bluetooth. Some retrofit Bluetooth modules are inaccessible to ordinary Android apps even while stock ZLINK works; the published workaround for those modules currently covers Android Auto, not iPhone CarPlay.
- Source builds omit CarPlay authentication assets. Determine the compatible authentication integration before treating a compiled APK as a working receiver. Existing release behavior and head-unit authentication services need assessment.
- Keep installed vendor services and the current receiver available during testing, with only one projection receiver active at a time.
- OpenAutoLink is also cloned but currently targets Android 12L+ GM AAOS and its wireless CarPlay is unverified/not working on the maintainer's vehicle. DiPlay itself is BYD-focused. Neither is assumed compatible with LR_J.
- Inspect upstream build requirements before installing anything: current CarLink/DiPlay builds require newer SDK/JDK/NDK packages than the Mac's verified SDK 35/36 and JDK 21. No upstream build or extra toolchain installation has occurred.

## 3. Locate the audio takeover

While parked, capture the working factory-Bluetooth state and the transition to `localhost`. Note the phone/iOS version, connection order, factory source, answer method, and event times.

Inspect the exact APKs with JADX and native-library tools as needed. Find receiver capability negotiation, audio-transfer modes, call/audio events, and vendor-service bindings. Correlate code with runtime evidence. Android muting cannot itself stop the iPhone choosing CarPlay audio; Carlinkit command IDs are not ZLINK APIs.

Deliverable: the responsible control point, evidence for it, required permissions, and a restoration procedure. Choose an existing API, a targeted patch/hook, or a replacement component from those findings. Preserve signature, activation, and accessory-authentication dependencies.

## 4. Implement and test the change

Use native Kotlin for new Android code. Add native code only if analysis requires it. Reuse the installed SDK/JDK and build through Gradle without an emulator. Match the real head unit's API/ABI and privileges before choosing dependencies or packaging.

The Silverado receiver code is a reference. Adopting a Carlinkit dongle would be a separate hardware choice, not a prerequisite or an APK-only ZLINK update.

| Vehicle scenario | Required result |
| --- | --- |
| CarPlay startup and repeated reconnects | Picture/touch work; factory Bluetooth audio stays usable without manual output selection |
| Music, pause/resume, next/previous | Audio and steering-wheel track controls work |
| Incoming/outgoing calls; CarPlay and OEM answer controls | Both parties hear each other through the factory audio/mic path; hangup and music resume work |
| Siri, navigation prompts, notifications | Input/output and interruption/resume work without persistent route takeover |
| Select reverse from Home, CarPlay, and the factory view | Factory camera view takes priority; record timing and behavior on leaving reverse |
| Phone/screen restarts and vehicle sleep cycle | The desired arrangement recovers consistently |
| Failure/restoration | Original behavior can be restored using the prototype's documented procedure |

Record repeated runs and failures. Build/test success on the Mac is separate from physical vehicle acceptance.

## Custom home screen

Build a native Kotlin launcher/home app with **CarPlay** as the main action and **Land Rover system** as the second action. Keep Settings secondary and omit built-in Navigation, Media, Phone, and App Mirror shortcuts from the main view. Voice assistant is optional and depends on actual installed support and microphone access.

- Design a modern Land Rover-inspired interface sized for the actual display; this changes the Android home screen, not the original infotainment firmware.
- Discover the installed ZLINK launch activity and the current launcher's Back to system command. Do not guess package names or OEM-switching intents.
- Keep the original launcher and vendor integration services available while testing. They may supply camera, parking, audio, or switching functions beyond the visible home screen.
- Preserve the owner's newly reported automatic return to the factory camera view on selecting reverse. Trace this separately from the manual Back to system command; do not assume both use the same Android API. Camera priority must not depend on our launcher remaining in the foreground.
- Check whether this firmware allows a replacement Home app and whether its startup behavior respects that selection. Android version and vendor behavior determine the integration method.
- UI work can proceed before the commands are bound, but unresolved actions must be clearly identified. Test Home/Back, display switching, ZLINK launch, camera/parking overlays, and restart behavior on the device.

Reordering or replacing the launcher does not itself repair CarPlay audio routing. Startup should not be changed to automatically open CarPlay without a separate owner preference.

## Android 15 feasibility

The owner wants to explore replacing the underlying Android installation as well as the launcher and receiver. An Android 15 port is a separate hardware-compatibility investigation; launcher and receiver work can proceed on the current firmware. No compatible Android 15 image or restoration method has been established for this board.

1. Identify the real API/framework, SoC/board, CPU ABI, kernel, vendor build, partition layout, bootloader capabilities, and Treble/cross-version compatibility. The current APK grabber covers only part of this inventory; it does not collect a firmware recovery backup.
2. Obtain the exact board-matched original firmware and a usable recovery procedure. Preserve readable originals and hashes where access permits. Copying APKs alone cannot restore a failed OS flash.
3. Map the required vendor services, libraries, framework changes, permissions/signatures, and controller interactions for reverse-trigger switching, touch/display, Bluetooth, audio, and ACC/sleep. Retaining an MCU does not establish that a generic Android image can communicate with it; copying a vendor APK does not establish that it will run on Android 15.
4. Evaluate a board-specific supported Android 15 build or a compatible Generic System Image only after those facts are known. A generic image omits manufacturer customizations. Successfully booting is separate from preserving vehicle integration.
5. Establish a boot/recovery path and test camera priority, manual switching, wireless connection, audio/microphone/wheel controls, and vehicle shutdown before treating an OS port as usable.

Sources: [Android architecture](https://source.android.com/docs/core/architecture) and [Google's GSI compatibility/recovery requirements](https://developer.android.com/topic/generic-system-image). These explain the general requirements; neither confirms LR_J support. No bootloader setting, MCU/CAN firmware, or installed OS has been changed by this project.

## Subsequent work

- **Interface switching:** trace Back to system and the two-finger return path separately; reuse verified vendor/controller commands. Screen switching, factory audio-source selection, and OEM firmware access are distinct operations.
- **Power-off fault:** investigate sleep/wakelocks, ACC/CAN/controller state, and wiring; physically verify timing and current draw. An Android sleep report alone does not prove the battery-drain issue fixed.
