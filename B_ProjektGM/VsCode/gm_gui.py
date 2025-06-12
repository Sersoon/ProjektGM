import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import os
from datetime import datetime
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mini_allegro.db")

class MagazynApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System Magazynowy - Mini Allegro")
        self.geometry("950x600")
        self.configure(bg="white")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.create_produkty_tab()
        self.create_operacje_tab()
        self.create_zamow_tab()
        self.create_cart_tab()
        self.create_orders_tab()
        self.cart_items = []
        self.create_PozycjeZam_tab()

        self.create_analiza_tab() 
        

#Frame produkty
    def create_produkty_tab(self):
        self.produkty_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.produkty_frame, text="Produkty")

        self.tree = ttk.Treeview(
            self.produkty_frame,
            columns=("ID", "Nazwa", "Kategoria", "Cena", "Ilość", "LokalizacjaID"),
            show="headings"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, pady=10)

        self.load_products()

        self.entry_frame = ttk.Frame(self.produkty_frame)
        self.entry_frame.pack(pady=5)

        self.name_entry = ttk.Entry(self.entry_frame, width=25)
        self.name_entry.insert(0, "Nazwa produktu")
        self.name_entry.grid(row=0, column=0, padx=5)

        self.kategoria_entry = ttk.Entry(self.entry_frame, width=15)
        self.kategoria_entry.insert(0, "Kategoria")
        self.kategoria_entry.grid(row=0, column=1, padx=5)

        self.price_entry = ttk.Entry(self.entry_frame, width=10)
        self.price_entry.insert(0, "Cena")
        self.price_entry.grid(row=0, column=2, padx=5)

        self.qty_entry = ttk.Entry(self.entry_frame, width=10)
        self.qty_entry.insert(0, "Ilość")
        self.qty_entry.grid(row=0, column=3, padx=5)

        self.lokalizacja_entry = ttk.Entry(self.entry_frame, width=10)
        self.lokalizacja_entry.insert(0, "LokalizacjaID")
        self.lokalizacja_entry.grid(row=0, column=4, padx=5)

        add_button = ttk.Button(self.entry_frame, text="Dodaj produkt", command=self.add_product)
        add_button.grid(row=0, column=5, padx=5)

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ProduktID, Nazwa, Kategoria, Cena, Ilosc, LokalizacjaID FROM Produkty")
        for produkt in cursor.fetchall():
            self.tree.insert("", "end", values=produkt)
        conn.close()

    def add_product(self):
        nazwa = self.name_entry.get()
        kategoria = self.kategoria_entry.get()
        try:
            cena = float(self.price_entry.get())
            ilosc = int(self.qty_entry.get())
            lokalizacja_id = self.lokalizacja_entry.get()
            lokalizacja_id = int(lokalizacja_id) if lokalizacja_id else None
        except ValueError:
            messagebox.showerror("Błąd", "Cena, ilość i lokalizacja muszą być liczbami (lub pusta lokalizacja)!")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Produkty (Nazwa, Kategoria, Cena, Ilosc, LokalizacjaID) 
            VALUES (?, ?, ?, ?, ?)
        """, (nazwa, kategoria, cena, ilosc, lokalizacja_id))
        conn.commit()
        conn.close()

        self.load_products()
        messagebox.showinfo("Sukces", "Produkt dodany!")

#Frame operacje
    def create_operacje_tab(self):
        self.operacje_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.operacje_frame, text="Operacje Magazynowe")

        self.operacje_tree = ttk.Treeview(
            self.operacje_frame,
            columns=("ID", "ProduktID", "Typ", "Data", "Ilość", "Uwagi"),
            show="headings"
        )
        for col in self.operacje_tree["columns"]:
            self.operacje_tree.heading(col, text=col)
        self.operacje_tree.pack(fill="both", expand=True, pady=10)

        self.load_operations()

    def load_operations(self):
        for row in self.operacje_tree.get_children():
            self.operacje_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT OperacjaID, ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi FROM OperacjeMagazynowe ORDER BY DataOperacji DESC")
        for op in cursor.fetchall():
            self.operacje_tree.insert("", "end", values=op)
        conn.close()

#Frame zamów
    def create_zamow_tab(self):
        self.zamowienia_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.zamowienia_frame, text="Zamów")


        #Frame produków
        self.products_frame=ttk.LabelFrame(self.zamowienia_frame, text="Produkty", padding=1)
        self.products_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        #Ustawienie wielkości grida produktów
        self.zamowienia_frame.grid_rowconfigure(0, weight=8)
        self.products_frame.grid_rowconfigure(0, weight=1)
        self.products_frame.grid_columnconfigure(0, weight=1)
        
        # Tabela produktów z dostępną i zamawianą ilością
        self.products_tree = ttk.Treeview(
            self.products_frame,
            columns=("ProduktID", "Nazwa", "Dostępna ilość", "Cena produktu"),
            show="headings"
        )
        for col in self.products_tree["columns"]:
            self.products_tree.heading(col, text=col)
        self.products_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.load_products_for_order()


        #Frame danych
        self.data_frame=ttk.LabelFrame(self.zamowienia_frame, text="Dane", padding=1)
        self.data_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        #Ustawienie wielkości grida danych
        self.zamowienia_frame.grid_rowconfigure(1, weight=1)

       
        self.countInput = ttk.Entry(self.data_frame, width=10)
        self.countInput.insert(0, "Ilosc")
        self.countInput.grid(row=1, column=0, padx=5, pady=5, sticky="w")


        #Dane dodatkowe
        self.total_price=ttk.Label(self.data_frame, state="readonly", text="Cena")
        self.total_price.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.product_SelectedId=ttk.Entry(self.data_frame, width=5)
        self.product_SelectedId.insert(0, "ID")
        self.product_SelectedId.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Przycisk składania zamówienia
        order_button = ttk.Button(self.zamowienia_frame, text="Dodaj do koszyka", command=self.add_To_cart)
        order_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="n")

    def load_clients(self, combo):
        """Wypełnia combobox listą klientów"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT KlientID, Imie || ' ' || Nazwisko FROM Klienci")
        clients = cursor.fetchall()
        conn.close()

        # mapa nazwa -> id
        self.client_map = {nazwa: klient_id for klient_id, nazwa in clients}
        combo["values"] = list(self.client_map.keys())

    def load_products_for_order(self):
        """Ładuje produkty do tabeli w zakładce Zamówienia"""
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ProduktID, Nazwa, Ilosc, Cena FROM Produkty")
        for produkt_id, nazwa, cena, ilosc in cursor.fetchall():
            # Kolumna "Zamawiana ilość" zaczyna od zera
            self.products_tree.insert("", "end", values=(produkt_id, nazwa, cena, ilosc))
        conn.close()

