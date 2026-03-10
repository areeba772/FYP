-- ==========================================
-- SMART CAFE DATABASE SCHEMA
-- Complete Database Setup for Smart Cafe System
-- ==========================================

-- Create Database
CREATE DATABASE IF NOT EXISTS smart_cafe_db;
USE smart_cafe_db;

-- ==========================================
-- 1. USERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('user', 'admin', 'authority') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 2. MENU ITEMS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS menu_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    image_url VARCHAR(255),
    availability BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 3. DINING TABLES TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS dining_tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    capacity INT DEFAULT 4,
    status ENUM('Available', 'Occupied', 'Reserved') DEFAULT 'Available',
    reserved_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 4. BOOKINGS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    table_id INT NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    guests INT NOT NULL,
    status ENUM('Confirmed', 'Cancelled', 'Completed') DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES dining_tables(table_id) ON DELETE CASCADE
);

-- ==========================================
-- 5. ORDERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status ENUM('Pending', 'Verify', 'Paid', 'Failed') DEFAULT 'Pending',
    transaction_id VARCHAR(100),
    delivery_address TEXT,
    table_number INT,
    number_of_guests INT,
    order_type ENUM('Dine-in', 'Takeaway') DEFAULT 'Dine-in',
    status ENUM('Pending', 'Cooking', 'Ready', 'Completed', 'Cancelled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==========================================
-- 6. ORDER DETAILS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS order_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id) ON DELETE CASCADE
);

-- ==========================================
-- 7. REVIEWS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_id INT,
    item_id INT,
    item_name VARCHAR(100),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id) ON DELETE SET NULL
);

-- ==========================================
-- 8. MESSAGES TABLE (User Complaints/Contact)
-- ==========================================
CREATE TABLE IF NOT EXISTS messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    admin_reply TEXT,
    status ENUM('Open', 'Replied', 'Closed') DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ==========================================
-- 9. NOTIFICATIONS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('Order', 'Booking', 'Message', 'Warning') DEFAULT 'Order',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 10. AUTHORITY WARNINGS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS authority_warnings (
    warning_id INT AUTO_INCREMENT PRIMARY KEY,
    authority_id INT,
    admin_id INT,
    warning_message TEXT NOT NULL,
    warning_type ENUM('Food Quality', 'Pricing', 'Hygiene', 'Other') DEFAULT 'Other',
    status ENUM('Active', 'Resolved') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (authority_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ==========================================
-- INSERT DEFAULT DATA
-- ==========================================

-- Insert Default Admin User
INSERT INTO users (full_name, email, password, role) 
VALUES ('Areeba', 'admin@cafe.com', 'admin123', 'admin')
ON DUPLICATE KEY UPDATE full_name='Areeba';

-- Insert Default Food Authority User
INSERT INTO users (full_name, email, password, role) 
VALUES ('Food Authority', 'authority@cafe.com', 'authority123', 'authority')
ON DUPLICATE KEY UPDATE full_name='Food Authority';

-- Insert Sample Menu Items
INSERT INTO menu_items (name, description, price, category, image_url) VALUES
('Burger', 'Delicious beef burger with fresh vegetables', 350.00, 'Fast Food', 'burger.jpg'),
('Pizza', 'Cheesy pizza with your favorite toppings', 800.00, 'Fast Food', 'pizza.jpg'),
('Pasta', 'Creamy pasta with rich sauce', 450.00, 'Italian', 'pasta.jpg'),
('Steak', 'Juicy grilled steak with sides', 1200.00, 'Main Course', 'steak.jpg'),
('Banana Shake', 'Fresh banana milkshake', 150.00, 'Beverages', 'banana.jpeg')
ON DUPLICATE KEY UPDATE name=name;

-- Insert Dining Tables
INSERT INTO dining_tables (table_name, capacity, status) VALUES
('Table 1', 4, 'Available'),
('Table 2', 4, 'Available'),
('Table 3', 6, 'Available'),
('Table 4', 4, 'Available'),
('Table 5', 2, 'Available'),
('Table 6', 4, 'Available'),
('Table 7', 6, 'Available'),
('Table 8', 4, 'Available')
ON DUPLICATE KEY UPDATE table_name=table_name;

-- ==========================================
-- CREATE INDEXES FOR PERFORMANCE
-- ==========================================
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_status ON orders(status);
CREATE INDEX idx_booking_date_time ON bookings(booking_date, booking_time);
CREATE INDEX idx_review_item ON reviews(item_id);
CREATE INDEX idx_notification_email ON notifications(user_email);

-- ==========================================
-- END OF SCHEMA
-- ==========================================
