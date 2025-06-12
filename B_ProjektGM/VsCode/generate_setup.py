import os
import sqlite3

# Ustal lokalizację bazy
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "mini_allegro.db")

# Usuń starą bazę jeśli istnieje
if os.path.exists(db_path):
    os.remove(db_path)

# Połączenie z bazą
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tworzenie tabel
cursor.execute("""
CREATE TABLE Produkty (
    ProduktID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nazwa TEXT NOT NULL,
    Kategoria TEXT,
    Cena REAL,
    Ilosc INTEGER DEFAULT 0,
    LokalizacjaID INTEGER,
    FOREIGN KEY (LokalizacjaID) REFERENCES Magazyn(MagazynID)
);
""")

cursor.execute("""
CREATE TABLE Klienci (
    KlientID INTEGER PRIMARY KEY AUTOINCREMENT,
    Imie TEXT,
    Nazwisko TEXT,
    Email TEXT
);
""")

cursor.execute("""
CREATE TABLE Zamowienia (
    ZamowienieID INTEGER PRIMARY KEY AUTOINCREMENT,
    KlientID INTEGER,
    DataZamowienia TEXT,
    Kwota REAL,
    FOREIGN KEY(KlientID) REFERENCES Klienci(KlientID)
);
""")

cursor.execute("""
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
""")

cursor.execute("""
CREATE TABLE Magazyn (
    MagazynID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nazwa TEXT NOT NULL,
    MaksymalnaPojemnosc INTEGER NOT NULL,
    AktualnaIlosc INTEGER NOT NULL DEFAULT 0
);
""")

cursor.execute("""
CREATE TABLE LokalizacjaProduktu (
    LokalizacjaID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProduktID INTEGER,
    MagazynID INTEGER,
    Ilosc INTEGER,
    FOREIGN KEY (ProduktID) REFERENCES Produkty(ProduktID),
    FOREIGN KEY (MagazynID) REFERENCES Magazyn(MagazynID)
);
""")

cursor.execute("""
CREATE TABLE OperacjeMagazynowe (
    OperacjaID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProduktID INTEGER,
    TypOperacji TEXT,
    DataOperacji TEXT,
    Ilosc INTEGER,
    Uwagi TEXT,
    FOREIGN KEY(ProduktID) REFERENCES Produkty(ProduktID)
);
""")

# Dodanie danych

klienci = [
    ("Anna", "Nowak", "anna@example.com"),
    ("Jan", "Kowalski", "jan@example.com"),
    ("Kasia", "Wiśniewska", "kasia@example.com"),
    ("Andrzej", "Malak", "andrzej@examlple.com"),
    ("Maciej", "Czaja", "maciej@examlple.com"),
    ("Jakub", "Buk", "jakub@examlple.com"),
    ("Marian", "Pazdzioch", "marian@examlple.com"),
    ("Marcelina", "Strych", "marcelina@examlple.com"),
    ("Agata", "Kasa", "agata@examlple.com"),
    ("Melania", "Kielich", "melania@examlple.com"),
    ("Felicja", "Fel", "felicja@examlple.com"),
    ("Alicja", "Drzewo", "alicja@examlple.com"),
    ("Grażyna", "Gracz", "grazyna@examlple.com")
]
cursor.executemany("INSERT INTO Klienci (Imie, Nazwisko, Email) VALUES (?, ?, ?);", klienci)

produkty = [
    ("Laptop Lenovo IdeaPad", "Elektronika", 3200.0, 15),
    ("Mysz Logitech", "Akcesoria", 299.0, 40),
    ("Papier A4 x500", "Biuro", 25.0, 100),
    ("Drukarka HP Inkjet", "Elektronika", 450.0, 10),
    ("Kabel HDMI 2m", "Akcesoria", 19.0, 70),
    ("Monitor Dell 24\"", "Elektronika", 799.0, 12),
    ("Długopis żelowy", "Biuro", 3.5, 500),
    ("Tusz do drukarki", "Biuro", 79.0, 30),
    ("Zeszyt A5", "Szkoła", 2.5, 300),
    ("Plecak Xiaomi", "Akcesoria", 129.0, 20),
    ("Karta SD 64GB", "Elektronika", 55.0, 25),
    ("Etui na telefon", "Akcesoria", 29.0, 50),
    ("Powerbank", "Elektronika", 99.0, 15),
    ("Notes A4", "Biuro", 18.0, 40),
    ("Klawiatura", "Elektronika", 259.0, 10),
    ("Torba na laptopa", "Akcesoria", 89.0, 18),
    ("Taśma pakowa", "Magazyn", 7.0, 200),
    ("Lampka LED", "Biuro", 45.0, 35),
    ("Słuchawki JBL", "Elektronika", 169.0, 8),
    ("Mata pod mysz", "Akcesoria", 39.0, 60),
    ("Pendrive 32GB", "Elektronika", 29.0, 75),
    ("Tablet Wacom", "Elektronika", 329.0, 5),
    ("Papier kolorowy", "Biuro", 19.0, 60),
    ("Ramka 10x15", "Dom", 12.0, 40),
    ("Markery 12 kolorów", "Biuro", 22.0, 35),
    ("Pojemnik na dokumenty", "Biuro", 16.0, 30),
    ("Kalkulator", "Szkoła", 49.0, 20),
    ("Głośnik Bluetooth", "Elektronika", 189.0, 10),
    ("Zasilacz", "Elektronika", 99.0, 12),
    ("Mikrofon USB", "Elektronika", 159.0, 6),
]
cursor.executemany("INSERT INTO Produkty (Nazwa, Kategoria, Cena, Ilosc) VALUES (?, ?, ?, ?);", produkty)

magazyny = [
    ("Regał A", 100),
    ("Regał B", 150),
]
for nazwa, max_poj in magazyny:
    cursor.execute("INSERT INTO Magazyn (Nazwa, MaksymalnaPojemnosc, AktualnaIlosc) VALUES (?, ?, ?)", (nazwa, max_poj, 0))

conn.commit()
conn.close()

print("Baza danych mini_allegro.db została utworzona.")
