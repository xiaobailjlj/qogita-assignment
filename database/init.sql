CREATE DATABASE QOGITA;

USE QOGITA;

CREATE TABLE offers (
    uuid VARCHAR(64) PRIMARY KEY,
    seller_id VARCHAR(128) NOT NULL,
    gtin VARCHAR(64) NOT NULL,
    currency VARCHAR(4) DEFAULT 'EUR',
    pack_price FLOAT NOT NULL,
    pack_quantity INT NOT NULL,
    pack_size INT NOT NULL,
    title VARCHAR(256),
    description TEXT,
    status ENUM('AVAILABLE', 'INVALID') DEFAULT 'AVAILABLE',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_gtin (gtin),
    INDEX idx_seller_id (seller_id)
);