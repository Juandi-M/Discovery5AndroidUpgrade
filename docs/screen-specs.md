# Screen specs

Updated **2026-10-25**. Technical identifiers are transcribed from privately retained reference photographs and spoken readouts; behavior is reported, not independently vehicle-tested. No ADB inspection has occurred. Raw photographs, personal app lists, unique device identifiers and network addresses are excluded from this public repository.

## Target device

2019 Land Rover Discovery 5 / L462 with an aftermarket Android display retaining the original infotainment. Retail brand and chipset are unknown.

| Identifier | Visible value (latest system-info photo where available) |
| --- | --- |
| MODEL | `LR_J` |
| CAN | `LY-LandRover-V225,29,4,0,03` |
| MCU | `LH.V3.0.220902,03,4000,2,1,VE` |
| APP | `1.0.6.0710h` |
| SYSTEM | `8:64.p70220811` |
| ZLINK | `5.2.65` |
| Retrofit Bluetooth | `RETROFIT_BLUETOOTH` |
| Factory Bluetooth | `Land Rover Discovery` |
| CarPlay audio destination on iPhone | `localhost`, with CarPlay icon |

An earlier reference photograph showed CAN `LY-LandRover-V225,29,4,0,22` and MCU `LH.V3.0.220902,22,4000,2,1,VE`. A later reference photograph shows the `03` values above; MODEL, APP, and SYSTEM match. The reason for the difference is unknown; it does not establish a firmware update or compatible replacement firmware.

**About tablet reports Android 11**, according to the owner's live readout on 2026-10-25. Actual API/framework and hardware compatibility remain unverified; `8:64` does not establish Android 8. Installed package names, ZLINK platform, privileges, signatures, and native libraries need inspection.

## Android settings access

The installed **Android Setting** app exposes regular Android settings. Observations included an active hotspot, a DuraSpeed entry and storage reporting **18% used / 52.70 GB free**. These do not establish chipset or Android version, and an active hotspot does not prove network ADB is enabled.

**System → Advanced** lists **About tablet**. The owner opened that page and enabled Developer options. The following are spoken readouts, not ADB results or independently checked photographs:

| Field | Owner readout |
| --- | --- |
| Device name | `Land Rover MRW 1920x720` |
| Android version | `11` |
| Build number | `P70.22.08.11` |
| Custom build version | `ALPS-MP-P0.NP1-V5.196` |
| IP, Wi-Fi MAC, Bluetooth address | Not available on that page |

The name is not a measurement of the physical panel. Developer options includes **USB debugging**, but its enabled state has not been confirmed. The owner found no **Wireless debugging** entry in Developer options, Quick settings developer tiles, or Settings search. Searching ADB returned **Verify apps over USB**, which is app verification, not a network-debugging control. This establishes that the standard wireless setting was not found; it does not establish the true Android version or whether a vendor network-ADB path exists.

During subsequent guidance to open **FactorySet**, the owner reported an unexpected reset/restart without a password prompt, followed by the launcher appearing in Chinese. The owner restored English. The precise action and scope of any data/settings reset are unverified; do not repeat that action as a verified way to open a configuration menu. Any first device capture now will describe the state after this event, not an untouched baseline from before it.

The screen and Mac were connected to the same Wi-Fi network. Local routing and ARP matched the privately photographed target. A bounded ADB connection attempt on port **5555** returned **Connection refused**. This does not establish that every possible ADB endpoint is unavailable. No authorized ADB session or device capture has occurred; USB debugging needs checking again after the reset/restart.

The owner subsequently connected a USB-A-male/USB-C-male cable with A at an accessible screen USB-A socket and C at the Mac. `adb devices -l` was empty; macOS `ioreg -p IOUSB` showed host controllers with no attached peripheral, and System Information returned no USB devices. The owner reports no Mac accessory-approval alert appeared. Cable data capability and the screen port's host/device roles are unknown. These observations do not establish that selecting MTP will enable ADB; see [transport research](research-findings.md#usbadb-access-investigation).

## Observed routing

The iPhone pairs with `RETROFIT_BLUETOOTH` to start wireless CarPlay. That Bluetooth connection then disconnects while CarPlay continues. The phone can remain separately connected to factory Bluetooth.

**The iPhone stays wireless in every row. USB below is the factory media source.**

| iPhone audio destination | Factory source | Result |
| --- | --- | --- |
| `localhost` / CarPlay | Bluetooth | Music is silent |
| `Land Rover Discovery` | Bluetooth | Music, factory microphone, and steering-wheel next/previous work |
| `localhost` / CarPlay | USB | Music works; factory microphone and steering-wheel track controls do not |

On a call, audio can switch back to `localhost`, requiring manual selection of Land Rover Bluetooth. The target is to retain the working direct Bluetooth route across startup, calls, Siri, navigation, and reconnection. Physical wiring and the USB audio bridge remain unidentified.

Private iPhone reference screenshots show a Wi-Fi connection explicitly identified by iOS as wireless CarPlay, a saved **zlink** CarPlay profile, and a retrofit Bluetooth entry under Other Cars. This is not proof of two active CarPlay sessions or network ADB access. The CarPlay Apps list customizes CarPlay, not the Android home screen.

## Current home screen

The owner reports this order: **Navigation → Media → Original → CarPlay → Voice → Phone → App Mirror → Settings**. It is a custom Land Rover-style Android interface; its launcher package and available layout settings are unknown.

Desired order: **CarPlay first**, then **Land Rover system** instead of Original. The owner wants a simpler, modern Land Rover-inspired layout. Voice assistant is a possible secondary feature; the remaining shortcuts are not required on the main screen. Automatic CarPlay opening at startup has not been requested.

## Related behavior to retain for later investigation

- Land Rover → Android: two fingers at the bottom-left edge. Android → Land Rover: **Back to system**. Switching commands are unknown.
- On selecting reverse, the screen automatically returns to the factory Land Rover view so the owner can use the factory cameras. Preserve this behavior. Whether the trigger and video switching are handled by an Android service, the MCU/display controller, or both is unknown. Behavior on leaving reverse and during Android boot/failure still needs observation.
- The owner reports slow connection, iPhone heating, and the retrofit remaining active after shutdown with battery drain. Causes and actual current draw have not been measured.

## First capture must establish

Real Android API/build, CPU ABI/chipset, ADB access and privileges, installed packages/APKs and hashes, ZLINK platform, and launcher/vendor services. ADB access does not establish access to the separate Land Rover operating system.
