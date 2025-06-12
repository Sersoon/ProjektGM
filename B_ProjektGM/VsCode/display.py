import sqlite3
import os

# Ładujemy bazę z tej samej lokalizacji co plik .py
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "mini_allegro.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def show_table(table_name):
    print(f"\n--- Tabela: {table_name} ---")
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]

        if not rows:
            print("Brak danych.")
            return

        # Wyświetlamy nagłówki kolumn
        print(" | ".join(col_names))
        print("-" * 80)

        # Wyświetlamy dane
        for row in rows:
            print(" | ".join(str(item) for item in row))
    except Exception as e:
        print(f"Błąd przy odczycie tabeli {table_name}: {e}")

tables = ["Produkty", "Klienci", "Zamowienia", "OperacjeMagazynowe", "Magazyn"]
for table in tables:
    show_table(table)

conn.close()
