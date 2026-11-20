def init():
    from gui.extendedsensitivityadjustment.mods_settings import register_mods_settings

    register_mods_settings()


def fini():
    from gui.extendedsensitivityadjustment.mods_settings import (
        unregister_mods_settings,
    )

    unregister_mods_settings()
