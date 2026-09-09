Additional reproduction on AmneziaVPN 5.0.1.5 / Windows 11 x64 using a synthetic native .vpn profile (no working VPN server):

- Before import, both the embedded raw config (`MTU = 1280`) and `last_config.mtu` (`"1280"`) were set explicitly.
- The import preview changed `last_config.mtu` to `"1376"` while retaining `MTU = 1280` inside the raw config.
- After saving, the expected description was displayed correctly, but Show connection parameters still displayed raw MTU 1280, concealing the metadata mismatch.

Source trace at 7d4f3e0f5090b74903609179653d1f669d2ad08a: processAmneziaConfig overwrites the metadata; LocalSocketController::activate passes it as deviceMTU; daemon.cpp parses it; InterfaceConfig::toWgConf writes it for the Windows tunnel service. This supports preserving the explicit value at the import boundary as proposed here.

We applied the patch at PR head a39f1c374ed760f886c62741d5645fd1c39c6630 to a temporary copy of the 5.0.1.5 source: git apply --check and apply passed. We have not built or runtime-tested the patched client. An accidental connection attempt occurred during the UI session; no successful connection or adapter MTU measurement was established. This report does not establish the cause of the separate traffic issue #3043.
