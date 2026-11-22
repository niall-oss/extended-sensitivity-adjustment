from debug_utils import LOG_NOTE

from gui.extendedsensitivityadjustment import sensitivity

MOD_LINKAGE = "extended_sensitivity_adjustment"
SETTINGS_VERSION = 2

ARCADE_VAR = "arcade_sensitivity"
SNIPER_VAR = "sniper_sensitivity"

HINT_TOOLTIP = (
    "{HEADER}Precise mouse sensitivity{/HEADER}"
    "{BODY}Enter exact sensitivity values. These are the same game settings "
    "as the Options menu sliders and are saved to your game preferences "
    "(preferences.xml).{/BODY}"
)

INPUT_TOOLTIP = (
    HINT_TOOLTIP
    + "{BODY}Valid range: %.1f to %.1f. Use up to six decimal places "
    "(for example 0.120000). Changes apply when you click Apply.{/BODY}"
)

_api = None
_settings_core = None
_panel_values = {}


def _get_mods_settings_api():
    try:
        from gui.modsSettingsApi import g_modsSettingsApi
    except ImportError:
        return None
    return g_modsSettingsApi


def _vars_to_keys():
    arcade_key, sniper_key = sensitivity.get_sensitivity_keys()
    return ((ARCADE_VAR, arcade_key), (SNIPER_VAR, sniper_key))


def _read_native_values():
    return dict(
        (var, sensitivity.format_sensitivity(sensitivity.get_sensitivity(key)))
        for var, key in _vars_to_keys()
    )


def _build_template(values):
    from gui.modsSettingsApi import templates

    tooltip = INPUT_TOOLTIP % (
        sensitivity.MIN_SENSITIVITY,
        sensitivity.MAX_SENSITIVITY,
    )

    return {
        "modDisplayName": "Extended Sensitivity Adjustment",
        "settingsVersion": SETTINGS_VERSION,
        "column1": [
            templates.createLabel(
                "Set precise arcade and sniper mouse sensitivity values.",
                tooltip=HINT_TOOLTIP,
            ),
            templates.createEmpty(),
            templates.createInput(
                "Arcade sensitivity",
                ARCADE_VAR,
                values[ARCADE_VAR],
                tooltip=tooltip,
                width=100,
            ),
            templates.createInput(
                "Sniper sensitivity",
                SNIPER_VAR,
                values[SNIPER_VAR],
                tooltip=tooltip,
                width=100,
            ),
        ],
        "column2": [
            templates.createLabel("Current arcade: %s" % values[ARCADE_VAR]),
            templates.createLabel("Current sniper: %s" % values[SNIPER_VAR]),
            templates.createEmpty(),
            templates.createLabel(
                "Values are saved to your game preferences when you click Apply."
            ),
        ],
    }


def _publish_native_values():
    # ModsSettings API only replaces a stored template when settingsVersion
    # increases, so the live values are written into its state directly.
    # Checked against ModsSettings API 1.7.1.
    values = _read_native_values()
    template = _build_template(values)
    state = _api.state
    state["templates"][MOD_LINKAGE] = template
    state["settings"][MOD_LINKAGE] = _api.getSettingsFromTemplate(template)
    _api.saveState()
    return values


def _sync_panel():
    _panel_values.clear()
    _panel_values.update(_publish_native_values())


def _edited_values(settings):
    # The panel sends every field of the mod on Apply, so only fields that
    # differ from what it was showing count as edits; the rest must not
    # overwrite a native change. _panel_values is deliberately not moved by
    # native changes, because an open panel still shows the older values.
    edited = {}
    for var, key in _vars_to_keys():
        shown = _panel_values.get(var)
        value = sensitivity.parse_sensitivity(
            settings.get(var), sensitivity.get_sensitivity(key)
        )
        if sensitivity.format_sensitivity(value) != shown:
            edited[key] = value
    return edited


def _apply_settings(settings):
    sensitivity.apply_sensitivities(_edited_values(dict(settings)))
    _sync_panel()


def _on_settings_changed(linkage, settings):
    if linkage != MOD_LINKAGE:
        return
    _apply_settings(settings)


def _on_window_opened():
    _sync_panel()


def _on_native_settings_changed(diff):
    if any(key in diff for _, key in _vars_to_keys()):
        _publish_native_values()


def register_mods_settings():
    global _api, _settings_core

    api = _get_mods_settings_api()
    if api is None:
        LOG_NOTE(
            "ModsSettings API not installed. Extended Sensitivity Adjustment "
            "requires ModsSettings API, ModsList, and OpenWG Gameface."
        )
        return False

    _api = api
    _settings_core = sensitivity.get_settings_core()
    _sync_panel()
    api.registerCallback(MOD_LINKAGE, _on_settings_changed)
    api.onWindowOpened += _on_window_opened
    # Options sensitivity changes reach onSettingsChanged only through the
    # client's AccountSettings forwarding; onSettingsApplied carries the
    # Apply diff itself, so the panel refreshes even without that forwarding.
    _settings_core.onSettingsChanged += _on_native_settings_changed
    _settings_core.onSettingsApplied += _on_native_settings_changed
    return True


def unregister_mods_settings():
    global _api, _settings_core

    if _api is None:
        return

    _api.onSettingsChanged -= _on_settings_changed
    _api.onWindowOpened -= _on_window_opened
    _settings_core.onSettingsChanged -= _on_native_settings_changed
    _settings_core.onSettingsApplied -= _on_native_settings_changed
    _api = None
    _settings_core = None
    _panel_values.clear()
