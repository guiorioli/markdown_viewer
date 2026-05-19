import sys
import os
import json
import webbrowser
from urllib.parse import urlparse, urldefrag
import tkinter as tk
from tkinter import filedialog, messagebox
import markdown2
from tkinterweb import HtmlFrame

APP_TITLE = "Markdown Viewer"
FILETYPES = [
    ("Markdown", "*.md *.markdown"),
    ("JSON", "*.json"),
    ("Texto", "*.txt"),
    ("Todos", "*.*"),
]
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".markdown_viewer_config.json")

# Index of "Salvar" in the Arquivo menu (0-based, separators count)
_SAVE_MENU_INDEX = 3

CSS_LIGHT = """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
    font-size: 16px;
    line-height: 1.7;
    color: #24292f;
    background: #ffffff;
    padding: 32px 48px;
    max-width: 900px;
    margin: 0 auto;
  }
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.3;
    color: #1f2328;
  }
  h1 { font-size: 2em; border-bottom: 2px solid #d0d7de; padding-bottom: 0.3em; }
  h2 { font-size: 1.5em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.2em; }
  h3 { font-size: 1.25em; }
  p { margin: 0.8em 0; }
  a { color: #0969da; text-decoration: none; }
  a:hover { text-decoration: underline; }
  code {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 0.1em 0.4em;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 0.9em;
    color: #cf222e;
  }
  pre {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin: 1em 0;
  }
  pre code {
    background: none;
    border: none;
    padding: 0;
    color: #24292f;
    font-size: 0.875em;
  }
  blockquote {
    border-left: 4px solid #d0d7de;
    color: #656d76;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f6f8fa;
    border-radius: 0 4px 4px 0;
  }
  ul, ol { padding-left: 2em; margin: 0.8em 0; }
  li { margin: 0.3em 0; }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
  }
  th, td {
    border: 1px solid #d0d7de;
    padding: 8px 12px;
    text-align: left;
  }
  th { background: #f6f8fa; font-weight: 600; }
  tr:nth-child(even) td { background: #f6f8fa; }
  img { max-width: 100%; height: auto; border-radius: 4px; }
  hr { border: none; border-top: 2px solid #d0d7de; margin: 2em 0; }
</style>
"""

CSS_DARK = """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
    font-size: 16px;
    line-height: 1.7;
    color: #e6edf3;
    background: #0d1117;
    padding: 32px 48px;
    max-width: 900px;
    margin: 0 auto;
  }
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.3;
    color: #f0f6fc;
  }
  h1 { font-size: 2em; border-bottom: 2px solid #30363d; padding-bottom: 0.3em; }
  h2 { font-size: 1.5em; border-bottom: 1px solid #30363d; padding-bottom: 0.2em; }
  h3 { font-size: 1.25em; }
  p { margin: 0.8em 0; }
  a { color: #58a6ff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  code {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 0.1em 0.4em;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 0.9em;
    color: #ff7b72;
  }
  pre {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin: 1em 0;
  }
  pre code {
    background: none;
    border: none;
    padding: 0;
    color: #e6edf3;
    font-size: 0.875em;
  }
  blockquote {
    border-left: 4px solid #30363d;
    color: #8b949e;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #161b22;
    border-radius: 0 4px 4px 0;
  }
  ul, ol { padding-left: 2em; margin: 0.8em 0; }
  li { margin: 0.3em 0; }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
  }
  th, td {
    border: 1px solid #30363d;
    padding: 8px 12px;
    text-align: left;
  }
  th { background: #161b22; font-weight: 600; }
  tr:nth-child(even) td { background: #161b22; }
  img { max-width: 100%; height: auto; border-radius: 4px; }
  hr { border: none; border-top: 2px solid #30363d; margin: 2em 0; }
</style>
"""

MARKDOWN_EXTRAS = [
    "fenced-code-blocks",
    "tables",
    "strike",
    "task_list",
    "footnotes",
    "header-ids",
    "code-friendly",
]


def _load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_config(data):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


