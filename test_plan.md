# TextEditor Test Plan

## Overview
Write unit tests for the TextEditor class in main.py using unittest with mocking for GUI dialogs.

## Testing Approach
- Use `unittest.mock` to patch `tk.filedialog` and `tk.messagebox` to avoid GUI interaction
- Test method logic directly without requiring the mainloop

## Tests Written

### TestTextEditor (15 tests)
1. **State initialization**
   - `test_initial_filepath_is_none`
   - `test_initial_is_modified_is_false`
   - `test_initial_title_contains_untitled`

2. **File operations**
   - `test_new_file_resets_state`
   - `test_open_file_loads_content`
   - `test_save_file_writes_to_path`
   - `test_save_file_as_returns_false_when_cancelled`
   - `test_save_file_uses_existing_path`

3. **Edit operations**
   - `test_edit_undo`
   - `test_edit_redo`
   - `test_edit_select_all`

4. **Exit guard**
   - `test_exit_app_prompts_when_modified`
   - `test_exit_app_destroys_when_not_modified`

5. **Status bar**
   - `test_update_status_bar_initially_correct`
   - `test_status_bar_updates_on_cursor_move`

6. **Line numbers**
   - `test_line_numbers_update`

### TestTextEditorEdgeCases (4 tests)
1. `test_open_file_cancelled`
2. `test_ask_save_if_dirty_returns_true_when_not_modified`
3. `test_ask_save_if_dirty_cancels_operation`

## Fix Applied
- Mock messagebox at class level (`setUpClass`/`tearDownClass`) to prevent dialogs during tearDown
- Return `False` from mocked messagebox to discard changes on shutdown