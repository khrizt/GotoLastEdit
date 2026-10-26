import sublime
import sublime_plugin

SETTINGS_FILE = "GotoLastEdit.sublime-settings"
DEFAULT_HISTORY_SIZE = 50

def history_size():
    """Return the configured edit-history length (at least 1)."""
    settings = sublime.load_settings(SETTINGS_FILE)
    try:
        size = int(settings.get("history_size", DEFAULT_HISTORY_SIZE))
    except (TypeError, ValueError):
        size = DEFAULT_HISTORY_SIZE
    return max(1, size)


class LastEditLineCommand(sublime_plugin.TextCommand):
    """Jump to a previous edit location, including across views."""

    def run(self, edit):
        CE = CaptureEditing
        CE.track(self.view)

        # Drop stale ids left behind if a view closed without on_close firing.
        while CE.last_view and CE.last_view[-1] not in CE.view_refs:
            CE.last_view.pop()

        target = self.view
        if (
            CE.last_view
            and self.view.id() != CE.last_view[-1]
            and CE.last_view[-1] > 0
        ):
            other = CE.view_refs.get(CE.last_view[-1])
            if other is not None:
                window = sublime.active_window()
                if window is not None:
                    window.focus_view(other)
                CE.last_view.pop()
                target = other
                CE.track(target)

        positions = CE.last_line[target.id()]
        index = CE.posn[target.id()]
        if len(positions) > index:
            point = positions[-(index + 1)]
            region = target.line(point)
            target.show(region)
            target.sel().clear()
            target.sel().add(region)
            # Cycle through as many stored positions as the history allows.
            cycle = min(history_size(), len(positions))
            CE.posn[target.id()] = (index + 1) % cycle
        else:
            CE.posn[target.id()] = 0


class CaptureEditing(sublime_plugin.EventListener):
    last_line = {}
    prev_line = {}
    posn = {}
    last_view = []
    view_refs = {}

    @classmethod
    def track(cls, view):
        """Ensure bookkeeping exists for *view* (safe for panels / late views)."""
        vid = view.id()
        cls.last_line.setdefault(vid, [])
        cls.prev_line.setdefault(vid, -1)
        cls.posn.setdefault(vid, 0)
        cls.view_refs.setdefault(vid, view)

    @classmethod
    def forget(cls, view):
        """Remove all state for a closed view, including last_view entries."""
        vid = view.id()
        cls.last_line.pop(vid, None)
        cls.prev_line.pop(vid, None)
        cls.view_refs.pop(vid, None)
        cls.posn.pop(vid, None)
        cls.last_view[:] = [v for v in cls.last_view if v != vid]

    def on_modified(self, view):
        # Find/replace, Goto Anything, and output panels are widgets. Their
        # views are never registered via on_new / on_activated, so indexing
        # by id() would KeyError on every keystroke.
        if view.settings().get("is_widget") or len(view.sel()) == 0:
            return

        CE = CaptureEditing
        CE.track(view)

        sel = view.sel()[0]
        curr_line, _ = view.rowcol(sel.begin())
        vid = view.id()

        if CE.prev_line[vid] == -1 or curr_line != CE.prev_line[vid]:
            CE.prev_line[vid] = curr_line
            CE.last_line[vid].append(sel.begin())
            max_hist = history_size()
            while len(CE.last_line[vid]) > max_hist:
                CE.last_line[vid].pop(0)
            CE.last_view.append(vid)
            while len(CE.last_view) > max_hist:
                CE.last_view.pop(0)

    def on_close(self, view):
        CaptureEditing.forget(view)

    def on_new(self, view):
        CaptureEditing.track(view)

    def on_activated(self, view):
        CaptureEditing.track(view)