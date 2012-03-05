import sublime
import sublime_plugin


class LastEditLineCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        if (len(CaptureEditing.last_view) > 0 and self.view.id() != CaptureEditing.last_view[-1] and CaptureEditing.last_view[-1] > 0):
            sublime.active_window().focus_view(CaptureEditing.view_refs[CaptureEditing.last_view[-1]])
            CaptureEditing.last_view.pop(-1)
        if len(CaptureEditing.last_line[self.view.id()]) > CaptureEditing.posn[self.view.id()]:
            self.view.show(self.view.line(CaptureEditing.last_line[self.view.id()][-(CaptureEditing.posn[self.view.id()] + 1)]))
            self.view.sel().clear()
            self.view.sel().add(self.view.line(CaptureEditing.last_line[self.view.id()][-(CaptureEditing.posn[self.view.id()] + 1)]))
            CaptureEditing.posn[self.view.id()] = (CaptureEditing.posn[self.view.id()] + 1) % 5
        else:
            CaptureEditing.posn[self.view.id()] = 0


class CaptureEditing(sublime_plugin.EventListener):
    last_line = {}
    prev_line = {}
    posn = {}
    last_view = []
    view_refs = {}

    def on_modified(self, view):
        sel = view.sel()[0]
        curr_line, _ = view.rowcol(sel.begin())
        CE = CaptureEditing
        if CE.prev_line[view.id()] == -1 or curr_line != CE.prev_line[view.id()]:
            CE.prev_line[view.id()] = curr_line
            CE.last_line[view.id()].append(sel.begin())
            if len(CE.last_line[view.id()]) > 10:
                CE.last_line[view.id()].pop(0)
            CE.last_view.append(view.id())
            if len(CE.last_view) > 10:
                CE.last_view.pop(0)

    def on_close(self, view):
        CE = CaptureEditing
        del CE.last_line[view.id()]
        del CE.prev_line[view.id()]
        del CE.view_refs[view.id()]
        del CE.posn[view.id()]

    def on_new(self, view):
        CE = CaptureEditing
        CE.last_line[view.id()] = []
        CE.prev_line[view.id()] = -1
        CE.posn[view.id()] = 0
        CE.view_refs[view.id()] = view

    def on_activated(self, view):
        CE = CaptureEditing
        if view.id() not in CE.last_line:
            CE.last_line[view.id()] = []
        if view.id() not in CE.prev_line:
            CE.prev_line[view.id()] = -1
        if view.id() not in CE.posn:
            CE.posn[view.id()] = 0
        if view.id() not in CE.view_refs:
            CE.view_refs[view.id()] = view
