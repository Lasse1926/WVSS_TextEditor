import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tkinter as tk
from main import TextEditor


class TestTextEditor(unittest.TestCase):

    def setUp(self):
        self.app = TextEditor()

    def tearDown(self):
        try:
            self.app.destroy()
        except tk.TclError:
            pass

    # ── State initialization ─────────────────────────────────────────────

    def test_initial_filepath_is_none(self):
        self.assertIsNone(self.app._filepath)

    def test_initial_is_modified_is_false(self):
        self.assertFalse(self.app._is_modified)

    def test_initial_title_contains_untitled(self):
        self.assertIn("Untitled", self.app.title())

    # ── File operations ────────────────────────────────────────────────

    def test_new_file_resets_state(self):
        self.app.text.insert("1.0", "test content")
        self.app._filepath = "/some/path.txt"
        self.app._is_modified = True
        self.app.new_file()
        self.assertEqual(self.app.text.get("1.0", "end-1c"), "")
        self.assertIsNone(self.app._filepath)
        self.assertFalse(self.app._is_modified)

    @patch("main.filedialog.askopenfilename")
    @patch("main.messagebox.askyesnocancel")
    def test_open_file_loads_content(self, mock_ask, mock_open_file):
        mock_ask.return_value = True
        mock_open_file.return_value = "/test/path.txt"
        with patch("builtins.open", mock_open(read_data="hello world")):
            self.app.open_file()
        self.assertEqual(self.app.text.get("1.0", "end-1c"), "hello world")
        self.assertEqual(self.app._filepath, "/test/path.txt")
        self.assertFalse(self.app._is_modified)

    @patch("main.filedialog.asksaveasfilename")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_file_writes_to_path(self, mock_file, mock_save_dialog):
        mock_save_dialog.return_value = "/test/save.txt"
        self.app.text.insert("1.0", "saved content")
        result = self.app.save_file_as()
        mock_file.assert_called_with("/test/save.txt", "w", encoding="utf-8")
        self.assertTrue(result)
        self.assertFalse(self.app._is_modified)

    @patch("main.filedialog.asksaveasfilename")
    def test_save_file_as_returns_false_when_cancelled(self, mock_save_dialog):
        mock_save_dialog.return_value = ""
        self.app.text.insert("1.0", "some content")
        result = self.app.save_file_as()
        self.assertFalse(result)

    @patch("main.filedialog.asksaveasfilename")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_file_uses_existing_path(self, mock_file, mock_save_dialog):
        self.app._filepath = "/existing/path.txt"
        self.app.text.insert("1.0", "content")
        result = self.app.save_file()
        mock_file.assert_called_with("/existing/path.txt", "w", encoding="utf-8")
        self.assertTrue(result)

    # ── Edit operations ────────────────────────────────────────────────

    def test_edit_undo(self):
        self.app.text.insert("1.0", "test")
        self.app.text.edit_undo()
        self.assertEqual(self.app.text.get("1.0", "end-1c"), "")

    def test_edit_redo(self):
        self.app.text.insert("1.0", "test")
        self.app.text.edit_undo()
        self.app.text.edit_redo()
        self.assertEqual(self.app.text.get("1.0", "end-1c"), "test")

    def test_edit_select_all(self):
        self.app.text.insert("1.0", "select all text")
        self.app.edit_select_all()
        self.assertEqual(self.app.text.get("1.0", "end-1c"), "select all text")

    # ── Exit guard ───────────────────────────────────────────────────────

    @patch("main.messagebox.askyesnocancel")
    def test_exit_app_prompts_when_modified(self, mock_ask):
        self.app.text.insert("1.0", "modified content")
        self.app._modified_callback()
        self.app.exit_app()
        mock_ask.assert_called_once()

    @patch("main.messagebox.askyesnocancel")
    def test_exit_app_destroys_when_not_modified(self, mock_ask):
        mock_ask.return_value = True
        self.app.exit_app()
        mock_ask.assert_not_called()
        self.app._is_modified = False  # Prevent double destroy in tearDown

    # ── Status bar ────────────────────────────────────────────────────

    def test_update_status_bar_initially_correct(self):
        status = self.app.status_var.get()
        self.assertIn("Ln 1", status)
        self.assertIn("Col 1", status)

    def test_status_bar_updates_on_cursor_move(self):
        self.app.text.insert("1.0", "ab")
        self.app.text.mark_set(tk.INSERT, "1.1")
        self.app._update_status_bar()
        status = self.app.status_var.get()
        self.assertIn("Col 2", status)

    # ── Line numbers ─────────────────────────────────────────────────

    def test_line_numbers_update(self):
        self.app.text.insert("1.0", "line1\nline2\nline3")
        self.app._update_line_numbers()
        ln_content = self.app.ln_text.get("1.0", "end-1c")
        self.assertIn("1", ln_content)
        self.assertIn("3", ln_content)


class TestTextEditorEdgeCases(unittest.TestCase):

    def setUp(self):
        self.app = TextEditor()

    def tearDown(self):
        try:
            self.app.destroy()
        except tk.TclError:
            pass

    @patch("main.filedialog.askopenfilename")
    @patch("main.messagebox.askyesnocancel")
    def test_open_file_cancelled(self, mock_ask, mock_open):
        mock_ask.return_value = True
        mock_open.return_value = ""
        result = self.app.open_file()
        self.assertEqual(result, "Path Error")

    @patch("main.messagebox.askyesnocancel")
    def test_ask_save_if_dirty_returns_true_when_not_modified(self, mock_ask):
        self.app._is_modified = False
        result = self.app._ask_save_if_dirty()
        self.assertTrue(result)
        mock_ask.assert_not_called()

    @patch("main.messagebox.askyesnocancel")
    def test_ask_save_if_dirty_cancels_operation(self, mock_ask):
        self.app._is_modified = True
        mock_ask.return_value = None
        result = self.app._ask_save_if_dirty()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()