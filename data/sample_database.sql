-- Sample database schema for testing
-- This script creates a simple e-commerce database for demonstration

-- Create database (adjust for your SQL Server instance)
-- CREATE DATABASE SampleECommerce;
-- USE SampleECommerce;

-- Customers table
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY IDENTITY(1,1),
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) UNIQUE NOT NULL,
    Phone NVARCHAR(20),
    Address NVARCHAR(200),
    City NVARCHAR(50),
    State NVARCHAR(50),
    ZipCode NVARCHAR(10),
    Country NVARCHAR(50) DEFAULT 'USA',
    DateCreated DATETIME DEFAULT GETDATE(),
    IsActive BIT DEFAULT 1
);

-- Categories table
CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY IDENTITY(1,1),
    CategoryName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    IsActive BIT DEFAULT 1
);

-- Products table
CREATE TABLE Products (
    ProductID INT PRIMARY KEY IDENTITY(1,1),
    ProductName NVARCHAR(200) NOT NULL,
    CategoryID INT,
    Price DECIMAL(10,2) NOT NULL,
    CostPrice DECIMAL(10,2),
    StockQuantity INT DEFAULT 0,
    Description NVARCHAR(1000),
    SKU NVARCHAR(50) UNIQUE,
    IsActive BIT DEFAULT 1,
    DateCreated DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- Orders table
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT NOT NULL,
    OrderDate DATETIME DEFAULT GETDATE(),
    TotalAmount DECIMAL(10,2) NOT NULL,
    Status NVARCHAR(20) DEFAULT 'Pending',
    ShippingAddress NVARCHAR(500),
    PaymentMethod NVARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- OrderItems table
CREATE TABLE OrderItems (
    OrderItemID INT PRIMARY KEY IDENTITY(1,1),
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    TotalPrice AS (Quantity * UnitPrice),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Insert sample data

-- Categories
INSERT INTO Categories (CategoryName, Description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Books', 'Books and educational materials'),
('Home & Garden', 'Home improvement and garden supplies'),
('Sports', 'Sports equipment and accessories');

-- Products
INSERT INTO Products (ProductName, CategoryID, Price, CostPrice, StockQuantity, SKU) VALUES
('iPhone 15', 1, 999.00, 700.00, 50, 'IPHONE15'),
('Samsung Galaxy S24', 1, 899.00, 650.00, 30, 'GALAXY24'),
('Dell Laptop', 1, 1299.00, 900.00, 25, 'DELL001'),
('Nike Sneakers', 2, 129.99, 80.00, 100, 'NIKE001'),
('Levi Jeans', 2, 79.99, 45.00, 75, 'LEVI001'),
('Python Programming Book', 3, 49.99, 25.00, 200, 'BOOK001'),
('Garden Tools Set', 4, 89.99, 50.00, 40, 'GARDEN001'),
('Tennis Racket', 5, 199.99, 120.00, 30, 'TENNIS001');

-- Customers
INSERT INTO Customers (FirstName, LastName, Email, Phone, City, State) VALUES
('John', 'Doe', 'john.doe@email.com', '555-0101', 'New York', 'NY'),
('Jane', 'Smith', 'jane.smith@email.com', '555-0102', 'Los Angeles', 'CA'),
('Mike', 'Johnson', 'mike.j@email.com', '555-0103', 'Chicago', 'IL'),
('Sarah', 'Williams', 'sarah.w@email.com', '555-0104', 'Houston', 'TX'),
('David', 'Brown', 'david.b@email.com', '555-0105', 'Phoenix', 'AZ'),
('Lisa', 'Davis', 'lisa.d@email.com', '555-0106', 'Philadelphia', 'PA'),
('Tom', 'Wilson', 'tom.w@email.com', '555-0107', 'San Antonio', 'TX'),
('Amy', 'Taylor', 'amy.t@email.com', '555-0108', 'San Diego', 'CA');

-- Orders (recent dates for testing)
INSERT INTO Orders (CustomerID, OrderDate, TotalAmount, Status, PaymentMethod) VALUES
(1, DATEADD(day, -5, GETDATE()), 1298.99, 'Completed', 'Credit Card'),
(2, DATEADD(day, -10, GETDATE()), 179.98, 'Completed', 'PayPal'),
(3, DATEADD(day, -15, GETDATE()), 999.00, 'Shipped', 'Credit Card'),
(4, DATEADD(day, -20, GETDATE()), 89.99, 'Completed', 'Debit Card'),
(5, DATEADD(day, -25, GETDATE()), 249.98, 'Completed', 'Credit Card'),
(1, DATEADD(day, -30, GETDATE()), 49.99, 'Completed', 'Credit Card'),
(6, DATEADD(day, -35, GETDATE()), 899.00, 'Completed', 'PayPal'),
(7, DATEADD(day, -40, GETDATE()), 129.99, 'Completed', 'Credit Card');

-- Order Items
INSERT INTO OrderItems (OrderID, ProductID, Quantity, UnitPrice) VALUES
-- Order 1
(1, 3, 1, 1299.00),  -- Dell Laptop
-- Order 2  
(2, 4, 1, 129.99),   -- Nike Sneakers
(2, 6, 1, 49.99),    -- Python Book
-- Order 3
(3, 1, 1, 999.00),   -- iPhone
-- Order 4
(4, 7, 1, 89.99),    -- Garden Tools
-- Order 5
(5, 8, 1, 199.99),   -- Tennis Racket
(5, 6, 1, 49.99),    -- Python Book
-- Order 6
(6, 6, 1, 49.99),    -- Python Book
-- Order 7
(7, 2, 1, 899.00),   -- Samsung Galaxy
-- Order 8
(8, 4, 1, 129.99);   -- Nike Sneakers

-- Create some useful views
CREATE VIEW CustomerOrderSummary AS
SELECT 
    c.CustomerID,
    c.FirstName + ' ' + c.LastName AS CustomerName,
    c.Email,
    COUNT(o.OrderID) as TotalOrders,
    SUM(o.TotalAmount) as TotalSpent,
    MAX(o.OrderDate) as LastOrderDate
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName, c.Email;

CREATE VIEW ProductSales AS
SELECT 
    p.ProductID,
    p.ProductName,
    c.CategoryName,
    SUM(oi.Quantity) as TotalQuantitySold,
    SUM(oi.TotalPrice) as TotalRevenue,
    AVG(oi.UnitPrice) as AveragePrice,
    (SUM(oi.UnitPrice) - SUM(p.CostPrice * oi.Quantity)) as TotalProfit
FROM Products p
JOIN Categories c ON p.CategoryID = c.CategoryID
LEFT JOIN OrderItems oi ON p.ProductID = oi.ProductID
GROUP BY p.ProductID, p.ProductName, c.CategoryName;

-- Create indexes for better performance
CREATE INDEX IX_Orders_CustomerID ON Orders(CustomerID);
CREATE INDEX IX_Orders_OrderDate ON Orders(OrderDate);
CREATE INDEX IX_Products_CategoryID ON Products(CategoryID);
CREATE INDEX IX_OrderItems_OrderID ON OrderItems(OrderID);
CREATE INDEX IX_OrderItems_ProductID ON OrderItems(ProductID);
