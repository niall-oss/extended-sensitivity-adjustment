# Decompiled reference

The mod is written against these sources. Update the pins when a new game patch or ModsSettings API release ships.

| Source | Pinned version |
|---|---|
| Game client | [StranikS-Scan/WorldOfTanks-Decompiled `2.4.1_EU`](https://github.com/StranikS-Scan/WorldOfTanks-Decompiled/tree/2.4.1_EU) (live client v2.4.1.1 EU) |
| ModsSettings API | [izeberg/modssettingsapi 1.7.1](https://github.com/izeberg/modssettingsapi) |

Game paths are under `source/res/scripts/`; ModsSettings paths are under `sources/scripts/client/gui/modsSettingsApi/`.

## Game behaviour the mod relies on

- **Setting keys**: `client/account_helpers/settings_core/settings_constants.py` defines `CONTROLS.MOUSE_ARCADE_SENS` (`mouseArcadeSens`) and `CONTROLS.MOUSE_SNIPER_SENS` (`mouseSniperSens`).
- **The sniper key is shared**: in `client/account_helpers/settings_core/settingscore.py`, `MOUSE_SNIPER_SENS` is registered three times, for the `sniper`, `dualgun` and `twinGun` modes. `SettingsCore.applySetting(key)` resolves the key through `SettingsContainer.indices` and reaches only the last entry. `SettingsCore.applySettings(diff)` iterates every entry. The mod uses `applySettings`, like the Options menu.
- **Storage**: `MouseSensitivitySetting` in `client/account_helpers/settings_core/options.py` reads and writes `AccountSettings` under the keys above and pushes the value to the active camera. `BigWorld.savePreferences()` writes it to disk.
- **Change notification**: the Options menu applies through `SettingsParams.apply` (`client/gui/Scaleform/daapi/view/common/settings/SettingsParams.py`), which calls `SettingsCore.applySettings(diff)`. That method raises `onSettingsApplied(diff)` with the full diff, but its own `onSettingsChanged` call carries only graphics keys. Sensitivity still reaches `onSettingsChanged` by another path: `MouseSensitivitySetting._set` writes through `AccountSettings.setSettings`, and `AccountSettings._setValue` (`client/account_helpers/AccountSettings.py`) raises `onSettingsChanging` when the value changes. `SettingsCore` forwards that as `onSettingsChanged({key: value})`. The mod listens to both events: `onSettingsApplied` for the Options Apply diff, and `onSettingsChanged` for `applySetting(key)` and direct `AccountSettings` writes.
- **Events**: `common/Event.py` `Event.__isub__` ignores handlers that were never added, so unsubscribing is always safe.

## ModsSettings API behaviour the mod relies on

- `api.py` stores templates and settings in `state`. `compareTemplates` replaces a stored template only when `settingsVersion` increases, so the mod writes its live template into `state['templates']` and `state['settings']` itself. If a ModsSettings update renames these, the mod breaks.
- `api.py` has no unregister call. `registerCallback` does `onSettingsChanged += callback`, so the mod removes it with `-=`.
- `view.py` `_populate` fires `onWindowOpened` before Flash calls `requestModsData`, which is when `generateSettingsData` reads `state`.
- `flash/src/.../ModsSettingsWindow.as` `collectModsData` sends only mods with changed fields on Apply, but includes *all* fields of each such mod. The mod therefore treats a field as edited only if it differs from what the panel showed.

## Updating for a new patch

1. Find the new branch: `git ls-remote --heads https://github.com/StranikS-Scan/WorldOfTanks-Decompiled.git`.
2. Re-check the files above for renamed keys, a changed `applySetting`/`applySettings` path or changed events.
3. Check the installed ModsSettings API version against the latest release and re-read `api.py` and `view.py`.
4. Update the pins in this file.
