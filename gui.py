import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox, Menu
import json
import os
from markdown_handler import load_markdown, save_markdown

TRANSLATION_DIR = "translations"

class MarkdownTableEditor:
    def __init__(self, root):
        self.root = root
        self.current_lang = "en"  # Default language
        self.translations = {}
        self.available_languages = self.get_available_languages()
        self.load_translations(self.current_lang)

        self.root.title(self.tr("title"))

        # Variables
        self.columns = []
        self.data = []

        # Table
        self.tree = ttk.Treeview(root, show="headings")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Buttons frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.buttons = {
            "add_row": tk.Button(btn_frame, text=self.tr("add_row"), command=self.add_row),
            "edit_row": tk.Button(btn_frame, text=self.tr("edit_row"), command=self.edit_row),
            "remove_row": tk.Button(btn_frame, text=self.tr("remove_row"), command=self.remove_row),
            "add_column": tk.Button(btn_frame, text=self.tr("add_column"), command=self.add_column),
            "edit_column": tk.Button(btn_frame, text=self.tr("edit_column"), command=self.edit_column),
            "remove_column": tk.Button(btn_frame, text=self.tr("remove_column"), command=self.remove_column),
            "load": tk.Button(btn_frame, text=self.tr("load"), command=self.load_markdown),
            "save": tk.Button(btn_frame, text=self.tr("save"), command=self.save_markdown),
        }

        for i, key in enumerate(self.buttons):
            self.buttons[key].grid(row=0, column=i, padx=5)

        # Menu bar
        self.menu_bar = Menu(root)
        self.root.config(menu=self.menu_bar)

        self.preferences_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.tr("preferences"), menu=self.preferences_menu)
        self.preferences_menu.add_command(label=self.tr("language"), command=self.change_language)

    def get_available_languages(self):
        """Scan the translations folder and get available languages."""
        languages = {}
        if not os.path.exists(TRANSLATION_DIR):
            return languages

        for filename in os.listdir(TRANSLATION_DIR):
            if filename.endswith(".json"):
                lang_code = filename.replace(".json", "")
                try:
                    with open(os.path.join(TRANSLATION_DIR, filename), "r", encoding="utf-8") as file:
                        data = json.load(file)
                        languages[lang_code] = data.get("language_name", lang_code)
                except:
                    continue
        return languages

    def load_translations(self, lang):
        """Load translations from JSON files in the translations directory."""
        filepath = os.path.join(TRANSLATION_DIR, f"{lang}.json")
        default_filepath = os.path.join(TRANSLATION_DIR, "en.json")

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                self.translations = json.load(file)
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Falling back to English.")
            try:
                with open(default_filepath, "r", encoding="utf-8") as file:
                    self.translations = json.load(file)
            except FileNotFoundError:
                print("Error: English fallback file not found. Using empty translations.")
                self.translations = {}

    def tr(self, key):
        """Return the translated text based on the selected language."""
        return self.translations.get(key, key)

    def change_language(self):
        """Show a selection window to choose a language."""
        lang_window = tk.Toplevel(self.root)
        lang_window.title(self.tr("language"))

        tk.Label(lang_window, text=self.tr("select_language")).pack(pady=10)

        for lang_code, lang_name in self.available_languages.items():
            tk.Button(lang_window, text=lang_name, command=lambda lc=lang_code: self.set_language(lc, lang_window)).pack(pady=2)

    def set_language(self, lang_code, window):
        """Set the selected language and update the UI."""
        self.current_lang = lang_code
        self.load_translations(lang_code)
        self.update_language()
        window.destroy()

    def update_language(self):
        """Update all UI elements to reflect the new language."""
        self.root.title(self.tr("title"))
        for key in self.buttons:
            self.buttons[key].config(text=self.tr(key))
        self.menu_bar.entryconfig(1, label=self.tr("preferences"))
        self.preferences_menu.entryconfig(1, label=self.tr("language"))


    def _refresh_table(self):
        """Refresh table view."""
        self.tree["columns"] = self.columns
        self.tree.delete(*self.tree.get_children())

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for row in self.data:
            self.tree.insert("", "end", values=row)

    def add_row(self):
        self._open_edit_window(self.tr("add_row"), [""] * len(self.columns))

    def edit_row(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(self.tr("warning"), self.tr("select_row_edit"))
            return
        values = self.tree.item(selected_item, "values")
        self._open_edit_window(self.tr("edit_row"), list(values), selected_item)

    def remove_row(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(self.tr("warning"), self.tr("select_row_remove"))
            return
        self.tree.delete(selected_item)
        self.data = [self.tree.item(row, "values") for row in self.tree.get_children()]

    def add_column(self):
        col_name = simpledialog.askstring(self.tr("add_column"), self.tr("enter_column_name"))
        if not col_name:
            return
        self.columns.append(col_name)
        for i in range(len(self.data)):
            self.data[i] = list(self.data[i]) + [""]
        self._refresh_table()

    def edit_column(self):
        if not self.columns:
            messagebox.showwarning(self.tr("warning"), self.tr("no_columns_edit"))
            return

        col_name = simpledialog.askstring(self.tr("edit_column"), self.tr("enter_column_name"))
        if col_name not in self.columns:
            messagebox.showerror(self.tr("error"), self.tr("column_not_found"))
            return

        new_name = simpledialog.askstring(self.tr("edit_column"), self.tr("enter_new_column_name"))
        if not new_name:
            return

        index = self.columns.index(col_name)
        self.columns[index] = new_name
        self._refresh_table()

    def remove_column(self):
        if not self.columns:
            messagebox.showwarning(self.tr("warning"), self.tr("no_columns_edit"))
            return

        col_name = simpledialog.askstring(self.tr("remove_column"), self.tr("enter_column_name"))
        if col_name not in self.columns:
            messagebox.showerror(self.tr("error"), self.tr("column_not_found"))
            return

        index = self.columns.index(col_name)
        self.columns.pop(index)
        self.data = [row[:index] + row[index+1:] for row in self.data]
        self._refresh_table()

    def load_markdown(self):
        filepath = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md")])
        if not filepath:
            return
        self.columns, self.data = load_markdown(filepath)
        self._refresh_table()

    def save_markdown(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown Files", "*.md")])
        if not filepath:
            return
        if save_markdown(filepath, self.columns, self.data):
            messagebox.showinfo(self.tr("save"), self.tr("table_saved"))
        else:
            messagebox.showerror(self.tr("error"), self.tr("save_failed"))

