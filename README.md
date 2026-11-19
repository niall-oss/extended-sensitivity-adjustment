# Extended Sensitivity Adjustment

<img width="1078" height="270" alt="image" src="https://github.com/user-attachments/assets/ca4e9e77-6b78-4f23-97db-ebeb636101ff" />

A World of Tanks mod that lets you set precise decimal values for arcade and sniper mouse sensitivity — the same floats stored in your game `preferences.xml`.

The in-game Options slider only allows coarse adjustments. This mod exposes two text inputs in the garage Mods settings menu so you can enter exact values.

## Dependencies

Required for the garage settings UI:

1. [OpenWG Gameface](https://gitlab.com/openwg/wot.gameface/)
2. [ModsList](https://gitlab.com/wot-public-mods/mods-list/)
3. [ModsSettings API](https://github.com/izeberg/modssettingapi)

Install load order: Gameface → ModsList → ModsSettings API → this mod.

Without ModsSettings, this mod has no UI and does nothing.

## Install

1. Download the latest `.wotmod` from [Releases](https://github.com/ANIALLATOR114/extended-sensitivity-adjustment/releases).
2. Copy it into your World of Tanks `mods/<game_version>/` folder.

Example:

```
World_of_Tanks/mods/2.2.1.1/ANIALLATOR.Extended_Sensitivity_Adjustment_1.0.0.wotmod
```

## Usage

1. Open the garage.
2. Go to **Mods** → **Extended Sensitivity Adjustment**.
3. Enter precise values for **Arcade sensitivity** and **Sniper sensitivity**.
4. Click **Apply**.

Values are written through the game's settings API and saved to `preferences.xml` (or `preferences_ct.xml` on Common Test).

## Values

- These are the **exact floats** from `scriptsPreferences/controlMode` in your preferences file.
- Valid range: **0.0 to 10.0** (same as the in-game slider).
- They are game sensitivity multipliers, not cm/360 measurements.

## Compatibility

- Wargaming realms (EU, NA, ASIA) and Lesta (Mir Tankov)
- Live client and Common Test client

## Build locally

Python 2.7 is required to compile WoT-compatible bytecode:

```bash
C:\Python27\python.exe build.py --username ANIALLATOR
```

Output: `build/ANIALLATOR.Extended_Sensitivity_Adjustment_1.0.0.wotmod`

## CI and releases

GitHub Actions builds the mod on every pull request and on merges to `main`.

- **Pull requests**: download the `.wotmod` from the workflow run's **Artifacts** (`wotmod-pr-{commit_sha}`).
- **Merges to `main`**: publishes or updates a [GitHub Release](https://github.com/ANIALLATOR114/extended-sensitivity-adjustment/releases) (`v{version}`) with the built `.wotmod` attached.

### Publishing to wgmods.net

The mod version lives in `build.py` (`--version` default). Release tooling in `scripts/wgmods.py` runs on the latest Python via [uv](https://docs.astral.sh/uv/) (`uv run scripts/wgmods.py --help`).

- **Game patches (automatic)**: the **Game patch update** workflow runs daily at 13:00 UTC. When wgmods lists a game version newer than the mod's latest update, it creates a `v{mod}+wot{game}` GitHub Release and submits the same mod version for that game version. If the mod already has the maximum number of updates (6), the oldest update is deleted first.
- **Code changes (manual)**: bump the version in `build.py`, then merge. Then run **Actions → Publish to wgmods** and enter the version changes text. Game version defaults to the latest; `dry_run` prints the request without uploading.

Both workflows authenticate with the repo secrets `WGMODS_SESSIONID` and `WGMODS_CSRFTOKEN`, which are your wgmods.net login cookies. Find them in DevTools → Application → Cookies → `https://wgmods.net`. If they stop working, the daily run opens a "wgmods session cookie expired" issue telling you to paste fresh ones.

