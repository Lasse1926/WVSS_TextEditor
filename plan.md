# Plan: Python tkinter Text Editor

## Context
Build a single-file Python tkinter text editor (`main.py`) from scratch.
Requirements:
- **Input**: text typed by the user
- **Processing**: display in a GUI (text editor widget)
- **Output**: save as file + GUI with standard menu and dialog-design principles (ISO 9241 / Grundsätze der Dialoggestaltung)

---

## Architecture

**Single file**: `main.py`  
**Single class**: `TextEditor(tk.Tk)` — subclasses `tk.Tk` directly (no separate root variable)  
**No third-party dependencies** — stdlib only (`tkinter`, `os`)

### Instance State

| Attribute | Type | Purpose |
|---|---|---|
| `self._filepath` | `str \| None` | Current open file path; `None` = new unsaved file |
| `self._is_modified` | `bool` | Dirty flag; drives `*` in title bar |
| `self.text` | `tk.Text` | Main editor widget |
| `self.ln_text` | `tk.Text` | Read-only line-number mirror (disabled Text widget) |
| `self.status_var` | `tk.StringVar` | Status bar content |

---

## Menu Structure

```
File:  New (Ctrl+N) | Open... (Ctrl+O) | Save (Ctrl+S) | Save As... (Ctrl+Shift+S) | --- | Exit
Edit:  Undo (Ctrl+Z) | Redo (Ctrl+Y) | --- | Cut | Copy | Paste | --- | Select All (Ctrl+A)
Help:  About
```

---

## Layout

```
┌──────────────────────────────────────────────────────┐
│  [File]  [Edit]  [Help]                    menu bar  │
├────┬─────────────────────────────────────┬───────────┤
│    │                                     │           │
│ 1  │                                     │  Scrollbar│
│ 2  │     tk.Text  (main editor)          │  (vert)   │
│ 3  │     wrap='none', undo=True          │           │
│ .. │     font=Consolas 11                │           │
│    │                                     │           │
├────┴─────────────────────────────────────┴───────────┤
│         Scrollbar (horizontal)                       │
├──────────────────────────────────────────────────────┤
│  Ln 1, Col 1  |  Untitled              status bar    │
└──────────────────────────────────────────────────────┘
```

---

## Method List

```
TextEditor(tk.Tk)
├── __init__()
├── _build_menu()
├── _build_editor_area()       # Text widget + line numbers + scrollbars
├── _build_status_bar()        # Label at bottom
├── _bind_shortcuts()
│
├── _modified_callback()       # <<Modified>> handler with double-fire guard
├── _update_status_bar()       # Ln/Col display from INSERT mark
├── _update_line_numbers()     # Regenerate ln_text content
├── _set_title()               # "* filename - TextEditor"
├── _on_yscroll()              # Sync vsb + ln_text on scroll
├── _scroll_both()             # Scroll text + ln_text from scrollbar
│
├── _ask_save_if_dirty() -> bool   # Yes/No/Cancel dialog; returns safe-to-proceed
├── _write_file(path) -> bool      # Actually writes file; shows error on OSError
│
├── new_file()
├── open_file()                # Returns "break" (bound on self.text)
├── save_file() -> bool        # Delegates to save_file_as() if no path
├── save_file_as() -> bool
├── exit_app()                 # WM_DELETE_WINDOW + menu Exit
│
├── edit_undo() / edit_redo()  # TclError-safe
├── edit_cut/copy/paste()      # Delegate to virtual events
├── edit_select_all()
└── show_about()               # messagebox.showinfo with shortcut list
```

---

## Key Implementation Details

### `_modified_callback`
`<<Modified>>` fires twice per edit (once when dirty=True, once after we reset it).
Guard: `if not self.text.edit_modified(): return` prevents the second firing from doing anything.

### `_ask_save_if_dirty` return semantics
`askyesnocancel` returns `True` (Yes → save), `False` (No → discard), `None` (Cancel → abort).

### `_write_file` — strip phantom newline
Use `self.text.get('1.0', 'end-1c')` — `end-1c` strips the trailing newline tkinter adds internally.

### `open_file` must return `"break"`
Bound directly on `self.text` so it must return `"break"` to suppress the Text widget's built-in Ctrl+O handler (which inserts a newline).

### Line numbers — mirror approach
A disabled `tk.Text` with matching font. `_on_yscroll` keeps it in sync with the main editor by calling `self.ln_text.yview_moveto(first)`.

### `edit_reset()` on New/Open
Clears the undo/redo stack so the user cannot undo back into the previous document.

---

## Dialog Design Principles Applied (ISO 9241 / Grundsätze der Dialoggestaltung)

| Principle | Implementation |
|---|---|
| Task suitability | File dialogs filtered to `.txt` / `All files` |
| Self-descriptiveness | Title bar shows filename + `*` when unsaved |
| Controllability | User can cancel every destructive action |
| Conformity with expectations | Standard Ctrl shortcuts, standard menu order |
| Error tolerance | `_ask_save_if_dirty` prevents accidental data loss; OSError shown in `showerror` |
| Suitability for learning | `About` dialog lists all shortcuts |

---

## Implementation Order

1. Imports + skeleton `__init__` + `mainloop` → window opens
2. `_build_editor_area` (Text, scrollbars, no line numbers) → can type
3. `_build_status_bar` → status label visible
4. `_build_menu` (all entries) → menu visible
5. `_write_file`, `save_file_as`, `save_file` → saving works
6. `_set_title`, `_modified_callback` → dirty tracking works
7. `new_file`, `open_file`, `_ask_save_if_dirty`, `exit_app` → full file lifecycle
8. Edit methods + wire all menu commands → Edit menu works
9. `_bind_shortcuts` + `_update_status_bar` bindings → shortcuts work
10. Line numbers (`ln_text`, `_on_yscroll`, `_scroll_both`, `_update_line_numbers`) → numbers sync
11. `show_about`, `minsize`, padding polish → done

---

## Verification

```bash
python main.py
```

Manual test checklist:
- [ ] Window opens with title "Untitled - TextEditor"
- [ ] Type text → title changes to "* Untitled - TextEditor", line numbers update
- [ ] File → Save As → saves `.txt` file, title loses `*`
- [ ] File → Open → loads file, line numbers correct
- [ ] Close with unsaved changes → Yes/No/Cancel dialog appears
- [ ] Ctrl+Z / Ctrl+Y undo/redo work
- [ ] Cut/Copy/Paste work via menu and keyboard
- [ ] Status bar shows correct Ln/Col on cursor movement
- [ ] Line numbers stay in sync when scrolling
- [ ] Help → About shows shortcut list
