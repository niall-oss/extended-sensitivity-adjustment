import sys
import types
from pathlib import Path

import pytest
from fakes import (
    ARCADE_KEY,
    SNIPER_KEY,
    FakeModsSettingsApi,
    FakeSettingsCore,
    make_templates_module,
)

CLIENT_SCRIPTS = Path(__file__).resolve().parents[1] / "res" / "scripts" / "client"
MOD_PACKAGES = ("gui.extendedsensitivityadjustment", "gui.mods")


def _install_game_modules(monkeypatch, core, api, saved):
    def module(name, **attrs):
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules, name, mod)
        return mod

    module("debug_utils", LOG_NOTE=lambda *args: None)
    module("BigWorld", savePreferences=lambda: saved.append(True))
    dependency = module("helpers.dependency", instance=lambda interface: core)
    module("helpers", dependency=dependency)
    module("skeletons")
    module("skeletons.account_helpers")
    module("skeletons.account_helpers.settings_core", ISettingsCore=object)
    module("account_helpers")
    module("account_helpers.settings_core")
    controls = types.SimpleNamespace(
        MOUSE_ARCADE_SENS=ARCADE_KEY, MOUSE_SNIPER_SENS=SNIPER_KEY
    )
    module("account_helpers.settings_core.settings_constants", CONTROLS=controls)
    templates = make_templates_module()
    monkeypatch.setitem(sys.modules, templates.__name__, templates)
    module("gui.modsSettingsApi", g_modsSettingsApi=api, templates=templates)


def _import_mod_fresh(monkeypatch):
    monkeypatch.syspath_prepend(str(CLIENT_SCRIPTS))
    for name in list(sys.modules):
        if any(name == pkg or name.startswith(pkg + ".") for pkg in MOD_PACKAGES):
            monkeypatch.delitem(sys.modules, name)

    import gui.mods.mod_extendedsensitivityadjustment as entry
    from gui.extendedsensitivityadjustment import mods_settings

    return entry, mods_settings


@pytest.fixture
def game(monkeypatch):
    core = FakeSettingsCore(arcade=1.0, sniper=0.5)
    api = FakeModsSettingsApi()
    saved = []
    _install_game_modules(monkeypatch, core, api, saved)
    entry, mods_settings = _import_mod_fresh(monkeypatch)

    yield types.SimpleNamespace(
        core=core, api=api, entry=entry, mods_settings=mods_settings, saved=saved
    )
    mods_settings.unregister_mods_settings()
