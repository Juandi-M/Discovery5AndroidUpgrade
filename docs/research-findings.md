# Research leads for implementation

Reviewed in this project on **2026-10-25**. These are external reports and implementations; none is a verified fix for this Discovery. Device facts and the current audio behavior belong in [screen-specs.md](screen-specs.md).

## Primary code target: receiver audio ownership

The useful lead is to keep CarPlay display/touch active while the iPhone retains its direct factory-Bluetooth audio path. Changing Android volume alone does not stop the iPhone selecting CarPlay as its output.

- **Implemented receiver mode:** in [node-CarPlay issue #19](https://github.com/rhysmorgan134/node-CarPlay/issues/19), a developer decompiled AutoKit with JADX, found the `AudioTransferMode` preference, and traced it to adapter message type `0x08`, values `22`/`23`. A collaborator implemented it and reported that the phone stopped switching audio to the dongle. These are **Carlinkit commands**, not established ZLINK or vehicle-bus commands.
- **Native Kotlin reference:** [lvalen91/carlink](https://github.com/lvalen91/carlink) reimplements the receiver client in Kotlin and documents Bluetooth routing for system voice/call controls. It requires a CPC200-CCPA adapter and was physically tested on a 2024 Silverado Intel Android Automotive radio. It supplies reference code, not a confirmed app for this screen.
- **Original mechanism reference:** [Slyosx31/Carlink](https://github.com/Slyosx31/Carlink#limitations) initializes the Carlinkit adapter without advertising audio support because its app could not process stable audio. That is a related mechanism, not evidence that the author had this Discovery's fault. Its Flutter framework is not a project dependency.

The first investigation is whether the **actual installed ZLINK build** has an equivalent mode, capability declaration, native function, or vendor-service API. Package identity, permissions, signatures, and authentication dependencies remain unknown.

## Migration candidates: source available locally

- **[F-e-n-y-x/CarLink](https://github.com/F-e-n-y-x/CarLink)** is a different project from the adapter client above: generic Android 7.1+ ARM, Kotlin, wired/wireless CarPlay, no extra dongle. `soundThroughCarBluetooth` maps into the DiPlay engine's `disableAudioOutput` capability negotiation. Development testing is reported on a Redmi Pad Pro; LR_J is untested. Some proprietary Bluetooth modules block wireless use, and ordinary source builds omit authentication assets. This is the leading migration candidate, not a confirmed fix.
- **[DiPlay](https://github.com/shihabal3amri/DiPlay)** is the native wired/wireless CarPlay engine reference, currently Android 7.0+ and BYD-focused. Its source exposes the car-Bluetooth/no-audio offer; other brands are unsupported by its maintainer. Authentication integration and vehicle tests are still required.
- **[OpenAutoLink](https://github.com/mossyhub/openautolink)** is real, but its current build requires Android 12L+ and targets GM AAOS. The maintainer documents working USB CarPlay, unfinished wireless CarPlay, and source builds without authentication assets. It is a reference, not the best initial wireless candidate for this screen.
- **[device-reveng](https://github.com/armeehn/device-reveng)** contains a Kotlin launcher and ZLINK event/launch integration on different Choiceway hardware. Its constants include unverified behavior and must be checked against our installed build.

Clones and exact fetched-main revisions are recorded in [upstreams.lock.json](../upstreams.lock.json). The [official Android zLink page](https://zjinnova.com/android-zlink.html) describes APK/HAL/driver/OS integration delivery; no public official ZLINK source repository was found. An exact latest compatible ZLINK application version was not established. A [vendor update-assistant page](https://www.zjinnova.com/personal.html) exists, but no updater or replacement APK was installed.

## Owner reports: success and failure

- **Exact ZLINK/localhost symptom:** an owner reported that an [AutoKit app plus Android-host USB dongle](https://www.reddit.com/r/CarPlay/comments/rmg65y/comment/jw93rcz/) let factory Bluetooth handle music and calls. The dongle plugs into the Android screen; this is a different architecture from built-in ZLINK and from selecting USB in the Land Rover media menu.
- **Counterexample:** a [CCPA/AutoKit owner](https://www.reddit.com/r/carlinkit/comments/1x8411g/ccpa_autokit_bluetooth_call/) still experienced calls taking audio back despite selecting Car Audio. Receiver mode alone is not a guarantee across firmware, calls, and Siri.
- **XDA transition failure:** a [Mercedes W204/COIKA owner](https://xdaforums.com/t/change-carplay-audio-playback-to-cars-bluetooth.4757026/) used an iPhone automation that initially selected factory Bluetooth, but Siri, notifications, and pause/resume restored CarPlay output. Only the indexed opening post was readable; no reply-based fix was verified. Startup-only success is insufficient.

## Leads specific to vendor integration

- **Matching software strings:** [Jaguar Forums, page 4](https://www.jaguarforums.com/forum/xf-xfr-x250-44/another-android-unit-245453/page4/) post #79 has the same APP `1.0.6.0710h` and SYSTEM `8:64.p70220811`, but a different MCU. Another owner in #72 reports a `BT Phone` → `normal BT` workaround with **Android Auto**. These are separate posters, not a proven exact-build iPhone fix or interchangeable firmware.
- **Potential internal option:** an [Acura RDX owner](https://www.reddit.com/r/CarPlay/comments/1fwvu43/comment/lqho9gc/) reports factory Bluetooth resolved their ZLINK call-quality issue through `System → factory mode → Disable Phone Link Audio`. This is a search term for the extracted apps; the option's existence and effect on LR_J are unverified.

## USB/ADB access investigation

Research on **2026-10-25** did not establish a PC/ADB port or vendor network-debugging procedure for the exact `LR_J / LH.V3.0 / P70.22.08.11` hardware. Do not present further factory-menu paths or USB-role switches as verified instructions.

- **MTP is not an ADB prerequisite.** [AOSP Android 11 USB configuration](https://github.com/aosp-mirror/platform_system_core/blob/android11-release/rootdir/init.usb.configfs.rc#L15-L36) implements standalone `adb` separately from `mtp,adb`. The earlier suggestion to select File transfer was generic experimentation, not an established fix for this unit.
- **Cable roles matter.** The [USB-IF Type-C specification, printed page 32](https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf) defines Type-C-male/Standard-A-male cables for a Type-C device connected to a legacy A host. The owner's A-at-screen/C-at-Mac arrangement therefore has a potential role mismatch with Mac-as-host ADB. This does not prove that the screen's port is host-only; board-specific device/OTG support remains unknown. Do not prescribe an A-to-A workaround without hardware documentation.
- **Related-unit owner report:** a Canavie/Merryway Jaguar owner identified an MRW-8833 board, enabled debugging and obtained a cable, but subsequently [reported ADB did not work, post 151](https://www.jaguarforums.com/forum/xj-x351-53/update-10-25-front-screen-all-xjs-210245/page8/). This is different hardware, not a verified LR_J procedure.
- **Mac approval is a separate possible gate.** [Apple documents accessory approval](https://support.apple.com/102282) on Apple-silicon laptops. The owner reports no alert appeared. That alone neither establishes nor excludes a Mac authorization problem; no global accessory policy was changed.
- **Supplier manual is not an exact match.** The [TAFFIO Discovery MRW8701 guide](https://www.realmediashop.de/DOKU/MRW8701_Quickguide_DEEN.pdf) documents smartphone USB use, but concerns Discovery 4 DENSO/Bosch hardware and supplies no established PC/ADB procedure for this Discovery 5.

### Inspect apps without ADB

[App Manager](https://github.com/MuntashirAkon/AppManager) documents **No-root mode**, device information, app-component inspection and **Share → APK/APKS** export in its [official manual](https://muntashir.dev/AppManager/en/). This offers a way to identify the board and copy readable installed launcher/vendor/receiver APKs through ordinary app installation and file transfer, while ADB remains unavailable. It does not itself provide root, enable a closed ADB endpoint, copy all private app data, or produce a firmware rollback image. Use inspection/export functions; avoid component blocking, uninstallation, restoration or automatic privilege selection.

Google also documents the on-device [Take bug report option](https://developer.android.com/studio/debug/bug-report), which the owner already saw. If this firmware implements it, the report may expose build and USB-service state without a working ADB session; obtaining its file remains a separate transfer step. Keep all raw reports private under `.local/`.

## What to carry into code

Inspect the installed receiver before choosing a companion service, targeted patch, or replacement. Preserve originals and hashes. Validate music, factory microphone, steering controls, incoming/outgoing calls, Siri, navigation, and reconnects on the car. A compiled APK or a successful music test does not establish the complete fix.
