import os
import sqlite3

# Ścieżka do pliku bazy danych
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "mini_allegro.db")

# Połączenie z bazą
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Rozpocznij transakcję
cursor.executescript("""
BEGIN TRANSACTION;

DROP TABLE IF EXISTS PozycjeZamowienia;
DROP TABLE IF EXISTS Zamowienia;

CREATE TABLE Zamowienia (
    ZamowienieID INTEGER PRIMARY KEY AUTOINCREMENT,
    KlientID INTEGER,
    DataZamowienia TEXT,
    Kwota REAL,
    FOREIGN KEY(KlientID) REFERENCES Klienci(KlientID)
);

INSERT INTO Zamowienia VALUES (1,1,'2025-06-11',7043.0);
INSERT INTO Zamowienia VALUES (2,2,'2025-06-11',897.0);
INSERT INTO Zamowienia VALUES (3,3,'2025-06-11',633.0);
INSERT INTO Zamowienia VALUES (4,4,'2025-06-11',297.0);
INSERT INTO Zamowienia VALUES (5,5,'2025-06-11',1431.0);

CREATE TABLE PozycjeZamowienia (
    PozycjaID INTEGER PRIMARY KEY AUTOINCREMENT,
    ZamowienieID INTEGER,
    ProduktID INTEGER,
    Ilosc INTEGER,
    Cena REAL,
    CenaBrutto REAL,
    FOREIGN KEY(ZamowienieID) REFERENCES Zamowienia(ZamowienieID),
    FOREIGN KEY(ProduktID) REFERENCES Produkty(ProduktID)
);

INSERT INTO PozycjeZamowienia VALUES (1,1,1,2,3200.0,6400.0);
INSERT INTO PozycjeZamowienia VALUES (2,1,2,2,299.0,598.0);
INSERT INTO PozycjeZamowienia VALUES (3,1,5,2,19.0,38.0);
INSERT INTO PozycjeZamowienia VALUES (4,1,7,2,3.5,7.0);
INSERT INTO PozycjeZamowienia VALUES (5,2,9,6,2.5,15.0);
INSERT INTO PozycjeZamowienia VALUES (6,2,21,3,29.0,87.0);
INSERT INTO PozycjeZamowienia VALUES (7,2,19,3,169.0,507.0);
INSERT INTO PozycjeZamowienia VALUES (8,2,17,3,7.0,21.0);
INSERT INTO PozycjeZamowienia VALUES (9,2,16,3,89.0,267.0);
INSERT INTO PozycjeZamowienia VALUES (10,3,25,3,22.0,66.0);
INSERT INTO PozycjeZamowienia VALUES (11,3,28,3,189.0,567.0);
INSERT INTO PozycjeZamowienia VALUES (12,4,29,3,99.0,297.0);
INSERT INTO PozycjeZamowienia VALUES (13,5,29,3,99.0,297.0);
INSERT INTO PozycjeZamowienia VALUES (14,5,28,6,189.0,1134.0);

COMMIT;
""")

# Zapisz zmiany i zamknij
conn.commit()
conn.close()

print("Baza danych została utworzona i wypełniona.")
