import os
import sqlite3
import random
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "mini_allegro.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

TOTAL_OPERATIONS = 600

produkt_ids = [row[0] for row in cursor.execute("SELECT ProduktID FROM Produkty").fetchall()]
magazyny_ids = [row[0] for row in cursor.execute("SELECT MagazynID FROM Magazyn").fetchall()]

operacje_do_dodania = []
zamowienia = []

# 1. Generujemy dostawy (21% = 126) — żeby mieć stany
num_dostawy = int(TOTAL_OPERATIONS * 0.21)
for _ in range(num_dostawy):
    produkt_id = random.choice(produkt_ids)
    ilosc = random.randint(10, 50)  # większe dostawy
    data_obj = datetime.now() - timedelta(days=random.randint(0, 10000))
    magazyn_id = random.choice(magazyny_ids)

    cursor.execute("UPDATE Produkty SET Ilosc = Ilosc + ? WHERE ProduktID = ?", (ilosc, produkt_id))
    cursor.execute("UPDATE Magazyn SET AktualnaIlosc = AktualnaIlosc + ? WHERE MagazynID = ?", (ilosc, magazyn_id))
    cursor.execute("SELECT Ilosc FROM LokalizacjaProduktu WHERE ProduktID = ? AND MagazynID = ?", (produkt_id, magazyn_id))
    lokal = cursor.fetchone()
    if lokal:
        cursor.execute("UPDATE LokalizacjaProduktu SET Ilosc = Ilosc + ? WHERE ProduktID = ? AND MagazynID = ?", (ilosc, produkt_id, magazyn_id))
    else:
        cursor.execute("INSERT INTO LokalizacjaProduktu (ProduktID, MagazynID, Ilosc) VALUES (?, ?, ?)", (produkt_id, magazyn_id, ilosc))

    operacje_do_dodania.append((produkt_id, "Dostawa", data_obj, ilosc, "Dostawa towaru"))

# 2. Generujemy zamówienia (35% = 210)
num_zamowienia = int(TOTAL_OPERATIONS * 0.35)
przyjete_zamowienia = 0
while przyjete_zamowienia < num_zamowienia:
    produkt_id = random.choice(produkt_ids)
    ilosc = random.randint(1, 20)
    data_obj = datetime.now() - timedelta(days=random.randint(0, 10000))

    cursor.execute("SELECT Ilosc FROM Produkty WHERE ProduktID = ?", (produkt_id,))
    wynik = cursor.fetchone()
    ilosc_dostepna = wynik[0] if wynik else 0

    if ilosc_dostepna < ilosc:
        continue  # nie ma wystarczająco produktu, pomijamy

    # Realizujemy zamówienie
    cursor.execute("UPDATE Produkty SET Ilosc = Ilosc - ? WHERE ProduktID = ?", (ilosc, produkt_id))
    cursor.execute("""
        SELECT MagazynID FROM LokalizacjaProduktu 
        WHERE ProduktID = ? AND Ilosc >= ?
        ORDER BY Ilosc DESC LIMIT 1
    """, (produkt_id, ilosc))
    lokalizacja = cursor.fetchone()
    if not lokalizacja:
        continue
    magazyn_id = lokalizacja[0]
    cursor.execute("UPDATE LokalizacjaProduktu SET Ilosc = Ilosc - ? WHERE ProduktID = ? AND MagazynID = ?", (ilosc, produkt_id, magazyn_id))
    cursor.execute("UPDATE Magazyn SET AktualnaIlosc = AktualnaIlosc - ? WHERE MagazynID = ?", (ilosc, magazyn_id))

    operacje_do_dodania.append((produkt_id, "Zamówienie", data_obj, ilosc, "Zamówienie klienta"))
    zamowienia.append((produkt_id, ilosc, data_obj))
    przyjete_zamowienia += 1

# 3. Generujemy wysyłki (35% = 210), każda powiązana z jednym zamówieniem
for produkt_id, ilosc, data_zamowienia in zamowienia:
    dni_po_zamowieniu = random.randint(1, 14)
    data_obj = data_zamowienia + timedelta(days=dni_po_zamowieniu)

    operacje_do_dodania.append((produkt_id, "Wysyłka", data_obj, ilosc, "Wysyłka zgodna z zamówieniem"))

# 4. Zwroty i reklamacje (9% = 54, podzielone po równo)
num_zwroty = num_reklamacje = int(TOTAL_OPERATIONS * 0.09 / 2)

for _ in range(num_zwroty):
    produkt_id = random.choice(produkt_ids)
    ilosc = random.randint(1, 10)
    data_obj = datetime.now() - timedelta(days=random.randint(0, 10000))

    cursor.execute("UPDATE Produkty SET Ilosc = Ilosc + ? WHERE ProduktID = ?", (ilosc, produkt_id))
    operacje_do_dodania.append((produkt_id, "Zwrot", data_obj, ilosc, "Zwrot od klienta"))

for _ in range(num_reklamacje):
    produkt_id = random.choice(produkt_ids)
    ilosc = random.randint(1, 10)
    data_obj = datetime.now() - timedelta(days=random.randint(0, 10000))

    cursor.execute("SELECT Ilosc FROM Produkty WHERE ProduktID = ?", (produkt_id,))
    ilosc_aktualna = cursor.fetchone()[0]
    if ilosc_aktualna >= ilosc:
        cursor.execute("UPDATE Produkty SET Ilosc = Ilosc - ? WHERE ProduktID = ?", (ilosc, produkt_id))
        operacje_do_dodania.append((produkt_id, "Reklamacja", data_obj, ilosc, "Reklamacja – usunięcie"))

# 5. Dopełniamy do 600 operacji dostawami jeśli potrzeba
while len(operacje_do_dodania) < TOTAL_OPERATIONS:
    produkt_id = random.choice(produkt_ids)
    ilosc = random.randint(1, 20)
    data_obj = datetime.now() - timedelta(days=random.randint(0, 10000))
    magazyn_id = random.choice(magazyny_ids)

    cursor.execute("UPDATE Produkty SET Ilosc = Ilosc + ? WHERE ProduktID = ?", (ilosc, produkt_id))
    cursor.execute("UPDATE Magazyn SET AktualnaIlosc = AktualnaIlosc + ? WHERE MagazynID = ?", (ilosc, magazyn_id))
    cursor.execute("SELECT Ilosc FROM LokalizacjaProduktu WHERE ProduktID = ? AND MagazynID = ?", (produkt_id, magazyn_id))
    lokal = cursor.fetchone()
    if lokal:
        cursor.execute("UPDATE LokalizacjaProduktu SET Ilosc = Ilosc + ? WHERE ProduktID = ? AND MagazynID = ?", (ilosc, produkt_id, magazyn_id))
    else:
        cursor.execute("INSERT INTO LokalizacjaProduktu (ProduktID, MagazynID, Ilosc) VALUES (?, ?, ?)", (produkt_id, magazyn_id, ilosc))

    operacje_do_dodania.append((produkt_id, "Dostawa", data_obj, ilosc, "Dodatkowa dostawa"))

# Sortujemy po dacie operacje
operacje_do_dodania.sort(key=lambda x: x[2])

# Zapisujemy do bazy
for produkt_id, typ, data_obj, ilosc, uwagi in operacje_do_dodania:
    data_str = data_obj.strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO OperacjeMagazynowe (ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi)
        VALUES (?, ?, ?, ?, ?)
    """, (produkt_id, typ, data_str, ilosc, uwagi))

conn.commit()
conn.close()
