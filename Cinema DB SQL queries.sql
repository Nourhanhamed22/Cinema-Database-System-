-- Create the Database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CinemaDB_Pro')
    CREATE DATABASE CinemaDB_Pro;
GO
USE CinemaDB_Pro;
GO

-- Drop tables to recreate them in the correct order
IF OBJECT_ID('Bookings', 'U') IS NOT NULL DROP TABLE Bookings;
IF OBJECT_ID('Seats', 'U') IS NOT NULL DROP TABLE Seats;
IF OBJECT_ID('Menu', 'U') IS NOT NULL DROP TABLE Menu;
IF OBJECT_ID('PromoCodes', 'U') IS NOT NULL DROP TABLE PromoCodes;
IF OBJECT_ID('Showtimes', 'U') IS NOT NULL DROP TABLE Showtimes;
IF OBJECT_ID('Movies', 'U') IS NOT NULL DROP TABLE Movies;

-- 1. Movies Table
CREATE TABLE Movies (
    MovieID INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(255) NOT NULL,
    Duration NVARCHAR(50)
);

-- 2. Showtimes Table
CREATE TABLE Showtimes (
    ShowID INT IDENTITY(1,1) PRIMARY KEY,
    MovieID INT FOREIGN KEY REFERENCES Movies(MovieID),
    ShowTime NVARCHAR(50)
);

-- 3. Seats Table
CREATE TABLE Seats (
    SeatID INT IDENTITY(1,1) PRIMARY KEY,
    SeatName NVARCHAR(10) UNIQUE,
    SeatType NVARCHAR(50), 
    Price DECIMAL(10,2),
    Status NVARCHAR(20) DEFAULT 'Available'
);

-- 4. Menu Table
CREATE TABLE Menu (
    ItemID INT IDENTITY(1,1) PRIMARY KEY,
    ItemName NVARCHAR(100),
    Category NVARCHAR(50), -- Food or Drink
    Price DECIMAL(10,2)
);

-- 5. Promo Codes Table
CREATE TABLE PromoCodes (
    Code NVARCHAR(50) PRIMARY KEY,
    DiscountValue DECIMAL(10,2)
);

-- 6. Bookings Table
CREATE TABLE Bookings (
    BookingID INT IDENTITY(1,1) PRIMARY KEY,
    MovieTitle NVARCHAR(255),
    ShowTime NVARCHAR(50),
    SeatsBooked NVARCHAR(MAX),
    TotalPaid DECIMAL(10,2),
    BookingDate DATETIME DEFAULT GETDATE()
);
GO

-- Stored Procedure for booking
DROP PROCEDURE IF EXISTS sp_BookTicket;
GO
CREATE PROCEDURE sp_BookTicket
    @Movie NVARCHAR(255),
    @Time NVARCHAR(50),
    @Seats NVARCHAR(MAX),
    @Total DECIMAL(10,2)
AS
BEGIN
    INSERT INTO Bookings (MovieTitle, ShowTime, SeatsBooked, TotalPaid)
    VALUES (@Movie, @Time, @Seats, @Total);
END;
GO

-- Trigger to strictly PREVENT double booking (Seat Duplication Rule)
CREATE TRIGGER trg_PreventDoubleBooking
ON Seats
FOR UPDATE
AS
BEGIN
    IF EXISTS (SELECT 1 FROM inserted i JOIN deleted d ON i.SeatID = d.SeatID WHERE d.Status = 'Booked' AND i.Status = 'Booked')
    BEGIN
        RAISERROR ('عفواً، المقعد محجوز مسبقاً!', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;
GO

-- ================= Initial Data Seeding =================
INSERT INTO Movies (Title, Duration) VALUES 
('Oppenheimer (Biography)', '180m'), ('The Dark Knight (Action)', '152m'), 
('Dune: Part Two (Sci-Fi)', '166m'), ('Avatar: The Way of Water', '192m'),
('Inception (Sci-Fi)', '148m'), ('Gladiator (Action)', '155m'), 
('Interstellar (Sci-Fi)', '169m');

INSERT INTO Showtimes (MovieID, ShowTime) VALUES 
(1, '10:00 AM'), (1, '01:00 PM'), (1, '10:30 PM'),
(2, '04:00 PM'), (3, '07:30 PM'), (4, '12:00 PM'),
(5, '09:00 PM'), (6, '06:00 PM'), (7, '03:00 PM');

INSERT INTO PromoCodes (Code, DiscountValue) VALUES ('ECU2026', 108.00);

-- Adding Food and Drinks
INSERT INTO Menu (ItemName, Category, Price) VALUES 
('فشار كراميل عائلي', 'Food', 120), ('فشار وسط مملح', 'Food', 80), 
('ناتشوز بالجبنة', 'Food', 110), ('هوت دوج كلاسيك', 'Food', 95), 
('مولتن كيك', 'Food', 130), ('دوريتوس', 'Food', 40),
('بيبسي كبير', 'Drink', 45), ('سفن أب', 'Drink', 40), 
('مياه معدنية', 'Drink', 20), ('قهوة اسبريسو', 'Drink', 60), 
('عصير برتقال فريش', 'Drink', 70), ('آيس كوفي', 'Drink', 85);

-- Generate IMAX seats
DECLARE @Row CHAR(1) = 'A';
DECLARE @Num INT;
WHILE @Row <= 'F'
BEGIN
    SET @Num = 1;
    WHILE @Num <= 8
    BEGIN
        DECLARE @Type NVARCHAR(50) = CASE WHEN @Row IN ('C', 'D') THEN 'VIP Premium' ELSE 'Standard' END;
        DECLARE @Price DECIMAL(10,2) = CASE WHEN @Row IN ('C', 'D') THEN 250 ELSE 150 END;
        INSERT INTO Seats (SeatName, SeatType, Price) VALUES (@Row + CAST(@Num AS NVARCHAR), @Type, @Price);
        SET @Num = @Num + 1;
    END
    SET @Row = CHAR(ASCII(@Row) + 1);
END;
GO
-- ---------------------------------------------------------
-- PART 4: OUTPUT QUERIES (FOR DOCTOR'S PRESENTATION)
-- ---------------------------------------------------------
-- Execute these separately during presentation to show live data

SELECT * FROM Movies;
SELECT * FROM Seats;
SELECT * FROM Menu;
SELECT * FROM PromoCodes;
SELECT * FROM Bookings; -- This will be empty until a booking is made via GUI
GO