BEGIN TRANSACTION;
CREATE TABLE Zamowienia (
    ZamowienieID INTEGER PRIMARY KEY AUTOINCREMENT,
    KlientID INTEGER,
    DataZamowienia TEXT,
    Kwota REAL,
    FOREIGN KEY(KlientID) REFERENCES Klienci(KlientID)
);
CREATE TABLE Produkty (
    ProduktID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nazwa TEXT NOT NULL,
    Kategoria TEXT,
    Cena REAL,
    Ilosc INTEGER DEFAULT 0,
    LokalizacjaID INTEGER,
    FOREIGN KEY (LokalizacjaID) REFERENCES Magazyn(MagazynID)
);
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
CREATE TABLE OperacjeMagazynowe (
    OperacjaID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProduktID INTEGER,
    TypOperacji TEXT,
    DataOperacji TEXT,
    Ilosc INTEGER,
    Uwagi TEXT,
    FOREIGN KEY(ProduktID) REFERENCES Produkty(ProduktID)
);
CREATE TABLE Magazyn (
    MagazynID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nazwa TEXT NOT NULL,
    MaksymalnaPojemnosc INTEGER NOT NULL,
    AktualnaIlosc INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE LokalizacjaProduktu (
    LokalizacjaID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProduktID INTEGER,
    MagazynID INTEGER,
    Ilosc INTEGER,
    FOREIGN KEY (ProduktID) REFERENCES Produkty(ProduktID),
    FOREIGN KEY (MagazynID) REFERENCES Magazyn(MagazynID)
);
CREATE TABLE Klienci (
    KlientID INTEGER PRIMARY KEY AUTOINCREMENT,
    Imie TEXT,
    Nazwisko TEXT,
    Email TEXT
);
COMMIT;
