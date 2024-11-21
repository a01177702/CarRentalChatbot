-- Insert into Shop Table
INSERT INTO Shop (ShopID, Location) 
VALUES 
    (1, 'New York'),
    (2, 'Los Angeles'),
    (3, 'Chicago'),
    (4, 'Miami'),
    (5, 'San Francisco');

-- Insert into Cars Table
INSERT INTO Cars (CarID, Model, Brand, Year, Color, PricePerDay, ShopID)
VALUES 
    (1, 'Model S', 'Tesla', 2023, 'Blue', 150.0, 1),
    (2, 'Corolla', 'Toyota', 2022, 'Red', 50.0, 2),
    (3, 'Civic', 'Honda', 2021, 'Black', 60.0, 3),
    (4, 'Mustang', 'Ford', 2020, 'Yellow', 120.0, 4),
    (5, 'Camry', 'Toyota', 2022, 'White', 55.0, 5),
    (6, 'Accord', 'Honda', 2023, 'Gray', 70.0, 1),
    (7, 'Model X', 'Tesla', 2023, 'Red', 180.0, 2),
    (8, 'F-150', 'Ford', 2020, 'Blue', 110.0, 3),
    (9, 'RAV4', 'Toyota', 2021, 'Green', 65.0, 4),
    (10, 'Explorer', 'Ford', 2022, 'Silver', 90.0, 5);

-- Insert into CarAvailability Table
INSERT INTO CarAvailability (CarID, StartDate, EndDate)
VALUES
    (1, '2024-01-01', '2024-01-10'),
    (2, '2024-02-01', '2024-02-15'),
    (3, '2024-03-01', '2024-03-20'),
    (4, '2024-01-15', '2024-01-25'),
    (5, '2024-04-01', '2024-04-10'),
    (6, '2024-01-10', '2024-01-20'),
    (7, '2024-02-15', '2024-02-28'),
    (8, '2024-03-01', '2024-03-10'),
    (9, '2024-04-05', '2024-04-20'),
    (10, '2024-05-01', '2024-05-15');
