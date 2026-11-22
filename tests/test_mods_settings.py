"""Settings lifecycle tests for the ModsSettings integration."""

from fakes import ARCADE_KEY, SNIPER_KEY


def _panel(game):
    return game.api.state["settings"][game.mods_settings.MOD_LINKAGE]


def _labels(game):
    template = game.api.state["templates"][game.mods_settings.MOD_LINKAGE]
    return [c["text"] for c in template["column2"] if c["type"] == "Label"]


def _apply(game, **fields):
    settings = dict(_panel(game))
    settings.update(fields)
    game.api.apply(game.mods_settings.MOD_LINKAGE, settings)


def test_init_publishes_native_values_without_enabled_switch(game):
    game.entry.init()

    assert _panel(game) == {
        "arcade_sensitivity": "1.000000",
        "sniper_sensitivity": "0.500000",
    }
    template = game.api.state["templates"][game.mods_settings.MOD_LINKAGE]
    assert "enabled" not in template
    assert "Current arcade: 1.000000" in _labels(game)


def test_apply_writes_only_the_edited_field(game):
    game.entry.init()

    _apply(game, arcade_sensitivity="0.123456")

    assert game.core.applied == [{ARCADE_KEY: 0.123456}]
    assert game.core.values == {ARCADE_KEY: 0.123456, SNIPER_KEY: 0.5}
    assert game.saved
    assert _panel(game)["arcade_sensitivity"] == "0.123456"
    assert "Current arcade: 0.123456" in _labels(game)


def test_unedited_field_does_not_overwrite_native_change(game):
    game.entry.init()
    stale = dict(_panel(game))

    game.core.change_natively(SNIPER_KEY, 2.25)
    stale["arcade_sensitivity"] = "1.500000"
    game.api.apply(game.mods_settings.MOD_LINKAGE, stale)

    assert game.core.values == {ARCADE_KEY: 1.5, SNIPER_KEY: 2.25}


def test_native_change_refreshes_panel(game):
    game.entry.init()

    game.core.change_natively(ARCADE_KEY, 3.0)

    assert _panel(game)["arcade_sensitivity"] == "3.000000"
    assert "Current arcade: 3.000000" in _labels(game)


def test_options_apply_diff_refreshes_panel(game):
    game.entry.init()
    game.core.values[SNIPER_KEY] = 2.5

    game.core.onSettingsApplied({SNIPER_KEY: 2.5})

    assert _panel(game)["sniper_sensitivity"] == "2.500000"
    assert "Current sniper: 2.500000" in _labels(game)


def test_reopening_shows_current_values_after_cancel(game):
    game.entry.init()
    game.core.values[SNIPER_KEY] = 4.0

    shown = game.api.open_window()

    assert shown[game.mods_settings.MOD_LINKAGE]["sniper_sensitivity"] == "4.000000"
    assert game.core.applied == []


def test_reload_replaces_stale_saved_panel_state(game):
    linkage = game.mods_settings.MOD_LINKAGE
    game.api.state["templates"][linkage] = {"settingsVersion": 1, "enabled": True}
    game.api.state["settings"][linkage] = {
        "enabled": True,
        "arcade_sensitivity": "9.000000",
        "sniper_sensitivity": "9.000000",
    }

    game.entry.init()

    assert _panel(game) == {
        "arcade_sensitivity": "1.000000",
        "sniper_sensitivity": "0.500000",
    }
    assert game.core.applied == []


def test_out_of_range_and_invalid_input(game):
    game.entry.init()

    _apply(game, arcade_sensitivity="42", sniper_sensitivity="not a number")

    assert game.core.values == {ARCADE_KEY: 10.0, SNIPER_KEY: 0.5}
    assert _panel(game)["sniper_sensitivity"] == "0.500000"


def test_other_mods_are_ignored(game):
    game.entry.init()

    game.api.apply("some_other_mod", {"arcade_sensitivity": "5.0"})

    assert game.core.applied == []


def test_fini_removes_every_handler_and_is_idempotent(game):
    game.entry.init()

    game.entry.fini()
    game.entry.fini()

    assert list(game.api.onSettingsChanged) == []
    assert list(game.api.onWindowOpened) == []
    assert list(game.core.onSettingsChanged) == []
    assert list(game.core.onSettingsApplied) == []


def test_reinit_after_fini_registers_once(game):
    game.entry.init()
    game.entry.fini()
    game.entry.init()

    assert len(game.api.onSettingsChanged) == 1
    assert len(game.api.onWindowOpened) == 1
    assert len(game.core.onSettingsChanged) == 1
    assert len(game.core.onSettingsApplied) == 1