class FindWindow(tk.Toplevel):
    def __init__(self, master, html_frame, dark_mode=False):
        super().__init__(master)
        self.html_frame = html_frame
        self._current_match = 1
        self._total_matches = 0
        self._query = ""
        self._last_query = ""

        self.title("Buscar")
        self.transient(master)
        self.resizable(False, False)

        frame = tk.Frame(self)
        frame.pack(padx=8, pady=8)

        self.entry = tk.Entry(frame, width=30)
        self.entry.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        self.entry.focus_set()

        tk.Button(frame, text="Anterior", command=self._prev).grid(row=1, column=0, padx=2)
        tk.Button(frame, text="Próximo", command=self._next).grid(row=1, column=1, padx=2)
        tk.Button(frame, text="Fechar", command=self._close).grid(row=1, column=2, padx=2)

        self.counter = tk.Label(frame, text="")
        self.counter.grid(row=2, column=0, columnspan=3, pady=(4, 0))

        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<Return>", lambda e: self._next())
        self.entry.bind("<Shift-Return>", lambda e: self._prev())
        self.bind("<Escape>", lambda e: self._close())

        self._apply_theme(dark_mode)

    def _apply_theme(self, dark_mode):
        if dark_mode:
            bg = "#0d1117"
            fg = "#e6edf3"
            entry_bg = "#161b22"
        else:
            bg = "#f6f8fa"
            fg = "#24292f"
            entry_bg = "#ffffff"
        self.configure(bg=bg)
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=bg)
                for c in child.winfo_children():
                    if isinstance(c, (tk.Label, tk.Button)):
                        c.configure(bg=bg, fg=fg)
                    elif isinstance(c, tk.Entry):
                        c.configure(bg=entry_bg, fg=fg, insertbackground=fg)

    def _on_key_release(self, event=None):
        self._query = self.entry.get()
        if not self._query:
            self.html_frame.find_text("")
            self._total_matches = 0
            self._current_match = 1
            self._last_query = ""
            self._update_counter()
            return
        if self._query == self._last_query:
            return
        self._last_query = self._query
        self._current_match = 1
        self._total_matches = self.html_frame.find_text(
            self._query, select=1, ignore_case=True, highlight_all=True
        )
        self._update_counter()

    def _next(self):
        if not self._query or self._total_matches == 0:
            return
        self._current_match += 1
        if self._current_match > self._total_matches:
            self._current_match = 1
        self.html_frame.find_text(
            self._query, select=self._current_match, ignore_case=True, highlight_all=True
        )
        self._update_counter()

    def _prev(self):
        if not self._query or self._total_matches == 0:
            return
        self._current_match -= 1
        if self._current_match < 1:
            self._current_match = self._total_matches
        self.html_frame.find_text(
            self._query, select=self._current_match, ignore_case=True, highlight_all=True
        )
        self._update_counter()

    def _update_counter(self):
        if self._total_matches == 0:
            self.counter.config(text="Nenhuma ocorrência")
        else:
            self.counter.config(text=f"{self._current_match} de {self._total_matches}")

    def _close(self):
        self.html_frame.find_text("")
        self.destroy()