#Metody koszyka
    def add_To_cart(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showerror("Błąd", "Wybierz produkt z listy")
            return

        produkt_values = self.products_tree.item(selected[0], "values")
        produkt_id = int(produkt_values[0])
        produkt_nazwa = produkt_values[1]
        try:
            dostepna_ilosc = float(produkt_values[2])
            produkt_cena = float(produkt_values[3])
            ilosc = float(self.countInput.get())
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowe dane liczbowe")
            return

        if ilosc <= 0:
            messagebox.showerror("Błąd", "Ilość musi być większa niż zero")
            return

        # Sprawdź, ile jest już w koszyku danego produktu
        ilosc_w_koszyku = 0
        for item in self.cart_items:
            if item["ProduktID"] == produkt_id:
                ilosc_w_koszyku = item["Ilosc"]
                break

        if ilosc + ilosc_w_koszyku > dostepna_ilosc:
            messagebox.showerror("Błąd", "Brak wystarczającej ilości produktu po dodaniu do koszyka")
            return

        # Jeśli produkt już jest w koszyku, aktualizuj ilość i cenę brutto
        for item in self.cart_items:
            if item["ProduktID"] == produkt_id:
                item["Ilosc"] += ilosc
                item["CenaBrutto"] = item["Ilosc"] * produkt_cena
                self.refresh_cart_tree()
                self.load_products_for_order()
                return

        # Jeśli produktu nie ma, dodaj nowy wpis
        cena_brutto = ilosc * produkt_cena

        self.cart_items.append({
            "ProduktID": produkt_id,
            "Nazwa": produkt_nazwa,
            "Ilosc": ilosc,
            "Cena": produkt_cena,
            "CenaBrutto": cena_brutto
        })

        self.refresh_cart_tree()
        self.load_products_for_order()
        self.load_operations()

    def reset_cart(self):
        self.cart_items.clear()
        self.refresh_cart_tree()

    def clear_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        self.cart_items.clear()
        self.cart_counter = 1

    def refresh_cart_tree(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        for i, item in enumerate(self.cart_items, start=1):
            self.cart_tree.insert("", "end", values=(
                i,
                item["ProduktID"],
                item["Nazwa"],
                item["Ilosc"],
                item["Cena"],
                item["CenaBrutto"]
            ))

#Frame koszyk
    def create_cart_tab(self):
        self.cart_frame=ttk.Frame(self.notebook)
        self.notebook.add(self.cart_frame, text="Koszyk")
    
        #frame Koszyk
        self.cart_label = ttk.LabelFrame(self.cart_frame, text="Koszyk")
        self.cart_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.cart_frame.grid_rowconfigure(0, weight=5)

        self.cart_tree = ttk.Treeview(
            self.cart_label,
            columns=("pozycja","ID Produktu", "Nazwa", "ilość", "Cena jednost", "cena brutto"),
            show="headings"
        )
        for col in self.cart_tree["columns"]:
            self.cart_tree.heading(col, text=col)
        self.cart_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        #frame dane
        self.cart_data_frame=ttk.LabelFrame(self.cart_frame, text="Dane")
        self.cart_data_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.cart_frame.grid_rowconfigure(0, weight=1)

        # Combobox z klientami
        self.client_combo = ttk.Combobox(self.cart_data_frame, state="readonly")
        self.client_combo.grid(row=0, column=0, padx=0, pady=5, sticky="w")
        self.load_clients(combo=self.client_combo)

        refresh_button = ttk.Button(self.cart_data_frame, text="Odśwież koszyk", command=self.refresh_cart_tree)
        refresh_button.grid(row=0, column=1, padx=10, pady=5, sticky="s")

        zapisz_button = ttk.Button(self.cart_data_frame, text="Zapisz zamowienie", command=self.add_zamowienie)
        zapisz_button.grid(row=0, column=2, padx=5, pady=5, sticky="s")

        reset_button=ttk.Button(self.cart_data_frame, text="Reset", command=self.reset_cart)
        reset_button.grid(row=0, column=4, padx=5, pady=5, sticky="s")

        #usun_button=ttk.Button(self.cart_data_frame, text="Usun wybrane", command=self.delete_position)
        #reset_button.grid(row=0, column=3, padx=5, pady=5, sticky="s")

    def add_zamowienie(self):
        klient_name = self.client_combo.get()
        if not klient_name or klient_name not in self.client_map:
            messagebox.showerror("Błąd", "Wybierz klienta.")
            return

        if not self.cart_tree.get_children():
            messagebox.showerror("Błąd", "Koszyk jest pusty.")
            return

        klient_id = self.client_map[klient_name]
        data = datetime.now().strftime("%Y-%m-%d")

        # Sumujemy kolumnę 'CenaBrutto' w cart_tree
        laczna_kwota = 0
        for item_id in self.cart_tree.get_children():
            values = self.cart_tree.item(item_id)["values"]
            # Zakładam, że kolumna "CenaBrutto" jest na 6 pozycji (indeks 5)
            try:
                cena_brutto = float(values[5])
            except (ValueError, IndexError):
                cena_brutto = 0
            laczna_kwota += cena_brutto

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            # Dodaj wpis do Zamowienia
            cursor.execute("""
                INSERT INTO Zamowienia (KlientID, DataZamowienia, Kwota)
                VALUES (?, ?, ?)
            """, (klient_id, data, laczna_kwota))
            zamowienie_id = cursor.lastrowid

            # Dodaj wpisy do PozycjeZamowienia na podstawie danych z cart_tree
            for item_id in self.cart_tree.get_children():
                values = self.cart_tree.item(item_id)["values"]
                # Przypuszczalnie masz kolumny:
                # pozycja (0), ID Produktu (1), Nazwa (2), ilość (3), Cena jednost (4), cena brutto (5)
                produkt_id = int(values[1])
                ilosc = float(values[3])
                cena = float(values[4])
                cena_brutto = float(values[5])

                cursor.execute("""
                    INSERT INTO PozycjeZamowienia (ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto)
                    VALUES (?, ?, ?, ?, ?)
                """, (zamowienie_id, produkt_id, ilosc, cena, cena_brutto))

                # Zmniejsz ilość produktu w magazynie
                cursor.execute("""
                    UPDATE Produkty SET Ilosc = Ilosc - ?
                    WHERE ProduktID = ?
                """, (ilosc, produkt_id))

                # Dodaj operację magazynową
                cursor.execute("""
                    INSERT INTO OperacjeMagazynowe (ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi)
                    VALUES (?, 'sprzedaz', ?, ?, ?)
                """, (produkt_id, data, ilosc, f"Zamówienie klienta {klient_name}"))

            conn.commit()
            messagebox.showinfo("Sukces", "Zamówienie zrealizowane!")
            self.clear_cart()
            self.load_products()
            self.load_products_for_order()
            self.load_orders()
            self.load_pozycje()
            self.load_operations

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Błąd", f"Błąd podczas zapisu: {e}")
        finally:
            conn.close()
    

#Frame zamówienia
    def create_orders_tab(self):
        self.orders_frame=ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Zamowienia")

        #Orders label
        self.orders_label=ttk.LabelFrame(self.orders_frame, text="Lista")
        self.orders_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.orders_frame.grid_rowconfigure(0, weight=5)

        self.test_button=ttk.Button(self.orders_frame, text="Usun rekord", command=self.delete_order)
        self.test_button.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")


        self.orders_tree = ttk.Treeview(
            self.orders_label,
            columns=("ZamowienieID","KlientID", "DataZamowienia", "Kwota"),
            show="headings"
        )
        for col in self.orders_tree["columns"]:
            self.orders_tree.heading(col, text=col)
        self.orders_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        #filtry label
        self.filtry_label=ttk.LabelFrame(self.orders_frame, text="Filtry")
        self.filtry_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.orders_frame.grid_rowconfigure(1, weight=1)

        # Combobox z klientami
        self.orders_client_combo = ttk.Combobox(self.filtry_label, state="readonly")
        self.orders_client_combo.grid(row=0, column=0, padx=0, pady=5, sticky="w")
        self.load_clients(combo=self.orders_client_combo)
        self.load_orders()

        self.filtruj_button=ttk.Button(self.filtry_label, text="Filtruj", command=self.FiltrujKlienta)
        self.filtruj_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.reset_button=ttk.Button(self.filtry_label, text="Reset", command=self.load_orders)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    def load_orders(self):
        """Ładuje produkty do tabeli w zakładce Zamówienia"""
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ZamowienieID, KlientID, DataZamowienia, Kwota FROM Zamowienia")
        for ZamowienieID, KlientID, DataZamowienia, Kwota in cursor.fetchall():
            # Kolumna "Zamawiana ilość" zaczyna od zera
            self.orders_tree.insert("", "end", values=(ZamowienieID, KlientID, DataZamowienia, Kwota))
        conn.close()

    def delete_order(self):
        selected_item=self.orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Błąd","Nie wybrano żadnej pozycji")
            return
        order_id=self.orders_tree.item(selected_item, "values")[0]

        try:
            conn=sqlite3.connect(DB_PATH)
            cursor=conn.cursor()
            cursor.execute("DELETE FROM Zamowienia WHERE ZamowienieID = ?", (order_id,))
            conn.commit()
            messagebox.showinfo("INFO",f"Usunięto rekordo ID: {order_id}")
        except sqlite3.Error as e:
            messagebox.showerror("Błąd",f"Błąd podczas usuwania {e}")
        finally:
            conn.close()

        self.load_orders()

    def FiltrujKlienta(self):
        klient_name=self.orders_client_combo.get()
        if not klient_name or klient_name not in self.client_map:
            messagebox.showerror("Błąd", "Wybierz klienta.")
            return
        klient_id=self.client_map[klient_name]

        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT ZamowienieID, KlientID, DataZamowienia, Kwota FROM Zamowienia WHERE KlientID={klient_id}")
        for ZamowienieID, KlientID, DataZamowienia, Kwota in cursor.fetchall():
            # Kolumna "Zamawiana ilość" zaczyna od zera
            self.orders_tree.insert("", "end", values=(ZamowienieID, KlientID, DataZamowienia, Kwota))
        conn.close()

#Frame pozycja
    def create_PozycjeZam_tab(self):
        self.pozycje_frame=ttk.Frame(self.notebook)
        self.notebook.add(self.pozycje_frame, text="PozycjeZamowien")

        self.pozycja_label=ttk.LabelFrame(self.pozycje_frame, text="Pozycje")
        self.pozycja_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.pozycje_frame.grid_rowconfigure(0, weight=5)
        
        self.pozycje_tree = ttk.Treeview(
            self.pozycja_label,
            columns=("PozycjaID","ZamowienieID", "ProduktID", "Ilosc", "Cena", "CenaBrutto"),
            show="headings"
        )
        for col in self.pozycje_tree["columns"]:
            self.pozycje_tree.heading(col, text=col)
        self.pozycje_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.load_pozycje()


        #filtry label
        self.poz_filtry_lab=ttk.LabelFrame(self.pozycje_frame, text="Filtry")
        self.poz_filtry_lab.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.pozycje_frame.grid_rowconfigure(1, weight=1)

        # Combobox z klientami
        self.poz_id_combo = ttk.Combobox(self.poz_filtry_lab, state="readonly")
        self.poz_id_combo.grid(row=0, column=0, padx=0, pady=5, sticky="w")
        self.LoadZamowienieCombo(ZamID=self.poz_id_combo)

        self.filtruj_button=ttk.Button(self.poz_filtry_lab, text="Filtruj", command=self.FiltrujZamID)
        self.filtruj_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.reset_button=ttk.Button(self.poz_filtry_lab, text="Reset", command=self.load_pozycje)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")


        self.odswiez_button=ttk.Button(self.poz_filtry_lab, text="Odśwież", command=self.LoadZamowienieCombo(ZamID=self.poz_id_combo))
        self.odswiez_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")


    
    def load_pozycje(self):
        for row in self.pozycje_tree.get_children():
            self.pozycje_tree.delete(row)

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()
        cursor.execute("SELECT PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto from PozycjeZamowienia")
        for PozID, ZamID, ProID, Il, Cen, CenB in cursor.fetchall():
            self.pozycje_tree.insert("", "end", values=(PozID, ZamID, ProID, Il, Cen, CenB))
        conn.close()

    def LoadZamowienieCombo(self, ZamID):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ZamowienieID FROM Zamowienia")
        Zamowienia = cursor.fetchall()
        conn.close()

        self.zam_map = [zid[0] for zid in Zamowienia]
        ZamID["values"] = self.zam_map

    def FiltrujZamID(self):
        zam_id = self.poz_id_combo.get()

        try:
            zam_id = int(zam_id)
        except ValueError:
            messagebox.showerror("Błąd", "Wybierz poprawne ID.")
            return

        if zam_id not in self.zam_map:
            messagebox.showerror("Błąd", "Wybierz poprawne ID.")
            return

        for row in self.pozycje_tree.get_children():
            self.pozycje_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto FROM PozycjeZamowienia WHERE ZamowienieID=?", (zam_id,))
        for PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto in cursor.fetchall():
            self.pozycje_tree.insert("", "end", values=(PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto))
        conn.close()

#Frame analiza
    def create_analiza_tab(self): 
        self.analiza_frame = ttk.Frame(self.notebook) 
        self.notebook.add(self.analiza_frame, text="Analiza") 

        # Dropdown do wyboru trybu analizy
        self.analysis_type = tk.StringVar()
        self.analysis_selector = ttk.Combobox(
            self.analiza_frame, 
            textvariable=self.analysis_type, 
            values=["Typ operacji", "Miesiąc i typ operacji", "Ranking produktów"]
        )
        self.analysis_selector.current(0)  # domyślnie "Typ operacji"
        self.analysis_selector.pack(pady=5)

        # Pola daty OD i DO
        date_frame = ttk.Frame(self.analiza_frame)
        date_frame.pack(pady=5)

        ttk.Label(date_frame, text="Data od (YYYY-MM-DD):").pack(side="left", padx=5)
        self.date_from_entry = ttk.Entry(date_frame, width=12)
        self.date_from_entry.pack(side="left")

        ttk.Label(date_frame, text="do:").pack(side="left", padx=5)
        self.date_to_entry = ttk.Entry(date_frame, width=12)
        self.date_to_entry.pack(side="left")

        # Tabela - będzie przebudowywana dynamicznie
        self.analiza_tree = ttk.Treeview(self.analiza_frame, show="headings") 
        self.analiza_tree.pack(fill="both", expand=True, pady=10) 

        # Przycisk analizy
        analiza_button = ttk.Button(
            self.analiza_frame, 
            text="Wykonaj analizę", 
            command=self.run_analysis
        ) 
        analiza_button.pack(pady=5)

        ttk.Button(self.analiza_frame, text="Pokaż wykres", command=self.show_chart).pack(pady=5)

    def run_analysis(self): 
        # Czyszczenie poprzednich wyników
        for row in self.analiza_tree.get_children(): 
            self.analiza_tree.delete(row) 

        # Odczyt dat z pól
        date_from = self.date_from_entry.get().strip()
        date_to = self.date_to_entry.get().strip()

        # Ustawienie domyślnego zakresu, jeśli pola są puste
        if not date_from:
            date_from = "0001-01-01"
        if not date_to:
            date_to = "9999-12-31"

        # Połączenie z bazą danych
        conn = sqlite3.connect(DB_PATH) 
        cursor = conn.cursor() 

        selected_analysis = self.analysis_type.get()

        if selected_analysis == "Typ operacji":
            query = """
                SELECT TypOperacji, COUNT(*) AS LiczbaOperacji, SUM(Ilosc) AS SumaIlosci 
                FROM OperacjeMagazynowe 
                WHERE date(DataOperacji) BETWEEN ? AND ?
                GROUP BY TypOperacji 
                ORDER BY LiczbaOperacji DESC
            """
            columns = ("Typ operacji", "Liczba operacji", "Suma ilości")

        elif selected_analysis == "Miesiąc i typ operacji":
            query = """
                SELECT strftime('%Y-%m', DataOperacji) AS Miesiac, TypOperacji, 
                    COUNT(*) AS LiczbaOperacji, SUM(Ilosc) AS SumaIlosci 
                FROM OperacjeMagazynowe 
                WHERE date(DataOperacji) BETWEEN ? AND ?
                GROUP BY Miesiac, TypOperacji 
                ORDER BY Miesiac DESC
            """
            columns = ("Miesiąc", "Typ operacji", "Liczba operacji", "Suma ilości")

        elif selected_analysis == "Ranking produktów":
            query = """
                SELECT p.Nazwa, COUNT(o.OperacjaID) AS LiczbaOperacji, SUM(o.Ilosc) AS SumaIlosci 
                FROM OperacjeMagazynowe o 
                JOIN Produkty p ON o.ProduktID = p.ProduktID 
                WHERE o.TypOperacji = 'Zamówienie' AND date(o.DataOperacji) BETWEEN ? AND ?
                GROUP BY p.Nazwa 
                ORDER BY SumaIlosci DESC
            """
            columns = ("Nazwa produktu", "Liczba operacji", "Suma sprzedanych sztuk")

        else:
            conn.close()
            return

        # Ustawienie kolumn tabeli
        self.analiza_tree["columns"] = columns
        for col in columns:
            self.analiza_tree.heading(col, text=col)

        # Wykonanie zapytania i wypełnienie tabeli
        cursor.execute(query, (date_from, date_to))
        for row in cursor.fetchall(): 
            self.analiza_tree.insert("", "end", values=row)

        conn.close()

    def show_chart(self):
        # Pobranie zakresu dat z pól Entry
        date_from = self.date_from_entry.get().strip() or "0001-01-01"
        date_to = self.date_to_entry.get().strip() or "9999-12-31"

        # Połączenie z bazą danych
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Przykład: liczba operacji wg typu (słupkowy)
        cursor.execute("""
            SELECT TypOperacji, COUNT(*) AS Liczba
            FROM OperacjeMagazynowe
            WHERE date(DataOperacji) BETWEEN ? AND ?
            GROUP BY TypOperacji
            ORDER BY Liczba DESC
        """, (date_from, date_to))

        wyniki = cursor.fetchall()
        conn.close()

        if not wyniki:
            return

        labels = [row[0] for row in wyniki]
        values = [row[1] for row in wyniki]

        # Tworzenie wykresu
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(labels, values, color='steelblue')
        ax.set_title("Liczba operacji wg typu")
        ax.set_ylabel("Liczba")
        ax.set_xlabel("Typ operacji")

        # Wstawienie wykresu do GUI
        canvas = FigureCanvasTkAgg(fig, master=self.analiza_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)


if __name__ == "__main__":
    app = MagazynApp()
    app.mainloop()

