# Cinema-Database-System-

A desktop cinema ticket booking application built with Python (Tkinter) for the interface and Microsoft SQL Server for data storage — covering the full booking flow from movie selection to seat picking, food & drinks ordering, promo codes, and final ticket generation.

##  Features
- Movie & showtime selection — pulled live from the database
- Interactive seat map — color-coded by seat type (Standard / VIP Premium), with booked seats automatically disabled
- Duplicate-booking prevention — enforced at the database level with a SQL trigger, so two customers can never book the same seat
- Food & drinks menu — categorized (Food / Drink) with a running order cart
- Promo code discounts — validated against the database and applied to the final invoice
- Automated ticket generation — stores the completed booking via a stored procedure and displays a formatted invoice/ticket
- Full Arabic RTL interface

##  Built With
- Python — Tkinter / ttk for the GUI
- pyodbc — database connectivity
- Microsoft SQL Server — data storage, stored procedures, and triggers

##  Database Design
The system uses six core tables: Movies (movie titles and durations), Showtimes (showtime slots linked to movies), Seats (seat inventory with type, price, and status), Menu (food & drink items with category and price), PromoCodes (discount codes and values), and Bookings (finalized booking records).

Business logic in the database: sp_BookTicket is a stored procedure that inserts a new booking record, and trg_PreventDoubleBooking is a trigger that blocks a seat from being booked twice, rolling back the transaction if a conflict is detected.

##  Project Structure
- ECU_Cinema_Booking_System.py — Main application (GUI + database logic)
- database_schema.sql — Full database creation script (tables, stored procedure, trigger, seed data)

##  Getting Started

### Prerequisites
- Python 3.8+
- Microsoft SQL Server (Express edition works fine)
- ODBC Driver for SQL Server

### Installation
Run: pip install pyodbc

### Database Setup
1. Open the database_schema.sql script in SQL Server Management Studio (SSMS)
2. Run it — this creates the CinemaDB_Pro database, all tables, the stored procedure, the trigger, and seeds sample movies/seats/menu items

### Configure the Connection
In ECU_Cinema_Booking_System.py, update the connect_db method with your SQL Server instance name (found in SSMS → Object Explorer), for example:
SERVER=localhost\SQLEXPRESS

### Run
Run: python ECU_Cinema_Booking_System.py

##  How It Works
1. Select a movie & showtime from dropdowns populated live from the database
2. Pick seats on an interactive IMAX-style seating grid
3. Add food & drinks to a running cart
4. Review the invoice, optionally apply a promo code
5. Confirm payment — the booking is saved to the database and a ticket is generated
