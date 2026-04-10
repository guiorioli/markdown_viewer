import sys
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import markdown2
from tkinterweb import HtmlFrame

APP_TITLE = "Markdown Viewer"
FILETYPES = [("Markdown", "*.md *.markdown"), ("Texto", "*.txt"), ("Todos", "*.*")]
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".markdown_viewer_config.json")

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


class MarkdownViewer(tk.Tk):
    def __init__(self, filepath=None):
        super().__init__()
        self.current_file = None
        config = _load_config()
        self.dark_mode = config.get("dark_mode", False)
        self._setup_window()
        self._setup_menu()
        self._setup_frame()
        self._bind_keys()
        if filepath:
            self.load_file(filepath)

    def _setup_window(self):
        self.title(APP_TITLE)
        self.geometry("1024x768")
        self.minsize(600, 400)
        self._apply_window_bg()

    def _apply_window_bg(self):
        self.configure(bg="#0d1117" if self.dark_mode else "#ffffff")

    def _setup_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Abrir...  Ctrl+O", command=self.open_file_dialog)
        file_menu.add_command(label="Recarregar  F5", command=self.reload)
        file_menu.add_separator()
        file_menu.add_command(label="Sair  Esc", command=self.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        self._dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(
            label="Tema Escuro  Ctrl+D",
            variable=self._dark_mode_var,
            command=self.toggle_dark_mode,
        )
        menubar.add_cascade(label="Visualizar", menu=view_menu)

        self.config(menu=menubar)

    def _setup_frame(self):
        self.html_frame = HtmlFrame(self, messages_enabled=False)
        self.html_frame.pack(fill="both", expand=True)

    def _bind_keys(self):
        self.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.bind("<F5>", lambda e: self.reload())
        self.bind("<Escape>", lambda e: self.quit())
        self.bind("<Control-d>", lambda e: self.toggle_dark_mode())

    def open_file_dialog(self):
        initial_dir = os.path.dirname(self.current_file) if self.current_file else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            title="Abrir arquivo Markdown",
            initialdir=initial_dir,
            filetypes=FILETYPES,
        )
        if path:
            self.load_file(path)

    def load_file(self, path):
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
        filename = os.path.basename(path)
        self.title(f"{filename} — {APP_TITLE}")
        self._render(content, base_path=os.path.dirname(path))

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self._dark_mode_var.set(self.dark_mode)
        _save_config({"dark_mode": self.dark_mode})
        self._apply_window_bg()
        if self.current_file:
            self.reload()
        else:
            self.show_welcome()

    def _render(self, markdown_text, base_path=""):
        css = CSS_DARK if self.dark_mode else CSS_LIGHT
        body = markdown2.markdown(markdown_text, extras=MARKDOWN_EXTRAS)
        base_url = f"file:///{base_path.replace(os.sep, '/')}/" if base_path else ""
        html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css}</head><body>{body}</body></html>"
        self.html_frame.load_html(html, base_url=base_url)

    def reload(self):
        if self.current_file:
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


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    app = MarkdownViewer(filepath=filepath)
    if not filepath:
        app.show_welcome()
    app.mainloop()


if __name__ == "__main__":
    main()
