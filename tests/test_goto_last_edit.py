"""Unit tests for GotoLastEdit bugfixes and history settings."""


import importlib
import os
import sys
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TESTS_DIR)
sys.path.insert(0, TESTS_DIR)
sys.path.insert(0, ROOT)

import mock_sublime as sublime  # noqa: E402
import mock_sublime_plugin as sublime_plugin  # noqa: E402

sys.modules["sublime"] = sublime
sys.modules["sublime_plugin"] = sublime_plugin

import GotoLastEdit as gle  # noqa: E402


def reload_plugin():
    importlib.reload(gle)
    gle.CaptureEditing.last_line.clear()
    gle.CaptureEditing.prev_line.clear()
    gle.CaptureEditing.posn.clear()
    gle.CaptureEditing.last_view[:] = []
    gle.CaptureEditing.view_refs.clear()
    return gle


class GotoLastEditTests(unittest.TestCase):
    def setUp(self):
        sublime.reset_mocks(history_size=50)
        self.gle = reload_plugin()

    def _edit(self, view, point, content=None):
        if content is not None:
            view.set_content(content)
        view.place_cursor(point)
        self.gle.CaptureEditing().on_modified(view)

    def test_closed_tab_removed_from_last_view(self):
        """Issue #10: closing the last-edited tab must not KeyError."""
        a = sublime.View("aaa\nbbb\n")
        b = sublime.View("xxx\nyyy\n")
        self.gle.CaptureEditing.track(a)
        self.gle.CaptureEditing.track(b)

        self._edit(a, 0)
        self._edit(b, 0)

        self.assertIn(b.id(), self.gle.CaptureEditing.last_view)
        self.gle.CaptureEditing().on_close(b)

        self.assertNotIn(b.id(), self.gle.CaptureEditing.last_view)
        self.assertNotIn(b.id(), self.gle.CaptureEditing.view_refs)

        # Must not raise KeyError — falls back to edits in A.
        cmd = self.gle.LastEditLineCommand(a)
        cmd.run(edit=None)
        self.assertIsNotNone(a._shown)

    def test_widget_modifications_are_ignored(self):
        """Issue #9 comment: Find panel keystrokes must not KeyError."""
        panel = sublime.View("query", is_widget=True)
        # Never tracked; on_modified must no-op without KeyError.
        self.gle.CaptureEditing().on_modified(panel)
        self.assertEqual(self.gle.CaptureEditing.last_line, {})
        self.assertEqual(self.gle.CaptureEditing.last_view, [])

    def test_track_on_demand_for_untacked_buffer(self):
        view = sublime.View("line1\nline2\n")
        # No on_new/on_activated — track happens inside on_modified.
        self._edit(view, 0)
        self.assertIn(view.id(), self.gle.CaptureEditing.last_line)
        self.assertEqual(self.gle.CaptureEditing.last_line[view.id()], [0])

    def test_history_size_setting_extends_storage(self):
        """Issue #8: history_size controls how many edits are kept."""
        sublime.reset_mocks(history_size=3)
        self.gle = reload_plugin()

        view = sublime.View("a\nb\nc\nd\ne\n")
        self.gle.CaptureEditing.track(view)
        # One edit per distinct line.
        for point in (0, 2, 4, 6, 8):
            self._edit(view, point)

        hist = self.gle.CaptureEditing.last_line[view.id()]
        self.assertEqual(len(hist), 3)
        self.assertEqual(hist, [4, 6, 8])
        self.assertEqual(len(self.gle.CaptureEditing.last_view), 3)

    def test_cycle_uses_full_history_not_hardcoded_five(self):
        sublime.reset_mocks(history_size=7)
        self.gle = reload_plugin()

        view = sublime.View("\n".join("abcdefg") + "\n")
        self.gle.CaptureEditing.track(view)
        points = [0, 2, 4, 6, 8, 10, 12]
        for point in points:
            self._edit(view, point)

        cmd = self.gle.LastEditLineCommand(view)
        seen = []
        for _ in range(7):
            cmd.run(edit=None)
            seen.append(view.sel()[0].begin())

        # Newest edit first, then walk back through all 7 slots.
        self.assertEqual(seen, [12, 10, 8, 6, 4, 2, 0])

    def test_focus_other_view_then_jump(self):
        a = sublime.View("aaa\n")
        b = sublime.View("bbb\nccc\n")
        self.gle.CaptureEditing.track(a)
        self.gle.CaptureEditing.track(b)
        self._edit(a, 0)
        self._edit(b, 4)

        cmd = self.gle.LastEditLineCommand(a)
        cmd.run(edit=None)

        self.assertIs(sublime.active_window().focused, b)
        self.assertIsNotNone(b._shown)

    def test_stale_last_view_ids_are_skipped(self):
        a = sublime.View("aaa\n")
        self.gle.CaptureEditing.track(a)
        self._edit(a, 0)
        # Simulate a leaked id that was never cleaned up.
        self.gle.CaptureEditing.last_view.append(99999)

        cmd = self.gle.LastEditLineCommand(a)
        cmd.run(edit=None)  # must not KeyError
        self.assertNotIn(99999, self.gle.CaptureEditing.last_view)


if __name__ == "__main__":
    unittest.main()