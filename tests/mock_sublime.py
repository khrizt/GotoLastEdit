"""Minimal Sublime Text API stubs for offline unit tests."""


class Region:
    def __init__(self, a, b=None):
        self.a = a
        self.b = a if b is None else b

    def begin(self):
        return min(self.a, self.b)

    def end(self):
        return max(self.a, self.b)


class Selection(list):
    def clear(self):
        del self[:]

    def add(self, region):
        self.append(region)


class Settings:
    def __init__(self, values=None):
        self._values = dict(values or {})

    def get(self, key, default=None):
        return self._values.get(key, default)

    def set(self, key, value):
        self._values[key] = value


class View:
    _next_id = 1

    def __init__(self, content="", is_widget=False):
        self._id = View._next_id
        View._next_id += 1
        self._content = content
        self._sel = Selection([Region(0)])
        self._settings = Settings({"is_widget": is_widget})
        self._shown = None
        self._focused = False

    def id(self):
        return self._id

    def sel(self):
        return self._sel

    def settings(self):
        return self._settings

    def rowcol(self, point):
        text = self._content[:point]
        row = text.count("\n")
        last_nl = text.rfind("\n")
        col = point if last_nl < 0 else point - last_nl - 1
        return row, col

    def line(self, point_or_region):
        if isinstance(point_or_region, Region):
            point = point_or_region.begin()
        else:
            point = point_or_region
        start = self._content.rfind("\n", 0, point) + 1
        end = self._content.find("\n", point)
        if end < 0:
            end = len(self._content)
        return Region(start, end)

    def show(self, region):
        self._shown = region

    def set_content(self, content):
        self._content = content

    def place_cursor(self, point):
        self._sel.clear()
        self._sel.add(Region(point))


class Window:
    def __init__(self):
        self.focused = None

    def focus_view(self, view):
        self.focused = view
        view._focused = True


_PACKAGE_SETTINGS = Settings({"history_size": 50})
_ACTIVE_WINDOW = Window()


def load_settings(name):
    return _PACKAGE_SETTINGS


def active_window():
    return _ACTIVE_WINDOW


def reset_mocks(history_size=50):
    global _ACTIVE_WINDOW
    View._next_id = 1
    _PACKAGE_SETTINGS._values = {"history_size": history_size}
    _ACTIVE_WINDOW = Window()