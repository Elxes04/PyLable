import pandas as pd

def load_markdown(filepath):
    """Carica una tabella Markdown da file e restituisce colonne e dati."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()
            columns = [x.strip() for x in lines[0].split("|")[1:-1]]
            data_lines = lines[2:]
            data = [[x.strip() for x in line.split("|")[1:-1]] for line in data_lines if "|" in line]
            return columns, data
    except Exception as e:
        print(f"Errore nel caricamento del file: {e}")
        return None, []

def save_markdown(filepath, columns, data):
    """Salva i dati in formato Markdown."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write("| " + " | ".join(columns) + " |\n")
            file.write("|" + "|".join(["----"] * len(columns)) + "|\n")
            for row in data:
                file.write("| " + " | ".join(row) + " |\n")
            file.write(f"\n- `Date: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}`\n")
        return True
    except Exception as e:
        print(f"Errore nel salvataggio del file: {e}")
        return False
