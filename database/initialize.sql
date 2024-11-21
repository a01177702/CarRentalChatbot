CREATE TABLE Cars (
    CarID INTEGER PRIMARY KEY,
    Model TEXT NOT NULL,
    Brand TEXT NOT NULL,
    Year INTEGER NOT NULL,
    Color TEXT NOT NULL,
    PricePerDay REAL NOT NULL,
    ShopID INTEGER
);

CREATE TABLE Shop (
    ShopID INTEGER PRIMARY KEY,
    Location TEXT NOT NULL
);

CREATE TABLE CarAvailability (
    CarID INTEGER NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    FOREIGN KEY (CarID) REFERENCES Cars(CarID)
);