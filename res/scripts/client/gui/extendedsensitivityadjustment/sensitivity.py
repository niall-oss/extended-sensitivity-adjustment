MIN_SENSITIVITY = 0.0
MAX_SENSITIVITY = 10.0


def get_settings_core():
    from helpers import dependency
    from skeletons.account_helpers.settings_core import ISettingsCore

    return dependency.instance(ISettingsCore)


def get_sensitivity_keys():
    from account_helpers.settings_core.settings_constants import CONTROLS

    return CONTROLS.MOUSE_ARCADE_SENS, CONTROLS.MOUSE_SNIPER_SENS


def clamp_sensitivity(value):
    return max(MIN_SENSITIVITY, min(MAX_SENSITIVITY, float(value)))


def parse_sensitivity(value, default):
    try:
        return clamp_sensitivity(float(value))
    except (TypeError, ValueError):
        return clamp_sensitivity(default)


def format_sensitivity(value):
    return "%.6f" % clamp_sensitivity(value)


def get_sensitivity(key):
    return get_settings_core().getSetting(key)


def apply_sensitivities(values):
    if not values:
        return {}

    import BigWorld

    diff = dict((key, clamp_sensitivity(value)) for key, value in values.items())
    # applySetting() resolves a key to a single option, but the sniper key is
    # shared by the sniper, dual-gun and twin-gun options; applySettings()
    # updates all of them, matching the native Options menu.
    get_settings_core().applySettings(diff)
    BigWorld.savePreferences()
    return diff