class MarkdownViewer(tk.Tk):
    def __init__(self, filepath=None):
        super().__init__()
        self.current_file = None
        self._modified = False
        self._edit_mode = False
        self._preview_timer = None
        self._find_window = None
        self._config = _load_config()
        self.dark_mode = self._config.get("dark_mode", False)
        self._setup_window()
        self._setup_menu()
        self._setup_frame()
        self._bind_keys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        if filepath:
            self.load_file(filepath)

    def _setup_window(self):
        self.title(APP_TITLE)
        self.minsize(800, 450)
        if self._config.get("maximized"):
            self.state("zoomed")
        else:
            saved_geom = self._config.get("geometry")
            if saved_geom:
                self.geometry(saved_geom)
            else:
                self._apply_default_geometry()
        self._apply_window_bg()

    def _apply_default_geometry(self):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = int(screen_w * 0.80)
        height = int(width * 9 / 16)
        if height > int(screen_h * 0.85):
            height = int(screen_h * 0.85)
            width = int(height * 16 / 9)
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _apply_window_bg(self):
        self.configure(bg="#0d1117" if self.dark_mode else "#ffffff")

    def _setup_menu(self):
        menubar = tk.Menu(self)

        # Arquivo
        self._file_menu = tk.Menu(menubar, tearoff=0)
        self._file_menu.add_command(label="Novo  Ctrl+N", command=self.new_file)
        self._file_menu.add_command(label="Abrir...  Ctrl+O", command=self.open_file_dialog)
        self._file_menu.add_separator()
        # index 3 — Salvar (starts disabled)
        self._file_menu.add_command(label="Salvar  Ctrl+S", command=self.save_file, state=tk.DISABLED)
        self._file_menu.add_command(label="Salvar Como...  Ctrl+Shift+S", command=self.save_file_as)
        self._file_menu.add_separator()
        self._file_menu.add_command(label="Recarregar  F5", command=self.reload)
        self._file_menu.add_separator()
        self._file_menu.add_command(label="Sair  Esc", command=self._on_close)
        menubar.add_cascade(label="Arquivo", menu=self._file_menu)

        # Visualizar
        self._dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        self._edit_mode_var = tk.BooleanVar(value=False)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(
            label="Modo Edição  Ctrl+E",
            variable=self._edit_mode_var,
            command=self.toggle_edit_mode,
        )
        view_menu.add_checkbutton(
            label="Tema Escuro  Ctrl+D",
            variable=self._dark_mode_var,
            command=self.toggle_dark_mode,
        )
        menubar.add_cascade(label="Visualizar", menu=view_menu)

        # Ferramentas
        self._tools_menu = tk.Menu(menubar, tearoff=0)
        self._tools_menu.add_command(
            label="Formatar JSON  Ctrl+Shift+I",
            command=self.format_json,
            state=tk.DISABLED,
        )
        menubar.add_cascade(label="Ferramentas", menu=self._tools_menu)

        self.config(menu=menubar)

    def _setup_frame(self):
        # PanedWindow is always the root container
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        self.paned.pack(fill="both", expand=True)

        # Editor frame (left) — built now, added to paned only when edit mode is on
        self.editor_frame = tk.Frame(self.paned)
        self._setup_editor_toolbar()
        self._setup_editor()

        # Preview frame (right) — always visible
        self.html_frame = HtmlFrame(self.paned, messages_enabled=False, on_link_click=self._on_link_click)
        self.paned.add(self.html_frame, stretch="always")

    def _on_link_click(self, url):
        parsed = urlparse(url)

        # External links -> system browser
        if parsed.scheme in ("http", "https"):
            webbrowser.open(url)
            return

        # file:// or plain local paths
        clean_url, fragment = urldefrag(url)
        parsed_clean = urlparse(clean_url)

        if parsed_clean.scheme == "file":
            path = parsed_clean.path
            # Windows file URIs: /C:/path -> C:/path
            if path.startswith("/") and len(path) > 2 and path[2] == ":":
                path = path[1:]
            path = os.path.normpath(path)
        else:
            path = clean_url
            if path and not os.path.isabs(path) and self.current_file:
                base = os.path.dirname(self.current_file)
                path = os.path.normpath(os.path.join(base, path))

        current = os.path.normpath(self.current_file) if self.current_file else None
        current_dir = os.path.dirname(current) if current else None

        # Anchor in current file (same file, empty path, or same directory)
        is_same_file = not path or path == current
        is_same_dir = bool(current_dir and path == current_dir)
        if fragment and (is_same_file or is_same_dir):
            base_path = os.path.dirname(self.current_file) if self.current_file else ""
            content = self.editor.get("1.0", tk.END)
            self._render(content, base_path=base_path, fragment=fragment)
            return

        # Another markdown file
        if path and path.lower().endswith((".md", ".markdown")):
            if os.path.isfile(path):
                self.load_file(path, fragment=fragment)
            else:
                messagebox.showerror(APP_TITLE, f"Arquivo não encontrado:\n{path}")
            return

        # Other local files -> open with system default
        if path and os.path.isfile(path):
            webbrowser.open(f"file:///{os.path.abspath(path).replace(os.sep, '/')}")
        else:
            webbrowser.open(url)

    def _setup_editor_toolbar(self):
        self.editor_toolbar = tk.Frame(self.editor_frame, height=30)
        self.editor_toolbar.pack(side=tk.TOP, fill=tk.X)
        self.format_btn = tk.Button(
            self.editor_toolbar,
            text="Formatar JSON",
            command=self.format_json,
            state=tk.DISABLED,
        )
        self.format_btn.pack(side=tk.LEFT, padx=8, pady=4)

    def _setup_editor(self):
        scrollbar = tk.Scrollbar(self.editor_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor = tk.Text(
            self.editor_frame,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 11),
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12,
        )
        self.editor.pack(fill="both", expand=True)
        scrollbar.config(command=self.editor.yview)

        self._apply_editor_colors()
        self.editor.bind("<KeyRelease>", self._on_editor_key)

    def _apply_editor_colors(self):
        if self.dark_mode:
            self.editor_frame.configure(bg="#0d1117")
            self.editor.configure(
                bg="#0d1117",
                fg="#e6edf3",
                insertbackground="#58a6ff",
                selectbackground="#1f4d7a",
                selectforeground="#e6edf3",
            )
        else:
            self.editor_frame.configure(bg="#f6f8fa")
            self.editor.configure(
                bg="#f6f8fa",
                fg="#24292f",
                insertbackground="#0969da",
                selectbackground="#b6d4fb",
                selectforeground="#24292f",
            )

    def _bind_keys(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file_as())
        self.bind("<F5>", lambda e: self.reload())
        self.bind("<Escape>", lambda e: self._on_close())
        self.bind("<Control-d>", lambda e: self.toggle_dark_mode())
        self.bind("<Control-e>", lambda e: self.toggle_edit_mode())
        self.bind("<F2>", lambda e: self.toggle_edit_mode())
        self.bind("<Control-Shift-I>", lambda e: self.format_json())
        self.bind("<Control-Shift-i>", lambda e: self.format_json())
        self.bind("<Control-f>", lambda e: self._open_find())
        self.bind("<F3>", lambda e: self._find_next())
        self.bind("<Shift-F3>", lambda e: self._find_previous())

        # Navegacao por teclado no preview HTML
        self.bind_all("<Up>", self._scroll_up)
        self.bind_all("<Down>", self._scroll_down)
        self.bind_all("<Prior>", self._scroll_page_up)    # Page Up
        self.bind_all("<Next>", self._scroll_page_down)   # Page Down
        self.bind_all("<Home>", self._scroll_home)
        self.bind_all("<End>", self._scroll_end)
        self.bind_all("<space>", self._scroll_page_down)
        self.bind_all("<Shift-space>", self._scroll_page_up)

    def _scroll_up(self, event=None):
        if not self._edit_mode or not self.editor_frame.winfo_ismapped():
            self.html_frame.yview_scroll(-3, "units")
        return "break"

    def _scroll_down(self, event=None):
        if not self._edit_mode or not self.editor_frame.winfo_ismapped():
            self.html_frame.yview_scroll(3, "units")
        return "break"

    def _scroll_page_up(self, event=None):
        if not self._edit_mode or not self.editor_frame.winfo_ismapped():
            self.html_frame.yview_scroll(-1, "pages")
        return "break"

    def _scroll_page_down(self, event=None):
        if not self._edit_mode or not self.editor_frame.winfo_ismapped():
            self.html_frame.yview_scroll(1, "pages")
        return "break"

    def _scroll_home(self, event=None):
        if not self._edit_mode or not self.editor_frame.winfo_ismapped():
            self.html_frame.yview_moveto(0.0)
        return "break"

    def _scroll_end(self, event=None):
        if not self._edit_mode or not self.editor_frame.winfo_ismapped():
            self.html_frame.yview_moveto(1.0)
        return "break"

    # ------------------------------------------------------------------ #
    # Editor events                                                        #
    # ------------------------------------------------------------------ #

    def _on_editor_key(self, event=None):
        if not self.editor.edit_modified():
            return
        if not self._modified:
            self._modified = True
            self._update_title()
            self._file_menu.entryconfig(_SAVE_MENU_INDEX, state=tk.NORMAL)
        if self._preview_timer:
            self.after_cancel(self._preview_timer)
        self._preview_timer = self.after(300, self._update_preview)

    def _update_preview(self):
        content = self.editor.get("1.0", tk.END)
        base_path = os.path.dirname(self.current_file) if self.current_file else ""
        self._render(content, base_path=base_path)

    # ------------------------------------------------------------------ #
    # Title management                                                     #
    # ------------------------------------------------------------------ #

    def _update_title(self):
        if self.current_file:
            filename = os.path.basename(self.current_file)
            prefix = "* " if self._modified else ""
            self.title(f"{prefix}{filename} — {APP_TITLE}")
        else:
            self.title(APP_TITLE)

    # ------------------------------------------------------------------ #
    # Unsaved-changes guard                                                #
    # ------------------------------------------------------------------ #

    def _confirm_discard(self):
        """Returns True if it's safe to proceed (no unsaved changes, or user handled them)."""
        if not self._modified:
            return True
        answer = messagebox.askyesnocancel(
            APP_TITLE,
            "Há alterações não salvas. Deseja salvar antes de continuar?",
        )
        if answer is None:   # Cancelar
            return False
        if answer:           # Sim — salvar primeiro
            if not self.save_file():
                return False
        return True          # Não — descartar e prosseguir

    # ------------------------------------------------------------------ #
    # File operations                                                      #
    # ------------------------------------------------------------------ #

    def open_file_dialog(self):
        if not self._confirm_discard():
            return
        initial_dir = os.path.dirname(self.current_file) if self.current_file else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            title="Abrir arquivo",
            initialdir=initial_dir,
            filetypes=FILETYPES,
        )
        if path:
            self.load_file(path)

    def load_file(self, path, fragment=None):
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            messagebox.showerror(APP_TITLE, f"Arquivo não encontrado:\n{path}")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Erro ao ler arquivo:\n{e}")
            return

        self.current_file = path
        self._modified = False
        self._file_menu.entryconfig(_SAVE_MENU_INDEX, state=tk.DISABLED)

        # Populate editor without triggering _on_editor_key
        self.editor.edit_reset()
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.editor.edit_modified(False)

        self._update_title()
        self._update_format_controls()
        self._render(content, base_path=os.path.dirname(path), fragment=fragment)

    def new_file(self):
        if not self._confirm_discard():
            return
        self.current_file = None
        self._modified = False
        self.editor.edit_reset()
        self.editor.delete("1.0", tk.END)
        self.editor.edit_modified(False)
        self._file_menu.entryconfig(_SAVE_MENU_INDEX, state=tk.DISABLED)
        self._update_title()
        self._update_format_controls()
        self._render("", base_path="")

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        content = self.editor.get("1.0", tk.END).rstrip("\n") + "\n"
        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Erro ao salvar:\n{e}")
            return False
        self._modified = False
        self.editor.edit_modified(False)
        self._file_menu.entryconfig(_SAVE_MENU_INDEX, state=tk.DISABLED)
        self._update_title()
        return True

    def save_file_as(self):
        initial_dir = os.path.dirname(self.current_file) if self.current_file else os.path.expanduser("~")
        if self.current_file:
            initial_file = os.path.basename(self.current_file)
            ext = os.path.splitext(self.current_file)[1] or ".md"
        else:
            initial_file = "novo.md"
            ext = ".md"
        path = filedialog.asksaveasfilename(
            title="Salvar Como",
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=ext,
            filetypes=FILETYPES,
        )
        if not path:
            return False
        self.current_file = path
        self._update_format_controls()
        return self.save_file()

    # ------------------------------------------------------------------ #
    # Mode toggles                                                         #
    # ------------------------------------------------------------------ #

    def toggle_edit_mode(self):
        self._edit_mode = not self._edit_mode
        self._edit_mode_var.set(self._edit_mode)
        if self._edit_mode:
            # Remove html_frame, re-add both: editor (left, 40%) then html (right, 60%)
            self.paned.forget(self.html_frame)
            editor_width = max(int(self.winfo_width() * 0.40), 300)
            self.paned.add(self.editor_frame, stretch="always", width=editor_width)
            self.paned.add(self.html_frame, stretch="always")
            self._apply_editor_colors()
            self.editor.focus_set()
        else:
            # Remove editor; html_frame stays as the only pane
            self.paned.forget(self.editor_frame)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self._dark_mode_var.set(self.dark_mode)
        self._config["dark_mode"] = self.dark_mode
        _save_config(self._config)
        self._apply_window_bg()
        self._apply_editor_colors()
        if self._find_window is not None and self._find_window.winfo_exists():
            self._find_window._apply_theme(self.dark_mode)
        if self.current_file:
            self._render(self.editor.get("1.0", tk.END), base_path=os.path.dirname(self.current_file))
        elif self._edit_mode:
            self._update_preview()
        else:
            self.show_welcome()

    # ------------------------------------------------------------------ #
    # Rendering                                                            #
    # ------------------------------------------------------------------ #

    def _update_format_controls(self):
        is_json = bool(self.current_file and self.current_file.lower().endswith(".json"))
        state = tk.NORMAL if is_json else tk.DISABLED
        self.format_btn.config(state=state)
        self._tools_menu.entryconfig(0, state=state)

    def format_json(self):
        if not self.current_file or not self.current_file.lower().endswith(".json"):
            return
        content = self.editor.get("1.0", tk.END)
        try:
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", formatted)
            self._on_editor_key()
        except json.JSONDecodeError as e:
            messagebox.showerror(APP_TITLE, f"Não foi possível formatar o JSON:\n{e}")

    def _escape_html(self, text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _render(self, text, base_path="", fragment=None):
        css = CSS_DARK if self.dark_mode else CSS_LIGHT
        if self.current_file and self.current_file.lower().endswith(".json"):
            try:
                parsed = json.loads(text)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                body = f"<pre><code>{self._escape_html(pretty)}</code></pre>"
            except json.JSONDecodeError as e:
                err = self._escape_html(str(e))
                body = f"<pre style='color:#cf222e;'><code>JSON inválido:\n{err}</code></pre>"
        else:
            body = markdown2.markdown(text, extras=MARKDOWN_EXTRAS)
        base_url = f"file:///{base_path.replace(os.sep, '/')}/" if base_path else ""
        html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css}</head><body>{body}</body></html>"
        self.html_frame.load_html(html, base_url=base_url, fragment=fragment)

    def reload(self):
        if not self.current_file:
            return
        if self._modified:
            answer = messagebox.askyesno(
                APP_TITLE,
                "Há alterações não salvas. Recarregar vai descartar essas alterações. Continuar?",
            )
            if not answer:
                return
        self.load_file(self.current_file)

    def show_welcome(self):
        welcome_md = """# Markdown Viewer

Nenhum arquivo aberto.

Use **Ctrl+O** para abrir um arquivo `.md`, ou passe o caminho como argumento:

```
markdown_viewer.exe seu_arquivo.md
```

---

Para associar ao menu "Abrir com" do Windows, clique com o botão direito em qualquer
arquivo `.md`, escolha **Abrir com > Escolher outro aplicativo** e selecione este executável.
"""
        self._render(welcome_md)

    # ------------------------------------------------------------------ #
    # Window close                                                         #
    # ------------------------------------------------------------------ #

    def _on_close(self):
        if not self._confirm_discard():
            return
        self._config["maximized"] = (self.state() == "zoomed")
        if not self._config["maximized"]:
            self._config["geometry"] = self.geometry()
        self._config["dark_mode"] = self.dark_mode
        _save_config(self._config)
        self.quit()

    # ------------------------------------------------------------------ #
    # Find / Search                                                        #
    # ------------------------------------------------------------------ #

    def _open_find(self):
        if self._find_window is not None and self._find_window.winfo_exists():
            self._find_window.lift()
            self._find_window.entry.focus_set()
            self._find_window.entry.selection_range(0, tk.END)
            return
        self._find_window = FindWindow(self, self.html_frame, dark_mode=self.dark_mode)
        self._find_window.protocol("WM_DELETE_WINDOW", self._on_find_close)

    def _on_find_close(self):
        if self._find_window is not None and self._find_window.winfo_exists():
            self._find_window._close()
        self._find_window = None

    def _find_next(self):
        if self._find_window is not None and self._find_window.winfo_exists():
            self._find_window._next()
        else:
            self._open_find()

    def _find_previous(self):
        if self._find_window is not None and self._find_window.winfo_exists():
            self._find_window._prev()
        else:
            self._open_find()


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    app = MarkdownViewer(filepath=filepath)
    if not filepath:
        app.show_welcome()
    app.mainloop()


if __name__ == "__main__":
    main()
