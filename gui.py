import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from markdown_handler import load_markdown, save_markdown

class MarkdownTableEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Table Editor")

        # Variabili
        self.columns = []
        self.data = []

        # Tabella
        self.tree = ttk.Treeview(root, show="headings")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Pulsanti
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Aggiungi Riga", command=self.add_row).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Modifica Riga", command=self.edit_row).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Rimuovi Riga", command=self.remove_row).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Aggiungi Colonna", command=self.add_column).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Modifica Colonna", command=self.edit_column).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Rimuovi Colonna", command=self.remove_column).grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="Carica", command=self.load_markdown).grid(row=0, column=6, padx=5)
        tk.Button(btn_frame, text="Salva", command=self.save_markdown).grid(row=0, column=7, padx=5)

    def _refresh_table(self):
        self.tree["columns"] = self.columns
        self.tree.delete(*self.tree.get_children())

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for row in self.data:
            self.tree.insert("", "end", values=row)

    def add_row(self):
        self._open_edit_window("Aggiungi", [""] * len(self.columns))

    def edit_row(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attenzione", "Seleziona una riga da modificare")
            return
        values = self.tree.item(selected_item, "values")
        self._open_edit_window("Modifica", list(values), selected_item)

    def remove_row(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attenzione", "Seleziona una riga da rimuovere")
            return
        self.tree.delete(selected_item)
        self.data = [self.tree.item(row, "values") for row in self.tree.get_children()]

    def add_column(self):
        col_name = simpledialog.askstring("Nuova Colonna", "Inserisci il nome della colonna:")
        if not col_name:
            return
        self.columns.append(col_name)
        for i in range(len(self.data)):
            self.data[i] = list(self.data[i]) + [""]
        self._refresh_table()

    def edit_column(self):
        if not self.columns:
            messagebox.showwarning("Attenzione", "Nessuna colonna da modificare")
            return

        col_name = simpledialog.askstring("Modifica Colonna", "Nome della colonna da modificare:")
        if col_name not in self.columns:
            messagebox.showerror("Errore", "Colonna non trovata")
            return

        new_name = simpledialog.askstring("Nuovo Nome", "Inserisci il nuovo nome della colonna:")
        if not new_name:
            return

        index = self.columns.index(col_name)
        self.columns[index] = new_name
        self._refresh_table()

    def remove_column(self):
        if not self.columns:
            messagebox.showwarning("Attenzione", "Nessuna colonna da rimuovere")
            return

        col_name = simpledialog.askstring("Rimuovi Colonna", "Nome della colonna da rimuovere:")
        if col_name not in self.columns:
            messagebox.showerror("Errore", "Colonna non trovata")
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
            messagebox.showinfo("Salvato", "Tabella salvata con successo!")
        else:
            messagebox.showerror("Errore", "Impossibile salvare il file.")

    def _open_edit_window(self, mode, values, selected_item=None):
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"{mode} riga")

        entries = []
        for i, col in enumerate(self.columns):
            tk.Label(edit_window, text=f"{col}:").grid(row=i, column=0)
            entry = tk.Entry(edit_window)
            entry.grid(row=i, column=1)
            entry.insert(0, values[i])
            entries.append(entry)

        def save():
            new_values = [entry.get() for entry in entries]
            if mode == "Aggiungi":
                self.tree.insert("", "end", values=new_values)
                self.data.append(new_values)
            else:
                self.tree.item(selected_item, values=new_values)
                self.data = [self.tree.item(row, "values") for row in self.tree.get_children()]
            edit_window.destroy()

        tk.Button(edit_window, text="Salva", command=save).grid(row=len(self.columns), column=0, columnspan=2)
