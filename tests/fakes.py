"""Stand-ins for the game and ModsSettings API 1.7.1 objects the mod talks to.

Behaviour mirrors the sources pinned in docs/DECOMPILED_REFERENCE.md.
"""

import copy
import types

ARCADE_KEY = "mouseArcadeSens"
SNIPER_KEY = "mouseSniperSens"


class Event(list):
    """Same semantics as the game's common/Event.py."""

    def __iadd__(self, delegate):
        if delegate not in self:
            self.append(delegate)
        return self

    def __isub__(self, delegate):
        if delegate in self:
            self.remove(delegate)
        return self

    def __call__(self, *args):
        for delegate in self[:]:
            delegate(*args)


class FakeSettingsCore:
    def __init__(self, arcade, sniper):
        self.values = {ARCADE_KEY: arcade, SNIPER_KEY: sniper}
        self.onSettingsChanged = Event()
        self.onSettingsApplied = Event()
        self.applied = []

    def getSetting(self, key):
        return self.values[key]

    def applySettings(self, diff):
        self.applied.append(dict(diff))
        for key, value in diff.items():
            if self.values[key] != value:
                self.values[key] = value
                self.onSettingsChanged({key: value})
        self.onSettingsApplied(dict(diff))

    def change_natively(self, key, value):
        self.values[key] = value
        self.onSettingsChanged({key: value})


class FakeModsSettingsApi:
    """The parts of ModsSettings API 1.7.1 (api.py, view.py) the mod relies on."""

    def __init__(self):
        self.state = {"settings": {}, "templates": {}, "storage": {}}
        self.activeMods = set()
        self.onSettingsChanged = Event()
        self.onButtonClicked = Event()
        self.onWindowOpened = Event()
        self.onWindowClosed = Event()

    def saveState(self):
        pass

    def registerCallback(self, linkage, callback, buttonHandler=None):
        self.activeMods.add(linkage)
        self.onSettingsChanged += callback
        if buttonHandler is not None:
            self.onButtonClicked += buttonHandler

    def getSettingsFromTemplate(self, template):
        result = {}
        if "enabled" in template:
            result["enabled"] = template["enabled"]
        for column in ("column1", "column2"):
            for component in template.get(column, []):
                if "varName" in component and "value" in component:
                    result[component["varName"]] = component["value"]
        return result

    def updateModSettings(self, linkage, newSettings):
        self.state["settings"][linkage] = newSettings
        self.onSettingsChanged(linkage, newSettings)

    def open_window(self):
        self.onWindowOpened()
        return copy.deepcopy(self.state["settings"])

    def apply(self, linkage, settings):
        self.updateModSettings(linkage, settings)


def _component(**fields):
    return dict(fields)


def make_templates_module():
    module = types.ModuleType("gui.modsSettingsApi.templates")
    module.createLabel = lambda text, tooltip="": _component(
        type="Label", text=text, tooltip=tooltip
    )
    module.createEmpty = lambda: _component(type="Empty")
    module.createInput = lambda text, varName, value, tooltip="", width=0: _component(
        type="TextInput", text=text, varName=varName, value=value, width=width
    )
    return module
