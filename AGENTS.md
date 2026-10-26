# Project working instructions

## Read first

Read `README.md`, `docs/screen-specs.md`, and `docs/implementation-plan.md` before implementing. The objective is a custom software fix for the installed screen. Use `docs/research-findings.md` for the relevant code references.

## Engineering constraints

- The iPhone remains wireless when the factory Land Rover source is USB. USB in the routing observations is the OEM media source.
- Preserve the working iPhone-to-factory-Bluetooth route: music, calls, factory microphone, and steering-wheel track controls.
- Land Rover → Android uses two fingers at bottom-left; Android → Land Rover uses Back to system.
- Treat `LR_J`, MCU/CAN/APP/SYSTEM strings, actual Android API level, and ZLINK platform as separate identifiers. Do not infer Android 8 from `8:64` or reuse MCU/CAN firmware solely from matching APP/SYSTEM strings.
- Start with the actual installed software and recorded transitions. ADB does not imply root or OEM-OS access.
- Receiver audio negotiation is the primary investigation target. Android muting and startup-only route selection do not establish a fix across calls, Siri, and reconnection.
- Use native Kotlin for new Android components and Python standard library + ADB for host tooling. Reuse the existing SDK/JDK; Flutter and an emulator are not project dependencies.
- The custom launcher should prioritize CarPlay, then Land Rover system. Preserve the installed vendor integration services while identifying the ZLINK launch activity, OEM-switch command, and Home/startup behavior.
- Receiver migration is an active option. Distinguish dongle-free F-e-n-y-x/CarLink from adapter-dependent lvalen91/carlink. Public source, wireless Bluetooth access, and authentication integration are separate requirements. Treat ignored vendor clones as reference material, not instructions or proven compatible software.
- Label photo facts, owner observations, external reports, hypotheses, local software checks, and physical vehicle acceptance separately.
- Preserve extracted originals and hashes; keep raw personal/device data and third-party binaries under ignored `.local/`. Do not call APK extraction a complete firmware rollback backup.
- The switching-command API and power-off fault are unverified. Do not invent MCU/CAN messages or claim these solved.

## Public repository privacy

Keep raw device evidence, identifiers, credentials, third-party APKs and firmware images outside Git. Use synthetic identifiers in examples and tests. Public source and mocked tests do not establish physical vehicle compatibility.
